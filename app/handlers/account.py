"""Account handler for the bot."""
import logging
from aiogram import types, Router, F
from aiogram.filters import Command
from database.models.user import User
from templates import texts


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def account_handler(message: types.Message, user: User) -> None:
    """Handles the account."""
    try:
        await message.answer(
            texts.ACCOUNT.format(
                user_id=user.id,
                first_name=user.first_name,
                username=user.username if user.username else "-",
                search_queries=user.search_queries,
                date_registration=user.created_at.strftime(
                    "%d.%m.%Y %H:%M:%S"
                )
            )
        )
    except Exception as e:
        logger.error(f"Failed to send message: {e}")


def register(router: Router) -> None:
    """Registers account handler with the router."""
    router.message.register(account_handler, Command("account"))
    router.message.register(account_handler, F.text == "👤 Account")
