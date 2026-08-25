from ultralytics import YOLO
import cv2

# Load YOLO11 model
model = YOLO("yolo11n.pt")

# Open webcam
cap = cv2.VideoCapture(0)

while True:

    # Read one frame
    ret, frame = cap.read()

    if not ret:
        break

    # Detect only persons
    results = model(frame, classes=[0], conf=0.5)

    # Start counting
    person_count = 0

    # Go through all detections
    for result in results:

        for box in result.boxes:

            cls = int(box.cls[0])

            if cls == 0:

                person_count += 1

                # Draw bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cv2.rectangle(frame,
                              (x1, y1),
                              (x2, y2),
                              (0,255,0),
                              2)

                cv2.putText(frame,
                            "Person",
                            (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0,255,0),
                            2)

    # Display total count
    cv2.putText(frame,
                f"People Count : {person_count}",
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,0,255),
                2)

    cv2.imshow("People Counting", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()