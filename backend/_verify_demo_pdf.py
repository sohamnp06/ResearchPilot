from app.database.database import SessionLocal
from app.database.models import Paper
import os

db = SessionLocal()
rows = db.query(Paper).filter(Paper.id.in_(["paper-transformer-demo", "paper-bert-demo"])).all()
print([(r.id, r.title, r.pdf_url, r.file_path) for r in rows])
print("LOCAL_PDF_EXISTS", os.path.exists(r"C:\Users\harsh\Archivum\ResearchPilot\frontend\public\pdfs\attention-is-all-you-need.pdf"))
db.close()
