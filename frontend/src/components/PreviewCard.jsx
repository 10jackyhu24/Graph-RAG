function PreviewCard() {
  return (
    <div className="preview-card">
      <h3>Industrial IPC Deployment</h3>

      <p><strong>核心問題</strong></p>
      <p>Will this deployment risk irreversible downtime?</p>

      <p><strong>關鍵假設</strong></p>
      <ul>
        <li>24/7 operation</li>
        <li>Limited onsite support</li>
      </ul>

      <div className="alert">
        Thermal misdesign leads to irreversible production loss.
      </div>
    </div>
  )
}

export default PreviewCard
