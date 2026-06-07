# 一起吃饭叭小程序需求文档

## 1. 项目定位

“一起吃饭叭”是一款面向情侣、家庭或同住伙伴的微信小程序，用于解决日常生活里“今天吃什么”的轻量决策问题，并沉淀两个人一起吃过的饭菜记录。

本项目第一版不做传统餐饮电商系统，不做外卖、配送、支付、优惠券、砍价、拼团、积分、余额等商业功能。第一版只围绕一个核心闭环设计：

```text
浏览菜品 -> 选择今晚想吃 -> 确认今晚菜单 -> 生成一起吃过记录
```

产品调性为温暖、轻量、生活化，文案应尽量贴近日常表达，避免“下单、结算、购物车、商品、订单”等强电商语义。

## 2. 前端现状分析

当前前端是开源面馆小程序模板，使用微信小程序原生开发，样式主要基于 WeUI/WXSS，不是 Vant Weapp。项目已有页面和能力包括：

```text
首页 pages/index/index
菜单分类页 pages/category/category
菜品详情页 pages/goods-details/index
购物车页 pages/shop-cart/index
待付款订单页 pages/to-pay-order/index
我的/订单页 pages/my/index
优惠券、积分、充值、提现、砍价、买单、物流等商业页面
```

可直接复用的前端能力：

```text
菜品分类列表
菜品详情展示
加入本地购物车
本地购物车数量增减、删除、全选
首页 banner 和推荐菜品
微信小程序 tabBar 结构
```

需要改造的核心方向：

```text
购物车 -> 今晚吃啥
商品 -> 菜品
加入购物车 -> 加入今晚菜单
去结算/提交订单 -> 就吃这些
订单记录 -> 一起吃过记录
店家推荐 -> 今日推荐
mallName -> 一起吃饭叭
```

建议第一版尽量少改前端结构，优先保留现有页面文件和本地存储逻辑，把原 `shopCarInfo` 作为“今晚菜单”的本地状态容器继续使用。后续如需代码语义更干净，可再统一重命名为 `dinnerPlanInfo`。

## 3. 第一版范围

### 3.1 必做

```text
首页展示今日推荐菜品
菜单页展示分类和菜品
菜品详情页支持查看菜品、选择数量、加入今晚菜单
今晚吃啥页支持查看、删除、修改数量
点击“就吃这些”后生成一起吃过记录
我的页展示用户信息和“一起吃过”入口
后端提供菜品、今晚菜单、一起吃过记录 API
```

### 3.2 第一版不做

```text
微信支付
余额充值
提现
积分
优惠券
砍价
拼团
物流配送
门店地图
外卖订单
后台营销活动
复杂推荐算法
多人实时协同点菜
```

这些功能在现有前端中已有页面或遗留代码，第一版应从入口上隐藏或移除，避免用户误入。

## 4. 信息架构

第一版保留 4 个底部 tab：

```text
首页
菜单
今晚吃啥
我的
```

对应现有前端文件：

```text
首页       pages/index/index
菜单       pages/category/category
今晚吃啥   pages/shop-cart/index
我的       pages/my/index
菜品详情   pages/goods-details/index
```

`app.json` 中 tabBar 文案需要调整：

```text
购物车 -> 今晚吃啥
```

如图标暂不调整，可沿用原购物车图标；后续可替换为碗、筷子、清单等更符合场景的图标。

## 5. 页面需求

### 5.1 首页

首页定位：进入小程序后的轻量决策入口，帮助用户快速看到今天可以吃什么。

当前可复用能力：

```text
bannerList 轮播图
goodsRecommend 推荐菜品
菜品详情跳转
```

页面展示内容：

```text
顶部标题：一起吃饭叭
今日推荐
最近想吃
今晚安排入口
```

文案调整：

```text
店家推荐 -> 今日推荐
商品价格 -> 可保留为参考价格；若不需要价格，可改为“想吃指数”或隐藏价格
```

交互要求：

```text
点击推荐菜品进入菜品详情
点击“今晚安排”进入“今晚吃啥”
如果没有推荐菜品，展示温和空状态：今天还没想好吃什么
```

第一版可暂时隐藏门店地址、营业时间、电话、地图等门店信息模块。

### 5.2 菜单页

菜单页定位：按分类浏览所有可选菜品。

当前可复用能力：

```text
goodsCategory 获取菜品分类
goods 获取菜品列表
左侧分类切换
右侧菜品列表滚动
点击菜品进入详情
```

页面展示内容：

```text
菜品分类
菜品图片
菜品名称
参考价格
```

交互要求：

```text
点击左侧分类，右侧滚动到对应分类
右侧滚动时同步选中左侧分类
点击菜品进入菜品详情页
```

第一版不要求在菜单列表直接加入今晚菜单，仍通过详情页加入，减少前端改动。

### 5.3 菜品详情页

菜品详情页定位：查看菜品信息，并加入今晚菜单。

当前可复用能力：

```text
goodsDetail 获取菜品详情
图片列表
规格选择
数量选择
加入本地购物车
```

页面展示内容：

```text
菜名
图片
参考价格
描述
规格/口味，若后端提供
数量
```

文案调整：

```text
购买数量 -> 想吃份数
加入购物车 -> 加入今晚菜单
加入购物车成功 -> 已加入今晚菜单
去结算 -> 去看看今晚吃啥
购买数量不能为0 -> 份数不能为0
请选择商品具体规格 -> 请选择口味或规格
```

业务要求：

```text
加入后写入本地当前今晚菜单
相同菜品和相同规格再次加入时数量累加
加入成功后不强制跳转，用户可继续浏览
```

现有本地存储 `shopCarInfo` 可继续复用为当前今晚菜单：

```text
shopCarInfo.shopList 当前今晚菜单明细
shopCarInfo.shopNum  当前已选份数
```

### 5.4 今晚吃啥页

今晚吃啥页由现有购物车页改造而来。

页面定位：展示今晚准备吃的菜品组合，不再承担电商购物车和付款结算职责。

当前可复用能力：

```text
读取本地 shopCarInfo
列表展示
左滑删除
数量增减
全选/删除
计算合计
```

页面展示内容：

```text
今晚吃啥
已选择菜品列表
菜品图片
菜名
规格/口味
份数
参考合计
```

文案调整：

```text
购物车空空如也～ -> 今晚还没选吃什么～
去选购美食 -> 去菜单看看
您选购的商品 -> 今晚想吃这些
合计 -> 参考合计
去结算 -> 就吃这些
删除 -> 删除
全选 -> 全选
```

交互要求：

```text
用户可删除菜品
用户可修改份数
用户可批量删除
点击“就吃这些”后生成一起吃过记录
生成成功后清空当前今晚菜单
生成成功后跳转到“我的 -> 一起吃过”或留在当前页展示成功提示
```

业务规则：

```text
未选择任何菜品时，不允许确认
确认时不再进入待付款订单页
确认时调用后端创建一起吃过记录接口
```

### 5.5 我的页

我的页定位：用户信息和生活记录入口。

现有我的页包含余额、订单、付款等商业信息，第一版需要弱化或移除。

页面展示内容：

```text
用户昵称/头像
一起吃过
偏好设置
不想吃清单
关于我们
```

第一版功能优先级：

```text
一起吃过：必做
偏好设置：可展示入口，功能可后续实现
不想吃清单：可展示入口，功能可后续实现
关于我们：可做简单静态页面或弹窗
```

文案调整：

```text
订单 -> 一起吃过
取餐号 -> 第几顿/记录编号
订单号 -> 记录编号
金额 -> 参考花费
订单状态 -> 记录状态
下单时间 -> 吃饭时间
商品列表 -> 菜品列表
立即付款 -> 移除
可用余额 -> 移除
```

### 5.6 一起吃过记录页

第一版可以先复用 `pages/my/index` 中的订单列表展示结构，也可以新增页面。为减少改动，建议第一版先在“我的”页直接展示最近的一起吃过记录。

记录展示字段：

```text
吃饭时间
菜品列表
每个菜品份数
备注
参考合计
```

可选扩展字段：

```text
这顿谁选的
是否喜欢
下次还吃
心情标签
照片
```

## 6. 后端需求

后端采用：

```text
Python
FastAPI
SQLAlchemy
PostgreSQL
Alembic
```

后端第一版提供 REST API 给微信小程序调用。接口语义应围绕“菜品、今晚菜单、一起吃过记录”，避免直接使用商城订单命名。

### 6.1 菜品分类

用于菜单页左侧分类。

数据字段：

```text
id
name
sort
is_active
created_at
updated_at
```

接口：

```text
GET /api/food-categories
```

返回按 `sort` 升序排列的有效分类。

### 6.2 菜品

用于首页推荐、菜单页、详情页。

数据字段：

```text
id
category_id
name
description
image_url
price
is_recommended
is_active
sort
created_at
updated_at
```

接口：

```text
GET /api/foods
GET /api/foods/{food_id}
```

查询参数：

```text
category_id
recommended
keyword
page
page_size
```

### 6.3 今晚菜单

第一版前端可优先使用本地存储维护当前今晚菜单；后端只需要在用户点击“就吃这些”时接收最终菜单并生成记录。

如后续需要跨设备同步，可增加今晚菜单接口：

```text
GET /api/dinner-plans/current
POST /api/dinner-plans/items
PATCH /api/dinner-plans/items/{item_id}
DELETE /api/dinner-plans/items/{item_id}
POST /api/dinner-plans/confirm
```

第一版最小接口：

```text
POST /api/eat-records
```

请求体示例：

```json
{
  "items": [
    {
      "food_id": 1,
      "food_name": "番茄炒蛋",
      "quantity": 1,
      "price": 18,
      "spec": "少油"
    }
  ],
  "remark": "今天想吃清淡点"
}
```

### 6.4 一起吃过记录

用于确认今晚菜单后的历史记录。

主表字段：

```text
id
user_id
eaten_at
remark
total_price
created_at
updated_at
```

明细字段：

```text
id
record_id
food_id
food_name
food_image_url
quantity
price
spec
created_at
```

接口：

```text
POST /api/eat-records
GET /api/eat-records
GET /api/eat-records/{record_id}
DELETE /api/eat-records/{record_id}
```

`POST /api/eat-records` 成功后返回记录详情，前端清空本地今晚菜单。

### 6.5 用户偏好

第一版可以先建表预留，不强制实现完整交互。

偏好设置：

```text
user_preference
id
user_id
taste_preference
spicy_level
notes
created_at
updated_at
```

不想吃清单：

```text
dislike_food
id
user_id
food_id
food_name
reason
created_at
updated_at
```

## 7. 数据库设计

第一版核心表：

```text
food_category        菜品分类
food                 菜品
eat_record           一起吃过记录主表
eat_record_item      一起吃过记录明细
```

可选预留表：

```text
dinner_plan          今晚菜单主表，后续跨设备同步使用
dinner_plan_item     今晚菜单明细，后续跨设备同步使用
user_preference      用户偏好
dislike_food         不想吃清单
```

第一版为了减少前后端复杂度，可以不落库保存未确认的今晚菜单，只在前端本地保存，确认后再写入 `eat_record` 和 `eat_record_item`。

## 8. 前端最小改造清单

### 8.1 必改文案

```text
app.json tabBar：购物车 -> 今晚吃啥
pages/index/index.wxml：店家推荐 -> 今日推荐
pages/shop-cart/index.json：购物车 -> 今晚吃啥
pages/template-cart/template-cart.wxml：购物车相关文案整体替换
pages/goods-details/index.wxml：购买/购物车/结算文案替换
pages/goods-details/index.js：toast 和校验文案替换
pages/my/index.wxml：订单和付款文案替换为一起吃过记录
```

### 8.2 必改逻辑

```text
首页标题固定为“一起吃饭叭”，不再依赖 mallName
点击“就吃这些”不再跳转 pages/to-pay-order/index
点击“就吃这些”调用后端创建一起吃过记录接口
创建成功后 wx.removeStorageSync('shopCarInfo')
隐藏或移除支付、余额、优惠券、配送、订单付款相关入口
```

### 8.3 可保留但暂不展示

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

这些页面可以先不从文件中删除，但应从 tab、按钮、列表入口中隐藏。

## 9. 核心业务流程

### 9.1 查看菜单

```text
用户进入菜单页
前端请求菜品分类
前端请求菜品列表
用户点击菜品
进入菜品详情
```

### 9.2 加入今晚菜单

```text
用户在菜品详情页选择份数/规格
点击“加入今晚菜单”
前端写入本地 shopCarInfo
提示“已加入今晚菜单”
用户可继续浏览菜品
```

### 9.3 查看今晚吃啥

```text
用户进入“今晚吃啥”
前端读取本地 shopCarInfo
展示今晚已选菜品
用户可删除或调整份数
```

### 9.4 确认今晚菜单

```text
用户点击“就吃这些”
前端校验至少选择一个菜品
前端提交菜品列表到 POST /api/eat-records
后端生成一起吃过记录
前端清空本地 shopCarInfo
前端提示“已记录这顿饭”
```

### 9.5 查看一起吃过

```text
用户进入“我的”
点击“一起吃过”
前端请求 GET /api/eat-records
展示历史吃饭记录和菜品明细
```

## 10. 验收标准

第一版验收标准：

```text
打开小程序后标题和主要文案为“一起吃饭叭”语境
首页能看到今日推荐菜品
菜单页能按分类浏览菜品
菜品详情能加入今晚菜单
今晚吃啥页能展示已选菜品
今晚吃啥页能删除和修改份数
点击“就吃这些”能生成一起吃过记录
生成记录后当前今晚菜单被清空
我的页能查看一起吃过记录
用户看不到支付、配送、优惠券、砍价、拼团等商业入口
```

## 11. 后续扩展

第一版稳定后可逐步扩展：

```text
随机帮我选
双方投票
不想吃清单参与推荐过滤
按最近吃过自动降权
菜品心情标签
一起吃过照片
家庭成员/情侣双人空间
周菜单
买菜清单
AI 推荐今晚吃什么
```

