from functions import *

bot = AsyncTeleBot(BOT_API_KEY,
                   disable_web_page_preview=True,
                   parse_mode="markdown")

# Configure logging
logging.basicConfig(
    filename="LongCaptionBot.log",  # Log file name
    filemode="a",  # Append to the file, use 'w' to overwrite
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S",  # Date-time format
    level=logging.INFO,  # Set the logging level
)

MEDIA_CONTENT_TYPES = [
    "photo",
    "video",
    "document",
    "audio",
    "animation",
    "voice",
    "video_note",
]

# Debounced jobs when an album is sent as a reply to caption text.
_album_reply_tasks: dict[tuple[int, str], asyncio.Task] = {}


def _message_has_media(msg) -> bool:
    return any(
        getattr(msg, field, None)
        for field in (
            "photo",
            "video",
            "document",
            "audio",
            "animation",
            "voice",
            "video_note",
        )
    )


def _caption_text(msg) -> str:
    return (msg.text or msg.caption or "") if msg else ""


async def merge_and_return(chat_id, media_message_ids, caption_message_id, language_code):
    """Copy media (single or album) + caption to the log channel, apply caption, return media to user."""
    if len(media_message_ids) == 1:
        media_log = await bot.copy_message(
            LONG_CAPTION_CHANNEL_ID, chat_id, media_message_ids[0]
        )
        media_log_ids = [media_log.message_id]
    else:
        media_log = await bot.copy_messages(
            LONG_CAPTION_CHANNEL_ID, chat_id, media_message_ids
        )
        media_log_ids = [item.message_id for item in media_log]

    caption_log = await bot.copy_message(
        LONG_CAPTION_CHANNEL_ID, chat_id, caption_message_id
    )
    # Album captions live on the first item of the media group.
    await private_router_apply_caption(
        LONG_CAPTION_CHANNEL_ID,
        media_log_ids[0],
        caption_log.message_id,
    )
    await bot.delete_message(LONG_CAPTION_CHANNEL_ID, caption_log.message_id)

    if len(media_log_ids) == 1:
        await bot.copy_message(chat_id, LONG_CAPTION_CHANNEL_ID, media_log_ids[0])
    else:
        returned = await bot.copy_messages(
            chat_id, LONG_CAPTION_CHANNEL_ID, media_log_ids
        )
        # Bot-sent albums never arrive as inbound updates — index them so
        # a later text reply to any item still resolves the whole pack.
        remember_album_ids(chat_id, [item.message_id for item in returned])

    if language_code == "fa":
        pass
    else:
        await bot.send_message(chat_id, success_message, parse_mode="markdown")


async def _merge_media_replied_to_text(message) -> None:
    """Media (or full album) was replied to a caption text message."""
    reply = message.reply_to_message
    caption = _caption_text(reply)
    if len(caption) < 1024:
        await bot.send_message(
            message.chat.id, short_caption_message, parse_mode="markdown"
        )
        await bot.send_message(LONG_CAPTION_CHANNEL_ID, "short caption received")
        return

    if message.media_group_id:
        media_ids = resolve_media_message_ids(message.chat.id, message)
    else:
        media_ids = [message.message_id]

    await merge_and_return(
        message.chat.id,
        media_ids,
        reply.message_id,
        message.from_user.language_code,
    )


async def main():
    @bot.message_handler(commands=["start"])
    async def start_command_(message):
        await bot.send_message(
            message.chat.id,
            "Hi. send a media like photo, video, voice, ... then send some large text replied to it. I will merge them and bring back to you.\n\nmy video tutorial is available too: https://youtu.be/L\\_hdOd8KGvQ",
            parse_mode="markdown",
        )

    @bot.message_handler(content_types=MEDIA_CONTENT_TYPES)
    async def buffer_media(message):
        # Needed so a later text reply to any album item can copy the whole pack.
        remember_album_message(message)

        reply = message.reply_to_message
        if not reply or not _caption_text(reply):
            return

        if message.media_group_id:
            key = (message.chat.id, str(message.media_group_id))
            previous = _album_reply_tasks.get(key)
            if previous and not previous.done():
                previous.cancel()

            async def _run_after_album_settles():
                try:
                    await asyncio.sleep(1.5)
                    await _merge_media_replied_to_text(message)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logging.error(
                        f"An error occurred: {e}\nTraceback:\n{traceback.format_exc()}"
                    )
                finally:
                    current = _album_reply_tasks.get(key)
                    if current is asyncio.current_task():
                        _album_reply_tasks.pop(key, None)

            _album_reply_tasks[key] = asyncio.create_task(_run_after_album_settles())
            return

        try:
            await _merge_media_replied_to_text(message)
        except Exception as e:
            logging.error(
                f"An error occurred: {e}\nTraceback:\n{traceback.format_exc()}"
            )

    @bot.message_handler(content_types=["text"])
    async def handle_media_reply(message):
        if not message.reply_to_message:
            await bot.send_message(
                message.chat.id,
                "your text message should be replied to a media message.",
            )
            return

        reply = message.reply_to_message
        if not _message_has_media(reply):
            await bot.send_message(
                message.chat.id,
                "your text message should be replied to a media message.",
            )
            return

        try:
            if len(message.text) < 1024:
                await bot.send_message(
                    message.chat.id, short_caption_message, parse_mode="markdown"
                )
                await bot.send_message(LONG_CAPTION_CHANNEL_ID, "short caption received")
                return

            media_ids = resolve_media_message_ids(message.chat.id, reply)
            logging.info(
                "text-reply album resolve: chat=%s reply_id=%s group=%s ids=%s",
                message.chat.id,
                reply.message_id,
                getattr(reply, "media_group_id", None),
                media_ids,
            )
            await merge_and_return(
                message.chat.id,
                media_ids,
                message.message_id,
                message.from_user.language_code,
            )
        except Exception as e:
            logging.error(
                f"An error occurred: {e}\nTraceback:\n{traceback.format_exc()}"
            )

    await bot.infinity_polling()


if __name__ == "__main__":
    asyncio.run(main())
