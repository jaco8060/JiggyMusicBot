// src/commands/repeatCommand.ts

import { ChatInputCommandInteraction, SlashCommandBuilder } from "discord.js";
import { AudioManager } from "../utils/audio";

export const RepeatCommand = {
  data: new SlashCommandBuilder()
    .setName("repeat")
    .setDescription("Toggle repeat mode on or off")
    .addStringOption((option) =>
      option
        .setName("mode")
        .setDescription("Choose 'on' or 'off'")
        .setRequired(true)
        .addChoices({ name: "on", value: "on" }, { name: "off", value: "off" })
    ),

  async execute(interaction: ChatInputCommandInteraction) {
    const mode = interaction.options.getString("mode", true).toLowerCase();
    const audioManager = AudioManager.getOrCreate(interaction.guildId!);

    if (mode === "on") {
      if (!audioManager.getRepeatMode()) {
        audioManager.setRepeatMode(true);
        await interaction.reply("Repeat mode is now **ON**.");
      } else {
        await interaction.reply({
          content: "Repeat mode is already **ON**.",
          ephemeral: true,
        });
      }
    } else if (mode === "off") {
      if (audioManager.getRepeatMode()) {
        audioManager.setRepeatMode(false);
        await interaction.reply("Repeat mode is now **OFF**.");
      } else {
        await interaction.reply({
          content: "Repeat mode is already **OFF**.",
          ephemeral: true,
        });
      }
    } else {
      await interaction.reply({
        content: "Please specify 'on' or 'off'.",
        ephemeral: true,
      });
    }
  },
};
