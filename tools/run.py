#!/usr/bin/env python
"""
tools/run.py - small wrapper to run common project tooling from one place.

Usage examples:
  python tools/run.py smoke
  python tools/run.py create-item-auction
  python tools/run.py reset-password
  python tools/run.py grant 3
  python tools/run.py revoke alice
  python tools/run.py auto-bid --auction 3 --amount 5.00
  python tools/run.py schema --tables auction item --output schema.json
"""
import argparse
import subprocess
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PY = sys.executable or 'python'

def run_cmd(cmd, env=None):
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    print('Running:', ' '.join(cmd))
    r = subprocess.run(cmd, env=full_env)
    return r.returncode


def run_module(module, args=None, env=None):
    """Run a tool as a module: python -m tools.<module> [args...]"""
    cmd = [PY, '-m', f'tools.{module}']
    if args:
        cmd += list(args)
    return run_cmd(cmd, env=env)

def main():
    p = argparse.ArgumentParser(description='Run project helper scripts')
    sub = p.add_subparsers(dest='cmd')

    sub.add_parser('smoke', help='Run smoke_test via Flask test client')
    sub.add_parser('smoke-verbose', help='Run run_smoke_verbose')
    sub.add_parser('test-conn', help='Run DB connection test')
    sub.add_parser('list-members', help='List members (list_members.py)')
    sub.add_parser('inspect-admin', help='Inspect raw m_is_admin flags')
    sub.add_parser('create-item-auction', help='Create item + auction that matches schema')
    sub.add_parser('create-test-auction', help='Create a simple auction (legacy helper)')
    sub.add_parser('reset-password', help='Reset test password for admin (edit script to change user)')
    sub.add_parser('print-alice-pass', help='Print alice password hash from DB')
    sub.add_parser('login-alice-test', help='Run login_alice_test using Flask test client')
    sub.add_parser('auto-bid', help='Auto place a bid to a running server')

    # grant/revoke with args
    g = sub.add_parser('grant', help='Grant admin to member id or username')
    g.add_argument('target', help='member id or username')
    r = sub.add_parser('revoke', help='Revoke admin from member id or username')
    r.add_argument('target', help='member id or username')

    # schema reader passthrough
    s = sub.add_parser('schema', help='Run odbc_schema_reader with args')
    s.add_argument('--tables', nargs='+', required=True)
    s.add_argument('--schema', default='dbo')
    s.add_argument('--output')
    s.add_argument('--suggest-joins', action='store_true')

    # tests runner
    t = sub.add_parser('test', help='Run unit tests (unittest discover by default)')
    t.add_argument('pattern', nargs='?', default='discover')

    args, extra = p.parse_known_args()
    if not args.cmd:
        p.print_help()
        sys.exit(1)

    # Map commands to script invocations
    if args.cmd == 'smoke':
        sys.exit(run_module('smoke_test'))
    if args.cmd == 'smoke-verbose':
        sys.exit(run_module('run_smoke_verbose'))
    if args.cmd == 'test-conn':
        sys.exit(run_module('test_conn'))
    if args.cmd == 'list-members':
        sys.exit(run_module('list_members'))
    if args.cmd == 'inspect-admin':
        sys.exit(run_module('inspect_m_is_admin'))
    if args.cmd == 'create-item-auction':
        sys.exit(run_module('create_item_and_auction'))
    if args.cmd == 'create-test-auction':
        sys.exit(run_module('create_test_auction'))
    if args.cmd == 'reset-password':
        sys.exit(run_module('reset_password'))
    if args.cmd == 'print-alice-pass':
        sys.exit(run_module('print_alice_pass'))
    if args.cmd == 'login-alice-test':
        sys.exit(run_module('login_alice_test'))
    if args.cmd == 'auto-bid':
        # allow optional env overrides via extra args
        # supported extra: --auction N --amount X --user U --pass P --url URL
        import argparse as _arg
        ap = _arg.ArgumentParser()
        ap.add_argument('--auction', default='3')
        ap.add_argument('--amount', default='2.00')
        ap.add_argument('--user', default='alice')
        ap.add_argument('--passw', dest='passw', default='TestPass123!')
        ap.add_argument('--url', default='http://127.0.0.1:5000')
        parsed, _ = ap.parse_known_args(extra)
        env = {
            'AUCTION_ID': str(parsed.auction),
            'BID_AMOUNT': str(parsed.amount),
            'TEST_USER': str(parsed.user),
            'TEST_PASS': str(parsed.passw),
            'APP_URL': str(parsed.url),
        }
        sys.exit(run_module('auto_place_bid', args=None, env=env))

    if args.cmd == 'grant':
        sys.exit(run_module('grant_revoke_admin', args=['grant', args.target]))
    if args.cmd == 'revoke':
        sys.exit(run_module('grant_revoke_admin', args=['revoke', args.target]))

    if args.cmd == 'schema':
        cmd = ['--schema', args.schema, '--tables'] + args.tables
        if args.output:
            cmd += ['--output', args.output]
        if args.suggest_joins:
            cmd += ['--suggest-joins']
        sys.exit(run_module('odbc_schema_reader', args=cmd))

    if args.cmd == 'test':
        if args.pattern == 'discover':
            sys.exit(run_cmd([PY, '-m', 'unittest', 'discover', '-v']))
        else:
            sys.exit(run_cmd([PY, '-m', 'unittest', args.pattern, '-v']))

    print('Unknown command:', args.cmd)
    sys.exit(2)

if __name__ == '__main__':
    main()
