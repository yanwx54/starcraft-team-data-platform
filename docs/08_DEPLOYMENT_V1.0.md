# DEPLOYMENT_V1.0

## 项目

韩国星际争霸团战数据自动采集与统计平台

版本：V1.0

------

# 1. 部署目标

采用Docker容器化部署。

实现：

- 一键部署
- 快速升级
- 自动重启
- 数据持久化
- 日志集中管理

------

# 2. 服务器信息

## 生产服务器

IP：

199.180.116.188

操作系统建议：

Ubuntu 24.04 LTS

最低配置：

CPU：4 Core

内存：8GB

硬盘：100GB SSD

推荐配置：

CPU：8 Core

内存：16GB

硬盘：200GB SSD

------

# 3. 技术架构

```text
Internet
    ↓
Nginx
    ↓
Vue3 Frontend
    ↓
FastAPI Backend
    ↓
PostgreSQL
```

------

# 4. Docker容器规划

| 容器   | 名称            |
| ------ | --------------- |
| 前端   | starcraft-web   |
| 后端   | starcraft-api   |
| 数据库 | starcraft-db    |
| Nginx  | starcraft-nginx |

------

# 5. 目录结构

```text
/opt/starcraft/

├── frontend/
├── backend/
├── database/
├── nginx/

├── logs/
│   ├── api/
│   ├── crawler/
│   └── nginx/

├── backups/

└── docker-compose.yml
```

------

# 6. PostgreSQL

数据库：

starcraft

用户：

starcraft

端口：

5432

------

## 数据持久化

挂载：

```text
/opt/starcraft/database
```

------

## 自动备份

执行时间：

每天凌晨03:00

保留：

30天

------

备份文件：

```text
starcraft_YYYYMMDD.sql.gz
```

------

# 7. FastAPI

容器：

```text
starcraft-api
```

端口：

```text
8000
```

------

环境变量：

```text
DATABASE_URL

OPENAI_API_KEY

TRANSLATION_PROVIDER

ENVIRONMENT
```

------

启动方式：

```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000
```

------

# 8. Vue3

容器：

```text
starcraft-web
```

------

构建：

```bash
npm run build
```

------

部署：

```text
/usr/share/nginx/html
```

------

# 9. Nginx

容器：

```text
starcraft-nginx
```

------

开放端口：

```text
80
443
```

------

反向代理：

```text
/api
→
FastAPI
```

------

静态资源：

```text
/
→
Vue3
```

------

# 10. SSL

建议：

Let's Encrypt

------

自动续期：

```bash
certbot renew
```

------

# 11. Docker Compose

服务：

```text
nginx

frontend

backend

postgres
```

------

启动：

```bash
docker compose up -d
```

------

关闭：

```bash
docker compose down
```

------

# 12. 日志管理

日志目录：

```text
/opt/starcraft/logs
```

------

保留：

90天

------

日志级别：

```text
INFO
WARNING
ERROR
```

------

# 13. 监控

健康检查接口：

```text
/api/v1/health
```

------

检查内容：

- API状态
- 数据库状态
- 爬虫状态

------

# 14. 更新流程

步骤：

```text
拉取代码

停止容器

构建镜像

启动容器

执行Migration

验证健康检查
```

------

# 15. 灾难恢复

恢复顺序：

```text
PostgreSQL

Backend

Frontend

Nginx
```

------

最大恢复时间目标：

```text
RTO ≤ 30分钟
```

------

最大数据丢失：

```text
RPO ≤ 24小时
```