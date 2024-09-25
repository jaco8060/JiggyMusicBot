// src/env.d.ts
declare namespace NodeJS {
  interface ProcessEnv {
    DISCORD_BOT_TOKEN: string;
    YOUTUBE_API_KEY: string;
    PICOVOICE_API_KEY: string;
  }
}
