#!/bin/sh
#
# entrypoint.sh – wird nur beim allerersten Start .env anlegen

ENV_FILE=/app/.env

if [ ! -f "$ENV_FILE" ]; then
  echo "Creating initial .env…" >&2
  SECRET_KEY=$(python3 - << 'PYCODE'
import secrets; print(secrets.token_urlsafe(32))
PYCODE
  )
  cat <<EOF > "$ENV_FILE"
SECRET_KEY=$SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES=60
CELERY_BROKER_URL=redis://redis:6379/0
EOF
fi

# Starte dann Uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000
