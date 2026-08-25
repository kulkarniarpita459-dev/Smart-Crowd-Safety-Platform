import sqlite3

conn = sqlite3.connect("crowd_data.db")
cursor = conn.cursor()

print("Database columns:")

cursor.execute("PRAGMA table_info(crowd_data)")

columns = cursor.fetchall()

for column in columns:
    print(column)

print("\nLive Crowd Records:")

cursor.execute("""
    SELECT id, date, time, people_count, restricted_count, status
    FROM crowd_data
    ORDER BY id DESC
    LIMIT 20
""")

rows = cursor.fetchall()

if not rows:
    print("No records found.")
else:
    for row in rows:
        print(row)

conn.close()