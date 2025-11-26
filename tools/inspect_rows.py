import sys, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    import db
except Exception as e:
    print('Failed to import db:', e)
    sys.exit(1)

def row_to_dict(cur, row):
    cols = [c[0] for c in cur.description]
    return dict(zip(cols, row))

conn = db.get_connection()
cur = conn.cursor()

samples = [
    ("dbo.auction", "a_id", 58),
    ("dbo.item", "item_id", 77),
]

for table, pkcol, pk in samples:
    try:
        q = f"SELECT * FROM {table} WHERE {pkcol} = ?"
        print('\n---')
        print('Query:', q, 'params=', (pk,))
        cur.execute(q, (pk,))
        row = cur.fetchone()
        if not row:
            print('No row found for', table, pkcol, pk)
            continue
        d = row_to_dict(cur, row)
        print('Row for', table, pkcol, pk)
        for k, v in d.items():
            print(f"  {k}: {v!r}")
    except Exception as e:
        print('Error querying', table, e)

try:
    conn.close()
except Exception:
    pass
