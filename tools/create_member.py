#!/usr/bin/env python3
"""CLI helper to create a member in the SQLite DB."""

from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from db import create_member, confirm_member  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a member account")
    parser.add_argument("username", nargs="?", default="alice")
    parser.add_argument("--password", default="Secret123!")
    parser.add_argument("--email", default="alice@example.com")
    parser.add_argument("--role", default="user")
    parser.add_argument("--activate", action="store_true", help="Mark the member as active")
    args = parser.parse_args()

    m_id = create_member(args.username, args.password, email=args.email, role=args.role)
    print(f"Created member id: {m_id}")
    if args.activate:
        confirm_member(m_id)
        print("Member activated (status = 'A').")


if __name__ == "__main__":
    main()
