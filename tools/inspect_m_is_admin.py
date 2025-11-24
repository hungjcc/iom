from db import get_connection

c = get_connection()
cur = c.cursor()
cur.execute("SELECT m_id,m_login_id,m_is_admin FROM dbo.member ORDER BY m_id")
rows = cur.fetchall()
out = []
for r in rows:
    try:
        m_id = getattr(r, 'm_id')
    except Exception:
        m_id = r[0]
    try:
        login = getattr(r, 'm_login_id')
    except Exception:
        login = r[1]
    try:
        is_admin = getattr(r, 'm_is_admin')
    except Exception:
        is_admin = r[2]
    out.append((m_id, login, is_admin))
print(out)

c.close()
