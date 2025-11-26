"""
Insert a short auction with end_date = now + 23 hours for duration rounding verification.
Run this script from project root inside the venv:
  & ".\.env\Scripts\Activate.ps1"; python tools\insert_short_auction.py
"""
import sys, os
from datetime import datetime, timedelta

# ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from db import create_item_and_auction

try:
    end_dt = datetime.utcnow() + timedelta(hours=23)
    # Use small unique title
    title = 'DURATION_TEST_23H'
    desc = 'Auto test: end in 23 hours'
    seller_id = None
    starting_price = 1.0

    result = create_item_and_auction(title, desc, seller_id=seller_id, starting_price=starting_price, end_date=end_dt)
    if not result:
        print('create_item_and_auction returned None (failed)')
        sys.exit(2)
    auction_id, item_id = result
    print(f'Inserted auction id={auction_id}, item id={item_id}, end_date={end_dt.isoformat()}')
    sys.exit(0)
except Exception as e:
    print('Error inserting short auction:', e)
    sys.exit(3)
