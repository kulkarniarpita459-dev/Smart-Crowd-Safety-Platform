import sqlite3
from datetime import datetime

conn = sqlite3.connect("crowd_data.db")

cursor = conn.cursor()

now = datetime.now()

date = now.strftime("%Y-%m-%d")
time = now.strftime("%H:%M:%S")

people_count = 5
restricted_count = 2
status = "WARNING"

cursor.execute("""
INSERT INTO crowd_data
(date,time,people_count,restricted_count,status)

VALUES(?,?,?,?,?)

""",(date,time,people_count,restricted_count,status))

conn.commit()

conn.close()

print("Data Saved Successfully")