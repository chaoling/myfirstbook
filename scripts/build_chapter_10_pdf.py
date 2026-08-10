#!/usr/bin/env python3
"""Build a print-friendly PDF review edition of Chapter 10."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer

import build_review_pdf as common


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_posts" / "2024-06-24-Chapter_10.markdown"
OUTPUT = ROOT / "output" / "pdf" / "chapter-10-three-teams-one-philosophy.pdf"


def convert_html_figures(lines: list[str]) -> list[str]:
    """Convert Jekyll HTML figures into the Markdown form used by the PDF parser."""
    converted: list[str] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped != '<figure class="chapter-figure">':
            converted.append(lines[index])
            index += 1
            continue

        block: list[str] = []
        index += 1
        while index < len(lines) and lines[index].strip() != "</figure>":
            block.append(lines[index].strip())
            index += 1
        if index >= len(lines):
            raise ValueError("Unclosed chapter figure")
        index += 1

        markup = " ".join(block)
        image_match = re.search(
            r'<img\s+src="\{\{\s*[\'\"](/assets/images/[^\'\"]+)[\'\"]\s*\|\s*relative_url\s*\}\}"\s+alt="([^"]*)"\s*/?>',
            markup,
        )
        caption_match = re.search(r"<figcaption>(.*?)</figcaption>", markup)
        if not image_match:
            raise ValueError(f"Could not parse figure image: {markup}")

        image_path, alt = image_match.groups()
        converted.append(
            f"![{alt}]({{{{ site.url }}}}{{{{ site.baseurl }}}}{image_path})"
        )
        if caption_match:
            caption = caption_match.group(1)
            caption = re.sub(r"<em>(.*?)</em>", r"*\1*", caption)
            converted.append(f"*{caption}*")
        converted.append("")

    return converted


def chapter_lines(lines: list[str]) -> list[str]:
    """Remove the repeated H1 and normalize figures for print."""
    normalized = convert_html_figures(lines)
    for index, line in enumerate(normalized):
        if line.strip():
            if line.startswith("# "):
                del normalized[index]
            break
    for index, line in enumerate(normalized):
        if line.strip() == "## Fire Kirin: Persistence":
            normalized.insert(index, "<!-- pagebreak -->")
            break
    return normalized


def draw_cover(canvas, doc) -> None:
    canvas.saveState()
    canvas.setTitle("Three Teams, One Philosophy - Chapter 10 Review Edition")
    canvas.setAuthor("Coach Ling")
    canvas.setSubject("FIRST LEGO League coaching philosophy for first-time volunteer coaches")
    canvas.restoreState()


def draw_header_footer(canvas, doc) -> None:
    canvas.saveState()
    width, height = letter
    canvas.setStrokeColor(common.RULE)
    canvas.setLineWidth(0.45)
    canvas.line(doc.leftMargin, height - 0.54 * inch, width - doc.rightMargin, height - 0.54 * inch)
    canvas.setFillColor(common.MUTED)
    canvas.setFont("BookSans", 7.4)
    canvas.drawString(doc.leftMargin, height - 0.43 * inch, "WE USE ROBOTS TO BUILD KIDS")
    canvas.drawRightString(width - doc.rightMargin, height - 0.43 * inch, "CHAPTER 10 REVIEW EDITION")
    canvas.setFont("BookSans", 8)
    canvas.drawCentredString(width / 2, 0.43 * inch, str(doc.page - 1))
    canvas.restoreState()


def build() -> Path:
    common.register_fonts()
    styles = common.make_styles()
    title, lines = common.read_chapter(SOURCE)
    clean_title = re.sub(r"^Chapter\s+\d+:\s*", "", title)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.72 * inch,
        leftMargin=0.72 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.67 * inch,
        title=f"{clean_title} - Chapter 10 Review Edition",
        author="Coach Ling",
        subject="FIRST LEGO League coaching philosophy for first-time volunteer coaches",
    )

    cover_kicker = ParagraphStyle(
        "CoverKicker10",
        fontName="BookSansBold",
        fontSize=10,
        leading=13,
        textColor=common.GOLD,
        alignment=TA_CENTER,
        tracking=2.3,
        spaceAfter=18,
    )
    cover_title = ParagraphStyle(
        "CoverTitle10",
        fontName="BookSerifBold",
        fontSize=34,
        leading=41,
        textColor=common.NAVY,
        alignment=TA_CENTER,
        spaceAfter=16,
    )
    cover_subtitle = ParagraphStyle(
        "CoverSubtitle10",
        fontName="BookSerifItalic",
        fontSize=15,
        leading=21,
        textColor=common.BLUE,
        alignment=TA_CENTER,
        spaceAfter=25,
    )
    cover_author = ParagraphStyle(
        "CoverAuthor10",
        fontName="BookSans",
        fontSize=11,
        leading=15,
        textColor=common.MUTED,
        alignment=TA_CENTER,
    )

    story: list = [
        Spacer(1, 1.0 * inch),
        Paragraph("FIRST LEGO LEAGUE COACHING PHILOSOPHY", cover_kicker),
        HRFlowable(width="72%", thickness=2.2, color=common.GOLD, spaceAfter=26, hAlign="CENTER"),
        Paragraph(common.inline_markup(clean_title), cover_title),
        Paragraph("Persistence, transformation, and accelerated learning", cover_subtitle),
        Spacer(1, 0.55 * inch),
        Paragraph("CHAPTER 10 REVIEW EDITION", cover_kicker),
        Paragraph("Coach Ling", cover_author),
        Spacer(1, 1.0 * inch),
        Paragraph("For editorial and family review", cover_author),
        PageBreak(),
        Spacer(1, 0.35 * inch),
        Paragraph("CHAPTER 10", styles["chapter_label"]),
        Paragraph(common.inline_markup(clean_title), styles["chapter_title"]),
        HRFlowable(width="100%", thickness=1.5, color=common.GOLD, spaceAfter=17),
    ]
    story.extend(common.markdown_story(chapter_lines(lines), styles))

    document.build(story, onFirstPage=draw_cover, onLaterPages=draw_header_footer)
    return OUTPUT


if __name__ == "__main__":
    print(build())
