from flask import Flask, jsonify, Response
from flask_cors import CORS
import sqlite3
import cv2
import time
from datetime import datetime
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

DATABASE = "crowd_data.db"


# =========================================================
# YOLO MODEL
# =========================================================

model = YOLO("yolo11n.pt")


# =========================================================
# RESTRICTED ZONE
# =========================================================

zone_x1 = 270
zone_y1 = 150
zone_x2 = 530
zone_y2 = 400


# =========================================================
# CAMERA
# =========================================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Camera could not be opened.")
else:
    print("Camera opened successfully.")


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return "Smart Crowd Safety Backend is Running"


# =========================================================
# LATEST DATA
# =========================================================

@app.route("/api/latest")
def latest_data():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date, time, people_count,
               restricted_count, status
        FROM crowd_data
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return jsonify({
            "id": 0,
            "date": "",
            "time": "",
            "people_count": 0,
            "restricted_count": 0,
            "status": "SAFE"
        })

    return jsonify({
        "id": row[0],
        "date": row[1],
        "time": row[2],
        "people_count": row[3],
        "restricted_count": row[4],
        "status": row[5]
    })


# =========================================================
# DATABASE RECORDS
# =========================================================

@app.route("/api/records")
def records():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date, time, people_count,
               restricted_count, status
        FROM crowd_data
        ORDER BY id DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()

    conn.close()

    data = []

    for row in rows:

        data.append({
            "id": row[0],
            "date": row[1],
            "time": row[2],
            "people_count": row[3],
            "restricted_count": row[4],
            "status": row[5]
        })

    return jsonify(data)


# =========================================================
# SAVE DATA TO DATABASE
# =========================================================

def save_data(people_count, restricted_count, status):

    now = datetime.now()

    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO crowd_data
        (date, time, people_count,
         restricted_count, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        current_date,
        current_time,
        people_count,
        restricted_count,
        status
    ))

    conn.commit()
    conn.close()


# =========================================================
# LIVE YOLO CAMERA
# =========================================================

def generate_frames():

    # Start 30-second scan timer
    scan_start_time = time.time()

    # Save data every 5 seconds
    last_save_time = 0

    while True:

        # -------------------------------------------------
        # CHECK 30 SECOND LIMIT
        # -------------------------------------------------

        elapsed_time = time.time() - scan_start_time

        if elapsed_time >= 30:

            print("================================")
            print("30 SECOND SCAN COMPLETED")
            print("Scanning stopped.")
            print("================================")

            break


        # -------------------------------------------------
        # READ CAMERA
        # -------------------------------------------------

        success, frame = camera.read()

        if not success:

            print("ERROR: Could not read camera frame.")

            break


        # -------------------------------------------------
        # YOLO PERSON DETECTION
        # -------------------------------------------------

        results = model(
            frame,
            classes=[0],
            conf=0.5,
            verbose=False
        )


        person_count = 0
        restricted_count = 0


        # -------------------------------------------------
        # DRAW RESTRICTED ZONE
        # -------------------------------------------------

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
            0.7,
            (0, 0, 255),
            2
        )


        # -------------------------------------------------
        # PROCESS DETECTED PEOPLE
        # -------------------------------------------------

        for result in results:

            for box in result.boxes:

                cls = int(box.cls[0])

                # Class 0 = person
                if cls != 0:
                    continue


                person_count += 1


                # Bounding box
                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )


                # Person center
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2


                # -------------------------------------------------
                # CHECK RESTRICTED ZONE
                # -------------------------------------------------

                inside_zone = (
                    zone_x1 <= center_x <= zone_x2
                    and
                    zone_y1 <= center_y <= zone_y2
                )


                # -------------------------------------------------
                # PERSON INSIDE RESTRICTED ZONE
                # -------------------------------------------------

                if inside_zone:

                    restricted_count += 1


                    # RED BOX
                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 0, 255),
                        3
                    )


                    cv2.putText(
                        frame,
                        "RESTRICTED",
                        (x1, max(y1 - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )


                # -------------------------------------------------
                # NORMAL PERSON
                # -------------------------------------------------

                else:

                    # GREEN BOX
                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )


                    cv2.putText(
                        frame,
                        "Person",
                        (x1, max(y1 - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )


        # =================================================
        # STATUS
        # =================================================

        if restricted_count > 0:

            status = "WARNING"
            status_color = (0, 0, 255)

        else:

            status = "SAFE"
            status_color = (0, 255, 0)


        # =================================================
        # PEOPLE COUNT
        # =================================================

        cv2.putText(
            frame,
            f"People Count : {person_count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 0, 0),
            2
        )


        # =================================================
        # RESTRICTED COUNT
        # =================================================

        cv2.putText(
            frame,
            f"Restricted Count : {restricted_count}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )


        # =================================================
        # STATUS
        # =================================================

        cv2.putText(
            frame,
            f"Status : {status}",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            status_color,
            2
        )


        # =================================================
        # 30 SECOND TIMER
        # =================================================

        remaining_time = max(
            30 - int(elapsed_time),
            0
        )

        cv2.putText(
            frame,
            f"Time Remaining : {remaining_time} sec",
            (20, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )


        # =================================================
        # DATE AND TIME
        # =================================================

        now = datetime.now()

        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")

        cv2.putText(
            frame,
            f"{current_date} {current_time}",
            (20, 180),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )


        # =================================================
        # SAVE DATA EVERY 5 SECONDS
        # =================================================

        current_timestamp = time.time()

        if current_timestamp - last_save_time >= 5:

            save_data(
                person_count,
                restricted_count,
                status
            )

            last_save_time = current_timestamp


        # =================================================
        # CONVERT FRAME TO JPEG
        # =================================================

        ret, buffer = cv2.imencode(
            ".jpg",
            frame
        )

        if not ret:
            continue


        frame_bytes = buffer.tobytes()


        # =================================================
        # SEND FRAME TO BROWSER
        # =================================================

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )


    # =====================================================
    # RELEASE CAMERA AFTER 30 SECONDS
    # =====================================================

    camera.release()

    print("Camera released.")


# =========================================================
# VIDEO ROUTE
# =========================================================

@app.route("/video")
def video():

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# =========================================================
# RUN FLASK SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )