import sys
import traceback

print('Starting DB checks...')
# Ensure parent folder (project package) is on sys.path so we can import db.py
import os
parent = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent not in sys.path:
    sys.path.insert(0, parent)
try:
    import db
except Exception as e:
    print('Failed to import db module:', e)
    traceback.print_exc()
    sys.exit(2)

try:
    conn = db.get_connection()
except Exception as e:
    print('get_connection() failed:', e)
    traceback.print_exc()
    sys.exit(3)

cur = conn.cursor()

def safe_execute(q, params=()):
    print('\n---')
    print('SQL:', q)
    try:
        cur.execute(q, params)
        rows = cur.fetchmany(10)
        print('Sample rows (up to 10):')
        for r in rows:
            print(r)
        try:
            # try to get count if available
            cur.execute('SELECT COUNT(*) FROM (' + q.replace('TOP 10', '') + ') as sub')
        except Exception:
            pass
    except Exception as e:
        print('Query failed:', e)

# 1) Count bids
try:
    cur.execute('SELECT COUNT(*) FROM dbo.bid')
    r = cur.fetchone()
    print('\nTotal bids in dbo.bid:', (r[0] if r else r))
except Exception as e:
    print('\nCould not count dbo.bid:', e)

# 2) Sample recent bids
try:
    safe_execute('SELECT TOP 10 b_a_id, b_amount, b_time FROM dbo.bid ORDER BY b_time DESC')
except Exception:
    print('Sample bid query failed')

# 3) Sample recent auctions
try:
    safe_execute('SELECT TOP 10 a_id, a_item_id, a_s_price, a_s_date FROM dbo.auction ORDER BY a_s_date DESC')
except Exception:
    print('Sample auction query failed')

# 4) Per-auction bid counts and max
try:
    safe_execute('SELECT TOP 20 a.a_id, COUNT(b.b_amount) AS bid_count, MAX(b.b_amount) AS max_bid FROM dbo.auction a LEFT JOIN dbo.bid b ON b.b_a_id = a.a_id GROUP BY a.a_id ORDER BY a.a_id DESC')
except Exception:
    print('Per-auction aggregation failed')

# 5) Look for any tables with "bid" in the name (helpful if schema uses different table name)
try:
    safe_execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_NAME LIKE '%bid%'")
except Exception:
    print('Could not list bid-like tables')

# 6) List all base tables to help locate possible bid table names
try:
    safe_execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' ORDER BY TABLE_NAME")
except Exception:
    print('Could not list all tables')

# 7) Check dbo.payment for potential bid-like records (some schemas reuse a payment table)
try:
    safe_execute('SELECT TOP 10 * FROM dbo.payment')
except Exception:
    print('Could not sample dbo.payment')

# 8) Show columns for dbo.payment
try:
    safe_execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='payment'")
except Exception:
    print('Could not list columns for dbo.payment')

try:
    conn.close()
except Exception:
    pass

print('\nDB checks complete.')
