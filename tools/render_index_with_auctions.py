import sys, os
sys.path.insert(0, os.getcwd())
from app import app
from db import get_auctions
from flask import render_template

with app.test_request_context('/'):
    auctions = get_auctions(limit=10)
    html = render_template('index.html', recent_auctions=auctions)
    print('Rendered length:', len(html))
    # Print a snippet around our item23 path if present
    if '/static/uploads/item23' in html:
        i = html.index('/static/uploads/item23')
        print('Context:', html[max(0,i-200):i+200])
    else:
        print('item23 path not found in rendered index HTML')
