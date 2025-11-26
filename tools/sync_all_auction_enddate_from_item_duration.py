"""
Sync auction `a_e_date` from each item's `i_duration` for all items with `i_duration` set.
Backs up auctions before updating. Usage:
  python tools\sync_all_auction_enddate_from_item_duration.py
"""
import os, sys, csv, datetime, argparse
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from db import get_connection

# CLI
p = argparse.ArgumentParser()
p.add_argument('--dry-run', action='store_true', help='Show what would be updated without writing backups or committing')
args = p.parse_args()
DRY_RUN = args.dry_run


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
    conn = get_connection()
    cur = conn.cursor()

    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    backup_root = os.path.join(os.path.dirname(__file__), 'backups', ts)
    if not DRY_RUN:
        os.makedirs(backup_root, exist_ok=True)

    # Find items with i_duration set
    try:
        cur.execute("SELECT i_id, i_duration FROM dbo.item WHERE i_duration IS NOT NULL")
        items = cur.fetchall()
    except Exception as e:
        print('Failed to query items with i_duration:', e)
        conn.close()
        sys.exit(2)

    if not items:
        print('No items found with i_duration set. Nothing to do.')
        conn.close()
        return

    total_items = 0
    total_auctions_backed_up = 0
    total_auctions_updated = 0
    total_auctions_would_update = 0

    for row in items:
        try:
            i_id = getattr(row, 'i_id') if hasattr(row, 'i_id') else row[0]
            i_duration = getattr(row, 'i_duration') if hasattr(row, 'i_duration') else row[1]
        except Exception:
            print('Skipping a malformed row:', row)
            continue

        total_items += 1
        # if dry-run: report how many auctions would be updated and skip backups/updates
        check_sql = '''
        SELECT COUNT(*) as cnt
        FROM dbo.auction a
        JOIN dbo.item i ON i.i_id = a.a_item_id
        WHERE i.i_id = ?
          AND (a.a_e_date IS NULL OR a.a_e_date <> DATEADD(day, i.i_duration, a.a_s_date))
        '''
        try:
            cur.execute(check_sql, (i_id,))
            c = cur.fetchone()
            cnt = getattr(c, 'cnt') if hasattr(c, 'cnt') else (c[0] if c else 0)
        except Exception as e:
            print(f'[{i_id}] Failed to check pending updates:', e)
            cnt = 0

        if DRY_RUN:
            if cnt:
                print(f'[{i_id}] DRY-RUN: {cnt} auction(s) would be updated for item {i_id} (i_duration={i_duration})')
                total_auctions_would_update = total_auctions_would_update + cnt if 'total_auctions_would_update' in locals() else cnt
            else:
                print(f'[{i_id}] DRY-RUN: no auctions need updating for item {i_id}')
            continue

        # per-item backup dir
        backup_dir = os.path.join(backup_root, f'item_{i_id}')
        os.makedirs(backup_dir, exist_ok=True)

        before_csv = os.path.join(backup_dir, f'dbo_auction_item_{i_id}_before.csv')
        q = "SELECT * FROM dbo.auction WHERE a_item_id = ?"
        try:
            n_before = dump_to_csv(cur, q, (i_id,), before_csv)
            total_auctions_backed_up += n_before
            print(f'[{i_id}] Backed up {n_before} auction rows to {before_csv}')
        except Exception as e:
            print(f'[{i_id}] Backup failed:', e)
            # continue to next item without making updates
            continue

        # Perform update for this item
        try:
            update_sql = '''
            UPDATE a
            SET a.a_e_date = DATEADD(day, i.i_duration, a.a_s_date)
            FROM dbo.auction a
            JOIN dbo.item i ON i.i_id = a.a_item_id
            WHERE i.i_id = ?
              AND (a.a_e_date IS NULL OR a.a_e_date <> DATEADD(day, i.i_duration, a.a_s_date))
            '''
            cur.execute(update_sql, (i_id,))
            affected = cur.rowcount
            conn.commit()
            total_auctions_updated += affected
            print(f'[{i_id}] Updated {affected} auction row(s).')
        except Exception as e:
            print(f'[{i_id}] Update failed, rolling back:', e)
            try:
                conn.rollback()
            except Exception:
                pass
            # continue to next item
            continue

    print('\nSummary:')
    print(' Items processed:', total_items)
    print(' Auctions backed up:', total_auctions_backed_up)
    print(' Auctions updated:', total_auctions_updated)
    print(' Backups written to:', backup_root)

    conn.close()

if __name__ == '__main__':
    main()
