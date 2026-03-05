import sys, os, traceback
# ensure project root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from app import app
except Exception:
    traceback.print_exc()
    sys.exit(1)

auction_id = 5
with app.test_client() as c:
    r = c.get(f'/auction/{auction_id}')
    print('Status:', r.status_code)
    html = r.data.decode('utf-8')
    # Find the Reserve price line
    import re
    m = re.search(r"<p><strong>Reserve price:</strong>\s*([^<]+)</p>", html)
    if m:
        print('Reserve price text:', m.group(1).strip())
    else:
        # fallback: search for $130
        if '$130' in html:
            print('Found $130 in HTML')
        else:
            print('Reserve price not found in HTML snippet; showing first 400 chars:')
            print(html[:400])
