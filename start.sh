#!/usr/bin/env bash
set -euo pipefail

# Ensure we're running from the repo root (same level as app.py)
SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$SCRIPT_DIR"

# Honour SQLITE_PATH if provided, otherwise default to ./iom.db
export SQLITE_PATH="${SQLITE_PATH:-$SCRIPT_DIR/iom.db}"

echo "[start.sh] Using SQLITE_PATH=$SQLITE_PATH"

# Initialise the database (idempotent)
python tools/init_sqlite_db.py

# Start Gunicorn
exec gunicorn app:app
