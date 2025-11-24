"""
Update the auction's a_s_price (starting/current price) for testing.
Usage:
  python tools/update_auction_price.py [auction_id] [price]
Defaults: auction_id=5, price=130.00
"""
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from db import get_connection
except Exception:
    print('Failed to import get_connection from db.py')
    traceback.print_exc()
    sys.exit(1)

auction_id = int(sys.argv[1]) if len(sys.argv) > 1 else 5
price = float(sys.argv[2]) if len(sys.argv) > 2 else 130.00

try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE dbo.auction SET a_s_price = ? WHERE a_id = ?", (price, auction_id))
    conn.commit()
    print(f'Updated auction {auction_id} a_s_price -> {price}. Rows affected: {cur.rowcount}')
except Exception:
    traceback.print_exc()
finally:
    try:
        conn.close()
    except Exception:
        pass
