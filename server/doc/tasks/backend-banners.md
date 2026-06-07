# backend-banners

目标：实现首页轮播 banner CRUD。

## 最小任务

- [x] 创建 `schemas/banner.py`：新增、修改、返回 schema
- [x] 创建 `routers/banners.py`
- [x] 实现 `GET /api/banners`，默认只返回 `is_active=true`
- [x] 支持 `include_inactive` 查询参数
- [x] 列表按 `sort` 升序、`id` 升序返回
- [x] 实现 `POST /api/banners`
- [x] 校验 `link_type` 只能为 `none`、`food`、`url`
- [x] 实现 `PUT /api/banners/{id}`
- [x] 实现 `DELETE /api/banners/{id}`，采用软删除 `is_active=false`
- [x] 在 `app/main.py` 注册 banner 路由

## 验收

- [x] `GET /api/banners` 返回数组格式 `data: []`
- [x] `link_type=food` 时 `link_target` 可保存菜品 id 字符串
- [x] 删除后默认列表不再出现该 banner
