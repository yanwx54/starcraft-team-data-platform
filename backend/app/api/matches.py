"""比赛接口。"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.match import Match
from app.models.match_details import MatchDetail
from app.models.match_stages import MatchStage
from app.models.prize_pool import PrizePool

router = APIRouter(prefix="/api/v1/matches", tags=["matches"])


@router.get("")
def list_matches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    season_id: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    team_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Match)
    if season_id:
        query = query.filter(Match.season_id == season_id)
    if date_from:
        from datetime import date as date_type

        query = query.filter(Match.match_date >= date_type.fromisoformat(date_from))
    if date_to:
        from datetime import date as date_type

        query = query.filter(Match.match_date <= date_type.fromisoformat(date_to))
    if team_id:
        query = query.filter(
            (Match.team_a_id == team_id) | (Match.team_b_id == team_id)
        )

    total = query.count()
    items = (
        query.order_by(Match.match_date.desc(), Match.id.desc())
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


@router.get("/{match_id}")
def get_match_detail(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="比赛不存在")

    stages = (
        db.query(MatchStage).filter(MatchStage.match_id == match_id).all()
    )
    games = (
        db.query(MatchDetail).filter(MatchDetail.match_id == match_id).all()
    )
    prizes = (
        db.query(PrizePool).filter(PrizePool.match_id == match_id).all()
    )

    return {
        "match": {
            "id": match.id,
            "wr_id": match.wr_id,
            "season_id": match.season_id,
            "title": match.title,
            "match_date": match.match_date.isoformat() if match.match_date else None,
            "source_url": match.source_url,
            "team_a_id": match.team_a_id,
            "team_b_id": match.team_b_id,
            "winner_team_id": match.winner_team_id,
        },
        "stages": [
            {
                "id": s.id,
                "stage_type": s.stage_type,
                "stage_order": s.stage_order,
                "winner_team_id": s.winner_team_id,
            }
            for s in stages
        ],
        "games": [
            {
                "id": g.id,
                "stage_id": g.stage_id,
                "game_no": g.game_no,
                "map_id": g.map_id,
                "player_a_id": g.player_a_id,
                "player_b_id": g.player_b_id,
                "winner_player_id": g.winner_player_id,
                "loser_player_id": g.loser_player_id,
                "score_a": g.score_a,
                "score_b": g.score_b,
            }
            for g in games
        ],
        "prizes": [
            {
                "id": p.id,
                "player_id": p.player_id,
                "prize_amount": float(p.prize_amount),
            }
            for p in prizes
        ],
    }


@router.get("/{match_id}/stages")
def get_match_stages(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="比赛不存在")

    stages = (
        db.query(MatchStage)
        .filter(MatchStage.match_id == match_id)
        .order_by(MatchStage.stage_order)
        .all()
    )
    return [
        {
            "id": s.id,
            "stage_type": s.stage_type,
            "stage_order": s.stage_order,
            "winner_team_id": s.winner_team_id,
        }
        for s in stages
    ]
