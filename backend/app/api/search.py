"""搜索接口。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.statistics import search_all

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("")
def global_search(keyword: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return search_all(db, keyword)
