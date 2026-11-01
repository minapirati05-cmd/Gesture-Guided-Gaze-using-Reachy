from ultralytics import YOLO

model = YOLO("yolov8n.pt")  
min_confidence = 0.5  # Minimum confidence threshold for detections
ignored_labels = {"person"}


def detect_objects(frame):
    '''
    Detect objects in the given frame using YOLOv8 model.
    Args:
        frame (numpy.ndarray): The input image frame in BGR format.
        Returns:
            List of detections, where each detection is a dictionary containing:
            - 'bbox': Bounding box coordinates (x1, y1, x2, y2)
            - 'label': Detected object label
            - 'confidence': Confidence score of the detection'''
    # Perform object detection
    results = model(frame, verbose = False)
    
    # Extract bounding boxes and labels
    detections = []


    for box in results[0].boxes: 
        confidence = float(box.conf[0])
        label = model.names[int(box.cls[0])]

        if confidence < min_confidence or label in ignored_labels:
            continue  # Skip detections below the confidence threshold or ignored labels    

        x1, y1, x2, y2 = box.xyxy[0].tolist() 

        detections.append({
            'bbox': (int(x1), int(y1), int(x2), int(y2)),
            'label': label,
            'confidence': confidence
        })
    return detections