"use client";

export default function DialogPage() {
  return (
    <main className="simple-page">
      <h1>決策對話</h1>
      <p>後續將支援以圖譜 + RAG 生成影子決策模擬。</p>

      <div className="chat-box">
        <div className="message ai">請輸入你的問題，例如：為什麼這根鋼樑的安裝方式不同？</div>
      </div>

      <input placeholder="輸入問題..." />
    </main>
  );
}
