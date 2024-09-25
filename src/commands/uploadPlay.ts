import { SlashCommandBuilder } from "@discordjs/builders";
import { joinVoiceChannel } from "@discordjs/voice";
import {
  Attachment,
  CommandInteraction,
  GuildMember,
  TextChannel,
} from "discord.js";
import { MusicSubscription } from "../utils/audioPlayer";

export const uploadPlayCommand = {
  data: new SlashCommandBuilder()
    .setName("upload_play")
    .setDescription("Play an uploaded audio file"),
  async execute(interaction: CommandInteraction) {
    const member = interaction.member as GuildMember;
    const voiceChannel = member.voice.channel;

    if (!voiceChannel) {
      await interaction.reply({
        content: "You need to be in a voice channel to use this command.",
        ephemeral: true,
      });
      return;
    }

    await interaction.reply({
      content:
        "Please upload an audio file (mp3, wav, m4a). You have 60 seconds.",
      ephemeral: true,
    });

    // Wait for the user's message with the attachment
    const filter = (message: any) =>
      message.author.id === interaction.user.id &&
      message.attachments.size > 0 &&
      [".mp3", ".wav", ".m4a"].some((ext) =>
        message.attachments.first()?.name.endsWith(ext)
      );

    const channel = interaction.channel as TextChannel;

    try {
      const response = await channel.awaitMessages({
        filter,
        max: 1,
        time: 60000,
        errors: ["time"],
      });

      const message = response.first();
      const attachment = message?.attachments.first() as Attachment;

      if (!attachment) {
        await interaction.followUp({
          content: "No valid audio file was uploaded.",
          ephemeral: true,
        });
        return;
      }

      const url = attachment.url;

      // Enqueue the audio file
      const subscription = MusicSubscription.getOrCreate(interaction.guildId!);

      if (!subscription.voiceConnection) {
        subscription.voiceConnection = joinVoiceChannel({
          channelId: voiceChannel.id,
          guildId: voiceChannel.guild.id,
          adapterCreator: voiceChannel.guild.voiceAdapterCreator,
        });
      }

      subscription.enqueue({
        title: attachment.name!,
        url: url,
        isLocalFile: true,
      });

      await interaction.followUp(`Enqueued **${attachment.name}**`);

      // Optionally delete the user's message containing the attachment
      await message?.delete();
    } catch (error) {
      console.error(error);
      await interaction.followUp({
        content: "You did not upload an audio file in time.",
        ephemeral: true,
      });
    }
  },
};
