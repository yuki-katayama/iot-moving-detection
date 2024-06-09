import requests
import tempfile
import cv2
import logging
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def line_notify(token, frame):
    _, buffer = cv2.imencode('.jpg', frame)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_image:
        tmp_image.write(buffer)
        tmp_image.flush()
        with open(tmp_image.name, 'rb') as img_file:
            files = {'imageFile': img_file}
            headers = {'Authorization': f'Bearer {token}'}
            data = {'message': '検知しました。'}
            response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=data, files=files)
            if response.status_code == 200:
                logging.info("Notification sent to LINE successfully")
            else:
                logging.error("Failed to send notification to LINE")
    os.unlink(tmp_image.name)
    return response.text
