import os
import re
import requests
import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from youtube_search import YoutubeSearch
from config import SUPPORT_CHAT, LOGGER_ID, OWNER_ID
from ... import app

SEARCH_RESULTS = {}
DOWNLOAD_QUEUE = {}
CURRENT_DOWNLOAD = {}

def time_to_seconds(time):
    return sum(int(x) * 60**i for i, x in enumerate(reversed(str(time).split(":"))))

def get_cookie_path(fallback=False):
    if fallback:
        return "SONALI/assets/cookies.txt"
    try:
        online_url = "https://v0-mongo-db-api-setup.vercel.app/api/cookies.txt"
        resp = requests.get(online_url, timeout=5)
        if resp.status_code == 200:
            with open("cookies.txt", "wb") as f:
                f.write(resp.content)
            return "cookies.txt"
    except Exception as e:
        print(f"[Cookie Download Error] Using fallback: {e}")
    return "SONALI/assets/cookies.txt"

def extract_youtube_video_id(url_or_query):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:[?&]|$)"
    match = re.search(regex, url_or_query)
    if match:
        return match.group(1)
    if len(url_or_query.strip()) == 11 and re.match(r"^[0-9A-Za-z_-]{11}$", url_or_query.strip()):
        return url_or_query.strip()
    return None

def is_playlist(url):
    return "list=" in url and "watch?v=" not in url

@app.on_message(filters.command(["song", "music"]))
async def song(client: Client, message: Message):
    user = message.from_user
    requester = f"[{user.first_name}](tg://user?id={user.id})"
    query = " ".join(message.command[1:])

    if not query:
        return await message.reply("**» ᴩʟᴇᴀsᴇ ᴩʀᴏᴠɪᴅᴇ ᴀ sᴏɴɢ ɴᴀᴍᴇ, ʏᴏᴜᴛᴜʙᴇ ᴜʀʟ, ᴏʀ ᴠɪᴅᴇᴏ ɪᴅ.**")

    video_id = extract_youtube_video_id(query)

    if "music.youtube.com" in query:
        return await message.reply("**» ʏᴏᴜᴛᴜʙᴇ ᴍᴜsɪᴄ ʟɪɴᴋs ᴀʀᴇ ɴᴏᴛ sᴜᴩᴩᴏʀᴛᴇᴅ.**")

    if video_id:
        link = f"https://youtube.com/watch?v={video_id}"
        return await enqueue_song(client, message, link, requester)

    try:
        results = YoutubeSearch(query, max_results=5).to_dict()
    except Exception:
        return await message.reply("**» ᴇʀʀᴏʀ ᴡʜɪʟᴇ sᴇᴀʀᴄʜɪɴɢ. ᴩʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.**")

    if not results:
        return await message.reply("**» ɴᴏ sᴏɴɢs ғᴏᴜɴᴅ. ᴛʀʏ ᴀɴᴏᴛʜᴇʀ ǫᴜᴇʀʏ ᴏʀ  ᴇɴsᴜʀᴇ ᴄᴀsᴇ sᴇɴsɪᴛɪᴠᴇ ᴏғ sᴏɴɢ ɴᴀᴍᴇ ᴡɪᴛʜ ᴀʀᴛɪsᴛ ᴏʀ ʏᴛ-ᴄʜᴀɴɴᴇʟ ɴᴀᴍᴇ.**")

    SEARCH_RESULTS[message.chat.id] = results

    buttons = []
    for i, result in enumerate(results):
        title = result["title"][:40]
        buttons.append([InlineKeyboardButton(f"{i+1}. {title}", callback_data=f"select_{i}")])

    await message.reply(
        "**» sᴇʟᴇᴄᴛ ᴀ sᴏɴɢ ғʀᴏᴍ ᴛʜᴇ ʀᴇsᴜʟᴛs ʙᴇʟᴏᴡ :**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_callback_query(filters.regex(r"select_\d+"))
async def select_song(client: Client, query: CallbackQuery):
    index = int(query.data.split("_")[1])
    chat_id = query.message.chat.id

    if chat_id not in SEARCH_RESULTS or index >= len(SEARCH_RESULTS[chat_id]):
        return await query.answer("Selection expired or invalid.", show_alert=True)

    result = SEARCH_RESULTS[chat_id][index]
    link = f"https://youtube.com{result['url_suffix']}"
    requester = f"[{query.from_user.first_name}](tg://user?id={query.from_user.id})"

    await query.message.edit("**» sᴏɴɢ sᴇʟᴇᴄᴛᴇᴅ. ǫᴜᴇᴜᴇᴅ ғᴏʀ ᴅᴏᴡɴʟᴏᴀᴅ...**")
    await enqueue_song(client, query.message, link, requester)

async def enqueue_song(client: Client, message: Message, link: str, requester: str):
    chat_id = message.chat.id
    if chat_id not in DOWNLOAD_QUEUE:
        DOWNLOAD_QUEUE[chat_id] = []
    DOWNLOAD_QUEUE[chat_id].append((client, message, link, requester))

    if len(DOWNLOAD_QUEUE[chat_id]) == 1:
        await process_queue(chat_id)

async def process_queue(chat_id):
    while DOWNLOAD_QUEUE[chat_id]:
        client, message, link, requester = DOWNLOAD_QUEUE[chat_id][0]
        CURRENT_DOWNLOAD[chat_id] = {"cancelled": False}
        await process_song(client, message, link, requester, chat_id)
        DOWNLOAD_QUEUE[chat_id].pop(0)
        CURRENT_DOWNLOAD.pop(chat_id, None)

async def process_song(client: Client, message: Message, link: str, requester: str, chat_id):
    if is_playlist(link):
        return await message.reply("**» ʏᴏᴜᴛᴜʙᴇ ᴩʟᴀʏʟɪsᴛs ᴀʀᴇ ɴᴏᴛ sᴜᴩᴩᴏʀᴛᴇᴅ.**")

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(link, download=False)

            if info.get('is_live'):
                return await message.reply("**» ʟɪᴠᴇ sᴛʀᴇᴀᴍs ᴀʀᴇ ɴᴏᴛ sᴜᴩᴩᴏʀᴛᴇᴅ.**")

            title = info.get('title', 'Unknown Title')[:40]
            thumbnail = info.get('thumbnail')
            duration = info.get('duration')
            views = info.get('view_count', 0)
            duration_str = f"{duration//60}:{duration%60:02d}"

        if message.from_user.id not in OWNER_ID and duration > 900:
            return await message.reply("**» sᴏɴɢ ᴅᴜʀᴀᴛɪᴏɴ ʟɪᴍɪᴛ ɪs 15 ᴍɪɴᴜᴛᴇs. ᴏɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴅᴏᴡɴʟᴏᴀᴅ ʟᴏɴɢᴇʀ sᴏɴɢs.**")

        thumb_name = f"thumb_{title}.jpg"
        with open(thumb_name, "wb") as f:
            f.write(requests.get(thumbnail).content)

    except Exception:
        return await message.reply("** sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ, ɪsɴ'ᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ʏᴛ ᴏʀ ɪɴᴠᴀʟɪᴅ ʟɪɴᴋ.**")

    status = await message.reply(
        "**» ᴅᴏᴡɴʟᴏᴀᴅ ᴩʀᴏɢʀᴇss : 0%**",
        reply_markup=cancel_markup()
    )

    audio_file = await download_song_with_progress(link, status, chat_id)

    if not audio_file:
        audio_file = await download_song_with_progress(link, status, chat_id, fallback=True)

    if not audio_file:
        return await status.edit(f"**» ᴅᴏᴡɴʟᴏᴀᴅ ᴇʀʀᴏʀ.**\n\n[Support](t.me/{SUPPORT_CHAT})")

    rep = (
        f"**🎵 ᴛɪᴛʟᴇ :** {title[:25]}\n"
        f"**⏱️ ᴅᴜʀᴀᴛɪᴏɴ :** `{duration_str}`\n"
        f"**👀 ᴠɪᴇᴡs :** `{views}`\n"
        f"**🙋‍♂️ ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {requester}"
    )

    try:
        await message.reply_audio(
            audio_file,
            caption=rep,
            performer=app.name,
            title=title,
            duration=duration,
            thumb=thumb_name,
        )

        await app.send_audio(
            LOGGER_ID,
            audio_file,
            caption=f"**[sᴘᴀᴄᴇ-x]** {rep}\n\n**💫 ᴩᴏᴡᴇʀᴇᴅ ʙʏ : @BillaSpace**",
            performer=app.name,
            title=title,
            duration=duration,
            thumb=thumb_name,
        )

        await status.delete()

    except Exception as e:
        print(e)
        await status.edit(
            f"**» sᴇɴᴅɪɴɢ ᴇʀʀᴏʀ.**\n**ᴇʀʀᴏʀ :** `{e}`\n\n[Support](t.me/{SUPPORT_CHAT})"
        )

    for file in [audio_file, thumb_name]:
        try:
            os.remove(file)
        except:
            pass

def cancel_markup():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🚫 ᴄᴀɴᴄᴇᴋ ᴅᴏᴡɴʟᴏᴀᴅ", callback_data="cancel_download")]])

@app.on_callback_query(filters.regex("cancel_download"))
async def cancel_download(client: Client, query: CallbackQuery):
    chat_id = query.message.chat.id
    if chat_id in CURRENT_DOWNLOAD:
        CURRENT_DOWNLOAD[chat_id]["cancelled"] = True
        await query.answer("Download cancelled.", show_alert=True)
        await query.message.edit("**» ᴅᴏᴡɴʟᴏᴀᴅ ᴄᴀɴᴄᴇʟʟᴇᴅ.**")
    else:
        await query.answer("No Active Download.", show_alert=True)

async def download_song_with_progress(link, status_message, chat_id, fallback=False):
    try:
        ydl_opts = {
            "format": "bestaudio[ext=m4a]",
            "cookiefile": get_cookie_path(fallback=fallback),
            "outtmpl": "%(title)s.%(ext)s",
            "quiet": True,
            "progress_hooks": [lambda d: asyncio.create_task(update_progress(d, status_message, chat_id))]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"Download error: {e}")
        return None

async def update_progress(d, status_message, chat_id):
    if CURRENT_DOWNLOAD.get(chat_id, {}).get("cancelled"):
        raise Exception("Download Cancelled")

    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '').strip()
        eta = d.get('eta', 0)
        try:
            await status_message.edit(
                f"**» ᴅᴏᴡɴʟᴏᴀᴅ ᴩʀᴏɢʀᴇss : {percent}**\n**⏳ ᴇᴛᴀ :** {eta} sᴇᴄᴏɴᴅs",
                reply_markup=cancel_markup()
            )
        except:
            pass

