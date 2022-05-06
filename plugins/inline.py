import logging
import os
from urllib.parse import quote
from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from database.ia_filterdb import get_search_results
from functions.utils import is_subscribed, get_size
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION, BUTTON_COUNT, SHARE_BUTTON_TEXT
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument, InlineQuery
from natsort import natsorted
logger = logging.getLogger(__name__)
cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME


@Client.on_inline_query(filters.user(AUTH_USERS) if AUTH_USERS else None)
async def answer(bot, query):
    """Show search results for given inline query"""

    if AUTH_CHANNEL and not await is_subscribed(bot, query):
        await query.answer(results=[],
                           cache_time=0,
                           switch_pm_text='Botu kullanmak için kanalıma abone olmalısınız.',
                           switch_pm_parameter="subscribe")
        return

    results = []
    if '|' in query.query:
        text, file_type = query.query.split('|', maxsplit=1)
        text = text.strip()
        file_type = file_type.strip().lower()
    else:
        text = query.query.strip()
        file_type = None

    offset = int(query.offset or 0)
    reply_markup = get_reply_markup(bot.username, query=text)
    files, next_offset, total = await get_search_results(text,
                                                         file_type=file_type,
                                                         max_results=BUTTON_COUNT,
                                                         offset=offset)
    for file in files:
        title = file.file_name
        size = get_size(file.file_size)
        f_caption = file.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{file.file_name}"
        results.append(
            InlineQueryResultCachedDocument(
                title=file.file_name,
                document_file_id=file.file_id,
                caption=f_caption,
                description=f'Boyut: {get_size(file.file_size)}\nTür: {file.file_type}',
                reply_markup=reply_markup))

    if results:
        switch_pm_text = f"{emoji.FILE_FOLDER} Sonuçlar - {total}"
        if text:
            switch_pm_text += f' "{text}"'
        try:
            await query.answer(results=results,
                               is_personal=True,
                               cache_time=cache_time,
                               switch_pm_text=switch_pm_text,
                               switch_pm_parameter="start",
                               next_offset=str(next_offset))
        except QueryIdInvalid:
            pass
        except Exception as e:
            logging.exception(str(e))
            await query.answer(results=[], is_personal=True,
                               cache_time=cache_time,
                               switch_pm_text=str(e)[:63],
                               switch_pm_parameter="error")
    else:
        switch_pm_text = f'{emoji.CROSS_MARK} Sonuç yok'
        if text:
            switch_pm_text += f' "{text}"'

        await query.answer(results=[],
                           is_personal=True,
                           cache_time=cache_time,
                           switch_pm_text=switch_pm_text,
                           switch_pm_parameter="okay")


def get_reply_markup(username, query):
    url = 't.me/share/url?url=' + quote(SHARE_BUTTON_TEXT.format(username=username))
    buttons = [
        [
            InlineKeyboardButton('Tekrar Ara', switch_inline_query_current_chat=query),
            InlineKeyboardButton('Botu Paylaş', url=url),
        ]
    ]
    return InlineKeyboardMarkup(buttons)
