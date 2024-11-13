# bot/bot.py

import discord
from discord.ext import commands
from bot.utils.config import load_opus, setup_logging
from bot.commands.music_commands import MusicCommands
from bot.commands.admin_commands import AdminCommands  # If you have admin commands

# Setup logging
logger = setup_logging()

# Load Opus before initializing the bot
load_opus()

# Enable necessary intents to match the Developer Portal settings
intents = discord.Intents.default()
intents.members = True
intents.presences = False
intents.message_content = True

# Initialize the bot with the correct intents
bot = commands.Bot(command_prefix='/', intents=intents)

# Sync slash commands when the bot is ready
@bot.event
async def on_ready():
    await bot.add_cog(MusicCommands(bot))
    await bot.add_cog(AdminCommands(bot))  # For potential extension
    await bot.tree.sync()
    print(f"Logged in as {bot.user} and ready!")
