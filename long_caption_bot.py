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
            # download the photo
            file_info = await bot.get_file(message.photo[-1].file_id)
            response = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(BOT_API_KEY, file_info.file_path))
            # Convert the downloaded content into a byte stream
            file_byte_stream = io.BytesIO(response.content)
            file_byte_stream.name = file_info.file_path.split("/")[-1]  # Give the file a name for proper handling
            # send merged message to private channel
            merged_message = await telethon_client.send_file(int(LONG_CAPTION_CHANNEL_ID), file=file_byte_stream, caption=message.reply_to_message.text)
            # copy from private channel to public user
            await bot.copy_message(message.chat.id, LONG_CAPTION_CHANNEL_ID, merged_message.id)
            await bot.send_message(message.chat.id, success_message, parse_mode="markdown")
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