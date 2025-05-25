from pyrogram import filters
from bot import userbot

@userbot.on_message(filters.private & filters.incoming)
async def userbot_test(client, message):
    await message.reply("✅ Userbot is running!")
