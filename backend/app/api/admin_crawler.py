"""后台管理接口 — 手动采集、采集日志。"""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.admin_auth import get_current_admin
from app.database import get_db
from app.models.admin_user import AdminUser
from app.models.crawl_log import CrawlLog
from app.crawler.scheduler import run_daily_crawl, run_single_crawl

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin/crawler", tags=["admin-crawler"])


@router.post("/run")
def run_crawl(
    background_tasks: BackgroundTasks,
    current_admin: AdminUser = Depends(get_current_admin),
):
    """手动触发每日采集任务。"""
    background_tasks.add_task(run_daily_crawl)
    logger.info("管理员 %s 触发手动采集", current_admin.username)
    return {"message": "采集任务已启动", "status": "running"}


@router.post("/run/{wr_id}")
def run_crawl_by_wr_id(
    wr_id: int,
    background_tasks: BackgroundTasks,
    current_admin: AdminUser = Depends(get_current_admin),
):
    """按 wr_id 采集单篇文章。"""
    background_tasks.add_task(run_single_crawl, wr_id=wr_id)
    logger.info("管理员 %s 触发单条采集: wr_id=%d", current_admin.username, wr_id)
    return {"message": f"采集任务已启动: wr_id={wr_id}", "status": "running"}


@router.get("/logs")
def get_crawl_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    log_level: str | None = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """查看采集日志。"""
    query = db.query(CrawlLog)
    if log_level:
        query = query.filter(CrawlLog.log_level == log_level)

    total = query.count()
    items = (
        query.order_by(CrawlLog.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [
            {
                "id": log.id,
                "wr_id": log.wr_id,
                "log_level": log.log_level,
                "message": log.message,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
