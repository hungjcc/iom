import sys, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    import db
except Exception as e:
    print('Failed to import db:', e)
    sys.exit(1)

conn = db.get_connection()
cur = conn.cursor()

try:
    cur.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='item'")
    rows = cur.fetchall()
    if not rows:
        print('No columns found for dbo.item (table may not exist)')
    else:
        print('Columns for dbo.item:')
        for r in rows:
            print(' ', r[0], '(', r[1], ')')
except Exception as e:
    print('Query failed:', e)
finally:
    try:
        conn.close()
    except Exception:
        pass
