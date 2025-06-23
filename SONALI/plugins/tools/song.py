import os
import re
import requests
import yt_dlp
from pyrogram import filters
from youtube_search import YoutubeSearch
from config import SUPPORT_CHAT, LOGGER_ID
from ... import app


def time_to_seconds(time):
    return sum(int(x) * 60**i for i, x in enumerate(reversed(str(time).split(":"))))


def get_cookie_path():
    online_url = "https://v0-mongo-db-api-setup.vercel.app/api/cookies.txt"
    fallback_path = "SONALI/assets/cookies.txt"
    try:
        resp = requests.get(online_url, timeout=5)
        if resp.status_code == 200:
            with open("cookies.txt", "wb") as f:
                f.write(resp.content)
            return "cookies.txt"
    except Exception as e:
        print(f"[Cookie Download Error] Using fallback: {e}")
    return fallback_path


def extract_youtube_video_id(url_or_query):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:[?&]|$)"
    match = re.search(regex, url_or_query)
    if match:
        return match.group(1)
    return None


@app.on_message(filters.command(["song", "music"]))
def song(client, message):
    message.delete()
    user = message.from_user
    requester = f"[{user.first_name}](tg://user?id={user.id})"
    query = " ".join(message.command[1:])
    print(f"Searching: {query}")

    m = message.reply("**» sᴇᴀʀᴄʜɪɴɢ, ᴩʟᴇᴀsᴇ ᴡᴀɪᴛ...**")

    if not query:
        m.edit("**» ᴩʟᴇᴀsᴇ ᴩʀᴏᴠɪᴅᴇ ᴀ sᴏɴɢ ɴᴀᴍᴇ ᴏʀ ᴀ ʏᴏᴜᴛᴜʙᴇ ʟɪɴᴋ.**")
        return

    video_id = None
    if "youtube.com/watch" in query or "youtu.be/" in query:
        video_id = extract_youtube_video_id(query)
        if "list=" in query:
            m.edit("**» ʏᴏᴜᴛᴜʙᴇ ᴘʟᴀʏʟɪsᴛs ᴀʀᴇ ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ.**")
            return
        if "music.youtube.com" in query:
            m.edit("**» ʏᴏᴜᴛᴜʙᴇ ᴍᴜsɪᴄ ʟɪɴᴋs ᴀʀᴇ ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ.**")
            return

    try:
        if video_id:
            link = f"https://youtube.com/watch?v={video_id}"
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(link, download=False)

                if info.get('is_live'):
                    m.edit("**» ʟɪᴠᴇ sᴛʀᴇᴀᴍs ᴀʀᴇ ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ.**")
                    return

                title = info.get('title', 'Unknown Title')[:40]
                thumbnail = info.get('thumbnail')
                duration = info.get('duration')
                views = info.get('view_count', 0)
                duration_str = f"{duration//60}:{duration%60:02d}"
        else:
            results = YoutubeSearch(query, max_results=1).to_dict()
            link = f"https://youtube.com{results[0]['url_suffix']}"
            if "list=" in link:
                m.edit("**» ʏᴏᴜᴛᴜʙᴇ ᴘʟᴀʏʟɪsᴛs ᴀʀᴇ ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ.**")
                return
            title = results[0]["title"][:40]
            thumbnail = results[0]["thumbnails"][0]
            duration = results[0]["duration"]
            views = results[0]["views"]
            duration_str = duration

        thumb_name = f"thumb_{title}.jpg"
        with open(thumb_name, "wb") as f:
            f.write(requests.get(thumbnail).content)

    except Exception as e:
        m.edit("**😴 ɴᴏ sᴏɴɢ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ.**")
        print(e)
        return

    m.edit("**» ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ... ᴩʟᴇᴀsᴇ ᴡᴀɪᴛ...**")

    cookie_path = get_cookie_path()
    ydl_opts = {
        "format": "bestaudio[ext=m4a]",
        "cookiefile": cookie_path,
        "outtmpl": "%(title)s.%(ext)s",
        "quiet": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            audio_file = ydl.prepare_filename(info)

        rep = (
            f"**🎵 ᴛɪᴛʟᴇ :** {title[:25]}\n"
            f"**⏱️ ᴅᴜʀᴀᴛɪᴏɴ :** `{duration_str}`\n"
            f"**👀 ᴠɪᴇᴡs :** `{views}`\n"
            f"**🙋‍♂️ ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {requester}"
        )

        duration_sec = time_to_seconds(duration_str)

        # Send to user
        message.reply_audio(
            audio_file,
            caption=rep,
            performer=app.name,
            title=title,
            duration=duration_sec,
            thumb=thumb_name,
        )

        # Send to LOGGER_ID
        app.send_audio(
            LOGGER_ID,
            audio_file,
            caption=f"**[LOGGER]** {rep}\n\n**💫 ᴩᴏᴡᴇʀᴇᴅ ʙʏ : @BillaSpace**",
            performer=app.name,
            title=title,
            duration=duration_sec,
            thumb=thumb_name,
        )

        m.delete()

    except Exception as e:
        m.edit(
            f"**» ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴇʀʀᴏʀ.**\n**ᴇʀʀᴏʀ :** `{e}`\n\n[Support](t.me/{SUPPORT_CHAT})"
        )
        print(e)

    for file in [audio_file, thumb_name]:
        try:
            os.remove(file)
        except:
            pass
