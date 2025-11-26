import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import db
conn = db.get_connection()
cur = conn.cursor()
try:
    cur.execute('SELECT * FROM dbo.item WHERE i_id = ?', (77,))
    row = cur.fetchone()
    if not row:
        print('No item with i_id=77')
    else:
        cols = [c[0] for c in cur.description]
        d = dict(zip(cols, row))
        for k,v in d.items():
            print(k, ':', repr(v))
finally:
    try:
        conn.close()
    except Exception:
        pass
