#!/usr/bin/env sh
set -e

# Optional: .env laden
if [ -f "/app/.env" ]; then
  export $(grep -v '^#' /app/.env | xargs)
fi

# FastAPI starten
exec uvicorn main:app --host 0.0.0.0 --port 8000
