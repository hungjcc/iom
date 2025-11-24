import sys, os
sys.path.insert(0, os.getcwd())
from db import get_auction
import json

def main():
    try:
        from db import get_auctions
        print('get_auction(23):')
        a = None
        try:
            a = get_auction(23)
        except Exception as e:
            print('get_auction error:', e)
        print(json.dumps(a, indent=2, default=str))

        print('\nSearching get_auctions for item_id=23 or title contains "23"...')
        try:
            all_ = get_auctions(limit=50)
            matches = [x for x in (all_ or []) if x.get('item_id') == 23 or ('23' in (str(x.get('title') or '')))]
            print(json.dumps(matches, indent=2, default=str))
        except Exception as e:
            print('get_auctions error:', e)
    except Exception as e:
        print('ERROR', e)

if __name__ == '__main__':
    main()
