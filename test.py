import cv2
import threading
from sshkeyboard import listen_keyboard, stop_listening
import time

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

def main():
    # キーボードリスニングを別スレッドで開始
    keyboard_thread.start()
    
    while keep_running:
        global shot
        # カメラからの画像取得
        ret, frame = cap.read()
        if not ret:
            break
        # カメラの画像の出力
        cv2.imshow('Camera', frame)
        cv2.waitKey(10)
        if shot:
            shot = False
            v_time = time.time()
            cv2.imwrite("./images/"+str(v_time)+".jpg", frame)
    destroy()

# 撮影の終了を判断するフラグ
keep_running = True
shot = False
# カメラの設定　デバイスIDは0
cap = cv2.VideoCapture(0)
# keyboardをコントトールするスレッド
keyboard_thread = threading.Thread(target=listen_to_keyboard)
if __name__ == '__main__':
    main()
