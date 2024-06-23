from config import *
from utils.camera_utils import capture_frame, initialize_average, detect_movement
from utils.mqtt_utils import connect_to_aws_iot, publish_image
from utils.line_notify_utils import line_notify
from utils.keyboard_utils import listen_to_keyboard
import cv2
import threading
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def on_key_press(key):
    global keep_running, shot
    if key == 'q':
        logging.debug("終了します...")
        keep_running = False
    if key == 's':
        logging.debug("手動で撮影をトリガーしました。")
        shot = True

def destroy(cap, mqtt_connection):
    logging.debug("リソースを解放中...")
    cap.release()
    cv2.destroyAllWindows()
    mqtt_connection.disconnect()
    logging.debug("リソースの解放完了。")

def main():
    global keep_running, shot
    keep_running = True
    shot = False
    cap = cv2.VideoCapture(0)
    mqtt_connection = connect_to_aws_iot(ENDPOINT, CLIENT_ID, CERT_FILEPATH, PRI_KEY_FILEPATH, CA_FILEPATH)
    
    # Start listening to keyboard in a separate thread
    keyboard_thread = threading.Thread(target=listen_to_keyboard, args=(on_key_press, lambda: keep_running))
    keyboard_thread.start()

    avg = None
    try:
        while keep_running:
            frame = capture_frame(cap)
            if avg is None:
                avg, gray = initialize_average(frame)
                continue
            if detect_movement(avg, gray, DETECT_CRITERIA):
                logging.debug("動体を検出しました！")
                line_notify(LINE_TOKEN, frame)
                publish_image(mqtt_connection, TOPIC_NAME, frame)
            if shot:
                shot = False
                logging.debug("手動撮影がトリガーされました。")
                publish_image(mqtt_connection, TOPIC_NAME, frame)
            cv2.imshow('Camera', frame)
            cv2.waitKey(1)
    finally:
        destroy(cap, mqtt_connection)
        keyboard_thread.join()  # キーボードスレッドの終了を待つ
if __name__ == '__main__':
    main()