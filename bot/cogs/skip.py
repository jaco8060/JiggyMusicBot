from discord.ext import commands
from bot.music import song_queue, play_next_song
import discord
import os
import logging

logger = logging.getLogger(__name__)

class SkipCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="skip", description="Skip the current song and play the next one in the queue")
    async def skip(self, ctx):
        voice_client = ctx.guild.voice_client

        if not voice_client or not voice_client.is_playing():
            await ctx.send("No song is currently playing.", ephemeral=True)
            return

        # Stop the current song, which will trigger the after function to play the next song
        voice_client.stop()

        # If there are files to delete, delete the first one
        if song_queue and 'path' in song_queue[0]:
            file_to_delete = song_queue[0]['path']
            try:
                os.remove(file_to_delete)
                logger.info(f"Deleted file: {file_to_delete}")
            except FileNotFoundError:
                logger.warning(f"File not found, could not delete: {file_to_delete}")
            except Exception as e:
                logger.error(f"Error deleting file {file_to_delete}: {e}")

        await ctx.send("Skipped the current song. Playing the next song in the queue.")

async def setup(bot):
    await bot.add_cog(SkipCommand(bot))