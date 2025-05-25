from pyrogram import Client, filters
import asyncio
from collections import deque
from bot import userbot

GROUP_ID = -1002506415678
 
app = Client
queue = deque()
processing = False
message_map = {}


USERBOT_CHAT_ID = 5785483456

@app.on_message(filters.private & filters.text & filters.regex(r"https://www\.instagram\.com/"))
async def bot_receive_link(client, message):
    # Bot ko private message Instagram link mila
    # Ab ye link userbot ko bhejna hai
    await message.reply("✅ Link received. Processing...")

    await userbot.send_message(USERBOT_CHAT_ID, message.text)
