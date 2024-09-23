from discord.ext import commands
from bot.music import song_queue
import discord
import os
import logging
import gc

logger = logging.getLogger(__name__)

class StopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stop", description="Stop the audio and disconnect the bot")
    async def stop(self, ctx):
        voice_client = ctx.guild.voice_client
        
        if voice_client:
            logger.info(f"Received stop command from {ctx.author}. Stopping playback and disconnecting the bot.")
            await ctx.send("Stopping playback and disconnecting the bot.")
            
            # Stop playback and disconnect the bot after stopping
            voice_client.stop()
            await voice_client.disconnect()

            # Now delete all remaining files in the deletion list after bot has disconnected
            while song_queue:
                file_to_delete = song_queue.pop(0).get('path')
                if file_to_delete:
                    try:
                        if os.path.exists(file_to_delete):
                            os.remove(file_to_delete)
                            logger.info(f"Deleted file: {file_to_delete}")
                        else:
                            logger.warning(f"File {file_to_delete} already deleted, skipping...")
                    except Exception as e:
                        logger.error(f"Error deleting file {file_to_delete}: {e}")
            
            # Clear the song queue
            song_queue.clear()
            
            # Trigger garbage collection
            gc.collect()
            logger.info("Playback stopped, bot disconnected, and cleanup complete.")
        else:
            logger.warning(f"Stop command received, but bot is not connected to a voice channel. Command issued by {ctx.author}.")
            await ctx.send("I'm not connected to a voice channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(StopCommand(bot))
