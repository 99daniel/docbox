# backend/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role            = Column(String, default="user", nullable=False)
    documents       = relationship("Document", back_populates="owner")

class Document(Base):
    __tablename__ = "documents"
    id            = Column(Integer, primary_key=True, index=True)
    filename      = Column(String, index=True, nullable=False)
    owner_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    upload_ts     = Column(DateTime, default=datetime.datetime.utcnow)
    ocr_status    = Column(String, default="processing")
    ocr_text_path = Column(String, nullable=True)
    owner         = relationship("User", back_populates="documents")
