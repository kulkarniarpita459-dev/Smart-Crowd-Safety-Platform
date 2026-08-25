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

    person_count = 0

    for result in results:

        for box in result.boxes:

            cls = int(box.cls[0])

            if cls == 0:

                person_count += 1

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

    # Crowd Density Logic
    if person_count <= 5:
        density = "LOW"
        color = (0,255,0)

    elif person_count <= 15:
        density = "MEDIUM"
        color = (0,255,255)

    else:
        density = "HIGH"
        color = (0,0,255)

    # Display People Count
    cv2.putText(frame,
                f"People Count : {person_count}",
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255,0,0),
                2)

    # Display Crowd Density
    cv2.putText(frame,
                f"Crowd Density : {density}",
                (20,80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color,
                2)

    cv2.imshow("Crowd Density Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()