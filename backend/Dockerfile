# backend/Dockerfile
FROM python:3.11-slim

# Arbeitsverzeichnis
WORKDIR /app

# 1) Python-Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Entrypoint-Script kopieren, Zeilenenden bereinigen & ausführbar machen
COPY entrypoint.sh /app/entrypoint.sh
RUN apt-get update && \
    apt-get install -y --no-install-recommends dos2unix && \
    dos2unix /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh && \
    rm -rf /var/lib/apt/lists/*

# 3) Restlichen Code kopieren
COPY . .

# 4) Entrypoint ausführen
ENTRYPOINT ["/app/entrypoint.sh"]
