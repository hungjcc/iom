"""
Sync auction `a_e_date` from the item's `i_duration` for a specific item.
Usage:
  python tools\sync_auction_enddate_from_item_duration.py --item-id 77

This will:
- Backup matching auctions to `tools/backups/<timestamp>/sync_auctions_before.csv`.
- Update `a_e_date = DATEADD(day, i_duration, a_s_date)` for auctions referencing the item.
- Print counts and exit.
"""
import os, sys, csv, datetime
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from db import get_connection
import argparse

def dump_to_csv(cur, query, params, path):
    cur.execute(query, params)
    rows = cur.fetchall()
    if not rows:
        return 0
    cols = [d[0] for d in cur.description]
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([getattr(r, c) if hasattr(r, c) else r[idx] for idx, c in enumerate(cols)])
    return len(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--item-id', type=int, required=True)
    args = p.parse_args()
    item_id = args.item_id

    conn = get_connection()
    cur = conn.cursor()

    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    backup_dir = os.path.join(os.path.dirname(__file__), 'backups', ts)
    os.makedirs(backup_dir, exist_ok=True)

    # Backup auctions for this item
    before_csv = os.path.join(backup_dir, f'dbo_auction_item_{item_id}_before.csv')
    q = "SELECT * FROM dbo.auction WHERE a_item_id = ?"
    try:
        n_before = dump_to_csv(cur, q, (item_id,), before_csv)
        print(f'Backed up {n_before} auction rows to {before_csv}')
    except Exception as e:
        print('Backup failed:', e)
        conn.close()
        sys.exit(2)

    # Perform update: set a_e_date = DATEADD(day, i.i_duration, a.a_s_date)
    try:
        update_sql = '''
        UPDATE a
        SET a.a_e_date = DATEADD(day, i.i_duration, a.a_s_date)
        FROM dbo.auction a
        JOIN dbo.item i ON i.i_id = a.a_item_id
        WHERE i.i_id = ?
          AND (a.a_e_date IS NULL OR a.a_e_date <> DATEADD(day, i.i_duration, a.a_s_date))
        '''
        cur.execute(update_sql, (item_id,))
        affected = cur.rowcount
        conn.commit()
        print(f'Updated {affected} auction row(s) for item {item_id}.')
    except Exception as e:
        print('Update failed, rolling back:', e)
        try:
            conn.rollback()
        except Exception:
            pass
        conn.close()
        sys.exit(3)

    # Show current auction status for this item
    try:
        cur.execute('SELECT a_id, a_s_date, a_e_date FROM dbo.auction WHERE a_item_id = ? ORDER BY a_s_date', (item_id,))
        rows = cur.fetchall()
        print('After update, auctions:')
        for r in rows:
            try:
                a_id = getattr(r, 'a_id')
            except Exception:
                a_id = r[0]
            try:
                s = getattr(r, 'a_s_date')
            except Exception:
                s = r[1]
            try:
                e = getattr(r, 'a_e_date')
            except Exception:
                e = r[2] if len(r) > 2 else None
            print(' a_id', a_id, 'start', s, 'end', e)
    except Exception as e:
        print('Failed to fetch auctions after update:', e)

    conn.close()

if __name__ == '__main__':
    main()
