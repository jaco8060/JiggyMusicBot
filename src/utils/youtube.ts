// src/utils/youtube.ts

import { google } from "googleapis";
import { Readable } from "stream";
import ytdl from "ytdl-core";

const youtube = google.youtube("v3");

export async function searchYouTube(
  query: string
): Promise<Array<{ url: string; title: string }>> {
  const apiKey = process.env.YOUTUBE_API_KEY;
  if (!apiKey) {
    throw new Error("YOUTUBE_API_KEY is not set.");
  }

  const res = await youtube.search.list({
    part: ["snippet"],
    q: query,
    maxResults: 5,
    key: apiKey,
  });

  return (
    res.data.items?.map((item) => ({
      url: `https://www.youtube.com/watch?v=${item.id?.videoId}`,
      title: item.snippet?.title || "Unknown Title",
    })) || []
  );
}

export async function getYouTubeStream(
  url: string
): Promise<{ stream: Readable; title: string; type: any }> {
  const info = await ytdl.getInfo(url);
  const stream = ytdl.downloadFromInfo(info, { filter: "audioonly" });
  return { stream, title: info.videoDetails.title, type: undefined };
}
