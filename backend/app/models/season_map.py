from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SeasonMap(Base):
    __tablename__ = "season_maps"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    season_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("seasons.id"), nullable=False)
    map_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("maps.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("season_id", "map_id", name="uq_season_map"),
    )
