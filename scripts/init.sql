-- ============================================================
-- StarCraft Team Data Platform - 数据库初始化脚本
-- 适用于 Neon PostgreSQL
-- 在 Neon SQL Editor 中直接执行即可
-- ============================================================

-- 1. 原始文章表
CREATE TABLE IF NOT EXISTS raw_articles (
    id BIGSERIAL PRIMARY KEY,
    wr_id BIGINT NOT NULL,
    title VARCHAR(500),
    source_url TEXT NOT NULL,
    article_date DATE,
    html_content TEXT NOT NULL,
    parsed_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(wr_id)
);
CREATE INDEX IF NOT EXISTS idx_raw_articles_wr_id ON raw_articles(wr_id);
CREATE INDEX IF NOT EXISTS idx_raw_articles_date ON raw_articles(article_date);

-- 2. 赛季表
CREATE TABLE IF NOT EXISTS seasons (
    id BIGSERIAL PRIMARY KEY,
    season_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(season_name)
);

-- 3. 地图表
CREATE TABLE IF NOT EXISTS maps (
    id BIGSERIAL PRIMARY KEY,
    map_uid VARCHAR(50) NOT NULL,
    kr_name VARCHAR(200),
    en_name VARCHAR(200),
    cn_name VARCHAR(200),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(map_uid)
);

-- 4. 赛季地图池
CREATE TABLE IF NOT EXISTS season_maps (
    id BIGSERIAL PRIMARY KEY,
    season_id BIGINT NOT NULL REFERENCES seasons(id),
    map_id BIGINT NOT NULL REFERENCES maps(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(season_id, map_id)
);

-- 5. 队伍表
CREATE TABLE IF NOT EXISTS teams (
    id BIGSERIAL PRIMARY KEY,
    team_uid VARCHAR(50) NOT NULL,
    team_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(team_uid)
);

-- 6. 选手表
CREATE TABLE IF NOT EXISTS players (
    id BIGSERIAL PRIMARY KEY,
    player_uid VARCHAR(50) NOT NULL,
    kr_name VARCHAR(200),
    game_id VARCHAR(200),
    cn_name VARCHAR(200),
    race VARCHAR(20),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(player_uid)
);

-- 7. 选手别名表
CREATE TABLE IF NOT EXISTS player_aliases (
    id BIGSERIAL PRIMARY KEY,
    player_id BIGINT NOT NULL REFERENCES players(id),
    alias_name VARCHAR(200) NOT NULL,
    alias_type VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 8. 转队历史表
CREATE TABLE IF NOT EXISTS player_team_history (
    id BIGSERIAL PRIMARY KEY,
    player_id BIGINT NOT NULL REFERENCES players(id),
    team_id BIGINT NOT NULL REFERENCES teams(id),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 9. 团战主表
CREATE TABLE IF NOT EXISTS matches (
    id BIGSERIAL PRIMARY KEY,
    wr_id BIGINT NOT NULL,
    season_id BIGINT REFERENCES seasons(id),
    title VARCHAR(500),
    match_date DATE NOT NULL,
    source_url TEXT,
    team_a_id BIGINT REFERENCES teams(id),
    team_b_id BIGINT REFERENCES teams(id),
    winner_team_id BIGINT REFERENCES teams(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(wr_id)
);

-- 10. 团战阶段表
CREATE TABLE IF NOT EXISTS match_stages (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES matches(id),
    stage_type VARCHAR(20) NOT NULL,
    stage_order INTEGER NOT NULL,
    winner_team_id BIGINT REFERENCES teams(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 11. 对局明细表
CREATE TABLE IF NOT EXISTS match_details (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES matches(id),
    stage_id BIGINT REFERENCES match_stages(id),
    game_no INTEGER,
    map_id BIGINT REFERENCES maps(id),
    player_a_id BIGINT NOT NULL REFERENCES players(id),
    player_b_id BIGINT NOT NULL REFERENCES players(id),
    winner_player_id BIGINT NOT NULL REFERENCES players(id),
    loser_player_id BIGINT NOT NULL REFERENCES players(id),
    score_a INTEGER DEFAULT 1,
    score_b INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_match_details_match ON match_details(match_id);
CREATE INDEX IF NOT EXISTS idx_match_details_player_a ON match_details(player_a_id);
CREATE INDEX IF NOT EXISTS idx_match_details_player_b ON match_details(player_b_id);
CREATE INDEX IF NOT EXISTS idx_match_details_winner ON match_details(winner_player_id);

-- 12. 奖金表
CREATE TABLE IF NOT EXISTS prize_pool (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES matches(id),
    player_id BIGINT NOT NULL REFERENCES players(id),
    prize_amount NUMERIC(18, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 13. 采集日志
CREATE TABLE IF NOT EXISTS crawl_log (
    id BIGSERIAL PRIMARY KEY,
    wr_id BIGINT,
    log_level VARCHAR(20),
    message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 14. 数据异常中心
CREATE TABLE IF NOT EXISTS data_issues (
    id BIGSERIAL PRIMARY KEY,
    issue_type VARCHAR(50),
    source_table VARCHAR(100),
    source_id BIGINT,
    description TEXT,
    status VARCHAR(20) DEFAULT 'open',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 15. 翻译规则表
CREATE TABLE IF NOT EXISTS translation_rules (
    id BIGSERIAL PRIMARY KEY,
    rule_type VARCHAR(20) NOT NULL,
    source_text VARCHAR(255) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    alias_group VARCHAR(255),
    priority INTEGER DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(rule_type, source_text)
);

-- 16. 回补任务表
CREATE TABLE IF NOT EXISTS backfill_jobs (
    id BIGSERIAL PRIMARY KEY,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    start_date VARCHAR(10) NOT NULL,
    total_count INTEGER NOT NULL DEFAULT 0,
    processed_count INTEGER NOT NULL DEFAULT 0,
    failed_count INTEGER NOT NULL DEFAULT 0,
    skipped_count INTEGER NOT NULL DEFAULT 0,
    last_processed_wr_id BIGINT,
    error_message VARCHAR(1000),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 17. 管理员表
CREATE TABLE IF NOT EXISTS admin_users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(username)
);

-- Alembic 版本记录
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO alembic_version (version_num) VALUES ('b2c3d4e5f6a7');

-- 初始化完成
SELECT 'Database initialized successfully! 17 tables created.' AS result;
