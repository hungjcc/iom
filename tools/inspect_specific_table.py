"""
Inspect a specific table (columns + sample row). Usage:
  python tools/inspect_specific_table.py StockPriceHistory
"""
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
if len(sys.argv) < 2:
    print('Usage: python tools/inspect_specific_table.py <TableName>')
    sys.exit(1)
TABLE = sys.argv[1]
try:
    from db import get_connection
except Exception:
    print('Failed to import get_connection')
    traceback.print_exc()
    sys.exit(1)

try:
    conn = get_connection()
except Exception:
    print('get_connection failed')
    traceback.print_exc()
    sys.exit(1)

try:
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT TOP 0 * FROM dbo.{TABLE}")
        cols = [c[0] for c in cur.description] if cur.description else []
        print('Columns:')
        for c in cols:
            print('-', c)
    except Exception as e:
        print('Error getting columns:', e)
    try:
        cur.execute(f"SELECT TOP 5 * FROM dbo.{TABLE}")
        rows = cur.fetchall()
        print('\nSample rows:')
        for r in rows:
            print(dict(zip(cols, r)))
    except Exception as e:
        print('Error fetching sample rows:', e)
finally:
    try:
        conn.close()
    except Exception:
        pass
