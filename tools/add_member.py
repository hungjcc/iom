# tools/add_member.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db import create_member

username = sys.argv[1] if len(sys.argv) > 1 else 'alice'
password = sys.argv[2] if len(sys.argv) > 2 else 'TestPass123!'
first = sys.argv[3] if len(sys.argv) > 3 else None
last = sys.argv[4] if len(sys.argv) > 4 else None
email = sys.argv[5] if len(sys.argv) > 5 else None

new_id = create_member(username, password, first, last, email)
print('Created member id:', new_id)