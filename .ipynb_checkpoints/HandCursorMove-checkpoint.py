import cv2
import mediapipe
import time
from HTModule import handDetector
import math
import numpy as np
import autopy


cam_width, cam_height = 683, 384
scr_width, scr_height = autopy.screen.size()
#print(scr_width, scr_height)
cap = cv2.VideoCapture(0)
cap.set(3, cam_width)
cap.set(4, cam_height)

detector = handDetector(maxHands=1)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

ptime = 0

smooth = 3
prev_locx, prev_locy = 0, 0
current_locx, current_locy = 0,0

alpha = 0.5  # Smoothing factor (adjust as needed)
smoothed_x, smoothed_y = 0, 0

def smooth_update(x, y):
    global smoothed_x, smoothed_y
    smoothed_x = alpha * smoothed_x + (1 - alpha) * x
    smoothed_y = alpha * smoothed_y + (1 - alpha) * y
    return int(smoothed_x), int(smoothed_y)

def fingers_up(positions):
    fingers = []
    for i in range(6):
        if positions[4*i-2][2] > positions[4*i][2]:
            fingers.append(1)
        else:
            fingers.append(0)
    
    return fingers

def point_up(positions):
    y_values = []
    y_values.append(positions[:][:][2])
    max_y = np.max(y_values)
    min_y = np.min(y_values)
    if positions[:][8][2] < max_y - ((max_y-min_y)/5):
        return 1
    return 0

def middle_up(positions):
    y_values = []
    y_values.append(positions[:][:][2])
    max_y = np.max(y_values)
    min_y = np.min(y_values)
    if positions[:][12][2] < max_y - ((max_y-min_y)/5):
        return 1
    return 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break
    
    frame = detector.findHands(frame)
    positions_list = detector.findPosition(frame, draw=False)
    if len(positions_list) != 0:
        point_finger = positions_list[8]
        middle_finger = positions_list[12]
        x_value, y_value = positions_list[8][1:]
        x = np.interp(x_value, (0, cam_width), (0, scr_width)) 
        y = np.interp(y_value, (0, cam_height), (0, scr_height))
        length = math.hypot((point_finger[1] - middle_finger[1]) + (point_finger[2] - middle_finger[2]))
        print(fingers_up(positions_list))
        if fingers_up(positions_list)[2] == 1 and fingers_up(positions_list)[3] == 0:
            #current_locy = prev_locx + (x - prev_locx) / smooth
            #current_locy = prev_locy + (y - prev_locy) / smooth
            x_smooth, y_smooth = smooth_update(x, y)
            
            cv2.circle(frame, positions_list[8][1:], 10, (0,255,0), cv2.FILLED)
            #autopy.mouse.move(scr_width - x, y)
            autopy.mouse.move(scr_width - x_smooth, y_smooth)
            #prev_locx, prev_locy = current_locx, current_locy

        if fingers_up(positions_list)[2] == 1 and fingers_up(positions_list)[3] == 1 and length < 20:
            cv2.circle(frame, positions_list[8][1:], 10, (0,255,0), cv2.FILLED)
            cv2.circle(frame, positions_list[12][1:], 10, (0,255,0), cv2.FILLED)
            autopy.mouse.click()
    
    
    ctime = time.time()
    fps = 1/(ctime-ptime)
    ptime = ctime

    cv2.putText(frame, f'FPS: {int(fps)}', (20,40), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()