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
    # Define a basic command handler
    @bot.message_handler(commands=['start'])
    async def start_command_(message):
        await bot.send_message(message.chat.id, "Hi. send a media like photo, video, voice, ... then send some large text replied to it. I will merge them and bring back to you.\n\nmy video tutorial is available too: https://youtu.be/L\\_hdOd8KGvQ", parse_mode="markdown")
        
    # Function to handle replies to media messages
    @bot.message_handler(content_types=['text'])
    async def handle_media_reply(message):
        # Check if the message is a reply
        if message.reply_to_message:
            try:
                # if caption was short and bot wansn't necessary
                if len(message.text) < 1024:
                    await bot.send_message(message.chat.id, short_caption_message, parse_mode="markdown")
                    await bot.send_message(LONG_CAPTION_CHANNEL_ID, f"short caption received")
                    return
                # forward photo to log channel
                photo_log_message_telebot = await bot.copy_message(LONG_CAPTION_CHANNEL_ID, message.chat.id, message.reply_to_message.message_id)
                # forward caption to log channel
                caption_log_message_telebot = await bot.copy_message(LONG_CAPTION_CHANNEL_ID, message.chat.id, message.message_id)
                # private-router applies formatted caption onto the media message
                await private_router_apply_caption(
                    LONG_CAPTION_CHANNEL_ID,
                    photo_log_message_telebot.message_id,
                    caption_log_message_telebot.message_id,
                )
                # remove text from log channel
                await bot.delete_message(LONG_CAPTION_CHANNEL_ID, caption_log_message_telebot.message_id)
                # copy the edited photo to user and send success message
                await bot.copy_message(message.chat.id, LONG_CAPTION_CHANNEL_ID, photo_log_message_telebot.message_id)
                
                # starpal promotion
                if message.from_user.language_code == "fa":
                    # await bot.send_message(message.chat.id, starpal_promotion_msg, parse_mode="markdown")
                    # await bot.send_message(LONG_CAPTION_CHANNEL_ID, f"⭐️ starpal promotion for iranian user")
                    pass
                else:
                    await bot.send_message(message.chat.id, success_message, parse_mode="markdown")
            except Exception as e:
                # Log the error with additional context
                logging.error(f"An error occurred: {e}\nTraceback:\n{traceback.format_exc()}")
        else:
            # If the media message isn't a reply, you can handle it differently
            await bot.send_message(message.chat.id, "your text message should be replied to a media message.")
    
    await bot.infinity_polling()

# Entry point
if __name__ == "__main__":
    asyncio.run(main())
