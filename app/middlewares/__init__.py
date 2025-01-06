"""Middlewares for the app."""
from aiogram import Dispatcher
from aiogram.utils.i18n import I18n
from .auth_middleware import AuthMiddleware
from .i18n_middleware import I18nMiddleware


def setup(dp: Dispatcher, i18n: I18n) -> None:
    """Setup middleware"""
    dp.update.outer_middleware(AuthMiddleware())
    dp.update.outer_middleware(I18nMiddleware(i18n))
