from sqlalchemy.orm import Session

from app.models.translation_rule import TranslationRule
from app.translate.parser import TranslateRules


def import_rules_to_db(db: Session, rules: TranslateRules) -> dict:
    """将翻译规则导入数据库。已存在则跳过，不存在则新增。禁止覆盖已有规则。"""
    added = 0
    skipped = 0

    for player in rules.players:
        # 韩文全名 → 中文名
        a, s = _upsert_rule(
            db,
            rule_type="player",
            source_text=player.kr_name,
            translated_text=player.cn_name,
            alias_group=player.cn_name,
        )
        added += a
        skipped += s

        # 韩文简称 → 中文名
        a, s = _upsert_rule(
            db,
            rule_type="player",
            source_text=player.kr_short,
            translated_text=player.cn_name,
            alias_group=player.cn_name,
        )
        added += a
        skipped += s

    for map_rule in rules.maps:
        # 韩文全称 → 中文名
        a, s = _upsert_rule(
            db,
            rule_type="map",
            source_text=map_rule.kr_name,
            translated_text=map_rule.cn_name,
            alias_group=map_rule.cn_name,
        )
        added += a
        skipped += s

        # 韩文简称 → 中文名
        a, s = _upsert_rule(
            db,
            rule_type="map",
            source_text=map_rule.kr_short,
            translated_text=map_rule.cn_name,
            alias_group=map_rule.cn_name,
        )
        added += a
        skipped += s

        # 英文名 → 中文名
        a, s = _upsert_rule(
            db,
            rule_type="map",
            source_text=map_rule.en_name,
            translated_text=map_rule.cn_name,
            alias_group=map_rule.cn_name,
        )
        added += a
        skipped += s

    db.commit()

    return {"added": added, "skipped": skipped}


def _upsert_rule(
    db: Session,
    rule_type: str,
    source_text: str,
    translated_text: str,
    alias_group: str,
) -> tuple[int, int]:
    """新增规则（不存在时），跳过（已存在时）。返回 (added, skipped)。"""
    existing = db.query(TranslationRule).filter_by(
        rule_type=rule_type,
        source_text=source_text,
    ).first()

    if existing:
        return 0, 1

    rule = TranslationRule(
        rule_type=rule_type,
        source_text=source_text,
        translated_text=translated_text,
        alias_group=alias_group,
    )
    db.add(rule)
    return 1, 0
