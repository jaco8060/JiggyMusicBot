// src/views/VideoSelectionView.ts

import {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonInteraction,
  ButtonStyle,
  ComponentType,
  InteractionReplyOptions,
  StringSelectMenuBuilder,
  StringSelectMenuInteraction,
} from "discord.js";
import { AudioManager } from "../utils/audio";

export class VideoSelectionView {
  private videos: Array<{ url: string; title: string }>;
  private audioManager: AudioManager;

  constructor(
    videos: Array<{ url: string; title: string }>,
    private interaction: ButtonInteraction | StringSelectMenuInteraction,
    audioManager: AudioManager
  ) {
    this.videos = videos;
    this.audioManager = audioManager;
    this.showMenu();
  }

  private async showMenu() {
    const options = this.videos.map((video, index) => ({
      label: video.title,
      value: index.toString(),
    }));

    const selectMenu = new StringSelectMenuBuilder()
      .setCustomId("video_select")
      .setPlaceholder("Select a video")
      .addOptions(options);

    const actionRow =
      new ActionRowBuilder<StringSelectMenuBuilder>().addComponents(selectMenu);

    await this.interaction.followUp({
      content: "Please select a video:",
      components: [actionRow],
    });

    const filter = (i: StringSelectMenuInteraction) =>
      i.customId === "video_select" && i.user.id === this.interaction.user.id;

    const collector = this.interaction.channel?.createMessageComponentCollector(
      {
        filter,
        componentType: ComponentType.StringSelect,
        time: 60000,
      }
    );

    collector?.on("collect", async (i: StringSelectMenuInteraction) => {
      const selectedIndex = parseInt(i.values[0], 10);
      const selectedVideo = this.videos[selectedIndex];

      const title = await this.audioManager.addToQueue(selectedVideo.url);
      await i.update({
        content: `Added **${title}** to the queue.`,
        components: [],
      });

      if (!this.audioManager.isPlaying()) {
        this.audioManager.playNext();
      }
    });

    collector?.on("end", async () => {
      await this.interaction.editReply({ components: [] });
    });
  }
}
