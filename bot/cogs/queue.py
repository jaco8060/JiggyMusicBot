from discord.ext import commands
from bot.music import song_queue
import logging

logger = logging.getLogger(__name__)

class QueueCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="queue", description="List the current song queue")
    async def queue(self, ctx):
        if len(song_queue) == 0:
            logger.info(f"Queue command issued by {ctx.author}, but the queue is currently empty.")
            await ctx.send("The queue is currently empty.", ephemeral=True)
        else:
            queue_list = "\n".join([
                f"{idx + 1}. {song['title']}"
                for idx, song in enumerate(song_queue)
            ])
            logger.info(f"Queue command issued by {ctx.author}. Current queue:\n{queue_list}")
            await ctx.send(f"Current song queue:\n\n{queue_list}")

async def setup(bot):
    await bot.add_cog(QueueCommand(bot))
