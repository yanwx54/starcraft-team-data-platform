from sqlalchemy.orm import Session

from app.models.data_issue import DataIssue
from app.models.translation_rule import TranslationRule
from app.translate.parser import parse_translate_rules


class PlayerTranslator:
    """选手名称翻译器。

    翻译优先级：
    Level 1 — translate_rules.md（内存）
    Level 2 — translation_rules 数据库
    Level 3 — 保留原文 + 记录异常
    """

    def __init__(self, db: Session, rules_file: str | None = None):
        self.db = db
        self._md_rules: dict[str, str] = {}

        if rules_file:
            self._load_md_rules(rules_file)

    def _load_md_rules(self, rules_file: str):
        """加载 translate_rules.md 到内存。"""
        try:
            rules = parse_translate_rules(rules_file)
            for player in rules.players:
                self._md_rules[player.kr_name] = player.cn_name
                self._md_rules[player.kr_short] = player.cn_name
        except FileNotFoundError:
            pass

    def translate_player(self, name: str, match_id: int | None = None) -> str:
        """翻译选手名称。

        匹配顺序：韩文全名 → 韩文简称 → 历史别名 → 游戏ID
        （调用方按此顺序依次调用，本方法负责单次查找）

        Args:
            name: 待翻译的选手名称
            match_id: 关联的比赛ID，用于异常记录

        Returns:
            翻译后的中文名称；未命中则返回原文
        """
        if not name:
            return name

        # Level 1: md 规则
        if name in self._md_rules:
            return self._md_rules[name]

        # Level 2: 数据库规则
        db_rule = self.db.query(TranslationRule).filter_by(
            rule_type="player",
            source_text=name,
        ).first()

        if db_rule:
            return db_rule.translated_text

        # Level 3: 保留原文 + 记录异常
        self._log_translation_error(name, match_id)
        return name

    def _log_translation_error(self, original_name: str, match_id: int | None = None):
        """记录 translation_error 到 data_issues 表。"""
        description = f"未知选手: {original_name}"
        if match_id is not None:
            description += f", 比赛ID: {match_id}"

        issue = DataIssue(
            issue_type="translation_error",
            source_table="players",
            description=description,
        )
        self.db.add(issue)
        self.db.commit()
