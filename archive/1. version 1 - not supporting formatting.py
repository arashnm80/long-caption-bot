# @bot.message_handler(content_types=['photo'])
# async def handle_media_reply(message):

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