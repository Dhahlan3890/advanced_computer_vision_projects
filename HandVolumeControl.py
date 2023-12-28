import cv2
import mediapipe
import time
from HTModule import handDetector
import math
import numpy as np

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

cam_width, cam_height = 800, 400

cap = cv2.VideoCapture(0)

cap.set(3, cam_width)
cap.set(4, cam_height)
detector = handDetector(maxHands=1)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()



ptime = 0

def fingers_up(positions):
    fingers = []
    for i in range(6):
        if positions[4*i-2][2] > positions[4*i][2]:
            fingers.append(1)
        else:
            fingers.append(0)
    
    return fingers

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