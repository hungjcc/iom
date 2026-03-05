#!/usr/bin/env python3
"""Delete an auction (and its bids) from the SQLite database."""

from __future__ import annotations

import sys
import traceback
from typing import Optional

from db import get_connection, get_auction


def show_auction(aid: int) -> Optional[dict]:
    a = get_auction(aid)
    if not a:
        print(f"Auction id {aid} not found.")
        return None
    print("\nAuction summary:")
    for key in ("id", "item_id", "title", "status", "start_date", "end_time", "duration", "current_bid"):
        print(f"  {key:>10}: {a.get(key)}")
    print("")
    return a


def confirm_delete(aid: int) -> bool:
    expected = f"DELETE {aid}"
    print("This will PERMANENTLY delete the auction and its bids.")
    print(f"To confirm, type exactly: {expected}")
    ans = input('> ').strip()
    return ans == expected


def delete_auction_and_bids(aid: int) -> None:
    conn = get_connection()
    try:
        conn.execute("BEGIN")
        deleted_bids = conn.execute("DELETE FROM bid WHERE b_a_id = ?", (aid,)).rowcount
        deleted_auctions = conn.execute("DELETE FROM auction WHERE a_id = ?", (aid,)).rowcount
        if deleted_auctions:
            conn.commit()
            print(f"Deleted auction rows: {deleted_auctions}, bids: {deleted_bids}")
        else:
            conn.rollback()
            print("No auction deleted; rolled back.")
    except Exception:
        conn.rollback()
        traceback.print_exc()
        print("Error occurred; transaction rolled back.")
    finally:
        conn.close()


def parse_id(s: str) -> Optional[int]:
    try:
        return int(s)
    except Exception:
        return None


def main() -> None:
    if len(sys.argv) > 1:
        aid = parse_id(sys.argv[1])
        if aid is None:
            print('Invalid auction id argument.')
            return
        if not show_auction(aid):
            return
        if confirm_delete(aid):
            delete_auction_and_bids(aid)
        else:
            print('Confirmation failed; aborting.')
        return

    if not sys.stdin or not getattr(sys.stdin, 'isatty', lambda: True)():
        print("Interactive mode requires a TTY. Run with `.venv/bin/python tools/delete_auction.py`.")
        return

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
        if not show_auction(aid):
            continue
        if confirm_delete(aid):
            delete_auction_and_bids(aid)
        else:
            print('Confirmation failed; not deleting.')


if __name__ == '__main__':
    main()
