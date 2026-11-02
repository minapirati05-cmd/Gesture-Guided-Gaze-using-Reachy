import time
import cv2
import mediapipe as mp                              
from mediapipe.tasks import python
from mediapipe.tasks.python import vision  
from hand import is_pointing, pointing_ray 

from objects import detect_objects

from selector import box_center, select_target 

from robot import pixel_head_angles


from reachy_mini import ReachyMini                 
from reachy_mini.utils import create_head_pose  

options = vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path="models/hand_landmarker.task"),
    running_mode = vision.RunningMode.VIDEO,
    num_hands=1)

landmarker = vision.HandLandmarker.create_from_options(options)



stable_frames = 8 
head_move_duration = 0.5 


with ReachyMini(media_backend="no_media") as mini:
    mini.goto_target(head=create_head_pose(), duration=1.0)

    cap = cv2.VideoCapture(0)

    candidate_label = None 
    stable_count = 0 
    announced_label = None 

    try: 

        while True: 
            ok, frame = cap.read()
            if not ok: 
                print("No frame received")
                break 
            frame = cv2.flip(frame, 1)   # mirror horizontally so the preview feels natural

            h, w = frame.shape[:2]
            current_target = None 
            pointing_now = False 
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            timestamp_ms = int(time.monotonic() * 1000)
            result = landmarker.detect_for_video(mp_image, timestamp_ms)
            objects = detect_objects(frame)

            for obj in objects: 
                x1, y1, x2, y2 = obj['bbox']
                label = obj['label']
                confidence = obj['confidence']
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, f"{label} ({confidence:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            if result.hand_landmarks: 
                hand = result.hand_landmarks[0]
            

                for point in hand:
                    x = int(point.x * w)
                    y = int(point.y * h)
                    cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

        
                if is_pointing(hand):
                    pointing_now = True 
                    cv2.putText(frame, "Pointing", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    origin, direction = pointing_ray(hand, w, h)

                    target, status = select_target(origin, direction, objects)
                    if status == "target":
                        current_target = target
                        # Highlight the chosen object: thick green box + its name
                        cx, cy = box_center(target["bbox"])
                        yaw, pitch = pixel_head_angles(cx, cy, w, h)
                        print(f"yaw={yaw:.1f} pitch={pitch:.1f}")
                        x1, y1, x2, y2 = target["bbox"]
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
                        cv2.putText(frame, f"Target: {target['label']}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


                    elif status == "ambiguous":
                        cv2.putText(frame, "Unclear - point more precisely", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
                    else:
                        cv2.putText(frame, "No target", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    t = 20  # how many finger-lengths to extend the ray
                    end = (int(origin[0] + t * direction[0]), int(origin[1] + t * direction[1]))
                    cv2.line(frame, origin, end, (0, 0, 255), 2)

            # --- Stability rule: act only on a target that is stable and new ---
            if current_target is not None:
                label = current_target["label"]
                if label == candidate_label:
                    stable_count += 1
                else:
                    candidate_label = label
                    stable_count = 1

                if stable_count >= stable_frames and label != announced_label:
                    mini.goto_target(
                        head=create_head_pose(yaw=yaw, pitch=pitch, degrees=True),
                        duration= head_move_duration,
                    )
                    announced_label = label
            else:
                # ambiguous, no target, or not pointing: the streak is broken
                candidate_label = None
                stable_count = 0

            if not pointing_now:
                # hand lowered: allow the same object to be named again next time
                announced_label = None

            cv2.imshow('Camera', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        mini.goto_target(head=create_head_pose(), duration=1.0) 