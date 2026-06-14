# StarCraft Team Data Platform (STDP)

韩国星际争霸团战数据自动采集与统计平台

## 项目简介

本平台是一个长期稳定运行的电竞数据平台，专注于韩国星际争霸（StarCraft: Remastered）职业团战赛事数据的自动采集、翻译、存储、统计与展示。

**数据来源**：[ELOBOARD 职业团战专区](https://eloboard.com/men/bbs/board.php?bo_table=pro_league)

## 核心功能

- **自动采集** — 每日定时抓取 ELOBOARD 最新团战数据（10:00 / 10:30 / 11:00 / 12:00）
- **自动翻译** — 韩文选手名、地图名、队伍名自动转中文
- **结构化存储** — PostgreSQL 统一管理，wr_id 唯一标识，数据冻结原则
- **数据统计** — 胜负统计、连胜统计、奖金统计、地图胜率、排行榜
- **Web 展示** — 首页、选手页、队伍页、地图页、排行榜页
- **后台管理** — 手动采集、历史回补、异常处理、翻译规则管理

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue3 + Vite + Pinia + Element Plus + ECharts |
| 后端 | Python 3.12 + FastAPI + SQLAlchemy 2.x + Alembic + Pydantic v2 |
| 数据库 | PostgreSQL 17 |
| 爬虫 | httpx + BeautifulSoup4 + tenacity |
| 部署 | Docker + Docker Compose + Nginx |

## 项目结构

```
project/
├── backend/          # FastAPI 后端
├── frontend/         # Vue3 前端
├── crawler/          # 爬虫模块
├── deployment/       # 部署配置
├── docs/             # 项目文档
├── tests/            # 测试
├── scripts/          # 脚本
├── translate_rules.md # 翻译规则
└── AGENT.md          # 开发规范
```

## 后端架构

```
Router → Service → Repository → Database
```

```
app/
├── routers/
├── services/
├── repositories/
├── models/
├── schemas/
├── core/
└── utils/
```

## 数据库表

| 表名 | 说明 |
|------|------|
| raw_articles | ELOBOARD 原始 HTML 存档 |
| seasons | 赛季 |
| maps | 地图 |
| season_maps | 赛季地图池 |
| teams | 队伍 |
| players | 选手 |
| player_aliases | 选手别名 |
| player_team_history | 转队历史 |
| matches | 团战主表 |
| match_stages | 团战阶段（BO7/KOF/ACE） |
| match_details | 对局明细 |
| prize_pool | 奖金 |
| crawl_log | 采集日志 |
| data_issues | 数据异常中心 |

## API 概览

Base URL: `/api/v1`

| 模块 | 路径 | 说明 |
|------|------|------|
| 首页 | `/dashboard/summary` | 统计概览 |
| 比赛 | `/matches` | 比赛列表/详情 |
| 选手 | `/players` | 选手列表/详情/战绩/奖金 |
| 队伍 | `/teams` | 队伍列表/详情 |
| 地图 | `/maps` | 地图列表/胜率 |
| 赛季 | `/seasons` | 赛季列表/排行 |
| 排行 | `/rankings` | 胜场/胜率/奖金/连胜排行 |
| 搜索 | `/search` | 全局搜索 |
| 后台 | `/admin/crawler/run` | 手动采集/回补 |
| 异常 | `/admin/issues` | 数据异常管理 |
| 翻译 | `/admin/translations` | 翻译规则管理 |
| 健康 | `/health` | 服务状态检查 |

## 快速开始

### 环境要求

- Docker & Docker Compose
- Python 3.12+
- Node.js 18+

### 启动开发环境

```bash
# 克隆项目
git clone <repository-url>
cd Project01_starcraft-team_data_platform

# 启动所有服务
docker compose up -d
```

### 环境变量

复制 `.env.example` 并填写配置：

```env
DATABASE_URL=postgresql://starcraft:password@localhost:5432/starcraft
OPENAI_API_KEY=your-api-key
TRANSLATION_PROVIDER=openai
ENVIRONMENT=development
```

### 数据库迁移

```bash
alembic upgrade head
```

## 爬虫模块

```
Scheduler → ListCrawler → ArticleCrawler → HtmlArchive → Parser → Translator → DatabaseWriter → StatisticsRefresh
```

- **增量采集**：基于 wr_id 去重，仅采集新文章
- **历史回补**：支持按日期范围 / wr_id 范围批量导入（2026-01-01 起）
- **断点续传**：回补过程支持中断恢复
- **幂等写入**：重复执行不产生重复数据
- **数据冻结**：首次采集后不覆盖，即使源站修改
- **异常记录**：未识别选手/地图/奖金异常自动进入 data_issues

## 部署

- **服务器**：Ubuntu 24.04 LTS
- **容器**：starcraft-nginx / starcraft-web / starcraft-api / starcraft-db
- **数据库备份**：每日 03:00 自动备份，保留 30 天
- **SSL**：Let's Encrypt + certbot 自动续期
- **日志**：保留 90 天

```bash
# 生产部署
docker compose up -d

# 更新流程
git pull
docker compose down
docker compose build
docker compose up -d
alembic upgrade head
```

## 项目文档

| 文档 | 说明 |
|------|------|
| [01_PROJECT_OVERVIEW.md](docs/01_PROJECT_OVERVIEW.md) | 项目概述 |
| [02_PRD_V1.3.md](docs/02_PRD_V1.3.md.md) | 产品需求文档 |
| [03_BUSINESS_RULES_V1.0.md](docs/03_BUSINESS_RULES_V1.0.md) | 业务规则 |
| [04_DATABASE_V1.0.md](docs/04_DATABASE_V1.0.md) | 数据库设计 |
| [05_API_SPEC_V1.0.md](docs/05_API_SPEC_V1.0.md) | API 规范 |
| [06_CRAWLER_SPEC_V1.0.md](docs/06_CRAWLER_SPEC_V1.0.md) | 爬虫规范 |
| [07_TRANSLATE_RULES_SPEC.md](docs/07_TRANSLATE_RULES_SPEC.md) | 翻译规则规范 |
| [08_DEPLOYMENT_V1.0.md](docs/08_DEPLOYMENT_V1.0.md) | 部署方案 |
| [09_ACCEPTANCE_TEST_V1.0.md](docs/09_ACCEPTANCE_TEST_V1.0.md) | 验收测试 |

## 开发规范

详见 [AGENT.md](AGENT.md)，核心规则：

- 严格遵循项目文档，禁止自行修改业务规则
- 禁止增加未需求功能（AI 战报、公众号推送、赛事预测、Elo 系统等）
- 一个 Task 对应一个 Commit + 一个 PR
- Commit 格式：`feat:` / `fix:` / `refactor:` / `test:` / `docs:`
- 代码必须包含类型注解、Docstring、测试（覆盖率 >= 80%）
- 禁止 `print()`，使用 `logging`
- 禁止硬编码密码/Token，使用 `.env`
- 所有服务必须容器化

## 性能目标

| 指标 | 目标 |
|------|------|
| 首页加载 | < 2 秒 |
| API 响应 | < 500ms |
| 数据库查询 | < 100ms |
| 采集成功率 | >= 99% |
| 数据重复率 | 0 |

## 项目愿景

构建中文社区最完整的韩国星际争霸职业团战数据平台，为未来扩展奠定基础：

- Elo 评级系统
- 比赛预测系统
- 战绩分析系统
- 数据开放平台
