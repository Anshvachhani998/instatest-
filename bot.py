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
from pyrogram import types
from pyrogram import utils as pyroutils
import random
import asyncio
import logging
from collections import deque

logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)


pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999999

GROUP_ID = [-1002506415678, -1002506415678]
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
import logging

queue = deque()
processing = False
message_map = {}



@userbot.on_message(filters.private & filters.text & filters.incoming)
async def userbot_receive_link(client, message):
    text = message.text.lower()

    if "https://www.instagram.com/" in text:
        queue.append((message.chat.id, message.text, message.id))
        position = len(queue)

        if not processing and position == 1:
            status_msg = "**Dᴏᴡɴʟᴏᴀᴅɪɴɢ Yᴏᴜʀ Rᴇᴇʟꜱ 🩷**"
        else:
            status_msg = (
                "**Dᴏᴡɴʟᴏᴀᴅɪɴɢ Yᴏᴜʀ Rᴇᴇʟꜱ 🩷**"
                f"\n🔢 You are #{position} in queue."
                f"\n🔄 Currently processing: {'1' if processing else '0'} request."
            )

        await message.reply(status_msg)
        await process_queue(client)

    elif text == "!ping":
        await message.reply("🏓 Userbot is running!")


async def process_queue(client):
    global processing
    if processing or not queue:
        return

    processing = True
    user_id, link, user_msg_id = queue.popleft()


    selected_group = random.choice(GROUP_ID)

    try:
        sent_msg = await client.send_message(selected_group, link)
        logging.info(f"Sent to group {selected_group}: {sent_msg.id}")
        message_map[sent_msg.id] = (user_id, user_msg_id)
    except Exception as e:
        logging.error(f"Send to group failed: {e}")
        await client.send_message(user_id, "❌ Unable to send link to group.", reply_to_message_id=user_msg_id)
        processing = False
        return

    for _ in range(30):
        await asyncio.sleep(1)
        if sent_msg.id not in message_map:
            break
    else:
        await client.send_message(
            chat_id=user_id,
            text="⚠️ Sorry, no response received from group within 30 seconds.",
            reply_to_message_id=user_msg_id
        )
        del message_map[sent_msg.id]

    processing = False
    await process_queue(client)

@userbot.on_message(filters.chat(GROUP_ID) & (filters.video | filters.document | filters.photo | filters.text) & filters.reply)
async def group_reply_handler(client, message):
    reply_to_id = message.reply_to_message.id
    user_info = message_map.get(reply_to_id)

    if user_info:
        user_id, original_msg_id = user_info
        try:
            await client.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,  # ✅ use actual group this message came from
                message_id=message.id,
                caption="Here is your file ✅",
                reply_to_message_id=original_msg_id
            )
            del message_map[reply_to_id]
        except Exception as e:
            print(f"Error copying message: {e}")

MAINTENANCE_MODE = True

@app.on_message(filters.all, group=-1)
async def maintenance_blocker(client, message):
    if MAINTENANCE_MODE and not message.text.startswith("/maintancemode"):
        await message.reply("🔧 **Bot is under maintenance. Please try again later.**")
        raise StopPropagation


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
