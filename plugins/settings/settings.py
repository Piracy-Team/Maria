import logging
import asyncio
from pyrogram import types, errors
from pyrogram.enums import MessageEntityType
from database.users_chats_db import db
from info import ADMINS

logger = logging.getLogger(__name__)


async def Settings(m: "types.Message"):
    user_id = m.chat.id

    if m.entities:
        if m.entities[0].type is MessageEntityType.BOT_COMMAND:
            message = await m.reply_text('**İşleniyor..**', reply_to_message_id=m.id)
            message = message.edit
    else:
        message = m.edit

    user_data = await db.get_user_data(user_id)

    if not user_data:
        await message("Verileriniz veritabanından alınamadı!")
        return

    get_notif = user_data.get("notif", False)

    buttons_markup = [
        [
            types.InlineKeyboardButton(f"{'🔔' if get_notif else '🔕'} Bildirimler",
                                       callback_data="notifon")],
        [
            types.InlineKeyboardButton(f"🔙 Geri",
                                       callback_data="start"),
            types.InlineKeyboardButton(f"Kapat",
                                       callback_data='close_data')]
    ]

    if user_id in ADMINS:
        buttons_markup.append([types.InlineKeyboardButton(f"👮‍♂ Admin",
                                                          callback_data="help")])

    try:
        await message(
            text="**⚙ Bot Ayarları**",
            reply_markup=types.InlineKeyboardMarkup(buttons_markup),
            disable_web_page_preview=True
        )
    except errors.MessageNotModified:
        pass
    except errors.FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as err:
        logger.error(err)
