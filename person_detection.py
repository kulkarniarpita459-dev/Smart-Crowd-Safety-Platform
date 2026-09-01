from ultralytics import YOLO
import cv2

# Load YOLO11 model
model = YOLO("yolo11n.pt")

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Detect only persons
    results = model(frame, classes=[0], conf=0.5)

    # Draw only person detections
    annotated_frame = results[0].plot()

    # Display output
    cv2.imshow("Person Detection", annotated_frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
