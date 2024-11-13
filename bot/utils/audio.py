# bot/utils/audio.py

import discord
import os
import asyncio
import logging
from bot.utils.youtube import YTDLSource, search_youtube

logger = logging.getLogger(__name__)

song_queue = []
current_song = None
repeat_mode = False
original_queue = []

# Detect ffmpeg path depending on the environment
if os.name == 'nt':  # Windows
    ffmpeg_path = "./ffmpeg.exe"  # Assuming ffmpeg.exe is in the project root
else:  # Unix/Linux including Raspberry Pi
    ffmpeg_path = "/usr/bin/ffmpeg"  # Default path for ffmpeg in Docker

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# Fetch the playback URL just before playing the song
async def fetch_playback_url(song):
    """
    Fetches the playback URL for a given song.
    The song should have a 'type' (e.g., 'url', 'query', 'file') and relevant details.
    """
    if song['type'] == 'url':
        data = await YTDLSource.from_url(
            song['url'], loop=asyncio.get_event_loop(), download=False, process=True
        )
        if data is None:
            return None
        return data.data.get('url')
    elif song['type'] == 'query':
        videos = await search_youtube(song['query'])
        if videos:
            return videos[0]['url']
    elif song['type'] == 'file':
        return song['path']
    return None

# Function to play the next song in the queue
async def play_next_song(voice_client):
    global current_song
    if song_queue:
        next_song = song_queue.pop(0)
        current_song = next_song  # Set the current song

        # Validate song structure
        if 'url' not in next_song and 'query' not in next_song and 'path' not in next_song:
            logger.warning(f"Skipping invalid song entry: {next_song}")
            await play_next_song(voice_client)
            return

        # Fetch the playback URL or file path
        playback_url = await fetch_playback_url(next_song)

        if not playback_url:
            logger.warning(f"Could not fetch URL for song: {next_song}")
            await play_next_song(voice_client)
            return

        # Log the URL of the song to be played
        logger.info(f"Now playing: {next_song.get('title', 'Unknown title')}")

        # Create the audio player
        if next_song['type'] == 'file':
            player = discord.FFmpegPCMAudio(
                executable=ffmpeg_path, source=playback_url)
        else:
            player = discord.FFmpegPCMAudio(
                executable=ffmpeg_path, source=playback_url, **ffmpeg_options)

        def after_playing(e):
            if e:
                logger.error(f"Error occurred during playback: {e}")

            # Set up to play the next song or repeat if needed
            coro = play_next_song(voice_client)
            fut = asyncio.run_coroutine_threadsafe(coro, voice_client.loop)
            try:
                fut.result()
            except Exception as e:
                logger.error(f"Error in after_playing: {e}")

        # Start playback
        voice_client.play(player, after=after_playing)
    else:
        # If repeat mode is active, reset the queue to original_queue and continue playback
        if repeat_mode and original_queue:
            song_queue.extend(original_queue.copy())
            logger.info("Repeat mode is ON. Resetting song queue.")
            await play_next_song(voice_client)
        else:
            current_song = None  # No song is playing
            await voice_client.disconnect()
            song_queue.clear()
            logger.info("Queue is empty. Disconnected from voice channel.")

# Cleanup audio files
async def cleanup_audio_files():
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

# Custom stop function to clear queue and remove files
async def stop_playback(voice_client):
    # Clear the queue, set current song to None, and disconnect the bot
    song_queue.clear()
    global current_song
    current_song = None
    await voice_client.disconnect()

    # Delete all audio files when playback stops
    await cleanup_audio_files()
    logger.info("Stopped playback and cleaned up audio files.")
