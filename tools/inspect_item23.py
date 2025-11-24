import sys, os
sys.path.insert(0, os.getcwd())
from db import get_connection

conn = get_connection()
cur = conn.cursor()
try:
    cur.execute("SELECT i_id, image_url FROM dbo.item WHERE i_id = ?", (23,))
    row = cur.fetchone()
    print('row:', row)
    if row:
        try:
            print('i_id:', getattr(row,'i_id'))
        except Exception:
            print('i_id[0]=', row[0])
        try:
            print('image_url:', getattr(row,'image_url'))
        except Exception:
            try:
                print('image_url[1]=', row[1])
            except Exception:
                print('could not read image_url')
finally:
    try:
        conn.close()
    except Exception:
        pass
