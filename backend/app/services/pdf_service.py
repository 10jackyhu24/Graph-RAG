from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import io

def decision_to_view(summary: dict) -> dict:
    return summary

def decision_pdf(view: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(view["document_metadata"]["document_title"], styles["Title"]))
    story.append(Spacer(1, 12))

    for ctx in view["contexts"]:
        story.append(Paragraph(
            f"[{ctx['decision_level']}] {ctx['title']} ({ctx['context_id']})",
            styles["Heading2"]
        ))

        story.append(Paragraph(
            f"<b>Roles:</b> {', '.join(ctx['primary_roles'])}",
            styles["Normal"]
        ))

        if ctx.get("conditions"):
            story.append(Paragraph("<b>Conditions</b>", styles["Heading3"]))
            for c in ctx["conditions"]:
                story.append(Paragraph(f"- {c}", styles["Normal"]))

        if ctx.get("risks"):
            story.append(Paragraph("<b>Risks</b>", styles["Heading3"]))
            for r in ctx["risks"]:
                story.append(Paragraph(f"- {r}", styles["Normal"]))

        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

