import cv2
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def capture_frame(cap):
    ret, frame = cap.read()
    if not ret:
        logging.error("Failed to capture frame")
        raise Exception("Failed to capture frame")
    # logging.debug("Frame captured successfully")
    return frame

def initialize_average(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    avg = gray.copy().astype("float")
    logging.debug("Frame converted to grayscale and initialized for averaging")
    return avg, gray

def detect_movement(avg, gray, detect_criteria):
    # ブラーを掛けてノイズを軽減する
    blur = cv2.GaussianBlur(gray, (1, 1), 1)
    cv2.accumulateWeighted(blur, avg, 0.7)
    frame_delta = cv2.absdiff(blur, cv2.convertScaleAbs(avg))
    thresh = cv2.threshold(frame_delta, 3, 255, cv2.THRESH_BINARY)[1]
    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    print("a" , contours)
    for contour in contours:
        len(contour)
        if cv2.contourArea(contour) < detect_criteria:
            continue
        logging.debug("Movement detected")
        return True
    return False
