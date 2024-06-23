import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iot from 'aws-cdk-lib/aws-iot';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as path from 'path';
import * as event_sources from 'aws-cdk-lib/aws-lambda-event-sources';
import { Construct } from 'constructs';
import * as dotenv from 'dotenv'

// .envファイルのパスを指定して環境変数を読み込む
dotenv.config({ path: path.resolve(__dirname, '../../.env') });


const PREFIX = "raspberrypi-iot-movement-detection"
const BUCKET_NAME = PREFIX + "-bucket"
const IOT_ROLE = PREFIX + "-iot-role"
const IOT_RULE = PREFIX + "-iot-rule"
const IOT_DEVICE = PREFIX + "-iot-device"
const IOT_THING_ATTACHMENT = PREFIX + "-iot-thing-attachment"
const IOT_POLICY_ATTACHMENT = PREFIX + "-iot-policy-attachment"
const IOT_POLICY = PREFIX + "-iot-policy";
const IOT_LAMBDA_PERMISSION = PREFIX + "-iot-permission";
const TOPIC_DIR = "detection"

export class IotStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    //     I want to save images to S3 via iot-core.
    // Next, I want to call lambda in the apis directory from an S3 event. There is a requirement.txt, so I want it to be usable on the lambda side. 
    // S3バケットを作成します

    const imageBucket = new s3.Bucket(this,
      BUCKET_NAME, {
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // 3. Create a Lambda function in the "apis" directory
    const lambdaFunction = new lambda.Function(this, 'lambdaFunction', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'iot.lambda_handler',
      code: lambda.Code.fromAsset(path.join('apis')),
      environment: {
        PYTHONPATH: '/var/task/apis:/var/task/apis/package',
        LINE_TOKEN: process.env.LINE_TOKEN!
      },
      events: [
        new event_sources.S3EventSource(imageBucket, {
          events: [s3.EventType.OBJECT_CREATED],
          filters: [{ prefix: TOPIC_DIR }]
        })
      ],
    });
    

    // IoT用のIAMロールを作成します
    const iotRole = new iam.Role(this, IOT_ROLE, {
      assumedBy: new iam.ServicePrincipal('iot.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3FullAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AWSIoTDataAccess'),
      ],
    });

    // IoTルールを作成して、S3バケットにデータを保存します
    const iotRule = new iot.CfnTopicRule(this, IOT_RULE, {
      topicRulePayload: {
        sql: 'SELECT * FROM "' + TOPIC_DIR + '"',
        actions: [
          {
            s3: {
              bucketName: imageBucket.bucketName,
              key: '${topic()}/${timestamp()}',
              roleArn: iotRole.roleArn,
            },
          },
        ],
      },
    });

    // S3バケットへの読み書き権限をLambda関数に付与します
    imageBucket.grantReadWrite(lambdaFunction);

    // Lambda関数に対するInvoke権限を設定します
    new lambda.CfnPermission(this, IOT_LAMBDA_PERMISSION, {
      functionName: lambdaFunction.functionName,
      action: 'lambda:InvokeFunction',
      principal: 'iot.amazonaws.com',
      sourceArn: iotRule.attrArn
    });

    // IoTデバイス（Thing）を作成します
    const thing = new iot.CfnThing(this, IOT_DEVICE, {
      thingName: IOT_DEVICE,
      attributePayload: {
        attributes: {
          // Add any desired attributes for the device
          deviceType: 'camera',
          location: 'office',
        },
      },
    });

    // IoTポリシーを作成します
    const policy = new iot.CfnPolicy(this, IOT_POLICY, {
      policyName: IOT_POLICY,
      policyDocument: {
        Version: "2012-10-17",
        Statement: [
          {
            Effect: "Allow",
            Action: [
              "iot:Connect",
              "iot:Publish",
              "iot:Subscribe",
              "iot:Receive"
            ],
            Resource: "*"
          }
        ]
      }
    });

    // ポリシーの作成後にアタッチメントを設定します
    const policyAttachment = new iot.CfnPolicyPrincipalAttachment(this, IOT_POLICY_ATTACHMENT, {
      policyName: policy.policyName!,
      principal: process.env.CERT_ARN!
    });

    policyAttachment.node.addDependency(policy);

    // Thingの作成後に証明書をアタッチします
    const thingPrincipalAttachment = new iot.CfnThingPrincipalAttachment(this, IOT_THING_ATTACHMENT, {
      principal: process.env.CERT_ARN!,
      thingName: thing.ref,
    });

    thingPrincipalAttachment.node.addDependency(thing);

  }
}
