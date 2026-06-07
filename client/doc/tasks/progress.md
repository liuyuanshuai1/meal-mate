# 总体进度

> 根据 `proposal.md`、`detailed-design-backend.md`、`detailed-design-frontend.md` 拆分。每个模块完成后，将对应项勾选。

## 后端模块

- [ ] [backend-foundation](./backend-foundation.md) - FastAPI 项目骨架、配置、数据库、统一响应
- [ ] [backend-models-migrations](./backend-models-migrations.md) - 核心数据模型与 Alembic 迁移
- [ ] [backend-food-categories](./backend-food-categories.md) - 菜品分类 API
- [ ] [backend-foods](./backend-foods.md) - 菜品 API 与图片上传
- [ ] [backend-banners](./backend-banners.md) - 首页 banner API
- [ ] [backend-eat-records](./backend-eat-records.md) - 一起吃过记录 API
- [ ] [backend-deploy-seed](./backend-deploy-seed.md) - Docker、Nginx、初始化数据与验收

## 前端模块

- [x] [frontend-foundation-api](./frontend-foundation-api.md) - 全局配置、tabBar、请求封装与接口适配
- [x] [frontend-home](./frontend-home.md) - 首页“今日推荐/最近想吃/今晚安排”
- [x] [frontend-category](./frontend-category.md) - 菜单分类与菜品列表
- [x] [frontend-food-detail](./frontend-food-detail.md) - 菜品详情与加入今晚菜单
- [x] [frontend-dinner-plan](./frontend-dinner-plan.md) - 今晚吃啥页确认生成记录
- [x] [frontend-my](./frontend-my.md) - 我的页生活化入口改造
- [x] [frontend-eat-records](./frontend-eat-records.md) - 一起吃过记录列表页
- [x] [frontend-commercial-cleanup](./frontend-commercial-cleanup.md) - 隐藏支付、配送、优惠券等商业入口

## 联调验收

- [ ] 后端服务能启动，`/api/food-categories`、`/api/foods`、`/api/banners` 可返回统一格式
- [x] 小程序首页、菜单、菜品详情、今晚吃啥、我的、一起吃过页面可完整访问
- [x] 从菜品详情加入今晚菜单后，`shopCarInfo` 正确写入本地存储
- [x] 点击“就吃这些”成功调用 `POST /api/eat-records` 并清空 `shopCarInfo`
- [x] 一起吃过记录页可查询并删除指定 `user_id` 的记录
- [x] 用户看不到支付、配送、优惠券、砍价、拼团、积分、余额入口
