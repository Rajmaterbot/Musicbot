"""
from os import getenv


API_ID = int(getenv("API_ID", "24120186"))
API_HASH = getenv("API_HASH", "01fd2c9e36d0754b9fd24f15359fe22e")
BOT_TOKEN = getenv("BOT_TOKEN", "7252797686:AAF_xw2oBKsYes_xfEX_1kMQXID3AuhSb8s")
OWNER_ID = int(getenv("OWNER_ID", "559031264"))
SUDO_USERS = list(map(int, getenv("SUDO_USERS", "559031264").split()))
MONGO_URL = getenv("MONGO_DB", "mongodb+srv://Yash_607:Yash_607@cluster0.r3s9sbo.mongodb.net/?retryWrites=true&w=majority")

CHANNEL_ID = int(getenv("CHANNEL_ID", "-1002243504787"))
PREMIUM_LOGS = int(getenv("PREMIUM_LOGS", "-1001688659594"))

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
