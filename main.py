from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Case

app = FastAPI(title="eCourts API", version="1.0")


# =========================
# Database Dependency
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# API: Health Check
# =========================
@app.get("/")
def root():
    return {"status": "API running successfully"}


# =========================
# API: Get ALL cases
# =========================
@app.get("/cases")
def get_all_cases(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
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
# API: Search case by Case No or FIR No
# =========================
@app.get("/cases/search")
def search_case(
    case_no: str | None = Query(None, description="Case Number"),
    fir_number: str | None = Query(None, description="FIR Number"),
    db: Session = Depends(get_db),
):
    if not case_no and not fir_number:
        raise HTTPException(
            status_code=400,
            detail="Provide either case_no or fir_number"
        )

    query = db.query(Case)

    if case_no:
        query = query.filter(Case.case_no == case_no)

    if fir_number:
        query = query.filter(Case.fir_number == fir_number)

    cases = query.all()   # ✅ FETCH ALL MATCHES

    if not cases:
        raise HTTPException(status_code=404, detail="Case not found")

    return [
        {
            "id": case.id,
            "update_time": case.update_time,
            "court_name": case.court_name,
            "case_type": case.case_type,
            "filing_date": case.filing_date,
            "registration_date": case.registration_date,
            "first_hearing_date": case.first_hearing_date,
            "decision_date": case.decision_date,
            "case_status": case.case_status,
            "nature_of_disposal": case.nature_of_disposal,
            "case_number": case.case_number,
            "case_year": case.case_year,
            "police_station": case.police_station,
            "fir_number": case.fir_number,
            "fir_year": case.fir_year,
            "court_code": case.court_code,
            "state_code": case.state_code,
            "dist_code": case.dist_code,
            "court_complex_code": case.court_complex_code,
            "case_no": case.case_no,
            "cino": case.cino,
            "search_flag": case.search_flag,
            "search_by": case.search_by,
            "ajax_req": case.ajax_req,
            "app_token": case.app_token,
            "status": case.status,
        }
        for case in cases
    ]