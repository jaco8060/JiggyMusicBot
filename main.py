import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Enable necessary intents to match the Developer Portal settings
intents = discord.Intents.default()
intents.members = True  # You enabled "Server Members Intent" in the Developer Portal
intents.presences = False  # If "Presence Intent" is not needed, set it to False
intents.message_content = False  # This is disabled in your Developer Portal, so set to False

# Initialize the bot with the correct intents
bot = commands.Bot(command_prefix='/', intents=intents)

# Use the existing command tree of the bot
tree = bot.tree

# Options for yt-dlp
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=False))

        if 'entries' in data:
            # Take the first item from a playlist
            data = data['entries'][0]

        filename = data['url']
        return cls(discord.FFmpegPCMAudio(executable="ffmpeg",  # Assuming FFmpeg is globally available
                                          source=filename,
                                          **ffmpeg_options),
                   data=data)

# Define a /play command as a slash command
@tree.command(name="play", description="Play a YouTube link in the voice channel")
async def play(interaction: discord.Interaction, url: str):
    if not interaction.user.voice:
        await interaction.response.send_message(
            f"{interaction.user.mention}, you need to be in a voice channel to use this command.",
            ephemeral=True)
        return
    
    await interaction.response.defer()  # Defer the interaction in case the command takes time
    
    channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client

    # If the bot is not connected to a voice channel, connect
    if not voice_client:
        try:
            voice_client = await channel.connect()
        except Exception as e:
            await interaction.followup.send(f"Failed to connect to the voice channel: {e}")
            return

    async with interaction.channel.typing():
        try:
            player = await YTDLSource.from_url(url, loop=bot.loop)
            voice_client.play(player, after=lambda e: print(f"Player error: {e}") if e else None)
        except Exception as e:
            await interaction.followup.send(f"Error processing the request: {e}")
            return

    await interaction.followup.send(f'Now playing: {player.title}')

# Define a /stop command
@tree.command(name="stop", description="Stop the audio and disconnect the bot")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message(
            "Stopped playing and left the voice channel.")
    else:
        await interaction.response.send_message(
            "The bot is not connected to any voice channel.", ephemeral=True)

# Sync slash commands when the bot is ready
@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user} and ready!")

# Error handler for command errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send(f"Command failed: {error}")
    else:
        raise error

# Run the bot using the token from the .env file
token = os.getenv('DISCORD_BOT_TOKEN')
if token is None:
    raise ValueError(
        "No Discord bot token found. Please set the DISCORD_BOT_TOKEN environment variable."
    )
bot.run(token)
