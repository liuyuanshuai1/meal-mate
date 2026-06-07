# backend-models-migrations

目标：完成第一版核心表结构、模型、时间字段和迁移。

## 最小任务

- [x] 初始化 Alembic：生成 `backend/alembic.ini` 与迁移目录
- [x] 定义通用时间字段策略：`created_at`、`updated_at` 使用带时区时间
- [x] 创建 `FoodCategory` 模型，对应 `food_category`
- [x] 创建 `Food` 模型，对应 `food`
- [x] 创建 `Banner` 模型，对应 `banner`
- [x] 创建 `EatRecord` 模型，对应 `eat_record`
- [x] 创建 `EatRecordItem` 模型，对应 `eat_record_item`
- [x] 配置关系：`food_category 1:n food`，`eat_record 1:n eat_record_item`，`food 1:n eat_record_item`
- [x] 添加约束：分类名非空、菜品名非空、价格不小于 0、记录明细数量大于 0
- [x] 添加索引：分类排序/启用、菜品分类/推荐/启用/排序/名称、记录用户/时间、记录明细 record_id/food_id
- [x] 生成首个 Alembic 迁移文件
- [x] 执行迁移并确认数据库表创建成功

## 验收

- [x] Alembic 能从空库迁移出所有核心表
- [x] `eat_record_item.record_id` 删除主表时级联删除
- [x] 预留表 `dinner_plan`、`user_preference`、`dislike_food` 第一版不创建
