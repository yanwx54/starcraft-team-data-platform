from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    player_uid: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    kr_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    game_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cn_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    race: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
