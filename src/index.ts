import * as dotenv from "dotenv"; // Import dotenv at the very beginning
dotenv.config(); // Load environment variables

import { Client, GatewayIntentBits } from "discord.js";
import { registerCommands } from "./commands/registerCommands";
import { config } from "./config"; // Import the centralized config
import { speechRecognitionHandler } from "./utils/speechRecognition";

// Create a new client instance
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
});

// Login to Discord with your client's token from the config object
client
  .login(config.token)
  .then(() => {
    console.log(`Logged in as ${client.user?.tag}!`);
    // Register commands
    registerCommands(client);
    // Handle speech recognition
    speechRecognitionHandler(client);
  })
  .catch((err) => {
    console.error("Failed to log in:", err);
  });
