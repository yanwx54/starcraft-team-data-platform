"""排行榜接口。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.statistics import (
    get_prize_ranking,
    get_streak_ranking,
    get_win_rate_ranking,
    get_win_ranking,
)

router = APIRouter(prefix="/api/v1/rankings", tags=["rankings"])


@router.get("/wins")
def win_ranking(
    season_id: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_win_ranking(db, season_id=season_id, limit=limit)


@router.get("/win-rate")
def win_rate_ranking(
    season_id: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    min_games: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    return get_win_rate_ranking(
        db, season_id=season_id, limit=limit, min_games=min_games
    )


@router.get("/prize")
def prize_ranking(
    season_id: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_prize_ranking(db, season_id=season_id, limit=limit)


@router.get("/streak")
def streak_ranking(
    season_id: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_streak_ranking(db, season_id=season_id, limit=limit)
