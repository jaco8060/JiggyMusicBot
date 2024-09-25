// src/commands/registerCommands.ts
import { Client, REST, Routes } from "discord.js";
import { config } from "../config";
import { playCommand } from "./play";
import { queueCommand } from "./queue";
import { skipCommand } from "./skip";
import { stopCommand } from "./stop";
import { uploadPlayCommand } from "./uploadPlay";

export async function registerCommands(client: Client) {
  const commands = [
    playCommand.data.toJSON(),
    uploadPlayCommand.data.toJSON(),
    queueCommand.data.toJSON(),
    skipCommand.data.toJSON(),
    stopCommand.data.toJSON(),
  ];

  const rest = new REST({ version: "10" }).setToken(config.token);

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
