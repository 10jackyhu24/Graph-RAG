"use client";

import { useEffect, useState } from "react";
import { BASE_URL } from "@/config";
import DecisionDocument from "@/components/DecisionDocument";

export default function MeetingPage() {
  const [tenantId, setTenantId] = useState("default");
  const [provider, setProvider] = useState("deepseek");
  const [model, setModel] = useState("deepseek-chat");
  const [agents, setAgents] = useState([]);
  const [agentId, setAgentId] = useState("");
  const [language, setLanguage] = useState("zh-Hant");
  const [text, setText] = useState("");
  const [audioFile, setAudioFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${BASE_URL}/api/agents?tenant_id=${tenantId}`)
      .then((res) => res.json())
      .then(setAgents)
      .catch(() => {});
  }, [tenantId]);

  const handleSubmit = async () => {
    setError("");
    if (!text.trim()) {
      setError("請貼上會議逐字稿或摘要");
      return;
    }

    const formData = new FormData();
    formData.append("text", text);
    formData.append("tenant_id", tenantId);
    formData.append("llm_provider", provider);
    formData.append("llm_model", model);
    if (agentId) formData.append("agent_id", agentId);
    formData.append("language", language);

    try {
      const res = await fetch(`${BASE_URL}/api/meeting/ingest`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("處理失敗");
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "處理失敗");
    }
  };

  const handleASR = async () => {
    setError("");
    if (!audioFile) {
      setError("請上傳音檔");
      return;
    }
    const formData = new FormData();
    formData.append("file", audioFile);
    formData.append("tenant_id", tenantId);
    formData.append("llm_provider", provider);
    formData.append("llm_model", model);
    if (agentId) formData.append("agent_id", agentId);
    formData.append("language", language);

    try {
      const res = await fetch(`${BASE_URL}/api/meeting/asr`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("ASR 處理失敗");
      const data = await res.json();
      setText(data.transcript || text);
      setResult(data);
    } catch (err) {
      setError(err.message || "處理失敗");
    }
  };

  return (
    <main className="workspace">
      <section className="workspace-header">
        <div>
          <h1>會議紀錄抽取</h1>
          <p>可上傳音檔進行 ASR，再用 Agent 做結構化抽取。</p>
        </div>
        <button className="btn primary" onClick={handleSubmit}>開始整理</button>
      </section>

      <section className="workspace-body">
        <aside className="panel">
          <label>租戶 ID</label>
          <input value={tenantId} onChange={(e) => setTenantId(e.target.value)} />

          <label>模型供應商</label>
          <select value={provider} onChange={(e) => setProvider(e.target.value)}>
            <option value="deepseek">DeepSeek API</option>
            <option value="ollama">Ollama (Local)</option>
          </select>

          <label>模型名稱</label>
          <input value={model} onChange={(e) => setModel(e.target.value)} />

          <label>選擇 Agent</label>
          <select value={agentId} onChange={(e) => setAgentId(e.target.value)}>
            <option value="">預設抽取</option>
            {agents.map((agent) => (
              <option key={agent.id} value={agent.id}>{agent.name}</option>
            ))}
          </select>

          <label>輸出語言</label>
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="zh-Hant">繁體中文</option>
            <option value="en">English</option>
          </select>

          <label>上傳音檔 (wav/mp3/m4a)</label>
          <input type="file" accept=".wav,.mp3,.m4a" onChange={(e) => setAudioFile(e.target.files[0])} />
          <button className="btn ghost" onClick={handleASR}>ASR 轉寫</button>

          <label>會議逐字稿</label>
          <textarea value={text} onChange={(e) => setText(e.target.value)} />

          {error && <p className="error-text">{error}</p>}
        </aside>

        <section className="panel preview">
          <h3>整理結果</h3>
          <DecisionDocument data={result?.extraction} />
        </section>
      </section>
    </main>
  );
}
