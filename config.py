import os
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.getenv('ENDPOINT')
CLIENT_ID = os.getenv('CLIENT_ID')
CERT_FILEPATH = os.getenv('CERT_FILEPATH')
PRI_KEY_FILEPATH = os.getenv('PRI_KEY_FILEPATH')
CA_FILEPATH = os.getenv('CA_FILEPATH')
TOPIC_NAME = os.getenv('TOPIC_NAME')
LINE_TOKEN = os.getenv('LINE_TOKEN')
DETECT_CRITERIA = 120
