import pandas as pd

INPUT_CSV = "/home/harold/Desktop/dailytracking/DAILY TRACKING - FINAL  - Requests.csv"
OUTPUT_CSV = "/home/harold/Desktop/dailytracking/DAILY TRACKING - FINAL  - Requests_cleaned.csv"

# Read the CSV
df = pd.read_csv(INPUT_CSV, dtype=str, keep_default_na=False, na_values=["", "nan", "NaN", "N/A", "NA"])

# Replace all remaining NaN/None with empty string
df = df.fillna("")

# Save cleaned CSV
df.to_csv(OUTPUT_CSV, index=False)

print(f"Cleaned CSV written to {OUTPUT_CSV}")