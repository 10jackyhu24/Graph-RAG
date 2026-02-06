"use client";

import { Space_Grotesk, Unbounded, IBM_Plex_Mono, Noto_Sans_TC } from "next/font/google";
import "../styles/home.css";
import Navbar from "../components/Navbar";
import "../i18n";
import "@/styles/globals.css";
import "@/styles/theme.css";
import "@/styles/layout.css";
import "@/styles/components.css";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "600", "700"],
});

const unbounded = Unbounded({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["400", "500", "600", "700"],
});

const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["400", "500", "600"],
});

const notoSansTc = Noto_Sans_TC({
  subsets: ["latin"],
  variable: "--font-zh",
  weight: ["400", "500", "700"],
});

export default function RootLayout({ children }) {
  return (
    <html lang="zh-Hant">
      <body className={`${spaceGrotesk.variable} ${unbounded.variable} ${plexMono.variable} ${notoSansTc.variable}`}>
        <Navbar />
        {children}
      </body>
    </html>
  );
}
