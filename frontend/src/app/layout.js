"use client"; // 確保這個文件是客戶端組件

import "../styles/home.css";
import Navbar from "../components/Navbar";
import "../i18n";
import "@/styles/globals.css"
import "@/styles/theme.css"
import "@/styles/layout.css"
import "@/styles/components.css"

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        {children}
      </body>
    </html>
  );
}
