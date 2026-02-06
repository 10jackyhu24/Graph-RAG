function PreviewCard() {
  return (
    <section className="preview-card">
      <div className="preview-header">
        <span className="pill">ECN-024</span>
        <span className="pill muted">結構變更</span>
      </div>

      <h3>地下二層防水改造決策</h3>
      <p>
        變更單指出防水層老化導致滲水，需改用雙層複合膜，並調整鋼筋保護層厚度。
      </p>

      <div className="preview-grid">
        <div>
          <span className="label">影響構件</span>
          <p>15 根立柱 / 4 面剪力牆</p>
        </div>
        <div>
          <span className="label">風險等級</span>
          <p className="risk high">High</p>
        </div>
        <div>
          <span className="label">因果鏈</span>
          <p>滲水 → 內部腐蝕 → 承載下修</p>
        </div>
      </div>
    </section>
  );
}

export default PreviewCard;
