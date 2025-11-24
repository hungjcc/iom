#!/usr/bin/env python
# tools/auto_place_bid.py
# Logs in as a user, posts a bid to a specific auction, and verifies DB rows.
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import requests
try:
    from db import get_connection
except Exception as e:
    print("Error importing db.get_connection:", e)
    raise

BASE = os.getenv('APP_URL', 'http://127.0.0.1:5000')
AUCTION_ID = int(os.getenv('AUCTION_ID', '3'))
USERNAME = os.getenv('TEST_USER', 'alice')
PASSWORD = os.getenv('TEST_PASS', 'TestPass123!')
BID_AMOUNT = os.getenv('BID_AMOUNT', '2.00')

session = requests.Session()

print(f"Logging in as {USERNAME} -> {BASE}/user_login")
login_resp = session.post(f"{BASE}/user_login", data={"username": USERNAME, "password": PASSWORD})
print("Login response status:", login_resp.status_code)
if login_resp.status_code not in (200, 302):
    print(login_resp.text[:800])

# Give server a moment to set session
time.sleep(0.3)

bid_url = f"{BASE}/auction/{AUCTION_ID}/bid"
print(f"Posting bid to {bid_url} amount={BID_AMOUNT}")
bid_resp = session.post(bid_url, data={"amount": BID_AMOUNT})
print("Bid POST status:", bid_resp.status_code)
print("Response snippet:\n", bid_resp.text[:1200])

# Verify in DB
print("\nVerifying DB entries...")
conn = get_connection()
cur = conn.cursor()
try:
    # Try common bid table name and schema
    cur.execute("SELECT TOP 10 * FROM bid WHERE auction_id = ? ORDER BY amount DESC, created_at DESC", (AUCTION_ID,))
    bids = cur.fetchall()
    print("Bids rows:")
    for b in bids:
        print(b)
except Exception as e:
    print("Querying bid table failed:", e)

try:
    cur.execute("SELECT a_id, a_item_id, a_s_price FROM auction WHERE a_id = ?", (AUCTION_ID,))
    auction_row = cur.fetchone()
    print("Auction row:", auction_row)
except Exception as e:
    print("Querying auction table failed:", e)

cur.close()
conn.close()
print("Done.")
