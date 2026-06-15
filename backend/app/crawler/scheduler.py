"""调度器 — 编排列表采集、文章采集、解析、写入的完整流程。"""

import logging

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.match import Match
from app.models.raw_article import RawArticle
from app.crawler.list_crawler import crawl_list, ListItem
from app.crawler.article_crawler import crawl_article
from app.crawler.parser import parse_article
from app.crawler.database_writer import write_parsed_match

logger = logging.getLogger(__name__)


def _is_wr_id_processed(db: Session, wr_id: int) -> bool:
    """检查 wr_id 是否已处理（matches 表中存在）。"""
    return db.query(Match).filter_by(wr_id=wr_id).first() is not None


def run_daily_crawl(max_pages: int = 3):
    """执行每日采集任务。

    流程:
    1. 采集列表页，发现新文章
    2. 对每个新文章: 采集详情 → 保存HTML → 解析 → 写入数据库
    3. 幂等: 已处理的 wr_id 自动跳过
    """
    db = SessionLocal()
    try:
        logger.info("===== 开始每日采集任务 =====")

        # 1. 采集列表页
        all_items: list[ListItem] = []
        for page in range(1, max_pages + 1):
            items = crawl_list(page=page)
            all_items.extend(items)

        if not all_items:
            logger.info("列表页未发现文章")
            return

        # 按 wr_id 升序处理（历史回补也按此顺序）
        all_items.sort(key=lambda x: x.wr_id)

        new_count = 0
        skip_count = 0

        for item in all_items:
            # 幂等: 已处理则跳过
            if _is_wr_id_processed(db, item.wr_id):
                skip_count += 1
                logger.info("跳过已处理: wr_id=%d", item.wr_id)
                continue

            # 2. 采集文章详情
            raw = crawl_article(db, item.wr_id)
            if not raw:
                logger.error("文章采集失败: wr_id=%d", item.wr_id)
                continue

            # 3. 解析
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
                continue

            # 4. 写入数据库
            result = write_parsed_match(db, parsed)
            if result:
                new_count += 1
                logger.info("处理完成: wr_id=%d", item.wr_id)
            else:
                logger.error("写入失败: wr_id=%d", item.wr_id)

        logger.info(
            "===== 每日采集任务完成: 新增 %d, 跳过 %d, 总计 %d =====",
            new_count, skip_count, len(all_items),
        )

    finally:
        db.close()


def run_single_crawl(wr_id: int):
    """采集单个 wr_id 的文章。"""
    db = SessionLocal()
    try:
        if _is_wr_id_processed(db, wr_id):
            logger.info("wr_id=%d 已处理，跳过", wr_id)
            return

        raw = crawl_article(db, wr_id)
        if not raw:
            return

        parsed = parse_article(
            html=raw.html_content,
            wr_id=wr_id,
            source_url=raw.source_url,
        )
        write_parsed_match(db, parsed)
        logger.info("单条采集完成: wr_id=%d", wr_id)

    finally:
        db.close()
