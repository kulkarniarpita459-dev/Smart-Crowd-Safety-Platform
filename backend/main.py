from fastapi import FastAPI
import sqlite3

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Smart Crowd Safety Platform API"}

@app.get("/crowd-data")
def get_crowd_data():

    conn = sqlite3.connect("../crowd_data.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM crowd_data
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

    return data