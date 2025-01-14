"""Subscription required database model."""
from sqlalchemy import Column, String, DateTime, Integer, BigInteger, func
from ..engine import Base


class SubscriptionRequired(Base):
    """Subscription required model."""

    __tablename__ = "subscription_required"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger)
    chat_title = Column(String)
    chat_link = Column(String)
    created_at = Column(DateTime, default=func.now())
