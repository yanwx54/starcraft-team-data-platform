"""后台管理接口 — 历史回补。"""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.admin_auth import get_current_admin
from app.database import get_db
from app.models.admin_user import AdminUser
from app.models.backfill_job import BackfillJob
from app.crawler.backfill import (
    run_backfill,
    pause_backfill_job,
    get_backfill_job as _get_backfill_job,
    create_backfill_job as _create_backfill_job,
)
from app.crawler.history_scanner import scan_history

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin/crawler/backfill", tags=["admin-backfill"])


class BackfillRequest(BaseModel):
    start_date: str = "2026-01-01"


class BackfillResumeRequest(BaseModel):
    job_id: int


@router.post("")
def start_backfill(
    request: BackfillRequest,
    background_tasks: BackgroundTasks,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """启动新的历史回补任务。"""
    job = _create_backfill_job(db, start_date=request.start_date)
    background_tasks.add_task(run_backfill, start_date=request.start_date, job_id=job.id)
    logger.info("管理员 %s 启动回补任务: job_id=%d", current_admin.username, job.id)
    return {"job_id": job.id, "status": "running", "start_date": request.start_date}


@router.post("/resume")
def resume_backfill(
    request: BackfillResumeRequest,
    background_tasks: BackgroundTasks,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """恢复中断的回补任务。"""
    job = _get_backfill_job(db, request.job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"回补任务不存在: job_id={request.job_id}")
    if job.status not in ("paused", "failed"):
        raise HTTPException(status_code=400, detail=f"任务状态不允许恢复: status={job.status}")

    background_tasks.add_task(run_backfill, job_id=request.job_id)
    logger.info("管理员 %s 恢复回补任务: job_id=%d", current_admin.username, request.job_id)
    return {"job_id": request.job_id, "status": "resuming"}


@router.post("/pause/{job_id}")
def pause_backfill(
    job_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """暂停回补任务。"""
    job = pause_backfill_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"回补任务不存在: job_id={job_id}")
    return {
        "job_id": job.id,
        "status": job.status,
        "processed_count": job.processed_count,
        "total_count": job.total_count,
    }


@router.get("/status/{job_id}")
def backfill_status(
    job_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """查询回补任务状态。"""
    job = _get_backfill_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"回补任务不存在: job_id={job_id}")
    return {
        "job_id": job.id,
        "status": job.status,
        "start_date": job.start_date,
        "total_count": job.total_count,
        "processed_count": job.processed_count,
        "failed_count": job.failed_count,
        "skipped_count": job.skipped_count,
        "last_processed_wr_id": job.last_processed_wr_id,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
    }


@router.get("/jobs")
def list_backfill_jobs(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """列出所有回补任务。"""
    jobs = db.query(BackfillJob).order_by(BackfillJob.id.desc()).all()
    return [
        {
            "job_id": j.id,
            "status": j.status,
            "start_date": j.start_date,
            "total_count": j.total_count,
            "processed_count": j.processed_count,
            "failed_count": j.failed_count,
            "skipped_count": j.skipped_count,
            "last_processed_wr_id": j.last_processed_wr_id,
            "created_at": j.created_at.isoformat() if j.created_at else None,
        }
        for j in jobs
    ]


@router.post("/scan")
def scan_history_endpoint(
    request: BackfillRequest,
    current_admin: AdminUser = Depends(get_current_admin),
):
    """仅扫描历史文章，不执行回补。"""
    items = scan_history(start_date=request.start_date)
    return {
        "start_date": request.start_date,
        "total_found": len(items),
        "items": [
            {
                "wr_id": item.wr_id,
                "title": item.title,
                "publish_date": item.publish_date,
            }
            for item in items
        ],
    }
