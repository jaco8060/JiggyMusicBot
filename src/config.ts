import * as dotenv from "dotenv";
dotenv.config({ path: "../.env" }); // Ensure the path is correctly pointing to your .env file

export const config = {
  token: process.env.DISCORD_BOT_TOKEN as string,
  youtubeApiKey: process.env.YOUTUBE_API_KEY as string,
  picovoiceApiKey: process.env.PICOVOICE_API_KEY as string,
};

console.log("Config loaded:");
console.log("DISCORD_BOT_TOKEN:", config.token);
console.log("YOUTUBE_API_KEY:", config.youtubeApiKey);
console.log("PICOVOICE_API_KEY:", config.picovoiceApiKey);

if (!config.token || !config.youtubeApiKey || !config.picovoiceApiKey) {
  console.error("Error: Missing required environment variables.");
  process.exit(1);
}
