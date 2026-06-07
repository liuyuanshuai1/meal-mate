# backend-foundation

目标：搭建后端最小可运行骨架，提供统一配置、数据库会话、统一响应和健康检查能力。

## 最小任务

- [ ] 创建 `backend/` 基础目录结构：`app/main.py`、`app/core/`、`app/routers/`、`app/models/`、`app/schemas/`、`app/services/`
- [ ] 编写 `backend/requirements.txt`，包含 `fastapi`、`uvicorn[standard]`、`sqlalchemy`、`psycopg[binary]`、`alembic`、`pydantic-settings`、`python-multipart`
- [ ] 实现 `app/core/config.py`，读取 `APP_NAME`、`APP_ENV`、`DEBUG`、`DATABASE_URL`、`UPLOAD_DIR`、`PUBLIC_STATIC_URL`、`TZ`
- [ ] 实现 `app/core/database.py`，提供 SQLAlchemy 2.x `engine`、`SessionLocal`、`Base`、`get_db`
- [ ] 实现 `app/core/response.py`，统一输出 `{ code, data, message }`
- [ ] 在 `app/main.py` 创建 FastAPI 应用，统一注册 `/api` 路由前缀
- [ ] 增加 `GET /api/health`，返回 `code=0` 和应用基础状态
- [ ] 增加全局异常处理，未知异常返回 `code=50000`，不暴露堆栈
- [ ] 本地运行 `uvicorn app.main:app --reload` 验证服务可启动

## 验收

- [ ] `GET /api/health` 返回统一响应格式
- [ ] 缺少可选环境变量时能使用开发默认值
- [ ] 数据库会话依赖可被后续路由复用
