README — Quick Command Reference

This file lists useful commands and small tools you can run from PowerShell in the project root (where `app.py` lives).

Prereqs
- Activate venv first:
  ```powershell
  & ".\.env\Scripts\Activate.ps1"
  ```
- Ensure DB connectivity: place `credential.py` in the project root or set `ODBC_DSN` / `ODBC_CONN` (see `db.get_connection()` behavior in `db.py`).

Configuring DB-backed mode (two options)

Option A — Preferred: create a local `credential.py` (recommended for development)
- Copy the example and edit with your values (do NOT commit):
  ```powershell
  copy .\credential.py.example .\credential.py
  # then edit .\credential.py in your editor and fill server/database/username/password
  ```

Option B — Use environment variables (CI / ephemeral runs)
- Using a DSN:
  ```powershell
  $env:ODBC_DSN='MyDsn'; $env:DB_USER='sa'; $env:DB_PASS='pw'
  $env:USE_DB='1'
  python app.py
  ```
- Or using a full connection string:
  ```powershell
  $env:ODBC_CONN="DRIVER={ODBC Driver 18 for SQL Server};SERVER=host;DATABASE=db;UID=user;PWD=pass"
  $env:USE_DB='1'
  python app.py
  ```

Quick DB connection test
- Run this tool to verify connectivity (uses the same `db.get_connection()` logic):
  ```powershell
  python tools/test_conn.py
  ```

Delete items by title (safe script)
- A small helper script `tools/delete_items_by_title.py` can delete rows in the `items` table where `i_title` matches a string. It supports a dry-run and requires `--confirm` to perform the delete.
- Examples (PowerShell):
  ```powershell
  # dry-run: shows count but does not delete
  python tools\delete_items_by_title.py --dry-run

  # actually delete rows with the default title 'E2E test direct'
  python tools\delete_items_by_title.py --confirm

  # specify a different title to match
  python tools\delete_items_by_title.py --confirm --title "My test title"
  ```

Notes
- The script prefers the project's `db.get_connection()` helper. If that is not available it falls back to using `ODBC_CONN` or `ODBC_DSN` + `DB_USER`/`DB_PASS` from the environment.


Run the app
- Run Flask dev server (DB mode optional):
  ```powershell
  $env:USE_DB='1'
  python app.py
  ```

Unit tests
- Run specific tests:
  ```powershell
  python -m unittest tests.test_bids -v
  ```
- Run all tests:
  ```powershell
  python -m unittest discover -v
  ```

Tools (in `tools/`)
- Smoke tests (Flask test client):
  ```powershell
  python tools/smoke_test.py
  python tools/run_smoke_verbose.py
  ```

- DB connection check:
  ```powershell
  python tools/test_conn.py
  ```

- Schema reader (requires pyodbc):
  ```powershell
  # using DSN
  $env:ODBC_DSN='MyDsn'; $env:DB_USER='sa'; $env:DB_PASS='pw'
  python tools/odbc_schema_reader.py --tables auction item member --schema dbo --output schema.json --suggest-joins

  # or using full connection string
  $env:ODBC_CONN="DRIVER={ODBC Driver 18 for SQL Server};SERVER=host;DATABASE=db;UID=user;PWD=pass"
  python tools/odbc_schema_reader.py --tables auction --schema dbo
  ```

- Create test data (item + auction) that matches current schema:
  ```powershell
  python tools/create_item_and_auction.py
  ```

- Create a simple auction (older helper; may use different column names):
  ```powershell
  python tools/create_test_auction.py
  ```

- Reset test passwords (edit file if you want different accounts):
  ```powershell
  python tools/reset_password.py
  ```

- Inspect members / admin flags:
  ```powershell
  python tools/list_members.py
  python tools/inspect_m_is_admin.py
  ```

- Grant / revoke admin (CLI):
  ```powershell
  python tools/grant_revoke_admin.py grant 3
  python tools/grant_revoke_admin.py revoke alice
  ```

- Quick login test (Flask test client):
  ```powershell
  python tools/login_alice_test.py
  python tools/test_login.py
  ```

- Auto place bid (posts to running server, prints DB verification):
  ```powershell
  # defaults: AUCTION_ID=3, TEST_USER=alice, TEST_PASS=TestPass123!, BID_AMOUNT=2.00
  $env:AUCTION_ID='3'; $env:BID_AMOUNT='2.00'
  python tools/auto_place_bid.py
  ```

Utility files
- `credential.py`: optional per-project credentials (preferred by `db.get_connection()`). Example fields: `server`, `database`, `username`, `password`, optional `DB_DRIVER` override.
- `db.py`: contains `get_connection()` and helpers; review it if you need to change connection behavior.

Notes & Troubleshooting
- Most tools call `db.get_connection()` — if you see ODBC errors, create or update `credential.py` or set `ODBC_DSN`/`ODBC_CONN` + `DB_USER`/`DB_PASS`.
- Run tools from the project root to avoid import path issues.
- If using `auto_place_bid.py`, ensure the Flask server is running and reachable at `http://127.0.0.1:5000` (or set `APP_URL` env var).

Want a wrapper CLI or different layout? Reply and I can create `tools/run.py` or expand this README with examples tailored to your environment.
