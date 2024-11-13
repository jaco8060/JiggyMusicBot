# bot/views/video_selection_view.py

import discord
from discord.ui import Button, View
import asyncio
import logging
from bot.utils.youtube import YTDLSource
from bot.utils.audio import song_queue, play_next_song, repeat_mode, original_queue  # Remove direct import of disconnect_timer
from bot.utils import audio  # Import the audio module
logger = logging.getLogger(__name__)

class VideoSelectionView(View):
    def __init__(self, videos, interaction, voice_client, bot):
        super().__init__(timeout=120)
        self.videos = videos
        self.interaction = interaction
        self.voice_client = voice_client
        self.bot = bot
        for idx, video in enumerate(videos[:5]):
            button = Button(label=f"#{idx+1}", custom_id=str(idx))
            button.callback = self.create_callback(idx)
            self.add_item(button)

    def create_callback(self, idx):
        async def callback(interaction):
            # Disable all buttons as soon as the user presses one
            for child in self.children:
                child.disabled = True
            await interaction.response.defer()  # Defer the response to avoid timeout
            await interaction.edit_original_response(view=self)  # Update the message with disabled buttons

            try:
                video = self.videos[idx]
                logger.info(f"Button pressed for video: {video['title']} ({video['url']})")

                # Cancel the disconnect timer if it's running
                if audio.disconnect_timer and not audio.disconnect_timer.cancelled():
                    audio.disconnect_timer.cancel()
                    audio.disconnect_timer = None

                # Add the selected video to the song queue
                song = {
                    'url': video['url'],
                    'title': video['title'],
                    'type': 'url'
                }
                song_queue.append(song)

                # Update original_queue if repeat_mode is on
                if repeat_mode:
                    if not original_queue:
                        # Include the currently playing song if any
                        if audio.current_song is not None:
                            original_queue.append(audio.current_song)
                    original_queue.append(song)

                logger.info(f"Added {video['title']} to the queue. Current queue: {[song['title'] for song in song_queue]}")

                # Trigger playback if not currently playing
                if not self.voice_client.is_playing():
                    await play_next_song(self.voice_client)
                    await interaction.followup.send(
                        f"Added **{video['title']}** to the queue and started playing!"
                    )
                else:
                    await interaction.followup.send(
                        f"Added **{video['title']}** to the queue. Currently playing another song."
                    )
            except Exception as e:
                logger.error(f"Error in button callback: {e}")
                await interaction.followup.send(f"An error occurred: {str(e)}")

        return callback

    async def on_timeout(self):
        # When the view times out, disable all buttons
        for child in self.children:
            child.disabled = True
        await self.interaction.edit_original_response(view=self)
