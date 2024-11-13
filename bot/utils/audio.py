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
disconnect_timer = None  # Variable to hold the disconnect timer task

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
    global current_song, disconnect_timer
    if song_queue:
        # Cancel any existing disconnect timer since we're about to play a song
        if disconnect_timer and not disconnect_timer.cancelled():
            disconnect_timer.cancel()
            disconnect_timer = None

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

            # Set up to play the next song or wait for new songs
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
            logger.info("Queue is empty. Cleaning up audio files and waiting for 5 minutes before disconnecting.")

            # Clean up audio files
            await cleanup_audio_files()

            # Start a disconnect timer
            disconnect_timer = asyncio.create_task(wait_and_disconnect(voice_client))

async def wait_and_disconnect(voice_client):
    global disconnect_timer
    try:
        await asyncio.sleep(300)  # Wait for 5 minutes
        if not voice_client.is_playing() and not song_queue:
            await voice_client.disconnect()
            logger.info("No songs played for 5 minutes. Disconnected from voice channel.")
    except asyncio.CancelledError:
        logger.info("Disconnect timer cancelled. A new song was added or playback resumed.")
    finally:
        disconnect_timer = None

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
    global song_queue, current_song, disconnect_timer
    # Clear the queue and set current song to None
    song_queue.clear()
    current_song = None

    # Cancel the disconnect timer if it's running
    if disconnect_timer and not disconnect_timer.cancelled():
        disconnect_timer.cancel()
        disconnect_timer = None

    # Stop playback and disconnect the bot
    if voice_client.is_playing():
        voice_client.stop()
    await voice_client.disconnect()

    # Delete all audio files when playback stops
    await cleanup_audio_files()
    logger.info("Stopped playback and cleaned up audio files.")
