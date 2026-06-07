# 简单管理系统详细设计

## 1. 设计目标

管理系统用于维护“一起吃饭叭”小程序第一版测试和运营数据，包括：

```text
菜品分类管理
菜品管理
Banner 管理
一起吃过记录管理
```

第一版采用 FastAPI 内嵌后台页面：

```text
FastAPI 路由处理页面请求
Jinja2 渲染 HTML
Bootstrap 或简单 CSS 提供基础样式
SQLAlchemy AsyncSession 访问现有数据库
```

第一版不做后台登录、账号权限、审计日志、复杂筛选、批量导入导出，也不管理未确认的“今晚吃啥”本地菜单。

## 2. 技术栈与依赖

现有后端技术栈：

```text
Python 3.11+
FastAPI
SQLAlchemy 2.x asyncio
PostgreSQL
Pydantic
python-multipart
```

新增依赖：

```text
jinja2
```

说明：

```text
FastAPI 的 Jinja2Templates 需要 jinja2。
后台表单提交和图片上传依赖 python-multipart，当前项目已包含。
第一版样式可以使用 Bootstrap CDN；如部署环境不能访问 CDN，再改为本地 CSS。
```

## 3. 目录结构设计

在现有后端结构中增加后台路由和模板：

```text
backend/
  app/
    main.py
    routers/
      admin.py
    templates/
      admin/
        base.html
        index.html
        categories.html
        foods.html
        banners.html
        eat_records.html
        eat_record_detail.html
```

`backend/app/main.py` 注册后台路由：

```text
app.include_router(admin.router)
```

后台路由统一挂载在：

```text
/admin
```

## 4. 通用页面设计

### 4.1 基础模板 `base.html`

`base.html` 提供所有后台页面共用结构：

```text
HTML 基础结构
Bootstrap / 简单 CSS 引入
顶部导航
主内容容器
消息提示区
删除确认脚本
```

顶部导航包含：

```text
后台首页
菜品分类
菜品
Banner
一起吃过记录
```

页面变量约定：

```text
title       当前页面标题
active_nav  当前导航标识
message     成功提示，可为空
error       错误提示，可为空
```

### 4.2 表单交互

第一版不拆分复杂前端组件，使用 HTML 表单提交。

通用规则：

```text
新增和编辑可以使用同一页面中的表单
编辑通过 query 参数传入 edit_id 后回填表单
保存成功后重定向回列表页
失败时留在当前页面并展示错误提示
删除使用 POST 表单提交，不使用 DELETE HTML 方法
删除按钮必须有浏览器 confirm 二次确认
```

### 4.3 请求方法约定

页面展示：

```text
GET /admin
GET /admin/categories
GET /admin/foods
GET /admin/banners
GET /admin/eat-records
GET /admin/eat-records/{record_id}
```

表单提交：

```text
POST /admin/categories
POST /admin/categories/{category_id}/update
POST /admin/categories/{category_id}/delete

POST /admin/foods
POST /admin/foods/{food_id}/update
POST /admin/foods/{food_id}/delete

POST /admin/banners
POST /admin/banners/{banner_id}/update
POST /admin/banners/{banner_id}/delete

POST /admin/eat-records/{record_id}/delete
```

说明：

```text
后台页面请求不复用 /api 的 JSON 返回格式。
后台页面成功后返回 RedirectResponse。
后台页面失败时返回 HTML 模板并展示错误。
```

## 5. 数据访问设计

后台直接复用现有模型：

```text
FoodCategory
Food
Banner
EatRecord
EatRecordItem
```

后台直接使用现有数据库依赖：

```text
Depends(get_db)
```

排序规则：

```text
分类：FoodCategory.sort asc, FoodCategory.id asc
菜品：Food.sort asc, Food.id asc
Banner：Banner.sort asc, Banner.id asc
一起吃过记录：EatRecord.eaten_at desc, EatRecord.id desc
```

列表查询默认包含已软删除数据，方便管理员查看和恢复启用状态：

```text
分类列表展示 is_active true / false
菜品列表展示 is_active true / false
Banner 列表展示 is_active true / false
```

小程序现有 API 是否展示数据仍由现有 `include_inactive` 规则决定，后台不改变 `/api` 默认行为。

## 6. 后台首页设计

### 6.1 路由

```text
GET /admin
```

### 6.2 模板

```text
templates/admin/index.html
```

### 6.3 页面内容

展示四个管理入口：

```text
菜品分类管理 -> /admin/categories
菜品管理 -> /admin/foods
Banner 管理 -> /admin/banners
一起吃过记录 -> /admin/eat-records
```

每个入口展示简短说明：

```text
维护菜单分类
维护菜品、图片、推荐和上架状态
维护首页轮播图
查看和删除历史吃饭记录
```

## 7. 菜品分类管理设计

### 7.1 路由

```text
GET  /admin/categories
POST /admin/categories
POST /admin/categories/{category_id}/update
POST /admin/categories/{category_id}/delete
```

### 7.2 模板

```text
templates/admin/categories.html
```

### 7.3 查询逻辑

`GET /admin/categories`：

```text
查询所有 FoodCategory
按 sort asc, id asc 排序
如果 query 参数 edit_id 存在，查询对应分类作为编辑对象
渲染列表和表单
```

### 7.4 表单字段

```text
name       分类名称，必填，最长 64 字符
sort       排序值，整数，默认 0
is_active  是否启用，checkbox
```

### 7.5 新增逻辑

`POST /admin/categories`：

```text
读取表单字段
校验 name 非空且长度不超过 64
sort 为空时按 0 处理
is_active 根据 checkbox 转为 bool
创建 FoodCategory
提交事务
重定向到 /admin/categories?message=created
```

### 7.6 修改逻辑

`POST /admin/categories/{category_id}/update`：

```text
根据 category_id 查询 FoodCategory
不存在则展示错误
校验并更新 name、sort、is_active
提交事务
重定向到 /admin/categories?message=updated
```

### 7.7 删除逻辑

`POST /admin/categories/{category_id}/delete`：

```text
根据 category_id 查询 FoodCategory
不存在则展示错误
设置 is_active = false
提交事务
重定向到 /admin/categories?message=deleted
```

删除不检查分类下是否存在菜品，不物理删除分类。

## 8. 菜品管理设计

### 8.1 路由

```text
GET  /admin/foods
POST /admin/foods
POST /admin/foods/{food_id}/update
POST /admin/foods/{food_id}/delete
```

### 8.2 模板

```text
templates/admin/foods.html
```

### 8.3 查询逻辑

`GET /admin/foods`：

```text
查询所有 Food
按 sort asc, id asc 排序
查询所有 FoodCategory 作为分类下拉选项
如果 query 参数 edit_id 存在，查询对应菜品作为编辑对象
渲染列表和表单
```

菜品列表展示所属分类名称。实现时可以使用 `selectinload(Food.category)` 或单独查询分类后按 `category_id` 建立映射。

### 8.4 表单字段

```text
category_id       所属分类，可为空
name              菜品名称，必填，最长 128 字符
description       菜品描述，可为空
image_url         图片 URL，可为空
image_file        图片文件，可为空
price             参考价格，数字，默认 0，必须大于等于 0
is_recommended    是否推荐，checkbox
is_active         是否上架，checkbox
sort              排序值，整数，默认 0
```

### 8.5 图片处理

图片字段支持两种输入：

```text
填写 image_url
上传 image_file
```

处理优先级：

```text
如果上传了 image_file，保存上传文件并使用上传后的 URL。
如果没有上传 image_file，使用表单中的 image_url。
如果两者都为空，image_url 保存为空。
```

上传规则：

```text
允许 image/jpeg -> .jpg
允许 image/png  -> .png
允许 image/webp -> .webp
最大 5MB
保存到 settings.upload_dir
返回 URL 使用 settings.public_static_url
```

实现建议：

```text
将现有 foods.py 中图片上传校验和保存逻辑抽成函数，供 /api/foods/image 和后台菜品表单复用。
如果第一版不抽公共函数，也必须保持后台上传规则与 /api/foods/image 一致。
```

### 8.6 新增逻辑

`POST /admin/foods`：

```text
读取表单字段和上传文件
校验 name 非空且长度不超过 128
校验 price 大于等于 0
category_id 为空时保存为 None
sort 为空时按 0 处理
checkbox 转为 bool
处理图片，得到最终 image_url
创建 Food
提交事务
重定向到 /admin/foods?message=created
```

### 8.7 修改逻辑

`POST /admin/foods/{food_id}/update`：

```text
根据 food_id 查询 Food
不存在则展示错误
校验表单字段
如果上传了新图片，替换 image_url 为新图片 URL
如果没有上传新图片，使用表单 image_url
更新 category_id、name、description、image_url、price、is_recommended、is_active、sort
提交事务
重定向到 /admin/foods?message=updated
```

### 8.8 删除逻辑

`POST /admin/foods/{food_id}/delete`：

```text
根据 food_id 查询 Food
不存在则展示错误
设置 is_active = false
提交事务
重定向到 /admin/foods?message=deleted
```

删除不物理删除菜品，不删除历史记录中的快照数据。

## 9. Banner 管理设计

### 9.1 路由

```text
GET  /admin/banners
POST /admin/banners
POST /admin/banners/{banner_id}/update
POST /admin/banners/{banner_id}/delete
```

### 9.2 模板

```text
templates/admin/banners.html
```

### 9.3 查询逻辑

`GET /admin/banners`：

```text
查询所有 Banner
按 sort asc, id asc 排序
如果 query 参数 edit_id 存在，查询对应 banner 作为编辑对象
渲染列表和表单
```

### 9.4 表单字段

```text
title        标题，可为空，最长 128 字符
image_url    图片 URL，必填
link_type    跳转类型，none / food / url，默认 none
link_target  跳转目标，可为空，最长 256 字符
sort         排序值，整数，默认 0
is_active    是否启用，checkbox
```

### 9.5 校验规则

```text
image_url 必填
link_type 只能是 none、food、url
title 长度不超过 128
link_target 长度不超过 256
sort 为空时按 0 处理
```

link_type 规则：

```text
none：不要求 link_target
food：link_target 填写菜品 ID 字符串
url：link_target 填写 URL 字符串
```

第一版只做基础字段校验，不强制验证 food 类型的 link_target 一定对应存在的菜品。

### 9.6 新增逻辑

`POST /admin/banners`：

```text
读取表单字段
执行字段校验
创建 Banner
提交事务
重定向到 /admin/banners?message=created
```

### 9.7 修改逻辑

`POST /admin/banners/{banner_id}/update`：

```text
根据 banner_id 查询 Banner
不存在则展示错误
执行字段校验
更新 title、image_url、link_type、link_target、sort、is_active
提交事务
重定向到 /admin/banners?message=updated
```

### 9.8 删除逻辑

`POST /admin/banners/{banner_id}/delete`：

```text
根据 banner_id 查询 Banner
不存在则展示错误
设置 is_active = false
提交事务
重定向到 /admin/banners?message=deleted
```

## 10. 一起吃过记录管理设计

### 10.1 路由

```text
GET  /admin/eat-records
GET  /admin/eat-records/{record_id}
POST /admin/eat-records/{record_id}/delete
```

### 10.2 模板

```text
templates/admin/eat_records.html
templates/admin/eat_record_detail.html
```

### 10.3 查询用户规则

第一版默认查询测试用户：

```text
user_id = 1
```

页面支持 query 参数覆盖：

```text
/admin/eat-records?user_id=1
```

规则：

```text
user_id 为空时使用 1
user_id 必须是大于 0 的整数
详情和删除也必须带同一个 user_id，未传时默认 1
```

### 10.4 列表页逻辑

`GET /admin/eat-records`：

```text
解析 user_id
查询 EatRecord
使用 selectinload(EatRecord.items) 加载明细
按 eaten_at desc, id desc 排序
渲染历史记录列表
```

列表展示字段：

```text
记录 ID
用户 ID
人物标识 person
总价 total_price
吃饭时间 eaten_at
菜品数量 items 数量
创建时间 created_at
操作
```

操作：

```text
查看详情
删除
```

### 10.5 详情页逻辑

`GET /admin/eat-records/{record_id}`：

```text
解析 user_id，默认 1
查询指定 record_id 和 user_id 的 EatRecord
使用 selectinload(EatRecord.items) 加载明细
不存在则显示错误或返回列表页错误提示
渲染详情页
```

详情展示字段：

```text
记录 ID
用户 ID
人物标识 person
总价 total_price
吃饭时间 eaten_at
创建时间 created_at
更新时间 updated_at
```

明细展示字段：

```text
菜品 ID food_id
菜品名称 food_name
菜品图片 food_image_url
数量 quantity
单价 price
小计 quantity * price
```

### 10.6 删除逻辑

`POST /admin/eat-records/{record_id}/delete`：

```text
解析 user_id，默认 1
查询指定 record_id 和 user_id 的 EatRecord
不存在则展示错误
执行 db.delete(record)
提交事务
EatRecordItem 通过关系级联删除
重定向到 /admin/eat-records?user_id={user_id}&message=deleted
```

删除记录用于处理错误历史数据。第一版不提供恢复能力。

## 11. 表单解析与校验设计

后台页面可以使用 `Form` 和 `File` 直接接收字段。

布尔字段规则：

```text
checkbox 选中时为 true
checkbox 未选中时为 false
```

数字字段规则：

```text
sort 为空按 0 处理
price 为空按 0 处理
user_id 为空按 1 处理
非法数字展示表单错误
```

字符串字段规则：

```text
首尾空格应去除
必填字段去除空格后不能为空
可空字段去除空格后为空则保存 None
```

金额字段：

```text
使用 Decimal 解析 price
禁止负数
保存到 Food.price
```

## 12. 消息与错误设计

成功消息 query 参数：

```text
message=created  新增成功
message=updated  修改成功
message=deleted  删除成功
```

页面展示文案：

```text
created -> 保存成功
updated -> 更新成功
deleted -> 删除成功
```

错误处理：

```text
表单校验错误：当前页面顶部展示错误，保留已输入字段
记录不存在：展示“数据不存在”
数据库提交失败：回滚事务，展示“保存失败，请稍后再试”
图片格式错误：展示“只允许上传 jpg、png 或 webp 图片”
图片过大：展示“图片不能超过 5MB”
```

后台 HTML 页面不返回统一 JSON `ok/fail` 格式，避免和小程序 API 响应混用。

## 13. 与现有 API 的关系

后台页面和现有 `/api` 接口共享数据库和模型，但路由语义分离：

```text
/api/...     小程序 JSON API
/admin/...   管理后台 HTML 页面
```

后台保存分类、菜品、Banner 后，小程序接口读取同一份数据。

软删除后的影响：

```text
分类 is_active=false 后，/api/food-categories 默认不展示
菜品 is_active=false 后，/api/foods 默认不展示，/api/foods/{id} 返回不存在或已下架
Banner is_active=false 后，/api/banners 默认不展示
```

一起吃过记录删除后的影响：

```text
删除 EatRecord 后，对应 EatRecordItem 一并删除
/api/eat-records 不再返回该记录
```

## 14. 安全与部署约束

第一版后台无登录能力。

部署要求：

```text
仅在本地开发环境、内网环境或受信任环境使用
不要直接暴露到公网
如必须公网访问，应先增加反向代理鉴权、Basic Auth 或固定密码登录
```

第一版不记录操作人，不提供操作审计。

## 15. 验收场景

### 15.1 后台首页

```text
访问 /admin 可以打开后台首页
首页能跳转到分类、菜品、Banner、一起吃过记录页面
```

### 15.2 分类管理

```text
新增分类后列表出现新分类
修改分类名称、排序、启用状态后列表展示最新值
删除分类后 is_active 变为 false
/api/food-categories 默认不再返回已删除分类
```

### 15.3 菜品管理

```text
新增菜品后列表出现新菜品
填写图片 URL 后列表可以展示图片
上传 jpg、png、webp 图片后保存为可访问 URL
设置推荐后 /api/foods?recommended=true 可返回该菜品
设置下架或删除后 /api/foods 默认不再返回该菜品
修改价格、分类、描述、排序后列表展示最新值
```

### 15.4 Banner 管理

```text
新增 banner 后列表出现新 banner
修改图片、标题、跳转类型、跳转目标、排序、启用状态后列表展示最新值
删除 banner 后 is_active 变为 false
/api/banners 默认不再返回已删除 banner
```

### 15.5 一起吃过记录管理

```text
列表页能展示 user_id=1 的历史记录
详情页能展示某次记录和菜品明细
删除记录后列表不再展示该记录
/api/eat-records?user_id=1 不再返回已删除记录
```

### 15.6 整体回归

```text
现有 /api/health 正常
现有 /api/food-categories 正常
现有 /api/foods 正常
现有 /api/banners 正常
现有 /api/eat-records 正常
后台页面不影响已有测试通过
```

## 16. 后续扩展

后续可在本设计基础上扩展：

```text
后台登录
固定密码保护
操作日志
列表分页
按名称搜索菜品
按启用状态筛选
批量上下架
图片删除和预览增强
当前今晚菜单后端持久化
dinner_plan / dinner_plan_item 后台管理
```
