"use client";

const riskColors = {
  low: "risk low",
  medium: "risk medium",
  high: "risk high",
};

const DEFAULT_KEYS = new Set([
  "document_metadata",
  "summary",
  "summary_text",
  "risk_level",
  "decision_background",
  "key_clauses",
  "risks",
  "affected_components",
  "entities",
  "causal_relations",
]);

const formatLabel = (key) => {
  if (!key) return "";
  if (/^[\x00-\x7F]+$/.test(key) && !/[\u4e00-\u9fff]/.test(key)) {
    return key.replace(/_/g, " ").replace(/\b\w/g, (m) => m.toUpperCase());
  }
  return key;
};

const isListOfObjects = (value) => Array.isArray(value) && value.length > 0 && value.every((item) => typeof item === "object");

const renderValue = (value) => {
  if (value === null || value === undefined) {
    return <p className="muted">—</p>;
  }
  if (Array.isArray(value)) {
    if (value.length === 0) {
      return <p className="muted">—</p>;
    }
    if (isListOfObjects(value)) {
      const columns = Array.from(new Set(value.flatMap((item) => Object.keys(item))));
      return (
        <div className="relation-table">
          <div className="relation-row header">
            {columns.map((col) => (
              <span key={col} className="relation-type">{formatLabel(col)}</span>
            ))}
          </div>
          {value.map((row, idx) => (
            <div key={idx} className="relation-row">
              {columns.map((col) => (
                <span key={col} className="relation-source">{row[col] ?? ""}</span>
              ))}
            </div>
          ))}
        </div>
      );
    }
    return (
      <ul>
        {value.map((item, idx) => (
          <li key={idx}>{String(item)}</li>
        ))}
      </ul>
    );
  }
  if (typeof value === "object") {
    return (
      <div className="key-value-grid">
        {Object.entries(value).map(([k, v]) => (
          <div key={k} className="key-value-row">
            <span className="key">{formatLabel(k)}</span>
            <span className="value">{typeof v === "object" ? JSON.stringify(v) : String(v)}</span>
          </div>
        ))}
      </div>
    );
  }
  return <p>{String(value)}</p>;
};

export default function DecisionDocument({ data }) {
  if (!data) {
    return (
      <div className="empty-state">
        <p>尚未產生解析內容</p>
        <p className="hint">上傳 PDF、IFC 或貼上文字後，這裡會顯示抽取結果。</p>
      </div>
    );
  }

  const meta = data.document_metadata || {};
  const relations = data.causal_relations || [];
  const isDefaultSchema = Boolean(data.document_metadata || data.summary || data.entities);

  const title =
    meta.document_title ||
    data.document_title ||
    data.title ||
    "未命名文件";
  const docType = meta.document_type || data.document_type || "Document";

  if (!isDefaultSchema) {
    const customKeys = Object.keys(data).filter((key) => key !== "document_metadata");
    return (
      <div className="decision-document">
        <header className="doc-header">
          <div className="doc-badge">{docType}</div>
          <h1 className="doc-title">{title}</h1>
          <div className="doc-meta">
            <span className="doc-id">ID: {meta.document_id || data.document_id || "N/A"}</span>
            <span className="doc-version">Version: {meta.version || data.version || "-"}</span>
            <span className="doc-source">Source: {meta.source || data.source || "-"}</span>
          </div>
        </header>

        {customKeys.map((key) => (
          <section key={key} className="info-card">
            <h3>{formatLabel(key)}</h3>
            {renderValue(data[key])}
          </section>
        ))}
      </div>
    );
  }

  return (
    <div className="decision-document">
      <header className="doc-header">
        <div className="doc-badge">{docType}</div>
        <h1 className="doc-title">{title}</h1>
        <div className="doc-meta">
          <span className="doc-id">ID: {meta.document_id || "N/A"}</span>
          <span className="doc-version">Version: {meta.version || "-"}</span>
          <span className="doc-source">Source: {meta.source || "-"}</span>
        </div>
      </header>

      <section className="summary-card">
        <h2>摘要</h2>
        <p>{data.summary || "—"}</p>
        {data.risk_level && (
          <span className={riskColors[data.risk_level] || "risk"}>
            Risk: {String(data.risk_level).toUpperCase()}
          </span>
        )}
      </section>

      <section className="grid-two">
        <div className="info-card">
          <h3>決策背景</h3>
          <ul>
            {(data.decision_background || []).map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="info-card">
          <h3>關鍵條款</h3>
          <ul>
            {(data.key_clauses || []).map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      </section>

      <section className="grid-two">
        <div className="info-card">
          <h3>風險與問題</h3>
          <ul>
            {(data.risks || []).map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="info-card">
          <h3>受影響構件</h3>
          <div className="chip-list">
            {(data.affected_components || []).map((item, idx) => (
              <span key={idx} className="chip">{item}</span>
            ))}
          </div>
        </div>
      </section>

      <section className="info-card">
        <h3>涉及實體</h3>
        <div className="entity-list">
          {(data.entities || []).map((entity, idx) => (
            <div key={idx} className="entity-item">
              <div className="entity-title">
                {entity.name}
                {entity.type && <span className="entity-type">{entity.type}</span>}
              </div>
              {entity.description && <p>{entity.description}</p>}
            </div>
          ))}
        </div>
      </section>

      <section className="info-card">
        <h3>因果 / 邏輯關係</h3>
        {relations.length === 0 ? (
          <p className="muted">未解析到明確關係。</p>
        ) : (
          <div className="relation-table">
            {relations.map((rel, idx) => (
              <div key={idx} className="relation-row">
                <span className="relation-type">{rel.relation_type}</span>
                <span className="relation-source">{rel.source}</span>
                <span className="relation-arrow">→</span>
                <span className="relation-target">{rel.target}</span>
                {rel.evidence && <span className="relation-evidence">{rel.evidence}</span>}
              </div>
            ))}
          </div>
        )}
      </section>

      {Object.keys(data).some((key) => !DEFAULT_KEYS.has(key)) && (
        <section className="info-card">
          <h3>自定義欄位</h3>
          {Object.keys(data)
            .filter((key) => !DEFAULT_KEYS.has(key))
            .map((key) => (
              <div key={key} className="custom-block">
                <h4>{formatLabel(key)}</h4>
                {renderValue(data[key])}
              </div>
            ))}
        </section>
      )}
    </div>
  );
}
