from discord.ext import commands
from bot.music import YTDLSource, song_queue, play_next_song, fetch_playback_url
from bot.views import VideoSelectionView
import discord
import logging

logger = logging.getLogger(__name__)

class PlayCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="play", description="Play a YouTube or SoundCloud link or search for a video/track")
    async def play(self, ctx, *, prompt: str):
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel.", ephemeral=True)
            return

        logger.info(f"Received play command with prompt: {prompt}")  # Log the prompt received
        await ctx.defer()

        voice_client = ctx.guild.voice_client or await ctx.author.voice.channel.connect()

        # Check if the prompt is a URL
        if prompt.startswith("http"):
            # Handle as a direct URL
            url = prompt
            songs = await YTDLSource.from_url(url, loop=self.bot.loop, download=False, max_retries=3, retry_delay=5)

            # If songs is a list, it's a playlist
            if isinstance(songs, list):
                for song in songs:
                    song_url = song.data.get('url', song.data.get('webpage_url', None))
                    if song_url:
                        song_queue.append({'url': song_url, 'title': song.title, 'type': 'url'})
                        logger.info(f"Added song to queue: {song.title}")
                    else:
                        logger.warning(f"Skipping song with missing URL: {song.title}")
                await ctx.followup.send(f'Added {len(songs)} songs to the queue from the playlist!')

            # If songs is a string starting with "Error", it's an error message
            elif isinstance(songs, str) and songs.startswith("Error"):
                logger.error(f"Error while fetching song: {songs}")
                await ctx.followup.send(songs)

            # Otherwise, it's a single track
            else:
                song_url = songs.data.get('url', songs.data.get('webpage_url', None))
                if song_url:
                    song_queue.append({'url': song_url, 'title': songs.title, 'type': 'url'})
                    logger.info(f"Added single song to queue: {songs.title}")
                    await ctx.followup.send(f'Added **{songs.title}** to the queue.')
                else:
                    logger.warning(f"Skipping song with missing URL: {songs.title}")
                    await ctx.followup.send(f"Error: Could not retrieve URL for the song {songs.title}.")

            if not voice_client.is_playing():
                await play_next_song(voice_client)
        
        # If the prompt is not a URL, treat it as a search query
        else:
            logger.info(f"Searching YouTube for query: {prompt}")
            videos = await search_youtube(prompt)
            if not videos:
                logger.warning(f"No videos found for query: {prompt}")
                await ctx.followup.send("No videos found.", ephemeral=True)
                return
            
            # Use VideoSelectionView to show the top 5 results for user selection
            view = VideoSelectionView(videos, ctx, voice_client)
            description = "\n".join([
                f"**(#{idx+1})** - {video['title']}"
                for idx, video in enumerate(videos[:5])
            ])
            
            await ctx.followup.send(
                f"Top 5 results for **{prompt}**:\n\n{description}", view=view)

async def setup(bot):
    await bot.add_cog(PlayCommand(bot))
