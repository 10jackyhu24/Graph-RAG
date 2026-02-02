from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import io

def summary_to_pdf(summary: dict) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(summary["title"], styles["Title"]))
    story.append(Spacer(1, 12))

    # Summary points
    story.append(Paragraph("<b>重點摘要</b>", styles["Heading2"]))
    for point in summary["summary"]:
        story.append(Paragraph(f"- {point}", styles["Normal"]))

    story.append(Spacer(1, 12))

    # Action items
    if summary.get("action_items"):
        story.append(Paragraph("<b>待辦事項</b>", styles["Heading2"]))
        for item in summary["action_items"]:
            story.append(Paragraph(f"- {item}", styles["Normal"]))

    # Conclusion
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>結論</b>", styles["Heading2"]))
    story.append(Paragraph(summary["conclusion"], styles["Normal"]))

    doc.build(story)
    buffer.seek(0)

    return buffer.read()
