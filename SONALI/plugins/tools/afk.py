import time
from config import BOT_USERNAME
from pyrogram.enums import MessageEntityType
from pyrogram import filters
from pyrogram.types import Message
from SONALI import app
from SONALI.mongo.readable_time import get_readable_time
from SONALI.mongo.afkdb import add_afk, is_afk, remove_afk


@app.on_message(filters.command(["afk", "offline"], prefixes=["/", "!"]))
async def active_afk(_, message: Message):
    if message.sender_chat:
        return
    user_id = message.from_user.id
    verifier, reasondb = await is_afk(user_id)
    if verifier:
        await remove_afk(user_id)
        try:
            timeafk = reasondb["time"]
            reasonafk = reasondb["reason"]
            seenago = get_readable_time((int(time.time() - timeafk)))

            if reasonafk:
                await message.reply_text(
                    f"**{message.from_user.first_name}** is back online and was away for {seenago}\n\nReason: `{reasonafk}`",
                    disable_web_page_preview=True,
                )
            else:
                await message.reply_text(
                    f"**{message.from_user.first_name}** is back online and was away for {seenago}",
                    disable_web_page_preview=True,
                )
        except Exception:
            await message.reply_text(
                f"**{message.from_user.first_name}** is back online",
                disable_web_page_preview=True,
            )

    if len(message.command) == 1:
        details = {
            "type": "text",
            "time": time.time(),
            "data": None,
            "reason": None,
        }
    else:
        _reason = (message.text.split(None, 1)[1].strip())[:100]
        details = {
            "type": "text_reason",
            "time": time.time(),
            "data": None,
            "reason": _reason,
        }

    await add_afk(user_id, details)
    await message.reply_text(f"{message.from_user.first_name} is now AFK!")


chat_watcher_group = 1


@app.on_message(
    ~filters.me & ~filters.bot & ~filters.via_bot,
    group=chat_watcher_group,
)
async def chat_watcher_func(_, message):
    if message.sender_chat:
        return

    userid = message.from_user.id
    user_name = message.from_user.first_name
    msg = ""
    replied_user_id = 0

    # If AFK user sends a message
    verifier, reasondb = await is_afk(userid)
    if verifier:
        await remove_afk(userid)
        try:
            timeafk = reasondb["time"]
            reasonafk = reasondb["reason"]
            seenago = get_readable_time((int(time.time() - timeafk)))

            if reasonafk:
                msg += f"**{user_name[:25]}** is back online and was away for {seenago}\n\nReason: `{reasonafk}`\n\n"
            else:
                msg += f"**{user_name[:25]}** is back online and was away for {seenago}\n\n"
        except Exception:
            msg += f"**{user_name[:25]}** is back online\n\n"

    # If replying to an AFK user
    if message.reply_to_message:
        try:
            replied_first_name = message.reply_to_message.from_user.first_name
            replied_user_id = message.reply_to_message.from_user.id
            verifier, reasondb = await is_afk(replied_user_id)
            if verifier:
                timeafk = reasondb["time"]
                reasonafk = reasondb["reason"]
                seenago = get_readable_time((int(time.time() - timeafk)))

                if reasonafk:
                    msg += f"**{replied_first_name[:25]}** is AFK since {seenago}\n\nReason: `{reasonafk}`\n\n"
                else:
                    msg += f"**{replied_first_name[:25]}** is AFK since {seenago}\n\n"
        except:
            pass

    # If mentioned user is AFK
    if message.entities:
        for entity in message.entities:
            if entity.type == MessageEntityType.MENTION:
                found = message.text[entity.offset : entity.offset + entity.length]
                if found.startswith("@"):
                    username = found[1:]
                    try:
                        user = await app.get_users(username)
                        if user.id == replied_user_id:
                            continue
                        verifier, reasondb = await is_afk(user.id)
                        if verifier:
                            timeafk = reasondb["time"]
                            reasonafk = reasondb["reason"]
                            seenago = get_readable_time((int(time.time() - timeafk)))

                            if reasonafk:
                                msg += f"**{user.first_name[:25]}** is AFK since {seenago}\n\nReason: `{reasonafk}`\n\n"
                            else:
                                msg += f"**{user.first_name[:25]}** is AFK since {seenago}\n\n"
                    except:
                        continue

            elif entity.type == MessageEntityType.TEXT_MENTION:
                try:
                    user_id = entity.user.id
                    if user_id == replied_user_id:
                        continue
                    first_name = entity.user.first_name
                except:
                    continue

                verifier, reasondb = await is_afk(user_id)
                if verifier:
                    timeafk = reasondb["time"]
                    reasonafk = reasondb["reason"]
                    seenago = get_readable_time((int(time.time() - timeafk)))

                    if reasonafk:
                        msg += f"**{first_name[:25]}** is AFK since {seenago}\n\nReason: `{reasonafk}`\n\n"
                    else:
                        msg += f"**{first_name[:25]}** is AFK since {seenago}\n\n"

    if msg != "":
        try:
            await message.reply_text(msg, disable_web_page_preview=True)
        except:
            return
