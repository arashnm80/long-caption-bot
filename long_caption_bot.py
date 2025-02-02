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

async def main():
    # Create async telethon client with telegram app api
    telethon_client = TelegramClient(session_name, TELEGRAM_APP_API_ID, TELEGRAM_APP_API_HASH, proxy=warp_proxy)
    await telethon_client.start()

    # Define a basic command handler
    @bot.message_handler(commands=['start'])
    async def start_command_(message):
        await bot.send_message(message.chat.id, "Hi. send a large text, then send an image replied to it. I will merge them and send it to you.")
        
    # Function to handle replies to media messages
    @bot.message_handler(content_types=['photo'])
    async def handle_media_reply(message):
        # Check if the message is a reply
        if message.reply_to_message:
            try:
                # forward photo to log channel
                photo_log_message_telebot = await bot.copy_message(LONG_CAPTION_CHANNEL_ID, message.chat.id, message.message_id)
                # forward caption to log channel
                caption_log_message_telebot = await bot.copy_message(LONG_CAPTION_CHANNEL_ID, message.chat.id, message.reply_to_message.message_id)
                # get caption text and entities from log channel in telethon format
                caption_log_message_telethon = await telethon_client.get_messages(
                    entity=int(LONG_CAPTION_CHANNEL_ID),
                    ids=caption_log_message_telebot.message_id,
                )
                telethon_caption_text = caption_log_message_telethon.raw_text
                telethon_caption_entities = caption_log_message_telethon.entities
                # edit the caption of photo in log channel
                await telethon_client.edit_message(
                    entity=int(LONG_CAPTION_CHANNEL_ID),
                    message=photo_log_message_telebot.message_id,
                    text=telethon_caption_text,
                    formatting_entities=telethon_caption_entities,
                )
                # copy the edited photo to user and send success message
                await bot.copy_message(message.chat.id, LONG_CAPTION_CHANNEL_ID, photo_log_message_telebot.message_id)
                await bot.send_message(message.chat.id, success_message, parse_mode="markdown")
            except Exception as e:
                # Log the error with additional context
                logging.error(f"An error occurred: {e}\nTraceback:\n{traceback.format_exc()}")
        else:
            # If the media message isn't a reply, you can handle it differently
            await bot.send_message(message.chat.id, "This is a photo message, but not a reply. reply it to your long desired text.")
    
    # Set bot to infinity polling
    try:
        await bot.infinity_polling()
    
    finally:
        # Always ensure Telethon client disconnects, even on error
        print("Disconnecting Telethon client...")
        await telethon_client.disconnect()

# Entry point
if __name__ == "__main__":
    asyncio.run(main())