import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as sfn from 'aws-cdk-lib/aws-stepfunctions';
import * as tasks from 'aws-cdk-lib/aws-stepfunctions-tasks';
import * as path from 'path';
import * as dotenv from 'dotenv'
import { Construct } from 'constructs';

// .envファイルのパスを指定して環境変数を読み込む
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

const PREFIX = "raspberrypi-iot-stepfunction"
const IOT_BUCKET = PREFIX + "-bucket"
const IOT_START_STEPFUNCTION = PREFIX + "-start-stepfunction"
const IOT_GET_S3 = PREFIX + "-get-s3-object"
const IOT_GET_S3_TASK = IOT_GET_S3 + "-task"
const IOT_NOTIFY_LINE = PREFIX + "notify-line"
const IOT_NOTIFY_LINE_TASK = IOT_NOTIFY_LINE + "-task"
const IOT_MACHINE = PREFIX + "-machine"

interface IotStepFunctionStackProps extends cdk.StackProps {
  bucketName: string;
}

export class IotStepFunctionStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: IotStepFunctionStackProps) {
    super(scope, id, props);
    // 既存のS3バケットを参照
    const existingBucket = s3.Bucket.fromBucketName(this, IOT_BUCKET, props.bucketName);

    // GetS3ObjectFunctionのLambda関数
    const getS3ObjectFunction = new lambda.Function(this, IOT_GET_S3, {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'get_s3_object.lambda_handler',
      code: lambda.Code.fromAsset(path.join('apis')),
    });

    // NotifyLINEFunctionのLambda関数
    const notifyLINEFunction = new lambda.Function(this, IOT_NOTIFY_LINE, {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'notify_line.lambda_handler',
      code: lambda.Code.fromAsset(path.join('apis')),
      environment: {
        LINE_TOKEN: process.env.LINE_TOKEN || '',
      },
    });

    // 既存のS3バケットへの権限をGetS3ObjectFunctionに付与
    existingBucket.grantRead(getS3ObjectFunction);

    // Step Functionsの定義
    // Step Functionsのタスク定義
    const getS3ObjectTask = new tasks.LambdaInvoke(this, IOT_GET_S3_TASK, {
      lambdaFunction: getS3ObjectFunction,
      outputPath: '$.Payload',
    }).addCatch(new sfn.Fail(this, 'GetS3ObjectFail', {
      cause: 'S3 Get Object Failed',
      error: 'GetS3ObjectError',
    }), {
      resultPath: '$.errorInfo'
    });

    const notifyLINETask = new tasks.LambdaInvoke(this, IOT_NOTIFY_LINE_TASK, {
      lambdaFunction: notifyLINEFunction,
      outputPath: '$.Payload',
    }).addCatch(new sfn.Fail(this, 'NotifyLINEFail', {
      cause: 'LINE Notification Failed',
      error: 'NotifyLINEError',
    }), {
      resultPath: '$.errorInfo'
    });

    const definition = getS3ObjectTask.next(notifyLINETask);

    const stateMachine = new sfn.StateMachine(this, IOT_MACHINE, {
      definition,
    });

    // StartStepFunctionのLambda関数
    const startStepFunction = new lambda.Function(this, IOT_START_STEPFUNCTION, {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'start_step_function.lambda_handler',
      code: lambda.Code.fromAsset(path.join('apis')),
      environment: {
        STATE_MACHINE_ARN: stateMachine.stateMachineArn,
      },
    });
    // S3バケットにイベント通知を設定して、オブジェクト作成時にStartStepFunctionをトリガー
    existingBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.LambdaDestination(startStepFunction),
    );
    // Step Functionsの実行を許可するためのポリシーをLambda関数に付与
    stateMachine.grantStartExecution(startStepFunction);
  }
}
