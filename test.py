import cv2
import threading
from sshkeyboard import listen_keyboard, stop_listening
from awsiot import mqtt_connection_builder
import awscrt
import os
from dotenv import load_dotenv

def connect_to_aws_iot():
    # AWS IoTへの接続
    print('Begin Connect')
    global mqtt_connection
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        port=8883,
        client_id=CLIENT_ID,
        cert_filepath=CERT_FILEPATH,
        pri_key_filepath=PRI_KEY_FILEPATH,
        ca_filepath=CA_FILEPATH,
        keep_alive_secs=30)

    connect_future = mqtt_connection.connect()
    connect_future.result()
    print('Connected!')

def press(key):
    print(f"'{key}' pressed")
    if key == 'q':
        print("Quitting...")
        global keep_running
        keep_running = False
        stop_listening()
    if key == 's':
        print("Shot...")
        global shot
        shot = True

def listen_to_keyboard():
    listen_keyboard(
        on_press=press,
    )

def destroy():
    # リソースの解放
    cap.release()
    cv2.destroyAllWindows()
    # キーボードリスニングスレッドの終了を待つ
    global keep_running
    keep_running = False
    keyboard_thread.join()

def initAvg(frame):
    global avg
    global gray
    # グレースケールに変換
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 比較用のフレームを取得する
    if avg is None:
        avg = gray.copy().astype("float")
        return True
    return False

def detection(frame):
    global gray
    # ブラーを掛けてノイズを軽減する
    blur = cv2.GaussianBlur(gray, (1, 1), 1)
    # 現在のフレームと移動平均との差を計算
    cv2.accumulateWeighted(blur, avg, 0.7)
    frameDelta = cv2.absdiff(blur, cv2.convertScaleAbs(avg))
    # デルタ画像を閾値処理を行う
    thresh = cv2.threshold(frameDelta, 3, 255, cv2.THRESH_BINARY)[1]
    # 画像の閾値に輪郭線を入れる
    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    shot = False
    for i in range(0, len(contours)):
        if len(contours[i]) > 0:
            # しきい値より小さい領域は無視する
            if cv2.contourArea(contours[i]) < DETECT_CRITERIA:
                continue
            # 短形で領域を囲む
            rect = contours[i]
            x, y, w, h = cv2.boundingRect(rect)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
            shot = True
    return shot


def main():
    global mqtt_connection
    global avg
    connect_to_aws_iot()  # AWS IoTに接続
    # キーボードリスニングを別スレッドで開始
    keyboard_thread.start()
    avg = None
    while keep_running:
        global shot
        # カメラからの画像取得
        ret, frame = cap.read()
        if not ret:
            break
        
        if initAvg(frame):
            continue

        shot = detection(frame)
        if shot:
            print("a")
            # 画像をMQTTで送信
            # image_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
            # mqtt_connection.publish(
            #   topic=TOPIC_NAME,
            #   payload=image_bytes,
            #   qos=awscrt.mqtt.QoS.AT_LEAST_ONCE
            # )         
        if shot:
            shot = False
            # 画像をMQTTで送信
            image_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
            mqtt_connection.publish(
              topic=TOPIC_NAME,
              payload=image_bytes,
              qos=awscrt.mqtt.QoS.AT_LEAST_ONCE
            )

        # カメラの画像の出力
        cv2.imshow('Camera', frame)
        cv2.waitKey(500)
    destroy()

load_dotenv()


ENDPOINT=os.environ['ENDPOINT']
CLIENT_ID=os.environ['CLIENT_ID']
CERT_FILEPATH=os.environ['CERT_FILEPATH']
PRI_KEY_FILEPATH=os.environ['PRI_KEY_FILEPATH']
CA_FILEPATH=os.environ['CA_FILEPATH']
TOPIC_NAME=os.environ['TOPIC_NAME']
DETECT_CRITERIA=120

# 撮影の終了を判断するフラグ
keep_running = True
shot = False
# カメラの設定　デバイスIDは0
cap = cv2.VideoCapture(0)
# keyboardをコントトールするスレッド
keyboard_thread = threading.Thread(target=listen_to_keyboard)
if __name__ == '__main__':
    main()
