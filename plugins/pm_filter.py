# Kanged From @TroJanZheX
import asyncio
import re
import ast
import time
import psutil
import shutil

from info import botStartTime
from translation import Translation
from plugins.settings.settings import Settings
from functions.utils import get_size, is_subscribed, temp
from info import ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION

from pyrogram import Client, filters, types
from pyrogram.enums import ParseMode, ChatType, ChatMemberStatus
from pyrogram.errors import UserIsBlocked, MessageNotModified, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from functions.utils import ReadableTime

from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}

from pyrogram.types import Message

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
from functions.utils import get_size, save_group_settings, get_settings

from database.ia_filterdb import get_search_results
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)


@Client.on_edited_message(~filters.channel & filters.text & filters.incoming)
@Client.on_message(~filters.channel & filters.text & filters.incoming)
async def give_filter(client, message):
    k = await manual_filters(client, message)
    if not k:
        await auto_filter(client, message)


@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("Senin değil. Kendin arat :P", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        return await query.answer("O çok eskimiş. Yeniden arat aynı şeyi.", show_alert=True)

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    btn = [[
        InlineKeyboardButton(
            text=f"{get_size(file.file_size)} {file.file_name}", callback_data=f'files#{file.file_id}'
        )]
        for file in files
    ]

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("◀ Geri", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 Sayfa {round(int(offset) / 10) + 1} / {round(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {round(int(offset) / 10) + 1} / {round(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("İleri ▶", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("◀ Geri", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {round(int(offset) / 10) + 1} / {round(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("İleri ▶", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


async def auto_filter(client, msg: Message, spoll=False):
    message = msg
    if message.text.startswith("/"): return  # ignore commands
    if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
        return
    if 2 < len(message.text) < 100:
        search = message.text
        files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
        if not files:
            delo = await msg.reply_text("Bulamadım bir şey.\nArama ipuçları için tıkla ve oku: /yardim")
            await asyncio.sleep(20)
            return await delo.delete()
    else:
        return
    btn = [
        [
            InlineKeyboardButton(
                text=f"{get_size(file.file_size)} {file.file_name}", callback_data=f'files#{file.file_id}'
            )
        ]
        for file in files
    ]

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"🗓 1/{round(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="İleri ▶", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
        )
    await message.reply_text(f"{search} İçin Bulduğum Sonuçlar:", reply_markup=InlineKeyboardMarkup(btn))
    if spoll:
        await msg.delete()


async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await client.send_message(group_id, reply_text, disable_web_page_preview=True)
                        else:
                            button = eval(btn)
                            await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False


@Client.on_callback_query()
async def cb_handler(client: Client, cb: CallbackQuery):
    user_id = cb.from_user.id
    message = cb.message
    if cb.data == "close_data":
        await message.delete()
    elif cb.data == "notifon":
        notif = await db.get_notif(user_id)
        if notif:
            await cb.answer("Bot bildirimleri kapatıldı.")
            await db.set_notif(user_id, False)
        else:
            await cb.answer("Bot bildirimleri etkinleştirildi.")
            await db.set_notif(user_id, True)
        await Settings(message)
    elif cb.data == "delallconfirm":
        chat_type = message.chat.type

        if chat_type == ChatType.PRIVATE:
            grpid = await active_connection(str(user_id))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await message.edit_text("Make sure I'm present in your group!!")
                    return
            else:
                await message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups"
                )
                return

        elif chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            grp_id = message.chat.id
            title = message.chat.title

        else:
            return

        st = await client.get_chat_member(grp_id, user_id)
        if (st.status == ChatMemberStatus.OWNER) or (int(user_id) in ADMINS):
            await del_all(message, grp_id, title)
        else:
            await cb.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)

    elif cb.data == "delallcancel":
        chat_type = message.chat.type

        if chat_type == ChatType.PRIVATE:
            await message.reply_to_message.delete()
            await message.delete()

        elif chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            grp_id = message.chat.id
            st = await client.get_chat_member(grp_id, user_id)
            if (st.status == ChatMemberStatus.OWNER) or (int(user_id) in ADMINS):
                await message.delete()
                try:
                    await message.reply_to_message.delete()
                except:
                    pass
            else:
                await cb.answer("Thats not for you!!", show_alert=True)

    elif "groupcb" in cb.data:
        await cb.answer()

        group_id = cb.data.split(":")[1]

        act = cb.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
        return

    elif "connectcb" in cb.data:
        await cb.answer()

        group_id = cb.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await message.edit_text(
                f"Connected to **{title}**",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.edit_text('Some error occured!!', parse_mode=ParseMode.MARKDOWN)
        return

    elif "disconnect" in cb.data:
        await cb.answer()

        group_id = cb.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = cb.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await message.edit_text(
                f"Some error occured!!",
                parse_mode=ParseMode.MARKDOWN
            )
        return
    elif "deletecb" in cb.data:
        await cb.answer()

        user_id = cb.from_user.id
        group_id = cb.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await message.edit_text(
                f"Some error occured!!",
                parse_mode=ParseMode.MARKDOWN
            )
        return
    elif cb.data == "backcb":
        await cb.answer()

        groupids = await all_connections(str(user_id))
        if groupids is None:
            await message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(user_id), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    elif "alertmessage" in cb.data:
        grp_id = message.chat.id
        i = cb.data.split(":")[1]
        keyword = cb.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await cb.answer(alert, show_alert=True)

    if cb.data.startswith("file"):
        ident, file_id = cb.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await cb.answer("Bulamadım bir şey.\nArama ipuçları için tıkla ve oku: /yardim")
        files = files_[0]
        f_caption = files.caption
        if not f_caption: f_caption = str(files.file_name)
        f_caption += '' if CUSTOM_FILE_CAPTION is None else f'\n{CUSTOM_FILE_CAPTION}'

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, cb):
                return await cb.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
            else:
                await client.send_cached_media(
                    chat_id=cb.from_user.id,
                    file_id=file_id,
                    caption=f_caption
                )
                await cb.answer('Özelden sana gönderdim', show_alert=False)
        except UserIsBlocked:
            await cb.answer('Beni bloklamışsın aq', show_alert=True)
        except PeerIdInvalid:
            await cb.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
        except Exception as e:
            await cb.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")

    elif cb.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, cb):
            return await cb.answer("Önce kanala üye ol. Sinirlendirme beni.", show_alert=True)
        ident, file_id = cb.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await cb.answer('Bulamadım bir şey.\nArama ipuçları için tıkla ve oku: /yardim')
        files = files_[0]
        f_caption = files.caption
        if not f_caption: f_caption = str(files.file_name)
        f_caption += '' if CUSTOM_FILE_CAPTION is None else f'\n{CUSTOM_FILE_CAPTION}'
        await cb.answer()
        await client.send_cached_media(
            chat_id=cb.from_user.id,
            file_id=file_id,
            caption=f_caption)

    elif cb.data == "pages":
        await cb.answer()
    elif cb.data == "start":
        await cb.answer()
        reply_markup = Translation.START_BUTTONS
        await message.edit_text(
            text=Translation.START_TXT.format(cb.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )
    elif cb.data == "settings":
        await cb.answer()
        await Settings(message)
    elif cb.data == "help":
        await cb.answer()
        buttons = [[
            InlineKeyboardButton('Manuel Filtre', callback_data='manuelfilter'),
            InlineKeyboardButton('Otomatik Filtre', callback_data='autofilter')
        ], [
            InlineKeyboardButton('Connection', callback_data='coct'),
            InlineKeyboardButton('Ekstra Modlar', callback_data='extra')
        ], [
            InlineKeyboardButton('🏠 Geri', callback_data='settings'),
            InlineKeyboardButton('🔮 İstatistik', callback_data='stats')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.edit_text(
            text=Translation.HELP_TXT.format(cb.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    elif cb.data == "about":
        await cb.answer()
        buttons = [
            [
                InlineKeyboardButton('◀ Geri', callback_data='start'),
                InlineKeyboardButton('Kapat', callback_data='close_data')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.edit_text(
            text=Translation.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup
        )
    elif cb.data == "source":
        await cb.answer()
        buttons = [[
            InlineKeyboardButton('◀️ Geri', callback_data='start'),
            InlineKeyboardButton('🔐 Kapat', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.edit_text(
            text=Translation.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    elif cb.data == "manuelfilter":
        await cb.answer()
        buttons = [[
            InlineKeyboardButton('◀️ Geri', callback_data='help'),
            InlineKeyboardButton('⏹️ Buttons', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.edit_text(
            text=Translation.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    elif cb.data == "button":
        await cb.answer()
        buttons = [[
            InlineKeyboardButton('◀️ Geri', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.edit_text(
            text=Translation.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    elif cb.data == "autofilter":
        await cb.answer()
        buttons = [[
            InlineKeyboardButton('◀️ Geri', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.edit_text(
            text=Translation.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    elif cb.data == "coct":
        await cb.answer()
        buttons = [[
            InlineKeyboardButton('◀️ Geri', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.edit_text(
            text=Translation.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    elif cb.data == "extra":
        await cb.answer()
        buttons = [[
            InlineKeyboardButton('◀️ Geri', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.edit_text(
            text=Translation.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    elif cb.data == "stats":
        await cb.answer()
        buttons = [[
            InlineKeyboardButton('◀️ Geri', callback_data='start'),
            InlineKeyboardButton('♻️', callback_data='stats')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        currentTime = ReadableTime(time.time() - botStartTime)
        totald, used, freeg = shutil.disk_usage('.')
        totald = get_size(totald)
        used = get_size(used)
        freeg = get_size(freeg)
        sent = get_size(psutil.net_io_counters().bytes_sent)
        recv = get_size(psutil.net_io_counters().bytes_recv)
        cpuUsage = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        stats = f'\n<b>Uptime:</b> <code>{currentTime}</code>\n' \
                f'<b>Total Disk:</b> <code>{totald}</code>\n' \
                f'<b>Used:</b> <code>{used}</code> ' \
                f'<b>Free:</b> <code>{freeg}</code>\n' \
                f'<b>Upload:</b> <code>{sent}</code> ' \
                f'<b>Download:</b> <code>{recv}</code>\n' \
                f'<b>CPU:</b> <code>{cpuUsage}%</code> ' \
                f'<b>RAM:</b> <code>{memory}%</code> ' \
                f'<b>DISK:</b> <code>{disk}%</code>'
        await message.edit_text(
            text=Translation.STATUS_TXT.format(total, users, chats, monsize, free) + stats,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    elif cb.data.startswith("setgs"):
        ident, set_type, status, grp_id = cb.data.split("#")
        grpid = await active_connection(str(cb.from_user.id))

        if str(grp_id) != str(grpid):
            await cb.message.edit("Aktif Bağlantınız Değiştirildi. Ayarlara git.")
            return await cb.answer('Korsan Suçtur xD')

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filtre Düğmesi',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Tek' if settings["button"] else 'Çift',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Bot PM', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Evet' if settings["botpm"] else '❌ Hayır',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Dosya Güvenliği',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Evet' if settings["file_secure"] else '❌ Hayır',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Yazım Denetimi',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Evet' if settings["spell_check"] else '❌ Hayır',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Hoşgeldin Mesajı', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Evet' if settings["welcome"] else '❌ Hayır',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await cb.message.edit_reply_markup(reply_markup)
