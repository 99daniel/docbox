# worker/Dockerfile
FROM python:3.11-alpine

WORKDIR /worker

# System-Pakete für Tesseract + deutsche Sprachdaten + Build-Tools
RUN apk add --no-cache \
      tesseract-ocr \
      tesseract-ocr-data-deu \
      build-base \
      python3-dev \
      jpeg-dev \
      zlib-dev \
      libffi-dev

# Tesseract-Datenpfad
ENV TESSDATA_PREFIX=/usr/share/tessdata

# Python-Dependencies
COPY worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code kopieren
COPY backend ./backend
COPY worker/tasks.py .

# Worker starten
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
