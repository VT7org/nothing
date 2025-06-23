import re
import requests
from pyrogram import filters

from SONALI import app
from config import LOGGER_ID


@app.on_message(filters.command(["ig", "insta", "reel"]))
async def download_instagram_video(client, message):
    if len(message.command) < 2:
        await message.reply_text(
            "Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇ Iɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴜʀʟ ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ"
        )
        return
    url = message.text.split()[1]
    if not re.match(
        re.compile(r"^(https?://)?(www\.)?(instagram\.com|instagr\.am)/.*$"), url
    ):
        return await message.reply_text(
            "Tʜᴇ ᴘʀᴏᴠɪᴅᴇᴅ ʟɪɴᴋ ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ Iɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴜʀʟ"
        )
    a = await message.reply_text("ᴘʀᴏᴄᴇssɪɴɢ...")
    api_url = f"https://insta-dl.hazex.workers.dev/?url={url}"

    response = requests.get(api_url)
    try:
        result = response.json()
        data = result["result"]
    except Exception as e:
        f = f"Eʀʀᴏʀ :\n{e}"
        try:
            await a.edit(f)
        except Exception:
            await message.reply_text(f)
            return await app.send_message(LOGGER_ID, f)
        return await app.send_message(LOGGER_ID, f)
    if not result["error"]:
        video_url = data["url"]
        duration = data["duration"]
        quality = data["quality"]
        type = data["extension"]
        size = data["formattedSize"]
        caption = f"Dᴜʀᴀᴛɪᴏɴ : {duration}\nQᴜᴀʟɪᴛʏ : {quality}\nTʏᴘᴇ : {type}\nSɪᴢᴇ : {size}"
        await a.delete()
        await message.reply_video(video_url, caption=caption)
    else:
        try:
            return await a.edit("Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇᴇʟ")
        except Exception:
            return await message.reply_text("Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʀᴇᴇʟ")


MODULE = "Rᴇᴇʟ"
HELP = """
ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ:

• /ig [URL]: ᴅᴏᴡɴʟᴏᴀᴅ ɪɢ ʀᴇᴇʟs ғʀᴏᴍ ɪᴛs ᴜʀʟ.
• /insta [URL]: ᴅᴏᴡɴʟᴏᴀᴅ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟs. Pʀᴏᴠɪᴅᴇ ᴛʜᴇ ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ.
• /reels [URL]:  ʏᴇᴛ ᴀɴᴏᴛʜᴇʀ ᴀʟᴛᴇʀɴᴀᴛɪᴠᴇ ᴄᴏᴍᴍᴀɴᴅ ғᴏʀ ɪɢ ʀᴇᴇʟs
"""
