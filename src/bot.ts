// src/bot.ts

import { Client, IntentsBitField, Interaction } from "discord.js";
import { AdminCommands } from "./commands/adminCommands";
import { PlayCommand, videoSelectionMaps } from "./commands/playCommand";
import { QueueCommand } from "./commands/queueCommand";
import { registerCommands } from "./commands/registerCommands";
import { RepeatCommand } from "./commands/repeatCommand";
import { SkipCommand } from "./commands/skipCommand";
import { StopCommand } from "./commands/stopCommand";
import { UploadPlayCommand } from "./commands/uploadPlayCommand";
import { AudioManager } from "./utils/audio";
import { ensureAudioFolder, setupLogging } from "./utils/config";
import { QueuePaginationView } from "./views/QueuePaginationView";
import { VideoSelectionView } from "./views/VideoSelectionView";

setupLogging();
ensureAudioFolder();

const client = new Client({
  intents: [
    IntentsBitField.Flags.Guilds,
    IntentsBitField.Flags.GuildVoiceStates,
    IntentsBitField.Flags.GuildMessages,
    IntentsBitField.Flags.MessageContent,
  ],
});

client.once("ready", async () => {
  console.log(`Logged in as ${client.user?.tag}!`);
  await registerCommands(client);
});

client.on("interactionCreate", async (interaction: Interaction) => {
  if (interaction.isChatInputCommand()) {
    const { commandName } = interaction;

    try {
      if (commandName === "play") {
        await PlayCommand.execute(interaction);
      } else if (commandName === "upload_play") {
        await UploadPlayCommand.execute(interaction);
      } else if (commandName === "skip") {
        await SkipCommand.execute(interaction);
      } else if (commandName === "stop") {
        await StopCommand.execute(interaction);
      } else if (commandName === "queue") {
        await QueueCommand.execute(interaction);
      } else if (commandName === "repeat") {
        await RepeatCommand.execute(interaction);
      } else if (commandName === "admin") {
        await AdminCommands.execute(interaction);
      } else {
        await interaction.reply("Unknown command.");
      }
    } catch (error) {
      console.error(error);
      if (interaction.deferred || interaction.replied) {
        await interaction.followUp({
          content: "There was an error executing the command.",
          ephemeral: true,
        });
      } else {
        await interaction.reply({
          content: "There was an error executing the command.",
          ephemeral: true,
        });
      }
    }
  } else if (interaction.isButton()) {
    await interaction.deferUpdate(); // Defer immediately

    if (interaction.customId.startsWith("video_select_")) {
      const audioManager = AudioManager.getOrCreate(interaction.guildId!);
      const match = interaction.customId.match(/video_select_(.+)_(\d+)/);
      if (!match) {
        await interaction.followUp({
          content: "The selection is invalid or has expired.",
          ephemeral: true,
        });
        return;
      }

      const selectionId = match[1];
      const index = parseInt(match[2], 10);

      const videos = videoSelectionMaps.get(selectionId);
      if (!videos) {
        await interaction.followUp({
          content: "The selection has expired or is invalid.",
          ephemeral: true,
        });
        return;
      }

      const video = videos[index];

      try {
        const title = await audioManager.addToQueue(video.url);
        await interaction.editReply({
          content: `Added **${title}** to the queue.`,
          components: [],
        });

        if (!audioManager.isPlaying()) {
          audioManager.playNext();
        }
      } catch (error) {
        console.error(error);
        await interaction.followUp({
          content: "An error occurred while processing your request.",
          ephemeral: true,
        });
      }
    }
  }
});

export default client;
