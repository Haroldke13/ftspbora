




from iso8601 import parse_date
import pandas as pd
from datetime import datetime, date
from app import app
from models import db, FileTracking

CSV_PATH = "DAILYTRACKING.csv"


def clean_value(field, value):
    import pandas as pd
    # List of all date fields in FileTracking
    DATE_FIELDS = [
        'date_received',
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
        # Try to parse as date, else return None
        try:
            dt = pd.to_datetime(value, dayfirst=True, errors='coerce')
            if pd.isna(dt):
                return None
            return dt.date()
        except Exception:
            return None

    if field in ENUM_FIELDS:
        # Accept both Authorised and Authorized for 'authorization' field
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

# Add the first column (e.g., 'project_name') to the mapping
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


    
with app.app_context():

    df = pd.read_csv(CSV_PATH, index_col=False)
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



print("✅ CSV data imported and cleaned successfully")