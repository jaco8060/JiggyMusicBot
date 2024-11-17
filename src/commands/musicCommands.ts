// src/commands/musicCommands.ts

import {
  ChatInputCommandInteraction,
  EmbedBuilder,
  GuildMember,
  SlashCommandBuilder,
} from "discord.js";
import { AudioManager } from "../utils/audio";
import { searchYouTube } from "../utils/youtube";
import { VideoSelectionView } from "../views/VideoSelectionView";

const musicCommands = {
  data: new SlashCommandBuilder()
    .setName("music")
    .setDescription("Music commands")
    .addSubcommand((subcommand) =>
      subcommand
        .setName("play")
        .setDescription("Play a YouTube link or search for a video")
        .addStringOption((option) =>
          option
            .setName("prompt")
            .setDescription("URL or search term")
            .setRequired(true)
        )
    )
    .addSubcommand((subcommand) =>
      subcommand.setName("skip").setDescription("Skip the current song")
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("stop")
        .setDescription("Stop playback and clear the queue")
    )
    .addSubcommand((subcommand) =>
      subcommand.setName("queue").setDescription("Show the current queue")
    )
    .addSubcommand((subcommand) =>
      subcommand
        .setName("repeat")
        .setDescription("Toggle repeat mode")
        .addBooleanOption((option) =>
          option.setName("mode").setDescription("On or off").setRequired(true)
        )
    ),

  async execute(interaction: ChatInputCommandInteraction) {
    const subcommand = interaction.options.getSubcommand();
    const audioManager = AudioManager.getOrCreate(interaction.guildId!);

    switch (subcommand) {
      case "play":
        // Existing play command implementation
        break;
      case "skip":
        // Implement skip logic
        break;
      case "stop":
        // Implement stop logic
        break;
      case "queue":
        // Implement queue display using QueuePaginationView
        break;
      case "repeat":
        // Implement repeat toggle logic
        break;
      default:
        await interaction.reply("Unknown subcommand.");
    }
  },
};

export default musicCommands;
