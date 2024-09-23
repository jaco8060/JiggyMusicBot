import discord
from discord.ext import commands
from bot import config, utils

# Enable necessary intents to match the Developer Portal settings
intents = discord.Intents.default()
intents.members = True
intents.presences = False
intents.message_content = True

# Initialize the bot with the correct intents
bot = commands.Bot(command_prefix='/', intents=intents)

# Asynchronous setup to load extensions
async def load_extensions():
    await bot.load_extension('bot.cogs.play')
    await bot.load_extension('bot.cogs.skip')
    await bot.load_extension('bot.cogs.stop')
    await bot.load_extension('bot.cogs.queue')

# Sync slash commands when the bot is ready
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user} and ready!")

# Start the bot and load extensions
async def main():
    async with bot:
        await load_extensions()
        await bot.start(config.TOKEN)

# Run the asynchronous main function
import asyncio
asyncio.run(main())
