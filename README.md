# Jiggy Music Bot

This bot allows you to play music, upload audio files, and manage music queues in a Discord server. It supports YouTube links and direct audio file uploads. This project is designed to run on a Raspberry Pi Zero 2 W using DietPi as the operating system.

## Setting Up the Project

### Step 1: Set Up Your Raspberry Pi Zero 2 W with DietPi

1. Visit the official [DietPi Installation Guide](https://dietpi.com/docs/install/) and follow the instructions for Raspberry Pi Zero 2 W.
2. Download the appropriate DietPi image for Raspberry Pi Zero 2 W.
3. Flash the image to your microSD card using a tool like Etcher or Raspberry Pi Imager.
4. Insert the microSD card into your Raspberry Pi Zero 2 W and power it on.
5. Follow the initial setup process for DietPi, ensuring you connect to your network.

### Step 2: Install Docker and Git on DietPi

1. After setting up DietPi, SSH into your Raspberry Pi Zero 2 W.
2. Visit the [DietPi Software Installation Tool guide](https://dietpi.com/docs/dietpi_tools/software_installation/) for detailed instructions on installing software packages.
3. To install Docker and Git, use the following commands in the DietPi-Software tool:
   ```
   Docker
   Git
   ```
   This will install Docker, Git, and all their dependencies.

4. After installation, reboot your Raspberry Pi:
   ```
   sudo reboot
   ```

### Step 3: Clone the Repository and Set Up the Project

1. Clone the repository:
   ```
   git clone https://github.com/your-username/jiggy-music-bot.git
   cd jiggy-music-bot
   ```

2. Create a `.env` file in the project directory:
   ```
   nano .env
   ```

3. Add your environment variables to the `.env` file:
   ```
   DISCORD_BOT_TOKEN=<your-discord-bot-token>
   YOUTUBE_API_KEY=<your-youtube-api-key>
   ```

### Step 4: Build and Run the Docker Container

Create a bash script named `start_bot.sh` in the project directory:

```bash
nano start_bot.sh
```

Add the following content to the script:

```bash
#!/bin/bash

# Build the Docker image
docker build -t jiggybot1 .

# Stop the existing container if running
docker stop jiggyBotContainer1

# Run a new container with the built image
docker run -d --name jiggyBotContainer1 --cpus="4.0" --env-file .env --restart unless-stopped jiggybot1
```

Make the script executable:

```bash
chmod +x start_bot.sh
```

Run the script to build and start the bot:

```bash
./start_bot.sh
```

This script will build the Docker image, stop any existing container (if running), and start a new container with the specified settings.

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
Enjoy using Jiggy Music Bot on your Raspberry Pi Zero 2 W for all your Discord music needs!
