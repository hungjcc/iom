#!/usr/bin/env python3
"""
Interactive script to delete an auction (and its bids) by auction id.

Usage:
  python tools/delete_auction.py <auction_id>
  python tools/delete_auction.py    # interactive prompt

This script uses the project's `db.get_connection` and `db.get_auction` helpers
to display the auction row before deletion. It will delete rows in `dbo.bid`
where `b_a_id = <auction_id>` and then delete from `dbo.auction` where
`a_id = <auction_id>` inside a transaction. It asks for an explicit
confirmation string `DELETE <id>` before making changes.
"""
import sys
import traceback
from typing import Optional

try:
    from db import get_connection, get_auction
except Exception:
    # If script is run from tools/ directory, ensure package path
    try:
        import importlib, os, sys as _sys
        _sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        db = importlib.import_module('db')
        get_connection = db.get_connection
        get_auction = db.get_auction
    except Exception:
        raise


def show_auction(aid: int) -> Optional[dict]:
    a = get_auction(aid)
    if not a:
        print(f"Auction id {aid} not found.")
        return None
    print("\nAuction summary:")
    print(f"  id:        {a.get('id')}")
    print(f"  item_id:   {a.get('item_id')}")
    print(f"  title:     {a.get('title')}")
    print(f"  status:    {a.get('status')}")
    print(f"  start:     {a.get('start_date')}")
    print(f"  end_time:  {a.get('end_time')}")
    print(f"  duration:  {a.get('duration')}")
    print(f"  current:   {a.get('current_bid')}")
    print("")
    return a


def confirm_delete(aid: int) -> bool:
    expected = f"DELETE {aid}"
    print("This will PERMANENTLY delete the auction and its bids.")
    print(f"To confirm, type exactly: {expected}")
    ans = input('> ').strip()
    return ans == expected


def delete_auction_and_bids(aid: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Start transaction if supported
        try:
            cur.execute('BEGIN TRANSACTION')
        except Exception:
            # Some ODBC drivers don't allow explicit BEGIN from client; rely on autocommit off
            pass

        # Delete bids first (if table exists)
        try:
            cur.execute('DELETE FROM dbo.bid WHERE b_a_id = ?', (aid,))
            deleted_bids = cur.rowcount
            print(f"Deleted bids: {deleted_bids}")
        except Exception as e:
            print('Warning: could not delete from dbo.bid (maybe table missing).')
            print('  ', e)

        # Delete auction row
        try:
            cur.execute('DELETE FROM dbo.auction WHERE a_id = ?', (aid,))
            deleted_auctions = cur.rowcount
            print(f"Deleted auction rows: {deleted_auctions}")
        except Exception as e:
            print('Error deleting auction row:')
            raise

        # Ensure we actually deleted the auction; otherwise rollback
        if deleted_auctions == 0:
            conn.rollback()
            print('No auction row deleted; rolled back.')
            return

        conn.commit()
        print('Deletion committed.')
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        print('An error occurred; transaction rolled back.')
        traceback.print_exc()
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def parse_id(s: str) -> Optional[int]:
    try:
        return int(s)
    except Exception:
        return None


def main():
    if len(sys.argv) > 1:
        sid = parse_id(sys.argv[1])
        if sid is None:
            print('Invalid auction id argument.')
            return
        aid = sid
        a = show_auction(aid)
        if not a:
            return
        if not confirm_delete(aid):
            print('Confirmation failed; aborting.')
            return
        delete_auction_and_bids(aid)
        return

    # Interactive loop
    # If stdin is not an interactive TTY (some launchers detach stdin), show
    # a helpful message instead of silently exiting.
    try:
        if not sys.stdin or not sys.stdin.isatty():
            print("Interactive mode requires a TTY. Run with `python tools/delete_auction.py` (use your venv python).")
            return
    except Exception:
        # If isatty is not available or fails for any reason, continue and
        # attempt interactive mode.
        pass

    print('Interactive auction delete. Enter auction id to delete, or q to quit.')
    while True:
        v = input('Auction id> ').strip()
        if not v:
            continue
        if v.lower() in ('q', 'quit', 'exit'):
            print('Bye.')
            return
        aid = parse_id(v)
        if aid is None:
            print('Please enter a numeric auction id.')
            continue
        a = show_auction(aid)
        if not a:
            continue
        if not confirm_delete(aid):
            print('Confirmation failed; not deleting.')
            continue
        delete_auction_and_bids(aid)


if __name__ == '__main__':
    main()
