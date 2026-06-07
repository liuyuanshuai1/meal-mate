# frontend-foundation-api

目标：完成小程序第一版全局配置、tabBar 文案、请求封装和后端接口适配。

## 最小任务

- [x] 修改 `config.js`，增加 `apiBaseUrl`、`fixedUserId`、`fixedPerson`
- [x] 将项目名称/说明调整为“一起吃饭叭第一版”
- [x] 修改 `app.json`，新增 `pages/eat-records/index`
- [x] 修改 `app.json` tabBar：`购物车` 改为 `今晚吃啥`
- [x] 保留 4 个 tab：首页、菜单、今晚吃啥、我的
- [x] 调整 `app.js`，首页标题固定为“一起吃饭叭”
- [x] 更新 `wxapi/main.js` 的请求基础地址为 `CONFIG.apiBaseUrl`
- [x] 统一处理后端 `{ code, data, message }` 返回格式
- [x] 新增 `WXAPI.banners(data)`
- [x] 新增 `WXAPI.foodCategories(data)`
- [x] 新增 `WXAPI.foods(data)`
- [x] 新增 `WXAPI.foodDetail(id)`
- [x] 新增 `WXAPI.createEatRecord(data)`
- [x] 新增 `WXAPI.eatRecords(data)`
- [x] 新增 `WXAPI.deleteEatRecord(id)`
- [x] 增加菜品列表字段适配：`image_url -> pic`，`price -> minPrice`，`category_id -> categoryId`
- [x] 增加菜品详情字段适配为现有页面可用的 `basicInfo`、`pics`、`content`、`properties`

## 验收

- [x] 现有页面调用 `WXAPI` 时无需直接拼接后端域名
- [x] `code !== 0` 时能显示 `message`
- [x] 固定用户信息从配置读取，不散落在页面里
