from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PlayerRule:
    kr_name: str
    kr_short: str
    cn_name: str


@dataclass
class MapRule:
    kr_name: str
    kr_short: str
    en_name: str
    cn_name: str


@dataclass
class TranslateRules:
    players: list[PlayerRule] = field(default_factory=list)
    maps: list[MapRule] = field(default_factory=list)

    def player_count(self) -> int:
        return len(self.players)

    def map_count(self) -> int:
        return len(self.maps)


def parse_translate_rules(file_path: str | Path) -> TranslateRules:
    """解析 translate_rules.md，返回结构化规则数据。

    选手格式：韩文全名|韩文简称|中文名
    地图格式：韩文全称|韩文简称|英文名|中文名
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"翻译规则文件未找到: {path}")

    content = path.read_text(encoding="utf-8")
    lines = content.strip().splitlines()

    players: list[PlayerRule] = []
    maps: list[MapRule] = []

    current_section: str | None = None

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("#"):
            if "PLAYERS" in stripped:
                current_section = "players"
            elif "MAPS" in stripped:
                current_section = "maps"
            continue

        parts = stripped.split("|")

        if current_section == "players" and len(parts) == 3:
            players.append(PlayerRule(
                kr_name=parts[0].strip(),
                kr_short=parts[1].strip(),
                cn_name=parts[2].strip(),
            ))
        elif current_section == "maps" and len(parts) == 4:
            maps.append(MapRule(
                kr_name=parts[0].strip(),
                kr_short=parts[1].strip(),
                en_name=parts[2].strip(),
                cn_name=parts[3].strip(),
            ))

    return TranslateRules(players=players, maps=maps)
