from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SONALI import app
from config import BOT_USERNAME
from SONALI.utils.errors import capture_err
import httpx 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_txt = """
✰ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ᴘʀᴏ-ʙᴏᴛ ᴘᴀᴄᴋᴇᴅ ᴡɪᴛʜ ᴀɪ-ɪɴᴛᴇʟʟɪɢᴇɴᴄᴇ ᴄᴏʀᴇs 
 
✰ ᴏғғɪᴄɪᴀʟʟʏ ʙᴀᴄᴋᴇᴅ ʙʏ sᴘᴀᴄᴇ-x & ᴄᴏ-ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴏᴘᴜs+
 
✰ ʙᴜɪʟᴛ ᴡɪᴛʜ ᴛʜᴇ sᴄʀᴀᴛᴄʜ ɴ ᴅɪᴍɴɪsʜᴇᴅ ᴄᴏᴅᴇs ɪ ʜᴀᴠᴇ ᴡᴏᴠᴇɴ ᴛʜᴇᴍ ᴘʀᴇᴄɪᴏᴜsʟʏ
 
✰ ᴀʟᴡᴀʏs ʜᴀᴠᴇ 24×7 ᴜᴘᴛɪᴍᴇ ᴡɪᴛʜᴏᴜᴛ ʟᴀɢs ɴ ɢʟɪᴛᴄʜᴇs
 
"""




@app.on_message(filters.command("dev"))
async def start(_, msg):
    buttons = [
        [ 
          InlineKeyboardButton("ᴄᴀᴛᴄʜ ᴍᴇ", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
        ],
        [
          InlineKeyboardButton("ʜᴇʟᴘ", url="https://t.me/BillaCore"),
          InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/x_ifeelram"),
          ],
               [
                InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/BillaCore"),
],
[
InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs", url=f"https://t.me/BillaSpace"),

        ]]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await msg.reply_photo(
        photo="https://graph.org/file/0799b110240ef68c1519b-46d4e55cf4b3b1b908.jpg",
        caption=start_txt,
        reply_markup=reply_markup
    )
