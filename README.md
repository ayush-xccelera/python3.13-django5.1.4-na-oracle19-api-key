# Notes API (Django + DRF + Oracle)

A minimal notes-taking backend. Clients authenticate with an API key
(`X-API-Key` header) and can create/read/update/archive/restore/delete
their own notes only.

## Overview

- **Entities**: `Note` (title, content, status ACTIVE/ARCHIVED, owner, timestamps),
  `ApiKey` (the client identity: hashed key, name, active flag).
- **Auth**: custom DRF `BaseAuthentication` reads `X-API-Key`, hashes it with
  SHA-256, and looks it up in the `ApiKey` table. Only active keys authenticate.
- **Admin auth**: API key management (`/api/v1/api-keys/`) is gated by a
  separate `X-Admin-Key` header checked against `ADMIN_API_KEY` — never usable
  as a client API key.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py seed     # optional sample data
```

## Environment variables

File: `.env_200ce3de-79bd-42d3-93b2-2d3d8d0c7eb9`

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True`/`False` |
| `DB_ENGINE` | `django.db.backends.oracle` |
| `DB_NAME` | Oracle DSN/service (blank = built from HOST:PORT/SERVICE_NAME) |
| `DB_USER` / `DB_PASSWORD` | Oracle credentials |
| `DB_HOST` / `DB_PORT` / `DB_SERVICE_NAME` | Oracle connection pieces |
| `ADMIN_API_KEY` | Admin key for `/api-keys` management |

> Note: if the configured Oracle instance is unreachable/unauthenticated at
> process start, `settings.py` automatically falls back to a local SQLite
> database (`db.sqlite3`) so the project stays runnable. Set `FORCE_ORACLE=True`
> to disable this fallback.

## Run

```bash
chmod +x start.sh
PORT=28828 ./start.sh
```

## Endpoints (prefix `/api/v1`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api-keys/` | `X-Admin-Key` | Create a new API key (raw key returned once) |
| GET | `/api-keys/` | `X-Admin-Key` | List API keys |
| GET | `/api-keys/{id}/` | `X-Admin-Key` | Retrieve one API key |
| PUT | `/api-keys/{id}/` | `X-Admin-Key` | Edit name/is_active |
| DELETE | `/api-keys/{id}/` | `X-Admin-Key` | Revoke (deactivate) a key |
| POST | `/notes/` | `X-API-Key` | Create a note (status defaults ACTIVE) |
| GET | `/notes/` | `X-API-Key` | List the caller's ACTIVE notes (paginated) |
| GET | `/notes/{id}/` | `X-API-Key` | Retrieve one of the caller's notes |
| PUT | `/notes/{id}/` | `X-API-Key` | Update title/content (ownership fixed) |
| PATCH | `/notes/{id}/archive/` | `X-API-Key` | ACTIVE → ARCHIVED |
| PATCH | `/notes/{id}/restore/` | `X-API-Key` | ARCHIVED → ACTIVE |
| DELETE | `/notes/{id}/` | `X-API-Key` | Permanently delete |

Pagination: `?limit=20&offset=0` (offset-style, default limit 20, max 100).

## Tests

```bash
pytest -v
```

## Docker

Not included in this build (infra.dockerfile=false / docker_compose=false).

## Project tree

```
config/            settings, urls, wsgi/asgi
notes/             models, serializers, authentication, permissions, views, urls, pagination
notes/management/commands/seed.py   idempotent sample data
tests/              pytest-django test suite
start.sh / start.bat
requirements.txt
.env_200ce3de-79bd-42d3-93b2-2d3d8d0c7eb9
```
