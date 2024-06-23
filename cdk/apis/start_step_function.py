import sys
import os
sys.path.append('/var/task/package')

import json
import boto3

def lambda_handler(event, context):
    sfn_client = boto3.client('stepfunctions')
    state_machine_arn = os.environ['STATE_MACHINE_ARN']  # Step FunctionsのARNを環境変数から取得
    
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        
        input = {
            "bucket_name": bucket_name,
            "object_key": object_key
        }
        
        response = sfn_client.start_execution(
            stateMachineArn=state_machine_arn,
            input=json.dumps(input)
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Step Function started successfully!')
    }
