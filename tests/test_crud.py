"""Tests for generic database CRUD behavior."""

# pyright: reportArgumentType=false, reportAttributeAccessIssue=false

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from database.crud import CRUD


class Model:
    """Small model double accepted by CRUD."""

    def __init__(self, **values: object) -> None:
        self.__dict__.update(values)


@pytest.mark.asyncio
async def test_get_returns_scalar(async_session: MagicMock) -> None:
    expected = Model(id=1)
    result = MagicMock()
    result.scalar_one_or_none.return_value = expected
    async_session.execute.return_value = result

    with patch("database.crud.select", return_value=MagicMock()):
        actual = await CRUD(Model, lambda: async_session).get(id=1)
    assert actual is expected
    async_session.execute.assert_awaited_once()
    async_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_returns_list(async_session: MagicMock) -> None:
    expected = [Model(id=1), Model(id=2)]
    result = MagicMock()
    result.scalars.return_value.all.return_value = expected
    async_session.execute.return_value = result

    with patch("database.crud.select", return_value=MagicMock()):
        actual = await CRUD(Model, lambda: async_session).get_all()
    assert actual == expected
    async_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_commits_refreshes_and_closes(
    async_session: MagicMock,
) -> None:
    created = await CRUD(Model, lambda: async_session).create(name="test")

    assert created.name == "test"
    async_session.add.assert_called_once_with(created)
    async_session.commit.assert_awaited_once()
    async_session.refresh.assert_awaited_once_with(created)
    async_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_sets_values_and_persists(
    async_session: MagicMock,
) -> None:
    instance = Model(name="old")

    result = await CRUD(Model, lambda: async_session).update(
        instance,
        name="new",
    )

    assert result is instance
    assert instance.name == "new"
    async_session.add.assert_called_once_with(instance)
    async_session.commit.assert_awaited_once()
    async_session.refresh.assert_awaited_once_with(instance)


@pytest.mark.asyncio
async def test_delete_commits_and_closes(async_session: MagicMock) -> None:
    instance = Model(id=1)

    assert await CRUD(Model, lambda: async_session).delete(instance)
    async_session.delete.assert_awaited_once_with(instance)
    async_session.commit.assert_awaited_once()
    async_session.close.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["create", "update", "delete"])
async def test_mutation_rolls_back_and_propagates(
    async_session: MagicMock,
    method: str,
) -> None:
    error = SQLAlchemyError("database failed")
    async_session.commit.side_effect = error
    crud = CRUD(Model, lambda: async_session)

    with pytest.raises(SQLAlchemyError) as raised:
        if method == "create":
            await crud.create(name="test")
        elif method == "update":
            await crud.update(Model(), name="test")
        else:
            await crud.delete(Model())

    assert raised.value is error
    assert async_session.rollback.await_count >= 1
    async_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_session_scoped_failure_rolls_back_and_closes(
    async_session: MagicMock,
) -> None:
    error = RuntimeError("query failed")
    async_session.execute = AsyncMock(side_effect=error)

    with (
        patch("database.crud.select", return_value=MagicMock()),
        pytest.raises(RuntimeError) as raised,
    ):
        await CRUD(Model, lambda: async_session).get(id=1)

    assert raised.value is error
    async_session.rollback.assert_awaited_once()
    async_session.close.assert_awaited_once()
