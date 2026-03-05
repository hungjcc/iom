# tools/create_item_and_auction.py
import os
import sys
import datetime

# Ensure the project root (one level up) is on sys.path so imports like `from db import ...` work
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from db import get_connection

conn = get_connection()
cur = conn.cursor()

# 1) Insert an item (adjust i_m_id to a valid member id if needed)
cur.execute("""
INSERT INTO item (i_m_id, i_title, i_desc, i_b_price, i_duration, i_status, created_at)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", (1, "TEST ITEM - Manual", "Created for bid test", 1.00, 7, 'P', datetime.datetime.utcnow()))
conn.commit()

# Get the new item id (driver-specific)
try:
    item_id = cur.lastrowid
except Exception:
    # fallback: query by title (less safe if title not unique)
    cur.execute("SELECT TOP 1 i_id FROM item WHERE i_title = ? ORDER BY created_at DESC", ("TEST ITEM - Manual",))
    item_id = cur.fetchone()[0]

print("Inserted item id:", item_id)

# 2) Insert auction referencing the item
cur.execute("""
INSERT INTO auction (a_item_id, a_m_id, a_s_price, a_s_date)
VALUES (?, ?, ?, ?)
""", (item_id, None, 1.00, datetime.datetime.utcnow()))
conn.commit()
try:
    auction_id = cur.lastrowid
except Exception:
    cur.execute("SELECT TOP 1 a_id FROM auction WHERE a_item_id = ? ORDER BY a_s_date DESC", (item_id,))
    auction_id = cur.fetchone()[0]

print("Inserted auction id:", auction_id)

cur.close()
conn.close()