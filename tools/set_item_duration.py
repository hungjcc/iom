"""
Set an item's duration column (i_duration) to a specific integer value.
Usage: python tools\set_item_duration.py <item_id> <duration>
"""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from db import get_connection

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python tools\\set_item_duration.py <item_id> <duration>')
        sys.exit(2)
    item_id = sys.argv[1]
    duration = sys.argv[2]
    try:
        item_id = int(item_id)
        duration = int(duration)
    except Exception:
        print('Invalid args')
        sys.exit(3)
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('UPDATE dbo.item SET i_duration = ? WHERE i_id = ?', (duration, item_id))
        conn.commit()
        print(f'Updated item {item_id}: set i_duration = {duration}. rows affected: {cur.rowcount}')
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
