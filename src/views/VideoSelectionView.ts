// src/views/VideoSelectionView.ts

import {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonInteraction,
  ButtonStyle,
  ChatInputCommandInteraction,
  ComponentType,
} from "discord.js";
import { AudioManager } from "../utils/audio";

export class VideoSelectionView {
  private videos: Array<{ url: string; title: string }>;
  private interaction: ChatInputCommandInteraction;
  private audioManager: AudioManager;
  private selectionId: string;

  constructor(
    videos: Array<{ url: string; title: string }>,
    interaction: ChatInputCommandInteraction,
    audioManager: AudioManager,
    selectionId: string
  ) {
    this.videos = videos;
    this.interaction = interaction;
    this.audioManager = audioManager;
    this.selectionId = selectionId;
  }

  public getComponents() {
    const buttons = this.videos.slice(0, 5).map((video, index) => {
      return new ButtonBuilder()
        .setCustomId(`video_select_${this.selectionId}_${index}`)
        .setLabel(`#${index + 1}`)
        .setStyle(ButtonStyle.Primary);
    });

    const actionRow = new ActionRowBuilder<ButtonBuilder>().addComponents(
      ...buttons
    );

    return [actionRow];
  }
}
