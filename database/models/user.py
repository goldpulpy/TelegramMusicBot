"""User database model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.engine import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    username: Mapped[str | None] = mapped_column(String, default=None)
    first_name: Mapped[str | None] = mapped_column(String, default=None)
    last_name: Mapped[str | None] = mapped_column(String, default=None)
    language_code: Mapped[str | None] = mapped_column(String, default=None)
    state: Mapped[str | None] = mapped_column(String, default=None)
    search_queries: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
