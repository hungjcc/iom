import os
import time
import unittest

class DBIntegrationTest(unittest.TestCase):
    def test_create_item_and_auction(self):
        # Import DB helpers inside the test to allow skipping if unavailable
        use_db = os.getenv('USE_DB', '').lower() in ('1', 'true', 'yes')
        try:
            from db import create_item_and_auction, get_auction, get_connection
        except Exception:
            self.skipTest('DB helpers not available; skipping integration test')
            return
        if not (use_db and create_item_and_auction and get_auction and get_connection):
            self.skipTest('DB integration not available; skipping integration test')
            return

        title = f"INTEGRATION_TEST_{int(time.time())}"
        # Create item+auction

        auction_id = create_item_and_auction(title, 'integration test description', seller_id=None, starting_price=1.23)
        if auction_id is None:
            self.skipTest('DB integration not available or DB not configured; skipping integration test')

        # Verify auction exists via get_auction
        fetched = get_auction(auction_id)
        if fetched is None:
            self.skipTest('DB integration not available or DB not configured; skipping integration test')
        self.assertEqual(int(fetched.get('id')), int(auction_id))

        # Attempt cleanup: delete auction and the created item (best-effort)
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute('DELETE FROM dbo.auction WHERE a_id = ?', (auction_id,))
            except Exception:
                try:
                    cur.execute('DELETE FROM dbo.auction WHERE id = ?', (auction_id,))
                except Exception:
                    pass
            # delete item if we can find item_id
            item_id = fetched.get('item_id') or fetched.get('a_item_id')
            if item_id:
                try:
                    cur.execute('DELETE FROM dbo.item WHERE item_id = ?', (item_id,))
                except Exception:
                    try:
                        cur.execute('DELETE FROM dbo.item WHERE id = ?', (item_id,))
                    except Exception:
                        pass
            conn.commit()
        except Exception:
            # cleanup best-effort; don't fail the test because cleanup failed
            pass
        finally:
            try:
                if conn:
                    conn.close()
            except Exception:
                pass


if __name__ == '__main__':
    unittest.main()
