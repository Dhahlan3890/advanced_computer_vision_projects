import cv2
import mediapipe
import time
from HTModule import handDetector
import math
import numpy as np
import autopy
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))


#volume.GetMute()
#volume.GetMasterVolumeLevel()
range1 = volume.GetVolumeRange()
max_volume = range1[1]
min_volume = range1[0]
#volume.SetMasterVolumeLevel(-20.0, None)

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

alpha = 0.7  # Smoothing factor (adjust as needed)
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



def cursormove(frm, positions):
    
    point_finger = positions_list[8]
    middle_finger = positions_list[12]
    x_value, y_value = positions_list[8][1:]
    x = np.interp(x_value, (0, cam_width), (0, scr_width)) 
    y = np.interp(y_value, (0, cam_height), (0, scr_height))
    length = math.hypot((point_finger[1] - middle_finger[1]) + (point_finger[2] - middle_finger[2]))
    print(fingers_up(positions_list))
    if fingers_up(positions_list)[2] == 1 and fingers_up(positions_list)[3] == 0 and fingers_up(positions_list)[4] == 0 and fingers_up(positions_list)[5] == 0:
        #current_locy = prev_locx + (x - prev_locx) / smooth
        #current_locy = prev_locy + (y - prev_locy) / smooth
        x_smooth, y_smooth = smooth_update(x, y)
        
        cv2.circle(frame, positions_list[8][1:], 10, (0,255,0), cv2.FILLED)
        #autopy.mouse.move(scr_width - x, y)
        autopy.mouse.move(scr_width - x_smooth, y_smooth)
        #prev_locx, prev_locy = current_locx, current_locy

    elif fingers_up(positions_list)[2] == 1 and fingers_up(positions_list)[3] == 1 and fingers_up(positions_list)[4] == 0 and fingers_up(positions_list)[5] == 0 and length < 10:
        cv2.circle(frame, positions_list[8][1:], 10, (0,255,0), cv2.FILLED)
        cv2.circle(frame, positions_list[12][1:], 10, (0,255,0), cv2.FILLED)
        autopy.mouse.click()

def volumecontrol(frm, positions):
    
    point_finger = positions_list[8]
    thumb = positions_list[4]
    cv2.circle(frame, point_finger[1:], 10, (0,255,0), cv2.FILLED)
    cv2.circle(frame, thumb[1:], 10, (0,255,0), cv2.FILLED)
    cv2.line(frame, point_finger[1:], thumb[1:], (0, 255, 0), 2)
    line_length1 = math.hypot((point_finger[1] - thumb[1]) + (point_finger[2] - thumb[2]))
    line_length2= math.hypot((positions_list[2][1] - positions_list[5][1]) + (positions_list[2][2] - positions_list[5][2]))
    #line_length = line_length1-line_length2
    volume_level = np.interp(line_length1, [line_length2, line_length2*2], [min_volume, max_volume])
    #print(fingers_up(positions_list))
    if fingers_up(positions_list)[3] == 0 and fingers_up(positions_list)[4] == 0 and fingers_up(positions_list)[5] == 0 :
    #min = 20, max = 200
        volume.SetMasterVolumeLevel(int(volume_level), None)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break
    
    frame = detector.findHands(frame)
    positions_list = detector.findPosition(frame, draw=False)
    if len(positions_list) != 0:
        cursormove(frame, positions_list)
        volumecontrol(frame, positions_list)
    
    
    ctime = time.time()
    fps = 1/(ctime-ptime)
    ptime = ctime

    cv2.putText(frame, f'FPS: {int(fps)}', (20,40), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()