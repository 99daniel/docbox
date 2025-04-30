# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 1) System‐ und Python‐Dependencies installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Quellcode (inkl. .env) ins Image kopieren
COPY . .

# 3) Uvicorn direkt starten – kein entrypoint.sh mehr nötig
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
