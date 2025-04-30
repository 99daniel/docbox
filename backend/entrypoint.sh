#!/usr/bin/env sh
set -e

# lade .env nur, wenn sie existiert
if [ -f "/app/.env" ]; then
  . /app/.env
fi

# Starte dann Uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000
