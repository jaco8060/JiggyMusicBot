# bot/utils/audio.py

import discord
import os
import asyncio
import logging
from bot.utils.youtube import search_youtube  

logger = logging.getLogger(__name__)

song_queue = []
files_to_delete = []

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
        if next_song['type'] == 'url' or next_song['type'] == 'query':
            playback_url = await fetch_playback_url(next_song)

            if not playback_url:
                logger.warning(f"Could not fetch URL for song: {next_song}")
                await play_next_song(voice_client)  # Skip to the next song
                return

            # Log the URL of the song to be played
            logger.info(f"Now playing URL: {playback_url}")
            # Create the audio player using the fetched playback URL
            player = discord.FFmpegPCMAudio(
                executable=ffmpeg_path, source=playback_url, **ffmpeg_options)

        elif next_song['type'] == 'file':
            # If it's a file, play the local file
            file_path = next_song['path']
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}. Skipping to the next song.")
                await play_next_song(voice_client)  # Skip to the next song
                return

            logger.info(f"Now playing local file: {file_path}")
            player = discord.FFmpegPCMAudio(
                executable=ffmpeg_path, source=file_path)

        else:
            logger.warning(f"Unknown song type for song: {next_song}. Skipping to the next song.")
            await play_next_song(voice_client)  # Skip to the next song
            return

        def after_playing(e):
            if e:
                logger.error(f"Error occurred during playback: {e}")
            if next_song['type'] == 'file':
                try:
                    os.remove(next_song['path'])
                except Exception as err:
                    logger.error(f"Error deleting file: {err}")
            # Proceed to play the next song
            asyncio.run_coroutine_threadsafe(play_next_song(voice_client), voice_client.loop)

        voice_client.play(player, after=after_playing)
    else:
        await voice_client.disconnect()
        song_queue.clear()
        logger.info("Queue is empty. Disconnected from voice channel.")
