# backend/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Nur Python-Pakete installieren (kein Tesseract mehr hier)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Restlichen Code kopieren
COPY . .

# FastAPI starten
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
