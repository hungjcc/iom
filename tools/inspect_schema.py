import json
import sys
import os
import traceback

# Ensure project package path includes the repo root where `db.py` lives
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

try:
    import db
except Exception:
    traceback.print_exc()
    raise SystemExit(1)

def fetch_columns(table_name):
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME=? ORDER BY ORDINAL_POSITION", (table_name,))
        rows = cur.fetchall()
        out = []
        for r in rows:
            try:
                cname = r[0]
            except Exception:
                cname = None
            try:
                dtype = r[1]
            except Exception:
                dtype = None
            try:
                isnull = r[2]
            except Exception:
                isnull = None
            try:
                cdef = r[3]
            except Exception:
                cdef = None
            out.append({'column': cname, 'data_type': dtype, 'is_nullable': isnull, 'default': cdef})
        return out
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

def main():
    for t in ('item', 'auction'):
        try:
            cols = fetch_columns(t)
            print('TABLE:', t)
            print(json.dumps(cols, indent=2, ensure_ascii=False))
            # also write to auth.log for debugging
            try:
                with open('../auth.log', 'a', encoding='utf-8') as lf:
                    lf.write('\nINSPECT_SCHEMA %s:\n' % (t,))
                    lf.write(json.dumps(cols, indent=2, ensure_ascii=False) + '\n')
            except Exception:
                pass
        except Exception:
            traceback.print_exc()

if __name__ == '__main__':
    main()
