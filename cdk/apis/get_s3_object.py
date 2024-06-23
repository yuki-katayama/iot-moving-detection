import sys
sys.path.append('/var/task/package')

import boto3
import json

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    bucket_name = event['bucket_name']
    object_key = event['object_key']
    
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    image_data = response['Body'].read()
    
    return {
        'statusCode': 200,
        'body': {
            'bucket_name': bucket_name,
            'object_key': object_key,
            'image_data': image_data.decode('ISO-8859-1')  # バイナリデータを文字列としてエンコード
        }
    }
