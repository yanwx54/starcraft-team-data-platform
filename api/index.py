"""Vercel Serverless Function — 防御性导入，逐步测试每个模块。"""

import os
import sys

# 添加项目根目录和 backend 到 Python 路径
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi import FastAPI
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy import BigInteger, DateTime, String, func

# 数据库连接
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://starcraft:starcraft123@localhost:5432/starcraft",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 记录每个模块的导入状态
import_status = {}

# 防御性导入每个模块
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
    )
    import_status["services.statistics"] = "ok"
except Exception as e:
    import_status["services.statistics"] = f"error: {e}"

try:
    from app.api import dashboard, matches, players
    import_status["api.dashboard"] = "ok"
    import_status["api.matches"] = "ok"
    import_status["api.players"] = "ok"
except Exception as e:
    import_status["api.import"] = f"error: {e}"


app = FastAPI(
    title="StarCraft Team Data Platform",
    description="韩国星际争霸团战数据自动采集与统计平台",
    version="1.0.0",
)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "import_status": import_status}


# ============================================================
# Players API
# ============================================================
@app.get("/api/v1/players")
def list_players(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if "models.player" not in import_status or not import_status["models.player"].startswith("ok"):
        raise HTTPException(status_code=500, detail="Player model not loaded")

    try:
        from app.models.player import Player
        query = db.query(Player)
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
    except Exception as e:
        return {"error": str(e), "total": 0, "items": []}


@app.get("/api/v1/players/{player_id}")
def get_player_detail(player_id: int, db: Session = Depends(get_db)):
    try:
        from app.models.player import Player
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise HTTPException(status_code=404, detail="选手不存在")
        return {
            "player": {
                "id": player.id,
                "player_uid": player.player_uid,
                "kr_name": player.kr_name,
                "game_id": player.game_id,
                "cn_name": player.cn_name,
                "race": player.race,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# Matches API
# ============================================================
@app.get("/api/v1/matches")
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
                }
                for m in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        return {"error": str(e), "total": 0, "items": []}


# ============================================================
# Dashboard API
# ============================================================
@app.get("/api/v1/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    try:
        from app.models.player import Player
        from app.models.match import Match
        from app.models.team import Team
        return {
            "total_players": db.query(Player).count(),
            "total_matches": db.query(Match).count(),
            "total_teams": db.query(Team).count(),
        }
    except Exception as e:
        return {"error": str(e), "total_players": 0, "total_matches": 0, "total_teams": 0}


# ============================================================
# Maps / Seasons / Teams / Rankings API
# ============================================================
@app.get("/api/v1/maps")
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
    except Exception as e:
        return {"error": str(e), "items": [], "total": 0}


@app.get("/api/v1/teams")
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
    except Exception as e:
        return {"error": str(e), "items": [], "total": 0}


@app.get("/api/v1/seasons")
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
    except Exception as e:
        return {"error": str(e), "items": [], "total": 0}


@app.get("/api/v1/rankings")
def rankings(db: Session = Depends(get_db)):
    try:
        from app.services.statistics import get_streak_ranking
        return get_streak_ranking(db, limit=20)
    except Exception as e:
        return {"error": str(e), "items": []}
