import unittest
from unittest.mock import patch, MagicMock
import types

import db


class TestDBHelpers(unittest.TestCase):

    @patch('db.get_connection')
    def test_create_member_success(self, mock_getconn):
        # Mock cursor behavior
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        # First SELECT (check existing) returns no rows, then SCOPE_IDENTITY returns new_id
        mock_cur.fetchone.side_effect = [None, types.SimpleNamespace(new_id=123)]
        mock_cur.description = [('m_id',), ('m_login_id',)]
        mock_conn.cursor.return_value = mock_cur
        mock_getconn.return_value = mock_conn

        new_id = db.create_member('testuser', 'Secret123!', 'First', 'Last', 'a@b.com')
        # Should return new id (from SCOPE_IDENTITY)
        self.assertEqual(new_id, 123)

    @patch('db.get_connection')
    def test_get_user_by_username_member(self, mock_getconn):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        # Simulate member row: values for m_id, m_login_id, m_pass
        mock_cur.fetchone.side_effect = [(42, 'bob', 'hashed')]
        # description matching m_id, m_login_id, m_pass
        mock_cur.description = [('m_id',), ('m_login_id',), ('m_pass',)]
        mock_conn.cursor.return_value = mock_cur
        mock_getconn.return_value = mock_conn

        user = db.get_user_by_username('bob')
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'bob')
        # m_id returned as 42
        self.assertEqual(int(user['id']), 42)

    @patch('db.get_connection')
    def test_create_member_existing_raises(self, mock_getconn):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        # First SELECT (check existing) returns a row -> simulate existing user
        mock_cur.fetchone.return_value = (999,)
        mock_conn.cursor.return_value = mock_cur
        mock_getconn.return_value = mock_conn

        with self.assertRaises(ValueError):
            db.create_member('existing_user', 'pw12345')

    @patch('db.get_connection')
    def test_confirm_member(self, mock_getconn):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        # Simulate update affecting one row
        mock_cur.rowcount = 1
        mock_conn.cursor.return_value = mock_cur
        mock_getconn.return_value = mock_conn

        ok = db.confirm_member(123)
        self.assertTrue(ok)

    @patch('db.get_connection')
    def test_confirm_member_no_update(self, mock_getconn):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        # Simulate update affecting zero rows
        mock_cur.rowcount = 0
        mock_conn.cursor.return_value = mock_cur
        mock_getconn.return_value = mock_conn

        ok = db.confirm_member(99999)
        self.assertFalse(ok)


if __name__ == '__main__':
    unittest.main()
