"""选手接口。"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.match import Match
from app.models.match_details import MatchDetail
from app.models.player import Player
from app.services.statistics import (
    get_player_current_team,
    get_player_map_stats,
    get_player_prizes,
    get_player_vs_record,
    get_player_win_rate,
    get_player_win_streak,
)

router = APIRouter(prefix="/api/v1/players", tags=["players"])


@router.get("")
def list_players(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = None,
    race: str | None = None,
    team_id: int | None = None,
    db: Session = Depends(get_db),
):
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
    if team_id:
        from app.models.player_team_history import PlayerTeamHistory
        from datetime import date as date_type

        sub = (
            db.query(PlayerTeamHistory.player_id)
            .filter(
                PlayerTeamHistory.team_id == team_id,
                (PlayerTeamHistory.end_date.is_(None))
                | (PlayerTeamHistory.end_date >= date_type.today()),
            )
            .subquery()
        )
        query = query.filter(Player.id == sub.c.player_id)

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


@router.get("/{player_id}")
def get_player_detail(player_id: int, db: Session = Depends(get_db)):
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


@router.get("/{player_id}/matches")
def get_player_matches(
    player_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="选手不存在")

    # 查找该玩家参与的所有 match_id
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


@router.get("/{player_id}/prizes")
def get_player_prizes_endpoint(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="选手不存在")
    return get_player_prizes(db, player_id)


@router.get("/{player_id}/maps")
def get_player_maps_endpoint(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="选手不存在")
    return get_player_map_stats(db, player_id)


@router.get("/{player_id}/vs/{opponent_id}")
def get_player_vs_endpoint(
    player_id: int,
    opponent_id: int,
    season_id: int | None = None,
    db: Session = Depends(get_db),
):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="选手不存在")
    opponent = db.query(Player).filter(Player.id == opponent_id).first()
    if not opponent:
        raise HTTPException(status_code=404, detail="对手不存在")
    return get_player_vs_record(db, player_id, opponent_id, season_id=season_id)
