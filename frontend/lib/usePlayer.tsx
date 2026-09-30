"use client";
import { createContext, useContext, useState } from "react";
import type { Song } from "@/lib/api";

interface PlayerCtx {
  currentTrack: Song | null;
  isPlaying: boolean;
  play: (song: Song) => void;
  togglePlay: () => void;
  stop: () => void;
  progress: number;
}

const Ctx = createContext<PlayerCtx>({
  currentTrack: null, isPlaying: false,
  play: () => {}, togglePlay: () => {}, stop: () => {}, progress: 0,
});

export function PlayerProvider({ children }: { children: React.ReactNode }) {
  const [currentTrack, setCurrentTrack] = useState<Song | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);

  const play = (song: Song) => {
    setCurrentTrack(song);
    setIsPlaying(true);
    setProgress(0);
  };

  const togglePlay = () => setIsPlaying((p) => !p);
  const stop = () => { setCurrentTrack(null); setIsPlaying(false); setProgress(0); };

  return (
    <Ctx.Provider value={{ currentTrack, isPlaying, play, togglePlay, stop, progress }}>
      {children}
    </Ctx.Provider>
  );
}

export const usePlayer = () => useContext(Ctx);
