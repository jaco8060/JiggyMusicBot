import { SlashCommandBuilder } from "@discordjs/builders";
import { joinVoiceChannel } from "@discordjs/voice";
import {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonInteraction,
  ButtonStyle,
  Collection,
  CommandInteraction,
  ComponentType,
  GuildMember,
  Message,
} from "discord.js";
import { MusicSubscription } from "../utils/audioPlayer";
import { getYTInfo, Video, youtubeSearch } from "../utils/youtube";

export const playCommand = {
  data: new SlashCommandBuilder()
    .setName("play")
    .setDescription("Play a song from YouTube")
    .addStringOption((option) =>
      option
        .setName("query")
        .setDescription("The song name or URL")
        .setRequired(true)
    ),
  async execute(interaction: CommandInteraction) {
    const query = interaction.options.get("query", true).value as string;

    const member = interaction.member as GuildMember;
    const voiceChannel = member.voice.channel;

    if (!voiceChannel) {
      await interaction.reply(
        "You need to be in a voice channel to play music!"
      );
      return;
    }

    await interaction.deferReply();

    const subscription = MusicSubscription.getOrCreate(interaction.guildId!);

    if (!subscription.voiceConnection) {
      subscription.voiceConnection = joinVoiceChannel({
        channelId: voiceChannel.id,
        guildId: voiceChannel.guild.id,
        adapterCreator: voiceChannel.guild.voiceAdapterCreator,
      });
    }

    if (isValidUrl(query)) {
      // Handle URL
      try {
        const track = await getYTInfo(query);
        subscription.enqueue(track);
        await interaction.editReply(`Enqueued **${track.title}**`);
      } catch (error) {
        console.error(error);
        await interaction.editReply("Error: Could not play the track.");
      }
    } else {
      // Handle search query
      try {
        const videos = await youtubeSearch(query);

        if (videos.length === 0) {
          await interaction.editReply("No videos found.");
          return;
        }

        const row = new ActionRowBuilder<ButtonBuilder>().addComponents(
          videos.map((video, index) =>
            new ButtonBuilder()
              .setCustomId(`select_${index}`)
              .setLabel(`#${index + 1}`)
              .setStyle(ButtonStyle.Primary)
          )
        );

        const description = videos
          .map((video, index) => `**#${index + 1}** - ${video.title}`)
          .join("\n");

        // After sending the initial message with buttons
        const message = (await interaction.editReply({
          content: `Top 5 results for **${query}**:\n\n${description}`,
          components: [row],
        })) as Message;

        // Create a message component collector
        const collector = message.createMessageComponentCollector({
          componentType: ComponentType.Button,
          filter: (i) => i.user.id === interaction.user.id,
          time: 60000,
        });

        collector.on("collect", async (i: ButtonInteraction) => {
          const index = parseInt(i.customId.split("_")[1], 10);
          const selectedVideo = videos[index];

          try {
            const track = await getYTInfo(selectedVideo.url);
            subscription.enqueue(track);

            await i.update({
              content: `Enqueued **${selectedVideo.title}**`,
              components: [],
            });

            collector.stop();
          } catch (error) {
            console.error(error);
            await i.update({
              content: "Error: Could not play the selected track.",
              components: [],
            });
          }
        });

        collector.on(
          "end",
          async (
            collected: Collection<string, ButtonInteraction>,
            reason: string
          ) => {
            if (reason === "time") {
              await interaction.editReply({
                content: "No selection made in time.",
                components: [],
              });
            }
          }
        );
      } catch (error) {
        console.error(error);
        await interaction.editReply("Error: Could not search YouTube.");
      }
    }
  },
};

function isValidUrl(string: string): boolean {
  try {
    new URL(string);
    return true;
  } catch {
    return false;
  }
}
