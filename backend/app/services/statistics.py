"""统计服务层：玩家胜负、胜率、连胜、奖金、地图、排行榜统计。"""

from datetime import date

from sqlalchemy import case, desc, func
from sqlalchemy.orm import Session

from app.models.map import Map
from app.models.match import Match
from app.models.match_details import MatchDetail
from app.models.player import Player
from app.models.player_team_history import PlayerTeamHistory
from app.models.prize_pool import PrizePool
from app.models.season import Season
from app.models.season_map import SeasonMap
from app.models.team import Team


# ── TASK-033: 玩家胜负统计 ──────────────────────────────────


def get_player_win_loss(db: Session, player_id: int, season_id: int | None = None) -> dict:
    """计算玩家胜场和负场。统计单位：单场对局（非团战）。"""
    win_query = db.query(func.count(MatchDetail.id)).filter(
        MatchDetail.winner_player_id == player_id
    )
    loss_query = db.query(func.count(MatchDetail.id)).filter(
        MatchDetail.loser_player_id == player_id
    )

    if season_id:
        win_query = win_query.join(Match, MatchDetail.match_id == Match.id).filter(
            Match.season_id == season_id
        )
        loss_query = loss_query.join(Match, MatchDetail.match_id == Match.id).filter(
            Match.season_id == season_id
        )

    wins = win_query.scalar() or 0
    losses = loss_query.scalar() or 0
    return {"wins": wins, "losses": losses}


# ── TASK-034: 玩家胜率统计 ──────────────────────────────────


def get_player_win_rate(db: Session, player_id: int, season_id: int | None = None) -> dict:
    """胜率 = 胜场 ÷ (胜场 + 负场)。"""
    wl = get_player_win_loss(db, player_id, season_id)
    total = wl["wins"] + wl["losses"]
    win_rate = round(wl["wins"] / total * 100, 2) if total > 0 else 0.0
    return {**wl, "total": total, "win_rate": win_rate}


# ── TASK-035: 玩家连胜统计 ──────────────────────────────────


def get_player_win_streak(db: Session, player_id: int, season_id: int | None = None) -> dict:
    """计算当前连胜和最高连胜。连胜定义：连续赢得个人对局；任意一场失利归零。"""
    query = (
        db.query(MatchDetail, Match.match_date)
        .join(Match, MatchDetail.match_id == Match.id)
        .filter(
            (MatchDetail.player_a_id == player_id)
            | (MatchDetail.player_b_id == player_id)
        )
    )
    if season_id:
        query = query.filter(Match.season_id == season_id)

    games = query.order_by(Match.match_date, MatchDetail.game_no).all()

    max_streak = 0
    temp_streak = 0
    for detail, _ in games:
        if detail.winner_player_id == player_id:
            temp_streak += 1
            if temp_streak > max_streak:
                max_streak = temp_streak
        else:
            temp_streak = 0

    # 当前连胜：从最近一场往前数连续胜场
    current_streak = 0
    for detail, _ in reversed(games):
        if detail.winner_player_id == player_id:
            current_streak += 1
        else:
            break

    return {"current_streak": current_streak, "max_streak": max_streak}


# ── TASK-036: 奖金统计 ──────────────────────────────────────


def get_player_prizes(db: Session, player_id: int, season_id: int | None = None) -> dict:
    """玩家奖金记录：累计奖金、赛季奖金、奖金明细。"""
    query = (
        db.query(PrizePool, Match)
        .join(Match, PrizePool.match_id == Match.id)
        .filter(PrizePool.player_id == player_id)
    )
    if season_id:
        query = query.filter(Match.season_id == season_id)

    rows = query.order_by(Match.match_date.desc()).all()

    total_prize = 0.0
    prizes = []
    for pool, match in rows:
        amount = float(pool.prize_amount)
        total_prize += amount
        prizes.append({
            "match_id": match.id,
            "title": match.title,
            "match_date": match.match_date.isoformat() if match.match_date else None,
            "prize_amount": amount,
        })

    return {"total_prize": round(total_prize, 2), "prizes": prizes}


def get_prize_ranking(
    db: Session, season_id: int | None = None, limit: int = 20
) -> list[dict]:
    """奖金排行榜。"""
    query = (
        db.query(
            Player.id,
            Player.cn_name,
            Player.game_id,
            Player.race,
            func.sum(PrizePool.prize_amount).label("total_prize"),
        )
        .join(PrizePool, Player.id == PrizePool.player_id)
    )
    if season_id:
        query = query.join(Match, PrizePool.match_id == Match.id).filter(
            Match.season_id == season_id
        )

    rows = query.group_by(Player.id).order_by(desc("total_prize")).limit(limit).all()

    return [
        {
            "player_id": r.id,
            "cn_name": r.cn_name,
            "game_id": r.game_id,
            "race": r.race,
            "total_prize": round(float(r.total_prize), 2),
        }
        for r in rows
    ]


def get_team_prize_ranking(db: Session, limit: int = 20) -> list[dict]:
    """队伍奖金排行榜（队伍成员奖金汇总）。"""
    # 当前队员
    current_histories = (
        db.query(PlayerTeamHistory)
        .filter(
            (PlayerTeamHistory.end_date.is_(None))
            | (PlayerTeamHistory.end_date >= date.today())
        )
        .subquery()
    )

    rows = (
        db.query(
            Team.id,
            Team.team_name,
            func.sum(PrizePool.prize_amount).label("total_prize"),
        )
        .join(current_histories, Team.id == current_histories.c.team_id)
        .join(PrizePool, current_histories.c.player_id == PrizePool.player_id)
        .group_by(Team.id)
        .order_by(desc("total_prize"))
        .limit(limit)
        .all()
    )

    return [
        {
            "team_id": r.id,
            "team_name": r.team_name,
            "total_prize": round(float(r.total_prize), 2),
        }
        for r in rows
    ]


# ── TASK-037: 地图统计 ──────────────────────────────────────


def get_map_stats(db: Session, map_id: int) -> dict:
    """地图使用统计。"""
    map_obj = db.query(Map).filter(Map.id == map_id).first()
    if not map_obj:
        return None

    usage_count = (
        db.query(func.count(MatchDetail.id))
        .filter(MatchDetail.map_id == map_id)
        .scalar()
    ) or 0

    return {
        "map": {
            "id": map_obj.id,
            "map_uid": map_obj.map_uid,
            "kr_name": map_obj.kr_name,
            "en_name": map_obj.en_name,
            "cn_name": map_obj.cn_name,
            "is_active": map_obj.is_active,
        },
        "usage_count": usage_count,
    }


def get_map_race_stats(db: Session, map_id: int) -> dict:
    """地图种族胜率统计。"""
    details = db.query(MatchDetail).filter(MatchDetail.map_id == map_id).all()
    if not details:
        return {"T": 0.0, "P": 0.0, "Z": 0.0}

    # 批量获取相关玩家
    player_ids = set()
    for d in details:
        player_ids.update([d.player_a_id, d.player_b_id, d.winner_player_id])

    players = db.query(Player).filter(Player.id.in_(player_ids)).all()
    player_map = {p.id: p for p in players}

    race_games = {"T": 0, "P": 0, "Z": 0}
    race_wins = {"T": 0, "P": 0, "Z": 0}

    for d in details:
        pa = player_map.get(d.player_a_id)
        pb = player_map.get(d.player_b_id)
        winner = player_map.get(d.winner_player_id)

        races_in_game = set()
        if pa and pa.race and pa.race in race_games:
            races_in_game.add(pa.race)
        if pb and pb.race and pb.race in race_games:
            races_in_game.add(pb.race)

        for r in races_in_game:
            race_games[r] += 1

        if winner and winner.race and winner.race in race_wins:
            race_wins[winner.race] += 1

    result = {}
    for race in ["T", "P", "Z"]:
        total = race_games[race]
        wins = race_wins[race]
        result[race] = round(wins / total * 100, 2) if total > 0 else 0.0

    return result


def get_player_map_stats(
    db: Session, player_id: int, season_id: int | None = None
) -> list[dict]:
    """玩家在各地图的胜率统计。"""
    query = db.query(
        MatchDetail.map_id,
        func.count(case((MatchDetail.winner_player_id == player_id, 1))).label("wins"),
        func.count(case((MatchDetail.loser_player_id == player_id, 1))).label("losses"),
    ).filter(
        (MatchDetail.player_a_id == player_id)
        | (MatchDetail.player_b_id == player_id)
    )

    if season_id:
        query = query.join(Match, MatchDetail.match_id == Match.id).filter(
            Match.season_id == season_id
        )

    rows = query.group_by(MatchDetail.map_id).all()

    # 批量获取地图信息
    map_ids = [r.map_id for r in rows if r.map_id]
    maps = db.query(Map).filter(Map.id.in_(map_ids)).all() if map_ids else []
    map_dict = {m.id: m for m in maps}

    result = []
    for map_id, wins, losses in rows:
        map_obj = map_dict.get(map_id) if map_id else None
        total = wins + losses
        win_rate = round(wins / total * 100, 2) if total > 0 else 0.0
        result.append({
            "map_id": map_id,
            "map_name": (
                map_obj.cn_name or map_obj.en_name or map_obj.kr_name
                if map_obj
                else "未知"
            ),
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
        })

    return result


# ── TASK-038: 排行榜统计 ────────────────────────────────────


def get_win_ranking(
    db: Session, season_id: int | None = None, limit: int = 20
) -> list[dict]:
    """总胜场排行。"""
    win_sub = (
        db.query(
            MatchDetail.winner_player_id.label("player_id"),
            func.count().label("wins"),
        )
        .group_by(MatchDetail.winner_player_id)
    )
    if season_id:
        win_sub = win_sub.join(Match, MatchDetail.match_id == Match.id).filter(
            Match.season_id == season_id
        )
    win_sub = win_sub.subquery()

    loss_sub = (
        db.query(
            MatchDetail.loser_player_id.label("player_id"),
            func.count().label("losses"),
        )
        .group_by(MatchDetail.loser_player_id)
    )
    if season_id:
        loss_sub = loss_sub.join(Match, MatchDetail.match_id == Match.id).filter(
            Match.season_id == season_id
        )
    loss_sub = loss_sub.subquery()

    rows = (
        db.query(
            Player.id,
            Player.cn_name,
            Player.game_id,
            Player.race,
            func.coalesce(win_sub.c.wins, 0).label("wins"),
            func.coalesce(loss_sub.c.losses, 0).label("losses"),
        )
        .outerjoin(win_sub, Player.id == win_sub.c.player_id)
        .outerjoin(loss_sub, Player.id == loss_sub.c.player_id)
        .filter(func.coalesce(win_sub.c.wins, 0) > 0)
        .order_by(desc("wins"), desc(func.coalesce(win_sub.c.wins, 0) * 1.0 / (func.coalesce(win_sub.c.wins, 0) + func.coalesce(loss_sub.c.losses, 0))))
        .limit(limit)
        .all()
    )

    return [
        {
            "player_id": r.id,
            "cn_name": r.cn_name,
            "game_id": r.game_id,
            "race": r.race,
            "wins": r.wins,
            "losses": r.losses,
        }
        for r in rows
    ]


def get_win_rate_ranking(
    db: Session, season_id: int | None = None, limit: int = 20, min_games: int = 10
) -> list[dict]:
    """胜率排行（最低出场数过滤）。"""
    win_sub = (
        db.query(
            MatchDetail.winner_player_id.label("player_id"),
            func.count().label("wins"),
        )
        .group_by(MatchDetail.winner_player_id)
    )
    if season_id:
        win_sub = win_sub.join(Match, MatchDetail.match_id == Match.id).filter(
            Match.season_id == season_id
        )
    win_sub = win_sub.subquery()

    loss_sub = (
        db.query(
            MatchDetail.loser_player_id.label("player_id"),
            func.count().label("losses"),
        )
        .group_by(MatchDetail.loser_player_id)
    )
    if season_id:
        loss_sub = loss_sub.join(Match, MatchDetail.match_id == Match.id).filter(
            Match.season_id == season_id
        )
    loss_sub = loss_sub.subquery()

    rows = (
        db.query(
            Player.id,
            Player.cn_name,
            Player.game_id,
            Player.race,
            func.coalesce(win_sub.c.wins, 0).label("wins"),
            func.coalesce(loss_sub.c.losses, 0).label("losses"),
        )
        .outerjoin(win_sub, Player.id == win_sub.c.player_id)
        .outerjoin(loss_sub, Player.id == loss_sub.c.player_id)
        .filter(
            (func.coalesce(win_sub.c.wins, 0) + func.coalesce(loss_sub.c.losses, 0))
            >= min_games
        )
        .all()
    )

    result = []
    for r in rows:
        total = r.wins + r.losses
        win_rate = round(r.wins / total * 100, 2) if total > 0 else 0.0
        result.append({
            "player_id": r.id,
            "cn_name": r.cn_name,
            "game_id": r.game_id,
            "race": r.race,
            "wins": r.wins,
            "losses": r.losses,
            "total": total,
            "win_rate": win_rate,
        })

    result.sort(key=lambda x: x["win_rate"], reverse=True)
    return result[:limit]


def get_streak_ranking(
    db: Session, season_id: int | None = None, limit: int = 20
) -> list[dict]:
    """连胜排行（按最高连胜排序）。"""
    # 获取所有有比赛记录的玩家
    player_ids_query = db.query(MatchDetail.winner_player_id).union(
        db.query(MatchDetail.loser_player_id)
    )
    if season_id:
        player_ids_query = (
            db.query(MatchDetail.winner_player_id)
            .join(Match, MatchDetail.match_id == Match.id)
            .filter(Match.season_id == season_id)
            .union(
                db.query(MatchDetail.loser_player_id)
                .join(Match, MatchDetail.match_id == Match.id)
                .filter(Match.season_id == season_id)
            )
        )

    pids = [pid for (pid,) in player_ids_query.all()]

    result = []
    for pid in pids:
        streak = get_player_win_streak(db, pid, season_id)
        player = db.query(Player).filter(Player.id == pid).first()
        if player:
            result.append({
                "player_id": pid,
                "cn_name": player.cn_name,
                "game_id": player.game_id,
                "race": player.race,
                "current_streak": streak["current_streak"],
                "max_streak": streak["max_streak"],
            })

    result.sort(key=lambda x: x["max_streak"], reverse=True)
    return result[:limit]


# ── 辅助函数 ────────────────────────────────────────────────


def get_player_current_team(db: Session, player_id: int) -> dict | None:
    """获取玩家当前所属队伍。"""
    history = (
        db.query(PlayerTeamHistory)
        .filter(
            PlayerTeamHistory.player_id == player_id,
            (PlayerTeamHistory.end_date.is_(None))
            | (PlayerTeamHistory.end_date >= date.today()),
        )
        .order_by(PlayerTeamHistory.start_date.desc())
        .first()
    )
    if history:
        team = db.query(Team).filter(Team.id == history.team_id).first()
        if team:
            return {
                "team_id": team.id,
                "team_uid": team.team_uid,
                "team_name": team.team_name,
            }
    return None


def get_player_vs_record(
    db: Session, player_id: int, opponent_id: int, season_id: int | None = None
) -> dict:
    """玩家对阵记录：胜负场次 + 每局对局明细（含比赛标题、日期、地图、胜者）。"""
    query = db.query(MatchDetail).filter(
        (
            (MatchDetail.player_a_id == player_id)
            & (MatchDetail.player_b_id == opponent_id)
        )
        | (
            (MatchDetail.player_a_id == opponent_id)
            & (MatchDetail.player_b_id == player_id)
        )
    )

    if season_id:
        query = query.join(Match, MatchDetail.match_id == Match.id).filter(
            Match.season_id == season_id
        )

    details = query.all()

    wins = sum(1 for d in details if d.winner_player_id == player_id)
    losses = sum(1 for d in details if d.winner_player_id == opponent_id)
    total = wins + losses
    win_rate = round(wins / total * 100, 2) if total > 0 else 0.0

    # 批量获取比赛信息
    match_ids = list({d.match_id for d in details})
    matches = (
        db.query(Match).filter(Match.id.in_(match_ids)).all() if match_ids else []
    )
    match_dict = {m.id: m for m in matches}

    # 批量获取地图信息
    map_ids = list({d.map_id for d in details if d.map_id})
    map_objs = db.query(Map).filter(Map.id.in_(map_ids)).all() if map_ids else []
    map_dict = {m.id: m for m in map_objs}

    # 获取双方选手信息
    player = db.query(Player).filter(Player.id == player_id).first()
    opponent = db.query(Player).filter(Player.id == opponent_id).first()
    winner_ids = {d.winner_player_id for d in details}
    winner_players = db.query(Player).filter(Player.id.in_(winner_ids)).all() if winner_ids else []
    winner_dict = {p.id: p for p in winner_players}

    match_list = []
    for d in details:
        m = match_dict.get(d.match_id)
        map_obj = map_dict.get(d.map_id) if d.map_id else None
        winner = winner_dict.get(d.winner_player_id)
        match_list.append({
            "match_id": d.match_id,
            "game_no": d.game_no,
            "title": m.title if m else None,
            "match_date": m.match_date.isoformat() if m and m.match_date else None,
            "map_name": (
                map_obj.cn_name or map_obj.en_name or map_obj.kr_name
                if map_obj
                else None
            ),
            "winner_player_id": d.winner_player_id,
            "winner_name": (
                winner.cn_name or winner.game_id or winner.kr_name
                if winner
                else None
            ),
        })

    return {
        "player": {
            "id": player.id,
            "cn_name": player.cn_name,
            "game_id": player.game_id,
            "race": player.race,
        } if player else None,
        "opponent": {
            "id": opponent.id,
            "cn_name": opponent.cn_name,
            "game_id": opponent.game_id,
            "race": opponent.race,
        } if opponent else None,
        "wins": wins,
        "losses": losses,
        "total": total,
        "win_rate": win_rate,
        "matches": match_list,
    }


def get_team_stats(db: Session, team_id: int) -> dict:
    """队伍统计。"""
    total = (
        db.query(func.count(Match.id))
        .filter((Match.team_a_id == team_id) | (Match.team_b_id == team_id))
        .scalar()
    ) or 0

    wins = (
        db.query(func.count(Match.id))
        .filter(Match.winner_team_id == team_id)
        .scalar()
    ) or 0

    losses = total - wins
    win_rate = round(wins / total * 100, 2) if total > 0 else 0.0

    return {"total": total, "wins": wins, "losses": losses, "win_rate": win_rate}


def get_team_members(db: Session, team_id: int) -> list[dict]:
    """获取队伍当前成员。"""
    histories = (
        db.query(PlayerTeamHistory)
        .filter(
            PlayerTeamHistory.team_id == team_id,
            (PlayerTeamHistory.end_date.is_(None))
            | (PlayerTeamHistory.end_date >= date.today()),
        )
        .all()
    )

    member_ids = [h.player_id for h in histories]
    if not member_ids:
        return []

    players = db.query(Player).filter(Player.id.in_(member_ids)).all()
    return [
        {
            "player_id": p.id,
            "cn_name": p.cn_name,
            "game_id": p.game_id,
            "race": p.race,
        }
        for p in players
    ]


def get_dashboard_summary(db: Session) -> dict:
    """首页统计概览。"""
    total_matches = db.query(func.count(Match.id)).scalar() or 0
    total_players = db.query(func.count(Player.id)).scalar() or 0
    total_teams = db.query(func.count(Team.id)).scalar() or 0
    latest = db.query(func.max(Match.match_date)).scalar()

    return {
        "total_matches": total_matches,
        "total_players": total_players,
        "total_teams": total_teams,
        "latest_match_date": latest.isoformat() if latest else None,
    }


def get_latest_matches(db: Session, limit: int = 10) -> list[dict]:
    """最新比赛列表。"""
    rows = (
        db.query(Match)
        .order_by(Match.match_date.desc(), Match.id.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": m.id,
            "wr_id": m.wr_id,
            "title": m.title,
            "match_date": m.match_date.isoformat() if m.match_date else None,
            "team_a_id": m.team_a_id,
            "team_b_id": m.team_b_id,
            "winner_team_id": m.winner_team_id,
        }
        for m in rows
    ]


def get_current_season_maps(db: Session) -> list[dict]:
    """当前赛季地图池。"""
    today = date.today()
    current_season = (
        db.query(Season)
        .filter(Season.start_date <= today, Season.end_date >= today)
        .first()
    )
    if not current_season:
        return []

    season_maps = (
        db.query(SeasonMap).filter(SeasonMap.season_id == current_season.id).all()
    )
    map_ids = [sm.map_id for sm in season_maps]
    maps = db.query(Map).filter(Map.id.in_(map_ids)).all() if map_ids else []
    map_dict = {m.id: m for m in maps}

    return [
        {
            "season_id": current_season.id,
            "season_name": current_season.season_name,
            "map_id": sm.map_id,
            "map_name": (
                map_dict[sm.map_id].cn_name
                or map_dict[sm.map_id].en_name
                or map_dict[sm.map_id].kr_name
                if sm.map_id in map_dict
                else "未知"
            ),
        }
        for sm in season_maps
    ]


def search_all(db: Session, keyword: str) -> dict:
    """全局搜索：选手、队伍、地图。"""
    like = f"%{keyword}%"

    players = (
        db.query(Player)
        .filter(
            (Player.cn_name.ilike(like))
            | (Player.kr_name.ilike(like))
            | (Player.game_id.ilike(like))
        )
        .limit(10)
        .all()
    )

    teams = db.query(Team).filter(Team.team_name.ilike(like)).limit(10).all()

    maps = (
        db.query(Map)
        .filter(
            (Map.cn_name.ilike(like))
            | (Map.kr_name.ilike(like))
            | (Map.en_name.ilike(like))
        )
        .limit(10)
        .all()
    )

    return {
        "players": [
            {
                "id": p.id,
                "cn_name": p.cn_name,
                "game_id": p.game_id,
                "race": p.race,
            }
            for p in players
        ],
        "teams": [{"id": t.id, "team_name": t.team_name} for t in teams],
        "maps": [
            {
                "id": m.id,
                "cn_name": m.cn_name,
                "en_name": m.en_name,
                "kr_name": m.kr_name,
            }
            for m in maps
        ],
    }
