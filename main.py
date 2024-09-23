import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import os
import asyncio
import requests
from discord import app_commands
from dotenv import load_dotenv
from discord.ui import Button, View
import html  # Import the html module for unescaping
import discord.opus
import gc
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Load environment variables from the .env file
load_dotenv()

# Function to check if Opus is loaded
def load_opus():
    if not discord.opus.is_loaded():
        # Manually load the Opus library from the expected location
        try:
            opus_path = '/usr/lib/libopus.so.0'
            discord.opus.load_opus(opus_path)
            print(f"Loaded Opus from {opus_path}")
        except Exception as e:
            print(f"Failed to load Opus: {e}")

# Load Opus before initializing the bot
load_opus()


# Enable necessary intents to match the Developer Portal settings
intents = discord.Intents.default()
intents.members = True
intents.presences = False
intents.message_content = True

# Initialize the bot with the correct intents
bot = commands.Bot(command_prefix='/', intents=intents)

# Use the existing command tree of the bot
tree = bot.tree

# Folder to store audio files
AUDIO_FOLDER = "audio_files"

# Ensure the audio folder exists
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)


# Function to clean up the folder at startup
def cleanup_audio_folder():
    for file_name in os.listdir(AUDIO_FOLDER):
        file_path = os.path.join(AUDIO_FOLDER, file_name)
        try:
            # Skip the .gitkeep file
            if file_name != '.gitkeep' and os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")


# Clean up audio folder at the start
cleanup_audio_folder()

# Global song queue
song_queue = []

# List to track files that need to be deleted after playing or skipping
files_to_delete = []

# Detect ffmpeg path depending on the environment
if os.name == 'nt':  # Windows
    ffmpeg_path = "./ffmpeg.exe"  # Assuming ffmpeg.exe is in the project root
else:  # Unix/Linux including Raspberry Pi
    ffmpeg_path = "/usr/bin/ffmpeg"  # Default path for ffmpeg in Docker

# yt-dlp options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': f'{AUDIO_FOLDER}/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'http_headers': {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.3',
    'retries': 3  # Number of retries in case of errors
}

}

ffmpeg_options = {
    'before_options':
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


# Define YTDLSource class to handle audio playback from YouTube
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, download=False, max_retries=3, retry_delay=5):
        loop = loop or asyncio.get_event_loop()
        attempts = 0
        last_exception = None
        
        while attempts < max_retries:
            try:
                data = await loop.run_in_executor(
                    None, lambda: ytdl.extract_info(url, download=download, process=True)
                )
                
                # Check if it's a playlist or a single track
                if 'entries' in data:  # Playlist
                    return [
                        cls(discord.FFmpegPCMAudio(executable=ffmpeg_path, source=entry['url'], **ffmpeg_options), data=entry)
                        for entry in data['entries']
                    ]
                else:  # Single track
                    return cls(discord.FFmpegPCMAudio(executable=ffmpeg_path, source=data['url'], **ffmpeg_options), data=data)
                
            except youtube_dl.utils.DownloadError as e:
                last_exception = e
                print(f"DownloadError: {e}. Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                attempts += 1
            
            except Exception as e:
                last_exception = e
                print(f"Unexpected error: {e}. Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                attempts += 1
        
        print(f"Failed to download after {max_retries} attempts. Last exception: {last_exception}")
        return f"Error: {str(last_exception)}"  # Return the error message after max retries


# Search using YouTube Data API
async def youtube_api_search(query):
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': 5,
        'key': os.getenv("YOUTUBE_API_KEY")
    }
    try:
        response = requests.get("https://www.googleapis.com/youtube/v3/search",
                                params=params)
        response.raise_for_status()
        data = response.json()
        videos = [
            {
                'url':
                f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                'title': html.unescape(
                    item['snippet']['title'])  # Unescape HTML entities
            } for item in data['items']
        ]
        return videos
    except requests.exceptions.RequestException as e:
        print(f"API error: {e}")
        return None


# Fallback to yt-dlp search
async def yt_dlp_search(query):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(
        None, lambda: ytdl.extract_info(f"ytsearch5:{query}", download=False))
    return [{
        'url': entry['webpage_url'],
        'title': entry['title']
    } for entry in data.get('entries', [])]


# Check API usage and fallback to yt-dlp if limit is hit
async def search_youtube(query):
    videos = await youtube_api_search(query)
    if not videos:
        print("YouTube API failed, falling back to yt-dlp.")
        videos = await yt_dlp_search(query)
    return videos

# Fetch the playback URL just before playing the song
async def fetch_playback_url(song):
    """
    Fetches the playback URL for a given song.
    The song should have a 'type' (e.g., 'url', 'query') and relevant details.
    """
    if song['type'] == 'url':
        # If the song already has a URL, return it
        return song['url']
    elif song['type'] == 'query':
        # If it's a query, search for the URL using the YouTube API or yt-dlp
        videos = await search_youtube(song['query'])
        if videos:
            return videos[0]['url']  # Return the first video result
    return None  # Return None if no URL can be found

# Function to play the next song in the queue
async def play_next_song(voice_client):
    if song_queue:
        next_song = song_queue.pop(0)

        # Fetch the playback URL just before playing
        playback_url = await fetch_playback_url(next_song)

        if not playback_url:
            logger.warning(f"Could not fetch URL for song: {next_song}")
            await play_next_song(voice_client)  # Skip to the next song
            return

        # Log the URL of the song to be played
        logger.info(f"Now playing URL: {playback_url}")

        # Create the audio player using the fetched playback URL
        player = discord.FFmpegPCMAudio(executable=ffmpeg_path, source=playback_url, **ffmpeg_options)

        def after_playing(e):
            if e:
                logger.error(f"Error occurred during playback: {e}")  # Log any error that occurs during playback
            if next_song['type'] == 'file':
                try:
                    os.remove(next_song['path'])
                except Exception as err:
                    logger.error(f"Error deleting file: {err}")  # Log error if file deletion fails
            # Proceed to play the next song
            asyncio.run_coroutine_threadsafe(play_next_song(voice_client), bot.loop)

        voice_client.play(player, after=after_playing)
    else:
        await voice_client.disconnect()
        song_queue.clear()
        logger.info("Queue is empty. Disconnected from voice channel.")  # Log when queue

        
# Class for video selection
class VideoSelectionView(View):

    def __init__(self, videos, interaction, voice_client):
        super().__init__(timeout=120)
        self.videos = videos
        self.interaction = interaction
        self.voice_client = voice_client
        for idx, video in enumerate(videos[:5]):
            button = Button(label=f"#{idx+1}", custom_id=str(idx))
            button.callback = self.create_callback(idx)
            self.add_item(button)

    def create_callback(self, idx):

        async def callback(interaction):
            # Disable all buttons as soon as the user presses one
            for child in self.children:
                child.disabled = True
            await interaction.response.defer(
            )  # Defer the response to avoid timeout
            await interaction.edit_original_response(
                view=self)  # Update the message with disabled buttons

            try:
                video = self.videos[idx]
                song_queue.append({
                    'url': video['url'],
                    'title': video['title'],
                    'type': 'url'
                })
                if not self.voice_client.is_playing():
                    await play_next_song(self.voice_client)
                    await interaction.followup.send(
                        f"Added **{video['title']}** to the queue and started playing!"
                    )
                else:
                    await interaction.followup.send(
                        f"Added **{video['title']}** to the queue.")
            except Exception as e:
                # Handle any potential errors here and re-enable buttons if necessary
                await interaction.followup.send(f"An error occurred: {str(e)}")

        return callback

    async def on_timeout(self):
        # When the view times out, disable all buttons
        for child in self.children:
            child.disabled = True
        await self.interaction.edit_original_response(view=self)


@tree.command(name="play", description="Play a YouTube or SoundCloud link or search for a video/track")
async def play(interaction, prompt: str):
    if not interaction.user.voice:
        await interaction.response.send_message(
            "You need to be in a voice channel.", ephemeral=True)
        return

    logger.info(f"Received play command with prompt: {prompt}")  # Log the prompt received
    await interaction.response.defer()

    voice_client = interaction.guild.voice_client or await interaction.user.voice.channel.connect()

    # Check if the prompt is a URL
    if prompt.startswith("http"):
        songs = await YTDLSource.from_url(prompt, loop=bot.loop, download=False, max_retries=3, retry_delay=5)
        
        # If songs is a list, it's a playlist
        if isinstance(songs, list):
            for song in songs:
                song_queue.append({'video_id': song.data.get('id'), 'title': song.title, 'type': 'url'})
                logger.info(f"Added song to queue: {song.title}")
            await interaction.followup.send(f'Added {len(songs)} songs to the queue from the playlist!')
        
        # If songs is a string starting with "Error", it's an error message
        elif isinstance(songs, str) and songs.startswith("Error"):
            logger.error(f"Error while fetching song: {songs}")
            await interaction.followup.send(songs)
        
        # Otherwise, it's a single track
        else:
            song_queue.append({'video_id': songs.data.get('id'), 'title': songs.title, 'type': 'url'})
            logger.info(f"Added single song to queue: {songs.title}")
            await interaction.followup.send(f'Added **{songs.title}** to the queue.')

        if not voice_client.is_playing():
            await play_next_song(voice_client)
    
    # If the prompt is not a URL, treat it as a search query
    else:
        logger.info(f"Searching YouTube for query: {prompt}")
        videos = await search_youtube(prompt)
        if not videos:
            logger.warning(f"No videos found for query: {prompt}")
            await interaction.followup.send("No videos found.", ephemeral=True)
            return
        
        view = VideoSelectionView(videos, interaction, voice_client)
        description = "\n".join([
            f"**(#{idx+1})** - {video['title']}"
            for idx, video in enumerate(videos[:5])
        ])
        
        await interaction.followup.send(
            f"Top 5 results for **{prompt}**:\n\n{description}", view=view)

# Play an uploaded audio file and add it to the queue
@tree.command(name="upload_play", description="Play an uploaded audio file")
async def upload_play(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message(
            f"{interaction.user.mention}, you need to be in a voice channel to use this command.",
            ephemeral=True)  # This makes the message visible only to the user
        return

    await interaction.response.send_message(
        "Now upload an audio file to play in voice channel:",
        ephemeral=True)  # Ephemeral message

    # Function to check if the message has an attachment that is an audio file
    def check(message):
        return message.author == interaction.user and message.attachments and any(
            message.attachments[0].filename.endswith(ext)
            for ext in ['.mp3', '.wav', '.m4a'])

    try:
        # Wait for the user to upload an audio file
        message = await bot.wait_for('message', check=check, timeout=60.0)
        audio_file = message.attachments[0]

        # Save the audio file locally in the folder
        audio_file_path = os.path.join(AUDIO_FOLDER, audio_file.filename)
        await audio_file.save(audio_file_path)

        # Delete the Discord message that contained the uploaded file
        await message.delete()

        # Add the audio file to the queue
        song_queue.append({
            'path': audio_file_path,
            'title': audio_file.filename,
            'type': 'file'
        })

        # Connect to the voice channel
        channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client
        if not voice_client:
            voice_client = await channel.connect()

        # Start playing if nothing is currently playing
        if not voice_client.is_playing():
            await play_next_song(voice_client)
            await interaction.followup.send(
                f"Added **{audio_file.filename}** to the queue and started playing!"
            )
        else:
            await interaction.followup.send(
                f"Added **{audio_file.filename}** to the queue.")

        # Delete the original interaction message after responding
        await interaction.delete_original_response()

    except asyncio.TimeoutError:
        await interaction.followup.send(
            "You took too long to upload an audio file.", ephemeral=True)


# Define a /skip command to skip the current song
@tree.command(
    name="skip",
    description="Skip the current song and play the next one in the queue")
async def skip(interaction: discord.Interaction):
    global files_to_delete
    voice_client = interaction.guild.voice_client

    if not voice_client or not voice_client.is_playing():
        await interaction.response.send_message(
            "No song is currently playing.", ephemeral=True)
        return

    # Stop the current song, which will trigger the after function to play the next song
    voice_client.stop()

    # If there are files to delete, delete the first one
    if files_to_delete:
        file_to_delete = files_to_delete.pop(0)
        try:
            os.remove(file_to_delete)
            print(f"Deleted file: {file_to_delete}")
        except Exception as e:
            print(f"Error deleting file {file_to_delete}: {e}")

    await interaction.response.send_message(
        "Skipped the current song. Playing the next song in the queue.")



# Define a /stop command to stop playback and disconnect the bot
@tree.command(name="stop", description="Stop the audio and disconnect the bot")
async def stop(interaction: discord.Interaction):
    global files_to_delete
    voice_client = interaction.guild.voice_client
    if voice_client:
        await interaction.response.send_message("Stopping playback and disconnecting the bot.")

        # Stop playback and disconnect the bot after stopping
        voice_client.stop() 
        # Disconnect the bot
        await voice_client.disconnect()
        # Now delete all remaining files in the deletion list after bot has disconnected
        while files_to_delete:
            file_to_delete = files_to_delete.pop(0)
            try:
                if os.path.exists(file_to_delete):
                    os.remove(file_to_delete)
                else:
                    print(f"File {file_to_delete} already deleted, skipping...")
            except Exception as e:
                print(f"Error deleting file {file_to_delete}: {e}")
        # Clear the song queue and file deletion list
        song_queue.clear()
        files_to_delete.clear()
        # Trigger garbage collection
        gc.collect()
    else:
        await interaction.response.send_message("I'm not connected to a voice channel.", ephemeral=True)

# Define a /queue command to list the current song queue
@tree.command(name="queue", description="List the current song queue")
async def queue(interaction: discord.Interaction):
    if len(song_queue) == 0:
        await interaction.response.send_message(
            "The queue is currently empty.", ephemeral=True)
    else:
        queue_list = "\n".join([
            f"{idx + 1}. {song['title']}"
            for idx, song in enumerate(song_queue)
        ])
        await interaction.response.send_message(
            f"Current song queue:\n\n{queue_list}")


# Sync slash commands when the bot is ready
@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user} and ready!")


# Run the bot using the token from the .env file
token = os.getenv('DISCORD_BOT_TOKEN')
if token is None:
    raise ValueError(
        "No Discord bot token found. Please set the DISCORD_BOT_TOKEN environment variable."
    )
bot.run(token)
