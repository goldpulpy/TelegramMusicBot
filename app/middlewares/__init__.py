"""Middlewares for the app."""
from aiogram import Dispatcher
from .middleware import Middleware


def setup(dp: Dispatcher) -> None:
    """Setup middleware"""
    dp.update.outer_middleware(Middleware())
