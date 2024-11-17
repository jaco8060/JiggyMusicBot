// src/index.ts

import { config } from "dotenv";
import client from "./bot";

config(); // Load environment variables from .env

const token = process.env.DISCORD_BOT_TOKEN;
if (!token) {
  throw new Error(
    "No Discord bot token found. Please set the DISCORD_BOT_TOKEN environment variable."
  );
}

client.login(token);
