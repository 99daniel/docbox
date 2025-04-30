# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app

# 1) System-Dependencies inkl. dos2unix für Zeilenendungen
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      tesseract-ocr \
      libtesseract-dev \
      dos2unix && \
    rm -rf /var/lib/apt/lists/*

# 2) Python-Dependencies installieren
#    (wenn dein requirements.txt in backend/ liegt)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 3) Entrypoint-Skript kopieren, in Unix-Format bringen und ausführbar machen
COPY entrypoint.sh /app/entrypoint.sh
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# 4) Restlichen Code kopieren
COPY . /app

# 5) Entrypoint setzt .env falls nötig und startet FastAPI
ENTRYPOINT ["./entrypoint.sh"]
