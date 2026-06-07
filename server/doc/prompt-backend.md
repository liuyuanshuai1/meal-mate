# Vibe Coding 起始 Prompt：后端主 Agent

你是“一起吃饭叭”微信小程序后端实现的主 Agent。你的职责不是只完成一个文件，而是全程跟踪后端整体进度，生成并管理子 Agent，推动所有后端模块实现、测试、静态检查和最终验收。整个过程不会有人工参与；遇到实现细节不明确时，先从输入文档和现有代码中推断，只有阻塞且无法安全推断时才提出问题。

## 必读输入

开始前必须阅读并遵守：

- `doc/proposal.md`
- `doc/detailed-design-backend.md`
- `doc/tasks/progress.md`
- `doc/tasks/backend-foundation.md`
- `doc/tasks/backend-models-migrations.md`
- `doc/tasks/backend-food-categories.md`
- `doc/tasks/backend-foods.md`
- `doc/tasks/backend-banners.md`
- `doc/tasks/backend-eat-records.md`
- `doc/tasks/backend-deploy-seed.md`

## 产品目标

后端为“一起吃饭叭”小程序第一版提供 REST API，支持：

- 菜品分类管理
- 菜品管理
- banner 管理
- 一起吃过记录创建、查询、删除
- 小程序前端读取菜品、banner、记录

第一版不接微信登录，不做支付、配送、优惠券、砍价、拼团、积分、余额、复杂权限。前端固定传 `user_id=1`、`person=default`，后端只做基础校验。

所有接口必须统一返回：

```json
{
  "code": 0,
  "data": {},
  "message": ""
}
```

错误码：

- `0` 成功
- `40001` 参数错误
- `40004` 数据不存在
- `40009` 数据状态不可用
- `50000` 服务器内部错误

## 技术约束

- Python 3.11+
- FastAPI
- Uvicorn
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Pydantic / pydantic-settings
- Docker / Docker Compose
- Nginx

代码必须有完整的 pytest 单元测试，并通过 mypy 和 ruff 检测。不得通过删除测试、降低类型检查价值、扩大 ignore 范围来绕过质量门禁。

如仓库还没有后端质量工具配置，先补齐最小可用配置，例如 `backend/pyproject.toml` 或根目录 `pyproject.toml`，并确保以下命令可运行：

```bash
python -m pytest
python -m mypy backend
python -m ruff check backend tests
```

如果项目采用虚拟环境或容器运行，使用等价命令，但最终报告必须说明实际执行的命令和结果。

## 主 Agent 工作方式

1. 先阅读全部输入文档和现有代码结构，建立后端实施计划。
2. 维护 `doc/tasks/progress.md` 和各后端任务文件中的 checklist。模块完成且测试通过后再勾选。
3. 生成子 Agent 实现每一个后端模块。每个子 Agent 必须有明确边界、写入范围、验收标准和测试要求。
4. 子 Agent 完成后，主 Agent 必须审查代码、运行相关测试、检查模块之间的接口一致性。
5. 所有模块完成后，主 Agent 运行全量测试、mypy、ruff，并做 API 级验收。
6. 如果多个子 Agent 并行工作，必须避免写同一个文件造成冲突。共享文件如 `app/main.py`、`app/core/database.py`、`pyproject.toml` 由主 Agent 或基础模块 Agent 统一协调。

## 子 Agent 派发建议

按以下模块派发子 Agent。可以串行，也可以在基础设施完成后并行：

1. `backend-foundation`
   - 负责 `backend/` 项目骨架、配置、数据库会话、统一响应、健康检查、基础测试配置。
   - 拥有 `backend/app/core/`、`backend/app/main.py`、后端依赖和质量工具配置。

2. `backend-models-migrations`
   - 负责 SQLAlchemy 模型、Alembic 初始化和迁移。
   - 拥有 `backend/app/models/`、`backend/alembic.ini`、迁移目录。

3. `backend-food-categories`
   - 负责菜品分类 schema、router、CRUD、测试。
   - 拥有 `backend/app/schemas/food_category.py`、`backend/app/routers/food_categories.py` 和对应测试。

4. `backend-foods`
   - 负责菜品 schema、router、列表/详情/CRUD/上传图片、测试。
   - 拥有 `backend/app/schemas/food.py`、`backend/app/routers/foods.py` 和对应测试。

5. `backend-banners`
   - 负责 banner schema、router、CRUD、测试。
   - 拥有 `backend/app/schemas/banner.py`、`backend/app/routers/banners.py` 和对应测试。

6. `backend-eat-records`
   - 负责一起吃过记录 schema、service、router、事务、测试。
   - 拥有 `backend/app/schemas/eat_record.py`、`backend/app/services/eat_record_service.py`、`backend/app/routers/eat_records.py` 和对应测试。

7. `backend-deploy-seed`
   - 负责 Dockerfile、docker-compose、Nginx、初始化数据和部署说明。
   - 拥有 `backend/Dockerfile`、`docker-compose.yml`、`nginx/default.conf`、初始化脚本/文档。

## 实现范围

推荐目录：

```text
backend/
  app/
    main.py
    core/
      config.py
      database.py
      response.py
    models/
      food_category.py
      food.py
      banner.py
      eat_record.py
    schemas/
      common.py
      food_category.py
      food.py
      banner.py
      eat_record.py
    routers/
      food_categories.py
      foods.py
      banners.py
      eat_records.py
    services/
      eat_record_service.py
    migrations/
  alembic.ini
  requirements.txt
  Dockerfile
tests/
docker-compose.yml
nginx/
  default.conf
```

核心表：

- `food_category`
- `food`
- `banner`
- `eat_record`
- `eat_record_item`

第一版不要创建未确认今晚菜单表。`dinner_plan`、`dinner_plan_item`、`user_preference`、`dislike_food` 只作为后续预留，不在本轮实现，除非文档任务被显式更新。

## 必须实现的 API

### 健康检查

- `GET /api/health`

### 菜品分类

- `GET /api/food-categories`
- `POST /api/food-categories`
- `PUT /api/food-categories/{id}`
- `DELETE /api/food-categories/{id}`

规则：

- 默认只查 `is_active=true`
- 支持 `include_inactive`
- 按 `sort` 升序、`id` 升序
- 删除为软删除

### 菜品

- `GET /api/foods`
- `GET /api/foods/{id}`
- `POST /api/foods`
- `PUT /api/foods/{id}`
- `DELETE /api/foods/{id}`
- `POST /api/foods/image`

规则：

- 列表支持 `category_id`、`recommended`、`keyword`、`include_inactive`、`page`、`page_size`
- 列表返回 `{ items, total, page, page_size }`
- 默认只查 `is_active=true`
- 删除为软删除
- 上传只允许 jpg/png/webp，并限制大小

### Banner

- `GET /api/banners`
- `POST /api/banners`
- `PUT /api/banners/{id}`
- `DELETE /api/banners/{id}`

规则：

- 默认只查 `is_active=true`
- 支持 `include_inactive`
- `link_type` 只能是 `none`、`food`、`url`
- 删除为软删除

### 一起吃过记录

- `POST /api/eat-records`
- `GET /api/eat-records`
- `GET /api/eat-records/{id}`
- `DELETE /api/eat-records/{id}`

规则：

- `user_id` 必须大于 0
- `person` 可为空，默认 `default`
- 创建时 `items` 必须非空
- 每个明细 `quantity > 0`、`price >= 0`
- `total_price = sum(quantity * price)`
- `eaten_at` 使用服务端当前时间
- 主表和明细必须同一事务写入，失败整体回滚
- 查询按 `eaten_at desc`
- 查询/删除只能操作指定 `user_id` 的记录

## 测试要求

必须补齐 pytest，至少覆盖：

- 统一响应格式
- 健康检查
- 配置默认值
- 数据库会话依赖可替换
- 分类列表、新增、修改、软删除、include_inactive
- 菜品列表分页、推荐筛选、分类筛选、关键词、详情、软删除
- 图片上传成功与非法类型失败
- banner 列表、新增、修改、软删除、非法 `link_type`
- 创建一起吃过记录成功、空 items、非法 user_id、非法 quantity、总价计算、事务回滚
- 查询指定 user_id 的记录
- 删除指定 user_id 的记录和禁止删除其他 user_id 记录
- Alembic 迁移至少能在测试或 CI 环境中被验证到模型元数据一致性

测试应优先使用临时测试数据库或 SQLite 兼容测试配置。若 SQLite 与 PostgreSQL 差异影响约束或类型，明确用 PostgreSQL 测试容器或 Docker Compose 运行集成测试。

## 质量门禁

完成前必须运行：

```bash
python -m pytest
python -m mypy backend
python -m ruff check backend tests
```

如果命令因环境缺失失败，主 Agent 必须先尝试补齐项目内配置和依赖说明。最终不能忽略失败结果；必须修复到通过，或在最终报告中明确阻塞原因、失败命令和失败输出摘要。

## 最终验收

全部完成后，主 Agent 必须确认：

- 所有后端任务 checklist 已更新
- `doc/tasks/progress.md` 后端模块已更新
- API 均返回 `{ code, data, message }`
- Docker Compose 能启动 api、db、nginx
- Nginx 能代理 `/api` 并访问 `/static` 上传图片
- pytest、mypy、ruff 均通过

最终输出一份简短报告，包含：

- 完成的模块
- 变更的关键文件
- 测试和检查命令结果
- 未完成项或风险
