from fastapi import FastAPI
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Case

app = FastAPI(title="eCourts API", version="1.0")


# Dependency: DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# API: Get ALL cases
# =========================
@app.get("/cases")
def get_all_cases(limit: int = 100, offset: int = 0):
    db: Session = next(get_db())

    cases = (
        db.query(Case)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": c.id,
            "update_time": c.update_time,
            "court_name": c.court_name,
            "case_type": c.case_type,
            "filing_date": c.filing_date,
            "registration_date": c.registration_date,
            "first_hearing_date": c.first_hearing_date,
            "decision_date": c.decision_date,
            "case_status": c.case_status,
            "nature_of_disposal": c.nature_of_disposal,
            "case_number": c.case_number,
            "case_year": c.case_year,
            "police_station": c.police_station,
            "fir_number": c.fir_number,
            "fir_year": c.fir_year,
            "court_code": c.court_code,
            "state_code": c.state_code,
            "dist_code": c.dist_code,
            "court_complex_code": c.court_complex_code,
            "case_no": c.case_no,
            "cino": c.cino,
            "search_flag": c.search_flag,
            "search_by": c.search_by,
            "ajax_req": c.ajax_req,
            "app_token": c.app_token,
            "status": c.status,
        }
        for c in cases
    ]


# =========================
# API: Health check
# =========================
@app.get("/")
def root():
    return {"status": "API running successfully"}
