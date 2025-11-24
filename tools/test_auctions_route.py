# Quick test script to verify /auctions route
import traceback
import os, sys

# Ensure project root is on sys.path when running this script from tools/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from app import app

    with app.test_client() as c:
        r = c.get('/auctions')
        print('Status:', r.status_code)
        print('Length:', len(r.data))
        print('\n--- Response snippet ---\n')
        print(r.data.decode('utf-8')[:800])
except Exception:
    traceback.print_exc()
