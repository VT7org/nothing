import asyncio
import time
from datetime import datetime
from logging import getLogger

from pyrogram import enums, filters
from pyrogram.types import ChatMemberUpdated

from SONALI import app
from SONALI.utils.database import get_assistant

LOGGER = getLogger(__name__)


class AWelDatabase:
    def __init__(self):
        self.data = {}

    async def find_one(self, chat_id):
        return self.data.get(chat_id)

    async def set_welcome(self, chat_id, custom_text=None):
        self.data[chat_id] = {
            "enabled": True,
            "custom_text": custom_text
        }

    async def disable_welcome(self, chat_id):
        if chat_id in self.data:
            del self.data[chat_id]

    async def is_enabled(self, chat_id):
        entry = self.data.get(chat_id)
        return entry and entry.get("enabled", False)

    async def get_custom_text(self, chat_id):
        entry = self.data.get(chat_id)
        return entry.get("custom_text") if entry else None


wlcm = AWelDatabase()

# Anti-spam
user_last_message_time = {}
user_command_count = {}
SPAM_THRESHOLD = 2
SPAM_WINDOW_SECONDS = 5


@app.on_message(filters.command("awelcome") & ~filters.private)
async def auto_state(_, message):
    user_id = message.from_user.id
    current_time = time.time()

    # Spam control
    last_time = user_last_message_time.get(user_id, 0)
    if current_time - last_time < SPAM_WINDOW_SECONDS:
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            warn = await message.reply_text(
                f"{message.from_user.mention}, don't spam! Try again in 5 seconds."
            )
            await asyncio.sleep(3)
            return await warn.delete()
    else:
        user_command_count[user_id] = 1
        user_last_message_time[user_id] = current_time

    chat_id = message.chat.id
    user = await app.get_chat_member(chat_id, user_id)

    if user.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        return await message.reply_text("Only admins can use this command.")

    if len(message.command) == 1:
        return await message.reply_text("Usage:\n• `/awelcome on|off`\n• `/awelcome <your custom message>`")

    args = message.text.split(None, 1)[1].strip()

    if args.lower() == "off":
        await wlcm.disable_welcome(chat_id)
        return await message.reply_text("Assistant welcome has been disabled.")

    elif args.lower() == "on":
        await wlcm.set_welcome(chat_id)
        return await message.reply_text("Assistant welcome has been enabled.")

    else:
        # Treat it as a custom message
        await wlcm.set_welcome(chat_id, custom_text=args)
        return await message.reply_text("Custom welcome message has been set and enabled!")


@app.on_chat_member_updated(filters.group, group=5)
async def greet_new_members(_, member: ChatMemberUpdated):
    try:
        chat_id = member.chat.id
        userbot = await get_assistant(chat_id)

        # Exit if not enabled
        if not await wlcm.is_enabled(chat_id):
            return

        # Only proceed on actual joining (not leaving)
        if member.old_chat_member and member.old_chat_member.status != "left":
            return

        if member.new_chat_member.status != "member":
            return

        user = member.new_chat_member.user
        count = await app.get_chat_members_count(chat_id)
        join_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        custom_text = await wlcm.get_custom_text(chat_id)

        # Welcome message format
        body = (
            f"👋 **Welcome to {member.chat.title}!**\n\n"
            f"**Name:** {user.mention}\n"
            f"**Username:** @{user.username if user.username else 'N/A'}\n"
            f"**User ID:** `{user.id}`\n"
            f"**Join Time:** {join_time}\n\n"
        )

        if custom_text:
            body += f"📝 **Message:** {custom_text}"

        await asyncio.sleep(1)
        await userbot.send_message(chat_id, text=body)

    except Exception as e:
        LOGGER.error(f"Error in welcome handler: {e}")
