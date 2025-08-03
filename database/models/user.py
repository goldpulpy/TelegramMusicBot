"""User database model."""

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, func

from database.engine import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String, default=None)
    first_name = Column(String, default=None)
    last_name = Column(String, default=None)
    language_code = Column(String, default=None)
    state = Column(String, default=None)
    search_queries = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
