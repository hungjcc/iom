from db import get_connection

c = get_connection()
cur = c.cursor()
cur.execute("SELECT m_id, m_login_id, m_pass FROM dbo.member WHERE m_login_id = ?", ('alice',))
row = cur.fetchone()
if not row:
    print('NOT FOUND')
else:
    try:
        mid = getattr(row,'m_id')
        login = getattr(row,'m_login_id')
        mp = getattr(row,'m_pass')
    except Exception:
        mid, login, mp = row[0], row[1], row[2]
    print('FOUND', mid, login)
    if mp is None:
        print('m_pass: NULL')
    else:
        s = str(mp)
        # print the full stored value but warn
        print('m_pass (full):', s)
        print('length:', len(s))
c.close()
