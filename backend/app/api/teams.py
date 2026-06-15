"""队伍接口。"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.match import Match
from app.models.team import Team
from app.services.statistics import (
    get_team_members,
    get_team_prize_ranking,
    get_team_stats,
)

router = APIRouter(prefix="/api/v1/teams", tags=["teams"])


@router.get("")
def list_teams(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.query(Team).count()
    items = (
        db.query(Team)
        .order_by(Team.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [
            {"id": t.id, "team_uid": t.team_uid, "team_name": t.team_name}
            for t in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/prize-ranking")
def team_prize_ranking(
    limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)
):
    return get_team_prize_ranking(db, limit=limit)


@router.get("/{team_id}")
def get_team_detail(team_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")

    members = get_team_members(db, team_id)
    statistics = get_team_stats(db, team_id)

    return {
        "team": {
            "id": team.id,
            "team_uid": team.team_uid,
            "team_name": team.team_name,
        },
        "members": members,
        "statistics": statistics,
    }


@router.get("/{team_id}/matches")
def get_team_matches(
    team_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="队伍不存在")

    query = db.query(Match).filter(
        (Match.team_a_id == team_id) | (Match.team_b_id == team_id)
    )
    total = query.count()
    matches = (
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
            for m in matches
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
