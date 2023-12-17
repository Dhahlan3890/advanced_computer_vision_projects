import cv2
import mediapipe as mp
import time
from FaceMeshModule import FaceMeshDetector

cap = cv2.VideoCapture('FaceVideo.mp4')
pTime = 0
detector = FaceMeshDetector(maxFaces=2)
while True:
    success, img = cap.read()
    img, faces = detector.findFaceMesh(img)
    if len(faces)!= 0:
        print(faces[0])
    cTime = time.time()
    if cTime != pTime:
        fps = 1 / (cTime - pTime)
    else:
        fps = 0 
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN,3, (0, 255, 0), 3)
    cv2.imshow('Image', img)
    if cv2.waitKey(1) == ord("q"):
        break
