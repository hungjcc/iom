from app import app
from flask import render_template

with app.test_request_context('/'):
    out = render_template('index.html')
    print(out[:1200])
