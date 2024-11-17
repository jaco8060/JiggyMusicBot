// src/utils/audio.ts

import {
  AudioPlayer,
  AudioPlayerStatus,
  createAudioPlayer,
  createAudioResource,
  DiscordGatewayAdapterCreator,
  entersState,
  joinVoiceChannel,
  StreamType,
  VoiceConnection,
  VoiceConnectionStatus,
} from "@discordjs/voice";
import { VoiceBasedChannel } from "discord.js";
import fs from "fs";
import fetch from "node-fetch"; // Works with node-fetch v2
import path from "path";
import { Readable } from "stream";
import { getYTInfo } from "./youtube";

interface Song {
  url?: string; // Make 'url' optional
  title: string;
  type: "url" | "file";
  stream?: Readable;
  filePath?: string;
}
export class AudioManager {
  private static instances: Map<string, AudioManager> = new Map();

  private guildId: string;
  private queue: Song[] = [];
  private originalQueue: Song[] = [];
  private currentSong: Song | null = null;
  private repeatMode = false;
  private voiceConnection: VoiceConnection | null = null;
  private audioPlayer: AudioPlayer;
  private disconnectTimer: NodeJS.Timeout | null = null;

  private constructor(guildId: string) {
    this.guildId = guildId;
    this.audioPlayer = createAudioPlayer();

    this.audioPlayer.on(AudioPlayerStatus.Idle, () => {
      this.playNext();
    });
  }
  getRepeatMode(): boolean {
    return this.repeatMode;
  }
  static getOrCreate(guildId: string): AudioManager {
    if (!this.instances.has(guildId)) {
      this.instances.set(guildId, new AudioManager(guildId));
    }
    return this.instances.get(guildId)!;
  }

  async connect(voiceChannel: VoiceBasedChannel) {
    if (
      !this.voiceConnection ||
      this.voiceConnection.state.status === "disconnected"
    ) {
      this.voiceConnection = joinVoiceChannel({
        channelId: voiceChannel.id,
        guildId: this.guildId,
        adapterCreator: voiceChannel.guild
          .voiceAdapterCreator as DiscordGatewayAdapterCreator,
      });

      this.voiceConnection.subscribe(this.audioPlayer);

      try {
        await entersState(
          this.voiceConnection,
          VoiceConnectionStatus.Ready,
          30_000
        );
      } catch (error) {
        this.voiceConnection.destroy();
        throw error;
      }
    }
  }

  async addToQueue(url: string): Promise<string> {
    const info = await getYTInfo(url);
    const song: Song = {
      url,
      title: info.title,
      type: "url",
      stream: info.stream,
    };
    this.queue.push(song);

    if (this.repeatMode) {
      this.originalQueue.push(song);
    }

    return song.title;
  }

  addFileToQueue(filePath: string, title: string) {
    const song: Song = { filePath, title, type: "file" };
    this.queue.push(song);

    if (this.repeatMode) {
      this.originalQueue.push(song);
    }
  }

  async saveUploadedFile(attachment: any): Promise<string> {
    const audioFolder = path.join(__dirname, "..", "..", "audio_files");
    const filePath = path.join(audioFolder, attachment.name);

    const response = await fetch(attachment.url);
    const arrayBuffer = await response.arrayBuffer();
    fs.writeFileSync(filePath, Buffer.from(arrayBuffer));

    return filePath;
  }

  isPlaying(): boolean {
    return this.audioPlayer.state.status === AudioPlayerStatus.Playing;
  }

  getQueue(): Song[] {
    return this.queue;
  }

  getCurrentSong(): Song | null {
    return this.currentSong;
  }

  setRepeatMode(mode: boolean) {
    this.repeatMode = mode;
    if (mode) {
      this.originalQueue = [];
      if (this.currentSong) {
        this.originalQueue.push(this.currentSong);
      }
      this.originalQueue.push(...this.queue);
    } else {
      this.originalQueue = [];
    }
  }

  skip() {
    this.audioPlayer.stop();
  }

  stop() {
    this.queue = [];
    this.originalQueue = [];
    this.repeatMode = false;
    this.currentSong = null;
    this.audioPlayer.stop();
    if (this.voiceConnection) {
      this.voiceConnection.disconnect();
      this.voiceConnection = null;
    }
    this.cleanupAudioFiles();
  }

  async playNext() {
    if (this.disconnectTimer) {
      clearTimeout(this.disconnectTimer);
      this.disconnectTimer = null;
    }

    if (this.queue.length === 0) {
      if (this.repeatMode && this.originalQueue.length > 0) {
        this.queue = [...this.originalQueue];
      } else {
        this.currentSong = null;
        this.disconnectTimer = setTimeout(() => {
          this.voiceConnection?.disconnect();
          this.cleanupAudioFiles();
        }, 300_000); // 5 minutes
        return;
      }
    }

    this.currentSong = this.queue.shift()!;

    if (this.currentSong.type === "url") {
      const stream = this.currentSong.stream!;
      const resource = createAudioResource(stream, {
        inputType: StreamType.Opus, // Change to the appropriate type
      });
      this.audioPlayer.play(resource);
    } else if (this.currentSong.type === "file") {
      const filePath = this.currentSong.filePath!;
      const stream = fs.createReadStream(filePath);
      const resource = createAudioResource(stream, {
        inputType: StreamType.Arbitrary,
      });
      this.audioPlayer.play(resource);
    } else {
      return;
    }
  }

  private cleanupAudioFiles() {
    const audioFolder = path.join(__dirname, "..", "..", "audio_files");
    fs.readdirSync(audioFolder).forEach((file) => {
      const filePath = path.join(audioFolder, file);
      fs.unlinkSync(filePath);
    });
  }
}
