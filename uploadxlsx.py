from iso8601 import parse_date as iso_parse_date
import pandas as pd
import re
import warnings
from pandas.errors import ParserWarning
from datetime import datetime, date
from app import app
from models import db, FileTracking


XLSX_PATH = "DAILY_TRACKING.xlsx"


def clean_value(field, value):
    import pandas as pd
    # List of all date fields in FileTracking
    DATE_FIELDS = [
        'date_received',
        'date_filed',
        'date_received_by_designate',
        'date_correction_required',
        'date_corrections_done',
        'date_completed',
        'date_authorised',
        'date_dispatched'
    ]
    if pd.isna(value):
        return None

    # Enum fields and their allowed values
    ENUM_FIELDS = {
        'designate': [
            'Asha', 'B. Odero', 'D.O.S', 'Eileen', 'Eric Njoroge',
            'Esther', 'Eznner', 'Finance - Allan', 'Finance - Muktar', 'Finance - Njane',
            'Habiba', 'Judy', 'Kamande', 'Legal - Vitalis', 'L.O - Cate',
            'L.O. - Cate', 'L.O. - Juliet', 'L.O. - Lynn', 'L.O. - Mercy', 'L.O. - Michelle',
            'Naomi', 'N. Sankale', 'Rukia', 'S.Monyoncho', 'Sarah', 'SDOR', 'Sankale', 'Topisia'
        ],
        'filed_by_registry_action': ['Filed', 'Not Filed'],
        'received_by_designate': ['Received', 'Not Received'],
        'correction_sent': ['Correction Sent', 'No Correction Sent'],
        'correction_status': ['Correction Done', 'Correction Not Done', 'Not Required'],
        'status': ['Completed', 'Incomplete'],
        'authorization': ['Authorized', 'Unauthorized', 'Authorised'],
        'signatory': ['Monyoncho', 'I.Sang'],
        'dispatch': ['Dispatched', 'Not Dispatched']
    }

    if field in DATE_FIELDS:
        # Robust parsing: try a list of common formats then fallback to pandas
        s = str(value).strip()
        if s == '' or s.lower() == 'nan':
            return None
        # Normalize separators
        s = re.sub(r'[\.\-]', '/', s)
        s = re.sub(r'\s+', ' ', s).strip()

        # Try comma-style month (e.g. 'Jan 1, 2020')
        try:
            dt = datetime.strptime(s, '%b %d, %Y')
            return dt.date()
        except Exception:
            pass

        formats = [
            '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%Y-%m-%d',
            '%d-%m-%Y', '%m-%d-%Y', '%d %b %Y', '%d %B %Y'
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(s, fmt)
                return dt.date()
            except Exception:
                continue

        # Fallback to pandas parser
        try:
            dt = pd.to_datetime(s, dayfirst=False, errors='coerce')
            if pd.isna(dt):
                return None
            return dt.date()
        except Exception:
            return None

    if field in ENUM_FIELDS:
        allowed = ENUM_FIELDS[field]
        if field == 'authorization' and value in ['Authorised', 'Authorized']:
            return 'Authorized'
        if value in allowed:
            return value
        return None

    # Truncate string fields to 255 chars if needed
    STRING255_FIELDS = [
        'organization_name',
        'service_requested'
    ]
    if field in STRING255_FIELDS and isinstance(value, str) and len(value) > 255:
        return value[:255]
    return value


def parse_date(value):
    if pd.isna(value) or value == "":
        return None
    try:
        dt = pd.to_datetime(value, dayfirst=True, errors="coerce")
        if pd.isna(dt):
            return None
        return dt.date()
    except Exception:
        return None


# Column mapping from spreadsheet header to model field
COLUMN_MAPPING = {
    "Name of the Organization": "organization_name",
    "Service Requested": "service_requested",
    "Remarks": "remarks",
    "Date Received": "date_received",
    "Designate": "designate",
    "Filed by Registry for Action": "filed_by_registry_action",
    "Date Filed": "date_filed",
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


with app.app_context():

    # Ignore pandas parser warnings about mismatched header lengths
    warnings.simplefilter(action='ignore', category=ParserWarning)

    # Read Excel file
    try:
        df = pd.read_excel(XLSX_PATH, engine='openpyxl')
    except Exception:
        # fallback to default engine if openpyxl not available
        df = pd.read_excel(XLSX_PATH)

    # Normalize column names and drop entirely empty / unnamed header columns
    df.columns = df.columns.astype(str).str.strip()
    cols_to_drop = [c for c in df.columns if c == '' or c.startswith('Unnamed')]
    if cols_to_drop:
        print(f"Dropping empty/unnamed columns: {cols_to_drop}")
        df.drop(columns=cols_to_drop, inplace=True)

    # Rename according to mapping
    df.rename(columns=COLUMN_MAPPING, inplace=True)
    # Ensure all columns in mapping are present, fill missing with None
    for col in COLUMN_MAPPING.values():
        if col not in df.columns:
            df[col] = None
    df = df[list(COLUMN_MAPPING.values())]

    for _, row in df.iterrows():
        cleaned = {field: clean_value(field, row[field]) for field in COLUMN_MAPPING.values()}
        record = FileTracking(**cleaned)
        db.session.add(record)

    db.session.commit()


print("✅ XLSX data imported and cleaned successfully")
