"""Get song handler for the bot."""
import logging
from aiogram import types, Router, F, Bot
from aiogram.types import BufferedInputFile
from service.core import MusicService
from service.data import Song

from app.utils import load_songs_from_db
from templates import texts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_song_handler(callback: types.CallbackQuery, bot: Bot) -> None:
    """Get song handler."""
    try:
        _, _, search_id, song_index = callback.data.split(":")
        songs: list[Song] = await load_songs_from_db(search_id)
        song: Song = songs[int(song_index)]

        await callback.answer(texts.SENDING_SONG)
        await bot.send_chat_action(callback.message.chat.id, "upload_document")

        async with MusicService() as service:
            song_bytes = await service.get_song_bytes(song)
            thumbnail_bytes = await service.get_thumbnail_bytes(song)

        audio_file = BufferedInputFile(song_bytes, filename=song.name)
        thumbnail_file = BufferedInputFile(thumbnail_bytes, filename=song.name)

        await callback.message.answer_audio(
            audio_file,
            title=song.title,
            performer=song.performer,
            caption=texts.PROMO_CAPTION.format(username=bot._me.username),
            thumbnail=thumbnail_file,
        )

    except Exception as e:
        await callback.message.answer(texts.ERROR)
        logger.error(f"Failed to send song: {e}")


def register(router: Router) -> None:
    """Registers get song handler with the router."""
    router.callback_query.register(
        get_song_handler, F.data.startswith("song:get:")
    )
