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
import traceback
import asyncio
import io
import requests
import json
from urllib.parse import urlparse

## app api
TELEGRAM_APP_API_ID = os.environ.get('ARASHNM80_TELEGRAM_APP_API_ID')
TELEGRAM_APP_API_HASH= os.environ.get('ARASHNM80_TELEGRAM_APP_API_HASH')
TELEGRAM_PHONE_NUMBER= os.environ.get('ARASHNM80_TELEGRAM_PHONE_NUMBER')
session_name = "arashnm80"
## bot
BOT_API_KEY = os.environ.get('LONG_CAPTION_BOT_API_KEY')
LONG_CAPTION_CHANNEL_ID = os.environ.get('LONG_CAPTION_CHANNEL_ID')

# warp socks proxy
warp_proxies = os.environ["WARP_PROXIES"]
warp_proxies = json.loads(warp_proxies)
# parse it and convert to a tuple to be used by telethon or other libraries
warp_proxy = urlparse(warp_proxies['http'])
warp_proxy = (
    warp_proxy.scheme.replace('h', ''),  # 'socks5h' → 'socks5'
    warp_proxy.hostname,
    warp_proxy.port,
    bool(warp_proxy.username and warp_proxy.password),
    warp_proxy.username,
    warp_proxy.password
)

# messages
# success_message = \
# f"""
# Give me energy with coffee and motivate me to add more features to the bot ☕️🤖:

# - [BuyMeACoffee](https://www.buymeacoffee.com/Arashnm80) (🇺🇸 $)
# - [Coffeete](https://www.coffeete.ir/Arashnm80) (🇮🇷 ريال)
# """
success_message = \
f"""
Me:\n[Youtube](https://www.youtube.com/@Arashnm80) • [𝕏](https://x.com/Arashnm80) • [Github](https://github.com/arashnm80)
"""

short_caption_message = \
f"""
You used the bot correctly and i can the caption for you✅.

But this caption isn't really long and you can set it without a bot or telegram premium too😄.
"""

starpal_promotion_msg = \
'''⭐️خرید ستاره تلگرام بدون احراز هویت و در کمتر از ۲ دقیقه!  👈  starpal.ir'''