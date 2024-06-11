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
API_ID = int(os.environ.get("24250238"))
# ------------------------------------------------
API_HASH = os.environ.get("cb3f118ce5553dc140127647edcf3720")
# ----------------D--------------------------------
BOT_TOKEN = os.environ.get("6103524529:AAGMbltmFHLulnBqSyi50CCZCLYeVrEFG8g")
# -----------------A-------------------------------
BOT_USERNAME = os.environ.get("test4k6_bot")
# ------------------X------------------------------
OWNER_ID = int(os.environ.get("6175650047"))
# ------------------X------------------------------

SUDO_USERS = list(map(int, getenv("6175650047", "").split()))
# ------------------------------------------------
CHANNEL_ID = int(os.environ.get("-1002065733031"))
# ------------------------------------------------
MONGO_URL = os.environ.get("mongodb+srv://daxxop:daxxop@daxxop.dg3umlc.mongodb.net/?retryWrites=true&w=majority")
# -----------------------------------------------
PREMIUM_LOGS = int(os.environ.get("-1002065733031"))

