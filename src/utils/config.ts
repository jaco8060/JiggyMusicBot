// src/utils/config.ts

import fs from "fs";
import path from "path";
import { createLogger, format, transports } from "winston";

export function setupLogging() {
  createLogger({
    level: "info",
    format: format.combine(format.timestamp(), format.simple()),
    transports: [new transports.Console()],
  });
}

export function ensureAudioFolder() {
  const audioFolder = path.join(__dirname, "..", "..", "audio_files");
  if (!fs.existsSync(audioFolder)) {
    fs.mkdirSync(audioFolder);
  }

  // Clean up the folder at startup
  fs.readdirSync(audioFolder).forEach((file) => {
    const filePath = path.join(audioFolder, file);
    fs.unlinkSync(filePath);
  });
}
