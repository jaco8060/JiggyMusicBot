// src/bot.ts

import { Client, IntentsBitField } from "discord.js";
import { registerCommands } from "./commands/registerCommands";
import { ensureAudioFolder, setupLogging } from "./utils/config";

setupLogging();
ensureAudioFolder();

const client = new Client({
  intents: [
    IntentsBitField.Flags.Guilds,
    IntentsBitField.Flags.GuildVoiceStates,
  ],
});

client.once("ready", async () => {
  console.log(`Logged in as ${client.user?.tag}!`);
  await registerCommands(client);
});

export default client;
