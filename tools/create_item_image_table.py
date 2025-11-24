import sys, os
sys.path.insert(0, os.getcwd())
from db import get_connection

CREATE_SQL = '''
IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON t.schema_id = s.schema_id WHERE t.name = 'item_image' AND s.name = 'dbo')
BEGIN
  CREATE TABLE dbo.item_image (
    img_id INT IDENTITY(1,1) PRIMARY KEY,
    item_id INT NOT NULL,
    image_url NVARCHAR(1024) NOT NULL,
    thumb_url NVARCHAR(1024) NULL,
    sort_order INT DEFAULT 0
  )
END
'''

if __name__ == '__main__':
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(CREATE_SQL)
            conn.commit()
            print('item_image table ensured')
        except Exception as e:
            print('Failed creating item_image table:', e)
            try:
                conn.rollback()
            except Exception:
                pass
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass
