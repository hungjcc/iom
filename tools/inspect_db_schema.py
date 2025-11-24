"""
Inspect dbo.auction and dbo.bid tables: print columns and one sample row.
Run from project root with DB env vars set, e.g.:
  $env:DB_DRIVER='{ODBC Driver 18 for SQL Server}'; python tools/inspect_db_schema.py
"""
import sys, os, traceback
# ensure project root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from db import get_connection
except Exception:
    print('Failed to import get_connection from db.py')
    traceback.print_exc()
    sys.exit(1)

TABLES = ['dbo.auction', 'dbo.bid']

def inspect_table(conn, table):
    cur = conn.cursor()
    info = {}
    try:
        # fetch zero rows but get description
        q = f"SELECT TOP 0 * FROM {table}"
        cur.execute(q)
        cols = [c[0] for c in cur.description] if cur.description else []
        info['columns'] = cols
        # fetch one sample row if available
        try:
            cur.execute(f"SELECT TOP 1 * FROM {table}")
            row = cur.fetchone()
            if row:
                info['sample'] = dict(zip(cols, row))
            else:
                info['sample'] = None
        except Exception as e:
            info['sample'] = f'Error fetching sample row: {e}'
    except Exception as e:
        info['error'] = str(e)
    return info


def main():
    try:
        conn = get_connection()
    except Exception as e:
        print('get_connection() failed:')
        traceback.print_exc()
        sys.exit(1)

    try:
        for t in TABLES:
            print('='*60)
            print(f'Inspecting {t}')
            info = inspect_table(conn, t)
            if 'error' in info:
                print('  Error:', info['error'])
                continue
            print('  Columns:')
            for c in info.get('columns', []):
                print('   -', c)
            print('  Sample row:')
            print('   ', info.get('sample'))
    finally:
        try:
            conn.close()
        except Exception:
            pass

if __name__ == '__main__':
    main()
