# Thanks to TeamUltroid for their Song Module.

import os
import random
import time
import logging
import asyncio
import requests
import aiohttp
import json
from io import BytesIO
from aiohttp import ClientSession
from traceback import format_exc
from Python_ARQ import ARQ
from youtube_dl import YoutubeDL
from pyrogram import filters, Client, idle
from youtubesearchpython import VideosSearch
from pyrogram.types import Message, InputMediaAudio
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup 
from pyrogram.types import (
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
)
from config import API_ID, API_HASH, BOT_TOKEN, ARQ_API_KEY, ARQ_API_URL


# logging
bot = Client(
   "Song Downloader",
   api_id=API_ID,
   api_hash=API_HASH,
   bot_token=BOT_TOKEN,
)

aiohttpsession = ClientSession()
arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)

opts = {
    "format": "bestaudio",
    "addmetadata": True,
    "key": "FFmpegMetadata",
    "writethumbnail": True,
    "prefer_ffmpeg": True,
    "nocheckcertificate": True,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }
    ],
    "outtmpl": "%(id)s.mp3",
    "quiet": False,
    "logtostderr": False,
}

async def quotify(messages: list):
    response = await arq.quotly(messages)
    if not response.ok:
        return [False, response.result]
    sticker = response.result
    sticker = BytesIO(sticker)
    sticker.name = "sticker.webp"
    return [True, sticker]


def getArg(message: Message) -> str:
    arg = message.text.strip().split(None, 1)[1].strip()
    return arg


def isArgInt(message: Message) -> bool:
    count = getArg(message)
    try:
        count = int(count)
        return [True, count]
    except ValueError:
        return [False, 0]


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
async def song(client, message):
    if len(message.command) < 2:
       return await message.reply("**Usage:**\n - `/song [query]`")
    query = message.text.split(None, 1)[1]
    user_name = message.from_user.first_name
    shed = await message.reply("🔎 Finding the Song...")
    
    try:
        search = VideosSearch(query, limit=1)
        for result in search.result()["result"]:
            ytid = result['id']
            url = f"https://www.youtube.com/watch?v={ytid}"
    except Exception as e:
        await shed.edit(
            "❌ Found Nothing.\nTry another keyword or maybe spell it properly."
        )
        print(str(e))
        return
    await shed.edit("📥 Downloading...")
    try:
            with YoutubeDL(opts) as rip:
                rip_data = rip.extract_info(url)
                rip_file = rip.prepare_filename(rip_data)
            
            dir = os.listdir()
            if f"{rip_data['id']}.mp3.jpg" in dir:
                thumb = f"{rip_data['id']}.mp3.jpg"
            elif f"{rip_data['id']}.mp3.webp" in dir:
                thumb = f"{rip_data['id']}.mp3.webp"
            else:
                thumb = None
            tail = time.time()
            CAPT = f"**🎶 Song -** [{rip_data['title']}]({url}) \n**👤 Req. By -** `{user_name}` \n"
            s = await message.reply_audio(rip_file, caption=CAPT, thumb=thumb, parse_mode='md', title=str(rip_data["title"]), duration=int(rip_data["duration"]))
            await shed.delete()
            try:
                os.remove(f"{rip_data['id']}.mp3")
                os.remove(thumb)
            except Exception as eo:
                print(eo)
    except Exception as e:
            await shed.edit("❌ Error")
            print(e)
   
@bot.on_message(filters.command(["q", "quote"]) & ~filters.edited)
async def quotly_func(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("`Reply To a Message To Quote It 🙄!`")
    if not message.reply_to_message.text:
        return await message.reply_text(
            "`Replied Message didn't contain any text! Please Reply To a Text Message 🥺!`"
        )
    m = await message.reply_text("`Quoting Messages...`")
    if len(message.command) < 2:
        messages = [message.reply_to_message]

    elif len(message.command) == 2:
        arg = isArgInt(message)
        if arg[0]:
            if arg[1] < 2 or arg[1] > 10:
                return await m.edit("`Argument must be between 2-10`")
            count = arg[1]
            messages = await client.get_messages(
                message.chat.id,
                [
                    i
                    for i in range(
                        message.reply_to_message.message_id,
                        message.reply_to_message.message_id + count,
                    )
                ],
                replies=0,
            )
        else:
            if getArg(message) != "r":
                return await m.edit(
                    f"Incorrect Argument, Pass `r` or `INT` \n**Example:** `/q 2`"
                )
            reply_message = await client.get_messages(
                message.chat.id,
                message.reply_to_message.message_id,
                replies=1,
            )
            messages = [reply_message]
    else:
        await m.edit(
            f"Incorrect Argument, Pass `r` or `INT` \n**Example:** `/q 2`"
        )
        return
    try:
        sticker = await quotify(messages)
        if not sticker[0]:
            await message.reply_text(sticker[1])
            return await m.delete()
        sticker = sticker[1]
        await message.reply_sticker(sticker)
        await m.delete()
        sticker.close()
    except Exception as e:
        await m.edit(f"`Something wrong happened while quoting messages. This error usually happens when there's a message containing something other than text.`")
        e = format_exc()
        print(e)

@bot.on_inline_query()
async def inline_query_handler(client, query):
    answers = []
    text = query.query.lower()
    if text == "":
        await client.answer_inline_query(
            query.id,
            results=answers,
            switch_pm_text="Type a YouTube Video Name...",
            switch_pm_parameter="start",
            cache_time=0,
         )
    else:
        search = VideosSearch(text, limit=10)
        for result in search.result()["result"]:
            url = f"https://www.youtube.com/watch?v={result['id']}"
            ytid = result['id']
            songname = result["title"]
            thumbid = result["thumbnails"][0]["url"]
            split = thumbid.split("?")
            photoid = split[0].strip()
            answers.append(
                InlineQueryResultPhoto(
                    photo_url=photoid,
                    title=result["title"],                    
                    description="{}, {} views.".format(
                        result["duration"], result["viewCount"]["short"]
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Download",
                                    callback_data=f"ytdl_{ytid}_audio"
                                ),
                                InlineKeyboardButton(
                                    text="Search",
                                    switch_inline_query_current_chat=""
                                )
                            ]
                        ]
                    ),
                    caption=f"**🎶 Song** - [{songname}]({url})",
                )   
            )
        await client.answer_inline_query(query.id, cache_time=0, results=answers)
        

@bot.on_callback_query(filters.regex(pattern="ytdl_(.*)_audio"))
async def yt_dl_audio(client, cb):
    ytid = cb.matches[0].group(1)
    url = f"https://www.youtube.com/watch?v={ytid}"
    oops = await cb.edit_message_text("`Downloading...`")
    try:
        with YoutubeDL(opts) as rip:
            rip_data = rip.extract_info(url)
            rip_file = rip.prepare_filename(rip_data)
        dir = os.listdir()
        if f"{rip_data['id']}.mp3.jpg" in dir:
            thumb = f"{rip_data['id']}.mp3.jpg"
        elif f"{rip_data['id']}.mp3.webp" in dir:
            thumb = f"{rip_data['id']}.mp3.webp"
        else:
            thumb = None
        ohhkay = await client.send_audio(-1001598544910, rip_file, duration=int(rip_data["duration"]), title=str(rip_data["title"]), thumb=thumb)
        await asyncio.sleep(1)
        CAPT = f"**🎶 Song -** [{rip_data['title']}]({url})"
        await cb.edit_message_media(InputMediaAudio(f"{ohhkay.audio.file_id}", caption=CAPT))
    except Exception as e:
        print (e)
    


bot.start()
idle()
