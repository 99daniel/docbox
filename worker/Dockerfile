# worker/Dockerfile
FROM python:3.11-alpine

WORKDIR /worker

# 1) System-Pakete installieren (Tesseract + Sprachdaten + Build-Tools für Pillow)
RUN apk add --no-cache \
      tesseract-ocr \
      tesseract-ocr-data-eng \
      build-base \
      libffi-dev \
      python3-dev \
      jpeg-dev \
      zlib-dev

# 2) TESSDATA_PREFIX setzen, damit Tesseract seine .traineddata findet
ENV TESSDATA_PREFIX=/usr/share/tessdata

# 3) Python-Dependencies installieren (inkl. Pillow und Celery)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pytesseract

# 4) Deinen Code kopieren
COPY . .

# 5) Celery-Worker starten
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
