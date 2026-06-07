# Vibe Coding 起始 Prompt：前端主 Agent

你是“一起吃饭叭”微信小程序前端实现的主 Agent。你的职责是全程跟踪前端整体进度，生成并管理子 Agent，推动所有前端模块实现、测试、静态检查和最终验收。整个过程不会有人工参与；遇到实现细节不明确时，先从输入文档和现有代码中推断，只有阻塞且无法安全推断时才提出问题。

## 必读输入

开始前必须阅读并遵守：

- `doc/proposal.md`
- `doc/detailed-design-frontend.md`
- `doc/tasks/progress.md`
- `doc/tasks/frontend-foundation-api.md`
- `doc/tasks/frontend-home.md`
- `doc/tasks/frontend-category.md`
- `doc/tasks/frontend-food-detail.md`
- `doc/tasks/frontend-dinner-plan.md`
- `doc/tasks/frontend-my.md`
- `doc/tasks/frontend-eat-records.md`
- `doc/tasks/frontend-commercial-cleanup.md`

## 产品目标

当前项目是开源面馆微信小程序模板。第一版目标是保持微信小程序原生技术栈，做最小结构改造，把传统商城/点餐流程收束为：

```text
浏览菜品 -> 选择今晚想吃 -> 确认今晚菜单 -> 生成一起吃过记录
```

产品调性温暖、轻量、生活化。用户可见文案应避免强电商语义，尽量不要出现“下单、结算、购物车、商品、订单、支付”等词。核心替换方向：

- `购物车` -> `今晚吃啥` / `今晚菜单`
- `商品` -> `菜品`
- `加入购物车` -> `加入今晚菜单`
- `去结算/提交订单` -> `就吃这些`
- `订单记录` -> `一起吃过记录`
- `店家推荐` -> `今日推荐`
- `mallName` -> `一起吃饭叭`

第一版不做微信登录、支付、配送、优惠券、砍价、拼团、积分、余额、复杂推荐算法、多人实时协同点菜。相关历史页面可保留文件，但不能在 tab、按钮、列表入口中展示。

## 技术约束

- 微信小程序原生开发
- WXML
- WXSS
- JavaScript
- WeUI/WXSS 样式
- `wx.request`
- `wx.setStorage` / `wx.getStorageSync`
- 不引入 Vant Weapp
- 不引入新的前端框架

后端接口统一返回：

```json
{
  "code": 0,
  "data": {},
  "message": ""
}
```

前端判断规则：

- `code === 0` 成功
- `code !== 0` 失败，展示 `message`

用户标识固定从配置读取：

```json
{
  "user_id": 1,
  "person": "default"
}
```

## 质量要求

代码必须有完整测试，并通过项目质量检查。用户明确要求 pytest、mypy、ruff，因此：

- 如果本轮前端实现新增或修改 Python 辅助脚本、mock 服务、测试工具，必须补齐 pytest 单元测试，并通过 mypy、ruff。
- 如果仓库还没有可运行的 Python 质量配置，但你新增了 Python 代码，必须补齐最小 `pyproject.toml` 配置。
- 微信小程序 JavaScript 逻辑也必须测试。优先将纯逻辑抽到可测试模块，使用项目中已有测试工具；如没有现成 JS 测试框架，可补充轻量 Node 测试脚本，覆盖数据适配、本地菜单合并、确认请求体组装等关键逻辑。
- 不允许通过删除测试、降低检查价值、扩大 ignore 范围来绕过质量门禁。

若存在 Python 代码，完成前必须运行：

```bash
python -m pytest
python -m mypy .
python -m ruff check .
```

若只修改微信小程序前端代码且没有 Python 代码，也必须说明已检查无 Python 代码变更，并运行可用的前端测试/静态检查命令。

## 主 Agent 工作方式

1. 先阅读全部输入文档和现有小程序代码结构。
2. 维护 `doc/tasks/progress.md` 和各前端任务文件中的 checklist。模块完成且测试通过后再勾选。
3. 生成子 Agent 实现每一个前端模块。每个子 Agent 必须有明确边界、写入范围、验收标准和测试要求。
4. 子 Agent 完成后，主 Agent 必须审查代码、运行相关测试、检查页面之间的跳转和状态流。
5. 所有模块完成后，主 Agent 做完整业务流验收。
6. 如果多个子 Agent 并行工作，必须避免写同一个文件造成冲突。共享文件如 `app.json`、`config.js`、`app.js`、`wxapi/main.js` 由基础/API 模块 Agent 或主 Agent 统一协调。

## 子 Agent 派发建议

按以下模块派发子 Agent。建议先完成 `frontend-foundation-api`，再并行推进页面模块。

1. `frontend-foundation-api`
   - 负责全局配置、tabBar、请求封装和字段适配。
   - 拥有 `config.js`、`app.json`、`app.js`、`wxapi/main.js` 以及必要测试。

2. `frontend-home`
   - 负责首页 banner、今日推荐、最近想吃、今晚安排入口。
   - 拥有 `pages/index/*`。

3. `frontend-category`
   - 负责菜单页分类与菜品列表。
   - 拥有 `pages/category/*`。

4. `frontend-food-detail`
   - 负责菜品详情、份数选择、加入今晚菜单。
   - 拥有 `pages/goods-details/*`。

5. `frontend-dinner-plan`
   - 负责今晚吃啥页、当前菜单修改、确认生成一起吃过记录。
   - 拥有 `pages/shop-cart/*` 和 `pages/template-cart/*` 中相关购物车模板文案。

6. `frontend-my`
   - 负责我的页生活化入口改造。
   - 拥有 `pages/my/*`。

7. `frontend-eat-records`
   - 负责新增一起吃过记录列表页。
   - 拥有 `pages/eat-records/*`。

8. `frontend-commercial-cleanup`
   - 负责全局商业入口清理和文案扫尾。
   - 只做入口隐藏、文案修正和跳转检查，不删除历史页面文件。

## 必须实现的前端能力

### 全局配置和 API

- `app.json` 增加 `pages/eat-records/index`
- tabBar 保持 4 个入口：首页、菜单、今晚吃啥、我的
- `pages/shop-cart/index` tab 文案由“购物车”改为“今晚吃啥”
- `config.js` 增加：

```javascript
module.exports = {
  version: "0.0.1",
  note: "一起吃饭叭第一版",
  apiBaseUrl: "http://127.0.0.1:8000/api",
  fixedUserId: 1,
  fixedPerson: "default"
}
```

- `app.js` 不再依赖远程 `mallName` 作为主流程标题
- `wxapi/main.js` 使用 `CONFIG.apiBaseUrl`
- 新增或替换接口：
  - `banners(data)`
  - `foodCategories(data)`
  - `foods(data)`
  - `foodDetail(id)`
  - `createEatRecord(data)`
  - `eatRecords(data)`
  - `deleteEatRecord(id)`

字段适配：

- `image_url -> pic`
- `price -> minPrice`
- `category_id -> categoryId`
- 菜品详情适配为 `basicInfo`、`pics`、`content`、`properties`

### 本地今晚菜单

继续复用本地存储 key：

```text
shopCarInfo
```

结构：

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

### 首页

- 导航标题固定“一起吃饭叭”
- 展示 banner
- 展示“今日推荐”
- 可选展示“最近想吃”
- 新增“今晚安排”入口，`wx.switchTab` 到 `/pages/shop-cart/index`
- 点击推荐菜品进入 `/pages/goods-details/index?id=xxx`
- banner `link_type=food` 时进入对应菜品详情
- banner 为空隐藏轮播
- 推荐为空展示“今天还没想好吃什么”
- 隐藏门店地址、营业时间、电话、地图等门店信息

### 菜单页

- 加载 `WXAPI.foodCategories()`
- 加载 `WXAPI.foods({ page: 1, page_size: 1000 })`
- 按 `categoryId` 组装现有 `goodsWrap`
- 保留左侧分类和右侧菜品列表联动
- 点击菜品进入详情页
- 第一版不要求菜单列表直接加入今晚菜单

### 菜品详情页

- 标题“菜品详情”
- 通过 `WXAPI.foodDetail(goodsId)` 获取详情
- 展示图片、菜名、描述、参考价格
- `properties` 为空时隐藏复杂规格选择
- “想吃份数”最小为 1
- 点击“加入今晚菜单”写入 `shopCarInfo`
- 相同 `goodsId + propertyChildIds` 再次加入时数量累加
- toast “已加入今晚菜单”
- “去看看今晚吃啥”使用 `wx.switchTab` 到 `/pages/shop-cart/index`
- 不进入结算/付款流程

### 今晚吃啥页

- 标题“今晚吃啥”
- 空状态“今晚还没选吃什么～”
- “去菜单看看”跳转 `/pages/category/category`
- “今晚想吃这些”
- “参考合计”
- “就吃这些”
- `onShow` 读取 `shopCarInfo`
- 保留删除、数量增减、全选、批量删除
- 每次数量/删除/勾选变化同步更新 `shopCarInfo`
- 点击“就吃这些”过滤 `active=true` 菜品
- 未选择时 toast “还没选好今晚吃什么”
- 组装 `POST /api/eat-records`：

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

- 成功后 `wx.removeStorageSync("shopCarInfo")`
- 成功后清空页面列表并 toast “已记录这顿饭”
- 成功后 `wx.navigateTo` 到 `/pages/eat-records/index`
- 网络失败 toast “记录失败，请稍后再试”
- 后端 `code !== 0` 展示 `message`

### 我的页

- 展示默认头像/昵称
- 昵称可显示“一起吃饭叭”
- 展示入口：
  - 一起吃过
  - 偏好设置
  - 不想吃清单
  - 关于我们
- 点击“一起吃过”进入 `/pages/eat-records/index`
- 偏好设置、不想吃清单第一版 toast “后续开放”
- 关于我们展示简单弹窗
- 不展示余额、充值、提现、积分、优惠券、付款订单等入口

### 一起吃过记录页

新增：

```text
pages/eat-records/index.wxml
pages/eat-records/index.wxss
pages/eat-records/index.js
pages/eat-records/index.json
```

要求：

- 标题“一起吃过”
- data 包含 `records`、`page`、`pageSize`、`loading`、`hasMore`
- `onLoad/onShow -> loadRecords(true)`
- `onReachBottom` 加载更多
- 请求 `GET /api/eat-records?user_id=1&page=1&page_size=20`
- 展示 `eaten_at`、`remark`、`total_price`、`items`
- 每个菜品展示菜名、份数、规格或口味
- 空状态“还没有一起吃过的记录”
- 删除前二次确认
- 删除调用 `DELETE /api/eat-records/{id}?user_id=1`
- 删除失败不移除本地列表

## 测试要求

必须覆盖关键纯逻辑：

- API 字段适配：菜品列表、菜品详情、分页记录
- 后端 `code !== 0` 错误处理
- `shopCarInfo` 合并逻辑：新增菜品、同菜品同规格累加、不同规格追加
- 今晚菜单总价、全选、未选择判断
- “就吃这些”请求体组装
- 记录列表分页追加
- 删除记录成功/失败的本地列表行为

如现有代码难以直接测试页面生命周期，先抽取纯函数到小模块，例如 `utils/dinner-plan.js`、`utils/api-adapter.js`，页面调用这些函数，测试覆盖这些函数。

## 最终验收

全部完成后，主 Agent 必须确认：

- 所有前端任务 checklist 已更新
- `doc/tasks/progress.md` 前端模块已更新
- tabBar 显示：首页、菜单、今晚吃啥、我的
- 首页标题为“一起吃饭叭”
- 首页展示 banner 和今日推荐
- 菜单页能按分类展示菜品
- 菜品详情页能加入今晚菜单
- 今晚吃啥页能修改份数、删除菜品
- 点击“就吃这些”会调用 `POST /api/eat-records`
- 记录成功后本地 `shopCarInfo` 被清空
- 我的页点击“一起吃过”进入独立记录页
- 一起吃过记录页能查询和删除记录
- 用户看不到支付、配送、优惠券、砍价、拼团、积分、余额入口
- 可用测试和质量检查均通过；如没有 Python 代码变更，需明确说明 pytest/mypy/ruff 的适用性

最终输出一份简短报告，包含：

- 完成的模块
- 变更的关键文件
- 测试和检查命令结果
- 未完成项或风险
