from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RawArticle(Base):
    __tablename__ = "raw_articles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    wr_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    title: Mapped[str | None] = mapped_column(String(500))
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    article_date: Mapped[date | None] = mapped_column(Date)
    html_content: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_raw_articles_wr_id", "wr_id"),
        Index("idx_raw_articles_date", "article_date"),
    )
