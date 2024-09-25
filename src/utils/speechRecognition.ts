import { EndBehaviorType, joinVoiceChannel } from "@discordjs/voice";
import { Leopard } from "@picovoice/leopard-node";
import { Porcupine } from "@picovoice/porcupine-node";
import { Client, VoiceState } from "discord.js";
import * as path from "path";
import { config } from "../config";

console.log("Using Picovoice API Key:", config.picovoiceApiKey); // Log the key before using it

export function speechRecognitionHandler(client: Client) {
  client.on(
    "voiceStateUpdate",
    (oldState: VoiceState, newState: VoiceState) => {
      if (newState.channelId && !oldState.channelId) {
        // User joined a voice channel
        const connection = joinVoiceChannel({
          channelId: newState.channelId,
          guildId: newState.guild.id,
          adapterCreator: newState.guild.voiceAdapterCreator,
        });
        const receiver = connection.receiver;

        receiver.speaking.on("start", (userId) => {
          const user = client.users.cache.get(userId);
          if (user) {
            const audioStream = receiver.subscribe(userId, {
              end: {
                behavior: EndBehaviorType.AfterSilence,
                duration: 1000,
              },
            });

            const chunks: Buffer[] = [];

            audioStream.on("data", (data: Buffer) => {
              chunks.push(data);
            });

            audioStream.on("end", async () => {
              const audioBuffer = Buffer.concat(chunks);

              if (detectWakeWord(audioBuffer)) {
                const transcript = await transcribeAudio(audioBuffer);
                console.log(
                  `Recognized speech from ${user.username}: ${transcript}`
                );
                // Process commands based on recognized text
              }
            });
          }
        });
      }
    }
  );
}

// Path to the custom wake word file in the root directory
const customKeywordPath = path.join(
  __dirname,
  "../../Hey-Jiggy-Bot_en_windows_v3_0_0.ppn"
);

console.log("Custom keyword path:", customKeywordPath); // Add this line to verify the file path

const porcupine = new Porcupine(
  config.picovoiceApiKey,
  [customKeywordPath], // Path to the custom keyword file in the root directory
  [0.5] // Sensitivity
);
const leopard = new Leopard(config.picovoiceApiKey);

function detectWakeWord(audioBuffer: Buffer): boolean {
  const pcm = new Int16Array(
    audioBuffer.buffer,
    audioBuffer.byteOffset,
    audioBuffer.length / 2
  );
  const keywordIndex = porcupine.process(pcm);
  return keywordIndex >= 0;
}

async function transcribeAudio(audioBuffer: Buffer): Promise<string> {
  const pcm = new Int16Array(
    audioBuffer.buffer,
    audioBuffer.byteOffset,
    audioBuffer.length / 2
  );
  const result = await leopard.process(pcm);
  return result.transcript;
}
