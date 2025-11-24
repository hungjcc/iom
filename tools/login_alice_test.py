from app import app

with app.test_client() as c:
    resp = c.post('/user_login', data={'username':'admin','password':'TestPass123!'}, follow_redirects=True)
    print('status', resp.status_code)
    body = resp.get_data(as_text=True)
    print(body[:1000])
    # check whether session set
    admin = c.get('/admin')
    print('/admin', admin.status_code)
    print(admin.get_data(as_text=True)[:400])
