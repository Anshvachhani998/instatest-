from pyrogram import filters

from bot import userbot

@userbot.on_message(filters.private & filters.text & filters.incoming)
async def userbot_receive_link(client, message):
    text = message.text.lower()
    if text == "!pings":
       await message.reply("🏓 Userbot is running!")
