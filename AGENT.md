# AGENT.md

# StarCraft Team Data Platform

韩国星际争霸团战数据自动采集与统计平台

------

# 1. Agent Role

你是本项目唯一的软件工程师。

你的职责：

- 阅读项目文档
- 设计代码
- 编写代码
- 编写测试
- 修复BUG
- 保持代码一致性

你必须严格遵循项目文档。

禁止自行修改业务规则。

------

# 2. Source of Truth

以下文档是项目唯一事实来源（Source of Truth）。

优先级从高到低：

```text
BUSINESS_RULES_V1.0.md

PRD_V1.3.md

DATABASE_V1.0.md

CRAWLER_SPEC_V1.0.md

API_SPEC_V1.0.md

TRANSLATE_RULES_SPEC_V1.1.md

DEPLOYMENT_V1.0.md

ACCEPTANCE_TEST_V1.0.md

CODING_TASKS_V1.0.md
```

如果发现冲突：

必须提出问题。

禁止自行猜测。

------

# 3. Development Rules

## Rule 1

禁止修改业务逻辑。

例如：

- 胜率公式
- 连胜规则
- ACE规则
- 奖金规则

全部以：

BUSINESS_RULES_V1.0

为准。

------

## Rule 2

禁止修改数据库结构。

必须严格遵循：

DATABASE_V1.0

------

## Rule 3

禁止增加未需求功能。

例如：

```text
AI战报

微信公众号推送

赛事预测

ELO系统

自动发文
```

全部禁止。

------

## Rule 4

禁止过度设计。

优先：

```text
简单

稳定

可维护
```

而不是：

```text
复杂

抽象

炫技
```

------

# 4. Tech Stack

必须使用：

## Backend

```text
Python 3.12

FastAPI

SQLAlchemy 2.x

Alembic

Pydantic v2
```

------

## Database

```text
PostgreSQL 17
```

------

## Frontend

```text
Vue3

Vite

Pinia

Element Plus

ECharts
```

------

## Crawler

```text
httpx

beautifulsoup4

tenacity
```

------

## Deployment

```text
Docker

Docker Compose

Nginx
```

------

# 5. Project Structure

必须使用：

```text
project/

├── backend/
│
├── frontend/
│
├── crawler/
│
├── deployment/
│
├── docs/
│
├── tests/
│
├── scripts/
│
├── translate_rules.md
│
└── AGENT.md
```

禁止随意增加目录。

------

# 6. Backend Architecture

采用：

```text
Router

↓

Service

↓

Repository

↓

Database
```

------

禁止：

```text
Router直接访问数据库
```

------

标准结构：

```text
app/

├── routers/
├── services/
├── repositories/
├── models/
├── schemas/
├── core/
└── utils/
```

------

# 7. Database Rules

必须：

```text
UUID作为业务ID

BIGSERIAL作为主键
```

------

所有表：

必须包含：

```sql
created_at

updated_at
```

------

禁止：

```text
SELECT *
```

------

必须明确字段。

------

# 8. API Rules

所有API：

统一返回：

```json
{
  "success": true,
  "data": {},
  "message": ""
}
```

------

错误返回：

```json
{
  "success": false,
  "error_code": "",
  "message": ""
}
```

------

禁止返回裸数据。

------

# 9. Logging Rules

必须记录：

```text
ERROR

WARNING

Crawler Failure

Database Failure
```

------

禁止：

```text
print()
```

------

使用：

```python
logging
```

------

# 10. Crawler Rules

严格遵循：

CRAWLER_SPEC_V1.0

------

必须支持：

```text
增量采集

历史回补

断点续传

幂等写入
```

------

禁止：

```text
重复数据
```

------

# 11. Translation Rules

严格遵循：

translate_rules.md

------

翻译优先级：

```text
translate_rules.md

↓

translation_rules

↓

原文
```

------

禁止：

```text
AI翻译选手

AI翻译地图
```

------

# 12. Testing Rules

所有新增代码：

必须包含测试。

------

最低覆盖率：

```text
80%
```

------

测试目录：

```text
tests/
```

------

必须包含：

```text
unit tests

integration tests
```

------

# 13. Migration Rules

数据库修改：

必须通过：

```bash
alembic revision
```

------

禁止：

```text
手工改库
```

------

# 14. Docker Rules

所有服务：

必须容器化。

------

开发环境：

```bash
docker compose up
```

即可启动。

------

禁止：

```text
依赖本机环境
```

------

# 15. Git Rules

一个Task：

对应：

```text
一个Commit

一个PR
```

------

Commit格式：

```text
feat:

fix:

refactor:

test:

docs:
```

------

示例：

```text
feat: add player statistics api

fix: duplicate prize insertion bug

docs: update crawler specification
```

------

# 16. Code Quality Rules

必须：

```text
类型注解

Docstring

Black格式化

Ruff检查
```

------

禁止：

```text
未使用代码

死代码

重复代码
```

------

# 17. Security Rules

禁止：

```text
硬编码密码

硬编码Token

硬编码数据库连接
```

------

全部使用：

```text
.env
```

------

# 18. Performance Targets

首页：

```text
< 2 秒
```

------

API：

```text
< 500ms
```

------

数据库查询：

```text
< 100ms
```

------

# 19. Acceptance Criteria

开发完成后：

必须通过：

```text
ACCEPTANCE_TEST_V1.0
```

全部测试。

------

要求：

```text
100%通过
```

------

# 20. Development Order

严格按照：

```text
CODING_TASKS_V1.0
```

执行。

顺序：

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

# 21. Definition of Done

任务完成必须满足：

```text
代码完成

测试通过

Lint通过

文档更新

Docker可运行
```

全部满足后才算完成。

------

# 22. Final Objective

构建：

韩国星际争霸职业团战数据库平台。

核心能力：

- 自动采集
- 自动翻译
- 数据沉淀
- 数据统计
- Web展示

长期稳定运行。

禁止偏离项目目标。