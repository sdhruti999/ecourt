import pandas as pd
import math
import re
from datetime import datetime
from database import SessionLocal
from models import Case

EXCEL_FILE = "ecourts_incremental_output.xlsx"

# ===================== HELPERS =====================

def parse_date(value):
    """Convert Excel/Pandas date values to Python datetime or None"""
    if value is None or value is pd.NaT:
        return None

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    if isinstance(value, datetime):
        return value

    if isinstance(value, float) and math.isnan(value):
        return None

    value = str(value).strip()
    if not value:
        return None

    # Remove ordinal suffixes (1st, 2nd, 3rd, 4th)
    value = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', value)

    for fmt in (
        "%d %B %Y",
        "%d %b %Y",
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None


def clean_value(value):
    """Ensure SQLite-safe values (no NaN / NaT)"""
    if value is None or value is pd.NaT:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        value = value.strip()
        return value if value else None

    return value


# ===================== LOAD EXCEL =====================

df = pd.read_excel(EXCEL_FILE)

# Exact column mapping (CONFIRMED)
COLUMN_MAPPING = {
    "_id": "id",
    "Update Time": "update_time",
    "Court Name": "court_name",
    "Case Type": "case_type",
    "Filing Date": "filing_date",
    "Registration Date": "registration_date",
    "First Hearing Date": "first_hearing_date",
    "Decision Date": "decision_date",
    "Case Status": "case_status",
    "Nature of Disposal": "nature_of_disposal",
    "Case Number": "case_number",
    "Case Year": "case_year",
    "Police Station": "police_station",
    "FIR Number": "fir_number",
    "FIR Year": "fir_year",
    "court_code": "court_code",
    "state_code": "state_code",
    "dist_code": "dist_code",
    "court_complex_code": "court_complex_code",
    "case_no": "case_no",
    "cino": "cino",
    "search_flag": "search_flag",
    "search_by": "search_by",
    "ajax_req": "ajax_req",
    "app_token": "app_token",
    "status": "status",
}

df = df.rename(columns=COLUMN_MAPPING)

# ===================== DATE CONVERSION =====================

date_columns = [
    "update_time",
    "filing_date",
    "registration_date",
    "first_hearing_date",
    "decision_date",
]

for col in date_columns:
    if col in df.columns:
        df[col] = df[col].apply(parse_date)

# 🔥 Force ALL NaN / NaT → None
df = df.astype(object).where(pd.notnull(df), None)

# ===================== INSERT INTO SQLITE =====================

session = SessionLocal()
inserted = 0

for _, row in df.iterrows():
    clean_row = {k: clean_value(v) for k, v in row.to_dict().items()}
    case = Case(**clean_row)
    session.merge(case)
    inserted += 1

session.commit()
session.close()

print(f"✅ {inserted} rows inserted successfully into SQLite")
