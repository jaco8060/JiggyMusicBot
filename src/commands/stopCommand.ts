// src/commands/stopCommand.ts

import { ChatInputCommandInteraction, SlashCommandBuilder } from "discord.js";
import { AudioManager } from "../utils/audio";

export const StopCommand = {
  data: new SlashCommandBuilder()
    .setName("stop")
    .setDescription("Stop the audio and disconnect the bot"),

  async execute(interaction: ChatInputCommandInteraction) {
    const audioManager = AudioManager.getOrCreate(interaction.guildId!);

    if (audioManager.isPlaying() || audioManager.getQueue().length > 0) {
      audioManager.stop();
      await interaction.reply("Stopped playback and disconnected the bot.");
    } else {
      await interaction.reply({
        content: "The bot is not connected to a voice channel.",
        ephemeral: true,
      });
    }
  },
};
