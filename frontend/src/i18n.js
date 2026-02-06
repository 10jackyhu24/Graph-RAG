"use client";

import i18n from "i18next";
import { initReactI18next } from "react-i18next";

const resources = {
  en: {
    translation: {
      home: "Home",
      workspace: "Workspace",
      meetingMode: "Meeting",
      decisionDialog: "Decision Dialog",
      lightMode: "Light",
      login: "Login",
    },
  },
  zh: {
    translation: {
      home: "首頁",
      workspace: "工作台",
      meetingMode: "會議模式",
      decisionDialog: "決策對話",
      lightMode: "亮色",
      login: "登入",
    },
  },
};

i18n.use(initReactI18next).init({
  resources,
  lng: "zh",
  fallbackLng: "en",
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
