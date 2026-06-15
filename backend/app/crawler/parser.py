"""比赛解析器 — 从文章 HTML 解析比赛、对局、选手、地图、奖金数据。"""

import logging
import re
from dataclasses import dataclass, field
from datetime import date

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


# ── 数据结构 ──────────────────────────────────────────────

@dataclass
class ParsedGame:
    """单局对局。"""
    game_no: int
    map_name: str
    player_a_name: str
    player_a_race: str
    player_b_name: str
    player_b_race: str
    winner_name: str
    loser_name: str


@dataclass
class ParsedStage:
    """一个阶段（SET）。"""
    stage_type: str  # BO7 / KOF / ACE
    stage_order: int
    games: list[ParsedGame] = field(default_factory=list)
    team_a_score: int = 0
    team_b_score: int = 0
    winner_team_name: str | None = None


@dataclass
class ParsedPrize:
    """奖金条目。"""
    player_name: str
    prize_amount: float


@dataclass
class ParsedMatch:
    """一场完整比赛。"""
    wr_id: int
    title: str
    match_date: date | None
    source_url: str
    team_a_name: str | None
    team_b_name: str | None
    winner_team_name: str | None
    stages: list[ParsedStage] = field(default_factory=list)
    prizes: list[ParsedPrize] = field(default_factory=list)


# ── 文本预处理 ────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """将 HTML 提取的文本清理为紧凑单行格式。"""
    return re.sub(r"\s+", " ", text).strip()


def _extract_content(soup: BeautifulSoup) -> str:
    """从 HTML 中提取文章内容区域的紧凑文本。"""
    content = soup.select_one(".view-content")
    if content:
        return _clean_text(content.get_text())
    return _clean_text(soup.get_text())


# ── 赛制识别 ──────────────────────────────────────────────

def _identify_stage_type(set_header: str) -> str:
    """识别赛制类型: BO7 / KOF / ACE。"""
    header_upper = set_header.upper()

    ace_keywords = ["SUPER ACE", "ACE MATCH", "결승전", "최종전"]
    for kw in ace_keywords:
        if kw.upper() in header_upper:
            return "ACE"
    if re.search(r"\bACE\b", header_upper):
        return "ACE"

    kof_keywords = ["위너스리그", "승자연전", "WINNERS LEAGUE"]
    for kw in kof_keywords:
        if kw.upper() in header_upper:
            return "KOF"

    bo_keywords = ["프로리그", "PRO LEAGUE"]
    for kw in bo_keywords:
        if kw.upper() in header_upper:
            return "BO7"

    return "BO7"


# ── 队伍解析 ──────────────────────────────────────────────

def _parse_teams(text: str) -> tuple[str | None, str | None]:
    """从文章文本中提取两支队伍名称。"""
    team_pattern = re.compile(r"\[([^\]]+?)팀\]")
    matches = team_pattern.findall(text)
    seen = set()
    teams = []
    for name in matches:
        name = name.strip()
        if name not in seen:
            seen.add(name)
            teams.append(name)
    if len(teams) >= 2:
        return teams[0], teams[1]
    return None, None


# ── 选手解析 ──────────────────────────────────────────────

def _parse_player_with_race(text: str) -> tuple[str, str]:
    """解析 '김택용P' 格式的选手名+种族。"""
    text = text.strip()
    m = re.match(r"^(.+?)\s*([ZPT저프테])\s*$", text)
    if m:
        name = m.group(1).strip()
        race_code = m.group(2).upper()
        if race_code in ("저",):
            race_code = "Z"
        elif race_code in ("프",):
            race_code = "P"
        elif race_code in ("테",):
            race_code = "T"
        return name, race_code
    return text, ""


# ── 对局解析 ──────────────────────────────────────────────

def _parse_game_block(block: str, game_no: int) -> ParsedGame | None:
    """解析单个对局块文本。

    格式: [地图] 选手A (승/패) vs (승/패) 选手B
    或:   [地图] 选手A vs 选手B (无胜负标记)
    """
    block = block.strip()
    if not block:
        return None

    # 移除前导序号 "1. " 或 "1 . "
    block = re.sub(r"^\d+\s*\.\s*", "", block).strip()

    # 提取地图
    map_match = re.match(r"\[\s*([^\]]+?)\s*\]", block)
    if not map_match:
        return None
    map_name = map_match.group(1).strip()
    rest = block[map_match.end():].strip()

    # 解析胜负: A (승) vs (패) B
    # B名以种族字母结尾，遇到 "팀 (" 比分行停止
    m = re.match(r"(.+?)\s*\(\s*승\s*\)\s*vs\s*\(\s*패\s*\)\s*(.+?[ZPT저프테])\s*(?=.*팀\s*\(|최종|$)", rest)
    if not m:
        m = re.match(r"(.+?)\s*\(\s*승\s*\)\s*vs\s*\(\s*패\s*\)\s*(\S+?)\s*(?=\S*팀\s*\(|최종|$)", rest)
    if m:
        a_name, a_race = _parse_player_with_race(m.group(1).strip())
        b_name, b_race = _parse_player_with_race(m.group(2).strip())
        return ParsedGame(
            game_no=game_no, map_name=map_name,
            player_a_name=a_name, player_a_race=a_race,
            player_b_name=b_name, player_b_race=b_race,
            winner_name=a_name, loser_name=b_name,
        )

    # A (패) vs (승) B
    m = re.match(r"(.+?)\s*\(\s*패\s*\)\s*vs\s*\(\s*승\s*\)\s*(.+?[ZPT저프테])\s*(?=.*팀\s*\(|최종|$)", rest)
    if not m:
        m = re.match(r"(.+?)\s*\(\s*패\s*\)\s*vs\s*\(\s*승\s*\)\s*(\S+?)\s*(?=\S*팀\s*\(|최종|$)", rest)
    if m:
        a_name, a_race = _parse_player_with_race(m.group(1).strip())
        b_name, b_race = _parse_player_with_race(m.group(2).strip())
        return ParsedGame(
            game_no=game_no, map_name=map_name,
            player_a_name=a_name, player_a_race=a_race,
            player_b_name=b_name, player_b_race=b_race,
            winner_name=b_name, loser_name=a_name,
        )

    # 无胜负标记: A vs B
    m = re.match(r"(.+?[ZPT저프테])\s+vs\s+(.+?[ZPT저프테])\s*(?=.*팀\s*\(|최종|$)", rest)
    if not m:
        m = re.match(r"(.+?[ZPT저프테]?)\s+vs\s+(.+?[ZPT저프테]?)\s*(?=\S*팀\s*\(|최종|$)", rest)
    if m:
        a_name, a_race = _parse_player_with_race(m.group(1).strip())
        b_name, b_race = _parse_player_with_race(m.group(2).strip())
        return ParsedGame(
            game_no=game_no, map_name=map_name,
            player_a_name=a_name, player_a_race=a_race,
            player_b_name=b_name, player_b_race=b_race,
            winner_name=a_name, loser_name=b_name,
        )

    return None


def _parse_games_from_text(text: str, is_ace: bool = False) -> list[ParsedGame]:
    """从 SET 内的文本中解析所有对局。"""
    games: list[ParsedGame] = []

    if is_ace:
        # ACE: 无序号，按 [地图] 拆分
        blocks = re.split(r"(?=\[\s*[^\]]+?\s*\])", text)
        for block in blocks:
            block = block.strip()
            if not block or not block.startswith("["):
                continue
            game = _parse_game_block(block, game_no=999)
            if game:
                games.append(game)
    else:
        # BO7 / KOF: 按 "数字. [" 拆分
        blocks = re.split(r"(?=\d+\s*\.\s*\[)", text)
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            # 提取序号
            no_match = re.match(r"(\d+)\s*\.", block)
            if not no_match:
                continue
            game_no = int(no_match.group(1))
            game = _parse_game_block(block, game_no=game_no)
            if game:
                games.append(game)

    games.sort(key=lambda g: g.game_no)
    return games


# ── 奖金解析 ──────────────────────────────────────────────

def _parse_prizes_from_table(soup: BeautifulSoup) -> list[ParsedPrize]:
    """从 HTML 表格中解析奖金信息。"""
    prizes: list[ParsedPrize] = []

    for td in soup.select("td"):
        text = td.get_text(strip=True)
        if not re.match(r"승자\d+$", text):
            continue

        next_td = td.find_next_sibling("td")
        if not next_td:
            parent_tr = td.find_parent("tr")
            if parent_tr:
                tds = parent_tr.find_all("td")
                if len(tds) >= 2:
                    next_td = tds[1] if tds[0] == td else None

        if next_td:
            value_text = next_td.get_text(strip=True)
            prize_match = re.match(r"(.+?)\(\\?([\d,]+)\)", value_text)
            if prize_match:
                name = prize_match.group(1).strip()
                amount_str = prize_match.group(2).replace(",", "")
                try:
                    amount = float(amount_str)
                    if name:
                        prizes.append(ParsedPrize(player_name=name, prize_amount=amount))
                except ValueError:
                    continue

    return prizes


def _parse_prizes_from_text(text: str) -> list[ParsedPrize]:
    """从纯文本中解析奖金信息（备用方案）。"""
    prizes: list[ParsedPrize] = []
    pattern = re.compile(r"승자\d+\s*\|?\s*(.+?)\(\\?([\d,]+)\)")
    for m in pattern.finditer(text):
        name = m.group(1).strip()
        amount_str = m.group(2).replace(",", "")
        try:
            amount = float(amount_str)
        except ValueError:
            continue
        if name:
            prizes.append(ParsedPrize(player_name=name, prize_amount=amount))
    return prizes


# ── SET 比分解析 ──────────────────────────────────────────

_SCORE_RE = re.compile(
    r"([가-힣]+?)팀\s*\(\s*(승|패)\s*\)\s*(\d+)\s*:\s*(\d+)\s*\(\s*(승|패)\s*\)\s*([가-힣]+?)팀"
)


def _parse_set_score_and_winner(text: str) -> tuple[int, int, str | None]:
    """解析 SET 比分和胜方。"""
    m = _SCORE_RE.search(text)
    if not m:
        return 0, 0, None

    team_a_name = m.group(1)
    result_a = m.group(2)
    score_a = int(m.group(3))
    score_b = int(m.group(4))
    result_b = m.group(5)
    team_b_name = m.group(6)

    if result_a == "승":
        winner = team_a_name
    else:
        winner = team_b_name

    return score_a, score_b, winner


# ── 主解析函数 ────────────────────────────────────────────

_SET_BLOCK_RE = re.compile(
    r"\[(\d+)SET\s*[-–]\s*(.+?)\](.*?)(?=\[\d+SET|$)",
    re.DOTALL,
)


def parse_article(html: str, wr_id: int, source_url: str = "") -> ParsedMatch:
    """解析文章 HTML，提取完整比赛数据。"""
    soup = BeautifulSoup(html, "html.parser")

    # 标题
    title = ""
    title_el = soup.select_one("h1")
    if title_el:
        title = title_el.get_text(strip=True)

    # 日期
    match_date = None
    m = re.search(r"(\d{4})\.(\d{2})\.(\d{2})", title)
    if m:
        try:
            match_date = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    # 提取紧凑文本
    text = _extract_content(soup)

    # 队伍
    team_a, team_b = _parse_teams(text)

    # 奖金
    prizes = _parse_prizes_from_table(soup)
    if not prizes:
        prizes = _parse_prizes_from_text(text)

    # 最终胜方
    winner_team_name = None
    final_result = re.search(r"최종 결과\s*(.+?)(?:\s*$)", text)
    if final_result:
        result_text = final_result.group(1).strip()
        m_win = re.match(r"(\S+?)팀\s+\d+\s*:\s*\d+\s*승", result_text)
        if m_win:
            winner_team_name = m_win.group(1)

    # 按 SET 块拆分
    stages: list[ParsedStage] = []

    for m in _SET_BLOCK_RE.finditer(text):
        stage_order = int(m.group(1))
        set_header = m.group(2).strip()
        set_content = m.group(3).strip()

        stage_type = _identify_stage_type(set_header)

        # 解析对局
        is_ace = stage_type == "ACE"
        games = _parse_games_from_text(set_content, is_ace=is_ace)

        # KOF 阶段 game_no 按出现顺序编号
        if stage_type == "KOF":
            for idx, game in enumerate(games, start=1):
                game.game_no = idx

        # 解析比分
        score_a, score_b, stage_winner = _parse_set_score_and_winner(set_content)

        stages.append(ParsedStage(
            stage_type=stage_type,
            stage_order=stage_order,
            games=games,
            team_a_score=score_a,
            team_b_score=score_b,
            winner_team_name=stage_winner,
        ))

    return ParsedMatch(
        wr_id=wr_id,
        title=title,
        match_date=match_date,
        source_url=source_url,
        team_a_name=team_a,
        team_b_name=team_b,
        winner_team_name=winner_team_name,
        stages=stages,
        prizes=prizes,
    )
