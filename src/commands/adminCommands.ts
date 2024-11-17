// src/commands/adminCommands.ts

import { ChatInputCommandInteraction, SlashCommandBuilder } from "discord.js";

export const AdminCommands = {
  data: new SlashCommandBuilder()
    .setName("admin")
    .setDescription("Admin commands")
    .addSubcommand((subcommand) =>
      subcommand
        .setName("shutdown")
        .setDescription("Shut down the bot (Owner only)")
    ),

  async execute(interaction: ChatInputCommandInteraction) {
    if (interaction.user.id !== interaction.client.application?.owner?.id) {
      await interaction.reply({
        content: "You do not have permission to use this command.",
        ephemeral: true,
      });
      return;
    }

    const subcommand = interaction.options.getSubcommand();
    switch (subcommand) {
      case "shutdown":
        await interaction.reply("Shutting down...");
        process.exit(0);
      default:
        await interaction.reply("Unknown admin command.");
    }
  },
};
