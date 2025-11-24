import os
import base64
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# tiny 1x1 PNG
png_b64 = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII='

uploads = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
os.makedirs(uploads, exist_ok=True)

items = [25, 27]

for item in items:
    fname = f'item{item}.png'
    path = os.path.join(uploads, fname)
    with open(path, 'wb') as f:
        f.write(base64.b64decode(png_b64))
    print('Wrote', path)

# Now attempt to register them in DB
try:
    import db
except Exception as e:
    print('Failed to import db:', e)
    raise SystemExit(1)

for item in items:
    web = f'/static/uploads/item{item}.png'
    try:
        img_id = db.add_item_image(item, web, None, sort_order=1)
        print('add_item_image returned:', img_id)
    except Exception as e:
        print('add_item_image failed for', item, e)
    try:
        ok = db.set_item_image(item, web)
        print('set_item_image returned for', item, ok)
    except Exception as e:
        print('set_item_image failed for', item, e)

# Print resulting rows
try:
    import pprint
    pprint.pprint(db.get_item_images(25))
    pprint.pprint(db.get_item_images(27))
    pprint.pprint(db.get_auction(19))
    pprint.pprint(db.get_auction(20))
except Exception as e:
    print('Error fetching rows after update:', e)
