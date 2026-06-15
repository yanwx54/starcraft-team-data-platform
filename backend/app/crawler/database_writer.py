"""数据库写入器 — 将解析后的比赛数据写入数据库，含幂等机制。"""

import logging
from datetime import date

from sqlalchemy.orm import Session

from app.models.data_issue import DataIssue
from app.models.map import Map
from app.models.match import Match
from app.models.match_details import MatchDetail
from app.models.match_stages import MatchStage
from app.models.player import Player
from app.models.player_alias import PlayerAlias
from app.models.prize_pool import PrizePool
from app.models.raw_article import RawArticle
from app.models.team import Team
from app.crawler.parser import ParsedMatch, ParsedStage, ParsedGame, ParsedPrize

logger = logging.getLogger(__name__)


# ── 队伍 ──────────────────────────────────────────────────

def _get_or_create_team(db: Session, team_name: str) -> Team:
    """获取或创建队伍。幂等：按 team_name 查找，不存在则新建。"""
    existing = db.query(Team).filter_by(team_name=team_name).first()
    if existing:
        return existing

    # 生成 team_uid: TEAM000001
    last_team = db.query(Team).order_by(Team.id.desc()).first()
    next_num = (last_team.id + 1) if last_team else 1
    team_uid = f"TEAM{next_num:06d}"

    team = Team(team_uid=team_uid, team_name=team_name)
    db.add(team)
    db.flush()
    logger.info("新建队伍: %s (%s)", team_name, team_uid)
    return team


# ── 选手 ──────────────────────────────────────────────────

def _get_or_create_player(db: Session, name: str, race: str = "") -> Player:
    """获取或创建选手。

    匹配流程: player_aliases → players.kr_name / players.game_id → 新建
    """
    # 1. 通过别名查找
    alias = db.query(PlayerAlias).filter_by(alias_name=name).first()
    if alias:
        player = db.query(Player).filter_by(id=alias.player_id).first()
        if player:
            return player

    # 2. 通过 kr_name 或 game_id 查找
    player = db.query(Player).filter(
        (Player.kr_name == name) | (Player.game_id == name)
    ).first()
    if player:
        # 自动写入别名
        _ensure_alias(db, player.id, name)
        return player

    # 3. 新建选手
    last_player = db.query(Player).order_by(Player.id.desc()).first()
    next_num = (last_player.id + 1) if last_player else 1
    player_uid = f"P{next_num:06d}"

    player = Player(
        player_uid=player_uid,
        kr_name=name,
        race=race if race else None,
    )
    db.add(player)
    db.flush()

    # 自动写入别名
    _ensure_alias(db, player.id, name)

    logger.info("新建选手: %s (%s, race=%s)", name, player_uid, race)
    return player


def _ensure_alias(db: Session, player_id: int, alias_name: str):
    """确保别名存在，幂等。"""
    existing = db.query(PlayerAlias).filter_by(
        player_id=player_id, alias_name=alias_name
    ).first()
    if not existing:
        alias = PlayerAlias(player_id=player_id, alias_name=alias_name)
        db.add(alias)
        db.flush()


# ── 地图 ──────────────────────────────────────────────────

def _get_or_create_map(db: Session, kr_name: str) -> Map:
    """获取或创建地图。

    匹配流程: maps.kr_name → maps.en_name → maps.cn_name → 新建
    """
    map_obj = db.query(Map).filter(
        (Map.kr_name == kr_name) | (Map.en_name == kr_name) | (Map.cn_name == kr_name)
    ).first()
    if map_obj:
        return map_obj

    # 新建地图
    last_map = db.query(Map).order_by(Map.id.desc()).first()
    next_num = (last_map.id + 1) if last_map else 1
    map_uid = f"MAP{next_num:06d}"

    map_obj = Map(map_uid=map_uid, kr_name=kr_name, is_active=True)
    db.add(map_obj)
    db.flush()

    # 记录异常
    _log_issue(db, "map_not_found", "maps", description=f"未知地图已新建: {kr_name}")
    logger.warning("新建地图: %s (%s)", kr_name, map_uid)
    return map_obj


# ── 异常记录 ──────────────────────────────────────────────

def _log_issue(
    db: Session,
    issue_type: str,
    source_table: str,
    source_id: int | None = None,
    description: str | None = None,
):
    """写入 data_issues 表。"""
    issue = DataIssue(
        issue_type=issue_type,
        source_table=source_table,
        source_id=source_id,
        description=description,
    )
    db.add(issue)
    db.flush()


# ── 比赛 ──────────────────────────────────────────────────

def _write_match(db: Session, parsed: ParsedMatch) -> Match:
    """写入 matches 表。幂等：wr_id 唯一索引保证。"""
    existing = db.query(Match).filter_by(wr_id=parsed.wr_id).first()
    if existing:
        logger.info("比赛已存在，跳过 wr_id=%d", parsed.wr_id)
        return existing

    team_a = None
    team_b = None
    winner_team = None

    if parsed.team_a_name:
        team_a = _get_or_create_team(db, parsed.team_a_name)
    if parsed.team_b_name:
        team_b = _get_or_create_team(db, parsed.team_b_name)

    # 确定胜方队伍
    if parsed.winner_team_name:
        if team_a and parsed.winner_team_name == parsed.team_a_name:
            winner_team = team_a
        elif team_b and parsed.winner_team_name == parsed.team_b_name:
            winner_team = team_b
        else:
            winner_team = _get_or_create_team(db, parsed.winner_team_name)

    match = Match(
        wr_id=parsed.wr_id,
        title=parsed.title,
        match_date=parsed.match_date or date.today(),
        source_url=parsed.source_url,
        team_a_id=team_a.id if team_a else None,
        team_b_id=team_b.id if team_b else None,
        winner_team_id=winner_team.id if winner_team else None,
    )
    db.add(match)
    db.flush()
    logger.info("比赛写入成功: wr_id=%d, %s vs %s", parsed.wr_id, parsed.team_a_name, parsed.team_b_name)
    return match


# ── 阶段 & 对局 ──────────────────────────────────────────

def _write_stages_and_details(
    db: Session, match: Match, stages: list[ParsedStage]
):
    """写入 match_stages 和 match_details 表。幂等：先检查是否已写入。"""
    for stage in stages:
        # 检查是否已存在该阶段
        existing_stage = db.query(MatchStage).filter_by(
            match_id=match.id,
            stage_type=stage.stage_type,
            stage_order=stage.stage_order,
        ).first()

        if existing_stage:
            stage_id = existing_stage.id
            logger.info("阶段已存在，跳过 match_id=%d stage=%s#%d",
                        match.id, stage.stage_type, stage.stage_order)
        else:
            # 确定阶段胜方
            winner_team_id = None
            if stage.winner_team_name:
                team = db.query(Team).filter_by(team_name=stage.winner_team_name).first()
                if team:
                    winner_team_id = team.id

            match_stage = MatchStage(
                match_id=match.id,
                stage_type=stage.stage_type,
                stage_order=stage.stage_order,
                winner_team_id=winner_team_id,
            )
            db.add(match_stage)
            db.flush()
            stage_id = match_stage.id
            logger.info("阶段写入: match_id=%d %s#%d", match.id, stage.stage_type, stage.stage_order)

        # 写入对局详情
        for game in stage.games:
            # 幂等检查
            existing_detail = db.query(MatchDetail).filter_by(
                match_id=match.id,
                stage_id=stage_id,
                game_no=game.game_no,
            ).first()
            if existing_detail:
                continue

            player_a = _get_or_create_player(db, game.player_a_name, game.player_a_race)
            player_b = _get_or_create_player(db, game.player_b_name, game.player_b_race)
            winner = _get_or_create_player(db, game.winner_name)
            loser = _get_or_create_player(db, game.loser_name)

            map_obj = _get_or_create_map(db, game.map_name) if game.map_name else None

            detail = MatchDetail(
                match_id=match.id,
                stage_id=stage_id,
                game_no=game.game_no,
                map_id=map_obj.id if map_obj else None,
                player_a_id=player_a.id,
                player_b_id=player_b.id,
                winner_player_id=winner.id,
                loser_player_id=loser.id,
                score_a=1,
                score_b=0,
            )
            db.add(detail)

        db.flush()
    logger.info("对局数据写入完成: match_id=%d", match.id)


# ── 奖金 ──────────────────────────────────────────────────

def _write_prizes(db: Session, match: Match, prizes: list[ParsedPrize]):
    """写入 prize_pool 表。幂等：按 match_id + player_id 去重。"""
    for prize in prizes:
        player = _get_or_create_player(db, prize.player_name)

        # 幂等检查
        existing = db.query(PrizePool).filter_by(
            match_id=match.id,
            player_id=player.id,
        ).first()
        if existing:
            continue

        pp = PrizePool(
            match_id=match.id,
            player_id=player.id,
            prize_amount=prize.prize_amount,
        )
        db.add(pp)

    db.flush()
    logger.info("奖金数据写入完成: match_id=%d, %d 条", match.id, len(prizes))


# ── 主写入函数 ────────────────────────────────────────────

def write_parsed_match(db: Session, parsed: ParsedMatch) -> Match | None:
    """将解析后的比赛数据完整写入数据库。

    包含: matches + match_stages + match_details + prize_pool
    幂等: wr_id 唯一索引 + 各子表去重检查

    Returns:
        写入的 Match 对象；若 wr_id 已存在则返回已有记录。
    """
    try:
        match = _write_match(db, parsed)

        # 仅当比赛是新创建时才写入子表（数据冻结规则）
        if match.wr_id == parsed.wr_id and db.query(MatchDetail).filter_by(match_id=match.id).first() is None:
            _write_stages_and_details(db, match, parsed.stages)
            _write_prizes(db, match, parsed.prizes)

        # 更新 raw_articles 的 parsed_status
        raw = db.query(RawArticle).filter_by(wr_id=parsed.wr_id).first()
        if raw and raw.parsed_status == "pending":
            raw.parsed_status = "parsed"

        db.commit()
        logger.info("比赛数据写入完成: wr_id=%d", parsed.wr_id)
        return match

    except Exception as e:
        db.rollback()
        logger.error("比赛数据写入失败 wr_id=%d: %s", parsed.wr_id, e)
        _log_issue(
            db, "crawl_error", "matches",
            source_id=parsed.wr_id,
            description=f"比赛数据写入失败: {e}",
        )
        try:
            db.commit()
        except Exception:
            db.rollback()
        return None
