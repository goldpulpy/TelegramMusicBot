"""Get song handler for the bot."""
import logging
from aiogram import types, Router, F, Bot
from aiogram.types import BufferedInputFile
from aiogram.utils.i18n import gettext
from service.core import MusicService
from service.data import Song
from app.utils import load_songs_from_db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_song(
    callback: types.CallbackQuery,
    bot: Bot,
    song: Song
) -> None:
    """Send song."""
    try:
        await bot.send_chat_action(callback.message.chat.id, "upload_document")

        async with MusicService() as service:
            song_bytes = await service.get_song_bytes(song)
            thumbnail_bytes = await service.get_thumbnail_bytes(song)

            audio_file = BufferedInputFile(song_bytes, filename=song.name)
            thumbnail_file = BufferedInputFile(
                thumbnail_bytes, filename=song.name
            )

        await callback.message.answer_audio(
            audio_file,
            title=song.title,
            performer=song.performer,
            caption=gettext("promo_caption").format(username=bot._me.username),
            thumbnail=thumbnail_file,
        )
    except Exception as e:
        await callback.message.answer(gettext("error"))
        logger.error(f"Failed to send song: {e}")


async def get_song_handler(callback: types.CallbackQuery, bot: Bot) -> None:
    """Get song handler."""
    try:
        _, _, search_id, song_index = callback.data.split(":")
        songs: list[Song] = await load_songs_from_db(search_id)
        song: Song = songs[int(song_index)]
        await callback.answer(gettext("song_sending"))
        await send_song(callback, bot, song)

    except Exception as e:
        logger.error(f"Failed get song handler: {e}")


async def get_all_from_page_handler(
    callback: types.CallbackQuery, bot: Bot
) -> None:
    """Get all songs from page handler."""
    try:
        _, _, search_id, start_indx, end_indx = callback.data.split(":")
        songs: list[Song] = await load_songs_from_db(search_id)
        songs = songs[int(start_indx):int(end_indx)]
        await callback.answer(gettext("song_sending"))
        for song in songs:
            await send_song(callback, bot, song)

    except Exception as e:
        logger.error(f"Failed get all from page handler: {e}")


def register(router: Router) -> None:
    """Registers get song handler with the router."""
    router.callback_query.register(
        get_song_handler, F.data.startswith("song:get:")
    )
    router.callback_query.register(
        get_all_from_page_handler, F.data.startswith("song:all:")
    )
