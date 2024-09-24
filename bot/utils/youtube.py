# bot/utils/youtube.py
import discord  # Add this import at the top of the file
import yt_dlp as youtube_dl
import asyncio
import logging
import os
import requests
import html

logger = logging.getLogger(__name__)

# yt-dlp options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'audio_files/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.3',
        'retries': 3  # Number of retries in case of errors
    }
}

ffmpeg_options = {
    'before_options':
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# Detect ffmpeg path depending on the environment
if os.name == 'nt':  # Windows
    ffmpeg_path = "./ffmpeg.exe"  # Assuming ffmpeg.exe is in the project root
else:  # Unix/Linux including Raspberry Pi
    ffmpeg_path = "/usr/bin/ffmpeg"  # Default path for ffmpeg in Docker

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, download=False, max_retries=3, retry_delay=5):
        loop = loop or asyncio.get_event_loop()
        attempts = 0
        last_exception = None

        while attempts < max_retries:
            try:
                data = await loop.run_in_executor(
                    None, lambda: ytdl.extract_info(url, download=download, process=True)
                )

                # Check if it's a playlist or a single track
                if 'entries' in data:  # Playlist
                    return [
                        cls(discord.FFmpegPCMAudio(
                            executable=ffmpeg_path, source=entry['url'], **ffmpeg_options), data=entry)
                        for entry in data['entries']
                    ]
                else:  # Single track
                    return cls(discord.FFmpegPCMAudio(
                        executable=ffmpeg_path, source=data['url'], **ffmpeg_options), data=data)

            except youtube_dl.utils.DownloadError as e:
                last_exception = e
                logger.error(f"DownloadError: {e}. Retrying in {retry_delay} seconds... (Attempt {attempts + 1}/{max_retries})")
                await asyncio.sleep(retry_delay)
                attempts += 1

            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error: {e}. Retrying in {retry_delay} seconds... (Attempt {attempts + 1}/{max_retries})")
                await asyncio.sleep(retry_delay)
                attempts += 1

        logger.error(f"Failed to download after {max_retries} attempts. Last exception: {last_exception}")
        return None  # Return None after max retries

# Fallback to yt-dlp search
async def yt_dlp_search(query):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(
        None, lambda: ytdl.extract_info(f"ytsearch5:{query}", download=False))
    return [{
        'url': entry['webpage_url'],
        'title': html.unescape(entry['title'])  # Unescape HTML entities
    } for entry in data.get('entries', [])]

# Search using YouTube Data API
async def youtube_api_search(query):
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': 5,
        'key': os.getenv("YOUTUBE_API_KEY")
    }
    try:
        response = requests.get("https://www.googleapis.com/youtube/v3/search",
                                params=params)
        response.raise_for_status()
        data = response.json()
        videos = [
            {
                'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                'title': html.unescape(item['snippet']['title'])  # Unescape HTML entities
            } for item in data['items']
        ]
        return videos
    except requests.exceptions.RequestException as e:
        logger.error(f"API error: {e}")
        return None

# Check API usage and fallback to yt-dlp if limit is hit
async def search_youtube(query):
    videos = await youtube_api_search(query)
    if not videos:
        logger.info("YouTube API failed, falling back to yt-dlp.")
        videos = await yt_dlp_search(query)
    return videos
