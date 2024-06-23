#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { IotStack } from '../lib/iot-stack';

const app = new cdk.App();

new IotStack(app, 'IotStack', {
  /* Uncomment the next line to specialize this stack for the AWS Account
   * and Region that are implied by the current CLI configuration. */
  env: {account: '008176221809', region: process.env.CDK_DEFAULT_REGION },
});