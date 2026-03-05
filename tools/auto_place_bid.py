#!/usr/bin/env python3
"""Log in via HTTP, place a bid, and verify rows in SQLite."""

from __future__ import annotations

import os
import sys
import time

import requests

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from db import get_connection

BASE = os.getenv('APP_URL', 'http://127.0.0.1:5000')
AUCTION_ID = int(os.getenv('AUCTION_ID', '1'))
USERNAME = os.getenv('TEST_USER', 'admin')
PASSWORD = os.getenv('TEST_PASS', 'TestPass123!')
BID_AMOUNT = os.getenv('BID_AMOUNT', '5.00')

session = requests.Session()

print(f"Logging in as {USERNAME} -> {BASE}/user_login")
resp = session.post(f"{BASE}/user_login", data={"username": USERNAME, "password": PASSWORD})
print("Login response status:", resp.status_code)
if resp.status_code not in (200, 302):
    print(resp.text[:800])

# Give server a moment to establish session
time.sleep(0.2)

bid_url = f"{BASE}/auction/{AUCTION_ID}/bid"
print(f"Posting bid to {bid_url} amount={BID_AMOUNT}")
bid_resp = session.post(bid_url, data={"amount": BID_AMOUNT})
print("Bid POST status:", bid_resp.status_code)
print("Response snippet:\n", bid_resp.text[:800])

print("\nVerifying DB entries...")
conn = get_connection()
try:
    rows = conn.execute(
        "SELECT b_id, b_amount, b_time, b_m_id FROM bid WHERE b_a_id = ? ORDER BY b_time DESC LIMIT 5",
        (AUCTION_ID,)
    ).fetchall()
    if not rows:
        print("No bids recorded.")
    for row in rows:
        print(dict(row))
    auction_row = conn.execute(
        "SELECT a_id, a_c_price, a_status FROM auction WHERE a_id = ?",
        (AUCTION_ID,)
    ).fetchone()
    print("Auction row:", dict(auction_row) if auction_row else None)
finally:
    conn.close()

print("Done.")
