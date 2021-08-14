from os import path

from youtube_dl import YoutubeDL

ytdl = YoutubeDL(
    {
        "format": "bestaudio[ext=m4a]",
        "writethumbnail": True,
        "outtmpl": 'downloads/%(id)s.%(ext)s',
    }
)


def download(url: str) -> str:
    info = ytdl.extract_info(url, False)
    ytdl.download([url])
    return path.join('downloads', f"{info['id']}.{info['ext']}")
