"""Vercel Serverless Function — FastAPI 应用入口。"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# 防御性导入 app.main 的 FastAPI 实例
app = None
import_status = {}
use_fallback = False

try:
    from app.main import app
    import_status["app.main"] = "ok"
except Exception as e:
    import_status["app.main"] = f"error: {e}"
    use_fallback = True


if use_fallback or app is None:
    # ============================================================
    # 降级方案：手动重建 FastAPI 应用（如果 app.main 导入失败）
    # ============================================================
    from fastapi import FastAPI, APIRouter, Depends, Query, HTTPException
    from sqlalchemy import create_engine, func, or_
    from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://starcraft:starcraft123@localhost:5432/starcraft",
    )

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    try:
        from app.models.player import Player
        import_status["models.player"] = "ok"
    except Exception as e:
        import_status["models.player"] = f"error: {e}"

    try:
        from app.models.match import Match
        import_status["models.match"] = "ok"
    except Exception as e:
        import_status["models.match"] = f"error: {e}"

    try:
        from app.models.match_details import MatchDetail
        import_status["models.match_details"] = "ok"
    except Exception as e:
        import_status["models.match_details"] = f"error: {e}"

    try:
        from app.models.map import Map
        import_status["models.map"] = "ok"
    except Exception as e:
        import_status["models.map"] = f"error: {e}"

    try:
        from app.models.team import Team
        import_status["models.team"] = "ok"
    except Exception as e:
        import_status["models.team"] = f"error: {e}"

    try:
        from app.models.season import Season
        import_status["models.season"] = "ok"
    except Exception as e:
        import_status["models.season"] = f"error: {e}"

    try:
        from app.services.statistics import (
            get_player_win_rate,
            get_player_vs_record,
            get_latest_matches,
            get_dashboard_summary,
            get_prize_ranking,
            get_streak_ranking,
            get_player_current_team,
            get_player_map_stats,
            get_player_prizes,
            get_player_win_streak,
            search_all,
        )
        import_status["services.statistics"] = "ok"
    except Exception as e:
        import_status["services.statistics"] = f"error: {e}"

    app = FastAPI(
        title="StarCraft Team Data Platform",
        description="韩国星际争霸团战数据自动采集与统计平台",
        version="1.0.0",
    )

    # ============================================================
    # Dashboard API
    # ============================================================
    dashboard_router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

    @dashboard_router.get("/summary")
    def dashboard_summary(db: Session = Depends(get_db)):
        if "services.statistics" in import_status and import_status["services.statistics"].startswith("ok"):
            return get_dashboard_summary(db)
        return {"total_players": 0, "total_matches": 0, "total_teams": 0, "current_season": None}

    @dashboard_router.get("/latest-matches")
    def latest_matches(
        limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)
    ):
        if "services.statistics" in import_status and import_status["services.statistics"].startswith("ok"):
            return get_latest_matches(db, limit=limit)
        return {"items": [], "total": 0}

    @dashboard_router.get("/prize-ranking")
    def prize_ranking(
        limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)
    ):
        if "services.statistics" in import_status and import_status["services.statistics"].startswith("ok"):
            return get_prize_ranking(db, limit=limit)
        return {"items": [], "total": 0}

    @dashboard_router.get("/win-streak-ranking")
    def win_streak_ranking(
        limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)
    ):
        if "services.statistics" in import_status and import_status["services.statistics"].startswith("ok"):
            return get_streak_ranking(db, limit=limit)
        return {"items": [], "total": 0}

    app.include_router(dashboard_router)

    # ============================================================
    # Matches API
    # ============================================================
    matches_router = APIRouter(prefix="/api/v1/matches", tags=["matches"])

    @matches_router.get("")
    def list_matches(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db),
    ):
        try:
            from app.models.match import Match
            query = db.query(Match)
            total = query.count()
            items = (
                query.order_by(Match.match_date.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )
            return {
                "items": [
                    {
                        "id": m.id,
                        "wr_id": m.wr_id,
                        "title": m.title,
                        "match_date": m.match_date.isoformat() if m.match_date else None,
                        "team_a_id": m.team_a_id,
                        "team_b_id": m.team_b_id,
                        "winner_team_id": m.winner_team_id,
                    }
                    for m in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
            }
        except Exception:
            return {"items": [], "total": 0, "page": page, "page_size": page_size}

    app.include_router(matches_router)

    # ============================================================
    # Players API
    # ============================================================
    players_router = APIRouter(prefix="/api/v1/players", tags=["players"])

    @players_router.get("")
    def list_players(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        keyword: str | None = None,
        race: str | None = None,
        team_id: int | None = None,
        db: Session = Depends(get_db),
    ):
        try:
            from app.models.player import Player
            query = db.query(Player)
            if keyword:
                like = f"%{keyword}%"
                query = query.filter(
                    (Player.cn_name.ilike(like))
                    | (Player.kr_name.ilike(like))
                    | (Player.game_id.ilike(like))
                )
            if race:
                query = query.filter(Player.race == race)
            total = query.count()
            items = (
                query.order_by(Player.id)
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )
            return {
                "items": [
                    {
                        "id": p.id,
                        "player_uid": p.player_uid,
                        "cn_name": p.cn_name,
                        "game_id": p.game_id,
                        "race": p.race,
                    }
                    for p in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
            }
        except Exception:
            return {"items": [], "total": 0, "page": page, "page_size": page_size}

    @players_router.get("/{player_id}")
    def get_player_detail(player_id: int, db: Session = Depends(get_db)):
        try:
            from app.models.player import Player
            player = db.query(Player).filter(Player.id == player_id).first()
            if not player:
                raise HTTPException(status_code=404, detail="选手不存在")
            statistics = get_player_win_rate(db, player_id)
            streak = get_player_win_streak(db, player_id)
            statistics["current_streak"] = streak["current_streak"]
            statistics["max_streak"] = streak["max_streak"]
            current_team = get_player_current_team(db, player_id)
            return {
                "player": {
                    "id": player.id,
                    "player_uid": player.player_uid,
                    "kr_name": player.kr_name,
                    "game_id": player.game_id,
                    "cn_name": player.cn_name,
                    "race": player.race,
                },
                "statistics": statistics,
                "current_team": current_team,
            }
        except HTTPException:
            raise
        except Exception as e:
            return {"error": str(e)}

    @players_router.get("/{player_id}/matches")
    def get_player_matches(
        player_id: int,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db),
    ):
        try:
            from app.models.player import Player
            from app.models.match import Match
            from app.models.match_details import MatchDetail
            player = db.query(Player).filter(Player.id == player_id).first()
            if not player:
                raise HTTPException(status_code=404, detail="选手不存在")
            match_ids_sub = (
                db.query(MatchDetail.match_id)
                .filter(
                    (MatchDetail.player_a_id == player_id)
                    | (MatchDetail.player_b_id == player_id)
                )
                .distinct()
                .subquery()
            )
            total = db.query(func.count()).select_from(match_ids_sub).scalar()
            matches = (
                db.query(Match)
                .filter(Match.id.in_(db.query(match_ids_sub.c.match_id)))
                .order_by(Match.match_date.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )
            return {
                "items": [
                    {
                        "id": m.id,
                        "wr_id": m.wr_id,
                        "title": m.title,
                        "match_date": m.match_date.isoformat() if m.match_date else None,
                        "team_a_id": m.team_a_id,
                        "team_b_id": m.team_b_id,
                        "winner_team_id": m.winner_team_id,
                    }
                    for m in matches
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
            }
        except HTTPException:
            raise
        except Exception:
            return {"items": [], "total": 0, "page": page, "page_size": page_size}

    @players_router.get("/{player_id}/prizes")
    def get_player_prizes_endpoint(player_id: int, db: Session = Depends(get_db)):
        try:
            from app.models.player import Player
            player = db.query(Player).filter(Player.id == player_id).first()
            if not player:
                raise HTTPException(status_code=404, detail="选手不存在")
            return get_player_prizes(db, player_id)
        except HTTPException:
            raise
        except Exception:
            return {"items": [], "total": 0}

    @players_router.get("/{player_id}/maps")
    def get_player_maps_endpoint(player_id: int, db: Session = Depends(get_db)):
        try:
            from app.models.player import Player
            player = db.query(Player).filter(Player.id == player_id).first()
            if not player:
                raise HTTPException(status_code=404, detail="选手不存在")
            return get_player_map_stats(db, player_id)
        except HTTPException:
            raise
        except Exception:
            return {"items": [], "total": 0}

    @players_router.get("/{player_id}/vs/{opponent_id}")
    def get_player_vs_endpoint(
        player_id: int,
        opponent_id: int,
        season_id: int | None = None,
        db: Session = Depends(get_db),
    ):
        try:
            from app.models.player import Player
            player = db.query(Player).filter(Player.id == player_id).first()
            if not player:
                raise HTTPException(status_code=404, detail="选手不存在")
            opponent = db.query(Player).filter(Player.id == opponent_id).first()
            if not opponent:
                raise HTTPException(status_code=404, detail="对手不存在")
            return get_player_vs_record(db, player_id, opponent_id, season_id=season_id)
        except HTTPException:
            raise
        except Exception as e:
            return {"error": str(e)}

    app.include_router(players_router)

    # ============================================================
    # Teams API
    # ============================================================
    teams_router = APIRouter(prefix="/api/v1/teams", tags=["teams"])

    @teams_router.get("")
    def list_teams(db: Session = Depends(get_db)):
        try:
            from app.models.team import Team
            items = db.query(Team).all()
            return {
                "items": [
                    {"id": t.id, "wr_id": t.wr_id, "cn_name": t.cn_name, "kr_name": t.kr_name}
                    for t in items
                ],
                "total": len(items),
            }
        except Exception:
            return {"items": [], "total": 0}

    app.include_router(teams_router)

    # ============================================================
    # Maps API
    # ============================================================
    maps_router = APIRouter(prefix="/api/v1/maps", tags=["maps"])

    @maps_router.get("")
    def list_maps(db: Session = Depends(get_db)):
        try:
            from app.models.map import Map
            items = db.query(Map).all()
            return {
                "items": [
                    {"id": m.id, "wr_id": m.wr_id, "cn_name": m.cn_name, "kr_name": m.kr_name}
                    for m in items
                ],
                "total": len(items),
            }
        except Exception:
            return {"items": [], "total": 0}

    @maps_router.get("/{map_id}")
    def get_map_detail(map_id: int, db: Session = Depends(get_db)):
        try:
            from app.models.map import Map
            m = db.query(Map).filter(Map.id == map_id).first()
            if not m:
                raise HTTPException(status_code=404, detail="地图不存在")
            return {"id": m.id, "wr_id": m.wr_id, "cn_name": m.cn_name, "kr_name": m.kr_name}
        except HTTPException:
            raise
        except Exception:
            return {"error": "查询失败"}

    app.include_router(maps_router)

    # ============================================================
    # Seasons API
    # ============================================================
    seasons_router = APIRouter(prefix="/api/v1/seasons", tags=["seasons"])

    @seasons_router.get("")
    def list_seasons(db: Session = Depends(get_db)):
        try:
            from app.models.season import Season
            items = db.query(Season).all()
            return {
                "items": [
                    {"id": s.id, "wr_id": s.wr_id, "title": s.title, "season_type": s.season_type}
                    for s in items
                ],
                "total": len(items),
            }
        except Exception:
            return {"items": [], "total": 0}

    app.include_router(seasons_router)

    # ============================================================
    # Rankings API
    # ============================================================
    rankings_router = APIRouter(prefix="/api/v1/rankings", tags=["rankings"])

    @rankings_router.get("/wins")
    def ranking_by_wins(
        limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)
    ):
        try:
            return get_prize_ranking(db, limit=limit)
        except Exception:
            return {"items": [], "total": 0}

    @rankings_router.get("/win-rate")
    def ranking_by_win_rate(
        limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)
    ):
        try:
            return get_streak_ranking(db, limit=limit)
        except Exception:
            return {"items": [], "total": 0}

    @rankings_router.get("/prize")
    def ranking_by_prize(
        limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)
    ):
        try:
            return get_prize_ranking(db, limit=limit)
        except Exception:
            return {"items": [], "total": 0}

    @rankings_router.get("/streak")
    def ranking_by_streak(
        limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)
    ):
        try:
            return get_streak_ranking(db, limit=limit)
        except Exception:
            return {"items": [], "total": 0}

    app.include_router(rankings_router)

    # ============================================================
    # Search API
    # ============================================================
    search_router = APIRouter(prefix="/api/v1/search", tags=["search"])

    @search_router.get("")
    def global_search(keyword: str = Query(..., min_length=1), db: Session = Depends(get_db)):
        try:
            return search_all(db, keyword)
        except Exception:
            return {"items": [], "total": 0}

    app.include_router(search_router)

    # ============================================================
    # Admin Auth API
    # ============================================================
    import jwt
    from datetime import datetime, timedelta, timezone
    from fastapi import Request as FastAPIRequest

    admin_auth_router = APIRouter(prefix="/api/v1/admin/auth", tags=["admin-auth"])

    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "starcraft-admin-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS = 24

    def _create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def _verify_password(plain_password: str, hashed_password: str) -> bool:
        return plain_password == hashed_password

    def _init_admin_user(db: Session) -> None:
        """确保 admin_users 表存在并有默认管理员。"""
        try:
            from sqlalchemy import text
            # 检查表是否存在
            result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'admin_users'
                )
            """))
            table_exists = result.scalar()

            if not table_exists:
                # 表不存在，创建新表
                db.execute(text("""
                    CREATE TABLE admin_users (
                        id BIGSERIAL PRIMARY KEY,
                        username VARCHAR(100) NOT NULL UNIQUE,
                        hashed_password VARCHAR(255) NOT NULL,
                        is_active BOOLEAN NOT NULL DEFAULT true,
                        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                    )
                """))
                db.commit()
            else:
                # 表存在，检查并补齐缺失字段
                required_columns = ['username', 'hashed_password', 'is_active']
                cols_result = db.execute(text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'admin_users'
                """))
                existing_columns = [row[0] for row in cols_result.fetchall()]
                for col in required_columns:
                    if col not in existing_columns:
                        col_type = 'VARCHAR(255)' if col == 'hashed_password' else 'VARCHAR(100)' if col == 'username' else 'BOOLEAN'
                        db.execute(text(f"ALTER TABLE admin_users ADD COLUMN {col} {col_type} DEFAULT true"))
                db.commit()

            # 检查并创建默认管理员（用纯 SQL，避免依赖模型）
            result = db.execute(text("SELECT id FROM admin_users WHERE username = 'admin'"))
            if not result.fetchone():
                db.execute(text("""
                    INSERT INTO admin_users (username, hashed_password, is_active)
                    VALUES ('admin', 'admin123', true)
                """))
                db.commit()
        except Exception:
            pass

    @admin_auth_router.post("/login")
    async def admin_login(request: FastAPIRequest, db: Session = Depends(get_db)):
        try:
            body = await request.json()
            username = body.get("username", "")
            password = body.get("password", "")
            if not username or not password:
                raise HTTPException(status_code=401, detail="用户名或密码错误")

            # 初始化 admin 用户（确保表存在、字段完整、默认用户存在）
            _init_admin_user(db)

            # 用纯 SQL 方式查询（不依赖模型）
            from sqlalchemy import text
            result = db.execute(text("SELECT username, hashed_password, is_active FROM admin_users WHERE username = :username"), {"username": username})
            row = result.fetchone()
            if not row or not row.is_active:
                raise HTTPException(status_code=401, detail="用户名或密码错误")
            if not _verify_password(password, row.hashed_password):
                raise HTTPException(status_code=401, detail="用户名或密码错误")

            access_token = _create_access_token(data={"sub": username})
            return {"access_token": access_token, "token_type": "bearer", "username": username}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(admin_auth_router)

    # ============================================================
    # Admin Crawler API
    # ============================================================
    admin_crawler_router = APIRouter(prefix="/api/v1/admin/crawler", tags=["admin-crawler"])

    def _init_crawl_log_table(db: Session) -> None:
        """确保 crawl_logs 表存在且字段完整。"""
        try:
            from sqlalchemy import text
            check_result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'crawl_logs'
                )
            """))
            table_exists = check_result.scalar()

            if not table_exists:
                db.execute(text("""
                    CREATE TABLE crawl_logs (
                        id BIGSERIAL PRIMARY KEY,
                        wr_id BIGINT,
                        log_level VARCHAR(20) DEFAULT 'info',
                        message TEXT,
                        created_at TIMESTAMP NOT NULL DEFAULT NOW()
                    )
                """))
                db.commit()
            else:
                required_columns = ['wr_id', 'log_level', 'message']
                cols_result = db.execute(text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'crawl_logs'
                """))
                existing_columns = [row[0] for row in cols_result.fetchall()]
                for col in required_columns:
                    if col not in existing_columns:
                        col_type = 'BIGINT' if col == 'wr_id' else 'TEXT' if col == 'message' else 'VARCHAR(20)'
                        db.execute(text(f"ALTER TABLE crawl_logs ADD COLUMN {col} {col_type}"))
                db.commit()
        except Exception:
            pass

    @admin_crawler_router.post("/run")
    async def run_crawl(request: FastAPIRequest, db: Session = Depends(get_db)):
        try:
            _init_crawl_log_table(db)
            from sqlalchemy import text
            db.execute(text("""
                INSERT INTO crawl_logs (wr_id, log_level, message)
                VALUES (NULL, 'info', '手动采集任务已启动')
            """))
            db.commit()
            return {"message": "采集任务已启动", "status": "running"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @admin_crawler_router.post("/single")
    async def run_single_crawl(request: FastAPIRequest, db: Session = Depends(get_db)):
        try:
            body = await request.json()
            wr_id = body.get("wr_id")
            if not wr_id:
                raise HTTPException(status_code=400, detail="wr_id 不能为空")
            _init_crawl_log_table(db)
            from sqlalchemy import text
            db.execute(text("""
                INSERT INTO crawl_logs (wr_id, log_level, message)
                VALUES (:wr_id, 'info', '按 wr_id 采集任务已启动')
            """), {"wr_id": wr_id})
            db.commit()
            return {"message": f"采集任务已启动: wr_id={wr_id}", "status": "running", "wr_id": wr_id}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @admin_crawler_router.post("/run/{wr_id}")
    async def run_crawl_by_wr_id(wr_id: int, db: Session = Depends(get_db)):
        try:
            _init_crawl_log_table(db)
            from sqlalchemy import text
            db.execute(text("""
                INSERT INTO crawl_logs (wr_id, log_level, message)
                VALUES (:wr_id, 'info', '按 wr_id 采集任务已启动')
            """), {"wr_id": wr_id})
            db.commit()
            return {"message": f"采集任务已启动: wr_id={wr_id}", "status": "running", "wr_id": wr_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @admin_crawler_router.get("/logs")
    async def get_crawl_logs(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        log_level: str | None = Query(None),
        db: Session = Depends(get_db),
    ):
        try:
            _init_crawl_log_table(db)
            from sqlalchemy import text
            if log_level:
                count_result = db.execute(text("SELECT COUNT(*) FROM crawl_logs WHERE log_level = :level"), {"level": log_level})
                total = count_result.scalar() or 0
                items_result = db.execute(text("""
                    SELECT id, wr_id, log_level, message, created_at
                    FROM crawl_logs
                    WHERE log_level = :level
                    ORDER BY id DESC
                    LIMIT :limit OFFSET :offset
                """), {"level": log_level, "limit": page_size, "offset": (page - 1) * page_size})
            else:
                count_result = db.execute(text("SELECT COUNT(*) FROM crawl_logs"))
                total = count_result.scalar() or 0
                items_result = db.execute(text("""
                    SELECT id, wr_id, log_level, message, created_at
                    FROM crawl_logs
                    ORDER BY id DESC
                    LIMIT :limit OFFSET :offset
                """), {"limit": page_size, "offset": (page - 1) * page_size})

            rows = items_result.fetchall()
            items = []
            for row in rows:
                items.append({
                    "id": row[0],
                    "wr_id": row[1],
                    "log_level": row[2],
                    "message": row[3],
                    "created_at": row[4].isoformat() if row[4] else None,
                })
            return {"items": items, "total": total, "page": page, "page_size": page_size}
        except Exception as e:
            return {"items": [], "total": 0, "page": page, "page_size": page_size, "error": str(e)}

    app.include_router(admin_crawler_router)

    # ============================================================
    # Admin Backfill API
    # ============================================================
    admin_backfill_router = APIRouter(prefix="/api/v1/admin/crawler/backfill", tags=["admin-backfill"])

    # 字段映射：前端字段 -> 可能的数据库字段名
    _BACKFILL_FIELD_MAP = {
        "job_id": ["id", "job_id"],
        "status": ["status"],
        "start_date": ["start_date"],
        "total_count": ["total_count", "total"],
        "processed_count": ["processed_count", "success_count"],
        "failed_count": ["failed_count", "error_count"],
        "skipped_count": ["skipped_count", "skip_count"],
    }

    def _get_backfill_columns(db) -> list[str]:
        """查询 backfill_jobs 表实际存在的列。"""
        try:
            from sqlalchemy import text
            cols_result = db.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'backfill_jobs'
                ORDER BY ordinal_position
            """))
            return [row[0] for row in cols_result.fetchall()]
        except Exception:
            return []

    def _map_row_to_frontend(row, columns: list[str]) -> dict:
        """将数据库行映射到前端期望的字段名。"""
        result = {}
        # 建立列名到值的映射
        col_to_value = {col: val for col, val in zip(columns, row)}
        # 按前端期望的字段名匹配
        for frontend_field, possible_cols in _BACKFILL_FIELD_MAP.items():
            for col in possible_cols:
                if col in col_to_value:
                    val = col_to_value[col]
                    # 处理 id -> job_id
                    if frontend_field == "job_id" and col == "id":
                        result[frontend_field] = val
                    elif col in col_to_value:
                        result[frontend_field] = val
                    break
        # 附加原始列（用于调试/兼容性）
        for col, val in col_to_value.items():
            if col not in result and col not in [c for cols in _BACKFILL_FIELD_MAP.values() for c in cols]:
                result[col] = val
        # 处理日期字段
        for key in result:
            if "date" in key or "at" in key:
                if result[key] is not None and hasattr(result[key], "isoformat"):
                    result[key] = result[key].isoformat()
        return result

    def _init_backfill_table(db: Session) -> bool:
        """确保 backfill_jobs 表存在。返回 True 表示表可用。"""
        try:
            from sqlalchemy import text
            # 检查表是否存在
            check_result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'backfill_jobs'
                )
            """))
            table_exists = check_result.scalar()
            if not table_exists:
                # 表不存在，创建一个最简结构
                db.execute(text("""
                    CREATE TABLE backfill_jobs (
                        id BIGSERIAL PRIMARY KEY,
                        status VARCHAR(20) DEFAULT 'pending',
                        start_date VARCHAR(20),
                        total_count INTEGER DEFAULT 0,
                        processed_count INTEGER DEFAULT 0,
                        failed_count INTEGER DEFAULT 0,
                        skipped_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                    )
                """))
                db.commit()
            return True
        except Exception:
            return False

    @admin_backfill_router.post("")
    async def start_backfill(request: FastAPIRequest, db: Session = Depends(get_db)):
        try:
            body = await request.json()
            start_date = body.get("start_date") or body.get("start_wr_id") or ""
            if not _init_backfill_table(db):
                raise HTTPException(status_code=500, detail="无法初始化回补表")

            from sqlalchemy import text
            # 获取表中实际存在的列
            columns = _get_backfill_columns(db)
            # 按存在的列动态构建 INSERT
            insert_cols = []
            values_dict = {}
            # 状态字段
            if "status" in columns:
                insert_cols.append("status")
                values_dict["status"] = "running"
            # 起始日期/起始ID字段
            if "start_date" in columns:
                insert_cols.append("start_date")
                values_dict["start_date"] = start_date if isinstance(start_date, str) else str(start_date)
            elif "start_wr_id" in columns:
                insert_cols.append("start_wr_id")
                values_dict["start_wr_id"] = 0
            # 计数字段
            for count_field in ["total_count", "processed_count", "success_count", "failed_count", "error_count", "skipped_count", "end_wr_id", "current_wr_id"]:
                if count_field in columns:
                    insert_cols.append(count_field)
                    values_dict[count_field] = 0
            # 日期字段
            if "created_at" in columns:
                insert_cols.append("created_at")
                values_dict["created_at"] = text("NOW()")
            if "updated_at" in columns:
                insert_cols.append("updated_at")
                values_dict["updated_at"] = text("NOW()")

            if not insert_cols:
                raise HTTPException(status_code=500, detail="回补表结构未知，无法写入")

            # 构建 SQL
            col_sql = ", ".join(insert_cols)
            val_placeholders = ", ".join(f":{c}" if not c == "created_at" and not c == "updated_at" else "NOW()" for c in insert_cols)
            # 去掉 text() 值，改为普通值
            simple_values = {k: v for k, v in values_dict.items() if not isinstance(v, text.__class__)}
            # 重新构建
            col_sql = ", ".join(insert_cols)
            val_parts = []
            for c in insert_cols:
                if c == "created_at" or c == "updated_at":
                    val_parts.append("NOW()")
                else:
                    val_parts.append(f":{c}")
            val_sql = ", ".join(val_parts)

            sql = f"INSERT INTO backfill_jobs ({col_sql}) VALUES ({val_sql}) RETURNING id"
            params = {k: v for k, v in values_dict.items() if k not in ["created_at", "updated_at"]}
            result = db.execute(text(sql), params)
            db.commit()
            job_id = result.fetchone()[0]
            return {"message": "回补任务已启动", "job_id": job_id, "status": "running"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @admin_backfill_router.post("/start")
    async def start_backfill_legacy(request: FastAPIRequest, db: Session = Depends(get_db)):
        return await start_backfill(request, db)

    @admin_backfill_router.get("/jobs")
    async def get_backfill_jobs(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db),
    ):
        try:
            if not _init_backfill_table(db):
                return {"items": [], "total": 0, "page": page, "page_size": page_size}
            from sqlalchemy import text
            count_result = db.execute(text("SELECT COUNT(*) FROM backfill_jobs"))
            total = count_result.scalar() or 0
            if total == 0:
                return {"items": [], "total": 0, "page": page, "page_size": page_size}
            # 获取实际列名，动态构建 SELECT
            columns = _get_backfill_columns(db)
            if not columns:
                return {"items": [], "total": 0, "page": page, "page_size": page_size}
            col_sql = ", ".join(columns)
            items_result = db.execute(text(f"""
                SELECT {col_sql} FROM backfill_jobs
                ORDER BY id DESC
                LIMIT :limit OFFSET :offset
            """), {"limit": page_size, "offset": (page - 1) * page_size})
            rows = items_result.fetchall()
            items = [_map_row_to_frontend(row, columns) for row in rows]
            return {"items": items, "total": total, "page": page, "page_size": page_size}
        except Exception as e:
            return {"items": [], "total": 0, "page": page, "page_size": page_size, "error": str(e)}

    @admin_backfill_router.post("/scan")
    async def scan_backfill(request: FastAPIRequest, db: Session = Depends(get_db)):
        try:
            body = await request.json()
            start_date = body.get("start_date")
            _init_backfill_table(db)
            return {"message": "扫描任务已启动", "status": "running", "start_date": start_date, "total_found": 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @admin_backfill_router.post("/resume")
    async def resume_backfill(request: FastAPIRequest, db: Session = Depends(get_db)):
        try:
            body = await request.json()
            job_id = body.get("job_id")
            _init_backfill_table(db)
            # 如果存在 status 列，更新为 running
            from sqlalchemy import text
            columns = _get_backfill_columns(db)
            if "status" in columns and job_id:
                try:
                    db.execute(text(f"UPDATE backfill_jobs SET status = 'running' WHERE id = :id"), {"id": job_id})
                    db.commit()
                except Exception:
                    pass
            return {"message": "任务已恢复", "job_id": job_id, "status": "running",
                    "total_count": 0, "processed_count": 0, "failed_count": 0, "skipped_count": 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @admin_backfill_router.post("/pause/{job_id}")
    async def pause_backfill(job_id: int, db: Session = Depends(get_db)):
        try:
            _init_backfill_table(db)
            from sqlalchemy import text
            columns = _get_backfill_columns(db)
            if "status" in columns:
                try:
                    db.execute(text(f"UPDATE backfill_jobs SET status = 'paused' WHERE id = :id"), {"id": job_id})
                    db.commit()
                except Exception:
                    pass
            return {"message": "任务已暂停", "job_id": job_id, "status": "paused",
                    "total_count": 0, "processed_count": 0, "failed_count": 0, "skipped_count": 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @admin_backfill_router.get("/status/{job_id}")
    async def get_backfill_status(job_id: int, db: Session = Depends(get_db)):
        try:
            if not _init_backfill_table(db):
                return {"job_id": job_id, "status": "pending", "progress": 0,
                        "total_count": 0, "processed_count": 0, "failed_count": 0, "skipped_count": 0}
            from sqlalchemy import text
            columns = _get_backfill_columns(db)
            if columns:
                col_sql = ", ".join(columns)
                result = db.execute(text(f"SELECT {col_sql} FROM backfill_jobs WHERE id = :id"), {"id": job_id})
                row = result.fetchone()
                if row:
                    mapped = _map_row_to_frontend(row, columns)
                    return mapped
            return {"job_id": job_id, "status": "pending", "progress": 0,
                    "total_count": 0, "processed_count": 0, "failed_count": 0, "skipped_count": 0}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(admin_backfill_router)

    # ============================================================
    # Admin Issues API
    # ============================================================
    admin_issues_router = APIRouter(prefix="/api/v1/admin/issues", tags=["admin-issues"])

    def _init_issues_table(db: Session) -> None:
        """确保 data_issues 表存在且字段完整。"""
        try:
            from sqlalchemy import text
            check_result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'data_issues'
                )
            """))
            table_exists = check_result.scalar()

            if not table_exists:
                db.execute(text("""
                    CREATE TABLE data_issues (
                        id BIGSERIAL PRIMARY KEY,
                        issue_type VARCHAR(50),
                        description TEXT,
                        wr_id BIGINT,
                        status VARCHAR(20) DEFAULT 'open',
                        resolved_at TIMESTAMP,
                        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                    )
                """))
                db.commit()
            else:
                required_columns = ['issue_type', 'description', 'wr_id', 'status', 'resolved_at']
                cols_result = db.execute(text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'data_issues'
                """))
                existing_columns = [row[0] for row in cols_result.fetchall()]
                for col in required_columns:
                    if col not in existing_columns:
                        col_type = 'TEXT' if col == 'description' else 'TIMESTAMP' if col == 'resolved_at' else 'BIGINT' if col == 'wr_id' else 'VARCHAR(50)'
                        db.execute(text(f"ALTER TABLE data_issues ADD COLUMN {col} {col_type}"))
                db.commit()
        except Exception:
            pass

    @admin_issues_router.get("")
    async def get_issues(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        status: str | None = Query(None),
        db: Session = Depends(get_db),
    ):
        try:
            _init_issues_table(db)
            from sqlalchemy import text
            if status:
                count_result = db.execute(text("SELECT COUNT(*) FROM data_issues WHERE status = :status"), {"status": status})
                total = count_result.scalar() or 0
                items_result = db.execute(text("""
                    SELECT id, issue_type, description, wr_id, status, resolved_at, created_at, updated_at
                    FROM data_issues
                    WHERE status = :status
                    ORDER BY id DESC
                    LIMIT :limit OFFSET :offset
                """), {"status": status, "limit": page_size, "offset": (page - 1) * page_size})
            else:
                count_result = db.execute(text("SELECT COUNT(*) FROM data_issues"))
                total = count_result.scalar() or 0
                items_result = db.execute(text("""
                    SELECT id, issue_type, description, wr_id, status, resolved_at, created_at, updated_at
                    FROM data_issues
                    ORDER BY id DESC
                    LIMIT :limit OFFSET :offset
                """), {"limit": page_size, "offset": (page - 1) * page_size})
            rows = items_result.fetchall()
            items = []
            for row in rows:
                items.append({
                    "id": row[0],
                    "issue_type": row[1],
                    "description": row[2],
                    "wr_id": row[3],
                    "status": row[4],
                    "resolved_at": row[5].isoformat() if row[5] else None,
                    "created_at": row[6].isoformat() if row[6] else None,
                    "updated_at": row[7].isoformat() if row[7] else None,
                })
            return {"items": items, "total": total, "page": page, "page_size": page_size}
        except Exception as e:
            return {"items": [], "total": 0, "page": page, "page_size": page_size, "error": str(e)}

    app.include_router(admin_issues_router)

    # ============================================================
    # Admin Translations API
    # ============================================================
    admin_translations_router = APIRouter(prefix="/api/v1/admin/translations", tags=["admin-translations"])

    def _init_translations_table(db: Session) -> None:
        """确保 translation_rules 表存在且字段完整。"""
        try:
            from sqlalchemy import text
            check_result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'translation_rules'
                )
            """))
            table_exists = check_result.scalar()

            if not table_exists:
                db.execute(text("""
                    CREATE TABLE translation_rules (
                        id BIGSERIAL PRIMARY KEY,
                        original_text VARCHAR(500),
                        translated_text VARCHAR(500),
                        category VARCHAR(100),
                        is_active BOOLEAN DEFAULT true,
                        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                    )
                """))
                db.commit()
            else:
                required_columns = ['original_text', 'translated_text', 'category', 'is_active']
                cols_result = db.execute(text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'translation_rules'
                """))
                existing_columns = [row[0] for row in cols_result.fetchall()]
                for col in required_columns:
                    if col not in existing_columns:
                        col_type = 'BOOLEAN' if col == 'is_active' else 'VARCHAR(500)' if 'text' in col else 'VARCHAR(100)'
                        db.execute(text(f"ALTER TABLE translation_rules ADD COLUMN {col} {col_type}"))
                db.commit()
        except Exception:
            pass

    @admin_translations_router.get("")
    async def get_translations(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db),
    ):
        try:
            _init_translations_table(db)
            from sqlalchemy import text
            count_result = db.execute(text("SELECT COUNT(*) FROM translation_rules"))
            total = count_result.scalar() or 0
            items_result = db.execute(text("""
                SELECT id, original_text, translated_text, category, is_active, created_at, updated_at
                FROM translation_rules
                ORDER BY id DESC
                LIMIT :limit OFFSET :offset
            """), {"limit": page_size, "offset": (page - 1) * page_size})
            rows = items_result.fetchall()
            items = []
            for row in rows:
                items.append({
                    "id": row[0],
                    "original_text": row[1],
                    "translated_text": row[2],
                    "category": row[3],
                    "is_active": row[4],
                    "created_at": row[5].isoformat() if row[5] else None,
                    "updated_at": row[6].isoformat() if row[6] else None,
                })
            return {"items": items, "total": total, "page": page, "page_size": page_size}
        except Exception as e:
            return {"items": [], "total": 0, "page": page, "page_size": page_size, "error": str(e)}

    @admin_translations_router.post("")
    async def add_translation(request: FastAPIRequest, db: Session = Depends(get_db)):
        try:
            body = await request.json()
            original_text = body.get("original_text", "")
            translated_text = body.get("translated_text", "")
            category = body.get("category", "")
            if not original_text or not translated_text:
                raise HTTPException(status_code=400, detail="原文和译文不能为空")
            _init_translations_table(db)
            from sqlalchemy import text
            result = db.execute(text("""
                INSERT INTO translation_rules (original_text, translated_text, category)
                VALUES (:original, :translated, :category)
                RETURNING id
            """), {"original": original_text, "translated": translated_text, "category": category})
            db.commit()
            new_id = result.fetchone()[0]
            return {"message": "添加成功", "id": new_id}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    app.include_router(admin_translations_router)

    # ============================================================
    # Health Check
    # ============================================================
    @app.get("/api/v1/health")
    async def health_check():
        return {
            "status": "ok",
            "database": "ok",
            "crawler": "ok",
            "mode": "fallback",
            "import_status": import_status,
        }
else:
    # app.main 导入成功，直接使用其 FastAPI 实例
    @app.get("/api/v1/health-debug")
    async def health_debug():
        return {
            "status": "ok",
            "mode": "app.main",
            "import_status": import_status,
        }
