"""
Set an item's i_duration to NULL.
Usage: python tools\set_item_duration_null.py <item_id>
"""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from db import get_connection

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python tools\\set_item_duration_null.py <item_id>')
        sys.exit(2)
    item_id = sys.argv[1]
    try:
        item_id = int(item_id)
    except Exception:
        print('Invalid item_id')
        sys.exit(3)
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('UPDATE dbo.item SET i_duration = NULL WHERE i_id = ?', (item_id,))
        conn.commit()
        print(f'Updated item {item_id}: set i_duration = NULL. rows affected: {cur.rowcount}')
    except Exception as e:
        print('Error:', e)
        sys.exit(4)
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
