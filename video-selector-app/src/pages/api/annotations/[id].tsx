import {
  AnnotationGetResponse,
  AnnotationPutRequestBody,
  AnnotationPutResponse,
} from "@/shared/types";
import { NextApiRequest, NextApiResponse } from "next";
import { promises as fs } from "fs";
import path from "path";

// Define the VideoMetadata structure

// Mock database

// GET function to retrieve VideoMetadata by id
export async function getAnnotation(req: NextApiRequest, res: NextApiResponse) {
  const { id } = req.query;
  // find a file of the form <id>.annotation.json in the videos directory
  // and return the contents as JSON
  const videoDirectory = path.join(process.cwd(), "../ungitable");
  const annotationPath = path.join(videoDirectory, `${id}.annotation.json`);
  try {
    const annotation = await fs.readFile(annotationPath, "utf-8");
    res.status(200).json(JSON.parse(annotation));
  } catch (error) {
    console.error(error);
    res.status(404).json({ message: `${error}` });
  }
}

// PUT function to update VideoMetadata by id
export async function putVideoMetadata(
  req: NextApiRequest,
  res: NextApiResponse<AnnotationPutResponse>
) {
  const { id } = req.query;
  // write a file of the form <id>.annotation.json in the videos directory
  // with the contents of the body as JSON
  const videoDirectory = path.join(process.cwd(), "../ungitable");
  const annotationPath = path.join(videoDirectory, `${id}.annotation.json`);
  try {
    await fs.writeFile(
      annotationPath,
      JSON.stringify(req.body as AnnotationPutRequestBody)
    );
    res.status(200).json({ message: "Metadata updated successfully" });
  } catch (error) {
    res.status(500).json({ message: `${error}` });
  }
}

// API route handler
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<AnnotationGetResponse | AnnotationPutResponse>
) {
  if (req.method === "GET") {
    await getAnnotation(req, res);
  } else if (req.method === "PUT") {
    await putVideoMetadata(req, res);
  } else {
    res.setHeader("Allow", ["GET", "PUT"]);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
