# 一起吃饭叭小程序后端详细设计

## 1. 设计目标

后端为“一起吃饭叭”微信小程序提供第一版 REST API，支持：

```text
菜品分类管理
菜品管理
banner 管理
一起吃过记录创建、查询、删除
小程序前端读取菜品、banner、记录
```

第一版不接微信登录，后端接受前端传入的固定 `user_id` 和 `person`。第一版不做支付、配送、优惠券、砍价、拼团、积分、余额。

## 2. 技术栈

```text
Python 3.11+
FastAPI
Uvicorn
SQLAlchemy 2.x
Alembic
PostgreSQL
Pydantic
Docker
Docker Compose
Nginx
```

## 3. 项目结构设计

建议后端目录：

```text
backend/
  app/
    main.py
    core/
      config.py
      database.py
      response.py
    models/
      food_category.py
      food.py
      banner.py
      eat_record.py
    schemas/
      food_category.py
      food.py
      banner.py
      eat_record.py
      common.py
    routers/
      food_categories.py
      foods.py
      banners.py
      eat_records.py
      admin.py
    services/
      eat_record_service.py
    migrations/
  alembic.ini
  requirements.txt
  Dockerfile
docker-compose.yml
nginx/
  default.conf
```

## 4. 统一接口规范

### 4.1 返回格式

所有接口统一返回：

```json
{
  "code": 0,
  "data": {},
  "message": ""
}
```

规则：

```text
code = 0      成功
code != 0    失败
message      失败原因或提示信息
data         成功数据，列表接口包含 items/total/page/page_size
```

### 4.2 分页格式

列表接口统一支持：

```text
page
page_size
```

分页返回：

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

### 4.3 时间格式

时间字段统一返回 ISO 8601 字符串：

```text
2026-05-16T12:30:00+08:00
```

数据库中使用 `timestamp with time zone`。

### 4.4 用户标识

第一版不接微信登录。

前端固定传：

```json
{
  "user_id": 1,
  "person": "default"
}
```

后端只做基础校验：

```text
user_id 必须存在且大于 0
person 可为空，默认 default
```

## 5. 数据库设计

### 5.1 ER 关系

```text
food_category 1 ---- n food
eat_record    1 ---- n eat_record_item
food          1 ---- n eat_record_item
```

`banner` 独立存储，可选关联菜品。

### 5.2 food_category 菜品分类表

用途：菜单页左侧分类和后台分类管理。

字段：

```text
id              bigserial primary key
name            varchar(64) not null
sort            integer not null default 0
is_active       boolean not null default true
created_at      timestamptz not null
updated_at      timestamptz not null
```

索引：

```text
idx_food_category_sort(sort)
idx_food_category_is_active(is_active)
```

约束：

```text
name 非空
sort 默认 0
```

删除策略：

```text
第一版删除分类采用软删除：is_active = false
如果分类下存在菜品，不物理删除
```

### 5.3 food 菜品表

用途：首页推荐、菜单列表、菜品详情和后台菜品管理。

字段：

```text
id              bigserial primary key
category_id     bigint references food_category(id)
name            varchar(128) not null
description     text
image_url       text
price           numeric(10,2) not null default 0
is_recommended  boolean not null default false
is_active       boolean not null default true
sort            integer not null default 0
created_at      timestamptz not null
updated_at      timestamptz not null
```

索引：

```text
idx_food_category_id(category_id)
idx_food_is_recommended(is_recommended)
idx_food_is_active(is_active)
idx_food_sort(sort)
idx_food_name(name)
```

约束：

```text
name 非空
price >= 0
```

删除策略：

```text
第一版删除菜品采用软删除：is_active = false
历史一起吃过记录保留 food_name、food_image_url、price 快照
```

图片策略：

```text
第一版使用 image_url 字段
上传图片接口接收图片后返回可访问 URL
如果暂不接对象存储，可先由部署服务提供静态文件目录
```

### 5.4 banner 表

用途：首页轮播图。

字段：

```text
id              bigserial primary key
title           varchar(128)
image_url       text not null
link_type       varchar(32) not null default 'none'
link_target     varchar(256)
sort            integer not null default 0
is_active       boolean not null default true
created_at      timestamptz not null
updated_at      timestamptz not null
```

`link_type` 可选值：

```text
none
food
url
```

第一版小程序只要求：

```text
none：点击不跳转
food：link_target 存 food_id，点击进入菜品详情
```

删除策略：

```text
软删除：is_active = false
```

### 5.5 eat_record 一起吃过记录主表

用途：保存一次确认的晚饭记录。

字段：

```text
id              bigserial primary key
user_id         bigint not null
person          varchar(64) not null default 'default'
eaten_at        timestamptz not null
remark          text
total_price     numeric(10,2) not null default 0
created_at      timestamptz not null
updated_at      timestamptz not null
```

索引：

```text
idx_eat_record_user_id(user_id)
idx_eat_record_eaten_at(eaten_at)
```

删除策略：

```text
第一版可物理删除 eat_record 及其明细
如果后续需要恢复能力，再改为软删除
```

### 5.6 eat_record_item 一起吃过记录明细表

用途：保存一次记录中的菜品快照。

字段：

```text
id              bigserial primary key
record_id       bigint not null references eat_record(id) on delete cascade
food_id         bigint references food(id)
food_name       varchar(128) not null
food_image_url  text
quantity        integer not null
price           numeric(10,2) not null default 0
spec            varchar(256)
created_at      timestamptz not null
```

索引：

```text
idx_eat_record_item_record_id(record_id)
idx_eat_record_item_food_id(food_id)
```

约束：

```text
quantity > 0
price >= 0
```

### 5.7 预留表

需求文档提到的以下表第一版可暂不建表，除非实现对应页面：

```text
dinner_plan
dinner_plan_item
user_preference
dislike_food
```

第一版未确认的今晚菜单只存在前端本地 `shopCarInfo`。

## 6. API 设计

### 6.1 菜品分类接口

#### 查询分类列表

```text
GET /api/food-categories
```

查询参数：

```text
include_inactive boolean 可选，默认 false
```

返回：

```json
{
  "code": 0,
  "data": [
    {
      "id": 1,
      "name": "家常菜",
      "sort": 1,
      "is_active": true,
      "created_at": "2026-05-16T12:00:00+08:00",
      "updated_at": "2026-05-16T12:00:00+08:00"
    }
  ],
  "message": ""
}
```

#### 新增分类

```text
POST /api/food-categories
```

请求：

```json
{
  "name": "家常菜",
  "sort": 1,
  "is_active": true
}
```

#### 修改分类

```text
PUT /api/food-categories/{id}
```

请求：

```json
{
  "name": "家常小炒",
  "sort": 2,
  "is_active": true
}
```

#### 删除分类

```text
DELETE /api/food-categories/{id}
```

行为：

```text
软删除，设置 is_active = false
```

### 6.2 菜品接口

#### 查询菜品列表

```text
GET /api/foods
```

查询参数：

```text
category_id
recommended
keyword
include_inactive
page
page_size
```

返回：

```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 1,
        "category_id": 1,
        "name": "番茄炒蛋",
        "description": "家常口味",
        "image_url": "https://example.com/tomato.jpg",
        "price": "18.00",
        "is_recommended": true,
        "is_active": true,
        "sort": 1
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20
  },
  "message": ""
}
```

#### 查询菜品详情

```text
GET /api/foods/{id}
```

#### 新增菜品

```text
POST /api/foods
```

请求：

```json
{
  "category_id": 1,
  "name": "番茄炒蛋",
  "description": "家常口味",
  "image_url": "https://example.com/tomato.jpg",
  "price": 18,
  "is_recommended": true,
  "is_active": true,
  "sort": 1
}
```

#### 修改菜品

```text
PUT /api/foods/{id}
```

#### 删除菜品

```text
DELETE /api/foods/{id}
```

行为：

```text
软删除，设置 is_active = false
```

#### 上传图片

```text
POST /api/foods/image
Content-Type: multipart/form-data
```

表单字段：

```text
file
```

返回：

```json
{
  "code": 0,
  "data": {
    "image_url": "/static/uploads/foods/xxx.jpg"
  },
  "message": ""
}
```

说明：第一版菜品表仍只保存 `image_url`，上传接口只负责返回 URL。

### 6.3 banner 接口

#### 查询 banner 列表

```text
GET /api/banners
```

查询参数：

```text
include_inactive boolean 可选，默认 false
```

返回：

```json
{
  "code": 0,
  "data": [
    {
      "id": 1,
      "title": "今晚吃点好的",
      "image_url": "https://example.com/banner.jpg",
      "link_type": "food",
      "link_target": "1",
      "sort": 1,
      "is_active": true
    }
  ],
  "message": ""
}
```

#### 新增 banner

```text
POST /api/banners
```

请求：

```json
{
  "title": "今晚吃点好的",
  "image_url": "https://example.com/banner.jpg",
  "link_type": "food",
  "link_target": "1",
  "sort": 1,
  "is_active": true
}
```

#### 修改 banner

```text
PUT /api/banners/{id}
```

#### 删除 banner

```text
DELETE /api/banners/{id}
```

行为：

```text
软删除，设置 is_active = false
```

### 6.4 一起吃过记录接口

#### 创建一起吃过记录

```text
POST /api/eat-records
```

请求：

```json
{
  "user_id": 1,
  "person": "default",
  "items": [
    {
      "food_id": 1,
      "food_name": "番茄炒蛋",
      "food_image_url": "https://example.com/tomato.jpg",
      "quantity": 1,
      "price": 18,
      "spec": ""
    }
  ],
  "remark": "今天想吃清淡点"
}
```

处理规则：

```text
校验 user_id > 0
校验 items 非空
校验每个 item.quantity > 0
计算 total_price = sum(quantity * price)
eaten_at 使用服务端当前时间
写入 eat_record 和 eat_record_item
返回完整记录
```

返回：

```json
{
  "code": 0,
  "data": {
    "id": 1,
    "user_id": 1,
    "person": "default",
    "eaten_at": "2026-05-16T18:30:00+08:00",
    "remark": "今天想吃清淡点",
    "total_price": "18.00",
    "items": [
      {
        "id": 1,
        "food_id": 1,
        "food_name": "番茄炒蛋",
        "food_image_url": "https://example.com/tomato.jpg",
        "quantity": 1,
        "price": "18.00",
        "spec": ""
      }
    ]
  },
  "message": ""
}
```

#### 查询一起吃过记录

```text
GET /api/eat-records
```

查询参数：

```text
user_id 必填
page
page_size
```

排序：

```text
eaten_at desc
```

#### 删除一起吃过记录

```text
DELETE /api/eat-records/{id}
```

查询参数：

```text
user_id 必填
```

行为：

```text
只能删除指定 user_id 下的记录
删除主表时级联删除明细
```

## 7. 后台管理设计

第一版后台为最简单的增删改查，可以直接使用 REST API，不要求单独管理后台页面。

管理能力：

```text
菜品分类：新增、修改、删除、查询
菜品：新增、修改、删除、查询、上传图片
banner：新增、修改、删除、查询
一起吃过记录：查询、删除
```

第一版不做管理员登录鉴权。如果部署到公网，建议先通过 Nginx basic auth 或内网访问限制保护管理接口。

## 8. 服务层设计

### 8.1 EatRecordService.create_record

职责：

```text
校验请求
计算总价
创建 eat_record
批量创建 eat_record_item
提交事务
返回记录详情
```

事务要求：

```text
主表和明细必须在同一数据库事务中写入
任一明细失败则整体回滚
```

### 8.2 CRUD 通用规则

```text
新增：写入 created_at、updated_at
修改：更新 updated_at
软删除：更新 is_active = false、updated_at
查询：默认只查 is_active = true
```

## 9. 环境配置

### 9.1 环境变量

```text
APP_NAME=yiqi-chifanba
APP_ENV=development
DEBUG=true
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/yiqi_chifanba
UPLOAD_DIR=/app/static/uploads
PUBLIC_STATIC_URL=/static
TZ=Asia/Shanghai
```

### 9.2 requirements.txt

```text
fastapi
uvicorn[standard]
sqlalchemy
psycopg[binary]
alembic
pydantic-settings
python-multipart
```

## 10. 部署设计

### 10.1 单机 Docker Compose

服务：

```text
api        FastAPI + Uvicorn
db         PostgreSQL
nginx      反向代理和静态文件
```

端口：

```text
80/443 -> nginx
8000   -> api 容器内部端口，不直接暴露公网
5432   -> db 容器内部端口，不直接暴露公网
```

### 10.2 docker-compose.yml 设计

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: yiqi_chifanba
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      TZ: Asia/Shanghai
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+psycopg://postgres:postgres@db:5432/yiqi_chifanba
      TZ: Asia/Shanghai
    depends_on:
      - db
    volumes:
      - uploads_data:/app/static/uploads
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  nginx:
    image: nginx:1.25
    ports:
      - "80:80"
    depends_on:
      - api
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
      - uploads_data:/usr/share/nginx/html/static/uploads:ro

volumes:
  postgres_data:
  uploads_data:
```

### 10.3 Nginx 配置

```nginx
server {
    listen 80;
    server_name _;

    location /api/ {
        proxy_pass http://api:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /usr/share/nginx/html/static/;
    }
}
```

正式上线微信小程序时，需要配置 HTTPS 域名。第一版开发联调可使用服务器 IP + FastAPI 或 Nginx。

## 11. 数据迁移与初始化

使用 Alembic 管理数据库结构。

初始化步骤：

```text
创建数据库表
插入默认菜品分类
插入默认菜品
插入默认 banner
```

示例默认分类：

```text
家常菜
主食
饮品
小吃
```

初始化数据仅用于开发测试，生产数据可通过 CRUD 接口维护。

## 12. 错误码设计

```text
0       成功
40001   参数错误
40004   数据不存在
40009   数据状态不可用
50000   服务器内部错误
```

错误返回示例：

```json
{
  "code": 40001,
  "data": null,
  "message": "items 不能为空"
}
```

## 13. 安全与限制

第一版限制：

```text
不接微信登录
不做管理员账号体系
不做复杂权限
```

最低安全措施：

```text
限制上传文件类型为 jpg/png/webp
限制上传文件大小
管理接口部署到公网时使用 Nginx basic auth 或 IP 白名单
数据库端口不暴露公网
错误信息不返回堆栈
```

## 14. 验收清单

```text
GET /api/food-categories 可查询分类
分类可新增、修改、删除
GET /api/foods 可查询菜品
菜品可新增、修改、删除
POST /api/foods/image 可上传图片并返回 image_url
GET /api/banners 可查询 banner
banner 可新增、修改、删除
POST /api/eat-records 可创建一起吃过记录
GET /api/eat-records 可查询指定 user_id 的记录
DELETE /api/eat-records/{id} 可删除指定 user_id 的记录
所有接口返回 { code, data, message }
Docker Compose 能启动 api、db、nginx
Nginx 能代理 /api 和访问 /static 上传图片
```

