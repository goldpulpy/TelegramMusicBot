"""Setup router for the bot."""
from aiogram import Dispatcher, Router
from . import start, search, account


def setup(dp: Dispatcher) -> None:
    """Setup handlers for the bot."""
    router = Router()

    # Register routers
    start.register(router)
    account.register(router)
    search.register(router)

    dp.include_router(router)
