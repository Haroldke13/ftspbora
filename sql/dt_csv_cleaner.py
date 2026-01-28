import pandas as pd
from datetime import datetime

INPUT_CSV = "/home/harold/Desktop/dailytracking/DAILY TRACKING - FINAL  - Requests.csv"
OUTPUT_CSV = "/home/harold/Desktop/dailytracking/dt.csv"

# Read the CSV as strings to preserve all data
# Use keep_default_na=False to avoid pandas auto-converting blanks to NaN
# We'll handle missing values ourselves

df = pd.read_csv(INPUT_CSV, dtype=str, keep_default_na=False)

# Fill missing values with None (so we can output as NULL)
df = df.where(df.notnull(), None)

# Standardize date columns to YYYY-MM-DD or NULL
DATE_COLS = [
    'Date Received',
    'Date Received by Designate',
    'Date Corrections done by Client',
    'Date Completed',
    'Date Authorised',
    'Date Dispatched'
]

def format_date(val):
    if val is None or str(val).strip() == '':
        return 'NULL'
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y", "%d-%b-%Y", "%d/%m/%Y "):
        try:
            dt = datetime.strptime(str(val).strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            continue
    return 'NULL'

for col in DATE_COLS:
    if col in df.columns:
        df[col] = df[col].apply(format_date)

# Fill all other missing values with NULL
for col in df.columns:
    if col not in DATE_COLS:
        df[col] = df[col].apply(lambda x: 'NULL' if x is None or str(x).strip() == '' else str(x).strip())

# Save as CSV, comma separated, no index, with correct column labels
# Use quoting to ensure commas in values are handled
import csv
df.to_csv(OUTPUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)

print(f"Cleaned CSV written to {OUTPUT_CSV}")
