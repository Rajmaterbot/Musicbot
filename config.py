"""
from os import getenv


API_ID = int(getenv("API_ID", "24250238"))
API_HASH = getenv("API_HASH", "cb3f118ce5553dc140127647edcf3720")
BOT_TOKEN = getenv("BOT_TOKEN", "6103524529:AAGMbltmFHLulnBqSyi50CCZCLYeVrEFG8g")
OWNER_ID = int(getenv("OWNER_ID", "6175650047"))
SUDO_USERS = list(map(int, getenv("SUDO_USERS", "6175650047").split()))
MONGO_URL = getenv("MONGO_DB", "mongodb+srv://daxxop:daxxop@daxxop.dg3umlc.mongodb.net/?retryWrites=true&w=majority")

CHANNEL_ID = int(getenv("CHANNEL_ID", "-1002065733031"))
PREMIUM_LOGS = int(getenv("PREMIUM_LOGS", "-1002065733031"))

"""
#




# --------------M----------------------------------

import os
from os import getenv
# ---------------R---------------------------------
API_ID = int(os.environ.get("API_ID"))
# ------------------------------------------------
API_HASH = os.environ.get("API_HASH")
# ----------------D--------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
# -----------------A-------------------------------
BOT_USERNAME = os.environ.get("BOT_USERNAME")
# ------------------X------------------------------
OWNER_ID = int(os.environ.get("OWNER_ID"))
# ------------------X------------------------------

SUDO_USERS = list(map(int, getenv("SUDO_USERS", "").split()))
# ------------------------------------------------
CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
# ------------------------------------------------
MONGO_URL = os.environ.get("MONGO_URL")
# -----------------------------------------------
PREMIUM_LOGS = int(os.environ.get("PREMIUM_LOGS"))
