# backend-deploy-seed

目标：完成第一版本地/单机部署配置和开发初始化数据。

## 最小任务

- [x] 创建 `backend/Dockerfile`
- [x] 创建根目录 `docker-compose.yml`，包含 `db`、`api`、`nginx`
- [x] 创建 `nginx/default.conf`，代理 `/api/` 到 FastAPI
- [x] 配置 `/static/` 访问上传图片目录
- [x] 确认数据库端口不暴露公网
- [x] 编写初始化脚本或命令，插入默认分类：家常菜、主食、饮品、小吃
- [x] 插入若干默认菜品，至少覆盖每个分类一个菜品
- [x] 插入至少一条默认 banner
- [x] 编写后端启动说明，包含迁移、初始化、启动命令
- [ ] 运行 Docker Compose 验证 api、db、nginx 可启动

## 验收

- [ ] Nginx 可访问 `/api/health`
- [ ] Nginx 可访问 `/static/uploads/...`
- [x] 默认数据能支撑首页、菜单页、详情页展示
- [x] 微信小程序开发环境可将 `apiBaseUrl` 指向后端服务
