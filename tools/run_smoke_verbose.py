import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app
import traceback

paths = ['/', '/search?key_word=test', '/user_login', '/register', '/logout', '/user_menu', '/browse', '/sell', '/help', '/static/app.js', '/static/styles.css']

with app.test_client() as client:
    for p in paths:
        try:
            r = client.get(p, follow_redirects=True)
            print(f"{p} => {r.status_code} | {r.content_type} | {len(r.data)} bytes")
        except Exception:
            print('ERROR for', p)
            traceback.print_exc()
