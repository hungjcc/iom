#!/usr/bin/env python3
"""Reset a member's password in the SQLite DB."""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from werkzeug.security import generate_password_hash

from db import get_connection


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset a member password")
    parser.add_argument("username", nargs="?", default="admin")
    parser.add_argument("--password", default="TestPass123!")
    args = parser.parse_args()

    new_password = args.password
    hashed = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=16)

    conn = get_connection()
    cur = conn.execute(
        "UPDATE member SET m_pass = ? WHERE m_login_id = ?",
        (hashed, args.username)
    )
    conn.commit()
    conn.close()
    if cur.rowcount:
        print(f"Password for {args.username} updated to: {new_password}")
    else:
        print(f"User {args.username} not found; no rows updated")


if __name__ == "__main__":
    main()
