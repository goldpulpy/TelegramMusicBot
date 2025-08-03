"""Database CRUD operations."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .engine import async_session_factory

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker


T = TypeVar("T")

logger = logging.getLogger(__name__)


class CRUD(Generic[T]):
    """Generic class to handle CRUD operations for any model."""

    def __init__(
        self,
        model: type[T],
        session_factory: sessionmaker = async_session_factory,
    ) -> None:
        """Initialize the CRUD class."""
        self.model = model
        self.session_factory = session_factory

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an asynchronous session."""
        session = self.session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            logger.exception("Failed to get session")
            raise
        finally:
            await session.close()

    async def create(self, **kwargs: Any) -> T:  # noqa: ANN401
        """Create a new record in the database."""
        async with self.get_session() as session:
            try:
                instance = self.model(**kwargs)
                session.add(instance)
                await session.commit()
                await session.refresh(instance)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception(
                    "Failed to create %s",
                    self.model.__name__,
                )
                raise
            return instance

    async def get(self, **kwargs: Any) -> T | None:  # noqa: ANN401
        """Retrieve a record by any field."""
        async with self.get_session() as session:
            query = await session.execute(
                select(self.model).filter_by(**kwargs),
            )
            return query.scalar_one_or_none()

    async def get_all(self) -> list[T]:
        """Get all records."""
        async with self.get_session() as session:
            query = await session.execute(select(self.model))
            return list(query.scalars().all())

    async def update(self, instance: T, **kwargs: Any) -> T:  # noqa: ANN401
        """Update a record's information."""
        async with self.get_session() as session:
            try:
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                session.add(instance)
                await session.commit()
                await session.refresh(instance)
            except SQLAlchemyError:
                await session.rollback()
                logger.exception(
                    "Failed to update %s",
                    self.model.__name__,
                )
                raise

            return instance

    async def delete(self, instance: T) -> bool:
        """Delete a record from the database."""
        async with self.get_session() as session:
            try:
                await session.delete(instance)
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()
                logger.exception(
                    "Failed to delete %s",
                    self.model.__name__,
                )
                raise
            return True
