import logging
import asyncio
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from aiohttp import web
import pytz
from datetime import date, datetime
from plugins import web_server
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, PORT, USER_SESSION
from pyrogram import utils as pyroutils

pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999999

logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)


class Bot(Client):
    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=10,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        logging.info(f"🤖 {me.first_name} (@{me.username}) running on Pyrogram v{__version__} (Layer {layer})")
        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        time = now.strftime("%H:%M:%S %p")
        await self.send_message(chat_id=LOG_CHANNEL, text=f"✅ Bot Restarted! 📅 Date: {today} 🕒 Time: {time}")

        # Start webserver inside this task so it runs concurrently
        app_runner = web.AppRunner(await web_server())
        await app_runner.setup()
        site = web.TCPSite(app_runner, "0.0.0.0", PORT)
        await site.start()
        logging.info(f"🌐 Web Server Running on PORT {PORT}")

    async def stop(self, *args):
        await super().stop()
        logging.info("🛑 Bot Stopped.")


app = Bot()
userbot = Client(name="userbot", api_id=API_ID, api_hash=API_HASH, session_string=USER_SESSION)

async def main():
    # Start bot and userbot concurrently
    await asyncio.gather(
        app.start(),
        userbot.start()
    )
    logging.info("Both bot and userbot started.")

    # Run until canceled
    await asyncio.Event().wait()

async def shutdown():
    await asyncio.gather(
        app.stop(),
        userbot.stop()
    )
    logging.info("Both bot and userbot stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Stopping bot and userbot...")
        asyncio.run(shutdown())
