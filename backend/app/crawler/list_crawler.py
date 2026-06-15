"""列表页采集器 — 从 eloboard.com 发现最新比赛文章。"""

import logging
import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)

BASE_URL = "https://eloboard.com/men/bbs/board.php"
BO_TABLE = "pro_league"


@dataclass
class ListItem:
    """列表页条目。"""
    wr_id: int
    title: str
    article_url: str
    publish_date: str


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5), reraise=True)
def _fetch_page(page: int = 1) -> str:
    """请求列表页 HTML，失败自动重试 3 次，间隔 5 秒。"""
    params = {"bo_table": BO_TABLE, "page": page}
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
    }
    resp = requests.get(BASE_URL, params=params, headers=headers, timeout=30, allow_redirects=True)
    resp.raise_for_status()
    return resp.text


def _parse_list_page(html: str) -> list[ListItem]:
    """解析列表页 HTML，提取 wr_id / title / article_url / publish_date。"""
    soup = BeautifulSoup(html, "html.parser")
    items: list[ListItem] = []

    for a_tag in soup.select("a[href*='wr_id=']"):
        href = a_tag.get("href", "")
        title_text = a_tag.get_text(strip=True)
        if not title_text or "wr_id=" not in href:
            continue

        # 提取 wr_id
        m = re.search(r"wr_id=(\d+)", href)
        if not m:
            continue
        wr_id = int(m.group(1))

        # 构建完整 URL
        if href.startswith("http"):
            article_url = href
        else:
            article_url = f"https://eloboard.com/men/bbs/{href}"

        # 提取日期 — 标题格式: "2026.04.13 (월) 스타 4:4 메이저 프로리그"
        date_match = re.search(r"(\d{4}\.\d{2}\.\d{2})", title_text)
        publish_date = date_match.group(1) if date_match else ""

        items.append(ListItem(
            wr_id=wr_id,
            title=title_text,
            article_url=article_url,
            publish_date=publish_date,
        ))

    return items


def crawl_list(page: int = 1) -> list[ListItem]:
    """采集列表页，返回条目列表。"""
    logger.info("开始采集列表页 page=%d", page)
    html = _fetch_page(page)
    items = _parse_list_page(html)
    logger.info("列表页采集完成 page=%d, 发现 %d 条", page, len(items))
    return items


def get_latest_wr_id() -> int | None:
    """获取列表页第一页中最大的 wr_id（即最新文章）。"""
    items = crawl_list(page=1)
    if not items:
        return None
    return max(item.wr_id for item in items)
