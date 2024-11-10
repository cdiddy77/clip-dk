import { promises as fs } from "fs";
import { NextApiRequest, NextApiResponse } from "next";
import path from "path";
import { createReadStream } from "fs";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  console.log("Video API called", req.query);
  const { path: filePath } = req.query;
  const videoDirectory = path.join(process.cwd(), "../ungitable");
  const fullPath = path.join(videoDirectory, filePath as string);

  try {
    const fileStat = await fs.stat(fullPath);

    if (fileStat.isFile()) {
      const range = req.headers.range;
      if (!range) {
        res.status(400).send("Requires Range header");
        return;
      }

      const videoSize = fileStat.size;
      const CHUNK_SIZE = 10 ** 6; // 1MB
      const start = Number(range.replace(/\D/g, ""));
      const end = Math.min(start + CHUNK_SIZE, videoSize - 1);

      const contentLength = end - start + 1;
      const headers = {
        "Content-Range": `bytes ${start}-${end}/${videoSize}`,
        "Accept-Ranges": "bytes",
        "Content-Length": contentLength,
        "Content-Type": "video/mp4",
      };

      res.writeHead(206, headers);

      const videoStream = createReadStream(fullPath, { start, end });
      videoStream.pipe(res);
    } else {
      res.status(404).json({ error: "File not found" });
    }
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Internal Server Error" });
  }
}
