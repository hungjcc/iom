import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db import get_member_by_id, get_user_by_username, set_member_admin

def print_member(m):
    if not m:
        print('Member not found')
        return
    is_admin = False
    if m.get('m_is_admin') in (1, '1', True, 't', 'true'):
        is_admin = True
    if m.get('is_admin') in (1, '1', True, 't', 'true'):
        is_admin = True
    role = (m.get('m_role') or '')
    if isinstance(role, str) and 'admin' in role.lower():
        is_admin = True
    print(f"id={m.get('m_id') or m.get('id')} username={m.get('m_login_id') or m.get('username')} email={m.get('m_email') or m.get('email')} status={m.get('m_status') or m.get('status')} admin={is_admin} role={role}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python tools/grant_revoke_admin.py <grant|revoke> <member_id|username>')
        sys.exit(1)
    action = sys.argv[1].lower()
    target = sys.argv[2]

    try:
        # resolve member by id or username
        member = None
        if target.isdigit():
            member = get_member_by_id(int(target))
        else:
            member = get_user_by_username(target)
            # normalize to structure matching get_member_by_id
            if member and not member.get('m_id') and member.get('id'):
                # try to fetch full member by id
                try:
                    member = get_member_by_id(member.get('id'))
                except Exception:
                    pass

        print('Before:')
        print_member(member)

        if not member:
            print('No member found; aborting')
            sys.exit(2)

        m_id = member.get('m_id') or member.get('id')
        if action == 'grant':
            ok = set_member_admin(m_id, True)
            print('Grant attempted, ok=', ok)
        elif action == 'revoke':
            ok = set_member_admin(m_id, False)
            print('Revoke attempted, ok=', ok)
        else:
            print('Unknown action:', action)
            sys.exit(3)

        # reload and print
        updated = get_member_by_id(m_id)
        print('After:')
        print_member(updated)

    except Exception:
        traceback.print_exc()
        sys.exit(4)
