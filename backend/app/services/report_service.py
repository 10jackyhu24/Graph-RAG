from __future__ import annotations

from io import BytesIO
from typing import Any, Iterable

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from langchain_core.messages import HumanMessage, SystemMessage

from app.services.llm_router import get_llm


DEFAULT_FIELDS = {
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
}


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return str(value)


def _normalize_language(language: str) -> str:
    if not language:
        return "zh-Hant"
    lower = language.lower().replace("_", "-")
    if lower in ("zh", "zh-hant", "zh-tw", "zh-hk"):
        return "zh-Hant"
    return language


def _is_chinese(language: str) -> bool:
    return _normalize_language(language).lower().startswith("zh")


def _get_label(language: str, zh: str, en: str) -> str:
    return zh if _is_chinese(language) else en


def _title_from_key(key: str) -> str:
    if not key:
        return ""
    if any("\u4e00" <= ch <= "\u9fff" for ch in key):
        return key
    return key.replace("_", " ").title()


def _table_from_dict(data: dict, language: str) -> Table:
    rows = [[_get_label(language, "欄位", "Field"), _get_label(language, "內容", "Value")]]
    for k, v in data.items():
        rows.append([_title_from_key(str(k)), _safe_text(v)])
    table = Table(rows, colWidths=[140, 340])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f5f9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1f2a44")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dde3ea")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ]
        )
    )
    return table


def _table_from_list_of_dicts(items: list[dict], language: str) -> Table:
    keys: list[str] = []
    for item in items:
        for key in item.keys():
            if key not in keys:
                keys.append(key)
    if not keys:
        return _table_from_dict({}, language)
    rows = [[_title_from_key(k) for k in keys]]
    for item in items:
        rows.append([_safe_text(item.get(k)) for k in keys])
    table = Table(rows, colWidths=[max(80, 480 // max(1, len(keys)))] * len(keys))
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f5f9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1f2a44")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dde3ea")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ]
        )
    )
    return table


def _build_generic_sections(payload: dict, language: str) -> Iterable:
    styles = getSampleStyleSheet()
    for key, value in payload.items():
        if key in DEFAULT_FIELDS:
            continue
        heading = _title_from_key(str(key))
        if not heading:
            continue
        yield Paragraph(heading, styles["Heading2"])
        if isinstance(value, list):
            if value and all(isinstance(item, dict) for item in value):
                yield _table_from_list_of_dicts(value, language)
            else:
                for item in value:
                    yield Paragraph(f"• {_safe_text(item)}", styles["BodyText"])
        elif isinstance(value, dict):
            yield _table_from_dict(value, language)
        else:
            yield Paragraph(_safe_text(value), styles["BodyText"])
        yield Spacer(1, 12)


def build_pdf_report(payload: dict, language: str = "zh") -> bytes:
    language = _normalize_language(language)
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    title = _get_label(language, "變更分析報告", "Engineering Change Report")
    story: list = [Paragraph(title, styles["Title"]), Spacer(1, 12)]

    doc_meta = payload.get("document_metadata") or {}
    if doc_meta:
        meta_rows = [
            [_get_label(language, "文件編號", "Document ID"), _safe_text(doc_meta.get("document_id"))],
            [_get_label(language, "標題", "Title"), _safe_text(doc_meta.get("document_title"))],
            [_get_label(language, "文件類型", "Type"), _safe_text(doc_meta.get("document_type"))],
        ]
        meta_table = Table(meta_rows, colWidths=[120, 360])
        meta_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f5f9")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1f2a44")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dde3ea")),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ]
            )
        )
        story.extend([meta_table, Spacer(1, 16)])

    summary = payload.get("summary") or payload.get("summary_text")
    if summary:
        story.append(Paragraph(_get_label(language, "摘要", "Summary"), styles["Heading2"]))
        story.append(Paragraph(_safe_text(summary), styles["BodyText"]))
        story.append(Spacer(1, 12))

    entities = payload.get("entities") or []
    if entities:
        story.append(Paragraph(_get_label(language, "關鍵實體", "Key Entities"), styles["Heading2"]))
        for entity in entities:
            name = _safe_text(entity.get("name")) if isinstance(entity, dict) else _safe_text(entity)
            desc = _safe_text(entity.get("description")) if isinstance(entity, dict) else ""
            story.append(Paragraph(f"• {name} {desc}", styles["BodyText"]))
        story.append(Spacer(1, 12))

    components = payload.get("affected_components") or []
    if components:
        story.append(Paragraph(_get_label(language, "受影響構件", "Impacted Components"), styles["Heading2"]))
        for component in components:
            story.append(Paragraph(f"• {_safe_text(component)}", styles["BodyText"]))
        story.append(Spacer(1, 12))

    relations = payload.get("causal_relations") or []
    if relations:
        story.append(Paragraph(_get_label(language, "因果關係", "Causal Relations"), styles["Heading2"]))
        for relation in relations:
            if isinstance(relation, dict):
                text = f"{_safe_text(relation.get('source'))} → {_safe_text(relation.get('relation_type'))} → {_safe_text(relation.get('target'))}"
            else:
                text = _safe_text(relation)
            story.append(Paragraph(f"• {text}", styles["BodyText"]))
        story.append(Spacer(1, 12))

    # Generic sections for custom schema
    if any(k not in DEFAULT_FIELDS for k in payload.keys()):
        story.extend(list(_build_generic_sections(payload, language)))

    if not story:
        story.append(Paragraph(_get_label(language, "原始內容", "Raw Payload"), styles["Heading2"]))
        story.append(Paragraph(_safe_text(payload), styles["BodyText"]))

    doc.build(story)
    return buffer.getvalue()


async def generate_note(payload: dict, language: str, provider: str | None, model: str | None) -> str:
    language = _normalize_language(language)
    llm = get_llm(provider, model, temperature=0.4)
    system_text = (
        "你是一個可愛又專業的技術助理，請用繁體中文整理成短筆記。"
        if _is_chinese(language)
        else "You are a friendly technical assistant. Summarize the input into a cute, concise note."
    )
    user_text = (
        "請根據以下資料整理成 4-6 行短句，每行 15-30 字，僅保留關鍵重點，"
        "不要使用 Markdown 或特殊符號（例如 **、#、-），每行直接換行：\n"
        if _is_chinese(language)
        else "Summarize into 4-6 short lines, each 10-20 words, key points only. No Markdown or special symbols; separate lines with newlines:\n"
    )
    user_text += _safe_text(payload)

    response = await llm.ainvoke([SystemMessage(content=system_text), HumanMessage(content=user_text)])
    return _safe_text(response.content)
