import sys
sys.path.insert(0, '.')
from db import get_connection

conn = None
try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='item'")
    cols = [r[0].lower() for r in cur.fetchall()]
    print('dbo.item columns:', cols)
    candidates = ['image_url','image','img','picture','photo','imagepath','i_image']
    found = [c for c in candidates if c in cols]
    if found:
        print('Found image-like columns in dbo.item:', found)
    else:
        print('No image-like columns found in dbo.item.')
except Exception as e:
    print('Error while checking columns:', e)
finally:
    try:
        if conn:
            conn.close()
    except Exception:
        pass
