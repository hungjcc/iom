#!/usr/bin/env python3
"""List members stored in the SQLite database."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from db import get_connection  # noqa: E402


def main() -> None:
    conn = get_connection()
    rows = conn.execute(
        "SELECT m_id, m_login_id, m_email, m_status, m_is_admin, m_role FROM member ORDER BY m_id"
    ).fetchall()
    if not rows:
        print("No members found")
        return
    for row in rows:
        print(
            f"{row['m_id']:>3}  {row['m_login_id']:<15}  {row['m_email'] or '-':<25}  "
            f"status={row['m_status']}  admin={bool(row['m_is_admin'])}  role={row['m_role'] or '-'}"
        )


if __name__ == "__main__":
    main()
