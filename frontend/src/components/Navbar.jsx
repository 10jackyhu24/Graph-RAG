"use client";

import { useTranslation } from "react-i18next";
import Link from "next/link";

export default function Navbar() {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <nav className="navbar">
      <div className="logo">GraphRAG Studio</div>

      <div className="nav-links">
        <Link href="/">{t("home")}</Link>
        <Link href="/workspace">{t("workspace")}</Link>
        <Link href="/meeting">{t("meetingMode")}</Link>
      </div>

      <div className="nav-actions">
        <button className="btn ghost" onClick={() => changeLanguage("en")}>EN</button>
        <button className="btn ghost" onClick={() => changeLanguage("zh")}>中文</button>
        <button className="btn ghost">{t("lightMode")}</button>
        <button className="btn primary">{t("login")}</button>
      </div>
    </nav>
  );
}
