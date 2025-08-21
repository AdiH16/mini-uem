# mini-uem

A tiny **Unified Endpoint Management** (UEM-like) backend built with **Django + DRF**. It demonstrates devices, policies, owners, JWT auth, and a couple of realistic device actions (assign a policy, device check-in).

## Stack

- Python 3.12
- Django 5.2.5
- Django REST framework 3.16.1
- SimpleJWT 5.5.1 (JWT auth)
- django-filter (filters/search/ordering)
- PostgreSQL 17 (Dockerized)

## Features

- CRUD for **Owners**, **Devices**, **Policies**
- **Many-to-many**: Device ↔ Policy via **DevicePolicy** (tracks status/timestamps)
- Custom actions:
  - `POST /api/devices/{id}/assign_policy/`
  - `POST /api/devices/{id}/check_in/`
- JWT auth (access/refresh), pagination, CORS for local frontends
- Dockerized **db + web**; one-command run

---

## Quickstart

### Option A — Run everything with Docker Compose (recommended)

```bash
# fresh build
docker compose down -v
docker compose up --build
```

- API: http://localhost:8000/api/health/
- DB is internal at `db:5432` (compose network). On the host it’s also published at **localhost:55432**.

### Option B — Local Django, Docker Postgres (Windows/macOS/Linux)

1. Create and activate venv; install requirements.
2. Start Postgres only:

```bash
docker compose up -d db
```

3. `.env` at repo root (example below). On Windows we use host port **55432**.
4. Run migrations & server:

```bash
python manage.py migrate
python manage.py runserver
```

---

## Environment

Create `.env` in repo root (not committed).

```dotenv
DJANGO_SECRET_KEY=change_me_in_prod
DB_NAME=mini_uem
DB_USER=mini_uem_user
DB_PASSWORD=mini_uem_pass
DB_HOST=localhost          # overridden to 'db' inside Docker web service
DB_PORT=55432              # overridden to '5432' inside Docker web service
```

> Compose overrides `DB_HOST=db` and `DB_PORT=5432` for the `web` container so containers talk internally while your host still uses 55432.

`.env.example` is included as a template.

---

## Database & Migrations

- The compose file defines Postgres 17 with a named volume `db_data`.
- The web container waits for DB, runs migrations automatically, then starts.
- Manually:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

## Auth (JWT)

Default DRF settings require authentication for all endpoints except `/api/health/` and `check_in`.

Token endpoints (SimpleJWT):

- `POST /api/auth/token/` → `{ "access", "refresh" }`
- `POST /api/auth/token/refresh/` → `{ "access" }`

Example (PowerShell):

```powershell
# obtain tokens
curl -Method POST http://localhost:8000/api/auth/token/ `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"username":"admin","password":"yourpass"}'

# use access token
$TOKEN = "<paste access>"
curl -Method GET http://localhost:8000/api/devices/ -Headers @{"Authorization"="Bearer $TOKEN"}

# refresh
curl -Method POST http://localhost:8000/api/auth/token/refresh/ `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"refresh":"<paste refresh>"}'
```

---

## API Endpoints (summary)

- Health: `GET /api/health/`
- Auth:
  - `POST /api/auth/token/`
  - `POST /api/auth/token/refresh/`
- Owners:
  - `GET/POST /api/owners/`
  - `GET/PATCH/DELETE /api/owners/{id}/`
- Devices:
  - `GET/POST /api/devices/`
  - `GET/PATCH/DELETE /api/devices/{id}/`
  - `POST /api/devices/{id}/assign_policy/` (body: `{ "policy_id": <int> }`)
  - `POST /api/devices/{id}/check_in/`
- Policies:
  - `GET/POST /api/policies/`
  - `GET/PATCH/DELETE /api/policies/{id}/`

### Filtering / Search / Ordering

Common query params:

- `?search=pixel` (devices: name, owner name/email)
- `?owner=1&os_type=android&status=active`
- `?ordering=-last_check_in` (prefix `-` for desc)

Examples:

```bash
# Android devices owned by 1, newest check-ins first
curl "http://localhost:8000/api/devices/?owner=1&os_type=android&ordering=-last_check_in" -H "Authorization: Bearer $TOKEN"

# Search by name/email
curl "http://localhost:8000/api/devices/?search=pixel" -H "Authorization: Bearer $TOKEN"

# Policies of type WiFi
curl "http://localhost:8000/api/policies/?type=wifi&ordering=name" -H "Authorization: Bearer $TOKEN"
```

### Sample create calls

```bash
# Owner
curl -X POST http://localhost:8000/api/owners/ \
  -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Alice","email":"alice@example.com"}'

# Device (owned by Alice id=1)
curl -X POST http://localhost:8000/api/devices/ \
  -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" \
  -d '{"device_name":"Pixel-7","os_type":"android","owner_id":1}'

# Policy
curl -X POST http://localhost:8000/api/policies/ \
  -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Corp WiFi","type":"wifi","payload":{"ssid":"CorpNet","psk":"s3cret"}}'

# Assign policy to device id=1
curl -X POST http://localhost:8000/api/devices/1/assign_policy/ \
  -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" \
  -d '{"policy_id":1}'

# Check-in device
curl -X POST http://localhost:8000/api/devices/1/check_in/
```

---

## CORS (dev)

Enabled for common local origins (`http://localhost:3000`, `http://localhost:5173`). Adjust `CORS_ALLOWED_ORIGINS` in `settings.py` if you add a frontend on a different port.

---

## Docker Details

### Files

- `Dockerfile` – Python 3.12 slim, installs deps, starts via `entrypoint.sh`
- `entrypoint.sh` – waits for DB, runs migrations, starts server
- `docker-compose.yml` – `db` (Postgres 17) + `web` (Django)

### Ports

- API: `localhost:8000`
- DB (host): `localhost:55432` → container `5432`

### Windows note

Ensure `entrypoint.sh` uses **LF** line endings. If you see `exec format error`, convert line endings to LF.

---

## Troubleshooting

- **Auth fails/401**: make sure you pass `Authorization: Bearer <access>`; refresh when expired.
- **DB password errors**: if you changed credentials, run `docker compose down -v && docker compose up -d` to recreate the volume.
- **Port 5432 conflicts**: we map host 55432 → container 5432 to avoid local Postgres clashes.

---

## License

MIT.
