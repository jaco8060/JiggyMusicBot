# Jiggy Music Bot

This bot allows you to play music, upload audio files, and manage music queues in a Discord server. It supports YouTube links and direct audio file uploads.

## Table of Contents
1. [Creating Your Discord Bot](#creating-your-discord-bot)
2. [Running the Bot on Windows](#running-the-bot-on-windows)
3. [Raspberry Pi Implementation](#raspberry-pi-implementation)
4. [Commands and How to Use Them](#commands-and-how-to-use-them)
5. [Terms of Service and Privacy Policy](#terms-of-service-and-privacy-policy)

## Creating Your Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click on "New Application" and give your bot a name.
3. Navigate to the "Bot" tab on the left sidebar.
4. Click "Add Bot" and confirm by clicking "Yes, do it!"
5. Under the "TOKEN" section, click "Copy" to copy your bot token. You'll need this for the `.env` file.
6. Scroll down to the "Privileged Gateway Intents" section and enable "MESSAGE CONTENT INTENT".
7. Click "Save Changes" at the bottom of the page.

### Inviting Your Bot to Your Server

1. In the Discord Developer Portal, go to the "OAuth2" tab in the left sidebar.
2. Scroll down to the "OAuth2 URL Generator" section.
3. Under "SCOPES", check the boxes for:
   - `bot`
   - `applications.commands`
4. Under "BOT PERMISSIONS", check the boxes for:
   - Send Messages
   - Connect
   - Speak
   - Manage Messages
   - Read Message History
5. Scroll down and copy the generated URL.
6. Open this URL in a new browser tab.
7. Select the server you want to add the bot to and click "Authorize".

## Running the Bot on Windows

### Prerequisites
- [Git](https://git-scm.com/downloads)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/jaco8060/JiggyMusicBot.git
   cd JiggyMusicBot
   ```

2. Create a `.env` file in the project directory:
   ```
   notepad .env
   ```

3. Add your environment variables to the `.env` file:
   ```
   DISCORD_BOT_TOKEN=<your-discord-bot-token>
   YOUTUBE_API_KEY=<your-youtube-api-key>
   ```

4. Create a batch file named `start_bot.bat` in the project directory:
   ```
   notepad start_bot.bat
   ```

5. Add the following content to the batch file:
   ```batch
   @echo off
   docker build -t jiggybot1 .
   docker stop jiggyBotContainer1
   docker rm jiggyBotContainer1
   docker run -d --name jiggyBotContainer1 --env-file .env --restart unless-stopped jiggybot1
   ```

6. Run the batch file to build and start the bot:
   ```
   start_bot.bat
   ```

## Raspberry Pi Implementation

This implementation is designed for a Raspberry Pi Zero 2 W using DietPi as the operating system.

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
   git clone https://github.com/jaco8060/JiggyMusicBot.git
   cd JiggyMusicBot
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

# Remove the existing container
docker rm jiggyBotContainer1

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

## Terms of Service and Privacy Policy

- By using JiggyMusicBot, you agree to our [Terms of Service](TERMS.md).
- Please review our [Privacy Policy](PRIVACY.md) to understand how we collect and use your data.

---
Enjoy using Jiggy Music Bot for all your Discord music needs!
