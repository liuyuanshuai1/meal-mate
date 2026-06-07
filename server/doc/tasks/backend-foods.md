# backend-foods

目标：实现菜品查询、维护和图片上传，支撑首页推荐、菜单页和详情页。

## 最小任务

- [x] 创建 `schemas/food.py`：新增、修改、列表项、详情返回 schema
- [x] 创建 `routers/foods.py`
- [x] 实现 `GET /api/foods`，支持 `category_id`、`recommended`、`keyword`、`include_inactive`、`page`、`page_size`
- [x] 列表返回分页格式 `{ items, total, page, page_size }`
- [x] 列表默认只返回 `is_active=true` 菜品
- [x] 菜品排序按 `sort` 升序、`id` 升序
- [x] 实现 `GET /api/foods/{id}`
- [x] 实现 `POST /api/foods`
- [x] 实现 `PUT /api/foods/{id}`
- [x] 实现 `DELETE /api/foods/{id}`，采用软删除 `is_active=false`
- [x] 创建上传目录，读取 `UPLOAD_DIR`
- [x] 实现 `POST /api/foods/image`，限制 jpg/png/webp 和文件大小
- [x] 图片上传成功后返回 `{ image_url }`，路径使用 `PUBLIC_STATIC_URL`
- [x] 在 `app/main.py` 注册菜品路由

## 验收

- [x] 推荐菜品可通过 `recommended=true` 查询
- [x] 关键词可按菜名模糊搜索
- [x] 菜品不存在或已下架时详情返回明确错误
- [x] 上传非图片文件会被拒绝
