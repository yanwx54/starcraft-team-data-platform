# API_SPEC_V1.0

## 项目

韩国星际争霸团战数据自动采集与统计平台

------

# 1. API规范

## Base URL

```text
/api/v1
```

------

## 返回格式

成功：

```json
{
  "success": true,
  "data": {},
  "message": ""
}
```

失败：

```json
{
  "success": false,
  "message": "error message"
}
```

------

## 分页格式

```json
{
  "items": [],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

------

# 2. 首页接口

## 首页统计

### GET

```http
/api/v1/dashboard/summary
```

------

返回：

```json
{
  "total_matches": 1000,
  "total_players": 300,
  "total_teams": 20,
  "latest_match_date": "2026-06-01"
}
```

------

## 最新比赛

### GET

```http
/api/v1/dashboard/latest-matches
```

参数：

```text
limit
```

默认：

```text
10
```

------

## 奖金排行榜

### GET

```http
/api/v1/dashboard/prize-ranking
```

参数：

```text
limit
```

默认：

```text
20
```

------

## 连胜排行榜

### GET

```http
/api/v1/dashboard/win-streak-ranking
```

参数：

```text
limit
```

------

# 3. 比赛接口

## 比赛列表

### GET

```http
/api/v1/matches
```

查询参数：

```text
page
page_size
season_id
date_from
date_to
team_id
```

------

返回：

```json
{
  "items": [
    {
      "id": 1,
      "wr_id": 2455,
      "title": "...",
      "match_date": "2026-06-01"
    }
  ]
}
```

------

## 比赛详情

### GET

```http
/api/v1/matches/{id}
```

返回：

```json
{
  "match": {},
  "teams": [],
  "stages": [],
  "games": [],
  "prizes": []
}
```

------

## 比赛阶段

### GET

```http
/api/v1/matches/{id}/stages
```

------

返回：

```json
[
  {
    "stage_type": "BO7",
    "winner_team_id": 1
  }
]
```

------

# 4. 选手接口

## 选手列表

### GET

```http
/api/v1/players
```

参数：

```text
page
page_size
keyword
race
team_id
```

------

## 选手详情

### GET

```http
/api/v1/players/{id}
```

返回：

```json
{
  "player": {},
  "statistics": {},
  "current_team": {}
}
```

------

## 选手历史战绩

### GET

```http
/api/v1/players/{id}/matches
```

参数：

```text
page
page_size
```

------

## 选手奖金记录

### GET

```http
/api/v1/players/{id}/prizes
```

------

## 选手地图胜率

### GET

```http
/api/v1/players/{id}/maps
```

返回：

```json
[
  {
    "map_name": "Jane Doe",
    "wins": 10,
    "losses": 5,
    "win_rate": 66.67
  }
]
```

------

## 选手对阵记录

### GET

```http
/api/v1/players/{id}/vs/{opponent_id}
```

参数：

```text
season_id
```

可选，按赛季筛选。

------

返回：

```json
{
  "player": {
    "id": 1,
    "cn_name": "选手A",
    "game_id": "PlayerA",
    "race": "T"
  },
  "opponent": {
    "id": 2,
    "cn_name": "选手B",
    "game_id": "PlayerB",
    "race": "Z"
  },
  "wins": 12,
  "losses": 8,
  "total": 20,
  "win_rate": 60.0,
  "matches": [
    {
      "match_id": 100,
      "game_no": 1,
      "title": "2026 Season 1 Round 3",
      "match_date": "2026-03-15",
      "map_name": "Jane Doe",
      "winner_player_id": 1,
      "winner_name": "选手A"
    }
  ]
}
```

------

# 5. 队伍接口

## 队伍列表

### GET

```http
/api/v1/teams
```

------

## 队伍详情

### GET

```http
/api/v1/teams/{id}
```

返回：

```json
{
  "team": {},
  "members": [],
  "statistics": {}
}
```

------

## 队伍历史比赛

### GET

```http
/api/v1/teams/{id}/matches
```

------

## 队伍奖金排行

### GET

```http
/api/v1/teams/prize-ranking
```

------

# 6. 地图接口

## 地图列表

### GET

```http
/api/v1/maps
```

------

## 地图详情

### GET

```http
/api/v1/maps/{id}
```

返回：

```json
{
  "map": {},
  "usage_count": 100,
  "statistics": {}
}
```

------

## 地图胜率

### GET

```http
/api/v1/maps/{id}/race-stats
```

返回：

```json
{
  "T": 52.3,
  "P": 49.8,
  "Z": 47.1
}
```

------

## 当前赛季地图池

### GET

```http
/api/v1/maps/current-season
```

------

# 7. 赛季接口

## 赛季列表

### GET

```http
/api/v1/seasons
```

------

## 赛季详情

### GET

```http
/api/v1/seasons/{id}
```

------

## 赛季排行榜

### GET

```http
/api/v1/seasons/{id}/ranking
```

------

## 赛季奖金排行

### GET

```http
/api/v1/seasons/{id}/prizes
```

------

# 8. 排行榜接口

## 总胜场排行

### GET

```http
/api/v1/rankings/wins
```

------

## 胜率排行

### GET

```http
/api/v1/rankings/win-rate
```

------

## 奖金排行

### GET

```http
/api/v1/rankings/prize
```

------

## 连胜排行

### GET

```http
/api/v1/rankings/streak
```

------

# 9. 搜索接口

## 全局搜索

### GET

```http
/api/v1/search
```

参数：

```text
keyword
```

------

返回：

```json
{
  "players": [],
  "teams": [],
  "maps": []
}
```

------

# 10. 后台接口

## 手动采集

### POST

```http
/api/v1/admin/crawler/run
```

------

## 按wr_id采集

### POST

```http
/api/v1/admin/crawler/run/{wr_id}
```

------

## 历史回补

### POST

```http
/api/v1/admin/crawler/backfill
```

请求：

```json
{
  "start_date": "2026-01-01",
  "end_date": "2026-06-01"
}
```

------

## 查看采集日志

### GET

```http
/api/v1/admin/crawler/logs
```

------

# 11. 数据异常中心

## 异常列表

### GET

```http
/api/v1/admin/issues
```

------

## 异常详情

### GET

```http
/api/v1/admin/issues/{id}
```

------

## 标记已解决

### PATCH

```http
/api/v1/admin/issues/{id}/resolve
```

------

# 12. 翻译管理

## 查看翻译规则

### GET

```http
/api/v1/admin/translations
```

------

## 新增翻译规则

### POST

```http
/api/v1/admin/translations
```

------

## 修改翻译规则

### PUT

```http
/api/v1/admin/translations/{id}
```

------

## 删除翻译规则

### DELETE

```http
/api/v1/admin/translations/{id}
```

------

# 13. 健康检查

## 服务状态

### GET

```http
/api/v1/health
```

返回：

```json
{
  "status": "ok",
  "database": "ok",
  "crawler": "ok"
}
```

------

# 14. 权限设计

## 游客

权限：

```text
查看所有公开数据
```

------

## 管理员

权限：

```text
采集管理

异常管理

翻译管理

数据修复
```

------

# 15. FastAPI目录结构

```text
backend/

app/

├── api/

│   ├── dashboard.py

│   ├── matches.py

│   ├── players.py

│   ├── teams.py

│   ├── maps.py

│   ├── seasons.py

│   ├── rankings.py

│   ├── search.py

│   └── admin.py

├── services/

├── repositories/

├── models/

├── schemas/

├── crawler/

├── core/

└── main.py
```