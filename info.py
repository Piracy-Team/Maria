import string
import random
import re
import os
from os import environ
from dotenv import load_dotenv
import time

if os.path.exists('config.env'):
    load_dotenv('config.env')

id_pattern = re.compile(r'^.\d+$')


def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y", "e"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n", "h"]:
        return False
    else:
        return default


# Bot information
SESSION = environ.get('SESSION', 'kitapmaria ' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)))
PICS = (environ.get('PICS', 'https://telegra.ph/file/7e56d907542396289fee4.jpg https://telegra.ph/file/9aa8dd372f4739fe02d85.jpg https://telegra.ph/file/adffc5ce502f5578e2806.jpg')).split()
API_ID = int(environ['API_ID'])
API_HASH = environ['API_HASH']
BOT_TOKEN = environ['BOT_TOKEN']
botStartTime = time.time()
# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', True))
BROADCAST_AS_COPY = bool(environ.get("BROADCAST_AS_COPY", True))
SINGLE_BUTTON = bool(environ.get('SINGLE_BUTTON', False))
PROTECT_CONTENT = bool(environ.get('PROTECT_CONTENT', True))

# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '0').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('AUTH_CHANNEL')
auth_grp = environ.get('AUTH_GROUP')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "")
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'dosyalar')

# Others
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', 0))
BUTTON_COUNT = int(environ.get('BUTTON_COUNT', 10))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'GercekArsivler')
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", "")
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
SHARE_BUTTON_TEXT = environ.get('SHARE_BUTTON_TEXT', 'Checkout {username} for searching files')
SEND_LOGS_WHEN_DYING = str(environ.get("SEND_LOGS_WHEN_DYING", "True")).lower() == 'true'

FORCE_TXT = environ.get('FORCE_TXT', """
**Botu sadece kanal aboneleri kullanabilir.**
""")


