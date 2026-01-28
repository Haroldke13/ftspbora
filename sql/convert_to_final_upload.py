import csv
from datetime import datetime

# Define the new header structure matching canonical CSV
new_header = [
    "ID", "Organization", "Service", "Remarks", "Date Received", "Designate", "Filed by Registry for Action", "Date Filed", "Received by Designate", "Date Received by Designate", "Correction Required", "Date Correction Required", "Corrections Done by Client", "Date Corrections done by Client", "Status", "Date Completed", "Authorization", "Date Authorised", "Signatory", "Dispatch", "Date Dispatched"
]

# Map old header indices to new header indices (where possible)
old_to_new = {
    0: 1,  # Name of the Organization -> Organization
    1: 2,  # Service Requested -> Service
    2: 3,  # Remarks -> Remarks
    3: 4,  # Date Received -> Date Received
    4: 5,  # Designate -> Designate
    5: 6,  # Filed by Registry for Action -> Filed by Registry Action
    7: 8,  # Received by Designate -> Received by Designate (new index)
    8: 9,  # Date Received by Designate -> Date Received by Designate
    9: 10, # Correction Required -> Correction Required
    10: 11,# Date Correction Required -> Date Correction Required
    11: 12,# Corrections Done by Client -> Corrections Done by Client
    12: 13,# Date Corrections done by Client -> Date Corrections done by Client
    13: 14,# Status -> Status
    14: 15,# Date Completed -> Date Completed
    15: 16,# Authorization -> Authorization
    16: 17,# Date Authorised -> Date Authorised
    17: 18,# Signatory -> Signatory
    18: 19,# Dispatch -> Dispatch
    19: 20,# Date Dispatched -> Date Dispatched
    # The rest will be left empty or filled as needed
}

input_file = 'DAILY TRACKING - FINAL  - Requests_uniform_dates.csv'
output_file = 'DAILY TRACKING - FINAL  - Requests_final_upload.csv'

def clean_date(val):
    # Accepts mm/dd/yyyy or empty, else returns empty
    try:
        if val.strip() == '':
            return ''
        dt = datetime.strptime(val.strip(), '%m/%d/%Y')
        return dt.strftime('%m/%d/%Y')
    except Exception:
        return ''

with open(input_file, newline='', encoding='utf-8') as infile, \
     open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.reader(infile)
    old_header = next(reader)
    writer = csv.writer(outfile)
    writer.writerow(new_header)
    id_counter = 4023  # Start from your latest ID, decrementing
    for row in reader:
        new_row = [''] * len(new_header)
        new_row[0] = str(id_counter)
        for old_idx, new_idx in old_to_new.items():
            if old_idx < len(row) and new_idx < len(new_row):
                val = row[old_idx]
                # Clean date fields
                if new_header[new_idx].lower().startswith('date') or 'date' in new_header[new_idx].lower():
                    val = clean_date(val)
                new_row[new_idx] = val
        writer.writerow(new_row)
        id_counter -= 1
print(f"Final upload CSV saved to {output_file} with new structure.")
