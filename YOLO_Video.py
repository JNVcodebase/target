from ultralytics import YOLO
import cv2
import math
import threading
from playsound import playsound

# Flag to prevent overlapping alerts
alert_playing = False

def play_alert():
    """Play alert sound."""
    global alert_playing
    alert_playing = True
    playsound("static/alert.mp3", block=False)  # Path to the alert sound file
    alert_playing = False

def video_detection(path_x):
    video_capture = path_x
    cap = cv2.VideoCapture(video_capture)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    
    # Load the YOLO model
    model = YOLO("YOLO-Weights/ppe.pt")
    classNames = ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest', 'Person', 'Safety Cone',
                  'Safety Vest', 'machinery', 'vehicle']
    
    global alert_playing

    while True:
        success, img = cap.read()
        if not success:
            break

        results = model(img, stream=True)
        alert_triggered = False

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])
                class_name = classNames[cls]
                label = f'{class_name}{conf}'

                # Set bounding box colors
                if class_name == 'Mask' or class_name == 'Hardhat' or class_name == 'Safety Vest':
                    color = (0, 255, 0)
                elif class_name == 'NO-Hardhat' or class_name == 'NO-Mask' or class_name == 'NO-Safety Vest':
                    color = (0, 0, 255)
                    alert_triggered = True  # Alert condition
                elif class_name == 'machinery' or class_name == 'vehicle':
                    color = (0, 149, 255)
                else:
                    color = (85, 45, 255)

                # Draw bounding boxes and labels
                if conf > 0.5:
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
                    t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
                    c2 = x1 + t_size[0], y1 - t_size[1] - 3
                    cv2.rectangle(img, (x1, y1), c2, color, -1, cv2.LINE_AA)  # Filled box for text
                    cv2.putText(img, label, (x1, y1 - 2), 0, 1, [255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

        # Trigger alert sound
        if alert_triggered and not alert_playing:
            threading.Thread(target=play_alert).start()

        # Yield the processed frame
        yield img

    cap.release()
    cv2.destroyAllWindows()
