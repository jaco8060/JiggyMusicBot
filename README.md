# Jiggy Music Bot

This bot allows you to play music, upload audio files, and manage music queues in a Discord server. It supports YouTube links and direct audio file uploads.

## Getting Started

### Step 1: Fork the Repl

1. Go to [Replit](https://replit.com/@jaco8060/JiggyMusic-Bot?v=1)
2. Press the **"Fork"** button to create your copy of the project.

### Step 2: Run the Bot

1. Once forked, click on the **"➡️ Run"** button to start the bot.
2. The bot will start running and show you a link to your bot's web server. However, this is just for keeping the bot alive — your primary interaction will be through Discord commands.

### Step 3: Invite the Bot to Your Server

To add the bot to your Discord server, use the following URL:
https://discord.com/oauth2/authorize?client_id=1284369572476223511&permissions=3221504&integration_type=0&scope=applications.commands+bot 

### Step 4: Use the Commands

Once the bot is in your server, you can interact with it using the following commands:

## Commands and How to Use Them

### `/play <YouTube URL or Search Query>`
- **Description**: Play a song from YouTube, either by providing a direct URL or searching by a keyword.
- **Usage**:
- **Example 1**: `/play https://www.youtube.com/watch?v=dQw4w9WgXcQ`
 - This command will directly play the specified YouTube video.
- **Example 2**: `/play Rick Astley - Never Gonna Give You Up`
 - The bot will search for the top results and allow you to select from the top 5 videos.

### `/upload_play`
- **Description**: Upload an audio file (e.g., .mp3 or .wav) and play it in the voice channel.
- **Usage**:
1. Run the command `/upload_play` while in a voice channel.
2. The bot will ask you to upload an audio file.
3. Once uploaded, it will be added to the queue and played after the current song, or immediately if the queue is empty.

### `/skip`
- **Description**: Skips the currently playing song and plays the next one in the queue (if any).
- **Usage**:
- **Example**: `/skip`
 - This will skip the current song and start the next in the queue.

### `/stop`
- **Description**: Stops the music, disconnects the bot from the voice channel, and clears the queue.
- **Usage**:
- **Example**: `/stop`
 - This will stop the bot from playing music and clear the queue.

### `/queue`
- **Description**: View the current queue of songs.
- **Usage**:
- **Example**: `/queue`
 - This will list all the songs currently in the queue, along with their order.

---

Enjoy using **JiggyMusic Bot** for all your music needs on Discord!
