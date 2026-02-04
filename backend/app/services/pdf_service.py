from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
import os
from app.utils.config import DATAPATH, FONT_MSYH, FONT_MYSHBD, FONT_ARIALUNI

def decision_to_view(summary: dict) -> dict:
    return summary

def register_chinese_fonts():
    """註冊中文字體（需要系統有這些字體）"""
    try:
        # Windows 系統字體路徑
        pdfmetrics.registerFont(TTFont('Microsoft-YaHei', FONT_MSYH))
        pdfmetrics.registerFont(TTFont('Microsoft-YaHei-Bold', FONT_MYSHBD))
        return True
    except:
        try:
            # 備用方案：使用 Arial Unicode MS
            pdfmetrics.registerFont(TTFont('Microsoft-YaHei', FONT_ARIALUNI))
            pdfmetrics.registerFont(TTFont('Microsoft-YaHei-Bold', FONT_ARIALUNI))
            return True
        except:
            return False

def get_custom_styles():
    """創建自定義樣式"""
    styles = getSampleStyleSheet()
    
    # 標題樣式
    styles.add(ParagraphStyle(
        name='ChineseTitle',
        parent=styles['Title'],
        fontName='Microsoft-YaHei-Bold',
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    ))
    
    # 決策層級標題
    styles.add(ParagraphStyle(
        name='ContextTitle',
        parent=styles['Heading2'],
        fontName='Microsoft-YaHei-Bold',
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceBefore=20,
        spaceAfter=12,
        leftIndent=0
    ))
    
    # 段落標題
    styles.add(ParagraphStyle(
        name='SectionTitle',
        parent=styles['Heading3'],
        fontName='Microsoft-YaHei-Bold',
        fontSize=11,
        textColor=colors.HexColor('#34495e'),
        spaceBefore=12,
        spaceAfter=6
    ))
    
    # 正文
    styles.add(ParagraphStyle(
        name='ChineseBody',
        parent=styles['Normal'],
        fontName='Microsoft-YaHei',
        fontSize=10,
        textColor=colors.HexColor('#2c3e50'),
        leading=16,
        leftIndent=20
    ))
    
    # 角色標籤
    styles.add(ParagraphStyle(
        name='RoleStyle',
        parent=styles['Normal'],
        fontName='Microsoft-YaHei',
        fontSize=9,
        textColor=colors.HexColor('#7f8c8d'),
        leftIndent=20
    ))
    
    return styles

def create_level_badge(level: str) -> str:
    """創建決策層級徽章"""
    colors_map = {
        'L': '#e74c3c',  # 紅色
        'M': '#f39c12',  # 橙色
        'S': '#3498db'   # 藍色
    }
    color = colors_map.get(level, '#95a5a6')
    return f'<font color="{color}"><b>[{level}]</b></font>'

def decision_pdf(view: dict, output_dir: str = DATAPATH) -> str:
    # 註冊中文字體
    font_registered = register_chinese_fonts()
    if not font_registered:
        print("警告: 無法註冊中文字體，可能會出現亂碼")
    
    # 確保輸出目錄存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = f"{view['document_metadata']['document_id']}.pdf"
    file_path = os.path.join(output_dir, file_name)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = get_custom_styles()
    story = []

    # 文檔標題
    title = view["document_metadata"]["document_title"]
    story.append(Paragraph(title, styles["ChineseTitle"]))
    
    # 文檔元數據
    metadata_data = [
        ['文檔ID:', view["document_metadata"]["document_id"]],
        ['文檔類型:', view["document_metadata"].get("document_type", "N/A")],
        ['版本:', view["document_metadata"].get("version", "N/A")]
    ]
    
    metadata_table = Table(metadata_data, colWidths=[1.5*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Microsoft-YaHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#7f8c8d')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(metadata_table)
    story.append(Spacer(1, 30))

    # 決策情境列表
    for idx, ctx in enumerate(view["contexts"], 1):
        # 決策標題（帶層級徽章）
        level_badge = create_level_badge(ctx['decision_level'])
        title_zh = ctx['title'].get('zh', '')
        title_en = ctx['title'].get('en', '')
        
        context_title = f"{level_badge} {title_zh}"
        story.append(Paragraph(context_title, styles["ContextTitle"]))
        
        if title_en and title_en != title_zh:
            story.append(Paragraph(
                f'<i><font size="9" color="#7f8c8d">{title_en}</font></i>',
                styles["ChineseBody"]
            ))
        
        story.append(Paragraph(
            f'<font color="#95a5a6" size="8">ID: {ctx["context_id"]}</font>',
            styles["RoleStyle"]
        ))
        story.append(Spacer(1, 8))

        # 主要角色
        if ctx.get("primary_roles"):
            roles_text = " • ".join(ctx["primary_roles"])
            story.append(Paragraph(
                f'<b>主要角色:</b> {roles_text}',
                styles["RoleStyle"]
            ))
            story.append(Spacer(1, 10))

        # 決策邊界
        if ctx.get("decision_boundaries"):
            story.append(Paragraph("<b>🚨 決策邊界</b>", styles["SectionTitle"]))
            for boundary in ctx["decision_boundaries"]:
                boundary_type = boundary.get("boundary_type", "未分類")
                desc_zh = boundary.get("description", {}).get("zh", "")
                desc_en = boundary.get("description", {}).get("en", "")
                
                # 邊界類型徽章
                type_color = {
                    'Safety-Critical': '#e74c3c',
                    'Irreversible': '#e67e22',
                    'Architectural': '#3498db',
                    'Technical': '#9b59b6',
                    'Operational': '#1abc9c',
                    'Performance': '#f39c12'
                }.get(boundary_type, '#95a5a6')
                
                story.append(Paragraph(
                    f'<font color="{type_color}"><b>▸ {boundary_type}</b></font>',
                    styles["ChineseBody"]
                ))
                story.append(Paragraph(f'  {desc_zh}', styles["ChineseBody"]))
                if desc_en and desc_en != desc_zh:
                    story.append(Paragraph(
                        f'  <i><font size="8" color="#7f8c8d">{desc_en}</font></i>',
                        styles["ChineseBody"]
                    ))
                story.append(Spacer(1, 6))

        # 不適用情況
        if ctx.get("non_applicability_notes"):
            story.append(Paragraph("<b>⚠️ 不適用情況</b>", styles["SectionTitle"]))
            na_zh = ctx["non_applicability_notes"].get("zh", "")
            na_en = ctx["non_applicability_notes"].get("en", "")
            
            story.append(Paragraph(f'  {na_zh}', styles["ChineseBody"]))
            if na_en and na_en != na_zh:
                story.append(Paragraph(
                    f'  <i><font size="8" color="#7f8c8d">{na_en}</font></i>',
                    styles["ChineseBody"]
                ))
            story.append(Spacer(1, 6))

        # 架構演化說明
        if ctx.get("architecture_evolution_note"):
            story.append(Paragraph("<b>🔄 架構演化</b>", styles["SectionTitle"]))
            evo_zh = ctx["architecture_evolution_note"].get("zh", "")
            evo_en = ctx["architecture_evolution_note"].get("en", "")
            
            story.append(Paragraph(f'  {evo_zh}', styles["ChineseBody"]))
            if evo_en and evo_en != evo_zh:
                story.append(Paragraph(
                    f'  <i><font size="8" color="#7f8c8d">{evo_en}</font></i>',
                    styles["ChineseBody"]
                ))
            story.append(Spacer(1, 6))

        # 信心度
        if ctx.get("confidence_score"):
            score = ctx["confidence_score"]
            score_color = '#27ae60' if score >= 0.9 else '#f39c12' if score >= 0.8 else '#e74c3c'
            story.append(Paragraph(
                f'<font color="{score_color}"><b>信心度: {score:.0%}</b></font>',
                styles["RoleStyle"]
            ))

        # 分隔線
        if idx < len(view["contexts"]):
            story.append(Spacer(1, 20))
            story.append(Table([['']], colWidths=[6.5*inch], rowHeights=[1]))
            story[-1].setStyle(TableStyle([
                ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#ecf0f1'))
            ]))
            story.append(Spacer(1, 20))

    # 生成 PDF
    doc.build(story)
    buffer.seek(0)

    # 寫入文件
    with open(file_path, "wb") as f:
        f.write(buffer.read())

    buffer.close()
    print(f"✅ PDF 已生成: {file_path}")
    return file_path

