// src/commands/queueCommand.ts

import { ChatInputCommandInteraction, SlashCommandBuilder } from "discord.js";
import { AudioManager } from "../utils/audio";
import { QueuePaginationView } from "../views/QueuePaginationView";

export const QueueCommand = {
  data: new SlashCommandBuilder()
    .setName("queue")
    .setDescription("List the current song queue"),

  async execute(interaction: ChatInputCommandInteraction) {
    const audioManager = AudioManager.getOrCreate(interaction.guildId!);

    if (
      audioManager.getCurrentSong() === null &&
      audioManager.getQueue().length === 0
    ) {
      await interaction.reply({
        content: "There are no songs currently playing or queued.",
        ephemeral: true,
      });
    } else {
      const view = new QueuePaginationView(interaction, audioManager);
      await view.showPage();
    }
  },
};
