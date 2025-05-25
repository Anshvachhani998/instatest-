from pyrogram import Client, filters
import asyncio
from collections import deque

GROUP_ID = -1002506415678
 
app = Client
queue = deque()
processing = False
message_map = {}

@app.on_message(filters.private & filters.text & filters.regex("https://www.instagram.com/"))
async def add_to_queue(client, message):
    queue.append((message.chat.id, message.text, message.id))
    await message.reply("Your link is added to queue, please wait...")
    await process_queue(client)

async def process_queue(client):
    global processing
    if processing or not queue:
        return

    processing = True
    user_id, link, user_msg_id = queue.popleft()

    # Send link to group
    sent_msg = await client.send_message(GROUP_ID, link)
    message_map[sent_msg.message_id] = (user_id, user_msg_id)

    # Wait max 30 seconds for reply
    for _ in range(30):
        await asyncio.sleep(1)
        if sent_msg.message_id not in message_map:
            break  # response received

    processing = False
    await process_queue(client)

@app.on_message(filters.chat(GROUP_ID) & (filters.video | filters.document | filters.photo) & filters.reply)
async def group_reply_handler(client, message):
    reply_id = message.reply_to_message.message_id
    user_info = message_map.get(reply_id)

    if user_info:
        user_id, original_msg_id = user_info
        await client.copy_message(
            chat_id=user_id,
            from_chat_id=GROUP_ID,
            message_id=message.id
        )
        # Clean up
        del message_map[reply_id]
