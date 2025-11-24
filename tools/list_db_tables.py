"""
List tables in the current database schema (dbo). Run with DB env vars set.
"""
import sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
try:
    from db import get_connection
except Exception:
    print('Failed to import get_connection from db.py')
    traceback.print_exc()
    sys.exit(1)

try:
    conn = get_connection()
except Exception:
    print('get_connection() failed:')
    traceback.print_exc()
    sys.exit(1)

try:
    cur = conn.cursor()
    cur.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_SCHEMA='dbo' ORDER BY TABLE_NAME")
    rows = cur.fetchall()
    print('Tables in dbo:')
    for r in rows:
        print('-', r.TABLE_NAME if hasattr(r, 'TABLE_NAME') else r[1])
finally:
    try:
        conn.close()
    except Exception:
        pass
