# backend/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends
from models import Base

DATABASE_URL = "sqlite:///./storage/docbox.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Erzeugt Tabellenschema, falls nicht vorhanden
Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """
    FastAPI-Dependency: liefert eine DB-Session und schließt sie danach.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
