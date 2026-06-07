# backend-eat-records

目标：实现“就吃这些”后的记录创建、查询和删除。

## 最小任务

- [ ] 创建 `schemas/eat_record.py`：创建请求、明细请求、记录返回、分页返回 schema
- [ ] 创建 `services/eat_record_service.py`
- [ ] 实现 `EatRecordService.create_record`
- [ ] 校验 `user_id > 0`
- [ ] 校验 `items` 非空
- [ ] 校验每个明细 `quantity > 0`、`price >= 0`
- [ ] 计算 `total_price = sum(quantity * price)`
- [ ] `eaten_at` 使用服务端当前时间
- [ ] 在同一事务中写入 `eat_record` 和全部 `eat_record_item`
- [ ] 创建 `routers/eat_records.py`
- [ ] 实现 `POST /api/eat-records`
- [ ] 实现 `GET /api/eat-records`，要求 `user_id`，支持 `page`、`page_size`，按 `eaten_at desc` 排序
- [ ] 实现 `GET /api/eat-records/{id}`，只能查询指定 `user_id` 的记录
- [ ] 实现 `DELETE /api/eat-records/{id}`，只能删除指定 `user_id` 的记录
- [ ] 删除主表时级联删除明细
- [ ] 在 `app/main.py` 注册记录路由

## 验收

- [ ] 创建成功后返回完整记录和明细
- [ ] 任一明细写入失败时整笔记录回滚
- [ ] 查询只返回传入 `user_id` 的记录
- [ ] 删除其他 `user_id` 的记录会失败
