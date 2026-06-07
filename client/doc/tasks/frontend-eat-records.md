# frontend-eat-records

目标：新增“一起吃过”记录列表页，支持查询和删除历史记录。

## 最小任务

- [x] 创建 `pages/eat-records/index.json`，标题为“一起吃过”
- [x] 创建 `pages/eat-records/index.wxml`
- [x] 创建 `pages/eat-records/index.wxss`
- [x] 创建 `pages/eat-records/index.js`
- [x] 页面 data 包含 `records`、`page`、`pageSize`、`loading`、`hasMore`
- [x] `onLoad` 或 `onShow` 调用 `loadRecords(true)`
- [x] `loadRecords(true)` 重置分页并请求 `WXAPI.eatRecords({ user_id, page: 1, page_size })`
- [x] `loadRecords(false)` 追加下一页
- [x] `onReachBottom` 在 `hasMore=true` 时加载更多
- [x] 列表展示 `eaten_at`、`remark`、`total_price`、`items`
- [x] 每个明细展示菜名、份数、规格或口味
- [x] 空列表展示“还没有一起吃过的记录”
- [x] 每条记录提供删除按钮
- [x] 删除前使用 `wx.showModal` 二次确认
- [x] 删除调用 `WXAPI.deleteEatRecord(id)`，携带固定 `user_id`
- [x] 删除成功后从 `records` 移除
- [x] 删除失败时保留本地列表并展示错误提示
- [x] 时间显示做轻量格式化，保留后端 ISO 时间兜底

## 验收

- [x] 从我的页和今晚吃啥页都能进入记录页
- [x] 记录分页加载不会重复覆盖已有数据
- [x] 删除记录后列表即时更新
