"""CRUD operations."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from .engine import async_session_factory

T = TypeVar("T")

logger = logging.getLogger(__name__)


class CRUD:
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
        except Exception as e:
            await session.rollback()
            logger.exception("Failed to get session: %s", e)
            raise
        finally:
            await session.close()

    async def create(self, **kwargs) -> T:
        """Create a new record in the database."""
        async with self.get_session() as session:
            instance = self.model(**kwargs)
            session.add(instance)
            try:
                await session.commit()
                await session.refresh(instance)
                return instance
            except SQLAlchemyError as e:
                await session.rollback()
                logger.exception(
                    f"Failed to create {self.model.__name__}: {e}",
                )
                raise

    async def get(self, **kwargs) -> T:
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
            return query.scalars().all()

    async def update(self, instance: T, **kwargs) -> T:
        """Update a record's information."""
        async with self.get_session() as session:
            instance = await session.merge(instance)
            for key, value in kwargs.items():
                setattr(instance, key, value)
            try:
                await session.commit()
                await session.refresh(instance)
                return instance
            except SQLAlchemyError as e:
                await session.rollback()
                logger.exception(
                    f"Failed to update {self.model.__name__}: {e}",
                )
                raise

    async def delete(self, instance: T) -> bool:
        """Delete a record."""
        async with self.get_session() as session:
            instance = await session.merge(instance)
            try:
                await session.delete(instance)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                logger.exception(
                    f"Failed to delete {self.model.__name__}: {e}",
                )
                raise
