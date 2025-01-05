"""State filter."""

from aiogram.filters import Filter
from database.models.user import User


class StateFilter(Filter):
    """
    A filter that checks if a user's state matches the specified state.
    """

    def __init__(self, state: str) -> None:
        """
        Initialize the filter with the desired state.
        """
        self.state = state

    async def __call__(self, user: User) -> bool:
        """
        Check if the user's state matches the specified state.
        """
        return user.state == self.state
