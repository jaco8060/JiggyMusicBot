# Jiggy Music Bot

This bot allows you to play music, upload audio files, and manage music queues in a Discord server. It supports YouTube links and direct audio file uploads.

## Getting Started

### Option 1: Installing and Running with Docker

This is the recommended method for running the bot, as it ensures consistent behavior across different systems.

#### Step 1: Build the Docker Image

1. Clone the repository from GitHub or download the project files.
2. Open a terminal and navigate to the project directory.
3. Build the Docker image using the following command:

```bash
docker build -t jiggy_music_bot .
```

#### Step 2: Run the Docker Container

Ensure you have a `.env` file in the project directory containing your environment variables:

```
DISCORD_BOT_TOKEN=<your-discord-bot-token>
YOUTUBE_API_KEY=<your-youtube-api-key>
```

Run the Docker container, specifying your `.env` file for the necessary environment variables:

```bash
docker run --env-file .env jiggy_music_bot
```

#### Step 3: Running the Container with Docker Desktop

1. Open Docker Desktop and go to the "Images" tab.
2. Find the `jiggy_music_bot` image and click "Run".
3. In the "Optional settings" section:
   - **Ports**: Leave the host port as `8080` (or any available port).
   - **Volumes**: Map the host path to the container path `/app/audio_files` if you want to persist audio files.
   - **Environment Variables**: Manually add your environment variables (e.g., `DISCORD_BOT_TOKEN` and `YOUTUBE_API_KEY`).
4. Click "Run" to start the container.

For more information on running Docker containers, refer to the [Docker Documentation](https://docs.docker.com/).

### Option 2: Installing and Running Locally on Windows

This option is for running the bot directly on your Windows machine using Poetry.

#### Step 1: Install Poetry

Download and install Poetry from the [official website](https://python-poetry.org/).

Verify the installation by running:

```
poetry --version
```

#### Step 2: Clone the Repository and Set Up the Environment

1. Clone the repository from GitHub or download the project files.
2. Navigate to the project directory in your terminal.
3. Create a `.env` file in the root directory with the following variables:

```
DISCORD_BOT_TOKEN=<your-discord-bot-token>
YOUTUBE_API_KEY=<your-youtube-api-key>
```

4. Install the dependencies using Poetry:

```
poetry install
```

#### Step 3: Run the Bot

Start the bot using the following command:

```
poetry run python main.py
```

### Obtaining the Discord Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click "New Application" and give your bot a name.
3. Navigate to the "Bot" tab and click "Add Bot".
4. Under "Token", click "Copy" to get your bot token. **Keep this token private!**

### Obtaining the YouTube API Key

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

### [Click here to read the Terms of Service](TERMS.md).


Enjoy using Jiggy Music Bot for all your music needs on Discord!
