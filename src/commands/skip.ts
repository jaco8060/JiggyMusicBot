// src/commands/skip.ts
import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { MusicSubscription } from "../utils/audioPlayer";

export const skipCommand = {
  data: new SlashCommandBuilder()
    .setName("skip")
    .setDescription("Skip the current song"),
  async execute(interaction: CommandInteraction) {
    const subscription = MusicSubscription.get(interaction.guildId!);

    if (subscription) {
      subscription.audioPlayer.stop();
      await interaction.reply("Skipped the current song.");
    } else {
      await interaction.reply("Not playing in this server.");
    }
  },
};
