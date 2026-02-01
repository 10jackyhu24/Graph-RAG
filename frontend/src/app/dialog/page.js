"use client"

export default function DialogPage() {
  return (
    <main className="simple-page">
      <h1>決策對話</h1>
      <p>針對決策內容與 AI 進行追問與風險分析。</p>

      <div className="chat-box">
        <div className="message ai">你想釐清哪一個決策？</div>
      </div>

      <input placeholder="輸入你的問題…" />
    </main>
  )
}
