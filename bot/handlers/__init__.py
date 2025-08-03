"""Set up handlers for the bot."""

from aiogram import Dispatcher, Router

from bot.filters import IsPrivateChatFilter

from . import faq, get_track, language, menu, pages, search, subscribe


def setup(dp: Dispatcher) -> None:
    """Set up handlers for the bot."""
    router = Router()

    # Add filters
    router.message.filter(IsPrivateChatFilter())
    router.callback_query.filter(IsPrivateChatFilter())

    # Register routers
    language.register(router)
    menu.register(router)
    faq.register(router)
    search.register(router)
    pages.register(router)
    subscribe.register(router)
    get_track.register(router)

    dp.include_router(router)
