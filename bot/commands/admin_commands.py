# bot/commands/admin_commands.py
import discord
from discord.ext import commands

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Define admin commands here
    # Example:
    # @commands.command(name="shutdown")
    # @commands.is_owner()
    # async def shutdown(self, ctx):
    #     await ctx.bot.logout()

def setup(bot):
    bot.add_cog(AdminCommands(bot))
