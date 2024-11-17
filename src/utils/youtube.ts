// src/utils/youtube.ts

import { google } from "googleapis";
import { Readable } from "stream";
import youtubedl from "youtube-dl-exec";

const youtube = google.youtube({
  version: "v3",
  auth: process.env.YOUTUBE_API_KEY,
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

export async function getYTInfo(
  url: string
): Promise<{ title: string; stream: Readable }> {
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
    quiet: true,
  });

  const stream = subprocess.stdout as Readable;

  return {
    title: info.title,
    stream,
  };
}
