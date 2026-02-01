"use client"; // 確保這個文件是客戶端組件

import "../styles/home.css";
import Navbar from "../components/Navbar";
import "../i18n"; // 確保 i18n 在應用啟動時初始化

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
