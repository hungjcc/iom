import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app

if __name__ == '__main__':
    with app.test_client() as client:
        r = client.post('/user_login', data={'username': 'alice', 'password': 'Secret123!'}, follow_redirects=True)
        print('Login status:', r.status_code)
        # Print a short excerpt of returned body
        body = r.data.decode('utf-8', errors='replace')
        print('Body excerpt:', body[:300])
        # Show whether session cookie set
        print('Set-Cookie headers:', r.headers.get_all('Set-Cookie'))
