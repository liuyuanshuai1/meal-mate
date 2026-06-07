# Vibe Coding 起始 Prompt：简单管理系统 Agent

你是“一起吃饭叭”简单管理系统实现的主 Agent。你的职责是根据需求文档和详细设计文档，完整实现 FastAPI 内嵌管理后台，并完成自动化测试、类型检查、代码风格检查和进度记录。

整个过程不会有人工参与。遇到实现细节不明确时，必须优先阅读输入文档和现有代码，从已有设计和项目模式中推断；只有出现无法安全推断且会阻塞实现的问题时，才提出问题。

## 必读输入

开始前必须阅读并遵守：

- `doc/proposal-manager.md`
- `doc/detailed-design-manager.md`
- `doc/proposal.md`
- `doc/detailed-design-backend.md`
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/core/database.py`
- `backend/app/routers/food_categories.py`
- `backend/app/routers/foods.py`
- `backend/app/routers/banners.py`
- `backend/app/routers/eat_records.py`
- `backend/app/models/food_category.py`
- `backend/app/models/food.py`
- `backend/app/models/banner.py`
- `backend/app/models/eat_record.py`
- `tests/`

## 产品目标

实现一个简单管理系统，用于维护当前小程序的测试和运营数据：

- 菜品分类管理
- 菜品管理
- Banner 管理
- 一起吃过记录管理

后台采用方案 A：

```text
FastAPI 内嵌后台页面
Jinja2 渲染 HTML
Bootstrap / 简单 CSS
不引入 Vue、React、Node 或独立前端工程
```

后台第一版不做登录、账号权限、操作审计、复杂筛选、批量导入导出，也不实现“今晚吃啥查看”。未确认的今晚菜单仍然只存在小程序前端本地 `shopCarInfo`，本轮不要新增 `dinner_plan` 或 `dinner_plan_item`。

## 进度跟踪

必须创建并维护：

```text
doc/checklist-manager.md
```

该文件用于跟踪管理后台整体进度。开始实现前先创建 checklist，至少包含：

```text
依赖与基础设施
后台首页
菜品分类管理
菜品管理
Banner 管理
一起吃过记录管理
测试
mypy
ruff
最终验收
```

规则：

- 每完成一个模块并通过对应测试后，再勾选该模块。
- 如果发现设计文档和现有代码冲突，在 checklist 中记录处理结论。
- 最终提交前，checklist 必须反映真实完成状态。

## 技术约束

使用现有后端技术栈：

```text
Python 3.11+
FastAPI
SQLAlchemy 2.x asyncio
Pydantic / pydantic-settings
PostgreSQL
pytest
mypy
ruff
```

新增依赖：

```text
jinja2
```

依赖要求：

- 在 `backend/requirements.txt` 中补充 `jinja2`。
- 不新增前端构建链路。
- 不引入大型后台框架。
- 如使用 Bootstrap，优先用 CDN 或极简本地 CSS，保持实现简单。

质量门禁：

```bash
python -m pytest
python -m mypy backend
python -m ruff check backend tests
```

不得通过删除测试、降低类型检查价值、扩大 ignore 范围来绕过质量门禁。

## 实现范围

需要新增或修改的主要文件：

```text
backend/requirements.txt
backend/app/main.py
backend/app/routers/admin.py
backend/app/templates/admin/base.html
backend/app/templates/admin/index.html
backend/app/templates/admin/categories.html
backend/app/templates/admin/foods.html
backend/app/templates/admin/banners.html
backend/app/templates/admin/eat_records.html
backend/app/templates/admin/eat_record_detail.html
tests/test_admin_manager.py
doc/checklist-manager.md
```

如果实现中需要抽取公共图片上传函数，可以新增：

```text
backend/app/services/image_upload.py
```

如果抽取公共函数，必须保持现有 `/api/foods/image` 行为不变，并补充或调整测试。

## 路由设计

后台页面路由统一挂载在 `/admin`。

必须实现：

```text
GET  /admin

GET  /admin/categories
POST /admin/categories
POST /admin/categories/{category_id}/update
POST /admin/categories/{category_id}/delete

GET  /admin/foods
POST /admin/foods
POST /admin/foods/{food_id}/update
POST /admin/foods/{food_id}/delete

GET  /admin/banners
POST /admin/banners
POST /admin/banners/{banner_id}/update
POST /admin/banners/{banner_id}/delete

GET  /admin/eat-records
GET  /admin/eat-records/{record_id}
POST /admin/eat-records/{record_id}/delete
```

页面请求返回 HTML，不使用 `/api` 的 `{ code, data, message }` JSON 格式。

成功提交后使用 `RedirectResponse` 返回列表页，并通过 query 参数显示成功消息：

```text
message=created
message=updated
message=deleted
```

失败时返回当前 HTML 页面并展示错误提示。

## 通用页面要求

所有后台页面必须继承或复用 `base.html`。

`base.html` 至少包含：

- 页面标题
- 顶部导航
- 内容区域
- 成功消息区域
- 错误消息区域
- 删除二次确认脚本或等价浏览器 confirm

导航包含：

- 后台首页
- 菜品分类
- 菜品
- Banner
- 一起吃过记录

第一版页面只需要清晰可用，不追求复杂视觉效果。

## 模块 1：后台首页

实现：

```text
GET /admin
templates/admin/index.html
```

首页展示四个入口：

- 菜品分类管理 -> `/admin/categories`
- 菜品管理 -> `/admin/foods`
- Banner 管理 -> `/admin/banners`
- 一起吃过记录 -> `/admin/eat-records`

测试至少覆盖：

- `/admin` 返回 200
- 页面包含四个入口链接

## 模块 2：菜品分类管理

复用模型：

```text
FoodCategory
```

页面：

```text
/admin/categories
templates/admin/categories.html
```

字段：

```text
name       必填，最长 64 字符
sort       整数，默认 0
is_active  checkbox，默认启用
```

行为：

- 列表展示所有分类，包括 `is_active=false`。
- 排序为 `sort asc, id asc`。
- 新增分类。
- 修改分类。
- 删除分类时软删除，即 `is_active=false`。
- 不物理删除分类。
- 不检查分类下是否存在菜品。

测试至少覆盖：

- 分类列表页返回 200。
- 新增分类后页面能看到分类名称。
- 修改分类名称、排序、启用状态成功。
- 删除分类后 `is_active=false`。
- 删除后 `/api/food-categories` 默认不返回该分类。

## 模块 3：菜品管理

复用模型：

```text
Food
FoodCategory
```

页面：

```text
/admin/foods
templates/admin/foods.html
```

字段：

```text
category_id       可为空
name              必填，最长 128 字符
description       可为空
image_url         可为空
image_file        可为空
price             Decimal，默认 0，必须 >= 0
is_recommended    checkbox，默认否
is_active         checkbox，默认上架
sort              整数，默认 0
```

行为：

- 列表展示所有菜品，包括 `is_active=false`。
- 排序为 `sort asc, id asc`。
- 列表展示所属分类名称。
- 新增菜品。
- 修改菜品。
- 删除菜品时软删除，即 `is_active=false`。
- 支持直接填写图片 URL。
- 支持上传图片，上传成功后保存生成的 URL。
- 如果上传了图片，优先使用上传图片 URL。
- 如果没有上传图片，使用表单中的 `image_url`。

图片规则必须与现有 `/api/foods/image` 一致：

```text
允许 image/jpeg -> .jpg
允许 image/png  -> .png
允许 image/webp -> .webp
最大 5MB
保存到 settings.upload_dir
URL 使用 settings.public_static_url
```

测试至少覆盖：

- 菜品列表页返回 200。
- 新增菜品后页面能看到菜品名称。
- 新增菜品可设置分类、价格、推荐、上架、排序。
- 修改菜品信息成功。
- 上传合法图片成功并保存 URL。
- 上传非法图片类型失败并展示错误。
- 删除菜品后 `is_active=false`。
- 下架或删除后 `/api/foods` 默认不返回该菜品。
- 推荐菜品可通过 `/api/foods?recommended=true` 返回。

## 模块 4：Banner 管理

复用模型：

```text
Banner
```

页面：

```text
/admin/banners
templates/admin/banners.html
```

字段：

```text
title        可为空，最长 128 字符
image_url    必填
link_type    none / food / url，默认 none
link_target  可为空，最长 256 字符
sort         整数，默认 0
is_active    checkbox，默认启用
```

行为：

- 列表展示所有 Banner，包括 `is_active=false`。
- 排序为 `sort asc, id asc`。
- 新增 Banner。
- 修改 Banner。
- 删除 Banner 时软删除，即 `is_active=false`。
- `link_type` 只能是 `none`、`food`、`url`。
- 第一版不强制校验 `link_type=food` 时 `link_target` 对应菜品存在。

测试至少覆盖：

- Banner 列表页返回 200。
- 新增 Banner 后页面能看到标题或图片 URL。
- 修改 Banner 成功。
- 非法 `link_type` 失败并展示错误。
- 删除 Banner 后 `is_active=false`。
- 删除后 `/api/banners` 默认不返回该 Banner。

## 模块 5：一起吃过记录管理

复用模型和服务：

```text
EatRecord
EatRecordItem
```

页面：

```text
/admin/eat-records
/admin/eat-records/{record_id}
templates/admin/eat_records.html
templates/admin/eat_record_detail.html
```

用户规则：

- 默认 `user_id=1`。
- 支持 query 参数 `/admin/eat-records?user_id=1`。
- `user_id` 必须是大于 0 的整数。
- 详情和删除未传 `user_id` 时默认使用 1。

列表行为：

- 查询指定 `user_id` 的历史记录。
- 使用 `selectinload(EatRecord.items)` 加载明细。
- 排序为 `eaten_at desc, id desc`。
- 展示记录 ID、用户 ID、person、总价、吃饭时间、菜品数量、创建时间。

详情行为：

- 查询指定 `record_id` 和 `user_id` 的记录。
- 展示主记录信息。
- 展示菜品明细：food_id、food_name、food_image_url、quantity、price、小计。

删除行为：

- 删除指定 `record_id` 和 `user_id` 的记录。
- 删除主记录时明细级联删除。
- 删除后重定向回 `/admin/eat-records?user_id={user_id}&message=deleted`。

测试至少覆盖：

- 记录列表页返回 200。
- 默认查询 `user_id=1`。
- 指定 `user_id` 只展示该用户记录。
- 详情页展示记录和菜品明细。
- 删除记录后列表不再展示。
- 删除记录后 `/api/eat-records?user_id=1` 不再返回该记录。
- 非法 `user_id` 展示错误或返回 400/HTML 错误页。

## 表单与校验要求

字符串：

- 必填字段 trim 后不能为空。
- 可空字段 trim 后为空保存为 `None`。
- 必须遵守模型和详细设计中的长度限制。

数字：

- `sort` 为空按 0。
- `price` 为空按 0。
- `user_id` 为空按 1。
- 非法数字必须展示错误。
- `price` 使用 `Decimal`，禁止负数。

布尔：

- checkbox 选中为 true。
- checkbox 未选中为 false。

错误文案至少覆盖：

- 数据不存在
- 保存失败，请稍后再试
- 只允许上传 jpg、png 或 webp 图片
- 图片不能超过 5MB
- 参数错误

数据库提交失败时必须回滚事务。

## 测试要求

必须新增完整 pytest 单元测试。优先新增：

```text
tests/test_admin_manager.py
```

测试应使用现有测试夹具和测试数据库方式，不依赖真实外部服务。

测试重点：

- HTML 页面可访问。
- 表单提交能创建、修改、删除数据。
- 后台软删除与现有 `/api` 默认过滤逻辑一致。
- 图片上传成功和失败路径。
- 一起吃过记录详情和删除。
- 错误输入能得到可理解的错误页面或响应。

如果模板内容测试不适合精确匹配完整 HTML，只验证关键文本、链接、状态码和数据库结果。

不得只做快照测试。每个模块必须有行为测试。

## mypy 与 ruff 要求

完成实现后必须通过：

```bash
python -m mypy backend
python -m ruff check backend tests
```

类型要求：

- 新增 Python 函数必须有类型标注。
- 不使用无意义的 `Any` 逃避类型检查。
- 不为了通过 mypy 大面积添加 `# type: ignore`。

风格要求：

- 遵守现有 `pyproject.toml`。
- 不引入未使用变量和未使用 import。
- 不把格式问题留给后续人工处理。

## 主 Agent 工作流程

1. 阅读输入文档和现有代码。
2. 创建 `doc/checklist-manager.md`。
3. 确认当前测试、mypy、ruff 的基线状态。
4. 补充依赖 `jinja2`。
5. 实现后台基础设施：`admin.py`、模板目录、`main.py` 路由注册。
6. 实现后台首页。
7. 实现菜品分类管理和测试。
8. 实现菜品管理和测试。
9. 实现 Banner 管理和测试。
10. 实现一起吃过记录管理和测试。
11. 运行全量 pytest。
12. 运行 mypy。
13. 运行 ruff。
14. 更新 `doc/checklist-manager.md`。
15. 最终输出实施报告。

如果需要使用子 Agent，可以按模块拆分，但必须避免并行修改同一文件造成冲突。共享文件如 `backend/app/main.py`、`backend/requirements.txt`、`doc/checklist-manager.md` 由主 Agent 统一维护。

## 最终验收

最终必须确认：

- `doc/checklist-manager.md` 已创建并更新。
- `doc/proposal-manager.md` 的功能范围已实现。
- `doc/detailed-design-manager.md` 的路由、模板和行为要求已实现。
- `/admin` 可以访问。
- `/admin/categories` 可以完成分类增改删查。
- `/admin/foods` 可以完成菜品增改删查、图片 URL 和上传、推荐和上架设置。
- `/admin/banners` 可以完成 Banner 增改删查。
- `/admin/eat-records` 可以查看历史记录、查看详情、删除错误记录。
- 未实现“今晚吃啥查看”，且没有新增 dinner_plan 相关表或路由。
- 现有 `/api` 接口行为未被破坏。
- `python -m pytest` 通过。
- `python -m mypy backend` 通过。
- `python -m ruff check backend tests` 通过。

最终报告必须包含：

- 完成的模块
- 关键变更文件
- 测试命令和结果
- mypy 命令和结果
- ruff 命令和结果
- 未完成项或风险
