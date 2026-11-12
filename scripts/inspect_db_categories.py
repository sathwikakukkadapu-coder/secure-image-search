import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import backend.database.db as db

cats = set()
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM images")
    rows = cursor.fetchall()
    for r in rows:
        cats.add(r['category'])

print("Distinct categories in database:", sorted(list(cats)))
