"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

export type ThemeAccent = "orange" | "violet" | "cyan" | "emerald" | "crimson";
export type VisualTheme = "classic" | "3d";
export type MotionPreference = "full" | "reduced";

interface ThemeContextType {
  theme: ThemeAccent;
  setTheme: (theme: ThemeAccent) => void;
  themes: { id: ThemeAccent; name: string; color: string; glow: string }[];
  visualTheme: VisualTheme;
  setVisualTheme: (visualTheme: VisualTheme) => void;
  motion: MotionPreference;
  setMotion: (motion: MotionPreference) => void;
}

const THEME_OPTIONS: { id: ThemeAccent; name: string; color: string; glow: string }[] = [
  { id: "orange", name: "Amber Blaze", color: "#f58220", glow: "rgba(245, 130, 32, 0.25)" },
  { id: "violet", name: "Electric Violet", color: "#a855f7", glow: "rgba(168, 85, 247, 0.25)" },
  { id: "cyan", name: "Cyber Cyan", color: "#06b6d4", glow: "rgba(6, 182, 212, 0.25)" },
  { id: "emerald", name: "Neon Emerald", color: "#10b981", glow: "rgba(16, 185, 129, 0.25)" },
  { id: "crimson", name: "Crimson Pulse", color: "#f43f5e", glow: "rgba(244, 63, 94, 0.25)" },
];

const ThemeContext = createContext<ThemeContextType>({
  theme: "orange",
  setTheme: () => {},
  themes: THEME_OPTIONS,
  visualTheme: "classic",
  setVisualTheme: () => {},
  motion: "full",
  setMotion: () => {},
});

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<ThemeAccent>("orange");
  const [visualTheme, setVisualThemeState] = useState<VisualTheme>("classic");
  const [motion, setMotionState] = useState<MotionPreference>("full");

  useEffect(() => {
    // Accent Theme
    const savedAccent = localStorage.getItem("ts_theme_accent") as ThemeAccent;
    if (savedAccent && THEME_OPTIONS.some((t) => t.id === savedAccent)) {
      setThemeState(savedAccent);
      document.documentElement.setAttribute("data-theme", savedAccent);
    } else {
      document.documentElement.setAttribute("data-theme", "orange");
    }

    // Visual Theme (Classic vs 3D)
    const savedVisual = localStorage.getItem("ts_visual_theme") as VisualTheme;
    if (savedVisual === "3d" || savedVisual === "classic") {
      setVisualThemeState(savedVisual);
      document.documentElement.setAttribute("data-visual-theme", savedVisual);
    } else {
      setVisualThemeState("classic");
      document.documentElement.setAttribute("data-visual-theme", "classic");
    }

    // Motion Preference
    const savedMotion = localStorage.getItem("ts_motion_pref") as MotionPreference;
    if (savedMotion === "reduced" || savedMotion === "full") {
      setMotionState(savedMotion);
      document.documentElement.setAttribute("data-motion", savedMotion);
    } else {
      const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const initialMotion = prefersReduced ? "reduced" : "full";
      setMotionState(initialMotion);
      document.documentElement.setAttribute("data-motion", initialMotion);
    }
  }, []);

  const setTheme = (newTheme: ThemeAccent) => {
    setThemeState(newTheme);
    localStorage.setItem("ts_theme_accent", newTheme);
    document.documentElement.setAttribute("data-theme", newTheme);
  };

  const setVisualTheme = (newVisual: VisualTheme) => {
    setVisualThemeState(newVisual);
    localStorage.setItem("ts_visual_theme", newVisual);
    document.documentElement.setAttribute("data-visual-theme", newVisual);
  };

  const setMotion = (newMotion: MotionPreference) => {
    setMotionState(newMotion);
    localStorage.setItem("ts_motion_pref", newMotion);
    document.documentElement.setAttribute("data-motion", newMotion);
  };

  return (
    <ThemeContext.Provider
      value={{
        theme,
        setTheme,
        themes: THEME_OPTIONS,
        visualTheme,
        setVisualTheme,
        motion,
        setMotion,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);
