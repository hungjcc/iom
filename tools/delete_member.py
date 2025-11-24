"""
Delete a member from dbo.member by id or login_id.
Usage:
  python tools/delete_member.py --id 7
  python tools/delete_member.py --login tmp_autotest

Be careful: this performs a DELETE on the database.
"""
import sys, os, argparse, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from db import get_connection
except Exception:
    print('Failed to import get_connection from db.py')
    traceback.print_exc()
    sys.exit(1)

parser = argparse.ArgumentParser()
parser.add_argument('--id', type=int, help='Member id to delete')
parser.add_argument('--login', help='Member login to delete')
parser.add_argument('--yes', action='store_true', help='Confirm deletion without prompt')
args = parser.parse_args()

if not args.id and not args.login:
    print('Specify --id or --login')
    sys.exit(1)

if not args.yes:
    resp = input(f"Are you sure you want to DELETE member {'id='+str(args.id) if args.id else 'login='+args.login}? Type YES to confirm: ")
    if resp.strip() != 'YES':
        print('Aborted')
        sys.exit(0)

try:
    conn = get_connection()
    cur = conn.cursor()
    if args.id:
        cur.execute('DELETE FROM dbo.member WHERE m_id = ?', (args.id,))
        affected = cur.rowcount if hasattr(cur, 'rowcount') else None
    else:
        cur.execute('DELETE FROM dbo.member WHERE m_login_id = ?', (args.login,))
        affected = cur.rowcount if hasattr(cur, 'rowcount') else None
    conn.commit()
    print('Rows affected:', affected)
except Exception:
    traceback.print_exc()
finally:
    try:
        conn.close()
    except Exception:
        pass
