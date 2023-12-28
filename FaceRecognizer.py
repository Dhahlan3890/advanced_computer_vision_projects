import cv2
import mediapipe as mp
import time
from FaceRecognitionModule import FaceDetector

cap = cv2.VideoCapture("FaceVideo.mp4")
pTime = 0
detector = FaceDetector()
while True:
    success, img = cap.read()
    img, bboxs = detector.findFaces(img)
    print(bboxs)

    cTime = time.time()
    if cTime != pTime:
        fps = 1 / (cTime - pTime)
    else:
        fps = 0 
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)
    cv2.imshow("Image", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()