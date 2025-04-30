# backend/schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        # Pydantic V2: 'from_attributes' statt 'orm_mode'
        from_attributes = True

class DocumentOut(BaseModel):
    id: int
    filename: str
    upload_ts: datetime
    ocr_status: str
    ocr_text_path: Optional[str] = None

    class Config:
        from_attributes = True

# Neu: Status-Response
class DocumentStatus(BaseModel):
    id: int
    ocr_status: str

    class Config:
        from_attributes = True

# Neu: OCR-Text-Response
class DocumentResult(BaseModel):
    id: int
    filename: str
    text: str

    class Config:
        from_attributes = True
