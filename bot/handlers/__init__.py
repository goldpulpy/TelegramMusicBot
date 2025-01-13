"""Setup router for the bot."""
from aiogram import Dispatcher, Router
from . import (
    get_track,
    language,
    menu,
    faq,
    search,
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
    get_track.register(router)

    dp.include_router(router)
