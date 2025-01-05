"""Song map database model."""
from sqlalchemy import Column, String, DateTime, func, Integer
from ..engine import Base


class Song(Base):
    """Song map model."""

    __tablename__ = "song_map"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hash = Column(String)
    name = Column(String)
    created_at = Column(DateTime, default=func.now())
