import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/AppShell";
import { AuthProvider } from "@/lib/useAuth";
import { PlayerProvider } from "@/lib/usePlayer";

export const metadata: Metadata = {
  title: "TuneSphere — AI Music Recommendation",
  description: "Discover, explore, and get personalized music recommendations powered by AI.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <PlayerProvider>
            <AppShell>{children}</AppShell>
          </PlayerProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
