#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { IotStack } from '../lib/iot-stack';
import { IotStepFunctionStack } from '../lib/iot-step-function-stack';

const app = new cdk.App();

const iotStack = new IotStack(app, 'IotStack', {
  env: {account: '008176221809', region: process.env.CDK_DEFAULT_REGION },
});

new IotStepFunctionStack(app, 'IotStepFunctionStack', {
  env: {account: '008176221809', region: process.env.CDK_DEFAULT_REGION },
  bucketName: iotStack.iotBucket.bucketName,
});