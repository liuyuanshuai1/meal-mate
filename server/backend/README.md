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
uv run --project .. python -m scripts.seed
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

# 智能推荐与菜谱

首页推荐调用服务端 `/api/recommendations`。直接运行后端或使用 `docker-compose.server.yml` 时，在 `backend/.env` 配置 `DEEPSEEK_API_KEY`；使用 `server/docker-compose.yml` 时，在 `server/.env` 配置。可用 `DEEPSEEK_MODEL` 指定模型（默认 `deepseek-flash`）。密钥只保留在服务端。

### 饭搭子下单提醒

应用内提醒无需配置：对方下单后，双方首页显示菜单，收件人看到未读提示。微信订阅消息需要先在微信公众平台的小程序「订阅消息」中选用或申请一个**一次性**下单提醒模板，再在服务端环境变量中配置：

```dotenv
WECHAT_DINNER_PLAN_TEMPLATE_ID=实际模板ID
WECHAT_DINNER_PLAN_TEMPLATE_FIELDS={"thing1":"creator","thing2":"summary","time3":"meal_time"}
```

字段名必须使用模板详情中的实际字段名。右侧只能选 `creator`（“某某下单了”）、`summary`（菜品份数和道数）、`meal_time`（就餐时间）；时间需映射到 `time` 或 `date` 字段。配置后重启后端，饭搭子页面才会出现「订阅下次下单提醒」按钮。每位收件人需要自行点击授权；一次性订阅通常只覆盖下一条提醒，用完需再次订阅。微信发送失败不影响下单或应用内提醒。

推荐仅从已上架且做法已发布的菜品中选取；已有菜品需要在 `/admin/foods` 补齐食材、用时、步骤并发布做法。后台的“AI 生成草稿”只生成待人工审核的内容，不会自动发布。迁移后原有菜品默认处于做法草稿状态，发布前不会进入智能推荐。

首页“探索新做法”调用 `POST /api/recipes/explore`，根据用户描述生成最多三份临时菜谱，展示食材、缺少的材料和步骤。探索结果不会写入菜单，也不能直接加入点餐或今晚菜单。接口需要用户登录，默认每位用户每天最多调用 20 次；可通过 `AI_EXPLORE_DAILY_LIMIT` 调整。新增的 `ai_explore_usage` 表需先运行 Alembic 迁移。

已发布的做法会显示在菜品详情页。提交今晚菜单时，系统把做法复制到每个菜单项，两位饭搭子都可以在共享菜单中展开查看；后续编辑或下架菜品不会改变已提交菜单中的做法。迁移会为已有菜单项补齐当前已发布的做法。
