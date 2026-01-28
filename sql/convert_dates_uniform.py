import csv
import re
from datetime import datetime

input_file = 'sql/DAILY TRACKING - FINAL  - Requests.csv'
output_file = 'DAILY TRACKING - FINAL  - Requests_uniform_dates.csv'

def is_date(string):
    patterns = [
        r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',
        r'\b\d{4}[/-]\d{2}[/-]\d{2}\b'
    ]
    for pattern in patterns:
        if re.fullmatch(pattern, string.strip()):
            return True
    return False

def parse_and_format_date(date_str):
    for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d'):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%m/%d/%Y')
        except ValueError:
            continue
    return date_str

def pad_row(row, length):
    return row + [''] * (length - len(row))


with open(input_file, newline='', encoding='utf-8') as infile:
    reader = list(csv.reader(infile))
    header = reader[0]
    # Remove empty column headers
    clean_header = [h for h in header if h.strip() != '']
    num_columns = len(clean_header)
    rows = reader[1:]

with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(clean_header)
    for row in rows:
        # Pad or trim row to header length
        row = pad_row(row, len(header))[:len(header)]
        # Remove empty columns in the same positions as header using zip
        clean_row = [cell for h, cell in zip(header, row) if h.strip() != '']
        clean_row = pad_row(clean_row, num_columns)
        new_row = [parse_and_format_date(cell) if is_date(cell) else cell for cell in clean_row]
        writer.writerow(new_row)

print(f"Uniform CSV saved to {output_file} with {num_columns} columns per row and no empty columns.")
