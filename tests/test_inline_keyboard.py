"""Tests for paginated inline track keyboards."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from bot.keyboards.inline import get_keyboard_of_tracks

if TYPE_CHECKING:
    from collections.abc import Callable

    from service.data import Track


def keyboard_rows(
    tracks: list[Track],
    page: int,
) -> list[list[tuple[str, str | None]]]:
    """Return visible labels and callback payloads for assertions."""
    keyboard = get_keyboard_of_tracks(tracks, 7, page)
    return [
        [(button.text, button.callback_data) for button in row]
        for row in keyboard.inline_keyboard
    ]


def test_empty_keyboard_has_no_rows() -> None:
    assert keyboard_rows([], 0) == []


def test_single_page_has_only_track_buttons(
    track_factory: Callable[..., Track],
) -> None:
    rows = keyboard_rows([track_factory(0), track_factory(1)], 0)
    assert rows == [
        [("Artist 0 - Title 0", "track:get:7:0")],
        [("Artist 1 - Title 1", "track:get:7:1")],
    ]


@pytest.mark.parametrize(
    ("page", "expected"),
    [
        (
            -1,
            (
                ("Artist 0 - Title 0", "track:get:7:0"),
                "1/3",
                ["track:noop", "track:noop", "track:page:7:1"],
                "track:all:7:0:10",
            ),
        ),
        (
            1,
            (
                ("Artist 10 - Title 10", "track:get:7:10"),
                "2/3",
                ["track:page:7:0", "track:noop", "track:page:7:2"],
                "track:all:7:10:20",
            ),
        ),
        (
            2,
            (
                ("Artist 20 - Title 20", "track:get:7:20"),
                "3/3",
                ["track:page:7:1", "track:noop", "track:noop"],
                "track:all:7:20:30",
            ),
        ),
        (
            99,
            (
                ("Artist 20 - Title 20", "track:get:7:20"),
                "3/3",
                ["track:page:7:1", "track:noop", "track:noop"],
                "track:all:7:20:30",
            ),
        ),
    ],
)
def test_multi_page_bounds_and_navigation(
    tracks: list[Track],
    page: int,
    expected: tuple[tuple[str, str], str, list[str], str],
) -> None:
    first_track, page_indicator, navigation, download = expected
    rows = keyboard_rows(tracks, page)
    assert rows[0] == [first_track]
    assert [row[0][0] for row in rows[:-2]] == [
        track.name for track in tracks[max(0, min(page, 2)) * 10 :][:10]
    ]
    assert rows[-2][1] == (page_indicator, "track:noop")
    assert [callback for _, callback in rows[-2]] == navigation
    assert rows[-1] == [("🔽", download)]
