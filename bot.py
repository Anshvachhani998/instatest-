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
app = bot()
userbot = Userbot()

# Yeh decorator userbot.start ke baad hi hona chahiye
@userbot.on_message(filters.private & filters.text & filters.incoming)
async def userbot_ping(client, message):
    if message.text.lower() == "!ping":
        await message.reply("🏓 Userbot is running!")

from collections import deque
import asyncio

GROUP_ID = -1002506415678
queue = deque()
processing = False
message_map = {}

@userbot.on_message(filters.chat(USERBOT_CHAT_ID) & filters.text)
async def userbot_receive_link(client, message):
    # Userbot ko Bot se link mila
    queue.append((message.chat.id, message.text, message.id))
    await message.reply("Link added to queue, please wait...")
    await process_queue(client)

async def process_queue(client):
    global processing
    if processing or not queue:
        return

    processing = True
    user_id, link, user_msg_id = queue.popleft()

    sent_msg = await client.send_message(GROUP_ID, link)
    message_map[sent_msg.message_id] = (user_id, user_msg_id)

    for _ in range(30):
        await asyncio.sleep(1)
        if sent_msg.message_id not in message_map:
            break

    processing = False
    await process_queue(client)


USERBOT_CHAT_ID = 5785483456

@app.on_message(filters.private & filters.text & filters.regex(r"https://www\.instagram\.com/"))
async def bot_receive_link(client, message):
    # Bot ko private message Instagram link mila
    # Ab ye link userbot ko bhejna hai
    await message.reply("✅ Link received. Processing...")

    await userbot.send_message(USERBOT_CHAT_ID, message.text)


@userbot.on_message(filters.chat(GROUP_ID) & (filters.video | filters.document | filters.photo) & filters.reply)
async def group_reply_handler(client, message):
    reply_id = message.reply_to_message.message_id
    user_info = message_map.get(reply_id)

    if user_info:
        user_id, original_msg_id = user_info

        # Userbot se Bot ko forward karo (use userbot chat with Bot)
        await client.send_message(USERBOT_CHAT_ID, f"Reply for {user_id}", reply_to_message_id=message.message_id)

        del message_map[reply_id]

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
