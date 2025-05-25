import os

SESSION = "my_bot5"
API_ID = int(os.getenv("API_ID", "8012239"))
API_HASH = os.getenv("API_HASH", "71e6f1bf66ed8dcc5140fbe827b6b08")
BOT_TOKEN = os.getenv("BOT_TOKEN", "67277194738:AAHapce3wJ-kSG3WDYG5oxg9wYxaenYwZ-8")
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-1002379643238"))
DUMP_CHANNEL = int(os.getenv("DUMP_CHANNEL", "-1002379643238"))
PORT = int(os.getenv("PORT", "8080"))
