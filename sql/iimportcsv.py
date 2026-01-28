# Enum allowed values
ENUM_VALUES = {
    "designate": [
        "Asha", "B.Ondero", "B. Odero", "Compliance", "D.O.S", "Eileen", "Eric Njoroge", "Esther", "Eznner", "Finance",
        "Finance - Allan", "Finance - Muktar", "Finance - Njane", "Habiba", "Investigations", "Judy", "Kamande", "Legal",
        "Legal - Vitalis", "L.O - Cate", "L.O. - Cate", "L.O. - Juliet", "L.O. - Lynn", "L.O. - Mercy", "L.O. - Michelle",
        "Naomi", "N. Sankale", "Rukia", "S.Monyoncho", "Sarah", "SDOR", "Sankale", "Topisia"
    ],
    "filed_by_registry_action": ["Filed", "Not Filed"],
    "received_by_designate": ["Received", "Not Received"],
    "correction_sent": ["Correction Sent", "No Correction Sent"],
    "correction_status": ["Correction Done", "Correction Not Done", "Not Required"],
    "status": ["Completed", "Incomplete"],
    "authorization": ["Authorized", "Unauthorized", "Authorised"],  # Accept both spellings
    "signatory": ["Monyoncho", "I.Sang"],
    "dispatch": ["Dispatched", "Not Dispatched"]
}

# Default fallback values
MISSING_VALUES = {
    "organization_name": "Unknown",
    "service_requested": "Unknown",
    "remarks": "Unknown",
    "date_received": None,
    "designate": "Asha",
    "filed_by_registry_action": "Not Filed",
    "received_by_designate": "Not Received",
    "date_received_by_designate": None,
    "correction_sent": "No Correction Sent",
    "correction_status": "Correction Not Done",
    "date_corrections_done": None,
    "date_correction_required": None,
    "status": "Incomplete",
    "date_completed": None,
    "authorization": "Unauthorized",
    "date_authorised": None,
    "signatory": "Unknown",
    "dispatch": "Not Dispatched",
    "date_dispatched": None
}


# Normalize known variants
ENUM_NORMALIZE = {
    "authorization": {"Authorised": "Authorized"},
}

def clean_value(field, value):
    # Empty / NaN → default
    if pd.isna(value) or value == "":
        if field == "organization_name":
            return None
        return MISSING_VALUES[field]

    val = str(value).strip()

    

    # Normalize known variants
    if field in ENUM_NORMALIZE and val in ENUM_NORMALIZE[field]:
        val = ENUM_NORMALIZE[field][val]

    # Enforce ENUM values
    if field in ENUM_VALUES:
        if val in ENUM_VALUES[field]:
            return val
        else:
            print(f"[WARN] Invalid value '{value}' for {field}, using default '{MISSING_VALUES[field]}'")
            return MISSING_VALUES[field]

    # Parse dates
    if "date" in field:
        return parse_date(val)

    # Strings → truncate
    if isinstance(val, str) and len(val) > 255:
        return val[:255]

    return val



from iso8601 import parse_date
import pandas as pd
from datetime import datetime, date
from app import app
from models import db, FileTracking

CSV_PATH = "/home/harold/Desktop/dailytracking/DAILY TRACKING - FINAL  - Requests.csv"

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
    df = pd.read_csv(CSV_PATH)
    df.rename(columns=COLUMN_MAPPING, inplace=True)
    df = df[list(COLUMN_MAPPING.values())]

    for _, row in df.iterrows():
        cleaned = {field: clean_value(field, row[field]) for field in COLUMN_MAPPING.values()}
        record = FileTracking(**cleaned)
        db.session.add(record)

    db.session.commit()



print("✅ CSV data imported and cleaned successfully")