// src/views/QueuePaginationView.ts

import {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonInteraction,
  ButtonStyle,
  CommandInteraction,
  ComponentType,
  EmbedBuilder,
} from "discord.js";
import { AudioManager } from "../utils/audio";

export class QueuePaginationView {
  private currentPage = 0;
  private itemsPerPage = 10;
  private queue: any[];
  private interaction: CommandInteraction;
  private messageId?: string;

  private audioManager: AudioManager;

  constructor(interaction: CommandInteraction, audioManager: AudioManager) {
    this.interaction = interaction;
    this.audioManager = audioManager;
    this.queue = audioManager.getQueue();
  }

  public async showPage() {
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

    if (this.audioManager.getCurrentSong()) {
      embed.setFooter({
        text: `Currently Playing: ${this.audioManager.getCurrentSong()?.title}`,
      });
    }

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

    const message = await this.interaction.reply({
      embeds: [embed],
      components: [actionRow],
      fetchReply: true,
    });

    this.messageId = message.id;
  }

  // Static method to handle button interactions
  public static async handleButtonInteraction(
    interaction: ButtonInteraction,
    audioManager: AudioManager
  ) {
    if (!interaction.message || !interaction.message.interaction) return;

    const originalInteractionId = interaction.message.interaction.id;
    if (interaction.message.id !== originalInteractionId) return;

    // Retrieve current page from embed footer or other storage
    let currentPage = 0; // You'll need to store and retrieve this value

    if (interaction.customId === "prev_page") {
      currentPage--;
    } else if (interaction.customId === "next_page") {
      currentPage++;
    }
  }
}
