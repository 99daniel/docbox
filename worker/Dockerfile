# worker/Dockerfile
FROM python:3.11-alpine

WORKDIR /worker

# Tesseract und Build-Tools via apk (kein apt-get mehr)
RUN apk add --no-cache \
      tesseract-ocr \
      build-base \
      libffi-dev \
      rust

# Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pytesseract

# Code kopieren
COPY . .

# Celery-Worker starten
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
