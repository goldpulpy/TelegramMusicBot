"""Texts for the bot."""

START: str = (
    "Hi, I'm a music search bot 🎶\n"
    "Just write the <b>author</b> or <b>title</b> and "
    "I will find it for you.\n\n<b>My source code is open:</b> "
    "<a href='https://github.com/goldpulpy/TelegramMusicBot'>github</a>"
)

ACCOUNT: str = (
    "<b>👤 Account information</b>\n\n"
    "<b>ID:</b> <code>{user_id}</code>\n"
    "<b>Username:</b> <code>{username}</code>\n"
    "<b>Name:</b> <code>{first_name}</code>\n"
    "<b>Date of registration:</b> <code>{date_registration}</code>\n"
    "<b>Search queries:</b> <code>{search_queries}</code>\n"
)

SEARCHING: str = "🔎 Searching..."

SEARCH_RESULTS: str = (
    "Search results for <b>{keyword}</b>\n\n"
    "Tap on the song to download it."
)

SENDING_SONG: str = "🎶 Sending song..."
