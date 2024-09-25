// src/commands/queue.ts
import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { MusicSubscription } from "../utils/audioPlayer";

export const queueCommand = {
  data: new SlashCommandBuilder()
    .setName("queue")
    .setDescription("View the song queue"),
  async execute(interaction: CommandInteraction) {
    const subscription = MusicSubscription.get(interaction.guildId!);

    if (subscription && subscription.queue.length > 0) {
      const queueDescription = subscription.queue
        .map((track, index) => `${index + 1}. ${track.title}`)
        .join("\n");

      await interaction.reply(`**Current Queue:**\n${queueDescription}`);
    } else {
      await interaction.reply("The queue is empty.");
    }
  },
};
