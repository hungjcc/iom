import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure the app imports the test-friendly config
os.environ['USE_DB'] = '1'

import app

class AdminGrantTest(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()
        # create a fake admin session
        with self.client.session_transaction() as sess:
            sess['u_name'] = 'admin'  # user_is_admin will be mocked to True

    @patch('app.user_is_admin', return_value=True)
    @patch('app._user_dict_from_session')
    def test_grant_blocked_for_pending(self, mock_user_from_session, mock_is_admin):
        # Mock to simulate logged in admin user
        mock_user_from_session.return_value = {'username': 'admin', 'm_is_admin': True}

        # Mock get_member_by_id to return a pending user
        pending_member = {'id': 99, 'm_login_id': 'pending_user', 'm_status': 'P'}
        m_get = MagicMock(return_value=pending_member)
        m_set = MagicMock()

        with patch('db.get_member_by_id', m_get), patch('db.set_member_admin', m_set):
            # POST to admin_grant should redirect to admin panel without calling set_member_admin
            resp = self.client.post(f"/admin/grant/{pending_member['id']}")
            self.assertEqual(resp.status_code, 302)
            # ensure set_member_admin was not called because status != 'A'
            m_set.assert_not_called()

    @patch('app.user_is_admin', return_value=True)
    @patch('app._user_dict_from_session')
    def test_grant_allowed_for_active(self, mock_user_from_session, mock_is_admin):
        mock_user_from_session.return_value = {'username': 'admin', 'm_is_admin': True}

        active_member = {'id': 100, 'm_login_id': 'active_user', 'm_status': 'A'}
        m_get = MagicMock(return_value=active_member)
        m_set = MagicMock()

        with patch('db.get_member_by_id', m_get), patch('db.set_member_admin', m_set) as mocked_set:
            resp = self.client.post(f"/admin/grant/{active_member['id']}")
            self.assertEqual(resp.status_code, 302)
            # set_member_admin should be called once to grant admin
            mocked_set.assert_called_once_with(active_member['id'], True)

if __name__ == '__main__':
    unittest.main()
