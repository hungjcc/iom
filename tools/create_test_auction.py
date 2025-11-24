from db import get_connection
import datetime

conn = get_connection()
cur = conn.cursor()
cur.execute("""
INSERT INTO auction (title, description, current_price, status, created_at)
VALUES (?, ?, ?, ?, ?)
""", ("TEST AUCTION", "Manual test", 1.00, 'O', datetime.datetime.utcnow()))
conn.commit()
try:
    print("Created auction id (driver-specific):", cur.lastrowid)
except:
    print("Inserted test auction; query to find it by title.")
cur.close()
conn.close()