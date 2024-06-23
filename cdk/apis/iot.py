# パッケージディレクトリをPYTHONPATHに追加
import sys
import os
sys.path.append('/var/task/package')

import json
import boto3
import requests
import tempfile
import logging

# パッケージディレクトリをPYTHONPATHに追加
sys.path.append('/var/task/package')

def lambda_handler(event, context):
    # LINEのアクセストークンを環境変数から取得
    line_token = os.environ['LINE_TOKEN']
    print(f"LINE Token: {line_token}")  # トークンの値をログに出力（必要ならコメントアウト）

    # イベントからバケット名とオブジェクトキーを取得
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # S3クライアントを作成
    s3_client = boto3.client('s3')
    
    # S3から画像を取得
    print("EVENT: ", event)
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        print("RESPONSE: ", response)
        image_data = response['Body'].read()
    except Exception as e:
        print(f"Error getting object {object_key} from bucket {bucket_name}. Make sure they exist and your bucket is in the same region as this function.")
        print(e)
        raise e
    
    # 一時ファイルに画像を書き込む
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_image:
        tmp_image.write(image_data)
        tmp_image.flush()

    # LINE Notify API用のヘッダーとデータ
    headers = {'Authorization': f'Bearer {line_token}'}
    data = {'message': '検知しました。'}

    # 画像ファイルを送信
    with open(tmp_image.name, 'rb') as img_file:
        files = {'imageFile': img_file}
        response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=data, files=files)
        if response.status_code == 200:
            logging.info("Notification sent to LINE successfully")
        else:
            logging.error(f"Failed to send notification to LINE: {response.status_code}, {response.text}")

    # 一時ファイルを削除
    os.unlink(tmp_image.name)
    
    return {
        'statusCode': response.status_code,
        'body': response.text
    }
