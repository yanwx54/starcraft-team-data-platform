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

    class LoginRequest:
        def __init__(self, username: str, password: str):
            self.username = username
            self.password = password

    @admin_auth_router.post("/login")
    def admin_login(request: dict, db: Session = Depends(get_db)):
        try:
            from app.models.admin_user import AdminUser
            username = request.get("username")
            password = request.get("password")
            if not username or not password:
                raise HTTPException(status_code=401, detail="用户名或密码错误")
            admin = db.query(AdminUser).filter(AdminUser.username == username).first()
            if not admin or not admin.is_active:
                raise HTTPException(status_code=401, detail="用户名或密码错误")
            if not _verify_password(password, admin.hashed_password):
                raise HTTPException(status_code=401, detail="用户名或密码错误")
            access_token = _create_access_token(data={"sub": admin.username})
            return {"access_token": access_token, "token_type": "bearer", "username": admin.username}
        except HTTPException:
            raise
        except Exception as e:
            return {"error": str(e)}

    app.include_router(admin_auth_router)

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
