from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from functions.utils import temp

class Translation(object):
    START_BUTTONS = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('🔍 Ara', switch_inline_query_current_chat='')
        ],
        [
            InlineKeyboardButton('⚙ Ayarlar', callback_data='settings'),
            InlineKeyboardButton('📜 Hakkımda', callback_data='about')
        ]
    ])
    BUTTON_TEXT = """🤖 Katıl"""
    START_TXT = """Esenlikler {}"""
    HELP_TXT = "Esenlikler {} aşağıdaki butonlar sana yardımcı olur."
    SOURCE_TXT = "Takıl işte üzümü ye bağını sorma."
    ABOUT_TXT = "Anonim kişiler tarafından geliştirildi."

    STATUS_TXT = """Dosya: <code>{}</code>
Kullanıcı: <code>{}</code>
Sohbet: <code>{}</code>
Dolu: <code>{}</code>
Boş: <code>{}</code>"""
    LOG_TEXT_G = """#YeniGrup
Grup = {}(<code>{}</code>)
Toplam Üye = <code>{}</code>
Added By - {}
Bot - @{}
"""
    LOG_TEXT_P = """#YeniKullanıcı
ID - <code>{}</code>
Ad - {}
Bot - @{}
"""

    MANUELFILTER_TXT = """Help: <b>Filters</b>
- Filter is the feature were users can set automated replies for a particular keyword and EvaMaria will respond whenever a keyword is found the message
<b>NOTE:</b>
1. eva maria should have admin privillage.
2. only admins can add filters in a chat.
3. alert buttons have a limit of 64 characters.
<b>Commands and Usage:</b>
• /filter - <code>add a filter in chat</code>
• /filters - <code>list all the filters of a chat</code>
• /del - <code>delete a specific filter in chat</code>
• /delall - <code>delete the whole filters in a chat (chat owner only)</code>"""
    BUTTON_TXT = """Help: <b>Buttons</b>
- Eva Maria Supports both url and alert inline buttons.
<b>NOTE:</b>
1. Telegram will not allows you to send buttons without any content, so content is mandatory.
2. Eva Maria supports buttons with any telegram media type.
3. Buttons should be properly parsed as markdown format
<b>URL buttons:</b>
<code>[Button Text](buttonurl:https://t.me/EvaMariaBot)</code>
<b>Alert buttons:</b>
<code>[Button Text](buttonalert:This is an alert message)</code>"""
    AUTOFILTER_TXT = """Yardım: <b>Otomatik Filtre</b>
<b>NOT:</b>
1. Eğer özelse beni kanalının admini yap.
2. kanalınızın kamera görüntüleri, porno ve sahte dosyalar içermediğinden emin olun.
3. Son mesajı tırnak işaretleri ile bana ilet.
O kanaldaki tüm dosyaları veritabanıma ekleyeceğim."""
    CONNECTION_TXT = """Yardım: <b>Connections</b>
- Used to connect bot to PM for managing filters 
- it helps to avoid spamming in groups.
<b>NOT:</b>
1. Yalnızca yöneticiler bağlantı ekleyebilir.
2. Send <code>/connect</code> for connecting me to ur PM
<b>Commands and Usage:</b>
• /connect  - <code>connect a particular chat to your PM</code>
• /disconnect  - <code>disconnect from a chat</code>
• /connections - <code>list all your connections</code>"""
    ADMIN_TXT = """Yardım: <b>Yönetici Modları</b>
<b>NOT:</b>
Bu modül yalnızca yöneticilerim için çalışıyor
<b>Komutlar ve Kullanım:</b>
• /logs - <code>son hataları almak için</code>
• /stats - <code>db'deki dosyaların durumunu almak için.</code>
• /delete - <code>db'den belirli bir dosyayı silmek için.</code>
• /users - <code>kullanıcıların ve kimliklerinin listesini almak için.</code>
• /setskip - <code>dizini atla.</code>
• /chats - <code>sohbetlerin ve kimliklerin listesini al </code>
• /leave  - <code>sohbetten ayrıl.</code>
• /disable  -  <code>sohbeti devre dışı bırak.</code>
• /ban  - <code>kullanıcı yasakla.</code>
• /unban  - <code>kullanıcı yasağını kaldır.</code>
• /channel - <code>toplam bağlı kanalların listesini almak için</code>
• /broadcast - <code>tüm kullanıcılara mesaj yayınlar</code>
• /deleteall - <code>tüm kayıtlı dosyaları veritabanından siler</code>"""



