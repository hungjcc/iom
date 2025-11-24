#!/usr/bin/env python3
"""
ODBC Schema Reader

Usage examples:

1) Use a DSN (recommended if already configured on this machine):

   set ODBC_DSN=MyDsnName
   set DB_USER=sa
   set DB_PASS=YourPassword
   python tools/odbc_schema_reader.py --tables auction category item member payment subcat users --schema dbo --output schema.json

2) Use a full ODBC connection string:

   set ODBC_CONN=DRIVER={ODBC Driver 17 for SQL Server};SERVER=server.example.com;DATABASE=MyDb;UID=user;PWD=pass
   python tools/odbc_schema_reader.py --tables auction --schema dbo

This script queries `INFORMATION_SCHEMA` to return columns and primary key info
for each table you specify. Output is JSON (printed to stdout or saved to `--output`).

Requires: `pyodbc` (install with `pip install pyodbc`).
"""
import os
import sys
import argparse
import json

try:
    import pyodbc
except Exception as e:
    print("Missing dependency: pyodbc. Install with 'pip install pyodbc'", file=sys.stderr)
    raise


def get_connection():
    dsn = os.getenv('ODBC_DSN')
    conn_env = os.getenv('ODBC_CONN')
    user = os.getenv('DB_USER')
    pwd = os.getenv('DB_PASS')

    if dsn:
        parts = [f"DSN={dsn}"]
        if user:
            parts.append(f"UID={user}")
        if pwd:
            parts.append(f"PWD={pwd}")
        conn_str = ';'.join(parts)
        return pyodbc.connect(conn_str)
    if conn_env:
        return pyodbc.connect(conn_env)

    print("Please set either ODBC_DSN or ODBC_CONN (and optionally DB_USER/DB_PASS).", file=sys.stderr)
    sys.exit(2)


def fetch_table_schema(conn, schema, table):
    cur = conn.cursor()
    # Columns
    cur.execute(
        """
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION,
               NUMERIC_SCALE, IS_NULLABLE, COLUMN_DEFAULT, ORDINAL_POSITION
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """,
        (schema, table)
    )
    columns = []
    for r in cur.fetchall():
        columns.append({
            'column_name': r.COLUMN_NAME,
            'data_type': r.DATA_TYPE,
            'char_max_length': r.CHARACTER_MAXIMUM_LENGTH,
            'numeric_precision': r.NUMERIC_PRECISION,
            'numeric_scale': r.NUMERIC_SCALE,
            'is_nullable': r.IS_NULLABLE,
            'column_default': r.COLUMN_DEFAULT,
            'ordinal_position': r.ORDINAL_POSITION,
        })

    # Primary key columns (if any)
    cur.execute(
        """
        SELECT KU.COLUMN_NAME
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS TC
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE KU
          ON TC.CONSTRAINT_NAME = KU.CONSTRAINT_NAME
        WHERE TC.TABLE_SCHEMA = ? AND TC.TABLE_NAME = ? AND TC.CONSTRAINT_TYPE = 'PRIMARY KEY'
        ORDER BY KU.ORDINAL_POSITION
        """,
        (schema, table)
    )
    pk = [row.COLUMN_NAME for row in cur.fetchall()]

    return {
        'table_schema': schema,
        'table_name': table,
        'columns': columns,
        'primary_key': pk,
    }


def suggest_item_fields(item_schema):
    """Return best-guess column names for common item fields."""
    cols = [c['column_name'] for c in item_schema.get('columns', [])]
    lower = {c.lower(): c for c in cols}

    def find_one(candidates):
        for cand in candidates:
            if cand.lower() in lower:
                return lower[cand.lower()]
        # fallback: substring match
        for cand in candidates:
            for col in cols:
                if cand.lower() in col.lower():
                    return col
        return None

    title = find_one(['title', 'name', 'item_title', 'i_title', 'tittle'])
    description = find_one(['description', 'desc', 'details', 'item_description'])
    image = find_one(['image_url', 'image', 'img', 'picture', 'photo', 'imagepath'])
    possible_id = item_schema.get('primary_key') or []
    if not possible_id:
        # guess id column
        id_guess = find_one(['item_id', 'id', 'i_id', 'itemid'])
        if id_guess:
            possible_id = [id_guess]

    return {
        'title': title,
        'description': description,
        'image': image,
        'primary_key': possible_id,
        'available_columns': cols,
    }


def suggest_joins(auction_schema, item_schema):
    """Suggest possible join column pairs between auction and item tables."""
    auction_cols = [c['column_name'] for c in auction_schema.get('columns', [])]
    item_cols = [c['column_name'] for c in item_schema.get('columns', [])]

    # find item PK
    item_pk = item_schema.get('primary_key') or []
    if not item_pk:
        # guess primary key in item cols
        for cand in ['item_id', 'id', 'i_id', 'itemid']:
            for col in item_cols:
                if cand.lower() == col.lower():
                    item_pk = [col]
                    break
            if item_pk:
                break

    fk_candidates = []
    for col in auction_cols:
        low = col.lower()
        if 'item' in low or low.endswith('_id'):
            if low == (item_pk[0].lower() if item_pk else ''):
                continue
            # numeric FK candidate
            fk_candidates.append(col)

    suggestions = []
    for fk in fk_candidates:
        suggestions.append({'auction_col': fk, 'item_pk': item_pk[0] if item_pk else None})

    return {
        'item_primary_key': item_pk,
        'auction_fk_candidates': fk_candidates,
        'suggested_pairs': suggestions,
    }


def main():
    parser = argparse.ArgumentParser(description='Read table schema via ODBC and output JSON.')
    parser.add_argument('--tables', nargs='+', required=True, help='Table names to inspect (without schema).')
    parser.add_argument('--schema', default='dbo', help='Schema name (default: dbo)')
    parser.add_argument('--output', help='Optional output JSON file (if omitted, prints to stdout)')
    parser.add_argument('--suggest-joins', action='store_true', help='Analyze auction/item schemas and suggest JOIN column names and item field mappings')
    args = parser.parse_args()

    try:
        conn = get_connection()
    except pyodbc.Error as e:
        print('Failed to connect via ODBC:', e, file=sys.stderr)
        sys.exit(3)

    result = {}
    for t in args.tables:
        try:
            schema_info = fetch_table_schema(conn, args.schema, t)
            result[t] = schema_info
        except Exception as e:
            result[t] = {'error': str(e)}

    # If requested, run basic analysis to suggest joins and item field mappings
    analysis = {}
    if args.suggest_joins:
        # look for auction and item schemas in result
        auction = result.get('auction') or result.get('auctions')
        item = result.get('item')
        if auction and item:
            analysis['join_suggestions'] = suggest_joins(auction, item)
            analysis['item_field_suggestions'] = suggest_item_fields(item)
        else:
            analysis['note'] = 'Both "auction" and "item" schemas are required for join suggestions. Include --tables auction item'

    out_payload = {'schemas': result}
    if analysis:
        out_payload['analysis'] = analysis

    out = json.dumps(out_payload, indent=2, default=str)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(out)
        print(f'Wrote schema for {len(args.tables)} table(s) to {args.output}')
    else:
        print(out)


if __name__ == '__main__':
    main()
