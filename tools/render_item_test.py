import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app
from flask import render_template

with app.test_request_context('/'):
    dummy_item = {
        'id': 123,
        'title': 'Dummy',
        'seller_id': 1,
        'current_bid': (os.getenv('CURRENCY_SYMBOL','HK$') + '100.00'),
        'duration': 7,
        'status': 'open',
        'description': 'A sample item',
        'image_url': '/static/placeholder.png'
    }
    html = render_template('item.html', item=dummy_item, highest_bid=None)
    print('Rendered length:', len(html))
