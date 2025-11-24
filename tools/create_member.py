import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db import create_member

if __name__ == '__main__':
    username = 'alice'
    password = 'Secret123!'
    first_name = 'Alice'
    last_name = 'Admin'
    email = 'alice@example.com'
    try:
        new_id = create_member(username, password, first_name, last_name, email)
        print('Created member id:', new_id)
    except Exception as e:
        print('Create member failed:', e)
        raise
