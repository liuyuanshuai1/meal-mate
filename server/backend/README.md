# MealMate Backend

## Configuration

Create a local environment file before running the API:

```bash
cp .env.example .env
```

The default development database URL in `.env.example` is:

```bash
postgresql+asyncpg://postgres:postgres@localhost:15432/meal_mate
```

## Local Database

Start PostgreSQL from the `server` directory:

```bash
docker compose up -d db
```

Run migrations and seed data from `server/backend`:

```bash
alembic upgrade head
python scripts/seed.py
```

Start API:

```bash
uv run uvicorn app.main:app --reload
```

Local uploaded images are served from:

```bash
backend/static/uploads
```

Use `/static/uploads/<filename>` as the public URL stored in food or banner data.

Health check:

```bash
curl http://localhost:8000/api/health
```

Quality checks from the `server` directory:

```bash
uv run python -m pytest
uv run python -m mypy backend
uv run python -m ruff check backend tests
```

With Nginx:

```bash
docker compose up --build
curl http://localhost:8080/api/health
```

For server deployment, copy `../docker-compose.server.example.yml` to `../docker-compose.server.yml` and keep the real file uncommitted.
