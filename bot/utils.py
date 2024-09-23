import os
import discord

AUDIO_FOLDER = "data/audio_files"
FFMPEG_PATH = "/usr/bin/ffmpeg" if os.name != 'nt' else "./data/ffmpeg.exe"

# Function to check if Opus is loaded
def load_opus():
    if not discord.opus.is_loaded():
        try:
            opus_path = '/usr/lib/libopus.so.0'
            discord.opus.load_opus(opus_path)
            print(f"Loaded Opus from {opus_path}")
        except Exception as e:
            print(f"Failed to load Opus: {e}")

# Ensure the audio folder exists
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

# Function to clean up the folder at startup
def cleanup_audio_folder():
    for file_name in os.listdir(AUDIO_FOLDER):
        file_path = os.path.join(AUDIO_FOLDER, file_name)
        try:
            if file_name != '.gitkeep' and os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

# Clean up audio folder at the start
cleanup_audio_folder()
