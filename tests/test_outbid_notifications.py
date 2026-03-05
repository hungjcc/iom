import os
import unittest
from unittest.mock import MagicMock, patch

os.environ['USE_DB'] = '1'
import app


class OutbidNotificationTests(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        app.USE_DB = True
        self.client = app.app.test_client()
        with self.client.session_transaction() as sess:
            sess['u_name'] = 'tester'

    @patch('app._user_dict_from_session')
    @patch('app.send_outbid_email')
    def test_send_outbid_email_to_previous_highest_bidder(self, m_send_outbid, m_user):
        m_user.return_value = {'username': 'tester', 'id': 5}

        with patch('db.get_auction', return_value={'id': 10, 'title': 'Vintage Watch', 'status': 'open', 'end_time': None}), \
             patch('db.get_current_highest_bidder', return_value={'member_id': 9, 'email': 'prev@example.com', 'amount': 50.0}), \
             patch('db.place_bid', return_value=True):
            resp = self.client.post('/auction/10/bid', data={'amount': '100.00'})

        self.assertIn(resp.status_code, (301, 302))
        m_send_outbid.assert_called_once()
        _, kwargs = m_send_outbid.call_args
        self.assertEqual(kwargs['to_email'], 'prev@example.com')
        self.assertEqual(kwargs['previous_amount'], 50.0)
        self.assertEqual(kwargs['new_amount'], 100.0)

    @patch('app._user_dict_from_session')
    @patch('app.send_outbid_email')
    def test_no_outbid_email_when_same_bidder_is_still_highest(self, m_send_outbid, m_user):
        m_user.return_value = {'username': 'tester', 'id': 5}

        with patch('db.get_auction', return_value={'id': 11, 'title': 'Camera', 'status': 'open', 'end_time': None}), \
             patch('db.get_current_highest_bidder', return_value={'member_id': 5, 'email': 'self@example.com', 'amount': 60.0}), \
             patch('db.place_bid', return_value=True):
            resp = self.client.post('/auction/11/bid', data={'amount': '80.00'})

        self.assertIn(resp.status_code, (301, 302))
        m_send_outbid.assert_not_called()


if __name__ == '__main__':
    unittest.main()
