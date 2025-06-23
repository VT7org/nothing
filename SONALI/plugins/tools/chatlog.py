import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import LOGGER_ID
from SONALI import app

@app.on_message(filters.new_chat_members, group=2)
async def join_watcher(_, message):    
    chat = message.chat
    link = await app.export_chat_invite_link(chat.id)
    for member in message.new_chat_members:
        if member.id == app.id:
            count = await app.get_chat_members_count(chat.id)
            msg = (
                f"✫ ᴀᴅᴅᴇᴅ ɪɴ ᴀ ɴᴇᴡ ɢʀᴏᴜᴘ\n\n"
                f"ᴄʜᴀᴛ ɴᴀᴍᴇ: {chat.title}\n"
                f"ᴄʜᴀᴛ ɪᴅ: {chat.id}\n"
                f"ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ: @{chat.username if chat.username else 'No Username'}\n"
                f"ᴄʜᴀᴛ ʟɪɴᴋ: {link}\n"
                f"ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs: {count}\n"
                f"ᴀᴅᴅᴇᴅ ʙʏ: {message.from_user.mention}"
            )
            await app.send_message(LOGGER_ID, msg, reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 View Group", url=link)]
            ]))

@app.on_message(filters.left_chat_member)
async def on_left_chat_member(_, message: Message):
    if (await app.get_me()).id == message.left_chat_member.id:
        remove_by = message.from_user.mention if message.from_user else "Unknown User"
        title = message.chat.title
        username = f"@{message.chat.username}" if message.chat.username else "Private Chat"
        chat_id = message.chat.id
        left = (
            f"✫ <b><u>#Left_Group</u></b> ✫\n\n"
            f"Chat Title: {title}\n"
            f"Chat ID: {chat_id}\n"
            f"Removed By: {remove_by}\n"
            f"Bot: @{app.username}"
        )
        await app.send_message(LOGGER_ID, left)
