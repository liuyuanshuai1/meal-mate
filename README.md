# MealMate

MealMate is a WeChat Mini Program plus FastAPI backend for a small meal-ordering/dinner-planning app. The repository is split into:

- `client/`: native WeChat Mini Program frontend.
- `server/backend/`: FastAPI API, SQLAlchemy models, Alembic migrations, seed script, and admin pages.
- `server/docker-compose.yml`: local PostgreSQL/API/Nginx composition.

## Configuration

This repository is prepared for a public GitHub upload. Real runtime configuration is intentionally ignored. Use the example files as templates:

```bash
cp client/config.example.js client/config.js
cp client/project.config.example.json client/project.config.json
cp server/backend/.env.example server/backend/.env
cp server/docker-compose.server.example.yml server/docker-compose.server.yml
```

Do not commit the copied files. They may contain API domains, WeChat app IDs, database URLs, server paths, or deployment secrets.

## Frontend

Open `client/` with WeChat Developer Tools after creating `client/config.js` and `client/project.config.json`.

Important frontend config:

- `apiBaseUrl`: backend API base URL, for example `http://127.0.0.1:8000/api` in local development.
- `fixedUserId` and `fixedPerson`: current development placeholders used by the app.
- `appid`: fill your own WeChat Mini Program app ID in the copied `project.config.json`.

## Backend

Start the local database from the `server` directory:

```bash
cd server
docker compose up -d db
```

Run migrations and seed data from `server/backend`:

```bash
cd server/backend
alembic upgrade head
python scripts/seed.py
```

Start the API:

```bash
uv run uvicorn app.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/api/health
```

## Quality Checks

From the `server` directory:

```bash
uv run python -m pytest
uv run python -m mypy backend
uv run python -m ruff check backend tests
```

## Deployment Notes

Keep real deployment files outside Git:

- `server/backend/.env`
- `server/docker-compose.server.yml`
- uploaded images under `server/static/` and `server/backend/static/uploads/`

`server/docker-compose.server.example.yml` documents the expected deployment shape without exposing credentials.
