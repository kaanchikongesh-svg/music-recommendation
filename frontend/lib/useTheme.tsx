"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

export type ThemeAccent = "orange" | "violet" | "cyan" | "emerald" | "crimson";

interface ThemeContextType {
  theme: ThemeAccent;
  setTheme: (theme: ThemeAccent) => void;
  themes: { id: ThemeAccent; name: string; color: string; glow: string }[];
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
});

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<ThemeAccent>("orange");

  useEffect(() => {
    const saved = localStorage.getItem("ts_theme_accent") as ThemeAccent;
    if (saved && THEME_OPTIONS.some((t) => t.id === saved)) {
      setThemeState(saved);
      document.documentElement.setAttribute("data-theme", saved);
    } else {
      document.documentElement.setAttribute("data-theme", "orange");
    }
  }, []);

  const setTheme = (newTheme: ThemeAccent) => {
    setThemeState(newTheme);
    localStorage.setItem("ts_theme_accent", newTheme);
    document.documentElement.setAttribute("data-theme", newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, themes: THEME_OPTIONS }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);
