from database.users_chats_db import db
from pyrogram import Client
from pyrogram.types import Message
from info import LOG_CHANNEL
from translation import Translation

import logging

logger = logging.getLogger(__name__)


async def add_user_to_database(c: Client, cmd: Message):
    bot = await c.get_me()
    BOT_USERNAME = bot.username
    user_id = cmd.from_user.id
    if not await db.is_user_exist(user_id):
        if LOG_CHANNEL:
            await c.send_message(LOG_CHANNEL,
                                 Translation.LOG_TEXT_P.format(user_id,
                                                               cmd.from_user.mention,
                                                               BOT_USERNAME
                                                               ))
        else:
            logging.info(f"#YeniKullanıcı :- Ad : {cmd.from_user.first_name} ID : {user_id}")
        await db.add_user(user_id, cmd.from_user.first_name)


async def add_chat_to_database(c: Client, cmd: Message):
    bot = await c.get_me()
    BOT_USERNAME = bot.username
    chat_id = cmd.chat.id
    chat_title = cmd.chat.title
    if not await db.get_chat(cmd.chat.id):
        total = await c.get_chat_members_count(cmd.chat.id)
        r_j = cmd.from_user.mention if cmd.from_user else "Anonymous"
        if LOG_CHANNEL:
            await c.send_message(LOG_CHANNEL,
                                 Translation.LOG_TEXT_G.format(chat_title,
                                                               chat_id,
                                                               total, r_j,
                                                               BOT_USERNAME))
        await db.add_chat(chat_id, chat_title)
    return
