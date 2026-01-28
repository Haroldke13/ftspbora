import re

SQL_FILE = "/home/harold/Desktop/dailytracking/filetracking_inserts.sql"
SQL_FILE_FIXED = "/home/harold/Desktop/dailytracking/filetracking_inserts_fixed.sql"

# List of reserved words to quote
reserved = ['authorization']

def quote_reserved_columns(sql, reserved):
    # Replace column names in the INSERT INTO (...) part
    def replacer(match):
        cols = match.group(1).split(',')
        cols = [col.strip() for col in cols]
        cols = [f'"{col}"' if col in reserved else col for col in cols]
        return "INSERT INTO filetracking (" + ', '.join(cols) + ")"
    sql = re.sub(r"INSERT INTO filetracking \((.*?)\)", replacer, sql)
    return sql

with open(SQL_FILE, "r") as f:
    sql = f.read()

sql_fixed = quote_reserved_columns(sql, reserved)

with open(SQL_FILE_FIXED, "w") as f:
    f.write(sql_fixed)

print(f"Fixed SQL written to {SQL_FILE_FIXED}")