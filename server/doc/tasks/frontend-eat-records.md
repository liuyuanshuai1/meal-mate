# frontend-eat-records

目标：新增“一起吃过”记录列表页，支持查询和删除历史记录。

## 最小任务

- [ ] 创建 `pages/eat-records/index.json`，标题为“一起吃过”
- [ ] 创建 `pages/eat-records/index.wxml`
- [ ] 创建 `pages/eat-records/index.wxss`
- [ ] 创建 `pages/eat-records/index.js`
- [ ] 页面 data 包含 `records`、`page`、`pageSize`、`loading`、`hasMore`
- [ ] `onLoad` 或 `onShow` 调用 `loadRecords(true)`
- [ ] `loadRecords(true)` 重置分页并请求 `WXAPI.eatRecords({ user_id, page: 1, page_size })`
- [ ] `loadRecords(false)` 追加下一页
- [ ] `onReachBottom` 在 `hasMore=true` 时加载更多
- [ ] 列表展示 `eaten_at`、`remark`、`total_price`、`items`
- [ ] 每个明细展示菜名、份数、规格或口味
- [ ] 空列表展示“还没有一起吃过的记录”
- [ ] 每条记录提供删除按钮
- [ ] 删除前使用 `wx.showModal` 二次确认
- [ ] 删除调用 `WXAPI.deleteEatRecord(id)`，携带固定 `user_id`
- [ ] 删除成功后从 `records` 移除
- [ ] 删除失败时保留本地列表并展示错误提示
- [ ] 时间显示做轻量格式化，保留后端 ISO 时间兜底

## 验收

- [ ] 从我的页和今晚吃啥页都能进入记录页
- [ ] 记录分页加载不会重复覆盖已有数据
- [ ] 删除记录后列表即时更新
