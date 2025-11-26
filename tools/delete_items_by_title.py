"""
Safe deletion helper for items with title 'E2E test direct'.

Usage (PowerShell):
  & ".\.env\Scripts\Activate.ps1";
  python tools\delete_items_by_title.py --dry-run
  python tools\delete_items_by_title.py --confirm

The script prefers the project's `db.get_connection()` if available, otherwise it will
try to connect using `ODBC_CONN` or `ODBC_DSN` + `DB_USER`/`DB_PASS` environment variables.

It prints counts before and after and requires `--confirm` to actually delete (safety).
"""
from __future__ import annotations
import os
import sys
import argparse

DRY_RUN = False
TARGET_TITLE = "TEST ITEM - Manual"


def get_conn_via_db_module():
    try:
        # attempt to import the project's db helper
        import db
        conn = db.get_connection()
        return conn
    except Exception:
        return None


def get_conn_via_pyodbc():
    try:
        import pyodbc
    except Exception as ex:
        print("pyodbc not available:", ex)
        return None

    conn_str = os.environ.get("ODBC_CONN")
    if conn_str:
        try:
            return pyodbc.connect(conn_str, autocommit=False)
        except Exception as ex:
            print("Failed to connect using ODBC_CONN:", ex)
            return None

    dsn = os.environ.get("ODBC_DSN")
    user = os.environ.get("DB_USER")
    pwd = os.environ.get("DB_PASS")
    if dsn:
        try:
            if user and pwd:
                return pyodbc.connect(f"DSN={dsn};UID={user};PWD={pwd}", autocommit=False)
            else:
                return pyodbc.connect(f"DSN={dsn}", autocommit=False)
        except Exception as ex:
            print("Failed to connect using DSN:", ex)
            return None

    print("No ODBC_CONN or ODBC_DSN found in environment. Please provide credentials via environment or use project's db module.")
    return None


def find_item_id_column(cursor):
    # legacy placeholder (kept for backward compatibility) — prefer using
    # the schema-aware helpers below instead.
    return None


def find_items_table(cursor):
    """Try to detect the table that contains an `i_title` column.

    Returns a tuple (schema, table) or None.
    """
    try:
        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE COLUMN_NAME = 'i_title'
            ORDER BY TABLE_SCHEMA = 'dbo' DESC, TABLE_NAME
        """)
        row = cursor.fetchone()
        if row:
            return row[0], row[1]
    except Exception:
        pass

    # fallback: try common table names in dbo
    common = ["items", "item", "itm_item", "i_item"]
    for t in common:
        try:
            cursor.execute("SELECT TOP 1 1 FROM dbo." + t)
            return 'dbo', t
        except Exception:
            try:
                cursor.execute("SELECT TOP 1 1 FROM " + t)
                return None, t
            except Exception:
                pass
    return None


def find_item_id_column_for_table(cursor, schema, table):
    """Find a likely id column name for the given table by checking known candidates
    and inspecting the table columns.
    Returns the column name or None.
    """
    candidates = ["i_id", "a_id", "id", "item_id", "itm_id"]
    qualified = f"{schema + '.' if schema else ''}{table}"
    for c in candidates:
        try:
            cursor.execute(f"SELECT TOP 1 {c} FROM {qualified}")
            row = cursor.fetchone()
            if row is not None:
                return c
        except Exception:
            pass
    try:
        cursor.execute(f"SELECT TOP 1 * FROM {qualified}")
        cols = [d[0] for d in cursor.description]
        for col in cols:
            if col.lower() in ("i_id", "id", "item_id", "itm_id"):
                return col
    except Exception:
        pass
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Show matching rows and counts but don't delete")
    parser.add_argument("--confirm", action="store_true", help="Actually perform the delete")
    parser.add_argument("--title", default=TARGET_TITLE, help="Title to match (default: 'E2E test direct')")
    args = parser.parse_args()

    title = args.title

    conn = get_conn_via_db_module()
    if conn is None:
        conn = get_conn_via_pyodbc()
    if conn is None:
        print("Unable to obtain DB connection. Exiting.")
        sys.exit(2)

    cur = conn.cursor()

    # detect the table that contains i_title
    found = find_items_table(cur)
    if not found:
        print("Could not locate a table with column 'i_title'. Please verify your schema.")
        conn.close()
        sys.exit(3)
    schema, table = found
    qualified = (schema + "." + table) if schema else table

    # find id column to show rows
    id_col = find_item_id_column_for_table(cur, schema, table) or "(unknown_id)"

    # count matching rows
    try:
        cur.execute(f"SELECT COUNT(*) FROM {qualified} WHERE i_title = ?", (title,))
        count_before = cur.fetchone()[0]
    except Exception as ex:
        print("Error counting matching rows:", ex)
        conn.close()
        sys.exit(3)

    print(f"Found {count_before} rows in `{qualified}` with i_title = '{title}' (id column hint: {id_col})")

    if args.dry_run or not args.confirm:
        print("Dry run mode or no --confirm supplied; no rows will be deleted.")
    if count_before == 0:
        print("Nothing to delete; exiting.")
        conn.close()
        return

    if not args.confirm:
        print("To delete these rows, re-run with the `--confirm` flag.")
        conn.close()
        return

    # perform deletion of dependents (auctions referencing these items) then items
    try:
        # collect item ids
        cur.execute(f"SELECT {id_col} FROM {qualified} WHERE i_title = ?", (title,))
        rows = cur.fetchall()
        item_ids = [r[0] for r in rows]
        if not item_ids:
            print("No item IDs found; nothing to delete.")
            conn.close()
            return

        placeholders = ",".join(["?" for _ in item_ids])

        # backup folder
        import datetime, csv, os
        ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        backup_dir = os.path.join(os.path.dirname(__file__), "backups", ts)
        os.makedirs(backup_dir, exist_ok=True)

        def dump_query_to_csv(cur, query, params, filename):
            try:
                cur.execute(query, params)
                cols = [d[0] for d in cur.description]
                rows = cur.fetchall()
                with open(os.path.join(backup_dir, filename), "w", newline='', encoding='utf-8') as f:
                    w = csv.writer(f)
                    w.writerow(cols)
                    for r in rows:
                        w.writerow(list(r))
                return len(rows)
            except Exception:
                return 0

        # find auctions referencing these items
        auction_ids = []
        try:
            cur.execute(f"SELECT a_id FROM dbo.auction WHERE a_item_id IN ({placeholders})", item_ids)
            auction_rows = cur.fetchall()
            auction_ids = [r[0] for r in auction_rows]
        except Exception:
            auction_ids = []

        # backup auctions and related bids
        total_dependent = 0
        deleted_dependent = 0

        if auction_ids:
            ap = ",".join(["?" for _ in auction_ids])
            # backup auctions
            cnt_a = dump_query_to_csv(cur, f"SELECT * FROM dbo.auction WHERE a_id IN ({ap})", auction_ids, "dbo_auction_before_delete.csv")
            # find and backup bids referencing these auctions
            cnt_b = dump_query_to_csv(cur, f"SELECT * FROM dbo.bid WHERE b_a_id IN ({ap})", auction_ids, "dbo_bid_before_delete.csv")
            total_dependent += cnt_a + cnt_b

            # delete bids first
            try:
                cur.execute(f"DELETE FROM dbo.bid WHERE b_a_id IN ({ap})", auction_ids)
                deleted_bids = cur.rowcount
                deleted_dependent += deleted_bids
            except Exception as ex:
                print("Error deleting bids:", ex)
                raise

            # then delete auctions
            try:
                cur.execute(f"DELETE FROM dbo.auction WHERE a_id IN ({ap})", auction_ids)
                deleted_auctions = cur.rowcount
                deleted_dependent += deleted_auctions
            except Exception as ex:
                print("Error deleting auctions:", ex)
                raise

        # detect and handle other dependents that reference items directly (e.g., item_image)
        cur.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        tables = cur.fetchall()
        fk_candidates = ["item_id", "i_id", "itm_id"]
        other_dependents = []
        for sch, tbl in tables:
            if (sch or '').lower() == (schema or '').lower() and tbl.lower() == table.lower():
                continue
            # skip auction table since already handled
            if ((sch or '').lower(), tbl.lower()) == (('dbo' if schema else '').lower(), 'auction'):
                continue
            for col in fk_candidates:
                try:
                    cur.execute("SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=? AND TABLE_NAME=? AND COLUMN_NAME=?", (sch, tbl, col))
                    if cur.fetchone():
                        qualified_other = (sch + "." + tbl) if sch else tbl
                        cnt_q = 0
                        try:
                            cur.execute(f"SELECT COUNT(*) FROM {qualified_other} WHERE {col} IN ({placeholders})", item_ids)
                            cnt_q = cur.fetchone()[0]
                        except Exception:
                            cnt_q = 0
                        if cnt_q and cnt_q > 0:
                            other_dependents.append((qualified_other, col, cnt_q))
                            break
                except Exception:
                    pass

        for qtbl, col, cnt in other_dependents:
            print(f" - {cnt} rows in {qtbl} referencing these items via column {col}")
            # backup
            dump_query_to_csv(cur, f"SELECT * FROM {qtbl} WHERE {col} IN ({placeholders})", item_ids, f"{qtbl.replace('.', '_')}_before_delete.csv")
            # delete
            cur.execute(f"DELETE FROM {qtbl} WHERE {col} IN ({placeholders})", item_ids)
            deleted_dependent += cur.rowcount

        # finally delete items by id
        cur.execute(f"DELETE FROM {qualified} WHERE {id_col} IN ({placeholders})", item_ids)
        deleted_items = cur.rowcount

        conn.commit()
        print(f"Deleted {deleted_dependent} dependent row(s) and {deleted_items} item row(s) from {qualified}.")

        # verify remaining
        cur.execute(f"SELECT COUNT(*) FROM {qualified} WHERE i_title = ?", (title,))
        count_after = cur.fetchone()[0]
        print(f"Rows remaining with that title after delete: {count_after}")

    except Exception as ex:
        print("Error during delete, rolling back:", ex)
        try:
            conn.rollback()
        except Exception:
            pass
        conn.close()
        sys.exit(4)

    conn.close()


if __name__ == '__main__':
    main()
