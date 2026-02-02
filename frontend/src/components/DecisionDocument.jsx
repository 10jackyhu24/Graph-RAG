"use client";

export default function DecisionDocument({ data }) {
  if (!data) {
    return (
      <div className="empty-state">
        <p>尚未處理任何文件</p>
        <p className="hint">請從左側上傳文件或貼上文字開始</p>
      </div>
    );
  }

  const { document_metadata, contexts } = data;

  // 依決策層級分組
  const groupedContexts = {
    L: contexts.filter(ctx => ctx.decision_level === 'L'),
    M: contexts.filter(ctx => ctx.decision_level === 'M'),
    S: contexts.filter(ctx => ctx.decision_level === 'S'),
  };

  const levelNames = {
    L: '高層決策 (Large)',
    M: '中層決策 (Medium)',
    S: '策略決策 (Strategic)',
  };

  const levelColors = {
    L: '#e74c3c',
    M: '#f39c12',
    S: '#3498db',
  };

  return (
    <div className="decision-document">
      {/* 文件標題區 */}
      <header className="doc-header">
        <div className="doc-badge">{document_metadata.document_type}</div>
        <h1 className="doc-title">{document_metadata.document_title}</h1>
        <div className="doc-meta">
          <span className="doc-id">ID: {document_metadata.document_id}</span>
          <span className="doc-version">v{document_metadata.version}</span>
        </div>
      </header>

      {/* 統計總覽 */}
      <section className="doc-stats">
        <div className="stat-card">
          <div className="stat-value">{contexts.length}</div>
          <div className="stat-label">決策情境</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{groupedContexts.L.length}</div>
          <div className="stat-label">高層決策</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{groupedContexts.M.length}</div>
          <div className="stat-label">中層決策</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{groupedContexts.S.length}</div>
          <div className="stat-label">策略決策</div>
        </div>
      </section>

      {/* 決策情境列表 */}
      {Object.entries(groupedContexts).map(([level, ctxList]) => {
        if (ctxList.length === 0) return null;
        
        return (
          <section key={level} className="context-section">
            <h2 className="section-title" style={{ borderLeftColor: levelColors[level] }}>
              {levelNames[level]}
            </h2>

            {ctxList.map((ctx) => (
              <article key={ctx.context_id} className="context-card">
                {/* 卡片標題 */}
                <div className="context-header">
                  <div className="context-title-group">
                    <span 
                      className="context-level-badge" 
                      style={{ backgroundColor: levelColors[level] }}
                    >
                      {level}
                    </span>
                    <h3 className="context-title">{ctx.title.zh}</h3>
                  </div>
                  <div className="context-confidence">
                    <span className="confidence-label">信心度</span>
                    <span className="confidence-value">
                      {(ctx.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>

                <p className="context-title-en">{ctx.title.en}</p>

                {/* 主要角色 */}
                <div className="context-section-item">
                  <h4 className="item-label">主要角色</h4>
                  <div className="role-tags">
                    {ctx.primary_roles.map((role, idx) => (
                      <span key={idx} className="role-tag">{role}</span>
                    ))}
                  </div>
                </div>

                {/* 決策邊界 */}
                <div className="context-section-item">
                  <h4 className="item-label">決策邊界</h4>
                  {ctx.decision_boundaries.map((boundary, idx) => (
                    <div key={idx} className="boundary-item">
                      <span className="boundary-type">{boundary.boundary_type}</span>
                      <p className="boundary-desc">{boundary.description.zh}</p>
                      <p className="boundary-desc-en">{boundary.description.en}</p>
                    </div>
                  ))}
                </div>

                {/* 不適用情況 */}
                <div className="context-section-item">
                  <h4 className="item-label">不適用情況</h4>
                  <p className="note-text">{ctx.non_applicability_notes.zh}</p>
                  <p className="note-text-en">{ctx.non_applicability_notes.en}</p>
                </div>

                {/* 架構演化說明 */}
                <div className="context-section-item">
                  <h4 className="item-label">架構演化說明</h4>
                  <p className="note-text evolution">{ctx.architecture_evolution_note.zh}</p>
                  <p className="note-text-en">{ctx.architecture_evolution_note.en}</p>
                </div>
              </article>
            ))}
          </section>
        );
      })}
    </div>
  );
}
