import os
import sys

# Ensure project root is on sys.path so we can import app when this file
# is executed from the tools/ directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app, ts

paths = [
    '/',
    '/search?key_word=test',
    '/user_login',
    '/register',
    '/logout',
    '/user_menu',
    '/browse',
    '/sell',
    '/help',
    '/static/app.js',
    '/static/styles.css',
]


if __name__ == '__main__':
    with app.test_client() as client:
        for path in paths:
            # follow redirects so we can observe final status
            r = client.get(path, follow_redirects=True)
            ct = r.content_type or ''
            print(f"{path} => {r.status_code} | {ct} | {len(r.data)} bytes")

        # --- Admin flow tests ---
        print('\n-- Admin flow tests --')
        # Log in as demo admin to get session cookie
        r = client.post('/user_login', data={'username': 'admin', 'password': 'adminpass'}, follow_redirects=True)
        print(f"POST /user_login (admin) => {r.status_code} | {r.content_type or ''} | {len(r.data)} bytes")

        # Access admin panel
        r = client.get('/admin', follow_redirects=True)
        print(f"GET /admin => {r.status_code} | {r.content_type or ''} | {len(r.data)} bytes")

        # Trigger resend confirmation (POST)
        r = client.post('/admin/resend/1', follow_redirects=True)
        print(f"POST /admin/resend/1 => {r.status_code} | {r.content_type or ''} | {len(r.data)} bytes")

        # Trigger unlock (POST)
        r = client.post('/admin/unlock/1', follow_redirects=True)
        print(f"POST /admin/unlock/1 => {r.status_code} | {r.content_type or ''} | {len(r.data)} bytes")

        # Test confirmation token handling
        try:
            token = ts.dumps({'m_id': 1})
            r = client.get(f'/confirm/{token}', follow_redirects=True)
            print(f"GET /confirm/<token> => {r.status_code} | {r.content_type or ''} | {len(r.data)} bytes")
        except Exception as e:
            print('Confirm token test failed:', e)
