import os, sys, re
sys.path.insert(0, os.getcwd())
from db import get_connection

UPLOAD_DIR = os.path.join(os.getcwd(), 'static', 'uploads')
# pattern matches files like item23_... or item23.ext (case-insensitive)
ITEM_RE = re.compile(r'^item(\d+)(?:_.*)?(\.[A-Za-z0-9]+)$', re.IGNORECASE)

def canonicalize():
    if not os.path.isdir(UPLOAD_DIR):
        print('Upload directory not found:', UPLOAD_DIR)
        return
    files = os.listdir(UPLOAD_DIR)
    # group by item id
    by_item = {}
    for f in files:
        m = ITEM_RE.match(f)
        if not m:
            continue
        item_id = int(m.group(1))
        ext = m.group(2) or ''
        by_item.setdefault(item_id, []).append((f, ext))

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        for item_id, entries in by_item.items():
            # pick canonical ext from the first entry that has an extension
            canonical_ext = None
            canonical_src = None
            for fname, ext in entries:
                if ext:
                    canonical_src = fname
                    canonical_ext = ext
                    break
            if not canonical_src:
                print('No extension found for item', item_id, '- skipping')
                continue
            canonical_name = f'item{item_id}{canonical_ext}'
            src_path = os.path.join(UPLOAD_DIR, canonical_src)
            dest_path = os.path.join(UPLOAD_DIR, canonical_name)
            if os.path.abspath(src_path) != os.path.abspath(dest_path):
                # if dest exists, choose to keep dest (do not overwrite)
                if os.path.exists(dest_path):
                    print('Canonical file already exists for', item_id, '- keeping', dest_path)
                else:
                    print('Renaming', src_path, '->', dest_path)
                    os.rename(src_path, dest_path)
            else:
                print('Already canonical for', item_id, '->', canonical_name)

            web_path = f'/static/uploads/{canonical_name}'
            try:
                # update DB image_url if not already set or different
                cur.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=\'dbo\' AND TABLE_NAME=\'item\'')
                cols = [r[0].lower() for r in cur.fetchall()]
                if 'image_url' in cols:
                    # find id column
                    id_col = None
                    for c in ['i_id', 'item_id', 'id']:
                        if c in cols:
                            id_col = c
                            break
                    if not id_col:
                        for c in cols:
                            if c.endswith('_id'):
                                id_col = c
                                break
                    if not id_col:
                        print('No id column detected for DB update; skipping item', item_id)
                        continue
                    # check current value
                    select_sql = f"SELECT image_url FROM dbo.item WHERE {id_col} = ?"
                    try:
                        cur.execute(select_sql, (item_id,))
                        r = cur.fetchone()
                        cur_val = None
                        if r:
                            try:
                                cur_val = getattr(r, 'image_url')
                            except Exception:
                                try:
                                    cur_val = r[0]
                                except Exception:
                                    cur_val = None
                        if not cur_val or cur_val != web_path:
                            upd_sql = f"UPDATE dbo.item SET image_url = ? WHERE {id_col} = ?"
                            cur.execute(upd_sql, (web_path, item_id))
                            conn.commit()
                            print('Updated DB image_url for item', item_id, '->', web_path)
                        else:
                            print('DB image_url already set for item', item_id)
                    except Exception as e:
                        print('Failed to query/update item', item_id, '-', e)
                else:
                    print('image_url column missing despite previous run; skipping DB update for', item_id)
            except Exception as e:
                print('Error preparing DB update for item', item_id, '-', e)
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

if __name__ == '__main__':
    canonicalize()
