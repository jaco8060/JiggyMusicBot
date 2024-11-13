# bot/commands/music_commands.py
import os 
import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.youtube import YTDLSource, search_youtube
from bot.utils.audio import (
    play_next_song,
    song_queue,
    files_to_delete,
)
from bot.views.video_selection_view import VideoSelectionView
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
                    song_queue.append({
                        "url": video_url,
                        "title": entry.get('title', 'Unknown title'),
                        "type": "url"
                    })
                await interaction.followup.send(
                    f"Added {len(entries)} songs to the queue from the playlist!"
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
                song_queue.append({
                    "url": video_url,
                    "title": data.get('title', 'Unknown title'),
                    "type": "url"
                })
                await interaction.followup.send(
                    f"Added **{data.get('title', 'Unknown title')}** to the queue."
                )

            if not voice_client.is_playing():
                await play_next_song(voice_client)
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

            # Save the audio file locally in the folder
            audio_file_path = os.path.join("audio_files", audio_file.filename)
            await audio_file.save(audio_file_path)

            # Delete the Discord message that contained the uploaded file
            await message.delete()

            # Add the audio file to the queue with the correct format
            song_queue.append(
                {
                    "type": "file",
                    "title": audio_file.filename,
                    "path": audio_file_path,
                }
            )

            # Connect to the voice channel
            voice_client = interaction.guild.voice_client
            if not voice_client:
                voice_client = await interaction.user.voice.channel.connect()

            # Start playing if nothing is currently playing
            if not voice_client.is_playing():
                await play_next_song(voice_client)
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

        # If there are files to delete, delete the first one
        if files_to_delete:
            file_to_delete = files_to_delete.pop(0)
            try:
                os.remove(file_to_delete)
                logger.info(f"Deleted file: {file_to_delete}")
            except FileNotFoundError:
                logger.warning(f"File not found, could not delete: {file_to_delete}")
            except Exception as e:
                logger.error(f"Error deleting file {file_to_delete}: {e}")

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

            # Clear the song queue and file deletion list
            song_queue.clear()
            files_to_delete.clear()

            # Trigger garbage collection
            import gc

            gc.collect()
            logger.info("Playback stopped, bot disconnected, and cleanup complete.")
        else:
            logger.warning(
                f"Stop command received, but bot is not connected to a voice channel. Command issued by {interaction.user}."
            )
            await interaction.response.send_message(
                "I'm not connected to a voice channel.", ephemeral=True
            )

    @app_commands.command(name="queue", description="List the current song queue")
    async def queue(self, interaction: discord.Interaction):
        if len(song_queue) == 0:
            logger.info(
                f"Queue command issued by {interaction.user}, but the queue is currently empty."
            )
            await interaction.response.send_message(
                "The queue is currently empty.", ephemeral=True
            )
        else:
            queue_list = "\n".join(
                [f"{idx + 1}. {song['title']}" for idx, song in enumerate(song_queue)]
            )
            logger.info(
                f"Queue command issued by {interaction.user}. Current queue:\n{queue_list}"
            )
            await interaction.response.send_message(
                f"Current song queue:\n\n{queue_list}"
            )
