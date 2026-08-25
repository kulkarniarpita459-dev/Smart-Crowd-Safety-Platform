from ultralytics import YOLO
import cv2
import sqlite3
from datetime import datetime
import time

# Load YOLO11 model
model = YOLO("yolo11n.pt")

# Connect Database
conn = sqlite3.connect("crowd_data.db")
cursor = conn.cursor()

# Open Webcam
cap = cv2.VideoCapture(0)

last_save_time = time.time()

while True:

    ret, frame = cap.read()

    if not ret:
        break

    height, width, _ = frame.shape

    # Restricted Zone
    zone_x1 = width // 2 - 100
    zone_y1 = height // 2 + 20

    zone_x2 = width // 2 + 100
    zone_y2 = height - 80

    cv2.rectangle(frame,
                  (zone_x1, zone_y1),
                  (zone_x2, zone_y2),
                  (0, 0, 255),
                  2)

    cv2.putText(frame,
                "RESTRICTED ZONE",
                (zone_x1, zone_y1 - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2)

    # Detect Persons
    results = model(frame, classes=[0], conf=0.5)

    person_count = 0
    restricted_count = 0

    for result in results:

        for box in result.boxes:

            cls = int(box.cls[0])

            if cls == 0:

                person_count += 1

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                if (zone_x1 <= center_x <= zone_x2) and (zone_y1 <= center_y <= zone_y2):

                    restricted_count += 1
                    color = (0, 0, 255)
                    label = "Restricted"

                else:

                    color = (0, 255, 0)
                    label = "Person"

                cv2.rectangle(frame,
                              (x1, y1),
                              (x2, y2),
                              color,
                              2)

                cv2.circle(frame,
                           (center_x, center_y),
                           5,
                           (255, 0, 0),
                           -1)

                cv2.putText(frame,
                            label,
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            color,
                            2)

    # Risk Level
    if restricted_count <= 2:
        status = "SAFE"
        status_color = (0, 255, 0)

    elif restricted_count <= 5:
        status = "WARNING"
        status_color = (0, 255, 255)

    else:
        status = "HIGH ALERT"
        status_color = (0, 0, 255)

    # Display Information
    cv2.putText(frame,
                f"People Count : {person_count}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 0),
                2)

    cv2.putText(frame,
                f"Restricted Count : {restricted_count}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2)

    cv2.putText(frame,
                f"Status : {status}",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                status_color,
                2)

    if restricted_count > 5:

        cv2.putText(frame,
                    "OVERCROWDING DETECTED!",
                    (70, 170),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    3)

    # Save data every 5 seconds
    current_time = time.time()

    if current_time - last_save_time >= 5:

        now = datetime.now()

        date = now.strftime("%Y-%m-%d")
        current_clock = now.strftime("%H:%M:%S")

        cursor.execute("""
        INSERT INTO crowd_data
        (date, time, people_count, restricted_count, status)
        VALUES (?, ?, ?, ?, ?)
        """, (date,
              current_clock,
              person_count,
              restricted_count,
              status))

        conn.commit()

        print("Data Saved Successfully")

        last_save_time = current_time

    cv2.imshow("Overcrowding Alert System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
conn.close()
cv2.destroyAllWindows()