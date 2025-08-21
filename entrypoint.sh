#!/usr/bin/env sh
set -e

# Wait for Postgres to accept connections
python <<'PY'
import os, time
import psycopg
host=os.getenv("DB_HOST","localhost")
port=int(os.getenv("DB_PORT","5432"))
name=os.getenv("DB_NAME")
user=os.getenv("DB_USER")
password=os.getenv("DB_PASSWORD")
for i in range(60):
    try:
        with psycopg.connect(host=host, port=port, dbname=name, user=user, password=password, connect_timeout=3):
            print("Database is ready.")
            break
    except Exception as e:
        print(f"Waiting for DB... ({e})")
        time.sleep(1)
else:
    raise SystemExit("DB not ready after 60s")
PY

# DB migrations 
python manage.py migrate --noinput

# Start app 
python manage.py runserver 0.0.0.0:8000
