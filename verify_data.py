from database import SessionLocal
from models import Case

db = SessionLocal()
print("Total cases:", db.query(Case).count())

sample = db.query(Case).first()
print(sample.court_name, sample.cino)

db.close()
