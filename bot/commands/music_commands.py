# bot/commands/music_commands.py
import os
import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.youtube import YTDLSource, search_youtube
from bot.utils import audio  # Import the audio module
from bot.views.video_selection_view import VideoSelectionView
from bot.views.pagination_view import QueuePaginationView
import asyncio
import logging
logger = logging.getLogger(__name__)

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="play",
        description="Play a YouTube or SoundCloud link or search for a video/track",
    )
    async def play(self, interaction: discord.Interaction, prompt: str):
        if not interaction.user.voice:
            await interaction.response.send_message(
                "You need to be in a voice channel.", ephemeral=True
            )
            return

        logger.info(f"Received play command with prompt: {prompt}")
        await interaction.response.defer()

        voice_client = interaction.guild.voice_client
        if not voice_client or not voice_client.is_connected():
            voice_client = await interaction.user.voice.channel.connect()

        # Cancel the disconnect timer if it's running
        if audio.disconnect_timer and not audio.disconnect_timer.cancelled():
            audio.disconnect_timer.cancel()
            audio.disconnect_timer = None

        # List to keep track of songs added during this command
        songs_added_to_queue = []

        # Check if the prompt is a URL
        if prompt.startswith("http"):
            # Fetch minimal info without processing formats
            data = await YTDLSource.from_url(
                prompt, loop=self.bot.loop, download=False, process=False
            )

            if data is None:
                await interaction.followup.send("Error retrieving information from the URL.")
                return

            if 'entries' in data:  # Playlist
                # Convert the generator to a list
                entries = list(data['entries'])
                for entry in entries:
                    # Handle missing 'webpage_url'
                    video_url = entry.get('webpage_url')
                    if not video_url:
                        video_id = entry.get('id')
                        if video_id:
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                        else:
                            logger.warning(f"Skipping song with missing URL: {entry.get('title', 'Unknown title')}")
                            continue
                    song = {
                        "url": video_url,
                        "title": entry.get('title', 'Unknown title'),
                        "type": "url"
                    }
                    audio.song_queue.append(song)
                    songs_added_to_queue.append(song)
                await interaction.followup.send(
                    f"Added {len(songs_added_to_queue)} songs to the queue from the playlist!"
                )
            else:  # Single track
                # Handle missing 'webpage_url'
                video_url = data.get('webpage_url')
                if not video_url:
                    video_id = data.get('id')
                    if video_id:
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                    else:
                        await interaction.followup.send("Could not retrieve video URL.")
                        return
                song = {
                    "url": video_url,
                    "title": data.get('title', 'Unknown title'),
                    "type": "url"
                }
                audio.song_queue.append(song)
                songs_added_to_queue.append(song)
                await interaction.followup.send(
                    f"Added **{data.get('title', 'Unknown title')}** to the queue."
                )
        else:
            logger.info(f"Searching YouTube for query: {prompt}")
            videos = await search_youtube(prompt)
            if not videos:
                logger.warning(f"No videos found for query: {prompt}")
                await interaction.followup.send("No videos found.", ephemeral=True)
                return

            # Use VideoSelectionView to show the top 5 results for user selection
            view = VideoSelectionView(videos, interaction, voice_client, self.bot)
            description = "\n".join(
                [f"**(#{idx+1})** - {video['title']}" for idx, video in enumerate(videos[:5])]
            )

            await interaction.followup.send(
                f"Top 5 results for **{prompt}**:\n\n{description}", view=view
            )
            return  # Exit the function since selection is handled by the view

        # After adding songs to song_queue, update original_queue if repeat_mode is on
        if audio.repeat_mode:
            if not audio.original_queue:
                # Include the currently playing song if any
                if audio.current_song is not None:
                    audio.original_queue.append(audio.current_song)
            audio.original_queue.extend(songs_added_to_queue)

        if not voice_client.is_playing():
            await audio.play_next_song(voice_client)
 
    @app_commands.command(name="upload_play", description="Play an uploaded audio file")
    async def upload_play(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message(
                f"{interaction.user.mention}, you need to be in a voice channel to use this command.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "Now upload an audio file to play in the voice channel:", ephemeral=True
        )

        def check(message):
            return (
                message.author == interaction.user
                and message.attachments
                and any(
                    message.attachments[0].filename.endswith(ext)
                    for ext in [".mp3", ".wav", ".m4a"]
                )
            )

        try:
            message = await self.bot.wait_for("message", check=check, timeout=60.0)
            audio_file = message.attachments[0]

            # Ensure the audio_files directory exists
            audio_folder = "audio_files"
            if not os.path.exists(audio_folder):
                os.makedirs(audio_folder)

            # Save the audio file locally in the folder
            audio_file_path = os.path.join(audio_folder, audio_file.filename)
            await audio_file.save(audio_file_path)

            # Delete the Discord message that contained the uploaded file
            await message.delete()

            # Cancel the disconnect timer if it's running
            if audio.disconnect_timer and not audio.disconnect_timer.cancelled():
                audio.disconnect_timer.cancel()
                audio.disconnect_timer = None

            # Add the audio file to the queue with the correct format
            song = {
                "type": "file",
                "title": audio_file.filename,
                "path": audio_file_path,
            }
            audio.song_queue.append(song)

            # Update original_queue if repeat_mode is on
            if audio.repeat_mode:
                if not audio.original_queue:
                    # Include the currently playing song if any
                    if audio.current_song is not None:
                        audio.original_queue.append(audio.current_song)
                audio.original_queue.append(song)

            # Connect to the voice channel
            voice_client = interaction.guild.voice_client
            if not voice_client or not voice_client.is_connected():
                voice_client = await interaction.user.voice.channel.connect()

            # Start playing if nothing is currently playing
            if not voice_client.is_playing():
                await audio.play_next_song(voice_client)
                await interaction.followup.send(
                    f"Added **{audio_file.filename}** to the queue and started playing!"
                )
            else:
                await interaction.followup.send(
                    f"Added **{audio_file.filename}** to the queue."
                )
            # Delete the original interaction message after responding
            await interaction.delete_original_response()
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "You took too long to upload an audio file.", ephemeral=True
            )


    @app_commands.command(
        name="skip",
        description="Skip the current song and play the next one in the queue",
    )
    async def skip(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client

        if not voice_client or not voice_client.is_playing():
            await interaction.response.send_message(
                "No song is currently playing.", ephemeral=True
            )
            return

        # Stop the current song, which will trigger the after function to play the next song
        voice_client.stop()

        # Delete the currently playing file if it's a local file
        current_source = voice_client.source
        if isinstance(current_source, discord.PCMVolumeTransformer):
            original_source = current_source.original
            if isinstance(original_source, discord.FFmpegPCMAudio):
                source_path = original_source.source
                if os.path.exists(source_path) and source_path.startswith("audio_files"):
                    try:
                        os.remove(source_path)
                        logger.info(f"Deleted file: {source_path}")
                    except Exception as e:
                        logger.error(f"Error deleting file {source_path}: {e}")

        await interaction.response.send_message(
            "Skipped the current song. Playing the next song in the queue."
        )
        
    @app_commands.command(name="stop", description="Stop the audio and disconnect the bot")
    async def stop(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client

        if voice_client and voice_client.is_connected():
            logger.info(
                f"Received stop command from {interaction.user}. Stopping playback and disconnecting the bot."
            )
            await interaction.response.send_message(
                "Stopping playback and disconnecting the bot."
            )

            # Stop playback and disconnect the bot after stopping
            voice_client.stop()
            await voice_client.disconnect()

            # Clear the song queue and reset variables
            audio.song_queue.clear()
            audio.original_queue.clear()
            audio.repeat_mode = False
            audio.current_song = None

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
        else:
            await interaction.response.send_message(
                "The bot is not connected to a voice channel.", ephemeral=True
            )

    @app_commands.command(name="queue", description="List the current song queue")
    async def queue(self, interaction: discord.Interaction):
        if audio.current_song is None and len(audio.song_queue) == 0:
            logger.info(
                f"Queue command issued by {interaction.user}, but no songs are currently playing or queued."
            )
            await interaction.response.send_message(
                "There are no songs currently playing or queued.", ephemeral=True
            )
        else:
            logger.info(
                f"Queue command issued by {interaction.user}."
            )
            view = QueuePaginationView(audio.song_queue.copy(), interaction, current_song=audio.current_song)
            await interaction.response.defer()
            await view.send_initial_message()

    @app_commands.command(name="repeat", description="Toggle repeat mode on or off")
    @app_commands.describe(mode="Choose 'on' or 'off'")
    async def repeat(self, interaction: discord.Interaction, mode: str):
        mode = mode.lower()
        if mode == 'on':
            if not audio.repeat_mode:
                audio.repeat_mode = True
                # Store the current song and queue
                audio.original_queue.clear()
                # Include the currently playing song
                if audio.current_song is not None:
                    audio.original_queue.append(audio.current_song)
                # Include the rest of the queue
                audio.original_queue.extend(audio.song_queue)
                await interaction.response.send_message("Repeat mode is now **ON**.")
            else:
                await interaction.response.send_message("Repeat mode is already **ON**.", ephemeral=True)
        elif mode == 'off':
            if audio.repeat_mode:
                audio.repeat_mode = False
                audio.original_queue.clear()
                await interaction.response.send_message("Repeat mode is now **OFF**.")
            else:
                await interaction.response.send_message("Repeat mode is already **OFF**.", ephemeral=True)
        else:
            await interaction.response.send_message("Please specify 'on' or 'off'.", ephemeral=True)

