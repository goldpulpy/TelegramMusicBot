"""Required subscriptions database model."""
from sqlalchemy import Column, String, DateTime, Integer, BigInteger, func
from ..engine import Base


class RequiredSubscriptions(Base):
    """Required subscriptions model."""

    __tablename__ = "required_subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger)
    chat_title = Column(String)
    chat_link = Column(String)
    created_at = Column(DateTime, default=func.now())
