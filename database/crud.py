"""CRUD operations."""
import logging
from typing import AsyncGenerator, Type, TypeVar
from contextlib import asynccontextmanager

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
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
                logger.info(
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

    async def get(self, id: int) -> T:
        """Retrieve a record by ID."""
        async with self.get_session() as session:
            instance = await session.get(self.model, id)
            if instance:
                logger.info(
                    "%s retrieved with ID: %s", self.model.__name__, id
                )
            else:
                logger.warning(
                    "%s with ID %s not found.", self.model.__name__, id
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
                logger.info(
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
                logger.info(
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
