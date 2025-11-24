import sys, os
sys.path.insert(0, os.getcwd())
from db import set_item_image, get_connection

IMAGE_PATH = '/static/uploads/item23_20251123085613067025_IMG_9858.JPG'
ITEM_ID = 23

print('Attempting set_item_image for item', ITEM_ID, '->', IMAGE_PATH)
try:
    ok = set_item_image(ITEM_ID, IMAGE_PATH)
    print('set_item_image returned:', ok)
except Exception as e:
    print('set_item_image raised exception:', e)

# If set_item_image returned False, probe the item table columns and try a direct UPDATE using common columns.
if not 'ok' in locals() or not ok:
    print('\nProbing dbo.item columns and attempting direct UPDATE (best-effort):')
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='item'")
        cols = [r[0] for r in cur.fetchall()]
        print('Columns in dbo.item:', cols)
        # Determine candidate image columns and id columns
        image_cands = ['image_url', 'image', 'img', 'picture', 'photo', 'imagepath', 'i_image']
        id_cands = ['i_id', 'item_id', 'id'] + [c for c in cols if c.endswith('_id')]
        chosen_img = None
        chosen_id = None
        for ic in image_cands:
            if ic in (c.lower() for c in cols):
                chosen_img = next(c for c in cols if c.lower()==ic)
                break
        for idc in id_cands:
            for c in cols:
                if c.lower() == idc.lower():
                    chosen_id = c
                    break
            if chosen_id:
                break
        print('Chosen image column:', chosen_img)
        print('Chosen id column:', chosen_id)
        if chosen_img and chosen_id:
            sql = f"UPDATE dbo.item SET {chosen_img} = ? WHERE {chosen_id} = ?"
            print('Attempting SQL:', sql)
            try:
                cur.execute(sql, (IMAGE_PATH, ITEM_ID))
                conn.commit()
                print('Direct UPDATE rowcount:', getattr(cur, 'rowcount', None))
            except Exception as e:
                print('Direct UPDATE failed:', e)
        else:
            print('No suitable image or id column found to update.')
    except Exception as e:
        print('Probe/update failed:', e)
    finally:
        try:
            conn.close()
        except Exception:
            pass
