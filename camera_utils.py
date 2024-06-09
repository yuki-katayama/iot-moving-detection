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
    cv2.accumulateWeighted(gray, avg, 0.7)
    frame_delta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    thresh = cv2.threshold(frame_delta, 3, 255, cv2.THRESH_BINARY)[1]
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) < detect_criteria:
            continue
        logging.debug("Movement detected")
        return True
    return False
