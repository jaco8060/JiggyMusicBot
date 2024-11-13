# bot/utils/audio.py

import discord
import os
import asyncio
import logging
from bot.utils.youtube import YTDLSource, search_youtube  

logger = logging.getLogger(__name__)

song_queue = []

# Detect ffmpeg path depending on the environment
if os.name == 'nt':  # Windows
    ffmpeg_path = "./ffmpeg.exe"  # Assuming ffmpeg.exe is in the project root
else:  # Unix/Linux including Raspberry Pi
    ffmpeg_path = "/usr/bin/ffmpeg"  # Default path for ffmpeg in Docker

ffmpeg_options = {
    'before_options':
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# Fetch the playback URL just before playing the song
async def fetch_playback_url(song):
    """
    Fetches the playback URL for a given song.
    The song should have a 'type' (e.g., 'url', 'query', 'file') and relevant details.
    """
    if song['type'] == 'url':
        # Fetch the playback URL using YTDLSource with process=True
        data = await YTDLSource.from_url(
            song['url'], loop=asyncio.get_event_loop(), download=False, process=True
        )
        if data is None:
            return None
        return data.data.get('url')
    elif song['type'] == 'query':
        # If it's a query, search for the URL using the YouTube API or yt-dlp
        videos = await search_youtube(song['query'])
        if videos:
            return videos[0]['url']  # Return the first video result
    elif song['type'] == 'file':
        # For local files, return the file path
        return song['path']
    return None  # Return None if no URL can be found

# Function to play the next song in the queue
async def play_next_song(voice_client):
    if song_queue:
        next_song = song_queue.pop(0)

        # Ensure the song has the correct structure
        if 'url' not in next_song and 'query' not in next_song and 'path' not in next_song:
            logger.warning(f"Skipping invalid song entry: {next_song}")
            await play_next_song(voice_client)  # Skip to the next song
            return

        # Fetch the playback URL or file path just before playing
        playback_url = await fetch_playback_url(next_song)

        if not playback_url:
            logger.warning(f"Could not fetch URL for song: {next_song}")
            await play_next_song(voice_client)  # Skip to the next song
            return

        # Log the URL of the song to be played
        logger.info(f"Now playing: {next_song.get('title', 'Unknown title')}")

        # Create the audio player using the fetched playback URL or file path
        if next_song['type'] == 'file':
            player = discord.FFmpegPCMAudio(
                executable=ffmpeg_path, source=playback_url)
        else:
            player = discord.FFmpegPCMAudio(
                executable=ffmpeg_path, source=playback_url, **ffmpeg_options)

        def after_playing(e):
            if e:
                logger.error(f"Error occurred during playback: {e}")
            if next_song['type'] == 'file':
                try:
                    os.remove(next_song['path'])
                    logger.info(f"Deleted file after playback: {next_song['path']}")
                except Exception as err:
                    logger.error(f"Error deleting file: {err}")
            # Proceed to play the next song
            coro = play_next_song(voice_client)
            fut = asyncio.run_coroutine_threadsafe(coro, voice_client.loop)
            try:
                fut.result()
            except Exception as e:
                logger.error(f"Error in after_playing: {e}")

        voice_client.play(player, after=after_playing)
    else:
        # Disconnect from the voice channel
        await voice_client.disconnect()
        song_queue.clear()
        logger.info("Queue is empty. Disconnected from voice channel.")

        # Delete all files in audio_files directory
        audio_folder = "audio_files"
        for filename in os.listdir(audio_folder):
            file_path = os.path.join(audio_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e}")

        logger.info("Cleaned up audio_files directory.")
