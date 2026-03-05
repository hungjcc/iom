
import traceback
import os
import sys

# Ensure DB mode
os.environ['USE_DB'] = '1'

# Add project root to sys.path so imports from repo work when running from tools/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from db import create_item_and_auction
except Exception:
    traceback.print_exc()
    raise SystemExit(1)

try:
    print('Calling create_item_and_auction with sub_category="watch"...')
    res = create_item_and_auction('TEST_ITEM_AUTOTEST', 'auto-desc', seller_id=1, starting_price=5.0, sub_category='watch')
    print('Result:', res)
except Exception:
    traceback.print_exc()
    raise
