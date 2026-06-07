# frontend-food-detail

目标：菜品详情支持查看菜品、选择份数、加入今晚菜单。

## 最小任务

- [ ] 修改 `pages/goods-details/index.json`，标题为“菜品详情”
- [ ] 修改 `pages/goods-details/index.js`，通过 `WXAPI.foodDetail(goodsId)` 获取详情
- [ ] 读取本地 `shopCarInfo`，初始化当前已选份数 `shopNum`
- [ ] 保留图片、菜名、描述、参考价格展示
- [ ] 第一版 `properties` 为空时隐藏复杂规格选择区域
- [ ] 将“购买数量”改为“想吃份数”
- [ ] 将“加入购物车”改为“加入今晚菜单”
- [ ] 将“加入购物车成功”改为“已加入今晚菜单”
- [ ] 将“去结算”改为“去看看今晚吃啥”
- [ ] 将“购买数量不能为0”改为“份数不能为0”
- [ ] 将“请选择商品具体规格”改为“请选择口味或规格”
- [ ] 点击加入时校验 `buyNumber >= 1`
- [ ] 构造本地明细：`goodsId`、`pic`、`name`、`label`、`price`、`active`、`number`、`left`
- [ ] 相同 `goodsId + propertyChildIds` 再次加入时数量累加
- [ ] 更新 `shopCarInfo.shopNum` 和 `shopCarInfo.shopList`
- [ ] 写入 `wx.setStorage({ key: "shopCarInfo" })`
- [ ] 点击“去看看今晚吃啥”使用 `wx.switchTab` 到 `/pages/shop-cart/index`
- [ ] 移除或隐藏砍价、拼团、支付、库存强校验等第一版不做逻辑

## 验收

- [ ] 加入后本地 `shopCarInfo` 数据结构符合设计
- [ ] 同菜品同规格重复加入会累加数量
- [ ] 用户不会进入结算/付款流程
