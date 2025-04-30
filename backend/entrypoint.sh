#!/usr/bin/env sh
set -e

# Falls es eine .env gibt, lade alle KEY=VALUE paarweise
if [ -f "/app/.env" ]; then
  export $(grep -v '^#' /app/.env | xargs)
fi

# Starte FastAPI
exec uvicorn main:app --host 0.0.0.0 --port 8000
