# frontend-dinner-plan

目标：将购物车页改造成“今晚吃啥”，支持修改当前菜单并确认生成一起吃过记录。

## 最小任务

- [ ] 修改 `pages/shop-cart/index.json`，标题为“今晚吃啥”
- [ ] 修改 `pages/shop-cart/index.wxml` 和相关模板文案：空购物车改为“今晚还没选吃什么～”
- [ ] 将“去选购美食”改为“去菜单看看”
- [ ] 将“您选购的商品”改为“今晚想吃这些”
- [ ] 将“合计”改为“参考合计”
- [ ] 将“去结算”改为“就吃这些”
- [ ] `onShow` 从 `wx.getStorageSync("shopCarInfo")` 读取当前菜单
- [ ] 保留左滑删除、数量增减、全选、批量删除能力
- [ ] 每次数量/删除/勾选变化后同步更新 `shopCarInfo`
- [ ] 点击“去菜单看看”使用 `wx.switchTab` 到 `/pages/category/category`
- [ ] 点击“就吃这些”时过滤 `active=true` 的菜品
- [ ] 未选择任何菜品时 toast “还没选好今晚吃什么”
- [ ] 组装 `POST /api/eat-records` 请求体，包含 `user_id`、`person`、`items`、`remark`
- [ ] 明细字段映射：`goodsId -> food_id`，`name -> food_name`，`pic -> food_image_url`，`number -> quantity`，`price -> price`，`label -> spec`
- [ ] 请求中显示 loading 或禁用按钮，避免重复提交
- [ ] 成功后 `wx.removeStorageSync("shopCarInfo")`
- [ ] 成功后清空页面列表并 toast “已记录这顿饭”
- [ ] 成功后 `wx.navigateTo` 到 `/pages/eat-records/index`
- [ ] 网络失败时 toast “记录失败，请稍后再试”
- [ ] 后端 `code !== 0` 时展示后端 `message`

## 验收

- [ ] 今晚菜单为空时不能确认
- [ ] 成功确认后不进入待付款订单页
- [ ] 创建记录成功后本地菜单被清空
