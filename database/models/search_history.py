"""Search history database model."""
from sqlalchemy import (
    Column, String, DateTime, func, Integer, BigInteger, ForeignKey
)
from ..engine import Base


class SearchHistory(Base):
    """Search history model."""

    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    keyword = Column(String, default=None)
    created_at = Column(DateTime, default=func.now())
