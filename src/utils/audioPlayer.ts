import {
  AudioPlayer,
  AudioPlayerStatus,
  createAudioPlayer,
  createAudioResource,
  StreamType,
  VoiceConnection,
} from "@discordjs/voice";
import { Readable } from "stream";

export interface Track {
  title: string;
  url: string;
  duration?: string;
  stream?: Readable;
  isLocalFile?: boolean;
}

export class MusicSubscription {
  public voiceConnection!: VoiceConnection;
  public audioPlayer: AudioPlayer;
  public queue: Track[];
  private static subscriptions: Map<string, MusicSubscription> = new Map();

  private constructor() {
    this.audioPlayer = createAudioPlayer();
    this.queue = [];

    this.audioPlayer.on(AudioPlayerStatus.Idle, () => {
      this.playNext();
    });
  }

  public static get(guildId: string): MusicSubscription | undefined {
    return this.subscriptions.get(guildId);
  }

  public static getOrCreate(guildId: string): MusicSubscription {
    let subscription = this.subscriptions.get(guildId);
    if (!subscription) {
      subscription = new MusicSubscription();
      this.subscriptions.set(guildId, subscription);
    }
    return subscription;
  }

  public static delete(guildId: string) {
    this.subscriptions.delete(guildId);
  }

  public enqueue(track: Track) {
    this.queue.push(track);
    if (this.audioPlayer.state.status !== AudioPlayerStatus.Playing) {
      this.playNext();
    }
  }

  private async playNext() {
    const nextTrack = this.queue.shift();
    if (nextTrack) {
      let resource;
      if (nextTrack.isLocalFile) {
        // For local files or URLs
        resource = createAudioResource(nextTrack.url, {
          inputType: StreamType.Arbitrary,
        });
      } else if (nextTrack.stream) {
        // For streams (YouTube)
        resource = createAudioResource(nextTrack.stream, {
          inputType: StreamType.Arbitrary,
        });
      } else {
        console.error("No stream available for track:", nextTrack.title);
        this.playNext();
        return;
      }
      this.audioPlayer.play(resource);
      this.voiceConnection.subscribe(this.audioPlayer);
    } else {
      // No more tracks, disconnect
      this.voiceConnection.disconnect();
    }
  }
}
