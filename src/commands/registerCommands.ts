// src/commands/registerCommands.ts

import { Client, REST, Routes } from "discord.js";
import musicCommands from "./musicCommands";

export async function registerCommands(client: Client) {
  const commands = [musicCommands.data.toJSON()]; // Convert to JSON

  const rest = new REST({ version: "10" }).setToken(
    process.env.DISCORD_BOT_TOKEN!
  );

  try {
    console.log("Started refreshing application (/) commands.");

    await rest.put(Routes.applicationCommands(client.user!.id), {
      body: commands,
    });

    console.log("Successfully reloaded application (/) commands.");
  } catch (error) {
    console.error(error);
  }
}
