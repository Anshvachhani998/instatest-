import logging
import asyncio
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from aiohttp import web
import pytz
from datetime import date, datetime
from plugins import web_server
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, PORT, USER_SESSION

logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

# Userbot (Client without bot_token)
userbot = Client(
    name="userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=USER_SESSION
)

# Bot with plugins
class Bot(Client):
    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins={"root": "plugins"},  # Plugin folder
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

        await self.send_message(
            chat_id=LOG_CHANNEL,
            text=f"✅ Bot Restarted!\n📅 Date: {today}\n🕒 Time: {time}"
        )

        # Start web server
        runner = web.AppRunner(await web_server())
        await runner.setup()
        await web.TCPSite(runner, "0.0.0.0", PORT).start()
        logging.info(f"🌐 Web Server Running on PORT {PORT}")

    async def stop(self, *args):
        await super().stop()
        logging.info("🛑 Bot Stopped.")

app = Bot()

# Main function to start both clients
async def main():
    await app.run()
    logging.info("✅ Bot client started.")

    await userbot.start()
    logging.info("✅ Userbot client started.")

    # Keep alive
    await asyncio.Event().wait()
