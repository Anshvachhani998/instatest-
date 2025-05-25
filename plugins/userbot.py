from pyrogram.handlers import MessageHandler
from bot import userbot

async def userbot_ping(client, message):
    if message.text.lower() == "!pings":
        await message.reply("🏓 Userbot is running!")

userbot.add_handler(MessageHandler(userbot_ping, filters.private & filters.text & filters.incoming))
