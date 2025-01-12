"""CRUD operations."""
import logging
from typing import AsyncGenerator, Type, TypeVar
from contextlib import asynccontextmanager

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from .engine import async_session_factory


T = TypeVar('T')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUD:
    """Generic class to handle CRUD operations for any model."""

    def __init__(
        self,
        model: Type[T],
        session_factory: sessionmaker = async_session_factory
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
                logger.debug(
                    "%s created with ID: %s", self.model.__name__,
                    getattr(instance, 'id', 'unknown')
                )
                return instance
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(
                    f"Failed to create {self.model.__name__}: {e}"
                )
                raise

    async def get(self, **kwargs) -> T:
        """Retrieve a record by any field."""
        async with self.get_session() as session:
            query = await session.execute(
                select(self.model).filter_by(**kwargs)
            )
            instance = query.scalar_one_or_none()

            if instance:
                logger.debug(
                    "%s retrieved with filters: %s", self.model.__name__,
                    kwargs
                )
            else:
                logger.debug(
                    "%s not found with filters: %s", self.model.__name__,
                    kwargs
                )
            return instance

    async def update(self, instance: T, **kwargs) -> T:
        """Update a record's information."""
        async with self.get_session() as session:
            instance = await session.merge(instance)
            for key, value in kwargs.items():
                setattr(instance, key, value)
            try:
                await session.commit()
                await session.refresh(instance)
                logger.debug(
                    "%s updated with ID: %s", self.model.__name__,
                    getattr(instance, 'id', 'unknown')
                )
                return instance
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(
                    f"Failed to update {self.model.__name__}: {e}"
                )
                raise

    async def delete(self, instance: T) -> bool:
        """Delete a record."""
        async with self.get_session() as session:
            instance = await session.merge(instance)
            try:
                await session.delete(instance)
                await session.commit()
                logger.debug(
                    "%s deleted with ID: %s", self.model.__name__,
                    getattr(instance, 'id', 'unknown')
                )
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(
                    f"Failed to delete {self.model.__name__}: {e}"
                )
                raise
