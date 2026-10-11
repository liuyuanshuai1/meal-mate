# MealMate

MealMate 是一个微信小程序 + FastAPI 后端的点餐 / 晚餐计划项目。仓库结构如下：

- `client/`：原生微信小程序前端。
- `server/backend/`：FastAPI API、SQLAlchemy 模型、Alembic 迁移、种子脚本和管理页面。
- `server/docker-compose.yml`：本地 PostgreSQL / API / Nginx 开发编排。

本仓库是 MealMate 前端与后端的唯一代码源。前后端功能、部署配置和文档统一在这里维护；历史拆分仓库仅供参考，不再双向同步。

后端 Python 依赖以 `server/pyproject.toml` 和 `server/uv.lock` 为准，使用 `uv` 安装和执行；`requirements*.txt` 仅为兼容用途。

## 配置说明

本仓库按公开 GitHub 仓库标准整理，真实运行配置不会提交。首次运行前，请基于模板文件创建本地配置：

```bash
cp client/config.example.js client/config.js
cp client/project.config.example.json client/project.config.json
cp server/backend/.env.example server/backend/.env
cp server/docker-compose.server.example.yml server/docker-compose.server.yml
```

请不要提交复制出来的真实配置文件。这些文件可能包含 API 域名、微信小程序 AppID、数据库连接、服务器路径或部署密钥。

## 小程序前端

创建 `client/config.js` 和 `client/project.config.json` 后，用微信开发者工具打开 `client/` 目录。

重要配置项：

- `apiBaseUrl`：后端 API 地址。本地开发通常是 `http://127.0.0.1:8000/api`。
- `appid`：在复制出来的 `project.config.json` 中填写自己的微信小程序 AppID。

小程序使用 `wx.login` 自动登录。请在 `server/backend/.env` 配置同一个小程序的 `WECHAT_APP_ID`、
`WECHAT_APP_SECRET`、随机生成的 `TOKEN_SECRET` 和独立的 `ADMIN_TOKEN`。管理页面使用用户名 `admin`、密码
`ADMIN_TOKEN`；管理写接口需要发送 `X-Admin-Token`。真机体验时，`apiBaseUrl` 需要使用 HTTPS，并加入微信
小程序“request 合法域名”。

## 后端服务

进入 `server` 目录启动本地数据库：

```bash
cd server
uv sync --frozen
docker compose up -d db
```

进入 `server/backend` 执行数据库迁移和初始化数据：

```bash
cd server/backend
uv run --project .. alembic upgrade head
uv run --project .. python scripts/seed.py
```

启动 API：

```bash
uv run --project .. uvicorn app.main:app --reload
```

健康检查：

```bash
curl http://localhost:8000/api/health
```

本地只调试界面且不调用微信登录服务时，可在后端 `.env` 设置 `WECHAT_MOCK_LOGIN=true`；该选项不能用于生产。

## 质量检查

在 `server` 目录执行：

```bash
uv sync --frozen
uv run python -m pytest
uv run python -m mypy backend
uv run python -m ruff check backend tests
```

在 `client` 目录执行：

```bash
node --test tests/*.test.js
```

## 部署说明

真实部署文件请保留在本地或服务器，不要提交到 Git：

- `server/backend/.env`
- `server/docker-compose.server.yml`
- `server/static/` 和 `server/backend/static/uploads/` 下的上传文件

`server/docker-compose.server.example.yml` 只用于说明部署文件结构，不包含真实凭据。
