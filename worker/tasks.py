# worker/tasks.py

import os
from celery import Celery
from PIL import Image
import pytesseract

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Models aus deinem Backend
from backend.models import Base, Document

# ENV-Variablen
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./docbox.db")
BROKER_URL   = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")

# Celery-Instanz
app = Celery("worker", broker=BROKER_URL)

# DB-Setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

@app.task
def ocr_file(filename: str):
    storage = "/worker/storage"
    img_path = os.path.join(storage, filename)
    txt_name = f"{filename}.txt"
    txt_path = os.path.join(storage, txt_name)

    # OCR auf Deutsch
    text = pytesseract.image_to_string(Image.open(img_path), lang="deu")

    # Textdatei speichern
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    # DB-Eintrag updaten
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.filename == filename).first()
        if doc:
            doc.ocr_status = "done"
            doc.ocr_text_path = txt_name
            db.commit()
    finally:
        db.close()

    return {"file": filename, "chars": len(text)}
