// src/commands/registerCommands.ts

import { Client, REST, Routes } from "discord.js";
import { AdminCommands } from "./adminCommands";
import { PlayCommand } from "./playCommand";
import { QueueCommand } from "./queueCommand";
import { RepeatCommand } from "./repeatCommand";
import { SkipCommand } from "./skipCommand";
import { StopCommand } from "./stopCommand";
import { UploadPlayCommand } from "./uploadPlayCommand";

export async function registerCommands(client: Client) {
  const commands = [
    PlayCommand.data.toJSON(),
    UploadPlayCommand.data.toJSON(),
    SkipCommand.data.toJSON(),
    StopCommand.data.toJSON(),
    QueueCommand.data.toJSON(),
    RepeatCommand.data.toJSON(),
    AdminCommands.data.toJSON(),
  ];

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
