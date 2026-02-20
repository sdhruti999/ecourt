from sqlalchemy import Column, String, Date, DateTime
from database import Base

class Case(Base):
    __tablename__ = "cases"

    id = Column(String, primary_key=True, index=True)
    update_time = Column(DateTime)

    court_name = Column(String)
    case_type = Column(String)
    filing_date = Column(Date)
    registration_date = Column(Date)
    first_hearing_date = Column(Date)
    decision_date = Column(Date)

    case_status = Column(String)
    nature_of_disposal = Column(String)

    case_number = Column(String)
    case_year = Column(String)

    police_station = Column(String)
    fir_number = Column(String)
    fir_year = Column(String)

    court_code = Column(String)
    state_code = Column(String)
    dist_code = Column(String)
    court_complex_code = Column(String)

    case_no = Column(String)
    cino = Column(String)

    search_flag = Column(String)
    search_by = Column(String)
    ajax_req = Column(String)
    app_token = Column(String)

    status = Column(String)
