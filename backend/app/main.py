import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.database import SessionLocal
from app.models.backfill_job import BackfillJob
from app.translate.parser import parse_translate_rules
from app.translate.importer import import_rules_to_db
from app.crawler.backfill import (
    run_backfill,
    pause_backfill_job,
    get_backfill_job as _get_backfill_job,
    create_backfill_job as _create_backfill_job,
)
from app.crawler.history_scanner import scan_history
from app.api import dashboard, matches, players, teams, maps, seasons, rankings, search

logger = logging.getLogger(__name__)

RULES_FILE = Path(__file__).resolve().parent.parent.parent / "translate_rules.md"

app = FastAPI(
    title="StarCraft Team Data Platform",
    description="韩国星际争霸团战数据自动采集与统计平台",
    version="1.0.0",
)

# 注册统计服务路由
app.include_router(dashboard.router)
app.include_router(matches.router)
app.include_router(players.router)
app.include_router(teams.router)
app.include_router(maps.router)
app.include_router(seasons.router)
app.include_router(rankings.router)
app.include_router(search.router)


@app.on_event("startup")
def startup_import_rules():
    """系统启动时读取 translate_rules.md 并导入数据库。"""
    try:
        rules = parse_translate_rules(RULES_FILE)
        db = SessionLocal()
        try:
            result = import_rules_to_db(db, rules)
            logger.info(
                "翻译规则导入完成: 新增 %d 条, 跳过 %d 条 (选手 %d, 地图 %d)",
                result["added"],
                result["skipped"],
                rules.player_count(),
                rules.map_count(),
            )
        finally:
            db.close()
    except FileNotFoundError:
        logger.warning("翻译规则文件未找到: %s", RULES_FILE)
    except Exception as e:
        logger.error("翻译规则导入失败: %s", e)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "database": "ok", "crawler": "ok"}


# ── 历史回补 API ──────────────────────────────────────────


class BackfillRequest(BaseModel):
    start_date: str = "2026-01-01"


class BackfillResumeRequest(BaseModel):
    job_id: int


@app.post("/api/v1/backfill/start")
async def start_backfill(request: BackfillRequest, background_tasks: BackgroundTasks):
    """启动新的历史回补任务（后台执行）。"""
    db = SessionLocal()
    try:
        job = _create_backfill_job(db, start_date=request.start_date)
    finally:
        db.close()

    background_tasks.add_task(run_backfill, start_date=request.start_date, job_id=job.id)
    return {"job_id": job.id, "status": "running", "start_date": request.start_date}


@app.post("/api/v1/backfill/resume")
async def resume_backfill(request: BackfillResumeRequest, background_tasks: BackgroundTasks):
    """恢复中断的回补任务。"""
    db = SessionLocal()
    try:
        job = _get_backfill_job(db, request.job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"回补任务不存在: job_id={request.job_id}")
        if job.status not in ("paused", "failed"):
            raise HTTPException(status_code=400, detail=f"任务状态不允许恢复: status={job.status}")
    finally:
        db.close()

    background_tasks.add_task(run_backfill, job_id=request.job_id)
    return {"job_id": request.job_id, "status": "resuming"}


@app.post("/api/v1/backfill/pause/{job_id}")
async def pause_backfill(job_id: int):
    """暂停回补任务。"""
    db = SessionLocal()
    try:
        job = pause_backfill_job(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"回补任务不存在: job_id={job_id}")
        return {
            "job_id": job.id,
            "status": job.status,
            "processed_count": job.processed_count,
            "total_count": job.total_count,
        }
    finally:
        db.close()


@app.get("/api/v1/backfill/status/{job_id}")
async def backfill_status(job_id: int):
    """查询回补任务状态。"""
    db = SessionLocal()
    try:
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
    finally:
        db.close()


@app.get("/api/v1/backfill/jobs")
async def list_backfill_jobs():
    """列出所有回补任务。"""
    db = SessionLocal()
    try:
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
    finally:
        db.close()


@app.post("/api/v1/backfill/scan")
async def scan_history_endpoint(request: BackfillRequest):
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
