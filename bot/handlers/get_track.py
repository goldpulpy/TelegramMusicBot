"""Get track handler for the bot."""

import logging

from aiogram import Bot, F, Router, types
from aiogram.types import BufferedInputFile
from aiogram.utils.i18n import gettext

from bot.utils import get_user_pic, load_tracks_from_db
from service import Music, Track

logger = logging.getLogger(__name__)


async def send_track(
    callback: types.CallbackQuery,
    bot: Bot,
    track: Track,
) -> None:
    """Send track."""
    try:
        if callback.message is None or callback.message.chat is None:
            await callback.answer(gettext("cannot_access_chat"))
            return

        await bot.send_chat_action(callback.message.chat.id, "upload_document")

        async with Music() as service:
            audio_bytes = await service.get_audio_bytes(track)

            audio_file = BufferedInputFile(audio_bytes, filename=track.name)

        me = await bot.get_me()

        if callback.message is None:
            await callback.answer(gettext("cannot_send_message"))
            return

        await callback.message.answer_audio(
            audio_file,
            title=track.title,
            performer=track.performer,
            caption=gettext("promo_caption").format(username=me.username),
            thumbnail=await get_user_pic(bot, me),
        )
    except Exception:
        if callback.message is not None:
            await callback.message.answer(gettext("send_track_error"))
        else:
            await callback.answer(gettext("send_track_error"))
        logger.exception("Failed to send track")


async def get_track_handler(callback: types.CallbackQuery, bot: Bot) -> None:
    """Get track handler."""
    try:
        if callback.data is None:
            await callback.answer(gettext("invalid_data"))
            return

        _, _, search_id_str, index = callback.data.split(":")
        search_id = int(search_id_str)
        tracks: list[Track] = await load_tracks_from_db(search_id)
        track: Track = tracks[int(index)]
        await callback.answer(gettext("track_sending"))
        await send_track(callback, bot, track)

    except Exception:
        logger.exception("Failed get track handler")


async def get_all_from_page_handler(
    callback: types.CallbackQuery,
    bot: Bot,
) -> None:
    """Get all tracks from page handler."""
    try:
        if callback.data is None:
            await callback.answer(gettext("invalid_data"))
            return

        _, _, search_id_str, start_indx, end_indx = callback.data.split(":")
        search_id = int(search_id_str)
        all_tracks: list[Track] = await load_tracks_from_db(search_id)
        page_tracks = all_tracks[int(start_indx) : int(end_indx)]
        await callback.answer(gettext("track_sending"))
        for track in page_tracks:
            await send_track(callback, bot, track)

    except Exception:
        logger.exception("Failed get all from page handler")


def register(router: Router) -> None:
    """Register get track handler with the router."""
    router.callback_query.register(
        get_track_handler,
        F.data.startswith("track:get:"),
    )
    router.callback_query.register(
        get_all_from_page_handler,
        F.data.startswith("track:all:"),
    )
