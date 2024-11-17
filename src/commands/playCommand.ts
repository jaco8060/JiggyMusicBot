// src/commands/playCommand.ts

import { randomUUID } from "crypto";
import {
  ChatInputCommandInteraction,
  EmbedBuilder,
  GuildMember,
  SlashCommandBuilder,
} from "discord.js";
import { AudioManager } from "../utils/audio";
import { youtubeSearch } from "../utils/youtube"; // Updated import
import { VideoSelectionView } from "../views/VideoSelectionView";

// Map to store video selections
export const videoSelectionMaps: Map<
  string,
  Array<{ url: string; title: string }>
> = new Map();

export const PlayCommand = {
  data: new SlashCommandBuilder()
    .setName("play")
    .setDescription("Play a YouTube link or search for a video")
    .addStringOption((option) =>
      option
        .setName("prompt")
        .setDescription("URL or search term")
        .setRequired(true)
    ),

  async execute(interaction: ChatInputCommandInteraction) {
    const prompt = interaction.options.getString("prompt", true);
    const member = interaction.member as GuildMember;
    const voiceChannel = member.voice.channel;

    if (!voiceChannel) {
      await interaction.reply({
        content: "You need to be in a voice channel.",
        ephemeral: true,
      });
      return;
    }

    await interaction.deferReply();

    try {
      const audioManager = AudioManager.getOrCreate(interaction.guildId!);
      await audioManager.connect(voiceChannel);

      let isUrl = false;
      try {
        new URL(prompt);
        isUrl = true;
      } catch {
        isUrl = false;
      }

      if (isUrl) {
        const title = await audioManager.addToQueue(prompt);
        await interaction.editReply(`Added **${title}** to the queue.`);

        if (!audioManager.isPlaying()) {
          audioManager.playNext();
        }
      } else {
        const videos = await youtubeSearch(prompt);
        if (videos.length === 0) {
          await interaction.editReply(`No videos found for **${prompt}**.`);
          return;
        }

        const selectionId = randomUUID();
        videoSelectionMaps.set(selectionId, videos);

        const view = new VideoSelectionView(
          videos,
          interaction,
          audioManager,
          selectionId
        );
        const components = view.getComponents();

        const embed = new EmbedBuilder()
          .setTitle(`Results for "${prompt}"`)
          .setDescription(
            videos
              .map((video, index) => `**${index + 1}.** ${video.title}`)
              .join("\n")
          );

        await interaction.editReply({ embeds: [embed], components });

        // Remove the selection after some time
        setTimeout(() => {
          videoSelectionMaps.delete(selectionId);
        }, 5 * 60 * 1000); // 5 minutes
      }
    } catch (error) {
      console.error(error);
      await interaction.editReply(
        "An error occurred while processing your request."
      );
    }
  },
};
