import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from collections import deque
import re
from bot import message_map, queue, processing

USERBOT_CHAT_ID = 5785483456

@app.on_message(filters.private & filters.text & filters.regex(r"https://www\.instagram\.com/"))
async def bot_receive_link(client, message):
    await message.reply("✅ Link received. Processing...")
    try:
        sent = await app.send_message(USERBOT_CHAT_ID, message.text)
        message_map[sent.id] = (message.chat.id, message.id)
    except Exception as e:
        await message.reply("❌ Failed to send to userbot.")
        print(e)

@app.on_message(filters.chat(USERBOT_CHAT_ID) & (filters.video | filters.document | filters.photo | filters.text) & filters.reply)
async def bot_reply_handler(client, message):
    reply_to_msg = message.reply_to_message
    reply_to_id = reply_to_msg.id
    user_data = message_map.get(reply_to_id)

    if not user_data:
        return

    user_id, original_msg_id, wait_msg_id = user_data if len(user_data) == 3 else (*user_data, None)

    is_wait_msg = message.text and message.text.startswith("Dᴏᴡɴʟᴏᴀᴅɪɴɢ Yᴏᴜʀ Rᴇᴇʟꜱ 🩷")

    try:
        if message.media:
            forwarded_msg = await client.copy_message(
                chat_id=user_id,
                from_chat_id=USERBOT_CHAT_ID,
                message_id=message.id,
                reply_to_message_id=original_msg_id,
                caption="**ʜᴇʀᴇ ɪꜱ ʏᴏᴜʀ Rᴇᴇʟꜱ 🎥**\n\n**ᴘʀᴏᴠɪᴅᴇᴅ ʙʏ @Ans_Bots**",
            )
        elif is_wait_msg:
            forwarded_msg = await client.send_message(
                chat_id=user_id,
                text=message.text
            )
        else:
            forwarded_msg = await client.send_message(
                chat_id=user_id,
                text=(
                    "**⛔️ Publication information could not be retrieved**\n\n"
                    "**Possible causes:**\n"
                    "**▫️closed (private) account;**\n"
                    "**▫️data retrieval error;**\n"
                    "**▫️the account has age restrictions.**"
                )
            )
    except Exception as e:
        print("❌ Error sending to user:", e)
        return

    if is_wait_msg:
        message_map[reply_to_id] = (user_id, original_msg_id, forwarded_msg.id)
        return

    if wait_msg_id:
        try:
            await client.delete_messages(chat_id=user_id, message_ids=wait_msg_id)
        except Exception as e:
            print("⚠️ Couldn't delete old status message:", e)

    del message_map[reply_to_id]
