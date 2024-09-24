# bot/main.py
import os
from dotenv import load_dotenv
from bot.bot import bot  # Import the bot instance

# Load environment variables from the .env file
load_dotenv()

# Run the bot using the token from the .env file
token = os.getenv('DISCORD_BOT_TOKEN')
if token is None:
    raise ValueError(
        "No Discord bot token found. Please set the DISCORD_BOT_TOKEN environment variable."
    )

bot.run(token)
