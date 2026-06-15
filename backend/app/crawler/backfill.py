"""批量回补 — 从历史扫描结果中批量导入数据，支持断点续传。"""

import logging
import time

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.backfill_job import BackfillJob
from app.models.match import Match
from app.crawler.history_scanner import scan_history, DEFAULT_START_DATE
from app.crawler.list_crawler import ListItem
from app.crawler.article_crawler import crawl_article
from app.crawler.parser import parse_article
from app.crawler.database_writer import write_parsed_match

logger = logging.getLogger(__name__)

# 每批处理条目数
BATCH_SIZE = 10
# 请求间隔（秒），避免过快请求
REQUEST_DELAY = 2.0


def create_backfill_job(db: Session, start_date: str = DEFAULT_START_DATE) -> BackfillJob:
    """创建新的回补任务。"""
    job = BackfillJob(
        status="pending",
        start_date=start_date,
        total_count=0,
        processed_count=0,
        failed_count=0,
        skipped_count=0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    logger.info("创建回补任务: job_id=%d, start_date=%s", job.id, start_date)
    return job


def get_backfill_job(db: Session, job_id: int) -> BackfillJob | None:
    """获取回补任务。"""
    return db.query(BackfillJob).filter_by(id=job_id).first()


def pause_backfill_job(db: Session, job_id: int) -> BackfillJob | None:
    """暂停回补任务。"""
    job = get_backfill_job(db, job_id)
    if job and job.status == "running":
        job.status = "paused"
        db.commit()
        db.refresh(job)
        logger.info("回补任务已暂停: job_id=%d", job_id)
    return job


def _update_job_progress(
    db: Session,
    job: BackfillJob,
    *,
    processed: int = 0,
    failed: int = 0,
    skipped: int = 0,
    last_wr_id: int | None = None,
    status: str | None = None,
    error_message: str | None = None,
):
    """更新回补任务进度。"""
    job.processed_count += processed
    job.failed_count += failed
    job.skipped_count += skipped
    if last_wr_id is not None:
        job.last_processed_wr_id = last_wr_id
    if status is not None:
        job.status = status
    if error_message is not None:
        job.error_message = error_message
    db.commit()
    db.refresh(job)


def _is_wr_id_processed(db: Session, wr_id: int) -> bool:
    """检查 wr_id 是否已处理（matches 表中存在）。"""
    return db.query(Match).filter_by(wr_id=wr_id).first() is not None


def _process_item(db: Session, item: ListItem) -> str:
    """处理单个条目。

    Returns:
        "success" / "skipped" / "failed"
    """
    # 幂等: 已处理则跳过
    if _is_wr_id_processed(db, item.wr_id):
        logger.info("跳过已处理: wr_id=%d", item.wr_id)
        return "skipped"

    # 采集文章详情
    raw = crawl_article(db, item.wr_id)
    if not raw:
        logger.error("文章采集失败: wr_id=%d", item.wr_id)
        return "failed"

    # 解析
    try:
        parsed = parse_article(
            html=raw.html_content,
            wr_id=item.wr_id,
            source_url=raw.source_url,
        )
    except Exception as e:
        logger.error("解析失败 wr_id=%d: %s", item.wr_id, e)
        raw.parsed_status = "error"
        db.commit()
        return "failed"

    # 写入数据库
    result = write_parsed_match(db, parsed)
    if result:
        logger.info("处理完成: wr_id=%d", item.wr_id)
        return "success"
    else:
        logger.error("写入失败: wr_id=%d", item.wr_id)
        return "failed"


def run_backfill(
    start_date: str = DEFAULT_START_DATE,
    job_id: int | None = None,
    batch_size: int = BATCH_SIZE,
    request_delay: float = REQUEST_DELAY,
) -> BackfillJob:
    """执行批量回补任务。

    支持断点续传: 若传入 job_id，则从上次中断处继续。

    Args:
        start_date: 起始日期，格式 YYYY-MM-DD
        job_id: 已有任务 ID（用于断点续传），为 None 则创建新任务
        batch_size: 每批处理条目数
        request_delay: 请求间隔秒数

    Returns:
        更新后的 BackfillJob 对象
    """
    db = SessionLocal()
    try:
        # 获取或创建任务
        if job_id is not None:
            job = get_backfill_job(db, job_id)
            if not job:
                raise ValueError(f"回补任务不存在: job_id={job_id}")
            if job.status not in ("pending", "paused", "failed"):
                raise ValueError(f"回补任务状态不允许执行: status={job.status}")
            logger.info("恢复回补任务: job_id=%d, 已处理 %d/%d",
                        job.id, job.processed_count, job.total_count)
        else:
            job = create_backfill_job(db, start_date)

        # 标记为运行中
        job.status = "running"
        db.commit()

        # 扫描历史文章
        all_items = scan_history(start_date=job.start_date)
        job.total_count = len(all_items)
        db.commit()

        if not all_items:
            job.status = "completed"
            db.commit()
            logger.info("未发现需要回补的文章")
            return job

        # 断点续传: 从 last_processed_wr_id 之后继续
        start_index = 0
        if job.last_processed_wr_id is not None:
            for i, item in enumerate(all_items):
                if item.wr_id > job.last_processed_wr_id:
                    start_index = i
                    break
            else:
                start_index = len(all_items)
            logger.info(
                "断点续传: 从 wr_id=%d (index=%d) 继续",
                all_items[start_index].wr_id if start_index < len(all_items) else -1,
                start_index,
            )

        # 批量处理
        items_to_process = all_items[start_index:]
        batch_processed = 0

        for i, item in enumerate(items_to_process):
            # 检查任务是否被暂停
            db.refresh(job)
            if job.status == "paused":
                logger.info("回补任务已暂停: job_id=%d, 已处理 %d", job.id, job.processed_count)
                return job

            result = _process_item(db, item)

            if result == "success":
                _update_job_progress(db, job, processed=1, last_wr_id=item.wr_id)
            elif result == "skipped":
                _update_job_progress(db, job, skipped=1, last_wr_id=item.wr_id)
            else:
                _update_job_progress(db, job, failed=1, last_wr_id=item.wr_id)

            batch_processed += 1

            # 每批提交后短暂休息
            if batch_processed >= batch_size:
                logger.info(
                    "批次完成: job_id=%d, 进度 %d/%d (成功 %d, 失败 %d, 跳过 %d)",
                    job.id,
                    job.processed_count + job.skipped_count + job.failed_count,
                    job.total_count,
                    job.processed_count,
                    job.failed_count,
                    job.skipped_count,
                )
                batch_processed = 0
                time.sleep(request_delay)
            else:
                time.sleep(request_delay * 0.3)

        # 标记完成
        db.refresh(job)
        job.status = "completed"
        db.commit()
        db.refresh(job)

        logger.info(
            "回补任务完成: job_id=%d, 总计 %d, 成功 %d, 失败 %d, 跳过 %d",
            job.id, job.total_count, job.processed_count, job.failed_count, job.skipped_count,
        )
        return job

    except Exception as e:
        logger.error("回补任务异常: %s", e)
        try:
            db.refresh(job)
            job.status = "failed"
            job.error_message = str(e)[:1000]
            db.commit()
        except Exception:
            db.rollback()
        raise

    finally:
        db.close()
