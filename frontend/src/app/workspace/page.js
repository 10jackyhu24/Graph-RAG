"use client";

import { useState } from "react";
import { BASE_URL } from "@/config";
import DecisionDocument from "@/components/DecisionDocument";
import "@/styles/decision-document.css";

export default function WorkspacePage() {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [documentData, setDocumentData] = useState(null);

  const handleSubmit = async () => {
    if (!file && !text) {
      alert("請上傳檔案或貼上文字");
      return;
    }

    const formData = new FormData();
    formData.append("title", title);
    if (file) formData.append("file", file);
    if (text) formData.append("text", text);

    try {
      const res = await fetch(`${BASE_URL}/api/process`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Failed to process the request");
      }

      const data = await res.json();
      console.log(data);
      setDocumentData(data);
    } catch (error) {
      console.error("Error:", error);
      alert("處理失敗，請稍後再試");
    }
  };

  return (
    <main className="work-area">
      {/* 標題區 */}
      <section className="title-bar">
        <h1>生成可審閱的決策頁面</h1>
      </section>

      <section className="word-body">
        {/* 左側：輸入來源 */}
        <aside className="input-panel card">
          <h3>輸入來源</h3>

          <label>標題（選填）</label>
          <input
            placeholder="請輸入決策標題"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />

          <label>上傳檔案</label>
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(e) => setFile(e.target.files[0])}
          />

          <label>或貼上文字</label>
          <textarea
            placeholder="貼上會議紀錄、文件內容…"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />

          <button onClick={handleSubmit}>開始處理</button>
        </aside>

        {/* 中間：決策頁預覽 */}
        <section className="preview-panel card">
          <div className="preview-header">
            <h3>決策頁預覽</h3>

            <div className="actions">
              <button disabled={!documentData}>下載 HTML</button>
              <button disabled={!documentData}>下載 PDF</button>
              <button disabled={!documentData}>全螢幕</button>
              <button disabled={!documentData}>刪除</button>
            </div>
          </div>

          <div className="preview-content">
            <DecisionDocument data={documentData} />
          </div>
        </section>

        {/* 右側：文件管理 */}
        <aside className="file-panel card">
          <h3>文件管理</h3>

          <ul>
            <li>
              永豐 <button>預覽</button>
            </li>
            <li>
              量子 <button>預覽</button>
            </li>
            <li>
              Untitled <button>預覽</button>
            </li>
          </ul>

          <button className="danger">刪除選取文件</button>
          <button>下載 Intelligence JSON</button>
        </aside>
      </section>
    </main>
  );
}
