"use client";

import i18n from "i18next";
import { initReactI18next } from "react-i18next";

const resources = {
  en: {
    translation: {
      home: "Home",
      workspace: "Workspace",
      meetingMode: "Meeting Mode",
      decisionDialog: "Decision Dialog",
      lightMode: "Light Mode",
      login: "Login",
    },
  },
  zh: {
    translation: {
      home: "首頁",
      workspace: "工作區",
      meetingMode: "會議模式",
      decisionDialog: "決策對話",
      lightMode: "淺色",
      login: "登入",
    },
  },
};

i18n.use(initReactI18next).init({
  resources,
  lng: "en", // 預設語言
  fallbackLng: "en",
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;