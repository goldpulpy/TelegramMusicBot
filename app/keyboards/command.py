"""Command keyboard for the bot."""
from typing import Callable
from aiogram.types import BotCommand


def get_commands(gettext: Callable[[str], str]) -> list[BotCommand]:
    """Get commands for the bot."""
    return [
        BotCommand(command="start", description=gettext("start_command")),
        BotCommand(command="language", description=gettext("language_command"))
    ]
