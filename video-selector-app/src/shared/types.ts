export interface VideoMetadata {
  id: string;
  title: string;
  src: string;
}

export interface Annotation {
  homePos: [number, number];
  firstPos: [number, number];
  contactTime?: number;
}

export type AnnotationGetResponse = Annotation;
export type AnnotationPutRequestBody = Annotation;
export type AnnotationPutResponse = { message: string };

export interface VideosListResponse {
  videos: VideoMetadata[];
}
