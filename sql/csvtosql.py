

import pandas as pd
import re

CSV_PATH = "/home/harold/Desktop/dailytracking/DAILY TRACKING - FINAL  - Requests_cleaned.csv"
SQL_PATH = "/home/harold/Desktop/dailytracking/filetracking_inserts.sql"

    # Map CSV columns to DB columns
COLUMN_MAPPING = {
        "Name of the Organization": "organization_name",
        "Service Requested": "service_requested",
        "Remarks": "remarks",
        "Date Received": "date_received",
        "Designate": "designate",
        "Filed by Registry for Action": "filed_by_registry_action",
        "Received by Designate": "received_by_designate",
        "Date Received by Designate": "date_received_by_designate",
            "Correction Required": "correction_sent",
            "Date Correction Required": "date_correction_required",
            "Corrections Done by Client": "correction_status",
            "Date Corrections done by Client": "date_corrections_done",
        "Status": "status",
        "Date Completed": "date_completed",
        "Authorization": "authorization",
        "Date Authorised": "date_authorised",
        "Signatory": "signatory",
        "Dispatch": "dispatch",
        "Date Dispatched": "date_dispatched"
    }

    # Reserved words in PostgreSQL that need quoting
def quote_col(col):
        if col in ["authorization"]:
            return f'"{col}"'
        return col

def sql_escape(val):
        if pd.isna(val):
            return "NULL"
        if isinstance(val, str):
            return "'" + val.replace("'", "''") + "'"
        return f"'{val}'"

def main():
        df = pd.read_csv(CSV_PATH)
        df.rename(columns=COLUMN_MAPPING, inplace=True)
        df = df[list(COLUMN_MAPPING.values())]

        # Truncate string fields to 3000 chars (per your models.py)
        for col in ["organization_name", "service_requested"]:
            df[col] = df[col].astype(str).str.slice(0, 3000)
            df.loc[df[col] == 'nan', col] = None

        with open(SQL_PATH, "w") as f:
            for _, row in df.iterrows():
                values = [sql_escape(row[col]) for col in df.columns]
                columns = ', '.join([quote_col(col) for col in df.columns])
                sql = f"INSERT INTO filetracking ({columns}) VALUES ({', '.join(values)});\n"
                f.write(sql)

        print(f"SQL file written to {SQL_PATH}")

if __name__ == "__main__":
        main()