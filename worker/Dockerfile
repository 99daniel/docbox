# worker/Dockerfile

FROM python:3.11-slim
WORKDIR /worker

# 1) System-Abhängigkeiten: Tesseract OCR
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      tesseract-ocr libtesseract-dev && \
    rm -rf /var/lib/apt/lists/*

# 2) Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Task-Code kopieren
COPY tasks.py .

# 4) Celery-Worker starten
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
