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

userbot = Userbot()

# Yeh decorator userbot.start ke baad hi hona chahiye
@userbot.on_message(filters.private & filters.text & filters.incoming)
async def userbot_ping(client, message):
    if message.text.lower() == "!ping":
        await message.reply("🏓 Userbot is running!")


# ----- Main Runner -----
app = Bot()

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
