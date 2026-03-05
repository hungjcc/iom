import os
import unittest
from unittest.mock import patch

os.environ['USE_DB'] = '1'
import app


class LoginRateLimitTests(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        app.USE_DB = True
        app.LOGIN_ATTEMPTS.clear()
        self.client = app.app.test_client()

    @patch('app.get_user_by_username')
    def test_unknown_user_attempts_get_locked(self, m_get_user):
        m_get_user.return_value = None
        ip = '203.0.113.10'

        for _ in range(app.MAX_FAILED):
            self.client.post('/user_login', data={'username': 'ghost', 'password': 'bad'}, headers={'X-Forwarded-For': ip})

        resp = self.client.post('/user_login', data={'username': 'ghost', 'password': 'bad'}, headers={'X-Forwarded-For': ip})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Too many login attempts. Try again later.', resp.data)

    @patch('app.verify_password')
    @patch('app.get_user_by_username')
    def test_successful_login_clears_rate_limit_counters(self, m_get_user, m_verify):
        ip = '198.51.100.99'
        username = 'alice'
        m_get_user.return_value = {'id': 5, 'password': 'hashed'}
        m_verify.return_value = False

        self.client.post('/user_login', data={'username': username, 'password': 'bad'}, headers={'X-Forwarded-For': ip})
        self.assertTrue(app.LOGIN_ATTEMPTS)

        m_verify.return_value = True
        resp = self.client.post('/user_login', data={'username': username, 'password': 'good'}, headers={'X-Forwarded-For': ip})

        self.assertIn(resp.status_code, (301, 302))
        self.assertNotIn(f'user:{username}'.lower(), app.LOGIN_ATTEMPTS)
        self.assertNotIn(f'ip:{ip}'.lower(), app.LOGIN_ATTEMPTS)


if __name__ == '__main__':
    unittest.main()
