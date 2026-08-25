import sqlite3

# Connect to database
conn = sqlite3.connect("crowd_data.db")

cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS crowd_data(

id INTEGER PRIMARY KEY AUTOINCREMENT,

date TEXT,

time TEXT,

people_count INTEGER,

restricted_count INTEGER,

status TEXT

)
""")

conn.commit()

conn.close()

print("Database Created Successfully")