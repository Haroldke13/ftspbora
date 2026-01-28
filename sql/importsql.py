

import sqlite3

SQLALCHEMY_DATABASE_URI = "sqlite:///../dailytracking_db.sqlite"
import os
SQL_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../filetracking_inserts.sql'))


# Connect to SQLite database
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../dailytracking_db.sqlite'))
conn = sqlite3.connect(db_path)
cur = conn.cursor()

with open(SQL_FILE, "r") as f:
    for line in f:
        stmt = line.strip()
        # Only execute non-empty lines that start with INSERT INTO
        if stmt and stmt.lower().startswith('insert into'):
            try:
                cur.execute(stmt)
            except Exception as e:
                print(f"Error executing: {stmt[:100]}...\n{e}")


conn.commit()
cur.close()
conn.close()

print("SQL file imported successfully.")