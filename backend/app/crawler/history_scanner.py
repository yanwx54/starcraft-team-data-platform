"""历史扫描器 — 从 2026-01-01 起扫描所有列表页，发现历史文章。"""

import logging
from datetime import date

from app.crawler.list_crawler import crawl_list, ListItem

logger = logging.getLogger(__name__)

DEFAULT_START_DATE = "2026-01-01"


def scan_history(start_date: str = DEFAULT_START_DATE, max_pages: int = 500) -> list[ListItem]:
    """扫描历史列表页，收集从 start_date 起的所有文章条目。

    从第 1 页开始逐页扫描，当列表页中所有条目的日期都早于 start_date 时停止。
    返回按 wr_id 升序排列的条目列表。

    Args:
        start_date: 起始日期，格式 YYYY-MM-DD，默认 2026-01-01
        max_pages: 最大扫描页数，防止无限循环

    Returns:
        符合日期范围的所有 ListItem 列表
    """
    start = date.fromisoformat(start_date)
    all_items: list[ListItem] = []
    seen_wr_ids: set[int] = set()

    logger.info("开始历史扫描: start_date=%s, max_pages=%d", start_date, max_pages)

    for page in range(1, max_pages + 1):
        try:
            items = crawl_list(page=page)
        except Exception as e:
            logger.error("列表页采集失败 page=%d: %s", page, e)
            break

        if not items:
            logger.info("列表页为空，停止扫描 page=%d", page)
            break

        # 检查是否所有条目日期都早于 start_date
        all_before_start = True
        page_new_count = 0
        for item in items:
            # 去重
            if item.wr_id in seen_wr_ids:
                continue
            seen_wr_ids.add(item.wr_id)

            # 日期过滤
            if item.publish_date:
                try:
                    item_date = date.fromisoformat(item.publish_date.replace(".", "-"))
                except ValueError:
                    # 日期解析失败，保留该条目
                    all_before_start = False
                    all_items.append(item)
                    page_new_count += 1
                    continue

                if item_date >= start:
                    all_before_start = False
                    all_items.append(item)
                    page_new_count += 1
            else:
                # 无日期的条目保留
                all_before_start = False
                all_items.append(item)
                page_new_count += 1

        logger.info(
            "扫描 page=%d, 本页新增 %d 条, 累计 %d 条",
            page, page_new_count, len(all_items),
        )

        # 当本页所有条目日期都早于 start_date 时，停止扫描
        if all_before_start and page_new_count == 0:
            logger.info("已扫描到早于 %s 的数据，停止扫描", start_date)
            break

    # 按 wr_id 升序排列
    all_items.sort(key=lambda x: x.wr_id)

    logger.info("历史扫描完成: 共发现 %d 条文章 (start_date=%s)", len(all_items), start_date)
    return all_items
