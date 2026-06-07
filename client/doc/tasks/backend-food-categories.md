# backend-food-categories

目标：实现菜品分类 CRUD，用于菜单页左侧分类和后台维护。

## 最小任务

- [ ] 创建 `schemas/food_category.py`：新增、修改、返回 schema
- [ ] 创建 `routers/food_categories.py`
- [ ] 实现 `GET /api/food-categories`，默认只返回 `is_active=true`
- [ ] 支持查询参数 `include_inactive`，为 true 时返回全部分类
- [ ] 列表按 `sort` 升序、`id` 升序返回
- [ ] 实现 `POST /api/food-categories`
- [ ] 实现 `PUT /api/food-categories/{id}`
- [ ] 实现 `DELETE /api/food-categories/{id}`，采用软删除 `is_active=false`
- [ ] 分类不存在时返回 `code=40004`
- [ ] 参数错误时返回 `code=40001`
- [ ] 在 `app/main.py` 注册分类路由

## 验收

- [ ] 查询接口返回数组格式 `data: []`
- [ ] 新增、修改后自动维护 `created_at`、`updated_at`
- [ ] 删除分类不会物理删除数据库记录
