import pandas as pd
from datetime import datetime
import re
import shutil
import os

CSV_PATH = "DAILY_TRACKING.csv"
BACKUP_PATH = "DAILYTRACKING.backup.csv"

# Headers in the CSV that should be parsed/formatted
DATE_HEADERS = [
    "Date Received",
    "Date Filed",
    "Date Received by Designate",
    "Date Correction Required",
    "Date Corrections done by Client",
    "Date Completed",
    "Date Authorised",
    "Date Dispatched",
]

print(f"Reading {CSV_PATH}")
# Make a backup
if os.path.exists(CSV_PATH):
    shutil.copy2(CSV_PATH, BACKUP_PATH)
    print(f"Backup written to {BACKUP_PATH}")

# Read robustly
try:
    df = pd.read_csv(CSV_PATH, engine='python', skip_blank_lines=True)
except Exception as e:
    print(f"Error reading CSV: {e}")
    raise

# normalize column names
df.columns = df.columns.astype(str).str.strip()

for hdr in DATE_HEADERS:
    if hdr in df.columns:
        print(f"Processing column: {hdr}")
        # Normalize common separators to a single slash before parsing
        col = df[hdr].astype(str).replace('nan', '')
        col = col.str.strip()
        # Replace hyphens and dots with slashes, collapse multiple spaces
        col = col.str.replace(r'[\.\-]', '/', regex=True)
        col = col.str.replace(r'\s+', ' ', regex=True)

        # Try parsing with several common formats to avoid ambiguous parsing
        def try_parse(s):
            if not s or s.strip() == '' or s.lower() == 'nan':
                return None
            s = s.strip()
            # Direct ISO-like (yyyy-mm-dd or yyyy/mm/dd) or already mm/dd/yyyy
            formats = [
                '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%Y-%m-%d',
                '%d-%m-%Y', '%m-%d-%Y', '%d %b %Y', '%d %B %Y'
            ]
            # If contains comma like 'Jan 1, 2020'
            try:
                return datetime.strptime(s, '%b %d, %Y')
            except Exception:
                pass
            for fmt in formats:
                try:
                    return datetime.strptime(s, fmt)
                except Exception:
                    continue
            # Fallback to pandas parser (dateutil)
            try:
                return pd.to_datetime(s, dayfirst=False, errors='coerce').to_pydatetime()
            except Exception:
                return None

        parsed_series = col.apply(lambda x: try_parse(x))
        # Format parsed datetimes as mm/dd/yyyy, empty string for None
        df[hdr] = parsed_series.apply(lambda d: d.strftime('%m/%d/%Y') if d and not pd.isna(d) else '')
    else:
        print(f"Column not present: {hdr}")

# Write back to CSV (overwrite)
df.to_csv(CSV_PATH, index=False)
print(f"Wrote reformatted CSV to {CSV_PATH}")
print("Done")
