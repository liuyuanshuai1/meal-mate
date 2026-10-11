# MealMate Backend

## Configuration

Create a local environment file before running the API:

```bash
cp .env.example .env
```

Set `WECHAT_APP_ID`, `WECHAT_APP_SECRET`, a long random `TOKEN_SECRET`, and a separate long random `ADMIN_TOKEN` in
`.env`. Requests that create, update, delete, or upload catalog content must send `X-Admin-Token`. The `/admin`
browser interface uses HTTP Basic authentication with username `admin` and `ADMIN_TOKEN` as its password. If
`ADMIN_TOKEN` is empty, both management paths are disabled. `WECHAT_MOCK_LOGIN=true` is available only for local UI
development and must stay disabled in production.

Install the locked backend and development dependencies from the `server` directory:

```bash
uv sync --frozen
```

`server/pyproject.toml` and `server/uv.lock` are the source of truth for Python dependencies. The requirements files are retained for compatibility only.

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
uv run --project .. alembic upgrade head
uv run --project .. python scripts/seed.py
```

Start API:

```bash
uv run --project .. uvicorn app.main:app --reload
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
