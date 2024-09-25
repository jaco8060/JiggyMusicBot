// src/commands/stop.ts
import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { MusicSubscription } from "../utils/audioPlayer";

export const stopCommand = {
  data: new SlashCommandBuilder()
    .setName("stop")
    .setDescription("Stop the music and leave the voice channel"),
  async execute(interaction: CommandInteraction) {
    const subscription = MusicSubscription.get(interaction.guildId!);

    if (subscription) {
      subscription.voiceConnection.destroy();
      MusicSubscription.delete(interaction.guildId!);
      await interaction.reply("Stopped the music and left the voice channel.");
    } else {
      await interaction.reply("Not playing in this server.");
    }
  },
};
