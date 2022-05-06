import os
import logging
import random
from pyrogram.types.messages_and_media.message import Message
from translation import Translation
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode, MessageMediaType, ChatType, ChatMemberStatus
from functions.forcesub import handle_force_subscribe
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from info import CHANNELS, ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION, PICS
from database.add import add_user_to_database
from plugins.settings.settings import Settings
from functions.utils import get_size, get_settings
from database.connections_mdb import active_connection

logger = logging.getLogger(__name__)


@Client.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    chat_id = message.from_user.id
    if AUTH_CHANNEL:
        fsub = await handle_force_subscribe(client, message)
        if fsub == 400:
            return
    buttons = Translation.START_BUTTONS

    if len(message.command) != 2:
        reply_markup = buttons
        await client.send_photo(
            chat_id=chat_id,
            photo=random.choice(PICS),
            caption=Translation.START_TXT.format(message.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
            protect_content=True
        )
        return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help", "start"]:
        reply_markup = buttons
        await client.send_photo(
            chat_id=chat_id,
            photo=random.choice(PICS),
            caption=Translation.START_TXT.format(message.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
            protect_content=True
        )
        return

    file_id = message.command[1]
    files_ = await get_file_details(file_id)
    if not files_:
        return await message.reply('Böyle bir dosya yok.')
    files = files_[0]
    title = files.file_name
    size = get_size(files.file_size)
    f_caption = files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption = f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    await client.send_cached_media(
        chat_id=chat_id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True,
    )


@Client.on_message(filters.command('kanal') & filters.user(ADMINS))
async def channel_info(bot, message):
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **İndekslenen kanallar/gruplar**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Toplam:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'İndekslenen kanallar.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('log.txt')
    except Exception as e:
        await message.reply(str(e))


@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if not (reply and reply.media):
        await message.reply('Silmek istediğiniz dosyayı /sil ile yanıtlayın', quote=True)
        return
    msg = await message.reply("İşleniyor...⏳", quote=True)
    for file_type in (MessageMediaType.DOCUMENT, MessageMediaType.VIDEO, MessageMediaType.AUDIO):
        media = getattr(reply, file_type.value, None)
        if media is not None:
            break
    else:
        await msg.edit('Bu desteklenen bir dosya biçimi değil.')
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('Dosya veritabanından başarıyla silindi.')
    else:
        # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39
        # have original file name.
        result = await Media.collection.delete_one({
            'file_name': media.file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
        })
        if result.deleted_count:
            await msg.edit('Dosya veritabanından başarıyla silindi.')
        else:
            await msg.edit('Veritabanında dosya bulunamadı.')


@Client.on_message(filters.private & filters.command(["ayarlar", "settings"]))
async def settings_handler(c: Client, m: "types.Message"):
    if not m.from_user:
        return await m.reply_text("Seni tanımıyorum ahbap.")
    await add_user_to_database(c, m)
    if AUTH_CHANNEL:
        fsub = await handle_force_subscribe(c, m)
        if fsub == 400:
            return
    await Settings(m)


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer('Korsan Suçtur xD')
    await message.message.edit('Tüm Dosyalar Başarıyla Silindi.')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'İndekslenen tüm dosyalar silinecektir.\n'
        'devam etmek istiyor musunuz?',
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Evet", callback_data="autofilter_delete")],
             [InlineKeyboardButton(text="Hayır", callback_data="close_data")],
             ]
        ),
        quote=True,
    )
