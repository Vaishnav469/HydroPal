import cv2
import torch
import time

metric = 0 #global variable to track the value

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # or 'yolov5m', 'yolov5l', 'yolov5x'

# Initialize video capture (0 is usually the built-in webcam)
cap = cv2.VideoCapture(0)

# Global variable to track the start time of the "Drinking Water" condition
drinking_start_time = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to RGB (OpenCV uses BGR by default)
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Perform inference
    results = model(img_rgb)

    #need to hold bottle and bound person boxes in lists
    bottles = []
    persons = []

    # Parse results
    for box in results.xyxy[0]:  # xyxy format
        x1, y1, x2, y2, confidence, class_id = box[:6]
        label = model.names[int(class_id)]

        if confidence > 0.5 and label == "bottle":  # Confidence threshold and class check
            bottles.append((int(x1), int(y1), int(x2), int(y2)))
            label_text = f'{label} {confidence:.2f}'
            # Draw the bounding box and label on the frame
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            cv2.putText(frame, label_text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        if confidence > 0.5 and label == "person":  # Confidence threshold and class check
            persons.append((int(x1), int(y1), int(x2), int(y2)))
            label_text = f'{label} {confidence:.2f}'
            # Draw the bounding box and label on the frame
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            cv2.putText(frame, label_text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    drinking_detected = False
    # Checking if the center of the bottle is inside 50% inward center of the person box
    for (bx1, by1, bx2, by2) in bottles:
        bottle_center_x = (bx1 + bx2) // 2
        bottle_center_y = (by1 + by2) // 2

        for (px1, py1, px2, py2) in persons:
            # Calculate the center of the person's bounding box
            person_center_x = (px1 + px2) // 2
            person_center_y = (py1 + py2) // 2

            # Calculate the range for "near the center" check
            center_margin_x = (px2 - px1) * 0.25  # 25% of the width from the center
            center_margin_y = (py2 - py1) * 0.25  # 25% of the height from the center

            if (person_center_x - center_margin_x < bottle_center_x < person_center_x + center_margin_x) and \
               (person_center_y - center_margin_y < bottle_center_y < person_center_y + center_margin_y):
                drinking_detected = True
                if drinking_start_time is None:
                    drinking_start_time = time.time() 
                elif time.time() - drinking_start_time > 3:
                    cv2.putText(frame, 'Drinking Water', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    metric += 2
                    drinking_start_time = None #taking it back to None
                    print("Drank for more than 3 sec")
                break
    
    # Display the frame
    cv2.imshow('YOLOv5 Bottle Detection', frame)

    # checking if the bounding box of the bottle is inside the bounding box of the person

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()



