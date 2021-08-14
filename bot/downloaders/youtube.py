from os import path

from youtube_dl import YoutubeDL

ytdl = YoutubeDL(
    {
        "format": "bestaudio/best",
        "writethumbnail": True,
        "outtmpl": 'downloads/%(id)s.%(ext)s',
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }
        ],
    }
)


def download(url: str) -> str:
    info = ytdl.extract_info(url, False)
    ytdl.download([url])
    return path.join('downloads', f"{info['id']}.mp3")
