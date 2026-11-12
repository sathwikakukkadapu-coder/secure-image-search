import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import backend.database.db as db

with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT category, count(*) as cnt FROM images GROUP BY category")
    for r in cursor.fetchall():
        print(f"Category {r['category']}: {r['cnt']} images")
