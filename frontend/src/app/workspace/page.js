"use client"

export default function WorkspacePage() {
  return (
    <main className="work-area">
      {/* 標題區 */}
      <section className="title-bar">
        <h1>生成可審閱的決策頁面</h1>
        {/* <p className="desc">
          上傳文件或貼上文字，轉成可保存、可下載的決策頁。
        </p> */}
      </section>

      <section className="word-body">
        {/* 左側：輸入來源 */}
        <aside className="input-panel card">
          <h3>輸入來源</h3>

          <label>標題（選填）</label>
          <input placeholder="請輸入決策標題" />

          <label>上傳檔案</label>
          <input type="file" />

          <label>或貼上文字</label>
          <textarea placeholder="貼上會議紀錄、文件內容…" />
        </aside>

        {/* 中間：決策頁預覽 */}
        <section className="preview-panel card">
          <div className="preview-header">
            <h3>決策頁預覽</h3>

            <div className="actions">
              <button>下載 HTML</button>
              <button>下載 PDF</button>
              <button>全螢幕</button>
              <button>刪除</button>
            </div>
          </div>

          <div className="preview-content">
            <p className="placeholder">
              模型產生時即時更新內容。
            </p>
          </div>
        </section>

        {/* 右側：文件管理 */}
        <aside className="file-panel card">
          <h3>文件管理</h3>

          <ul>
            <li>永豐 <button>預覽</button></li>
            <li>量子 <button>預覽</button></li>
            <li>Untitled <button>預覽</button></li>
          </ul>

          <button className="danger">刪除選取文件</button>
          <button>下載 Intelligence JSON</button>
        </aside>
      </section>
    </main>
  )
}
