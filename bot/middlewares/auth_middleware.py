"""Auth middleware module for the bot."""
import logging
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Update

from database.crud import CRUD
from database.models import User


logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """Auth middleware for handling user registration in the database."""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        """Intercepts incoming updates, processes them and calls the next."""
        data['user'] = await self.ensure_user_in_db(data['event_from_user'])
        return await handler(event, data)

    async def ensure_user_in_db(self, user: User) -> User:
        """Ensures that the user is registered in the database."""
        user_crud = self._get_user_crud()
        user_data = self._prepare_user_data(user)

        try:
            return await self._get_or_create_user(
                user, user_crud, user_data
            )

        except Exception as e:
            logger.error("Failed to process user %s: %s", user.id, str(e))
            raise

    def _get_user_crud(self) -> CRUD:
        """Creates CRUD instance for User model."""
        return CRUD(User)

    @staticmethod
    def _prepare_user_data(user: User) -> Dict[str, Any]:
        """Prepares user data for database operations."""
        return {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }

    @staticmethod
    async def _get_or_create_user(
        user: User,
        user_crud: CRUD,
        user_data: Dict[str, Any]
    ) -> User:
        """Gets existing user or creates new one."""
        db_user = await user_crud.get(id=user.id)

        if not db_user:
            user_data['language_code'] = user.language_code
            db_user = await user_crud.create(**user_data)
            logger.info("User %s registered in the database.", user.id)

        else:
            user_data['updated_at'] = datetime.now()
            db_user = await user_crud.update(db_user, **user_data)
            logger.info("User %s updated in the database.", user.id)

        return db_user
