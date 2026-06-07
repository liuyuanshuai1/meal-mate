# 一起吃饭叭小程序前端详细设计

## 1. 设计目标

根据 `proposal.md`，前端第一版目标是基于现有开源面馆小程序做最小改造，把传统商城/点餐流程收束为：

```text
浏览菜品 -> 选择今晚想吃 -> 确认今晚菜单 -> 生成一起吃过记录
```

第一版不接微信登录，不做支付、配送、优惠券、砍价、拼团、积分、余额等电商能力。前端使用固定用户标识调用后端接口。

## 2. 技术栈

现有前端技术栈保持不变：

```text
微信小程序原生开发
WXML
WXSS
JavaScript
WeUI/WXSS 样式
wx.request
本地存储 wx.setStorage / wx.getStorageSync
```

不引入 Vant Weapp，不引入新的前端框架。

## 3. 目录与页面规划

### 3.1 保留并改造的页面

```text
pages/index/index              首页
pages/category/category        菜单页
pages/goods-details/index      菜品详情页
pages/shop-cart/index          今晚吃啥页
pages/my/index                 我的页
```

### 3.2 新增页面

```text
pages/eat-records/index        一起吃过记录列表页
```

新增页面用于展示历史一起吃过记录，不继续把记录列表塞在 `pages/my/index` 中。

### 3.3 保留但不展示入口的页面

以下页面第一版不删除文件，但不在 tab、按钮、列表入口中展示：

```text
pages/to-pay-order/index
pages/wuliu/index
pages/recharge/index
pages/withdraw/index
pages/kanjia/index
pages/score-excharge/index
pages/asset/index
pages/score/index
pages/maidan/index
pages/coupons/index
pages/mycoupons/index
```

## 4. 全局配置设计

### 4.1 app.json

`pages` 增加一起吃过记录页：

```json
{
  "pages": [
    "pages/index/index",
    "pages/category/category",
    "pages/goods-details/index",
    "pages/shop-cart/index",
    "pages/my/index",
    "pages/eat-records/index"
  ]
}
```

说明：实际文件中可继续保留历史页面路径，但第一版功能入口只使用上述核心页面。

tabBar 保持 4 个入口：

```text
首页
菜单
今晚吃啥
我的
```

`pages/shop-cart/index` 的 tab 文案由“购物车”改为“今晚吃啥”。

### 4.2 config.js

新增后端 API 基础地址配置：

```javascript
module.exports = {
  version: "0.0.1",
  note: "一起吃饭叭第一版",
  apiBaseUrl: "http://127.0.0.1:8000/api",
  fixedUserId: 1,
  fixedPerson: "default"
}
```

开发、测试、生产环境可通过修改 `apiBaseUrl` 切换。

### 4.3 app.js

首页标题不再从远程 `mallName` 获取，固定为：

```text
一起吃饭叭
```

保留网络状态监听和小程序更新检测。

登录相关逻辑第一版不作为主流程依赖。需要用户标识时，前端统一使用 `CONFIG.fixedUserId` 和 `CONFIG.fixedPerson`。

## 5. API 适配层设计

### 5.1 统一请求方法

在 `wxapi/main.js` 中保留 `request` 封装，但 API 基础地址改为后端服务地址：

```text
CONFIG.apiBaseUrl
```

请求返回格式统一：

```json
{
  "code": 0,
  "data": {},
  "message": ""
}
```

前端判断规则：

```text
code === 0 表示成功
code !== 0 表示失败，message 用于 toast 或 modal 展示
```

### 5.2 新接口方法

新增或替换以下方法：

```javascript
banners(data)
foodCategories(data)
foods(data)
foodDetail(id)
createEatRecord(data)
eatRecords(data)
deleteEatRecord(id)
```

### 5.3 旧字段兼容策略

为减少页面改动，API 适配层可以把后端字段转换为当前页面更容易使用的旧字段结构。

菜品列表后端字段：

```json
{
  "id": 1,
  "category_id": 2,
  "name": "番茄炒蛋",
  "description": "家常口味",
  "image_url": "https://example.com/a.jpg",
  "price": 18,
  "is_recommended": true
}
```

前端页面兼容字段：

```json
{
  "id": 1,
  "categoryId": 2,
  "name": "番茄炒蛋",
  "pic": "https://example.com/a.jpg",
  "minPrice": 18,
  "description": "家常口味"
}
```

菜品详情前端兼容结构：

```json
{
  "basicInfo": {
    "id": 1,
    "name": "番茄炒蛋",
    "pic": "https://example.com/a.jpg",
    "minPrice": 18,
    "stores": 999
  },
  "pics": [
    {
      "pic": "https://example.com/a.jpg"
    }
  ],
  "content": "家常口味",
  "properties": []
}
```

第一版不设计复杂规格库存，`properties` 默认为空，`stores` 给一个足够大的固定值。

## 6. 本地状态设计

### 6.1 当前今晚菜单

继续复用本地存储 key：

```text
shopCarInfo
```

语义变更为“当前今晚菜单”。

数据结构：

```json
{
  "shopNum": 2,
  "shopList": [
    {
      "goodsId": 1,
      "pic": "https://example.com/a.jpg",
      "name": "番茄炒蛋",
      "label": "",
      "price": 18,
      "active": true,
      "number": 1,
      "left": ""
    }
  ]
}
```

字段说明：

```text
shopNum     当前已选份数合计
shopList    当前今晚菜单明细
goodsId     菜品 id
pic         菜品图片
name        菜名
label       规格/口味，第一版可为空
price       参考价格
active      是否选中用于确认
number      份数
left        左滑删除 UI 状态
```

### 6.2 固定用户

第一版不接微信登录，所有请求携带固定用户：

```json
{
  "user_id": 1,
  "person": "default"
}
```

`person` 用于后续扩展“谁选的”，第一版只固定传值。

## 7. 页面详细设计

### 7.1 首页 pages/index/index

页面目标：展示 banner、今日推荐、最近想吃和今晚安排入口。

数据字段：

```javascript
data: {
  swiperCurrent: 0,
  bannerList: [],
  goodsRecommend: [],
  recentFoods: []
}
```

加载流程：

```text
onShow
  -> WXAPI.banners()
  -> WXAPI.foods({ recommended: true })
  -> 可选：WXAPI.eatRecords({ page: 1, page_size: 3 }) 提取最近吃过菜品
```

页面调整：

```text
导航标题固定为“一起吃饭叭”
保留 banner 轮播
隐藏门店地址、营业时间、联系电话、地图
“店家推荐”改为“今日推荐”
新增“今晚安排”入口，点击 switchTab 到 pages/shop-cart/index
```

交互：

```text
点击 banner：如果 banner.business_id 或 food_id 存在，进入菜品详情
点击推荐菜品：navigateTo pages/goods-details/index?id=xxx
点击今晚安排：switchTab pages/shop-cart/index
```

空状态：

```text
bannerList 为空：隐藏轮播区域
goodsRecommend 为空：显示“今天还没想好吃什么”
```

### 7.2 菜单页 pages/category/category

页面目标：按分类浏览菜品。

数据字段沿用：

```javascript
data: {
  categories: [],
  goodsWrap: [],
  categorySelected: "",
  goodsToView: "",
  categoryToView: ""
}
```

加载流程：

```text
onLoad
  -> WXAPI.foodCategories()
  -> WXAPI.foods({ page: 1, page_size: 1000 })
  -> 按 category_id 组装 goodsWrap
```

分类结构：

```json
{
  "id": 1,
  "name": "家常菜",
  "sort": 1,
  "scrollId": "s1"
}
```

菜品结构：

```json
{
  "id": 1,
  "categoryId": 1,
  "name": "番茄炒蛋",
  "pic": "https://example.com/a.jpg",
  "minPrice": 18
}
```

交互沿用：

```text
点击左侧分类，右侧滚动到对应分类
右侧滚动时更新左侧选中项
点击菜品进入详情页
```

### 7.3 菜品详情页 pages/goods-details/index

页面目标：查看菜品详情，并加入今晚菜单。

数据字段沿用：

```javascript
data: {
  goodsDetail: {},
  selectSizePrice: 0,
  shopNum: 0,
  buyNumber: 1,
  buyNumMin: 1,
  buyNumMax: 999,
  propertyChildIds: "",
  propertyChildNames: "",
  canSubmit: true,
  shopCarInfo: {}
}
```

加载流程：

```text
onLoad
  -> 保存 goodsId
  -> 读取 shopCarInfo，更新 shopNum
onShow
  -> WXAPI.foodDetail(goodsId)
  -> 设置 goodsDetail、selectSizePrice、buyNumber
```

文案替换：

```text
商品详情 -> 菜品详情
购买数量 -> 想吃份数
去结算 -> 去看看今晚吃啥
加入购物车 -> 加入今晚菜单
加入购物车成功 -> 已加入今晚菜单
购买数量不能为0 -> 份数不能为0
请选择商品具体规格 -> 请选择口味或规格
```

加入今晚菜单逻辑：

```text
校验 buyNumber >= 1
构造 shopCarMap
读取 shopCarInfo.shopList
如果 goodsId + propertyChildIds 相同，则数量累加
否则追加新菜品
更新 shopNum
写入 wx.setStorage({ key: "shopCarInfo" })
toast “已加入今晚菜单”
```

跳转：

```text
点击“去看看今晚吃啥”：wx.switchTab({ url: "/pages/shop-cart/index" })
```

第一版不处理砍价、拼团、视频、库存校验和支付相关逻辑。

### 7.4 今晚吃啥页 pages/shop-cart/index

页面目标：查看当前今晚菜单，修改份数，确认生成一起吃过记录。

数据字段沿用：

```javascript
data: {
  goodsList: {
    saveHidden: true,
    totalPrice: 0,
    allSelect: true,
    noSelect: false,
    list: []
  },
  delBtnWidth: 120
}
```

页面文案：

```text
购物车空空如也～ -> 今晚还没选吃什么～
去选购美食 -> 去菜单看看
您选购的商品 -> 今晚想吃这些
合计 -> 参考合计
去结算 -> 就吃这些
```

读取流程：

```text
onShow
  -> wx.getStorageSync("shopCarInfo")
  -> goodsList.list = shopCarInfo.shopList || []
  -> 计算 totalPrice、allSelect、noSelect
```

确认流程：

```text
用户点击“就吃这些”
  -> 过滤 active 为 true 的菜品
  -> 如果为空，toast “还没选好今晚吃什么”
  -> 组装 POST /api/eat-records 请求
  -> 成功后 wx.removeStorageSync("shopCarInfo")
  -> 清空页面 goodsList
  -> toast “已记录这顿饭”
  -> navigateTo pages/eat-records/index
```

请求体：

```json
{
  "user_id": 1,
  "person": "default",
  "items": [
    {
      "food_id": 1,
      "food_name": "番茄炒蛋",
      "food_image_url": "https://example.com/a.jpg",
      "quantity": 1,
      "price": 18,
      "spec": ""
    }
  ],
  "remark": ""
}
```

错误处理：

```text
网络失败：toast “记录失败，请稍后再试”
后端 code !== 0：展示 message
确认中：按钮置灰或 wx.showLoading
```

### 7.5 我的页 pages/my/index

页面目标：展示用户信息和功能入口。

第一版不展示余额和订单付款内容。

展示内容：

```text
默认头像/昵称
一起吃过
偏好设置
不想吃清单
关于我们
```

入口行为：

```text
点击“一起吃过”：navigateTo /pages/eat-records/index
点击“偏好设置”：第一版可 toast “后续开放”
点击“不想吃清单”：第一版可 toast “后续开放”
点击“关于我们”：展示简单弹窗
```

固定用户展示：

```text
昵称可显示：一起吃饭叭
用户标识不暴露给用户
```

### 7.6 一起吃过记录页 pages/eat-records/index

页面目标：查询和删除历史一起吃过记录。

页面文件：

```text
pages/eat-records/index.wxml
pages/eat-records/index.wxss
pages/eat-records/index.js
pages/eat-records/index.json
```

导航标题：

```text
一起吃过
```

数据字段：

```javascript
data: {
  records: [],
  page: 1,
  pageSize: 20,
  loading: false,
  hasMore: true
}
```

加载流程：

```text
onLoad/onShow
  -> loadRecords(true)
onReachBottom
  -> hasMore 时 loadRecords(false)
```

接口：

```text
GET /api/eat-records?user_id=1&page=1&page_size=20
DELETE /api/eat-records/{id}?user_id=1
```

列表展示字段：

```text
吃饭时间 eaten_at
备注 remark
参考花费 total_price
菜品列表 items
菜品份数 quantity
```

删除流程：

```text
点击删除
  -> wx.showModal 二次确认
  -> DELETE /api/eat-records/{id}
  -> 成功后从 records 移除
```

空状态：

```text
还没有一起吃过的记录
```

## 8. 静态资源与样式

图标第一版可沿用现有 tabBar 图标。

样式原则：

```text
保持现有暖色背景 #f6f0e3
保留 WeUI 按钮和列表样式
去掉强商城感的支付/订单/金额强调
价格统一显示为“参考价”或“参考合计”
```

## 9. 异常与边界处理

```text
接口失败：统一 toast 或 modal 展示 message
菜品分类为空：显示空状态
菜品为空：显示空状态
菜品详情不存在：提示“菜品不存在或已下架”
今晚菜单为空：不允许确认
一起吃过记录为空：显示空状态
删除记录失败：不移除本地列表
```

## 10. 验收清单

```text
tabBar 显示：首页、菜单、今晚吃啥、我的
首页标题为“一起吃饭叭”
首页展示 banner 和今日推荐
菜单页能按分类展示菜品
菜品详情页能加入今晚菜单
今晚吃啥页能修改份数、删除菜品
点击“就吃这些”会调用 POST /api/eat-records
记录成功后本地 shopCarInfo 被清空
我的页点击“一起吃过”进入独立记录页
一起吃过记录页能查询和删除记录
用户看不到支付、配送、优惠券、砍价、拼团、积分、余额入口
```

