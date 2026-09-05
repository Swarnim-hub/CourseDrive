"use client";

import React, { useRef, useState, useEffect } from "react";
import ReactPlayer from "react-player";

export function VideoPlayer({
  url,
  onComplete,
  onWatchProgress,
}: {
  url?: string;
  onComplete?: () => void;
  onWatchProgress?: (seconds: number) => void;
  lastPosition?: number;
}) {
  const playerRef = useRef<ReactPlayer>(null);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return <div className="aspect-video w-full bg-slate-900 animate-pulse rounded-xl" />;
  }

  return (
    <div className="relative aspect-video w-full bg-black rounded-xl overflow-hidden group">
      <ReactPlayer
        ref={playerRef}
        url={url || "https://www.w3schools.com/html/mov_bbs.mp4"}
        width="100%"
        height="100%"
        controls={true}
        onEnded={onComplete}
        onProgress={(state) => {
          onWatchProgress?.(state.playedSeconds);
        }}
      />
    </div>
  );
}
