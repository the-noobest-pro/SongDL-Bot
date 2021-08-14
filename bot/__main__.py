import os
import logging
import requests
import aiohttp
import json
import youtube_dl
from pyrogram import filters, Client, idle
from youtube_search import YoutubeSearch
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup 

from .config import API_ID, API_HASH, BOT_TOKEN
from .downloaders import youtube

# logging
bot = Client(
   "Song Downloader",
   api_id=API_ID,
   api_hash=API_HASH,
   bot_token=BOT_TOKEN,
)


@bot.on_message(filters.command("start") & ~filters.edited)
async def start(_, message):
   if message.chat.type == 'private':
       await message.reply("**Hey There, I'm a song downloader bot.\nUsage:** `/song [query]`",   
                            reply_markup=InlineKeyboardMarkup(
                                [[
                                     InlineKeyboardButton(
                                            "Source", url="https://github.com/me-piro-786/SongDL-Bot")
                                    ]]
                            ))
   else:
      await message.reply("**Song DL Bot is Online ✨**")



@bot.on_message(filters.command("song") & ~filters.edited)
async def song(_, message):
    if len(message.command) < 2:
       return await message.reply("**Usage:**\n - `/song [query]`")
    query = message.text.split(None, 1)[1]
    user_name = message.from_user.first_name
    shed = await message.reply("🔎 Finding the Song...")
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        # print(results)
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)

        duration = results[0]["duration"]
        results[0]["url_suffix"]
        results[0]["views"]

    except Exception as e:
        await shed.edit(
            "❌ Found Nothing.\n\nTry another keyword or maybe spell it properly."
        )
        print(str(e))
        return
    await shed.edit("📥 Downloading...")
    try:
        audio_file = youtube.download(link)
        rep = f"**🎶 Song Name :** [{title}]({link}) \n**👤 Requested By :** {user_name} \n**🔍 Requested For :** `{query}`"
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        await shed.edit("📤 Uploading...")
        s = await message.reply_audio(audio_file, caption=rep, thumb=thumb_name, parse_mode='md', title=title, duration=dur)
        await shed.delete()
    except Exception as e:
        await shed.edit("❌ Error")
        print(e)

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)

bot.start()
idle() 
