import os
import sys

sys.path.append('/var/task/package')
import requests
import tempfile
import logging

def lambda_handler(event, context):
    line_token = os.environ['LINE_TOKEN']
    image_data = event['body']['image_data'].encode('ISO-8859-1')  # エンコードされた文字列をバイナリに戻す
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_image:
        tmp_image.write(image_data)
        tmp_image.flush()

    headers = {'Authorization': f'Bearer {line_token}'}
    data = {'message': '検知しました。'}

    with open(tmp_image.name, 'rb') as img_file:
        files = {'imageFile': img_file}
        response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=data, files=files)
        if response.status_code == 200:
            logging.info("Notification sent to LINE successfully")
        else:
            logging.error(f"Failed to send notification to LINE: {response.status_code}, {response.text}")

    os.unlink(tmp_image.name)
    
    return {
        'statusCode': response.status_code,
        'body': response.text
    }
