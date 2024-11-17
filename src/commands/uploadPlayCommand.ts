// src/commands/uploadPlayCommand.ts

import {
  ChatInputCommandInteraction,
  GuildMember,
  SlashCommandBuilder,
  TextChannel,
} from "discord.js";
import { AudioManager } from "../utils/audio";

export const UploadPlayCommand = {
  data: new SlashCommandBuilder()
    .setName("upload_play")
    .setDescription("Play an uploaded audio file"),

  async execute(interaction: ChatInputCommandInteraction) {
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
      content: "Please upload an audio file to play in the voice channel:",
      ephemeral: true,
    });

    const filter = (m: any) =>
      m.author.id === interaction.user.id &&
      m.attachments.size > 0 &&
      [".mp3", ".wav", ".m4a"].some((ext) =>
        m.attachments.first()?.name?.endsWith(ext)
      );

    const channel = interaction.channel;
    if (!channel || !(channel instanceof TextChannel)) {
      await interaction.followUp(
        "This command can only be used in a text channel."
      );
      return;
    }

    try {
      const collected = await channel.awaitMessages({
        filter,
        max: 1,
        time: 60000,
        errors: ["time"],
      });

      const attachment = collected?.first()?.attachments.first();
      if (attachment) {
        const audioManager = AudioManager.getOrCreate(interaction.guildId!);
        await audioManager.connect(voiceChannel);

        const filePath = await audioManager.saveUploadedFile(attachment);
        audioManager.addFileToQueue(filePath, attachment.name!);

        await collected?.first()?.delete();

        await interaction.followUp(
          `Added **${attachment.name}** to the queue.`
        );

        if (!audioManager.isPlaying()) {
          audioManager.playNext();
        }
      } else {
        await interaction.followUp("No valid audio file uploaded.");
      }
    } catch (error) {
      await interaction.followUp("You took too long to upload an audio file.");
    }
  },
};
