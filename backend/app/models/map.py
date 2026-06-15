from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Map(Base):
    __tablename__ = "maps"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    map_uid: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    kr_name: Mapped[str | None] = mapped_column(String(200))
    en_name: Mapped[str | None] = mapped_column(String(200))
    cn_name: Mapped[str | None] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
