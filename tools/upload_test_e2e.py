import io
import os
import sys
import time
import base64

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import importlib
# Ensure DB-backed mode for this E2E test (toggle before importing app module)
os.environ['USE_DB'] = os.environ.get('USE_DB', '1')
import app as app_module
importlib.reload(app_module)
app = app_module.app

# Create a small JPEG in memory
def make_test_image(path):
    # Use a tiny 1x1 PNG (base64) to avoid depending on Pillow in the test environment
    png_b64 = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII='
    data = base64.b64decode(png_b64)
    with open(path, 'wb') as f:
        f.write(data)


def find_new_uploads(since_ts):
    updir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    if not os.path.exists(updir):
        return []
    out = []
    for fn in os.listdir(updir):
        p = os.path.join(updir, fn)
        try:
            if os.path.getmtime(p) >= since_ts:
                out.append(fn)
        except Exception:
            continue
    return out


if __name__ == '__main__':
    now = time.time()
    # ensure upload dir exists
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    test_img_path = os.path.join(upload_dir, 'e2e_test_temp.png')
    make_test_image(test_img_path)

    # read bytes
    with open(test_img_path, 'rb') as f:
        img_bytes = f.read()

    with app.test_client() as client:
        # simulate logged-in user by patching module-level helper to avoid DB user lookup
        # This bypasses _user_dict_from_session's DB lookup for the test run.
        try:
            app_module._user_dict_from_session = lambda: {'id': 1, 'm_id': 1, 'username': 'e2e_test_user'}
        except Exception:
            pass
        # Also keep a basic session for compatibility
        with client.session_transaction() as sess:
            sess['u_name'] = 'e2e_test_user'
            sess['user_id'] = 1

        data = [
            ('title', 'E2E Test Item'),
            ('desc', 'This is a test upload from automated E2E script'),
            ('category', '2'),
            ('starting_price', '10.00'),
            ('duration', '1'),
            ('images', (io.BytesIO(img_bytes), 'e2e_test.png')),
        ]

        # BEFORE posting, attempt a direct call to DB helper to see errors
        try:
            import db
            print('Testing db.create_item_and_auction directly...')
            try:
                res = db.create_item_and_auction('E2E test direct', 'desc', seller_id=1, starting_price=1.0)
                print('create_item_and_auction returned:', res)
            except Exception as e:
                print('create_item_and_auction raised:', repr(e))
        except Exception as e:
            print('DB module import failed or DB unavailable:', repr(e))

        print('Posting to /auctions/new (multipart) using simple dict form')
        # First try: simple dict with a single file tuple
        try:
            data_dict = {
                'title': 'E2E Test Item',
                'desc': 'This is a test upload from automated E2E script',
                'category': '2',
                'starting_price': '10.00',
                'duration': '1',
                'images': (io.BytesIO(img_bytes), 'e2e_test.png')
            }
            resp = client.post('/auctions/new', data=data_dict, follow_redirects=True)
        except Exception as e:
            print('First POST attempt failed:', e)
            resp = None

        if resp is None or resp.status_code >= 400:
            # Try using MultiDict for more complex forms
            try:
                from werkzeug.datastructures import MultiDict
                md = MultiDict()
                md.add('title', 'E2E Test Item')
                md.add('desc', 'This is a test upload from automated E2E script')
                md.add('category', '2')
                md.add('starting_price', '10.00')
                md.add('duration', '1')
                md.add('images', (io.BytesIO(img_bytes), 'e2e_test.png'))
                print('Posting using MultiDict fallback')
                resp = client.post('/auctions/new', data=md, follow_redirects=True)
            except Exception as ee:
                print('MultiDict POST attempt failed:', ee)
                resp = resp or None
        print('Response status:', resp.status_code)
        print('Response content-type:', resp.content_type)
        body_text = resp.data.decode('utf-8', errors='replace')
        snippet = body_text[:2400]
        print('Response page snippet (first 2400 chars):\n', snippet)
        # Look for known messages
        for token in ('Item and auction created successfully', 'Failed to create auction', 'Please upload at least one image', 'Failed to create item/auction'):
            if token in body_text:
                print('Found message in response:', token)

        # scan uploads for files created since script start
        new_files = find_new_uploads(now - 5)
        print('New files in static/uploads (modified in last ~5s):', new_files)

        # try to import db helpers and inspect item images
        try:
            import db
            # attempt to find recent item_image rows by looking for our filename in image_url
            found = False
            images = []
            try:
                # naive scan of item_image table using get_item_images for likely item ids near 1..200
                for candidate in range(1, 200):
                    try:
                        rows = db.get_item_images(candidate)
                        if not rows:
                            continue
                        for r in rows:
                            if r.get('image_url') and 'e2e_test' in r.get('image_url'):
                                print('DB image row for item', candidate, r)
                                found = True
                                images.append((candidate, r))
                    except Exception:
                        continue
            except Exception as e:
                print('Error scanning DB item_image:', e)
            if not found:
                print('No DB item_image rows referencing e2e_test found (this may be due to DB constraints or create_item_and_auction failure).')
        except Exception as e:
            print('DB module not available or DB access failed:', e)

    # cleanup temp
    try:
        os.remove(test_img_path)
    except Exception:
        pass

    print('E2E upload test complete')
