import cv2
import time
import sqlite3
from datetime import datetime
from ultralytics import YOLO
from test_video import VIDEO_PATH


# ============================================================
# SETTINGS
# ============================================================

DATABASE = "crowd_data.db"

SCAN_DURATION = 30

LOW_LIMIT = 10
MEDIUM_LIMIT = 30


# ============================================================
# SAVE DATA
# ============================================================

def save_live_data(people_count, restricted_count, status):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    cursor.execute("""
        INSERT INTO crowd_data
        (date, time, people_count, restricted_count, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        date,
        current_time,
        people_count,
        restricted_count,
        status
    ))

    conn.commit()
    conn.close()


# ============================================================
# CROWD LEVEL
# ============================================================

def get_crowd_level(people_count):

    if people_count <= LOW_LIMIT:
        return "LOW CROWD"

    elif people_count <= MEDIUM_LIMIT:
        return "MEDIUM CROWD"

    else:
        return "HIGH CROWD"


# ============================================================
# START
# ============================================================

print()
print("==============================================")
print(" SMART CROWD SAFETY & INTELLIGENCE PLATFORM")
print("==============================================")
print()


# ============================================================
# LOAD YOLO
# ============================================================

model = YOLO("yolo11n.pt")


# ============================================================
# SELECT INPUT MODE
# ============================================================

print("SELECT INPUT MODE")
print()

print("1 - LIVE CAMERA")
print("2 - CROWD DATASET / VIDEO")

print()

choice = input("Enter choice (1 or 2): ")


# ============================================================
# OPTION 1 - LIVE CAMERA
# ============================================================

if choice == "1":

    print()
    print("LIVE CAMERA MODE SELECTED")
    print()

    cap = cv2.VideoCapture(0)

    window_title = "Live Camera - Crowd Safety"


# ============================================================
# OPTION 2 - VIDEO
# ============================================================

elif choice == "2":

    print()
    print("CROWD DATASET / VIDEO MODE SELECTED")
    print()

    print("Using video:")
    print(VIDEO_PATH)
    print()

    cap = cv2.VideoCapture(VIDEO_PATH)

    window_title = "Dataset Video - Crowd Safety"


# ============================================================
# INVALID OPTION
# ============================================================

else:

    print()
    print("Invalid option.")
    exit()


# ============================================================
# CHECK CAMERA / VIDEO
# ============================================================

if not cap.isOpened():

    print()
    print("ERROR: Could not open selected source.")
    print()

    exit()


print("Input source opened successfully.")
print()


# ============================================================
# RESTRICTED ZONE
# ============================================================

zone_x1 = 270
zone_y1 = 150

zone_x2 = 530
zone_y2 = 400


# ============================================================
# TIMER
# ============================================================

start_time = time.time()

last_save_time = time.time()


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    # --------------------------------------------------------
    # READ FRAME
    # --------------------------------------------------------

    ret, frame = cap.read()

    if not ret:

        print()
        print("Input finished or frame could not be read.")
        break


    # --------------------------------------------------------
    # YOLO PERSON DETECTION
    # --------------------------------------------------------

    results = model(
        frame,
        classes=[0],
        conf=0.5,
        verbose=False
    )


    # --------------------------------------------------------
    # COUNTERS
    # --------------------------------------------------------

    person_count = 0
    restricted_count = 0


    # ========================================================
    # DRAW RESTRICTED ZONE
    # ========================================================

    cv2.rectangle(
        frame,
        (zone_x1, zone_y1),
        (zone_x2, zone_y2),
        (0, 0, 255),
        3
    )

    cv2.putText(
        frame,
        "RESTRICTED ZONE",
        (zone_x1, zone_y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2
    )


    # ========================================================
    # PERSON DETECTION
    # ========================================================

    for result in results:

        for box in result.boxes:

            # Class ID
            cls = int(box.cls[0])

            # Only person
            if cls != 0:
                continue

            person_count += 1


            # ------------------------------------------------
            # BOUNDING BOX
            # ------------------------------------------------

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )


            # ------------------------------------------------
            # PERSON CENTER
            # ------------------------------------------------

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2


            # =================================================
            # CHECK RESTRICTED ZONE
            # =================================================

            inside_zone = (

                zone_x1 <= center_x <= zone_x2

                and

                zone_y1 <= center_y <= zone_y2

            )


            # =================================================
            # PERSON INSIDE RESTRICTED ZONE
            # =================================================

            if inside_zone:

                restricted_count += 1


                # Red bounding box
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    3
                )


                # Restricted label
                cv2.putText(
                    frame,
                    "RESTRICTED",
                    (x1, max(y1 - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )


                # Center point
                cv2.circle(
                    frame,
                    (center_x, center_y),
                    5,
                    (0, 0, 255),
                    -1
                )


            # =================================================
            # NORMAL PERSON
            # =================================================

            else:

                # Green bounding box
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )


                # Person label
                cv2.putText(
                    frame,
                    "PERSON",
                    (x1, max(y1 - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )


                # Center point
                cv2.circle(
                    frame,
                    (center_x, center_y),
                    5,
                    (0, 255, 0),
                    -1
                )


    # ========================================================
    # CROWD LEVEL
    # ========================================================

    crowd_level = get_crowd_level(person_count)


    # ========================================================
    # STATUS
    # ========================================================

    if person_count > MEDIUM_LIMIT:

        if restricted_count > 0:

            status = "HIGH CROWD + RESTRICTED ALERT"

        else:

            status = "HIGH CROWD ALERT"

        status_color = (0, 0, 255)


    elif person_count > LOW_LIMIT:

        if restricted_count > 0:

            status = "MEDIUM CROWD + RESTRICTED ALERT"
            status_color = (0, 0, 255)

        else:

            status = "MEDIUM CROWD - MONITOR"
            status_color = (0, 165, 255)


    elif restricted_count > 0:

        status = "RESTRICTED ZONE VIOLATION"

        status_color = (0, 0, 255)


    else:

        status = "SAFE"

        status_color = (0, 255, 0)


    # ========================================================
    # PEOPLE COUNT
    # ========================================================

    cv2.putText(
        frame,
        f"People Count : {person_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 0, 0),
        2
    )


    # ========================================================
    # RESTRICTED COUNT
    # ========================================================

    cv2.putText(
        frame,
        f"Restricted Count : {restricted_count}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2
    )


    # ========================================================
    # CROWD LEVEL
    # ========================================================

    cv2.putText(
        frame,
        f"Crowd Level : {crowd_level}",
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        status_color,
        2
    )


    # ========================================================
    # STATUS
    # ========================================================

    cv2.putText(
        frame,
        f"Status : {status}",
        (20, 145),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        status_color,
        2
    )


    # ========================================================
    # MODE
    # ========================================================

    if choice == "1":

        mode_text = "Mode : LIVE CAMERA"

    else:

        mode_text = "Mode : DATASET VIDEO"


    cv2.putText(
        frame,
        mode_text,
        (20, 180),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # ========================================================
    # DATE AND TIME
    # ========================================================

    now = datetime.now()

    current_datetime = now.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cv2.putText(
        frame,
        current_datetime,
        (20, 215),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )


    # ========================================================
    # 30 SECOND TIMER
    # ========================================================

    elapsed_time = int(
        time.time() - start_time
    )

    remaining_time = SCAN_DURATION - elapsed_time

    cv2.putText(
        frame,
        f"Time Remaining : {max(remaining_time, 0)} sec",
        (20, 250),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # ========================================================
    # SAVE DATA EVERY SECOND
    # ========================================================

    if time.time() - last_save_time >= 1:

        save_live_data(
            person_count,
            restricted_count,
            status
        )

        last_save_time = time.time()

        print(
            f"Mode: "
            f"{'LIVE CAMERA' if choice == '1' else 'DATASET VIDEO'} | "
            f"People: {person_count} | "
            f"Restricted: {restricted_count} | "
            f"Crowd: {crowd_level} | "
            f"Status: {status}"
        )


    # ========================================================
    # SHOW FRAME
    # ========================================================

    cv2.imshow(
        window_title,
        frame
    )


    # ========================================================
    # STOP AFTER 30 SECONDS
    # ========================================================

    if elapsed_time >= SCAN_DURATION:

        print()
        print("30-second scan completed.")
        break


    # ========================================================
    # PRESS Q TO EXIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        print()
        print("Scan stopped manually.")
        break


# ============================================================
# RELEASE
# ============================================================

cap.release()

cv2.destroyAllWindows()

print()
print("Input source released.")