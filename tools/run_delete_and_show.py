import traceback
import sys
sys.path.insert(0, '.')

from datetime import datetime

def show_rows(conn, aid):
    cur = conn.cursor()
    out = {}
    # Try common auction pk names
    try:
        cur.execute("SELECT * FROM dbo.auction WHERE a_id = ?", (aid,))
        rows = cur.fetchall()
        out['auction_a_id'] = rows
    except Exception as e:
        out['auction_a_id'] = f'ERR: {e}'
    try:
        cur.execute("SELECT * FROM dbo.auction WHERE id = ?", (aid,))
        rows = cur.fetchall()
        out['auction_id'] = rows
    except Exception as e:
        out['auction_id'] = f'ERR: {e}'
    try:
        cur.execute("SELECT * FROM dbo.auction WHERE auction_id = ?", (aid,))
        rows = cur.fetchall()
        out['auction__auction_id'] = rows
    except Exception as e:
        out['auction__auction_id'] = f'ERR: {e}'

    # Bids
    try:
        cur.execute("SELECT * FROM dbo.bid WHERE b_a_id = ?", (aid,))
        out['bids_b_a_id'] = cur.fetchall()
    except Exception as e:
        out['bids_b_a_id'] = f'ERR: {e}'
    try:
        cur.execute("SELECT * FROM dbo.bid WHERE auction_id = ?", (aid,))
        out['bids_auction_id'] = cur.fetchall()
    except Exception as e:
        out['bids_auction_id'] = f'ERR: {e}'
    try:
        cur.execute("SELECT * FROM dbo.bid WHERE b_auction_id = ?", (aid,))
        out['bids_b_auction_id'] = cur.fetchall()
    except Exception as e:
        out['bids_b_auction_id'] = f'ERR: {e}'
    return out


def print_rows(title, out):
    print(f"--- {title} ---")
    for k, v in out.items():
        print(f"[{k}] -> ")
        if isinstance(v, str):
            print('  ', v)
        else:
            if not v:
                print('  (no rows)')
            else:
                for r in v:
                    try:
                        print('  ', tuple(getattr(r, c) if hasattr(r, c) else r[i] for i, c in enumerate([col[0] for col in r.cursor_description]) ) )
                    except Exception:
                        # fallback simple repr
                        print('  ', r)
    print()


if __name__ == '__main__':
    aid = 57
    if len(sys.argv) > 1:
        try:
            aid = int(sys.argv[1])
        except Exception:
            pass
    print(f"Running delete-and-show for auction id: {aid} at {datetime.utcnow().isoformat()}Z\n")
    try:
        import db
        conn = db.get_connection()
    except Exception:
        traceback.print_exc()
        print('\nFailed to import db or get connection; ensure credentials are configured.')
        sys.exit(2)

    try:
        before = show_rows(conn, aid)
        print_rows('BEFORE', before)
    except Exception:
        traceback.print_exc()

    # Run delete helper
    try:
        try:
            deleted_auctions, deleted_bids = db.delete_auction_and_bids(aid)
        except TypeError:
            # older helper signature may return None or single value
            res = db.delete_auction_and_bids(aid)
            if isinstance(res, tuple):
                deleted_auctions, deleted_bids = res
            else:
                deleted_auctions = res or 0
                deleted_bids = 0
        print(f"Delete helper returned: auctions_removed={deleted_auctions}, bids_removed={deleted_bids}\n")
    except Exception:
        traceback.print_exc()
        print('\nDelete helper failed')

    # Reconnect to ensure consistent view
    try:
        conn.close()
    except Exception:
        pass
    try:
        conn = db.get_connection()
    except Exception:
        traceback.print_exc()
        sys.exit(3)

    try:
        after = show_rows(conn, aid)
        print_rows('AFTER', after)
    except Exception:
        traceback.print_exc()

    try:
        conn.close()
    except Exception:
        pass
    print('Done.')
