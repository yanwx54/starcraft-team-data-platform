from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MatchStage(Base):
    __tablename__ = "match_stages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("matches.id"), nullable=False)
    stage_type: Mapped[str] = mapped_column(String(20), nullable=False)
    stage_order: Mapped[int] = mapped_column(Integer, nullable=False)
    winner_team_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("teams.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
