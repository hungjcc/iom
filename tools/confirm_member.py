"""
Confirm a member (set m_status = 'A') using db.confirm_member(m_id).
Usage:
  python tools/confirm_member.py <m_id>
Example:
  $env:DB_DRIVER='{ODBC Driver 18 for SQL Server}'; python tools/confirm_member.py 5
"""
import sys, os, traceback
# Ensure project root is importable when running from tools/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from db import confirm_member
except Exception:
    print('Failed to import confirm_member from db.py')
    traceback.print_exc()
    sys.exit(1)

if len(sys.argv) < 2:
    print('Usage: python tools/confirm_member.py <m_id>')
    sys.exit(1)

try:
    m_id = int(sys.argv[1])
except Exception:
    print('m_id must be an integer')
    sys.exit(1)

try:
    ok = confirm_member(m_id)
    print(f'confirm_member({m_id}) ->', ok)
    if ok:
        print('Member marked as active (m_status = A)')
    else:
        print('No rows updated or operation failed')
except Exception:
    traceback.print_exc()
    sys.exit(2)
