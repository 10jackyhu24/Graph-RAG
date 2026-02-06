function Steps() {
  const items = [
    {
      title: "感知與結構化",
      desc: "PDF/IFC 轉成保留表格與標題的 Markdown。",
      meta: "Unstructured hi_res",
    },
    {
      title: "語義萃取",
      desc: "LLM 依據 Pydantic Schema 自動填寫 JSON。",
      meta: "LangChain 1.0",
    },
    {
      title: "三層儲存",
      desc: "Postgres + Chroma + Neo4j 同步落地。",
      meta: "Data Sovereignty",
    },
  ];

  return (
    <section className="steps">
      <div className="section-header">
        <h2>GraphRAG Pipeline</h2>
        <p>從非結構化資料到可推理的決策網路。</p>
      </div>

      <div className="step-grid">
        {items.map((item) => (
          <article key={item.title} className="step-card">
            <div className="step-meta">{item.meta}</div>
            <h3>{item.title}</h3>
            <p>{item.desc}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

export default Steps;
