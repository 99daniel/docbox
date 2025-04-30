# backend/auth.py

import os
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import jwt

# .env laden
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Erzeugt ein JWT mit Daten (z.B. {'sub':user_id}) und Ablaufdatum.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    """
    Verifiziert und dekodiert ein JWT. Wirft bei ungültigem/abgelaufenem Token.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
