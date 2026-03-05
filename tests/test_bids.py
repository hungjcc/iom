import os
import unittest
from unittest.mock import patch, MagicMock

os.environ['USE_DB'] = '1'
import app

class BidTests(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        self.client = app.app.test_client()
        # make an admin-like user for session if necessary
        with self.client.session_transaction() as sess:
            sess['u_name'] = 'tester'

    @patch('app._user_dict_from_session')
    def test_bid_too_low(self, mock_user_session):
        # Simulate logged-in user with id
        mock_user_session.return_value = {'username': 'tester', 'id': 5}
        # patch db.place_bid to return False (bid too low)
        m_place = MagicMock(return_value=False)
        with patch('db.place_bid', m_place):
            resp = self.client.post('/auction/1/bid', data={'amount': '1.00'})
            # Should redirect back to auction view
            self.assertIn(resp.status_code, (302, 301))
            m_place.assert_called_once_with(1, 5, '1.00')

    @patch('app._user_dict_from_session')
    def test_bid_success(self, mock_user_session):
        mock_user_session.return_value = {'username': 'tester', 'id': 5}
        m_place = MagicMock(return_value=True)
        with patch('db.place_bid', m_place):
            resp = self.client.post('/auction/2/bid', data={'amount': '100.00'})
            self.assertIn(resp.status_code, (302, 301))
            m_place.assert_called_once_with(2, 5, '100.00')

if __name__ == '__main__':
    unittest.main()
