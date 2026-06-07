# frontend-home

目标：把首页改造成轻量决策入口，展示 banner、今日推荐、最近想吃和今晚安排入口。

## 最小任务

- [x] 修改 `pages/index/index.json`，导航标题为“一起吃饭叭”
- [x] 修改 `pages/index/index.js`，`onShow` 加载 `WXAPI.banners()`
- [x] 修改 `pages/index/index.js`，`onShow` 加载 `WXAPI.foods({ recommended: true })`
- [x] 可选加载 `WXAPI.eatRecords({ page: 1, page_size: 3 })`，提取最近吃过菜品
- [x] 修改 `pages/index/index.wxml`，保留 banner 轮播
- [x] 隐藏门店地址、营业时间、电话、地图模块
- [x] 将“店家推荐”改为“今日推荐”
- [x] 增加“今晚安排”入口，点击 `wx.switchTab` 到 `/pages/shop-cart/index`
- [x] 推荐菜品点击进入 `/pages/goods-details/index?id=xxx`
- [x] banner 点击：`link_type=food` 时进入对应菜品详情
- [x] 推荐为空时展示“今天还没想好吃什么”
- [x] banner 为空时隐藏轮播区域

## 验收

- [x] 首页不再出现强门店/商城信息
- [x] 今日推荐能打开菜品详情
- [x] 今晚安排能进入“今晚吃啥”
