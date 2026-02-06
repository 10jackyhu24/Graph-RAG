import Link from "next/link";

function Hero() {
  return (
    <section className="hero">
      <div className="hero-tag">INDUSTRIAL KNOWLEDGE GRAPH</div>

      <h1>
        將大師經驗
        <br />
        變成可推理的決策圖譜
      </h1>

      <p className="hero-desc">
        以 GraphRAG 抽取 PDF / IFC / 會議紀錄中的因果與脈絡，
        全程在地端推理與向量化，確保資料主權與機密安全。
      </p>

      <div className="hero-buttons">
        <Link className="btn primary" href="/workspace">開始建模</Link>
        <Link className="btn ghost" href="/workspace">開啟工作台</Link>
      </div>
    </section>
  );
}

export default Hero;
