"use client"

import { useTranslation } from "react-i18next"

export default function Navbar() {
    const { t, i18n } = useTranslation();

    const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };
  return (
    <nav className="navbar">
      <div className="logo">VISION IRG</div>

      <div className="nav-links">
        <a>{t("home")}</a>
        <a>{t("workspace")}</a>
        <a>{t("meetingMode")}</a>
        <a>{t("decisionDialog")}</a>
      </div>

      <div className="nav-actions">
        <button onClick={() => changeLanguage("en")}>EN</button>
        <button onClick={() => changeLanguage("zh")}>中文</button>
        <button>淺色</button>
        <button>登入</button>
      </div>
    </nav>
  )
}
