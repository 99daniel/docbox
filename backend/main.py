# backend/main.py


from dotenv import load_dotenv
load_dotenv()   

from fastapi import (
    FastAPI, Depends, HTTPException, status,
    UploadFile, File
)
from fastapi.security import (
    OAuth2PasswordBearer, OAuth2PasswordRequestForm
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import timedelta
from typing import List
from pathlib import Path
import os
from fastapi.staticfiles import StaticFiles

import database, models, schemas, auth
from celery import Celery

# FastAPI-Instanz
app = FastAPI()
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# CORS konfigurieren – erlaubt deinen Frontend-Dev-Server
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # oder ["*"] wenn alle erlaubt sein sollen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password-Hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 Scheme für Login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Celery-Client für OCR-Tasks
CELERY_BROKER = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
celery_app = Celery("backend", broker=CELERY_BROKER)

# Storage-Verzeichnis (gemountet auf /app/storage im Container)
STORAGE_DIR = Path("storage")
STORAGE_DIR.mkdir(exist_ok=True)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/auth/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = pwd_context.hash(user_in.password)
    new_user = models.User(username=user_in.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/auth/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültige Zugangsdaten",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db)
):
    try:
        payload = auth.verify_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ungültig oder abgelaufen",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User nicht gefunden")
    return user


@app.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.get("/documents", response_model=List[schemas.DocumentOut])
def list_documents(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    docs = (
        db.query(models.Document)
          .filter(models.Document.owner_id == current_user.id)
          .all()
    )
    return docs


@app.post("/documents/upload", response_model=schemas.DocumentOut, status_code=201)
def upload_document(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    dest = STORAGE_DIR / file.filename
    with dest.open("wb") as buf:
        buf.write(file.file.read())

    doc = models.Document(
        filename=file.filename,
        owner_id=current_user.id,
        ocr_status="processing",
        ocr_text_path=None
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    celery_app.send_task("tasks.ocr_file", args=[file.filename])
    return doc


@app.get("/documents/{doc_id}/status", response_model=schemas.DocumentStatus)
def get_document_status(
    doc_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    doc = (
        db.query(models.Document)
          .filter(
              models.Document.id == doc_id,
              models.Document.owner_id == current_user.id
          )
          .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden")

    txt_path = STORAGE_DIR / f"{doc.filename}.txt"
    if txt_path.exists() and doc.ocr_status != "done":
        doc.ocr_status = "done"
        doc.ocr_text_path = str(txt_path)
        db.commit()
        db.refresh(doc)

    return {"id": doc.id, "ocr_status": doc.ocr_status}


@app.get("/documents/{doc_id}/result", response_model=schemas.DocumentResult)
def get_document_result(
    doc_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    doc = (
        db.query(models.Document)
          .filter(
              models.Document.id == doc_id,
              models.Document.owner_id == current_user.id
          )
          .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden")

    txt_path = STORAGE_DIR / f"{doc.filename}.txt"
    if not txt_path.exists():
        raise HTTPException(
            status_code=404,
            detail="OCR-Ergebnis noch nicht verfügbar"
        )

    text = txt_path.read_text(encoding="utf-8")
    return {"id": doc.id, "filename": doc.filename, "text": text}
