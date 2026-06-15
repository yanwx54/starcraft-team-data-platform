"""首页接口。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.statistics import (
    get_dashboard_summary,
    get_latest_matches,
    get_prize_ranking,
    get_streak_ranking,
)

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    return get_dashboard_summary(db)


@router.get("/latest-matches")
def latest_matches(
    limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)
):
    return get_latest_matches(db, limit=limit)


@router.get("/prize-ranking")
def prize_ranking(
    limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)
):
    return get_prize_ranking(db, limit=limit)


@router.get("/win-streak-ranking")
def win_streak_ranking(
    limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)
):
    return get_streak_ranking(db, limit=limit)
