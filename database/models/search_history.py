"""Search history database model."""
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import (
    Column, String, DateTime, Integer, BigInteger, ForeignKey, func
)
from ..engine import Base


class SearchHistory(Base):
    """Search history model."""

    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    keyword = Column(String, default=None)
    tracks = Column(JSONB, default=[])
    created_at = Column(DateTime, default=func.now())
