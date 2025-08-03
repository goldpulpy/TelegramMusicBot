"""Search history database model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from database.engine import Base


class SearchHistory(Base):
    """Search history model."""

    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    keyword: Mapped[str | None] = mapped_column(String, default=None)
    tracks: Mapped[list[dict[str, str]]] = mapped_column(JSONB, default=[])

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )
