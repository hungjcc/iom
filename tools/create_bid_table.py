import sys
import traceback
import os

# Ensure project parent dir is on path
parent = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent not in sys.path:
    sys.path.insert(0, parent)

print('Create dbo.bid table script starting...')
try:
    import db
except Exception as e:
    print('Failed to import db module:', e)
    traceback.print_exc()
    sys.exit(2)

try:
    conn = db.get_connection()
    cur = conn.cursor()
except Exception as e:
    print('Failed to connect to DB:', e)
    traceback.print_exc()
    sys.exit(3)

# Check if table exists
try:
    cur.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='bid'")
    r = cur.fetchone()
    exists = (r[0] if r else 0) > 0
except Exception:
    exists = False

if exists:
    print('Table dbo.bid already exists; no action taken.')
    try:
        conn.close()
    except Exception:
        pass
    sys.exit(0)

# Create table
create_sql = '''
CREATE TABLE dbo.bid (
  b_id INT IDENTITY(1,1) PRIMARY KEY,
  b_a_id INT NOT NULL,
  b_m_id INT NULL,
  b_amount DECIMAL(18,2) NOT NULL,
  b_time DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
)
'''

print('Creating dbo.bid...')
try:
    cur.execute(create_sql)
    conn.commit()
    print('dbo.bid created successfully.')
except Exception as e:
    print('Failed to create dbo.bid:', e)
    traceback.print_exc()
    try:
        conn.rollback()
    except Exception:
        pass
    try:
        conn.close()
    except Exception:
        pass
    sys.exit(4)

# Create index on b_a_id
try:
    print('Creating index IX_bid_b_a_id...')
    cur.execute('CREATE INDEX IX_bid_b_a_id ON dbo.bid (b_a_id)')
    conn.commit()
    print('Index created.')
except Exception as e:
    print('Failed to create index (non-fatal):', e)
    try:
        conn.rollback()
    except Exception:
        pass

# Try to add FK to auction.a_id if that column exists
try:
    cur.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='auction' AND COLUMN_NAME IN ('a_id','id')")
    r = cur.fetchone()
    if r and r[0] > 0:
        try:
            print('Attempting to add foreign key FK_bid_auction...')
            cur.execute('ALTER TABLE dbo.bid ADD CONSTRAINT FK_bid_auction FOREIGN KEY (b_a_id) REFERENCES dbo.auction(a_id)')
            conn.commit()
            print('Foreign key FK_bid_auction added.')
        except Exception as e:
            print('Could not add foreign key (non-fatal):', e)
            try:
                conn.rollback()
            except Exception:
                pass
    else:
        print('auction.a_id column not found; skipping FK creation.')
except Exception as e:
    print('Error checking auction columns for FK:', e)

try:
    conn.close()
except Exception:
    pass

print('Script finished.')
