import sys, os
sys.path.insert(0, os.getcwd())
from db import get_connection

IMAGE_PATH = '/static/uploads/item23_20251123085613067025_IMG_9858.JPG'
ITEM_ID = 23

def main():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Ensure image_url column exists
        try:
            cur.execute("SELECT 1 FROM sys.columns WHERE Name = N'image_url' AND Object_ID = Object_ID(N'dbo.item')")
            exists = cur.fetchone() is not None
        except Exception:
            exists = False

        if not exists:
            print('image_url column not found; attempting to add it...')
            try:
                cur.execute("ALTER TABLE dbo.item ADD image_url NVARCHAR(1024) NULL")
                conn.commit()
                print('ALTER TABLE succeeded: image_url column added.')
            except Exception as e:
                conn.rollback()
                print('ALTER TABLE failed:', e)
                print('Cannot proceed to update image path without image_url column.')
                return
        else:
            print('image_url column already exists.')

        # Determine id column to use in WHERE clause
        cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='item'")
        cols = [r[0] for r in cur.fetchall()]
        id_col = None
        for c in ['i_id', 'item_id', 'id']:
            for col in cols:
                if col.lower() == c.lower():
                    id_col = col
                    break
            if id_col:
                break
        if not id_col:
            # fallback to any column that ends with _id
            for col in cols:
                if col.lower().endswith('_id'):
                    id_col = col
                    break
        if not id_col:
            print('Could not determine an id column in dbo.item; aborting.')
            return
        print('Using id column:', id_col)

        # Perform the update
        sql = f"UPDATE dbo.item SET image_url = ? WHERE {id_col} = ?"
        try:
            cur.execute(sql, (IMAGE_PATH, ITEM_ID))
            conn.commit()
            print('UPDATE executed, rowcount =', getattr(cur, 'rowcount', None))
        except Exception as e:
            conn.rollback()
            print('UPDATE failed:', e)

    except Exception as e:
        print('Connection or unexpected error:', e)
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

if __name__ == '__main__':
    main()
