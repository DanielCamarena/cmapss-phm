from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(__file__).resolve().parent
INPUT_PATH = ROOT / "final_paper_draft.md"
OUTPUT_PATH = ROOT / "final_paper_draft.pdf"


def build_styles() -> StyleSheet1:
    styles = getSampleStyleSheet()
    styles["BodyText"].fontName = "Helvetica"
    styles["BodyText"].fontSize = 10.5
    styles["BodyText"].leading = 14
    styles["BodyText"].alignment = TA_JUSTIFY
    styles["Title"].fontName = "Helvetica-Bold"
    styles["Title"].fontSize = 18
    styles["Title"].leading = 22
    styles["Title"].spaceAfter = 10
    styles["Heading1"].fontName = "Helvetica-Bold"
    styles["Heading1"].fontSize = 15
    styles["Heading1"].leading = 18
    styles["Heading1"].spaceBefore = 10
    styles["Heading1"].spaceAfter = 6
    styles["Heading2"].fontName = "Helvetica-Bold"
    styles["Heading2"].fontSize = 12.5
    styles["Heading2"].leading = 15
    styles["Heading2"].spaceBefore = 8
    styles["Heading2"].spaceAfter = 4
    styles["Heading3"].fontName = "Helvetica-BoldOblique"
    styles["Heading3"].fontSize = 11
    styles["Heading3"].leading = 13
    styles["Heading3"].spaceBefore = 6
    styles["Heading3"].spaceAfter = 3

    styles.add(
        ParagraphStyle(
            name="BulletText",
            parent=styles["BodyText"],
            leftIndent=0,
            firstLineIndent=0,
            spaceBefore=0,
            spaceAfter=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodeBlock",
            fontName="Courier",
            fontSize=8.5,
            leading=11,
            leftIndent=10,
            rightIndent=10,
            borderColor=colors.HexColor("#CCCCCC"),
            borderWidth=0.5,
            borderPadding=6,
            backColor=colors.HexColor("#F7F7F7"),
            spaceBefore=4,
            spaceAfter=6,
        )
    )
    return styles


def escape_text(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def flush_paragraph(buffer: list[str], story: list, styles: StyleSheet1) -> None:
    if not buffer:
        return
    text = " ".join(part.strip() for part in buffer if part.strip())
    if text:
        story.append(Paragraph(escape_text(text), styles["BodyText"]))
        story.append(Spacer(1, 0.16 * cm))
    buffer.clear()


def flush_bullets(buffer: list[str], story: list, styles: StyleSheet1) -> None:
    if not buffer:
        return
    items = [
        ListItem(Paragraph(escape_text(item.strip()), styles["BulletText"]))
        for item in buffer
        if item.strip()
    ]
    if items:
        story.append(
            ListFlowable(
                items,
                bulletType="bullet",
                start="circle",
                leftIndent=14,
            )
        )
        story.append(Spacer(1, 0.16 * cm))
    buffer.clear()


def markdown_to_story(text: str) -> list:
    styles = build_styles()
    story: list = []
    paragraph_buffer: list[str] = []
    bullet_buffer: list[str] = []
    in_code_block = False
    code_lines: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        if line.strip().startswith("```"):
            flush_paragraph(paragraph_buffer, story, styles)
            flush_bullets(bullet_buffer, story, styles)
            if in_code_block:
                story.append(Preformatted("\n".join(code_lines), styles["CodeBlock"]))
                story.append(Spacer(1, 0.12 * cm))
                code_lines.clear()
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if not line.strip():
            flush_paragraph(paragraph_buffer, story, styles)
            flush_bullets(bullet_buffer, story, styles)
            continue

        if line.startswith("# "):
            flush_paragraph(paragraph_buffer, story, styles)
            flush_bullets(bullet_buffer, story, styles)
            story.append(Paragraph(escape_text(line[2:].strip()), styles["Title"]))
            story.append(Spacer(1, 0.1 * cm))
            continue

        if line.startswith("## "):
            flush_paragraph(paragraph_buffer, story, styles)
            flush_bullets(bullet_buffer, story, styles)
            story.append(Paragraph(escape_text(line[3:].strip()), styles["Heading1"]))
            continue

        if line.startswith("### "):
            flush_paragraph(paragraph_buffer, story, styles)
            flush_bullets(bullet_buffer, story, styles)
            story.append(Paragraph(escape_text(line[4:].strip()), styles["Heading2"]))
            continue

        if line.startswith("#### "):
            flush_paragraph(paragraph_buffer, story, styles)
            flush_bullets(bullet_buffer, story, styles)
            story.append(Paragraph(escape_text(line[5:].strip()), styles["Heading3"]))
            continue

        if line.lstrip().startswith("- "):
            flush_paragraph(paragraph_buffer, story, styles)
            bullet_buffer.append(line.lstrip()[2:])
            continue

        flush_bullets(bullet_buffer, story, styles)
        paragraph_buffer.append(line)

    flush_paragraph(paragraph_buffer, story, styles)
    flush_bullets(bullet_buffer, story, styles)

    if in_code_block and code_lines:
        story.append(Preformatted("\n".join(code_lines), styles["CodeBlock"]))

    return story


def main() -> None:
    source = INPUT_PATH.read_text(encoding="utf-8")
    story = markdown_to_story(source)
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Final Academic Paper Draft",
        author="OpenAI Codex",
    )
    doc.build(story)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
