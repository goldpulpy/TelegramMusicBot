"""Get track handler for the bot."""
import logging
from aiogram import types, Router, F, Bot
from aiogram.types import BufferedInputFile
from aiogram.utils.i18n import gettext
from service import Music, Track
from app.utils import load_tracks_from_db


logger = logging.getLogger(__name__)


async def send_track(
    callback: types.CallbackQuery,
    bot: Bot,
    track: Track
) -> None:
    """Send track."""
    try:
        await bot.send_chat_action(callback.message.chat.id, "upload_document")

        async with Music() as service:
            audio_bytes = await service.get_audio_bytes(track)
            thumbnail_bytes = await service.get_thumbnail_bytes(track)

            audio_file = BufferedInputFile(audio_bytes, filename=track.name)
            thumbnail_file = BufferedInputFile(
                thumbnail_bytes, filename=track.name
            )

        await callback.message.answer_audio(
            audio_file,
            title=track.title,
            performer=track.performer,
            caption=gettext("promo_caption").format(username=bot._me.username),
            thumbnail=thumbnail_file,
        )
    except Exception as e:
        await callback.message.answer(gettext("send_track_error"))
        logger.error("Failed to send track: %s", e)


async def get_track_handler(callback: types.CallbackQuery, bot: Bot) -> None:
    """Get track handler."""
    try:
        _, _, search_id, index = callback.data.split(":")
        tracks: list[Track] = await load_tracks_from_db(search_id)
        track: Track = tracks[int(index)]
        await callback.answer(gettext("track_sending"))
        await send_track(callback, bot, track)

    except Exception as e:
        logger.error("Failed get track handler: %s", e)


async def get_all_from_page_handler(
    callback: types.CallbackQuery, bot: Bot
) -> None:
    """Get all tracks from page handler."""
    try:
        _, _, search_id, start_indx, end_indx = callback.data.split(":")
        tracks: list[Track] = await load_tracks_from_db(search_id)
        tracks = tracks[int(start_indx):int(end_indx)]
        await callback.answer(gettext("track_sending"))
        for track in tracks:
            await send_track(callback, bot, track)

    except Exception as e:
        logger.error("Failed get all from page handler: %s", e)


def register(router: Router) -> None:
    """Registers get track handler with the router."""
    router.callback_query.register(
        get_track_handler, F.data.startswith("track:get:")
    )
    router.callback_query.register(
        get_all_from_page_handler, F.data.startswith("track:all:")
    )
