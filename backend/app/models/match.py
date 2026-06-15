from datetime import date, datetime

from sqlalchemy import BigInteger, Date, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    wr_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    season_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("seasons.id"), nullable=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    match_date: Mapped[date] = mapped_column(Date, nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    team_a_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=True)
    team_b_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=True)
    winner_team_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("teams.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
