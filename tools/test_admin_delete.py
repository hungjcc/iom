import sys, types
sys.path.insert(0,'.')
import importlib
app = importlib.import_module('app')
# Ensure app is in a known state
app.USE_DB = True
# Provide a fake get_user_by_username to identify admin users
app.get_user_by_username = lambda username: {'id':1,'username':'admin','m_is_admin':True,'is_admin':True,'m_login_id':'admin'}
# Create fake db module to intercept deletion
fake_db = types.ModuleType('db')
def fake_delete(aid):
    print('fake_delete called', aid)
    return (1, 2)
fake_db.delete_auction_and_bids = fake_delete
sys.modules['db'] = fake_db
# Use test client to simulate POST with admin session
client = app.app.test_client()
with client.session_transaction() as sess:
    sess['u_name'] = 'admin'
resp = client.post('/admin/auction/123/delete', follow_redirects=True)
print('status', resp.status_code)
text = resp.data.decode()
print('deleted message present?', 'Deleted auction' in text)
print('deleted bids phrase present?', 'bids' in text and 'Deleted auction' not in text)
print('response length', len(text))
