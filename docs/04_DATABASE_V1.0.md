# DATABASE_V1.0

## 项目

韩国星际争霸团战数据自动采集与统计平台

数据库：

PostgreSQL 16

字符集：

UTF8

时区：

UTC

------

# 命名规范

## 主键

统一：

```sql
id BIGSERIAL PRIMARY KEY
```

------

## 时间字段

统一：

```sql
created_at TIMESTAMP NOT NULL DEFAULT NOW()
updated_at TIMESTAMP NOT NULL DEFAULT NOW()
```

------

# 1. 原始文章表

## raw_articles

保存ELOBOARD原始HTML

```sql
CREATE TABLE raw_articles (
    id BIGSERIAL PRIMARY KEY,

    wr_id BIGINT NOT NULL UNIQUE,

    title VARCHAR(500),

    source_url TEXT NOT NULL,

    article_date DATE,

    html_content TEXT NOT NULL,

    parsed_status VARCHAR(20) NOT NULL DEFAULT 'pending',

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

------

CREATE INDEX

```sql
CREATE INDEX idx_raw_articles_wr_id
ON raw_articles(wr_id);

CREATE INDEX idx_raw_articles_date
ON raw_articles(article_date);
```

------

# 2. 赛季表

## seasons

```sql
CREATE TABLE seasons (
    id BIGSERIAL PRIMARY KEY,

    season_name VARCHAR(100) NOT NULL UNIQUE,

    start_date DATE NOT NULL,

    end_date DATE NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

示例：

```text
2026 Season 1
2026 Season 2
```

------

# 3. 地图表

## maps

```sql
CREATE TABLE maps (
    id BIGSERIAL PRIMARY KEY,

    map_uid VARCHAR(50) NOT NULL UNIQUE,

    kr_name VARCHAR(200),

    en_name VARCHAR(200),

    cn_name VARCHAR(200),

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

------

示例：

```text
MAP0001
Jane Doe
```

------

# 4. 赛季地图池

## season_maps

```sql
CREATE TABLE season_maps (
    id BIGSERIAL PRIMARY KEY,

    season_id BIGINT NOT NULL,

    map_id BIGINT NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_season_maps_season
        FOREIGN KEY (season_id)
        REFERENCES seasons(id),

    CONSTRAINT fk_season_maps_map
        FOREIGN KEY (map_id)
        REFERENCES maps(id)
);
```

------

CREATE UNIQUE INDEX

```sql
CREATE UNIQUE INDEX uq_season_map
ON season_maps(season_id,map_id);
```

------

# 5. 队伍表

## teams

```sql
CREATE TABLE teams (
    id BIGSERIAL PRIMARY KEY,

    team_uid VARCHAR(50) NOT NULL UNIQUE,

    team_name VARCHAR(200) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

------

# 6. 选手表

## players

唯一身份表

```sql
CREATE TABLE players (
    id BIGSERIAL PRIMARY KEY,

    player_uid VARCHAR(50) NOT NULL UNIQUE,

    kr_name VARCHAR(200),

    game_id VARCHAR(200),

    cn_name VARCHAR(200),

    race VARCHAR(20),

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

------

race枚举

```text
T
P
Z
R
```

------

# 7. 选手别名表

## player_aliases

解决改名问题

```sql
CREATE TABLE player_aliases (
    id BIGSERIAL PRIMARY KEY,

    player_id BIGINT NOT NULL,

    alias_name VARCHAR(200) NOT NULL,

    alias_type VARCHAR(50),

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_alias_player
        FOREIGN KEY (player_id)
        REFERENCES players(id)
);
```

------

alias_type

```text
kr_name
game_id
cn_name
```

------

# 8. 转队历史表

## player_team_history

```sql
CREATE TABLE player_team_history (
    id BIGSERIAL PRIMARY KEY,

    player_id BIGINT NOT NULL,

    team_id BIGINT NOT NULL,

    start_date DATE,

    end_date DATE,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_pth_player
        FOREIGN KEY(player_id)
        REFERENCES players(id),

    CONSTRAINT fk_pth_team
        FOREIGN KEY(team_id)
        REFERENCES teams(id)
);
```

------

# 9. 团战主表

## matches

一篇文章对应一场团战

```sql
CREATE TABLE matches (
    id BIGSERIAL PRIMARY KEY,

    wr_id BIGINT NOT NULL UNIQUE,

    season_id BIGINT,

    title VARCHAR(500),

    match_date DATE NOT NULL,

    source_url TEXT,

    team_a_id BIGINT,

    team_b_id BIGINT,

    winner_team_id BIGINT,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_match_season
        FOREIGN KEY(season_id)
        REFERENCES seasons(id)
);
```

------

# 10. 团战阶段表

## match_stages

支持：

```text
BO7
KOF
ACE
CREATE TABLE match_stages (
    id BIGSERIAL PRIMARY KEY,

    match_id BIGINT NOT NULL,

    stage_type VARCHAR(20) NOT NULL,

    stage_order INTEGER NOT NULL,

    winner_team_id BIGINT,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_stage_match
        FOREIGN KEY(match_id)
        REFERENCES matches(id)
);
```

------

# 11. 对局明细表

## match_details

核心表

```sql
CREATE TABLE match_details (
    id BIGSERIAL PRIMARY KEY,

    match_id BIGINT NOT NULL,

    stage_id BIGINT,

    game_no INTEGER,

    map_id BIGINT,

    player_a_id BIGINT NOT NULL,

    player_b_id BIGINT NOT NULL,

    winner_player_id BIGINT NOT NULL,

    loser_player_id BIGINT NOT NULL,

    score_a INTEGER DEFAULT 1,

    score_b INTEGER DEFAULT 0,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_md_match
        FOREIGN KEY(match_id)
        REFERENCES matches(id),

    CONSTRAINT fk_md_stage
        FOREIGN KEY(stage_id)
        REFERENCES match_stages(id),

    CONSTRAINT fk_md_map
        FOREIGN KEY(map_id)
        REFERENCES maps(id)
);
```

------

CREATE INDEX

```sql
CREATE INDEX idx_match_details_match
ON match_details(match_id);

CREATE INDEX idx_match_details_player_a
ON match_details(player_a_id);

CREATE INDEX idx_match_details_player_b
ON match_details(player_b_id);

CREATE INDEX idx_match_details_winner
ON match_details(winner_player_id);
```

------

# 12. 奖金表

## prize_pool

奖金属于选手

```sql
CREATE TABLE prize_pool (
    id BIGSERIAL PRIMARY KEY,

    match_id BIGINT NOT NULL,

    player_id BIGINT NOT NULL,

    prize_amount NUMERIC(18,2) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_prize_match
        FOREIGN KEY(match_id)
        REFERENCES matches(id),

    CONSTRAINT fk_prize_player
        FOREIGN KEY(player_id)
        REFERENCES players(id)
);
```

------

# 13. 采集日志

## crawl_log

```sql
CREATE TABLE crawl_log (
    id BIGSERIAL PRIMARY KEY,

    wr_id BIGINT,

    log_level VARCHAR(20),

    message TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

------

# 14. 数据异常中心

## data_issues

```sql
CREATE TABLE data_issues (
    id BIGSERIAL PRIMARY KEY,

    issue_type VARCHAR(50),

    source_table VARCHAR(100),

    source_id BIGINT,

    description TEXT,

    status VARCHAR(20) DEFAULT 'open',

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

------

issue_type

```text
translation_error
player_not_found
map_not_found
score_conflict
prize_error
crawl_error
```

------

# 推荐初始化数据

## seasons

```text
2026 Season 1
```

------

## stage_type

```text
BO7
KOF
ACE
```

------

## race

```text
T
P
Z
R
```

------

# 数据量预估

2026年开始

预计：

团战：

5000+

对局：

50000+

奖金记录：

50000+

PostgreSQL单机可轻松支撑。

------

# V2预留表（暂不创建）

```text
player_elo_history

prediction_records

ranking_snapshots
```

V1阶段不落库。
