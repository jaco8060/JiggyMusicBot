# bot/views/video_selection_view.py
import discord
from discord.ui import Button, View
import asyncio
import logging
from bot.utils.youtube import YTDLSource
from bot.utils.audio import song_queue, play_next_song

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

                # Convert the selected video URL into a playable URL
                song = await YTDLSource.from_url(video['url'], loop=self.bot.loop, download=False, max_retries=3, retry_delay=5)

                # Ensure the song is a valid YTDLSource object
                if isinstance(song, str) and song.startswith("Error"):
                    await interaction.followup.send(f"Error processing the video: {song}")
                    return

                # Add the selected video to the song queue
                song_url = song.data.get('url', song.data.get('webpage_url', None))
                if song_url:
                    song_queue.append({'url': song_url, 'title': song.title, 'type': 'url'})
                    logger.info(f"Added {song.title} to the queue. Current queue: {[song['title'] for song in song_queue]}")

                    # Trigger playback if not currently playing
                    if not self.voice_client.is_playing():
                        await play_next_song(self.voice_client)
                        await interaction.followup.send(
                            f"Added **{song.title}** to the queue and started playing!"
                        )
                    else:
                        await interaction.followup.send(
                            f"Added **{song.title}** to the queue. Currently playing another song."
                        )
                else:
                    await interaction.followup.send(f"Error: Could not retrieve a playable URL for the video.")
            except Exception as e:
                logger.error(f"Error in button callback: {e}")
                await interaction.followup.send(f"An error occurred: {str(e)}")

        return callback

    async def on_timeout(self):
        # When the view times out, disable all buttons
        for child in self.children:
            child.disabled = True
        await self.interaction.edit_original_response(view=self)
