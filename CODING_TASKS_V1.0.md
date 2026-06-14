# CODING_TASKS_V1.0

项目：韩国星际争霸团战数据自动采集与统计平台

版本：V1.0

状态：开发任务拆解版

------

# Sprint 0：项目初始化

------

## TASK-001

项目初始化

目标：

创建项目目录结构

产出：

```text
backend/
frontend/
crawler/
deployment/
docs/
```

验收：

项目可启动

------

## TASK-002

Docker开发环境

目标：

创建：

```text
docker-compose.yml
```

包含：

- PostgreSQL
- FastAPI
- Vue3

验收：

```bash
docker compose up -d
```

成功

------

## TASK-003

环境变量管理

目标：

创建：

```text
.env.example
```

验收：

项目支持环境变量启动

------

# Sprint 1：数据库

------

## TASK-004

创建Alembic

目标：

初始化Migration

验收：

```bash
alembic upgrade head
```

成功

------

## TASK-005

创建players表

来源：

DATABASE_V1.0

验收：

表结构一致

------

## TASK-006

创建teams表

验收：

表结构一致

------

## TASK-007

创建maps表

验收：

表结构一致

------

## TASK-008

创建matches表

验收：

表结构一致

------

## TASK-009

创建match_details表

验收：

表结构一致

------

## TASK-010

创建prizes表

验收：

表结构一致

------

## TASK-011

创建translation_rules表

验收：

表结构一致

------

## TASK-012

创建data_issues表

验收：

表结构一致

------

## TASK-013

创建raw_articles表

验收：

表结构一致

------

## TASK-014

创建全部索引

验收：

与DATABASE一致

------

# Sprint 2：翻译模块

------

## TASK-015

解析translate_rules.md

目标：

读取：

```text
translate_rules.md
```

验收：

成功加载全部规则

------

## TASK-016

导入translation_rules

验收：

数据库记录正确

------

## TASK-017

实现PlayerTranslator

接口：

```python
translate_player()
```

验收：

全部选手翻译成功

------

## TASK-018

实现MapTranslator

接口：

```python
translate_map()
```

验收：

全部地图翻译成功

------

# Sprint 3：ELOBOARD采集

------

## TASK-019

实现列表页采集

来源：

https://eloboard.com/men/bbs/board.php?bo_table=pro_league

验收：

获取最新wr_id

------

## TASK-020

实现文章详情采集

验收：

获取HTML

------

## TASK-021

保存raw_articles

验收：

HTML入库

------

## TASK-022

实现比赛解析器

验收：

识别：

- BO7
- KOF
- ACE

------

## TASK-023

解析选手信息

验收：

正确识别选手

------

## TASK-024

解析地图信息

验收：

正确识别地图

------

## TASK-025

解析奖金信息

验收：

正确识别奖金

------

## TASK-026

保存比赛数据

验收：

matches写入成功

------

## TASK-027

保存对局数据

验收：

match_details写入成功

------

## TASK-028

保存奖金数据

验收：

prizes写入成功

------

## TASK-029

实现幂等机制

验收：

重复采集无重复数据

------

# Sprint 4：历史回补

------

## TASK-030

实现历史扫描器

范围：

2026-01-01起

验收：

扫描成功

------

## TASK-031

实现批量回补

验收：

批量导入成功

------

## TASK-032

断点续传

验收：

支持恢复

------

# Sprint 5：统计服务

------

## TASK-033

玩家胜负统计

验收：

计算正确

------

## TASK-034

玩家胜率统计

验收：

计算正确

------

## TASK-035

玩家连胜统计

验收：

计算正确

------

## TASK-036

奖金统计

验收：

计算正确

------

## TASK-037

地图统计

验收：

计算正确

------

## TASK-038

排行榜统计

验收：

计算正确

------

# Sprint 6：API

------

## TASK-039

健康检查API

```text
GET /health
```

------

## TASK-040

比赛列表API

```text
GET /matches
```

------

## TASK-041

比赛详情API

```text
GET /matches/{id}
```

------

## TASK-042

选手列表API

```text
GET /players
```

------

## TASK-043

选手详情API

```text
GET /players/{id}
```

------

## TASK-044

队伍列表API

```text
GET /teams
```

------

## TASK-045

地图列表API

```text
GET /maps
```

------

## TASK-046

排行榜API

```text
GET /rankings
```

------

## TASK-047

奖金排行榜API

```text
GET /rankings/prize
```

------

# Sprint 7：后台管理

------

## TASK-048

管理员登录

------

## TASK-049

手动采集

------

## TASK-050

历史回补

------

## TASK-051

异常中心

------

## TASK-052

翻译规则管理

------

# Sprint 8：前端

------

## TASK-053

首页

------

## TASK-054

比赛列表页

------

## TASK-055

比赛详情页

------

## TASK-056

选手列表页

------

## TASK-057

选手详情页

------

## TASK-058

队伍页

------

## TASK-059

地图页

------

## TASK-060

排行榜页

------

# Sprint 9：部署

------

## TASK-061

Docker镜像构建

------

## TASK-062

Nginx配置

------

## TASK-063

SSL配置

------

## TASK-064

自动备份

------

## TASK-065

日志管理

------

# Sprint 10：测试验收

------

## TASK-066

执行AT-001 ~ AT-010

------

## TASK-067

执行AT-011 ~ AT-020

------

## TASK-068

执行AT-021 ~ AT-030

------

## TASK-069

性能测试

------

## TASK-070

上线验收

------

# 开发顺序

严格按照以下顺序执行：

```text
Sprint 0
↓
Sprint 1
↓
Sprint 2
↓
Sprint 3
↓
Sprint 4
↓
Sprint 5
↓
Sprint 6
↓
Sprint 7
↓
Sprint 8
↓
Sprint 9
↓
Sprint 10
```

禁止跳过依赖任务。

------

# V1最终交付物

```text
Docker部署环境

PostgreSQL数据库

ELOBOARD自动采集

历史数据回补

翻译规则系统

统计服务

REST API

后台管理系统

Vue3前端

生产环境部署
```

共计：

```text
70个开发任务
10个Sprint
```

预计开发周期：

```text
Claude Code / Codex
3~7天

人工开发
4~6周
```

