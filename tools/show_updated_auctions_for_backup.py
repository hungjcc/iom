"""
Show current auctions for items that had backups in the most recent `tools/backups/<ts>` run.
Prints: item_id, a_id, a_s_date, a_e_date, i_duration, expected_end (a_s_date + i_duration days).
"""
import os, sys, csv, datetime
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from db import get_connection


def find_latest_backup_root():
    base = os.path.join(os.path.dirname(__file__), 'backups')
    if not os.path.isdir(base):
        return None
    entries = [os.path.join(base, d) for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
    if not entries:
        return None
    entries.sort()
    return entries[-1]


def items_with_before_csv(backup_root):
    items = []
    for name in os.listdir(backup_root):
        p = os.path.join(backup_root, name)
        if not os.path.isdir(p):
            continue
        # look for dbo_auction_item_<id>_before.csv
        for fn in os.listdir(p):
            if fn.startswith('dbo_auction_item_') and fn.endswith('_before.csv'):
                full = os.path.join(p, fn)
                try:
                    with open(full, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                        if len(rows) > 1:
                            # extract item id from filename
                            try:
                                item_id = int(fn.split('_')[3])
                                items.append(item_id)
                            except Exception:
                                pass
                except Exception:
                    pass
    return sorted(set(items))


def main():
    backup_root = find_latest_backup_root()
    if not backup_root:
        print('No backups found under tools/backups/')
        return
    print('Using backup root:', backup_root)
    items = items_with_before_csv(backup_root)
    if not items:
        print('No item-level backup CSVs with rows found in', backup_root)
        return

    conn = get_connection()
    cur = conn.cursor()

    q = '''
    SELECT a.a_id, a.a_s_date, a.a_e_date, i.i_id, i.i_duration,
           DATEADD(day, i.i_duration, a.a_s_date) as expected_end
    FROM dbo.auction a
    JOIN dbo.item i ON i.i_id = a.a_item_id
    WHERE i.i_id = ?
    ORDER BY a.a_s_date
    '''

    for item_id in items:
        print('\n=== Item', item_id, '===')
        try:
            cur.execute(q, (item_id,))
            rows = cur.fetchall()
            if not rows:
                print(' No auctions currently for item', item_id)
                continue
            for r in rows:
                # handle both row object and tuple
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
                    e = r[2]
                try:
                    i_dur = getattr(r, 'i_duration')
                except Exception:
                    i_dur = r[4]
                try:
                    exp = getattr(r, 'expected_end')
                except Exception:
                    exp = r[5]
                print(' a_id', a_id, 'start', s, 'end', e, 'i_duration', i_dur, 'expected_end', exp)
        except Exception as ex:
            print(' Failed to query auctions for item', item_id, ':', ex)

    conn.close()

if __name__ == '__main__':
    main()
