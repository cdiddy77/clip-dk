import { NextApiRequest, NextApiResponse } from "next";
import { promises as fs } from "fs";
import path from "path";
import { VideosListResponse } from "@/shared/types";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<VideosListResponse>
) {
  // get a list of files that have the .mp4 extension
  // in the video directory and return all of the names minus the extension
  // as an array
  const videoDirectory = path.join(process.cwd(), "../ungitable");
  const files = await fs.readdir(videoDirectory);
  console.log("/api/videos: Files", files);
  const videos = files
    .filter((file) => file.endsWith(".mp4"))
    .map((file) => ({
      id: file.replace(".mp4", ""),
      title: file.replace(".mp4", ""),
      src: `/videos/${file}`,
    }));
  res.status(200).json({ videos });
}
