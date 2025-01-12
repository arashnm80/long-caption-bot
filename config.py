import os
# telebot
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from telebot.types import InlineQueryResultArticle, InputTextMessageContent
# telethon
import telethon
from telethon.sync import TelegramClient # for geetting messages in telethon
from telethon import TelegramClient
import logging
import asyncio
import io
import requests

## app api
TELEGRAM_APP_API_ID = os.environ.get('ARASHNM80_TELEGRAM_APP_API_ID')
TELEGRAM_APP_API_HASH= os.environ.get('ARASHNM80_TELEGRAM_APP_API_HASH')
TELEGRAM_PHONE_NUMBER= os.environ.get('ARASHNM80_TELEGRAM_PHONE_NUMBER')
session_name = "arashnm80"
## bot
BOT_API_KEY = os.environ.get('LONG_CAPTION_BOT_API_KEY')
LONG_CAPTION_CHANNEL_ID = os.environ.get('LONG_CAPTION_CHANNEL_ID')

# proxy
warp_proxy = ('socks5', '127.0.0.1', 40000)

# messages
success_message = \
f"""
Give me energy with coffee and motivate me to add more features to the bot ☕️🤖:

- [BuyMeACoffee](https://www.buymeacoffee.com/Arashnm80) (🇺🇸 $)
- [Coffeete](https://www.coffeete.ir/Arashnm80) (🇮🇷 ريال)
"""