import time
import cv2
import mediapipe as mp                              
from mediapipe.tasks import python
from mediapipe.tasks.python import vision  
from hand import is_pointing, pointing_ray 

options = vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path="models/hand_landmarker.task"),
    running_mode = vision.RunningMode.VIDEO,
    num_hands=1)

landmarker = vision.HandLandmarker.create_from_options(options)
cap = cv2.VideoCapture(0)



while True: 
    ok, frame = cap.read()
    if not ok: 
        print("No frame received")
        break 

    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    timestamp_ms = int(time.monotonic() * 1000)
    result = landmarker.detect_for_video(mp_image, timestamp_ms)

    if result.hand_landmarks: 
        hand = result.hand_landmarks[0]
        label = result.handedness[0][0].category_name


        for point in hand:
            x = int(point.x * w)
            y = int(point.y * h)
            cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

 
        if is_pointing(hand):
            cv2.putText(frame, "Pointing", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            origin, direction = pointing_ray(hand, w, h)
            t = 20  # how many finger-lengths to extend the ray
            end = (int(origin[0] + t * direction[0]), int(origin[1] + t * direction[1]))
            cv2.line(frame, origin, end, (0, 0, 255), 2)
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)




    cv2.imshow('Camera', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()