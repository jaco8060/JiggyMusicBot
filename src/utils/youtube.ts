import { google } from "googleapis";
import { Readable } from "stream";
import youtubedl from "youtube-dl-exec";
import { config } from "../config";
import { Track } from "../utils/audioPlayer";

const youtube = google.youtube({
  version: "v3",
  auth: config.youtubeApiKey,
});

export interface Video {
  title: string;
  url: string;
}

export async function youtubeSearch(query: string): Promise<Video[]> {
  const response = await youtube.search.list({
    part: ["snippet"],
    q: query,
    type: ["video"],
    maxResults: 5,
  });

  const videos =
    response.data.items?.map((item) => ({
      title: item.snippet?.title || "No Title",
      url: `https://www.youtube.com/watch?v=${item.id?.videoId}`,
    })) || [];

  return videos;
}

export async function getYTInfo(url: string): Promise<Track> {
  const info: any = await youtubedl(url, {
    dumpSingleJson: true,
    noWarnings: true,
    preferFreeFormats: true,
    youtubeSkipDashManifest: true,
  });

  const subprocess = youtubedl.exec(url, {
    output: "-",
    format: "bestaudio",
    audioFormat: "opus",
  });

  const stream = subprocess.stdout as Readable;

  return {
    title: info.title,
    url: url,
    duration: info.duration,
    stream,
  };
}
