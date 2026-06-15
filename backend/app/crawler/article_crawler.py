"""文章详情采集器 — 获取文章页 HTML 并保存到 raw_articles。"""

import hashlib
import logging
import re
from datetime import date

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_fixed

from app.models.raw_article import RawArticle

logger = logging.getLogger(__name__)

BASE_URL = "https://eloboard.com/men/bbs/board.php"


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5), reraise=True)
def fetch_article_html(wr_id: int) -> str:
    """请求文章详情页 HTML，失败自动重试 3 次，间隔 5 秒。"""
    params = {"bo_table": "pro_league", "wr_id": wr_id}
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


def _extract_title(html: str) -> str:
    """从文章页提取标题。"""
    soup = BeautifulSoup(html, "html.parser")
    # 标题通常在 h2 或 .bo_v_title 等位置
    title_el = soup.select_one("h2, .bo_v_title, .view-title")
    if title_el:
        return title_el.get_text(strip=True)
    return ""


def _extract_date(html: str) -> date | None:
    """从文章页提取日期。"""
    # 优先从标题中提取: "2026.04.13 (월) ..."
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    m = re.search(r"(\d{4})\.(\d{2})\.(\d{2})", text)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    return None


def _compute_html_hash(html: str) -> str:
    """计算 HTML 的 SHA256 哈希。"""
    return hashlib.sha256(html.encode("utf-8")).hexdigest()


def save_raw_article(db: Session, wr_id: int, html: str) -> RawArticle:
    """保存原始 HTML 到 raw_articles 表。

    幂等逻辑：若 wr_id 已存在，检查 html_hash 是否变化；
    变化则记录日志但不更新业务数据。
    """
    source_url = f"{BASE_URL}?bo_table=pro_league&wr_id={wr_id}"
    title = _extract_title(html)
    article_date = _extract_date(html)
    html_hash = _compute_html_hash(html)

    existing = db.query(RawArticle).filter_by(wr_id=wr_id).first()

    if existing:
        if existing.html_content != html:
            old_hash = _compute_html_hash(existing.html_content)
            if old_hash != html_hash:
                logger.warning(
                    "wr_id=%d HTML内容变化 (旧hash=%s, 新hash=%s)，记录但不更新业务数据",
                    wr_id, old_hash[:12], html_hash[:12],
                )
                # 更新 HTML 存档但标记 parsed_status 为 changed
                existing.html_content = html
                existing.title = title
                existing.article_date = article_date
                existing.parsed_status = "changed"
        return existing

    raw = RawArticle(
        wr_id=wr_id,
        title=title,
        source_url=source_url,
        article_date=article_date,
        html_content=html,
        parsed_status="pending",
    )
    db.add(raw)
    db.flush()
    logger.info("raw_articles 保存成功 wr_id=%d", wr_id)
    return raw


def crawl_article(db: Session, wr_id: int) -> RawArticle | None:
    """采集文章详情并保存到数据库。

    Returns:
        保存后的 RawArticle 对象；采集失败返回 None。
    """
    logger.info("开始采集文章详情 wr_id=%d", wr_id)
    try:
        html = fetch_article_html(wr_id)
        raw = save_raw_article(db, wr_id, html)
        db.commit()
        logger.info("文章详情采集完成 wr_id=%d", wr_id)
        return raw
    except Exception as e:
        db.rollback()
        logger.error("文章详情采集失败 wr_id=%d: %s", wr_id, e)
        return None
