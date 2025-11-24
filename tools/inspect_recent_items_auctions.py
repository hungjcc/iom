import sys
sys.path.insert(0, '.')
from db import get_connection

conn = None
try:
    conn = get_connection()
    cur = conn.cursor()
    print('Recent items:')
    try:
        cur.execute("SELECT TOP 10 * FROM dbo.item ORDER BY i_id DESC")
        rows = cur.fetchall()
        for r in rows:
            print(r)
    except Exception as e:
        print('Could not fetch items:', e)
    print('\nRecent auctions:')
    try:
        cur.execute("SELECT TOP 10 * FROM dbo.auction ORDER BY a_id DESC")
        rows = cur.fetchall()
        for r in rows:
            print(r)
    except Exception as e:
        print('Could not fetch auctions:', e)
except Exception as e:
    print('DB connection failed:', e)
finally:
    try:
        if conn:
            conn.close()
    except Exception:
        pass
