# bot.py
import importlib
import os
import logging
import asyncio
from pyrogram import Client, __version__, filters
from pyrogram.raw.all import layer
from aiohttp import web
import pytz
from datetime import date, datetime
from plugins import web_server
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, PORT, USER_SESSION
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, PORT, USER_SESSION
from pyrogram import types
from pyrogram import utils as pyroutils

logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)


pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999999

logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

USERBOT_CHAT_ID = 5785483456

# ----- Bot with Plugins -----
class Bot(Client):
    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins={"root": "plugins"},
            workers=200,
            sleep_threshold=10,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        logging.info(f"🤖 {me.first_name} (@{me.username}) running on Pyrogram v{__version__} (Layer {layer})")

        # Send log
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz)
        today = now.date()
        time = now.strftime("%H:%M:%S %p")
        await self.send_message(chat_id=LOG_CHANNEL, text=f"✅ Bot Restarted!\n📅 Date: {today}\n🕒 Time: {time}")

        # Start web server
        runner = web.AppRunner(await web_server())
        await runner.setup()
        await web.TCPSite(runner, "0.0.0.0", PORT).start()
        logging.info(f"🌐 Web Server Running on PORT {PORT}")

    async def stop(self, *args):
        await super().stop()
        logging.info("🛑 Bot Stopped.")


class Userbot(Client):
    def __init__(self):
        super().__init__(
            name="userbot",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=USER_SESSION,
            plugins={"root": "plugins"},
            workers=50,
        )
app = Bot()
userbot = Userbot()

from collections import deque
import asyncio
from pyrogram import filters

GROUP_ID = -1002506415678
queue = deque()
processing = False
message_map = {}

@userbot.on_message(filters.private & filters.text & filters.incoming)
async def userbot_receive_link(client, message):
    text = message.text.lower()
    if "https://www.instagram.com/" in text:
        queue.append((message.chat.id, message.text, message.id))
        await message.reply("✅ Instagram link received! Processing your request...")
        await process_queue(client)
    elif text == "!ping":
        await message.reply("🏓 Userbot is running!")

async def process_queue(client):
    global processing
    if processing or not queue:
        return

    processing = True
    user_id, link, user_msg_id = queue.popleft()

    try:
        sent_msg = await client.send_message(GROUP_ID, link)
        logging.info(f"Sent message to group {GROUP_ID}: {sent_msg.id}")  # changed here
        message_map[sent_msg.id] = (user_id, user_msg_id)  # and here
    except Exception as e:
        logging.info(f"Failed to send message to group: {e}")
        await client.send_message(user_id, "❌ Unable to send link to group.")
        processing = False
        return

    # Wait for replies or timeout
    for _ in range(30):
        await asyncio.sleep(1)
        if sent_msg.id not in message_map:  # changed here
            break

    processing = False
    await process_queue(client)

@userbot.on_message(filters.chat(GROUP_ID) & (filters.video | filters.document | filters.photo | filters.text) & filters.reply)
async def group_reply_handler(client, message):
    reply_to_id = message.reply_to_message.id  # change here
    user_info = message_map.get(reply_to_id)

    if user_info:
        user_id, original_msg_id = user_info

        await client.copy_message(
            chat_id=user_id,
            from_chat_id=GROUP_ID,
            message_id=message.id,
            caption="Your new caption here",
            reply_to_message_id=original_msg_id 

        )

        del message_map[reply_to_id]



USERBOT_CHAT_ID = 5785483456

@app.on_message(filters.private & filters.text & filters.regex(r"https://www\.instagram\.com/"))
async def bot_receive_link(client, message):
    await message.reply("✅ Link received. Processing...")
    await app.send_message(USERBOT_CHAT_ID, message.text)


# ----- Main Runner -----


async def main():
    await app.start()
    logging.info("✅ Bot client started.")

    await userbot.start()
    me = await userbot.get_me()
    logging.info(me.first_name)
    plugins_path = "./plugins"
    for filename in os.listdir(plugins_path):
        if filename.endswith(".py"):
            importlib.import_module(f"plugins.{filename[:-3]}")

    await asyncio.Event().wait()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
