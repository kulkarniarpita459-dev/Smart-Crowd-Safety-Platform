from ultralytics import YOLO
import cv2
from database import insert_data

model = YOLO("yolo11n.pt")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    height, width, _ = frame.shape

    zones = {
        "Zone 1": (0, 0, width//2, height//2),
        "Zone 2": (width//2, 0, width, height//2),
        "Zone 3": (0, height//2, width//2, height),
        "Zone 4": (width//2, height//2, width, height)
    }

    zone_count = {
        "Zone 1": 0,
        "Zone 2": 0,
        "Zone 3": 0,
        "Zone 4": 0
    }

    results = model(frame)

    for result in results:
        for box in result.boxes:

            cls = int(box.cls[0])

            if cls == 0:   # Person detection

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                for zone, (zx1, zy1, zx2, zy2) in zones.items():

                    if zx1 < cx < zx2 and zy1 < cy < zy2:
                        zone_count[zone] += 1


    # Store data in database
    for zone, count in zone_count.items():

        if count > 10:
            status = "ALERT"
        else:
            status = "SAFE"

        insert_data(zone, count, status)


    # Display zones
    for zone, (x1, y1, x2, y2) in zones.items():

        count = zone_count[zone]

        if count > 10:
            status = "ALERT"
            color = (0, 0, 255)
        else:
            status = "SAFE"
            color = (0, 255, 0)

        cv2.rectangle(frame,
                      (x1, y1),
                      (x2, y2),
                      color,
                      2)

        cv2.putText(frame,
                    f"{zone}: {count} {status}",
                    (x1 + 10, y1 + 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2)


    cv2.imshow("Smart Crowd Safety - Zone Monitoring", frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
