"""地图接口。"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.map import Map
from app.services.statistics import (
    get_current_season_maps,
    get_map_race_stats,
    get_map_stats,
)

router = APIRouter(prefix="/api/v1/maps", tags=["maps"])


@router.get("")
def list_maps(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.query(Map).count()
    items = (
        db.query(Map)
        .order_by(Map.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "items": [
            {
                "id": m.id,
                "map_uid": m.map_uid,
                "kr_name": m.kr_name,
                "en_name": m.en_name,
                "cn_name": m.cn_name,
                "is_active": m.is_active,
            }
            for m in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/current-season")
def current_season_maps(db: Session = Depends(get_db)):
    return get_current_season_maps(db)


@router.get("/{map_id}")
def get_map_detail(map_id: int, db: Session = Depends(get_db)):
    result = get_map_stats(db, map_id)
    if not result:
        raise HTTPException(status_code=404, detail="地图不存在")
    return result


@router.get("/{map_id}/race-stats")
def get_map_race_stats_endpoint(map_id: int, db: Session = Depends(get_db)):
    map_obj = db.query(Map).filter(Map.id == map_id).first()
    if not map_obj:
        raise HTTPException(status_code=404, detail="地图不存在")
    return get_map_race_stats(db, map_id)
