"use client";
import { Annotation, VideoMetadata, VideosListResponse } from "@/shared/types";
import { MouseEventHandler, useRef, useState } from "react";
import useSWR from "swr";

export default function Home() {
  const [selectedVideo, setSelectedVideo] = useState<VideoMetadata | null>(
    null
  );
  const videosListResponse = useSWR<VideosListResponse>("/api/videos", fetcher);
  const activeAnnotationResponse = useSWR<Annotation>(
    `/api/annotations/${selectedVideo?.id ?? ""}`,
    fetcher
  );
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const videoRef = useRef<HTMLVideoElement>(null);
  const [currentTime, setCurrentTime] = useState(0);

  const updateActiveAnnotation = async (annotation: Annotation) => {
    if (!selectedVideo) {
      return;
    }
    await fetch(`/api/annotations/${selectedVideo.id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(annotation),
    });
    activeAnnotationResponse.mutate(annotation);
  };

  const handleTimeUpdate = () => {
    // console.log("Time Update", videoRef.current?.currentTime);
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleScrub = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log("Scrub", event.target.value);
    if (videoRef.current) {
      videoRef.current.currentTime = parseFloat(event.target.value);
    }
  };

  const handleFrameNavigation = (
    ev: React.MouseEvent<HTMLButtonElement, MouseEvent>,
    frames: number
  ) => {
    ev.stopPropagation();
    ev.preventDefault();
    if (videoRef.current) {
      const frameDuration = 1 / 30; // Assuming 30 FPS
      console.log(
        "Frame Navigation",
        frames,
        frames * frameDuration,
        videoRef.current?.currentTime
      );
      videoRef.current.currentTime =
        videoRef.current.currentTime + frames * frameDuration;
    }
  };

  type BasesMetadata = Pick<Annotation, "homePos" | "firstPos">;

  const [whichBase, setWhichBase] = useState<keyof BasesMetadata>("homePos");

  const handleMouseMove: MouseEventHandler<HTMLDivElement> = (ev) => {
    if (!videoRef.current) {
      return;
    }
    const rect = videoRef.current.getBoundingClientRect();
    const x = ev.clientX - rect.left;
    const y = ev.clientY - rect.top;
    if (0 <= x && x <= 1280 && 0 <= y && y <= 720) {
      setMousePosition({ x, y });
    }
  };

  const handleMouseClick: MouseEventHandler<HTMLDivElement> = (ev) => {
    if (!videoRef.current) {
      return;
    }
    ev.stopPropagation();
    ev.preventDefault();
    console.log("Mouse Clicked", mousePosition, whichBase);
    if (!selectedVideo) {
      return;
    }
    const baseAnnotation = activeAnnotationResponse.data ?? {
      homePos: [0, 0],
      firstPos: [0, 0],
    };

    if (whichBase === "homePos") {
      updateActiveAnnotation({
        ...baseAnnotation,
        homePos: [mousePosition.x, mousePosition.y],
      });
    } else {
      updateActiveAnnotation({
        ...baseAnnotation,
        firstPos: [mousePosition.x, mousePosition.y],
      });
    }
    setWhichBase((prev) => (prev === "homePos" ? "firstPos" : "homePos"));
  };

  const handleSetContactTime: MouseEventHandler<HTMLButtonElement> = (ev) => {
    ev.stopPropagation();
    ev.preventDefault();
    if (!selectedVideo) {
      return;
    }
    const baseAnnotation = activeAnnotationResponse.data ?? {
      homePos: [0, 0],
      firstPos: [0, 0],
    };
    const contactTime = videoRef.current?.currentTime ?? 0;
    updateActiveAnnotation({ ...baseAnnotation, contactTime });
  };

  return (
    <div className="flex flex-row">
      <div className="flex flex-col p-4">
        <h1 className="text-2xl">Select a Video</h1>
        <ul>
          {videosListResponse.data?.videos.map((video) => (
            <li key={video.id} className="w-full">
              <button
                className={`px-2 py-1 hover:bg-gray-600 w-full text-left text-sm ${
                  video.id === selectedVideo?.id ? "bg-gray-800" : ""
                }`}
                onClick={() => setSelectedVideo(video)}
              >
                {video.title}
              </button>
            </li>
          ))}
        </ul>
      </div>
      {selectedVideo && (
        <div
          style={{ position: "relative", width: "1280px", height: "720px" }}
          onMouseMove={handleMouseMove}
          onClick={handleMouseClick}
        >
          <div
            style={{
              width: "100%",
              padding: "10px",
              backgroundColor: "rgba(0, 0, 0, 0.5)",
              color: "white",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <button
              className="px-2"
              onClick={(ev) => handleFrameNavigation(ev, -30)}
            >
              &lt;&lt;&lt;
            </button>
            <button
              className="px-2"
              onClick={(ev) => handleFrameNavigation(ev, -10)}
            >
              &lt;&lt;
            </button>
            <button
              className="px-2"
              onClick={(ev) => handleFrameNavigation(ev, -1)}
            >
              &lt;
            </button>
            <button
              className="px-2"
              onClick={() => {
                if (videoRef.current) {
                  if (videoRef.current.paused) {
                    videoRef.current.play();
                  } else {
                    videoRef.current.pause();
                  }
                }
              }}
            >
              {videoRef.current?.paused ? "Play" : "Pause"}
            </button>
            <div className="px-2">{currentTime.toFixed(2)}s</div>
            <button
              className="px-2"
              onClick={(ev) => handleFrameNavigation(ev, 1)}
            >
              &gt;
            </button>
            <button
              className="px-2"
              onClick={(ev) => handleFrameNavigation(ev, 10)}
            >
              &gt;&gt;
            </button>
            <button
              className="px-2"
              onClick={(ev) => handleFrameNavigation(ev, 30)}
            >
              &gt;&gt;&gt;
            </button>
            <input
              type="range"
              min="0"
              max={videoRef.current?.duration || 0}
              step="0.01"
              value={currentTime}
              onChange={handleScrub}
              style={{ flex: 1, margin: "0 10px" }}
            />
          </div>
          <video
            ref={videoRef}
            src={selectedVideo.src}
            width="1280"
            height="720"
            controls={false}
            crossOrigin="anonymous"
            style={{ display: "block", pointerEvents: "none" }}
            onLoadedMetadata={() => {
              if (videoRef.current) {
                // videoRef.current.muted = true;
                console.log("metadata loaded");

                // videoRef.current.currentTime = 0;
              }
            }}
            onError={(ev) => console.error(ev)}
            onTimeUpdate={handleTimeUpdate}
          />
          <div
            style={{
              width: "100%",
              padding: "10px",
              backgroundColor: "rgba(0, 0, 0, 0.5)",
              color: "white",
            }}
          >
            <div>
              Mouse Position: {mousePosition.x}, {mousePosition.y}
            </div>
            {activeAnnotationResponse.data &&
            !activeAnnotationResponse.error ? (
              <>
                <div>
                  HOME: {activeAnnotationResponse.data.homePos[0]},{" "}
                  {activeAnnotationResponse.data.homePos[1]}
                </div>
                <div>
                  FIRST: {activeAnnotationResponse.data.firstPos[0]},{" "}
                  {activeAnnotationResponse.data.firstPos[1]}
                </div>
                <div>
                  <button
                    className="px-2 py-1 hover:bg-gray-600 w-full text-left text-sm border-gray-800 border-2"
                    onClick={handleSetContactTime}
                  >
                    Set Contact Time -{" "}
                    {`${(
                      activeAnnotationResponse.data.contactTime ?? 0.0
                    ).toFixed(2)} => ${currentTime.toFixed(2)}s`}
                  </button>
                </div>
              </>
            ) : (
              <div>No anno data</div>
            )}{" "}
          </div>
        </div>
      )}
    </div>
  );
}

const fetcher = async (url: string) => {
  const res = await fetch(url);

  // If the status is not OK, throw an error to trigger SWR's error handling
  if (!res.ok) {
    const error = new FetcherError(
      "An error occurred while fetching the data."
    );
    error.info = await res.json(); // Attach response body to error
    error.status = res.status;
    throw error;
  }

  return res.json(); // Return JSON response if status is OK
};

class FetcherError extends Error {
  status!: number;
  info: unknown;

  constructor(message: string) {
    super(message);
    this.name = "FetcherError";
  }
}
