// src/views/QueuePaginationView.ts

// This file would implement a view that allows users to navigate through the queue.
// Since the implementation was not provided, here's a basic structure.

import {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonInteraction,
  ButtonStyle,
  EmbedBuilder,
  Interaction,
} from "discord.js";
import { AudioManager } from "../utils/audio";

export class QueuePaginationView {
  private currentPage = 0;
  private itemsPerPage = 10;
  private queue: any[];
  private interaction: Interaction;
  private audioManager: AudioManager;

  constructor(interaction: Interaction, audioManager: AudioManager) {
    this.interaction = interaction;
    this.audioManager = audioManager;
    this.queue = audioManager.getQueue();
    this.showPage();
  }

  private async showPage() {
    const start = this.currentPage * this.itemsPerPage;
    const end = start + this.itemsPerPage;
    const pageItems = this.queue.slice(start, end);

    const embed = new EmbedBuilder()
      .setTitle("Music Queue")
      .setDescription(
        pageItems
          .map((song, index) => `${start + index + 1}. ${song.title}`)
          .join("\n")
      );

    const prevButton = new ButtonBuilder()
      .setCustomId("prev_page")
      .setLabel("Previous")
      .setStyle(ButtonStyle.Primary)
      .setDisabled(this.currentPage === 0);

    const nextButton = new ButtonBuilder()
      .setCustomId("next_page")
      .setLabel("Next")
      .setStyle(ButtonStyle.Primary)
      .setDisabled(end >= this.queue.length);

    const actionRow = new ActionRowBuilder<ButtonBuilder>().addComponents(
      prevButton,
      nextButton
    );

    await this.interaction.reply({
      embeds: [embed],
      components: [actionRow],
    });

    const filter = (i: ButtonInteraction) =>
      ["prev_page", "next_page"].includes(i.customId) &&
      i.user.id === this.interaction.user.id;

    const collector = this.interaction.channel?.createMessageComponentCollector(
      {
        filter,
        time: 60000,
      }
    );

    collector?.on("collect", async (i: ButtonInteraction) => {
      if (i.customId === "prev_page") {
        this.currentPage--;
      } else if (i.customId === "next_page") {
        this.currentPage++;
      }
      await i.deferUpdate();
      await this.showPage();
    });

    collector?.on("end", async () => {
      await this.interaction.editReply({ components: [] });
    });
  }
}
