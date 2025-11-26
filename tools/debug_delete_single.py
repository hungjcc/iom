import sys, traceback
sys.path.insert(0,'.')
try:
    import db
    conn = db.get_connection()
    cur = conn.cursor()
    aid = 57
    print('COUNT before delete:')
    try:
        cur.execute('SELECT COUNT(*) AS cnt FROM dbo.auction WHERE a_id = ?', (aid,))
        r = cur.fetchone()
        print(' ->', getattr(r, 'cnt', r[0] if r else None))
    except Exception as e:
        print('SELECT COUNT error:', e)

    print('\nAttempting DELETE FROM dbo.auction WHERE a_id = ?')
    try:
        cur.execute('DELETE FROM dbo.auction WHERE a_id = ?', (aid,))
        print('cursor.rowcount after DELETE:', cur.rowcount)
    except Exception as e:
        print('DELETE error:', e)
        traceback.print_exc()

    try:
        print('\nCOUNT after DELETE (before commit):')
        cur.execute('SELECT COUNT(*) AS cnt FROM dbo.auction WHERE a_id = ?', (aid,))
        r = cur.fetchone()
        print(' ->', getattr(r, 'cnt', r[0] if r else None))
    except Exception as e:
        print('SELECT COUNT after delete error:', e)

    try:
        conn.commit()
        print('\nCommitted')
    except Exception as e:
        print('Commit error:', e)

    try:
        print('\nCOUNT after commit:')
        cur.execute('SELECT COUNT(*) AS cnt FROM dbo.auction WHERE a_id = ?', (aid,))
        r = cur.fetchone()
        print(' ->', getattr(r, 'cnt', r[0] if r else None))
    except Exception as e:
        print('SELECT COUNT after commit error:', e)

    cur.close()
    conn.close()
except Exception:
    traceback.print_exc()
    print('Could not run debug delete; check db connection.')
