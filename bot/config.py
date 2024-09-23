import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# Check if tokens are missing
if not TOKEN:
    raise ValueError("No Discord bot token found. Please set the DISCORD_BOT_TOKEN environment variable.")
if not YOUTUBE_API_KEY:
    raise ValueError("No YouTube API key found. Please set the YOUTUBE_API_KEY environment variable.")
