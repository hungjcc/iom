import sys
import os
import traceback

# Ensure project root is on sys.path so local modules (like `db` and `credential`) can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import db

try:
    conn = db.get_connection()
    print("Connected OK:", conn)
    try:
        conn.close()
    except Exception:
        pass
except Exception:
    traceback.print_exc()