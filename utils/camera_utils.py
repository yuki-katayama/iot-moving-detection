import cv2
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# これを高くすることで閾値を鈍感にできる。
CRITERIA = 150
def capture_frame(cap):
    ret, frame = cap.read()
    if not ret:
        logging.error("Failed to capture frame")
        raise Exception("Failed to capture frame")
    # logging.debug("Frame captured successfully")
    return frame

def initialize_average(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)  # グレースケール変換後にブラーを適用
    avg = gray.copy().astype("float")
    logging.debug("Frame converted to grayscale and initialized for averaging")
    return avg, gray

def detect_movement(avg, gray, detect_criteria):
    # ブラーを掛けてノイズを軽減する
    try:
        gray = cv2.GaussianBlur(gray, (21, 21), 0)  # グレースケール変換後にブラーを適用
        cv2.accumulateWeighted(gray, avg, 0.1)  # 平均化のパラメータを調整
        frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
        thresh = cv2.threshold(frame_delta, CRITERIA, 255, cv2.THRESH_BINARY)[1]  # 閾値設定を調整
        contours, aa = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print("a" , contours, aa)
        for contour in contours:
            # len(contour)
            if cv2.contourArea(contour) < detect_criteria:
                continue
            logging.debug("Movement detected")
            return True
        return False
    except Exception as e:
        print(e)
