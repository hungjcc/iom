import requests
url='http://127.0.0.1:5000/static/uploads/item23.JPG'
try:
    r = requests.get(url, timeout=5)
    print('status', r.status_code)
    print('content-type', r.headers.get('Content-Type'))
    print('len', len(r.content))
except Exception as e:
    print('error', e)
