from db import get_connection
from werkzeug.security import generate_password_hash

new_password = "TestPass123!"   # choose a secure test password
hashed = generate_password_hash(new_password)

c = get_connection()
cur = c.cursor()
cur.execute("UPDATE dbo.member SET m_pass = ? WHERE m_login_id = ?", (hashed, 'admin'))
c.commit()
c.close()
print('admin password reset to:', new_password)