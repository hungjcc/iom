#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$SCRIPT_DIR"

export SQLITE_PATH="${SQLITE_PATH:-$SCRIPT_DIR/iom.db}"
PORT="${PORT:-10000}"

echo "[start.sh] Using SQLITE_PATH=$SQLITE_PATH"
python tools/init_sqlite_db.py

echo "[start.sh] Starting gunicorn on 0.0.0.0:$PORT"
exec gunicorn --bind "0.0.0.0:${PORT}" app:app
