"""Search handler for the bot."""
import logging
from aiogram import types, Router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def search_handler(message: types.Message) -> None:
    """Handles the search."""
    try:
        await message.answer(
            "Searching..."
        )
        # TODO: Search for the song
    except Exception as e:
        logger.error(f"Failed to send message: {e}")


def register(router: Router) -> None:
    """Registers start handler with the router."""
    router.message.register(search_handler)
