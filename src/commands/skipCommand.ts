// src/commands/skipCommand.ts

import { ChatInputCommandInteraction, SlashCommandBuilder } from "discord.js";
import { AudioManager } from "../utils/audio";

export const SkipCommand = {
  data: new SlashCommandBuilder()
    .setName("skip")
    .setDescription("Skip the current song and play the next one in the queue"),

  async execute(interaction: ChatInputCommandInteraction) {
    const audioManager = AudioManager.getOrCreate(interaction.guildId!);

    if (!audioManager.isPlaying()) {
      await interaction.reply({
        content: "No song is currently playing.",
        ephemeral: true,
      });
      return;
    }

    audioManager.skip();
    await interaction.reply("Skipped the current song.");
  },
};
