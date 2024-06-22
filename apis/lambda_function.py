import json
import boto3
import os
import requests

def lambda_handler(event, context):
    # LINEのアクセストークンを環境変数から取得
    line_token = os.environ['LINE_TOKEN']
    
    # イベントからバケット名とオブジェクトキーを取得
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # S3クライアントを作成
    s3_client = boto3.client('s3')
    
    # S3から画像を取得
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        image_data = response['Body'].read()
    except Exception as e:
        print(f"Error getting object {object_key} from bucket {bucket_name}. Make sure they exist and your bucket is in the same region as this function.")
        print(e)
        raise e
    
    # LINE Messaging API用のヘッダー
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {line_token}'
    }
    
    # LINE Messaging APIのエンドポイント
    line_endpoint = 'https://api.line.me/v2/bot/message/push'
    
    # LINEへのリクエストボディを作成
    body = {
        "to": "ユーザーまたはグループID",
        "messages": [{
            "type": "image",
            "originalContentUrl": f"https://{bucket_name}.s3.amazonaws.com/{object_key}",
            "previewImageUrl": f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
        }]
    }
    
    # LINEへのリクエストを送信
    try:
        response = requests.post(line_endpoint, headers=headers, data=json.dumps(body))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message to LINE: {e}")
        raise e
    
    return {
        'statusCode': 200,
        'body': json.dumps('Message sent successfully!')
    }
