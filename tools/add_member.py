#!/usr/bin/env python3
"""Shorthand helper to create a member."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db import create_member

username = sys.argv[1] if len(sys.argv) > 1 else 'alice'
password = sys.argv[2] if len(sys.argv) > 2 else 'TestPass123!'
email = sys.argv[3] if len(sys.argv) > 3 else 'alice@example.com'
role = sys.argv[4] if len(sys.argv) > 4 else 'user'

new_id = create_member(username, password, email=email, role=role)
print('Created member id:', new_id)
