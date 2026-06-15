from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MatchDetail(Base):
    __tablename__ = "match_details"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("matches.id", name="fk_md_match"), nullable=False)
    stage_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("match_stages.id", name="fk_md_stage"))
    game_no: Mapped[int | None] = mapped_column(Integer)
    map_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("maps.id", name="fk_md_map"))
    player_a_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    player_b_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    winner_player_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    loser_player_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    score_a: Mapped[int | None] = mapped_column(Integer, server_default="1")
    score_b: Mapped[int | None] = mapped_column(Integer, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_match_details_match", "match_id"),
        Index("idx_match_details_player_a", "player_a_id"),
        Index("idx_match_details_player_b", "player_b_id"),
        Index("idx_match_details_winner", "winner_player_id"),
    )
