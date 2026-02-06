"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { BASE_URL } from "@/config";
import DecisionDocument from "@/components/DecisionDocument";
import "@/styles/decision-document.css";

const parseNoteItems = (text) => {
  if (!text) return [];
  const cleaned = text
    .replace(/\*\*/g, "")
    .replace(/[#*_`]/g, "")
    .replace(/\s+/g, " ")
    .trim();

  let lines = cleaned.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  if (lines.length < 3) {
    lines = cleaned
      .split(/[。！？!?]/)
      .map((line) => line.trim())
      .filter(Boolean);
  }
  return lines.slice(0, 6);
};

const normalizeDocId = (value) => {
  if (!value) return null;
  const text = String(value).trim();
  if (!text) return null;
  if (["null", "n/a", "-"].includes(text.toLowerCase())) return null;
  return text;
};

export default function WorkspacePage() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [tenantId, setTenantId] = useState("default");
  const [provider, setProvider] = useState("deepseek");
  const [model, setModel] = useState("deepseek-chat");
  const [sourceType, setSourceType] = useState("auto");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const [agents, setAgents] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [agentId, setAgentId] = useState("");
  const [agentDetail, setAgentDetail] = useState(null);
  const [showAgentForm, setShowAgentForm] = useState(false);
  const [agentName, setAgentName] = useState("");
  const [agentPrompt, setAgentPrompt] = useState("");
  const [agentDesc, setAgentDesc] = useState("");
  const [agentVisibility, setAgentVisibility] = useState("private");
  const [createFromSelected, setCreateFromSelected] = useState(false);
  const [language, setLanguage] = useState("zh-Hant");

  const [note, setNote] = useState("");
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState([]);
  const chatEndRef = useRef(null);

  const extractionPayload = result?.extraction || null;
  const noteItems = useMemo(() => parseNoteItems(note), [note]);

  const refreshLists = () => {
    if (!tenantId) return;
    fetch(`${BASE_URL}/api/agents?tenant_id=${tenantId}&include_inactive=true`)
      .then((res) => res.json())
      .then(setAgents)
      .catch(() => {});
    fetch(`${BASE_URL}/api/documents?tenant_id=${tenantId}`)
      .then((res) => res.json())
      .then(setDocuments)
      .catch(() => {});
  };

  useEffect(() => {
    refreshLists();
  }, [tenantId]);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages]);

  useEffect(() => {
    setAgentDetail(null);
  }, [agentId]);

  const simulateProgress = () => {
    setProgress(10);
    const timer = setInterval(() => {
      setProgress((prev) => (prev < 90 ? prev + Math.random() * 8 : prev));
    }, 500);
    return () => clearInterval(timer);
  };

  const handleSubmit = async () => {
    setError("");
    if (!file && !text) {
      setError("請上傳檔案或貼上文字內容。 ");
      return;
    }

    const formData = new FormData();
    if (file) formData.append("file", file);
    if (text) formData.append("text", text);
    formData.append("tenant_id", tenantId);
    formData.append("llm_provider", provider);
    if (model) formData.append("llm_model", model);
    if (sourceType !== "auto") formData.append("source_type", sourceType);
    if (agentId) formData.append("agent_id", agentId);

    const stopProgress = simulateProgress();

    try {
      setLoading(true);
      const res = await fetch(`${BASE_URL}/api/ingest`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const detail = await res.text();
        throw new Error(detail || "處理失敗");
      }

      const data = await res.json();
      setResult(data);
      setProgress(100);
      refreshLists();
    } catch (err) {
      setError(err.message || "處理失敗");
    } finally {
      stopProgress();
      setTimeout(() => setProgress(0), 1200);
      setLoading(false);
    }
  };

  const handleCreateAgent = async () => {
    if (!agentName || !agentPrompt) {
      setError("請輸入 Agent 名稱與需求描述");
      return;
    }
    setError("");
    try {
      const res = await fetch(`${BASE_URL}/api/agents`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tenant_id: tenantId,
          name: agentName,
          description: agentDesc,
          prompt: agentPrompt,
          output_language: language,
          llm_provider: provider,
          llm_model: model,
          visibility: agentVisibility,
          base_agent_id: createFromSelected ? agentId : null,
        }),
      });
      if (!res.ok) {
        throw new Error("建立 Agent 失敗");
      }
      const data = await res.json();
      setAgents([data, ...agents]);
      setAgentId(data.id);
      setShowAgentForm(false);
      setAgentName("");
      setAgentPrompt("");
      setAgentDesc("");
      setCreateFromSelected(false);
      refreshLists();
    } catch (err) {
      setError(err.message || "建立 Agent 失敗");
    }
  };

  const handleDeactivateAgent = async () => {
    if (!agentId) return;
    await fetch(`${BASE_URL}/api/agents/${agentId}/deactivate?tenant_id=${tenantId}`, { method: "POST" });
    refreshLists();
  };

  const handleDeleteAgent = async () => {
    if (!agentId) return;
    await fetch(`${BASE_URL}/api/agents/${agentId}?tenant_id=${tenantId}`, { method: "DELETE" });
    setAgentId("");
    setAgentDetail(null);
    refreshLists();
  };

  const handleViewAgent = async () => {
    if (!agentId) return;
    const res = await fetch(`${BASE_URL}/api/agents/${agentId}?tenant_id=${tenantId}`);
    if (res.ok) {
      const data = await res.json();
      setAgentDetail(data);
      setShowAgentForm(false);
    }
  };

  const handleNote = async () => {
    if (!extractionPayload) return;
    const res = await fetch(`${BASE_URL}/api/report/note`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        payload: extractionPayload,
        language,
        llm_provider: provider,
        llm_model: model,
      }),
    });
    const data = await res.json();
    setNote(data.note || "");
  };

  const handlePdf = async () => {
    if (!extractionPayload) return;
    const res = await fetch(`${BASE_URL}/api/report/pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ payload: extractionPayload, language }),
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank");
  };

  const handleChat = async () => {
    if (!chatInput.trim()) return;
    const userMessage = { role: "user", content: chatInput };
    setChatMessages((prev) => [...prev, userMessage, { role: "assistant", content: "" }]);
    setChatInput("");

    const res = await fetch(`${BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tenant_id: tenantId,
        query: userMessage.content,
        language,
        llm_provider: provider,
        llm_model: model,
      }),
    });

    if (!res.body) return;
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let done = false;
    while (!done) {
      const { value, done: doneReading } = await reader.read();
      done = doneReading;
      const chunk = decoder.decode(value || new Uint8Array(), { stream: true });
      setChatMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last && last.role === "assistant") {
          last.content += chunk;
        }
        return updated;
      });
    }
  };

  const handleDownload = async (doc) => {
    const docId = normalizeDocId(doc?.document_id);
    if (docId) {
      window.open(`${BASE_URL}/api/documents/${docId}/download?tenant_id=${tenantId}`, "_blank");
    } else if (doc?.row_id) {
      window.open(`${BASE_URL}/api/documents/by-row/${doc.row_id}/download?tenant_id=${tenantId}`, "_blank");
    }
  };

  const handleDeleteDoc = async (doc) => {
    const docId = normalizeDocId(doc?.document_id);
    if (docId) {
      await fetch(`${BASE_URL}/api/documents/${docId}?tenant_id=${tenantId}`, { method: "DELETE" });
    } else if (doc?.row_id) {
      await fetch(`${BASE_URL}/api/documents/by-row/${doc.row_id}?tenant_id=${tenantId}`, { method: "DELETE" });
    }
    refreshLists();
  };

  const handleLoadDoc = async (doc) => {
    if (!doc) return;
    const docId = normalizeDocId(doc?.document_id);
    const url = docId
      ? `${BASE_URL}/api/documents/${docId}?tenant_id=${tenantId}`
      : `${BASE_URL}/api/documents/by-row/${doc.row_id}?tenant_id=${tenantId}`;
    const res = await fetch(url);
    if (!res.ok) return;
    const loaded = await res.json();
    if (loaded?.raw_json) {
      let payload = loaded.raw_json;
      if (typeof payload === "string") {
        try {
          payload = JSON.parse(payload);
        } catch (err) {
          payload = { summary: payload };
        }
      }
      setResult({ extraction: payload, storage: { postgres: true, chroma: true, neo4j: true } });
    }
  };

  const openAgentModal = () => {
    setShowAgentForm(true);
    setAgentDetail(null);
  };

  const openDetailModal = async () => {
    await handleViewAgent();
  };

  const closeAgentModal = () => {
    setShowAgentForm(false);
    setAgentDetail(null);
  };

  return (
    <main className="workspace">
      <section className="workspace-header">
        <div>
          <h1>知識抽取工作台</h1>
          <p>上傳 PDF / IFC / DOCX 或貼上文字，立即生成結構化圖譜。</p>
        </div>
        <button className="btn primary" onClick={handleSubmit} disabled={loading}>
          {loading ? "處理中..." : "開始解析"}
        </button>
      </section>

      <section className="workspace-grid">
        <aside className="panel">
          <h3>輸入設定</h3>

          <label>租戶 ID</label>
          <input
            value={tenantId}
            onChange={(e) => setTenantId(e.target.value)}
            placeholder="customer_a"
          />

          <label>模型供應商</label>
          <select value={provider} onChange={(e) => setProvider(e.target.value)}>
            <option value="deepseek">DeepSeek API</option>
            <option value="ollama">Ollama (Local)</option>
          </select>

          <label>模型名稱</label>
          <input
            value={model}
            onChange={(e) => setModel(e.target.value)}
            placeholder="deepseek-chat / qwen3:8b"
          />

          <label>來源類型</label>
          <select value={sourceType} onChange={(e) => setSourceType(e.target.value)}>
            <option value="auto">自動判斷</option>
            <option value="pdf">PDF</option>
            <option value="ifc">IFC</option>
            <option value="text">Text</option>
          </select>

          <label>選擇 Agent</label>
          <select value={agentId} onChange={(e) => setAgentId(e.target.value)}>
            <option value="">預設抽取</option>
            {agents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name} v{agent.version} {agent.is_active ? "" : "(停用)"}
              </option>
            ))}
          </select>

          <div className="agent-actions">
            <button className="btn ghost" onClick={openAgentModal}>
              建立 Agent
            </button>
            <button className="btn ghost" onClick={openDetailModal} disabled={!agentId}>
              查看內容
            </button>
            <button className="btn ghost" onClick={handleDeactivateAgent} disabled={!agentId}>
              停用
            </button>
            <button className="btn ghost" onClick={handleDeleteAgent} disabled={!agentId}>
              刪除
            </button>
          </div>

          <label>上傳檔案</label>
          <input
            type="file"
            accept=".pdf,.ifc,.ifczip,.docx,.txt"
            onChange={(e) => setFile(e.target.files[0])}
          />

          <label>或貼上文字</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="貼上變更單、會議摘要或技術規範..."
          />

          <div className="doc-list">
            <h4>最近文件</h4>
            {documents.slice(0, 6).map((doc, idx) => (
              <div key={`${normalizeDocId(doc.document_id) || ("row-" + (doc.row_id || idx))}-${doc.created_at || idx}`} className="doc-item">
                <strong>{doc.document_title || "未命名文件"}</strong>
                <span className="muted">{normalizeDocId(doc.document_id) || `#${doc.row_id}`}</span>
                <div className="doc-actions">
                  <button
                    className="btn ghost"
                    onClick={() => handleLoadDoc(doc)}
                    disabled={!normalizeDocId(doc.document_id) && !doc.row_id}
                  >
                    檢視
                  </button>
                  <button className="btn ghost" onClick={() => handleDownload(doc)} disabled={!normalizeDocId(doc.document_id) && !doc.row_id}>
                    下載
                  </button>
                  <button className="btn ghost" onClick={() => handleDeleteDoc(doc)} disabled={!normalizeDocId(doc.document_id) && !doc.row_id}>
                    刪除
                  </button>
                </div>
              </div>
            ))}
          </div>

          {loading && (
            <div className="progress-wrap">
              <div className="progress-bar" style={{ width: `${progress}%` }} />
              <p className="muted">正在整理內容中... {Math.round(progress)}%</p>
            </div>
          )}

          {error && <p className="error-text">{error}</p>}
        </aside>

        <section className="panel preview">
          <div className="preview-header">
            <div>
              <h3>解析結果</h3>
              <p className="muted">
                Postgres / Chroma / Neo4j 將在同一次解析中同步寫入。
              </p>
            </div>
            {result?.storage && (
              <div className="storage-status">
                <span className={result.storage.postgres ? "pill" : "pill muted"}>Postgres</span>
                <span className={result.storage.chroma ? "pill" : "pill muted"}>Chroma</span>
                <span className={result.storage.neo4j ? "pill" : "pill muted"}>Neo4j</span>
              </div>
            )}
          </div>

          <div className="result-actions">
            <button className="btn ghost" onClick={handlePdf} disabled={!extractionPayload}>匯出 PDF 報告</button>
            <button className="btn ghost" onClick={handleNote} disabled={!extractionPayload}>生成可愛筆記</button>
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              <option value="zh-Hant">繁體中文</option>
              <option value="en">English</option>
            </select>
          </div>

          <DecisionDocument data={extractionPayload} />

          {noteItems.length > 0 && (
            <div className="note-grid">
              {noteItems.map((item, idx) => (
                <div key={idx} className="note-item">{item}</div>
              ))}
            </div>
          )}
        </section>

        <aside className="panel chat-panel">
          <div className="chat-header">
            <h3>GraphRAG 對話</h3>
            <p className="muted">只會查詢你的租戶資料庫（{tenantId}）。</p>
          </div>
          <div className="chat-messages">
            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`chat-bubble ${msg.role}`}>
                {msg.content}
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <div className="chat-input">
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="輸入你的問題..."
            />
            <button className="btn primary" onClick={handleChat}>送出</button>
          </div>
        </aside>
      </section>

      {(showAgentForm || agentDetail) && (
        <div className="modal-backdrop" onClick={closeAgentModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{agentDetail ? "Agent 詳情" : "建立 Agent"}</h3>
              <button className="btn ghost" onClick={closeAgentModal}>關閉</button>
            </div>
            <div className="modal-body">
              {agentDetail ? (
                <div>
                  <p className="muted">{agentDetail.name} v{agentDetail.version} · {agentDetail.visibility}</p>
                  <p><strong>需求描述</strong></p>
                  <p className="muted">{agentDetail.prompt}</p>
                  <p><strong>Schema</strong></p>
                  <pre className="json-block">{JSON.stringify(agentDetail.schema_json, null, 2)}</pre>
                </div>
              ) : (
                <div className="agent-form">
                  <label>Agent 名稱</label>
                  <input value={agentName} onChange={(e) => setAgentName(e.target.value)} />
                  <label>描述</label>
                  <input value={agentDesc} onChange={(e) => setAgentDesc(e.target.value)} />
                  <label>需求描述 / Prompt</label>
                  <textarea value={agentPrompt} onChange={(e) => setAgentPrompt(e.target.value)} />
                  <label>輸出語言</label>
                  <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                    <option value="zh-Hant">繁體中文</option>
                    <option value="en">English</option>
                  </select>
                  <label>權限</label>
                  <select value={agentVisibility} onChange={(e) => setAgentVisibility(e.target.value)}>
                    <option value="private">私人</option>
                    <option value="team">團隊</option>
                  </select>
                  <label>
                    <input
                      type="checkbox"
                      checked={createFromSelected}
                      onChange={(e) => setCreateFromSelected(e.target.checked)}
                    />
                    從選擇的 Agent 建立新版本
                  </label>
                  <button className="btn primary" onClick={handleCreateAgent}>建立並儲存</button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
