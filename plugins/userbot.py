from pyrogram.handlers import MessageHandler

async def userbot_ping(client, message):
    if message.text.lower() == "!ping":
        await message.reply("🏓 Userbot is running!")

userbot.add_handler(MessageHandler(userbot_ping, filters.private & filters.text & filters.incoming))
