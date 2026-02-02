This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.js`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

```
backend/app/
├─ api/v1/
│  ├─ sources.py            # 上傳各種來源
│  ├─ pipelines.py          # 啟動流程
│  └─ artifacts.py          # 下載結果
│
├─ services/
│  ├─ pipeline_service.py   ⭐ 流程主控（最重要）
│  ├─ quota_service.py
│  └─ payment_service.py
│
├─ sources/                 # 各種「輸入」
│  ├─ document_source.py    # PDF / DOCX
│  ├─ audio_source.py       # MP3 / WAV
│  └─ text_source.py        # 直接貼文字
│
├─ pipelines/               # 可組合流程
│  ├─ base.py               # Pipeline 抽象
│  ├─ doc_summary.py        # 文件摘要
│  ├─ meeting_minutes.py   # 會議模式 ⭐
│
├─ transformers/            # 單一職責轉換
│  ├─ speech_to_text.py     # 音檔 → 文字
│  ├─ text_cleaner.py
│  ├─ text_splitter.py
│  ├─ summarizer.py         # LLM
│
├─ exporters/               # 輸出
│  ├─ pdf_exporter.py
│  └─ docx_exporter.py
│
├─ models/
│  ├─ job.py                # 任務狀態
│  └─ artifact.py
│
└─ utils/
```