// src/utils/audio.ts

import {
  AudioPlayer,
  AudioPlayerStatus,
  createAudioPlayer,
  createAudioResource,
  joinVoiceChannel,
  VoiceConnection,
} from "@discordjs/voice";
import { Guild, VoiceBasedChannel } from "discord.js";
import fs from "fs";
import path from "path";
import { getYouTubeStream } from "./youtube";

interface Song {
  url: string;
  title: string;
  type: "url" | "file";
  filePath?: string;
}

export class AudioManager {
  private static instances: Map<string, AudioManager> = new Map();

  private guildId: string;
  private queue: Song[] = [];
  private currentSong: Song | null = null;
  private repeatMode = false;
  private voiceConnection: VoiceConnection | null = null;
  private audioPlayer: AudioPlayer;

  private constructor(guildId: string) {
    this.guildId = guildId;
    this.audioPlayer = createAudioPlayer();

    this.audioPlayer.on(AudioPlayerStatus.Idle, () => {
      this.playNext();
    });
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
        adapterCreator: voiceChannel.guild.voiceAdapterCreator,
      });
      this.voiceConnection.subscribe(this.audioPlayer);
    }
  }

  async addToQueue(url: string): Promise<string> {
    const info = await getYouTubeStream(url);
    const song: Song = { url, title: info.title, type: "url" };
    this.queue.push(song);
    return song.title;
  }

  isPlaying(): boolean {
    return this.audioPlayer.state.status === AudioPlayerStatus.Playing;
  }

  async playNext() {
    if (this.queue.length === 0) {
      this.currentSong = null;
      // Optionally disconnect after some time
      return;
    }

    this.currentSong = this.queue.shift()!;
    const streamInfo = await getYouTubeStream(this.currentSong.url);
    const resource = createAudioResource(streamInfo.stream, {
      inputType: streamInfo.type,
    });
    this.audioPlayer.play(resource);
  }

  // Implement other methods like skip, stop, toggleRepeat
}
