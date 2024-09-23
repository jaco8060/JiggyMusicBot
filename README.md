# Jiggy Music Bot

This bot allows you to play music, upload audio files, and manage music queues in a Discord server. It supports YouTube links and direct audio file uploads. This project is designed to run on a Raspberry Pi Zero 2 W using DietPi as the operating system.

## Creating the Project

### Step 1: Set Up Your Raspberry Pi Zero 2 W with DietPi

1. Visit the official [DietPi Installation Guide](https://dietpi.com/docs/install/) and follow the instructions for Raspberry Pi Zero 2 W.
2. Download the appropriate DietPi image for Raspberry Pi Zero 2 W.
3. Flash the image to your microSD card using a tool like Etcher or Raspberry Pi Imager.
4. Insert the microSD card into your Raspberry Pi Zero 2 W and power it on.
5. Follow the initial setup process for DietPi, ensuring you connect to your network.

### Step 2: Install Docker on DietPi

1. After setting up DietPi, SSH into your Raspberry Pi Zero 2 W.
2. Visit the [DietPi Software Installation Tool guide](https://dietpi.com/docs/dietpi_tools/software_installation/) for detailed instructions on installing software packages.
3. To install Docker, use the following command in the DietPi-Software tool:
   ```
   Docker
   ```
   This will install Docker and all its dependencies.

4. After installation, reboot your Raspberry Pi:
   ```
   sudo reboot
   ```

### Step 3: Set Up the Project

1. Clone the repository or create a new directory for your project:
   ```
   git clone https://github.com/your-username/jiggy-music-bot.git
   cd jiggy-music-bot
   ```
2. Create a `Dockerfile` in the project directory:
   ```
   nano Dockerfile
   ```
3. Add the following content to the `Dockerfile`:
   ```dockerfile
   # Use the Alpine base image for a lightweight container
   FROM python:3.10-alpine

   # Install FFmpeg, Opus, and other necessary packages with no-cache for a smaller image size
   RUN apk add --no-cache ffmpeg opus

   # Install Poetry for dependency management
   RUN pip install --no-cache-dir poetry

   # Set the working directory in the container
   WORKDIR /app

   # Copy only the dependency files to the container to leverage Docker caching
   COPY pyproject.toml poetry.lock ./

   # Install project dependencies using Poetry
   RUN poetry config virtualenvs.create false && \
       poetry install --no-root --no-dev --no-interaction --no-ansi

   # Copy the rest of the application files
   COPY . .

   # Ensure the audio_files directory exists
   RUN mkdir -p audio_files

   # Command to run the bot
   CMD ["poetry", "run", "python", "main.py"]
   ```
4. Create a `pyproject.toml` file with your project dependencies and configuration.
5. Create a `poetry.lock` file by running `poetry lock` (if you have Poetry installed locally).
6. Create a `.env` file in the project directory:
   ```
   nano .env
   ```
7. Add your environment variables to the `.env` file:
   ```
   DISCORD_BOT_TOKEN=<your-discord-bot-token>
   YOUTUBE_API_KEY=<your-youtube-api-key>
   ```

### Step 4: Build and Run the Docker Container

1. Build the Docker image:
   ```
   docker build -t jiggy_music_bot .
   ```
2. Run the Docker container:
   ```
   docker run --env-file .env -v /path/to/host/audio_files:/app/audio_files jiggy_music_bot
   ```
   Replace `/path/to/host/audio_files` with the actual path where you want to store audio files on your Raspberry Pi.

## Obtaining Necessary Tokens and Keys

### Discord Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click "New Application" and give your bot a name.
3. Navigate to the "Bot" tab and click "Add Bot".
4. Under "Token", click "Copy" to get your bot token. **Keep this token private!**

### YouTube API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click on the project dropdown and select "New Project".
3. Give your project a name and click "Create".
4. Navigate to the "API & Services" section and click "Enable APIs and Services".
5. Search for "YouTube Data API v3" and enable it.
6. Click on "Create Credentials", choose "API key", and copy the generated key.

### Inviting the Bot to Your Server

To add the bot to your Discord server, use the following [Invite Link](https://discord.com/oauth2/authorize?client_id=1284369572476223511&permissions=3221504&integration_type=0&scope=applications.commands+bot).

## Commands and How to Use Them

- `/play <YouTube URL or Search Query>`
  - **Description**: Play a song from YouTube, either by providing a direct URL or searching by a keyword.
  - **Example**: `/play Rick Astley - Never Gonna Give You Up`

- `/upload_play`
  - **Description**: Upload an audio file (e.g., `.mp3` or `.wav`) and play it in the voice channel.
  - **Usage**: Run the command `/upload_play` and follow the instructions to upload your file.

- `/skip`
  - **Description**: Skips the currently playing song and plays the next one in the queue.

- `/stop`
  - **Description**: Stops the music, disconnects the bot from the voice channel, and clears the queue.

- `/queue`
  - **Description**: View the current queue of songs.

## Terms of Service

By using JiggyMusicBot, you agree to our [Terms of Service](TERMS.md).

## Privacy Policy

Please review our [Privacy Policy](PRIVACY.md) to understand how we collect and use your data.

---
Enjoy creating and using Jiggy Music Bot on your Raspberry Pi Zero 2 W for all your Discord music needs!
