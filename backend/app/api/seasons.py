"""赛季接口。"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.season import Season
from app.services.statistics import get_prize_ranking, get_win_ranking

router = APIRouter(prefix="/api/v1/seasons", tags=["seasons"])


@router.get("")
def list_seasons(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.query(Season).count()
    items = (
        db.query(Season)
        .order_by(Season.start_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [
            {
                "id": s.id,
                "season_name": s.season_name,
                "start_date": s.start_date.isoformat() if s.start_date else None,
                "end_date": s.end_date.isoformat() if s.end_date else None,
            }
            for s in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{season_id}")
def get_season_detail(season_id: int, db: Session = Depends(get_db)):
    season = db.query(Season).filter(Season.id == season_id).first()
    if not season:
        raise HTTPException(status_code=404, detail="赛季不存在")
    return {
        "id": season.id,
        "season_name": season.season_name,
        "start_date": season.start_date.isoformat() if season.start_date else None,
        "end_date": season.end_date.isoformat() if season.end_date else None,
    }


@router.get("/{season_id}/ranking")
def get_season_ranking(season_id: int, db: Session = Depends(get_db)):
    season = db.query(Season).filter(Season.id == season_id).first()
    if not season:
        raise HTTPException(status_code=404, detail="赛季不存在")
    return get_win_ranking(db, season_id=season_id)


@router.get("/{season_id}/prizes")
def get_season_prizes(
    season_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    season = db.query(Season).filter(Season.id == season_id).first()
    if not season:
        raise HTTPException(status_code=404, detail="赛季不存在")
    return get_prize_ranking(db, season_id=season_id, limit=limit)
