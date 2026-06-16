"""爬虫命令行入口 — 供 GitHub Actions / 本地手动执行。"""

import logging
import sys

from app.database import SessionLocal
from app.crawler.scheduler import run_daily_crawl

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    """执行每日采集任务。"""
    logger = logging.getLogger("crawler_cli")
    logger.info("开始执行爬虫任务 (CLI)")

    try:
        run_daily_crawl(max_pages=3)
        logger.info("爬虫任务执行完成")
    except Exception as e:
        logger.error("爬虫任务执行失败: %s", e)
        sys.exit(1)
    finally:
        SessionLocal.kw["bind"].dispose()


if __name__ == "__main__":
    main()
