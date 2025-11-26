import sys
import os
from datetime import timedelta, datetime

# Ensure project root on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    import db
except Exception as e:
    print('Error importing db module:', e)
    sys.exit(1)

conn = db.get_connection()
cur = conn.cursor()

print('Discovering auction schema...')
cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='auction'")
auction_cols = [r[0].lower() for r in cur.fetchall()]
print('Auction columns:', auction_cols)

# pick or create end-date column
end_candidates = ['a_e_date', 'end_date', 'a_end', 'a_e']
end_col = None
for c in end_candidates:
    if c in auction_cols:
        end_col = c
        break

if not end_col:
    # Add a_e_date column
    print('No auction end-date column found. Adding `a_e_date` column...')
    try:
        cur.execute('ALTER TABLE dbo.auction ADD a_e_date DATETIME2 NULL')
        conn.commit()
        end_col = 'a_e_date'
        print('Added column a_e_date')
    except Exception as e:
        print('Failed to add a_e_date column:', e)
        conn.rollback()
        conn.close()
        sys.exit(2)
else:
    print('Using existing auction end-date column:', end_col)

# discover duration columns on auction and item
cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='auction'")
auction_cols = [r[0].lower() for r in cur.fetchall()]
cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='item'")
item_cols = [r[0].lower() for r in cur.fetchall()]

duration_candidates = ['a_duration', 'duration', 'i_duration', 'i_dur', 'length', 'days']
auction_duration_col = None
item_duration_col = None
for cand in duration_candidates:
    if cand in auction_cols and auction_duration_col is None:
        auction_duration_col = cand
    if cand in item_cols and item_duration_col is None:
        item_duration_col = cand

# detect item primary key column name (common candidates)
item_id_candidates = ['i_id', 'item_id', 'id', 'i_item_id', 'i_id']
item_id_col = None
for c in item_id_candidates:
    if c in item_cols:
        item_id_col = c
        break
if not item_id_col:
    # fallback: pick any column that ends with '_id'
    for c in item_cols:
        if c.endswith('_id'):
            item_id_col = c
            break
if not item_id_col:
    print('Could not determine item primary key column. Aborting.')
    conn.close()
    sys.exit(4)
print('Using item PK column:', item_id_col)

print('Found auction duration column:', auction_duration_col)
print('Found item duration column:', item_duration_col)

# query auctions missing end date
sql = f"SELECT a_id, a_item_id, a_s_date{', ' + auction_duration_col if auction_duration_col else ''} FROM dbo.auction WHERE {end_col} IS NULL"
print('Selecting auctions to backfill with:', sql)
try:
    cur.execute(sql)
    rows = cur.fetchall()
except Exception as e:
    print('Failed to fetch auctions:', e)
    conn.close()
    sys.exit(3)

if not rows:
    print('No auctions require backfill. Exiting.')
    conn.close()
    sys.exit(0)

print(f'Found {len(rows)} auctions with NULL {end_col}')
updated = 0
skipped = 0

for row in rows:
    try:
        # row may be tuple; map columns by index
        # We selected a_id, a_item_id, a_s_date, [auction_duration]
        a_id = None
        a_item_id = None
        a_s_date = None
        a_dur = None
        if len(row) >= 1:
            a_id = row[0]
        if len(row) >= 2:
            a_item_id = row[1]
        if len(row) >= 3:
            a_s_date = row[2]
        if auction_duration_col and len(row) >= 4:
            a_dur = row[3]

        duration_val = None
        if a_dur is not None:
            try:
                duration_val = int(a_dur)
            except Exception:
                duration_val = None

        # if no auction duration, try item duration
        if duration_val is None and item_duration_col and a_item_id is not None:
            try:
                cur2 = conn.cursor()
                cur2.execute(f"SELECT {item_duration_col} FROM dbo.item WHERE {item_id_col} = ?", (a_item_id,))
                r = cur2.fetchone()
                if r:
                    try:
                        duration_val = int(getattr(r, item_duration_col) if hasattr(r, item_duration_col) else r[0])
                    except Exception:
                        try:
                            duration_val = int(r[0])
                        except Exception:
                            duration_val = None
                cur2.close()
            except Exception:
                duration_val = None

        if duration_val is None:
            print(f'Auction {a_id}: no duration found (skip)')
            skipped += 1
            continue
        if a_s_date is None:
            print(f'Auction {a_id}: missing start date a_s_date (skip)')
            skipped += 1
            continue

        # compute end date
        try:
            if not isinstance(a_s_date, datetime):
                # attempt parse if string
                a_s_date = datetime.fromisoformat(str(a_s_date))
        except Exception:
            pass
        if not isinstance(a_s_date, datetime):
            print(f'Auction {a_id}: could not parse start date (skip)')
            skipped += 1
            continue

        end_dt = a_s_date + timedelta(days=int(duration_val))

        # perform update
        try:
            cur.execute(f"UPDATE dbo.auction SET {end_col} = ? WHERE a_id = ?", (end_dt, a_id))
            conn.commit()
            print(f'Updated auction {a_id}: set {end_col} = {end_dt.isoformat()} (duration {duration_val})')
            updated += 1
        except Exception as e:
            print(f'Failed to update auction {a_id}:', e)
            conn.rollback()
            skipped += 1
    except Exception as e:
        print('Unexpected error processing row:', e)
        skipped += 1

print(f'Backfill complete. Updated: {updated}, Skipped: {skipped}, Total considered: {len(rows)}')

conn.close()
