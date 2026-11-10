import os
# telebot
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from telebot.types import InlineQueryResultArticle, InputTextMessageContent
import logging
import traceback
import asyncio
import io
import requests
import json
import httpx

## bot
BOT_API_KEY = os.environ.get('LONG_CAPTION_BOT_API_KEY')
LONG_CAPTION_CHANNEL_ID = os.environ.get('LONG_CAPTION_CHANNEL_ID')

## private-router (owns the Telethon user session)
PRIVATE_ROUTER_URL = os.environ.get('PRIVATE_ROUTER_URL', 'http://127.0.0.1:3010').rstrip('/')
PRIVATE_ROUTER_TOKEN = os.environ.get('PRIVATE_ROUTER_TOKEN', '')

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


async def private_router_apply_caption(chat_id, media_message_id, caption_message_id):
    """Ask private-router to copy formatted caption onto the media message."""
    if not PRIVATE_ROUTER_TOKEN:
        raise RuntimeError('PRIVATE_ROUTER_TOKEN is not set')
    headers = {'Authorization': f'Bearer {PRIVATE_ROUTER_TOKEN}'}
    payload = {
        'chat_id': int(chat_id),
        'media_message_id': int(media_message_id),
        'caption_message_id': int(caption_message_id),
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f'{PRIVATE_ROUTER_URL}/v1/messages/apply-caption',
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        return response.json()
