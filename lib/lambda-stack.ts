import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import { S3Stack } from './s3-stack';

export class LambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Get the S3 bucket from the S3Stack
    const s3Stack = new S3Stack(this, 'S3Stack');
    const imageBucket = s3Stack.imageBucket;

    // Create a Lambda function in the 'apis' directory
    const imageProcessor = new lambda.Function(this, 'ImageProcessor', {
      runtime: lambda.Runtime.NODEJS_14_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('apis/image-processor'),
    });

    // Grant the Lambda function permission to access the S3 bucket
    imageBucket.grantRead(imageProcessor);

    // Configure S3 event notification to invoke the Lambda function
    imageBucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.LambdaDestination(imageProcessor)
    );
  }
}
