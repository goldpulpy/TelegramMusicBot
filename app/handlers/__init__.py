"""Setup router for the bot."""
from aiogram import Dispatcher, Router
from . import (
    language,
    menu,
    faq,
    search,
    get_song,
    pages
)


def setup(dp: Dispatcher) -> None:
    """Setup handlers for the bot."""
    router = Router()

    # Register routers
    language.register(router)
    menu.register(router)
    faq.register(router)
    search.register(router)
    pages.register(router)
    get_song.register(router)

    dp.include_router(router)
