import discord
import yt_dlp as youtube_dl
import os
import asyncio
from bot import utils

# Global song queue
song_queue = []

# yt-dlp options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': f'{utils.AUDIO_FOLDER}/%(extractor)s-%(id)s-%(title)s.%(ext)s',
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.3',
        'retries': 3  # Number of retries in case of errors
    }
}

ffmpeg_options = {
    'before_options':
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# Define YTDLSource class to handle audio playback from YouTube
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
                        cls(discord.FFmpegPCMAudio(executable=utils.FFMPEG_PATH, source=entry['url'], **ffmpeg_options), data=entry)
                        for entry in data['entries']
                    ]
                else:  # Single track
                    return cls(discord.FFmpegPCMAudio(executable=utils.FFMPEG_PATH, source=data['url'], **ffmpeg_options), data=data)

            except youtube_dl.utils.DownloadError as e:
                last_exception = e
                print(f"DownloadError: {e}. Retrying in {retry_delay} seconds... (Attempt {attempts + 1}/{max_retries})")
                await asyncio.sleep(retry_delay)
                attempts += 1

            except Exception as e:
                last_exception = e
                print(f"Unexpected error: {e}. Retrying in {retry_delay} seconds... (Attempt {attempts + 1}/{max_retries})")
                await asyncio.sleep(retry_delay)
                attempts += 1

        print(f"Failed to download after {max_retries} attempts. Last exception: {last_exception}")
        return None  # Return None after max retries

# Function to play the next song in the queue
async def play_next_song(voice_client):
    if song_queue:
        next_song = song_queue.pop(0)

        # Ensure the song has the correct structure
        if 'url' not in next_song and 'query' not in next_song and 'path' not in next_song:
            print(f"Skipping invalid song entry: {next_song}")
            await play_next_song(voice_client)  # Skip to the next song
            return

        # Fetch the playback URL or file path just before playing
        if next_song['type'] == 'url' or next_song['type'] == 'query':
            playback_url = await fetch_playback_url(next_song)

            if not playback_url:
                print(f"Could not fetch URL for song: {next_song}")
                await play_next_song(voice_client)  # Skip to the next song
                return

            # Log the URL of the song to be played
            print(f"Now playing URL: {playback_url}")
            # Create the audio player using the fetched playback URL
            player = discord.FFmpegPCMAudio(executable=utils.FFMPEG_PATH, source=playback_url, **ffmpeg_options)

        elif next_song['type'] == 'file':
            # If it's a file, play the local file
            file_path = next_song['path']
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}. Skipping to the next song.")
                await play_next_song(voice_client)  # Skip to the next song
                return

            print(f"Now playing local file: {file_path}")
            player = discord.FFmpegPCMAudio(executable=utils.FFMPEGPATH, source=file_path)

        else:
            print(f"Unknown song type for song: {next_song}. Skipping to the next song.")
            await play_next_song(voice_client)  # Skip to the next song
            return

        def after_playing(e):
            if e:
                print(f"Error occurred during playback: {e}")
            if next_song['type'] == 'file':
                try:
                    os.remove(next_song['path'])
                except Exception as err:
                    print(f"Error deleting file: {err}")
            # Proceed to play the next song
            asyncio.run_coroutine_threadsafe(play_next_song(voice_client), bot.loop)

        voice_client.play(player, after=after_playing)
    else:
        await voice_client.disconnect()
        song_queue.clear()
        print("Queue is empty. Disconnected from voice channel.")

# Fetch the playback URL just before playing the song
async def fetch_playback_url(song):
    """
    Fetches the playback URL for a given song.
    The song should have a 'type' (e.g., 'url', 'query') and relevant details.
    """
    if song['type'] == 'url':
        # If the song already has a URL, return it
        return song['url']
    elif song['type'] == 'query':
        # If it's a query, search for the URL using the YouTube API or yt-dlp
        videos = await search_youtube(song['query'])
        if videos:
            return videos[0]['url']  # Return the first video result
    return None  # Return None if no URL can be found

# Check API usage and fallback to yt-dlp if limit is hit
async def search_youtube(query):
    videos = await youtube_api_search(query)
    if not videos:
        print("YouTube API failed, falling back to yt-dlp.")
        videos = await yt_dlp_search(query)
    return videos

# Fallback to yt-dlp search
async def yt_dlp_search(query):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(
        None, lambda: ytdl.extract_info(f"ytsearch5:{query}", download=False))
    return [{
        'url': entry['webpage_url'],
        'title': entry['title']
    } for entry in data.get('entries', [])]

# Search using YouTube Data API
async def youtube_api_search(query):
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': 5,
        'key': config.YOUTUBE_API_KEY
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
        print(f"API error: {e}")
        return None
