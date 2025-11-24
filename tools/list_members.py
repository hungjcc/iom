import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db import get_connection

if __name__ == '__main__':
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Discover which optional columns exist, then select only those to avoid SQL errors
        cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='member'")
        existing = [r[0].lower() for r in cur.fetchall()]
        cols = ['m_id', 'm_login_id', 'm_email', 'm_status']
        if 'm_is_admin' in existing:
            cols.append('m_is_admin')
        if 'is_admin' in existing:
            cols.append('is_admin')
        if 'm_role' in existing:
            cols.append('m_role')
        sql = "SELECT " + ", ".join(cols) + " FROM dbo.member ORDER BY m_id"
        cur.execute(sql)
        rows = cur.fetchall()
        if not rows:
            print('No members found (empty table)')
        for r in rows:
            try:
                mid = getattr(r, 'm_id')
            except Exception:
                mid = r[0]
            try:
                uname = getattr(r, 'm_login_id')
            except Exception:
                uname = r[1]
            try:
                email = getattr(r, 'm_email')
            except Exception:
                email = r[2]
            try:
                status = getattr(r, 'm_status')
            except Exception:
                status = r[3] if len(r) > 3 else None
            try:
                raw_m_is_admin = getattr(r, 'm_is_admin')
            except Exception:
                raw_m_is_admin = r[4] if len(r) > 4 else None
            try:
                raw_is_admin = getattr(r, 'is_admin')
            except Exception:
                raw_is_admin = r[5] if len(r) > 5 else None
            try:
                role = getattr(r, 'm_role') or ''
            except Exception:
                role = r[6] if len(r) > 6 else ''

            def _to_bool(val):
                if val is None:
                    return False
                if isinstance(val, bool):
                    return val
                if isinstance(val, (int, float)):
                    return int(val) != 0
                if isinstance(val, bytes):
                    try:
                        return int.from_bytes(val, 'little') != 0
                    except Exception:
                        return bool(val)
                s = str(val).strip().lower()
                return s in ('1', 'true', 't', 'yes', 'y')

            is_admin = _to_bool(raw_m_is_admin) or _to_bool(raw_is_admin) or (isinstance(role, str) and 'admin' in role.lower())
            print(f"{mid}\t{uname}\t{email}\tstatus={status}\tadmin={is_admin}\tm_is_admin={raw_m_is_admin}\tis_admin={raw_is_admin}\trole={role}")
        try:
            conn.close()
        except Exception:
            pass
    except Exception:
        traceback.print_exc()
