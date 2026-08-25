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

    # Track persons
    results = model.track(
        frame,
        persist=True,
        classes=[0],
        conf=0.5
    )

    person_count = 0

    for result in results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            person_count += 1

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Tracking ID
            if box.id is not None:
                track_id = int(box.id[0])
            else:
                track_id = -1

            # Draw box
            cv2.rectangle(frame,
                          (x1, y1),
                          (x2, y2),
                          (0,255,0),
                          2)

            # Label with ID
            cv2.putText(frame,
                        f"Person {track_id}",
                        (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0,255,0),
                        2)

    cv2.putText(frame,
                f"People Count : {person_count}",
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255,0,0),
                2)

    cv2.imshow("Person Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()