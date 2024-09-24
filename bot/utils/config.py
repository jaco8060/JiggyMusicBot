# bot/utils/config.py
import discord
import logging
import os

def load_opus():
    if not discord.opus.is_loaded():
        try:
            opus_path = '/usr/lib/libopus.so.0'
            discord.opus.load_opus(opus_path)
            print(f"Loaded Opus from {opus_path}")
        except Exception as e:
            print(f"Failed to load Opus: {e}")

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    return logger

# Ensure the audio_files directory exists
def ensure_audio_folder():
    audio_folder = "audio_files"
    if not os.path.exists(audio_folder):
        os.makedirs(audio_folder)

    # Function to clean up the folder at startup
    for file_name in os.listdir(audio_folder):
        file_path = os.path.join(audio_folder, file_name)
        try:
            if file_name != '.gitkeep' and os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
