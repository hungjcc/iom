import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from db import get_auction, get_auctions

aucs = get_auctions(limit=10)
for a in aucs:
    print('a_id', a.get('id'), 'start', a.get('start_date'), 'end', a.get('end_time'), 'duration', a.get('duration'), 'status', a.get('status'), 'current_bid', a.get('current_bid'))

print('\nSingle auction detail for id=58')
a = get_auction(58)
print(a)
