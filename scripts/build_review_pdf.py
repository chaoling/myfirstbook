#!/usr/bin/env python3
"""Build a print-friendly PDF review edition from the first four chapters."""

from __future__ import annotations

import html
import re
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "fll-coaching-philosophy-chapters-1-4.pdf"
CHAPTERS = [
    ROOT / "_posts" / "2024-12-24-Chapter_1.markdown",
    ROOT / "_posts" / "2024-06-24-Chapter_2.markdown",
    ROOT / "_posts" / "2024-06-24-Chapter_3.markdown",
    ROOT / "_posts" / "2024-06-24-Chapter_4.markdown",
]

NAVY = colors.HexColor("#183B56")
BLUE = colors.HexColor("#2D6687")
GOLD = colors.HexColor("#D69B2D")
INK = colors.HexColor("#202A33")
MUTED = colors.HexColor("#66737D")
PALE = colors.HexColor("#F3F6F7")
RULE = colors.HexColor("#D7DEE2")


def register_fonts() -> None:
    font_dir = Path("/System/Library/Fonts/Supplemental")
    pdfmetrics.registerFont(TTFont("BookSerif", str(font_dir / "Georgia.ttf")))
    pdfmetrics.registerFont(TTFont("BookSerifBold", str(font_dir / "Georgia Bold.ttf")))
    pdfmetrics.registerFont(TTFont("BookSerifItalic", str(font_dir / "Georgia Italic.ttf")))
    pdfmetrics.registerFont(TTFont("BookSans", str(font_dir / "Arial.ttf")))
    pdfmetrics.registerFont(TTFont("BookSansBold", str(font_dir / "Arial Bold.ttf")))
    pdfmetrics.registerFontFamily(
        "BookSerif",
        normal="BookSerif",
        bold="BookSerifBold",
        italic="BookSerifItalic",
        boldItalic="BookSerifBold",
    )


def normalize_print_text(value: str) -> str:
    """Use predictable print characters and ASCII hyphens."""
    return (
        value.replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
        .replace("\u00a0", " ")
    )


def inline_markup(value: str) -> str:
    value = normalize_print_text(value.strip())
    tokens: list[str] = []

    def hold(fragment: str) -> str:
        tokens.append(fragment)
        return f"@@TOKEN{len(tokens) - 1}@@"

    def link_repl(match: re.Match[str]) -> str:
        label = html.escape(match.group(1), quote=False)
        url = html.escape(match.group(2), quote=True)
        return hold(f'<link href="{url}" color="#2D6687"><u>{label}</u></link>')

    value = re.sub(r"\[([^]]+)]\((https?://[^)]+)\)", link_repl, value)
    value = html.escape(value, quote=False)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", value)
    for index, token in enumerate(tokens):
        value = value.replace(f"@@TOKEN{index}@@", token)
    return value


def read_chapter(path: Path) -> tuple[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"Missing YAML front matter in {path}")
    front, body = parts[1], parts[2]
    title_match = re.search(r'^title:\s*["\']?(.+?)["\']?$', front, re.MULTILINE)
    if not title_match:
        raise ValueError(f"Missing title in {path}")
    return title_match.group(1), body.strip().splitlines()


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="BookSerif",
            fontSize=10.2,
            leading=15.2,
            textColor=INK,
            spaceAfter=8,
            alignment=TA_LEFT,
            allowWidows=0,
            allowOrphans=0,
        ),
        "chapter_label": ParagraphStyle(
            "ChapterLabel",
            fontName="BookSansBold",
            fontSize=9,
            leading=11,
            textColor=GOLD,
            tracking=1.7,
            spaceAfter=8,
        ),
        "chapter_title": ParagraphStyle(
            "ChapterTitle",
            fontName="BookSerifBold",
            fontSize=28,
            leading=33,
            textColor=NAVY,
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "H2",
            fontName="BookSerifBold",
            fontSize=17,
            leading=21,
            textColor=NAVY,
            spaceBefore=15,
            spaceAfter=7,
            keepWithNext=1,
        ),
        "h3": ParagraphStyle(
            "H3",
            fontName="BookSansBold",
            fontSize=11.5,
            leading=15,
            textColor=BLUE,
            spaceBefore=11,
            spaceAfter=5,
            keepWithNext=1,
        ),
        "caption": ParagraphStyle(
            "Caption",
            fontName="BookSerifItalic",
            fontSize=8.3,
            leading=11.3,
            textColor=MUTED,
            alignment=TA_CENTER,
            leftIndent=18,
            rightIndent=18,
            spaceBefore=3,
            spaceAfter=10,
        ),
        "quote": ParagraphStyle(
            "Quote",
            fontName="BookSerifItalic",
            fontSize=10.4,
            leading=15.5,
            textColor=NAVY,
            leftIndent=18,
            borderColor=GOLD,
            borderWidth=0,
            borderPadding=8,
            spaceBefore=5,
            spaceAfter=10,
        ),
        "list": ParagraphStyle(
            "List",
            fontName="BookSerif",
            fontSize=10,
            leading=14.5,
            textColor=INK,
            leftIndent=0,
            spaceAfter=3,
        ),
        "table_head": ParagraphStyle(
            "TableHead",
            fontName="BookSansBold",
            fontSize=7.6,
            leading=9.4,
            textColor=colors.white,
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            fontName="BookSans",
            fontSize=7.4,
            leading=9.5,
            textColor=INK,
        ),
        "toc": ParagraphStyle(
            "TOC",
            fontName="BookSerif",
            fontSize=13,
            leading=18,
            textColor=INK,
            leftIndent=12,
            spaceAfter=8,
        ),
    }


def image_flowable(path: Path, max_width: float = 6.25 * inch, max_height: float = 4.9 * inch) -> Image:
    with PILImage.open(path) as source:
        width, height = source.size
    scale = min(max_width / width, max_height / height)
    picture = Image(str(path), width=width * scale, height=height * scale)
    picture.hAlign = "CENTER"
    return picture


def parse_image(line: str) -> tuple[Path, str] | None:
    match = re.match(
        r"!\[([^]]*)]\(\{\{ site\.url }}\{\{ site\.baseurl }}/([^\)]+)\)(?:\{:[^}]+})?",
        line,
    )
    if not match:
        return None
    return ROOT / match.group(2), match.group(1)


def flush_paragraph(buffer: list[str], story: list, styles: dict[str, ParagraphStyle]) -> None:
    if buffer:
        story.append(Paragraph(inline_markup(" ".join(part.strip() for part in buffer)), styles["body"]))
        buffer.clear()


def markdown_story(lines: list[str], styles: dict[str, ParagraphStyle]) -> list:
    story: list = []
    paragraph: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        stripped = line.strip()

        if not stripped:
            flush_paragraph(paragraph, story, styles)
            index += 1
            continue

        if stripped == "<!-- pagebreak -->":
            flush_paragraph(paragraph, story, styles)
            story.append(PageBreak())
            index += 1
            continue

        image_info = parse_image(stripped)
        if image_info:
            flush_paragraph(paragraph, story, styles)
            image_path, alt = image_info
            if not image_path.exists():
                raise FileNotFoundError(image_path)
            picture = image_flowable(image_path)
            block = [Spacer(1, 5), picture]
            caption_index = index + 1
            while caption_index < len(lines) and not lines[caption_index].strip():
                caption_index += 1
            next_line = lines[caption_index].strip() if caption_index < len(lines) else ""
            if next_line.startswith("*") and next_line.endswith("*"):
                block.append(Paragraph(inline_markup(next_line), styles["caption"]))
                index = caption_index
            else:
                block.append(Paragraph(inline_markup(f"*{alt}*"), styles["caption"]))
            story.append(KeepTogether(block))
            index += 1
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph(paragraph, story, styles)
            table_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            rows = [[cell.strip() for cell in row.strip("|").split("|")] for row in table_lines]
            if len(rows) > 1 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]):
                rows.pop(1)
            table_data = []
            for row_index, row in enumerate(rows):
                style = styles["table_head"] if row_index == 0 else styles["table_cell"]
                table_data.append([Paragraph(inline_markup(cell), style) for cell in row])
            col_widths = [1.25 * inch, 2.05 * inch, 3.05 * inch] if len(rows[0]) == 3 else None
            table = Table(table_data, colWidths=col_widths, repeatRows=1, hAlign="CENTER")
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("GRID", (0, 0), (-1, -1), 0.35, RULE),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
                    ]
                )
            )
            story.extend([Spacer(1, 5), table, Spacer(1, 9)])
            continue

        heading = re.match(r"^(#{2,4})\s+(.+)$", stripped)
        if heading:
            flush_paragraph(paragraph, story, styles)
            level, text = len(heading.group(1)), heading.group(2)
            story.append(Paragraph(inline_markup(text), styles["h2" if level == 2 else "h3"]))
            index += 1
            continue

        if stripped.startswith(">"):
            flush_paragraph(paragraph, story, styles)
            quote_lines = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote_lines.append(lines[index].strip().lstrip(">").strip())
                index += 1
            story.append(Paragraph(inline_markup(" ".join(quote_lines)), styles["quote"]))
            continue

        bullet = re.match(r"^-\s+(.+)$", stripped)
        numbered = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if bullet or numbered:
            flush_paragraph(paragraph, story, styles)
            ordered = numbered is not None
            items: list[ListItem] = []
            start = int(numbered.group(1)) if numbered else 1
            while index < len(lines):
                current = lines[index].strip()
                match = re.match(r"^(\d+)\.\s+(.+)$", current) if ordered else re.match(r"^-\s+(.+)$", current)
                if not match:
                    break
                text = match.group(2) if ordered else match.group(1)
                items.append(ListItem(Paragraph(inline_markup(text), styles["list"]), leftIndent=8))
                index += 1
            list_options = {
                "bulletType": "1" if ordered else "bullet",
                "leftIndent": 25,
                "bulletFontName": "BookSans",
                "bulletFontSize": 8.5,
                "bulletColor": BLUE,
                "spaceAfter": 7,
            }
            if ordered:
                list_options["start"] = str(start)
            story.append(ListFlowable(items, **list_options))
            story.append(Spacer(1, 4))
            continue

        paragraph.append(stripped)
        index += 1

    flush_paragraph(paragraph, story, styles)
    return story


def draw_header_footer(canvas, doc) -> None:
    canvas.saveState()
    width, height = letter
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.45)
    canvas.line(doc.leftMargin, height - 0.54 * inch, width - doc.rightMargin, height - 0.54 * inch)
    canvas.setFillColor(MUTED)
    canvas.setFont("BookSans", 7.4)
    canvas.drawString(doc.leftMargin, height - 0.43 * inch, "WE USE ROBOTS TO BUILD KIDS")
    canvas.drawRightString(width - doc.rightMargin, height - 0.43 * inch, "CHAPTERS 1-4 REVIEW EDITION")
    canvas.setFont("BookSans", 8)
    canvas.drawCentredString(width / 2, 0.43 * inch, str(doc.page - 1))
    canvas.restoreState()


def draw_cover(canvas, doc) -> None:
    canvas.saveState()
    canvas.setTitle("We Use Robots to Build Kids - Chapters 1-4 Review Edition")
    canvas.setAuthor("Coach Ling")
    canvas.setSubject("FIRST LEGO League coaching philosophy for first-time volunteer coaches")
    canvas.restoreState()


def build() -> Path:
    register_fonts()
    styles = make_styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    chapter_data = [read_chapter(path) for path in CHAPTERS]

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.72 * inch,
        leftMargin=0.72 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.67 * inch,
        title="We Use Robots to Build Kids - Chapters 1-4 Review Edition",
        author="Coach Ling",
        subject="FIRST LEGO League coaching philosophy for first-time volunteer coaches",
    )

    story: list = [Spacer(1, 1.0 * inch)]
    cover_kicker = ParagraphStyle(
        "CoverKicker",
        fontName="BookSansBold",
        fontSize=10,
        leading=13,
        textColor=GOLD,
        alignment=TA_CENTER,
        tracking=2.3,
        spaceAfter=18,
    )
    cover_title = ParagraphStyle(
        "CoverTitle",
        fontName="BookSerifBold",
        fontSize=37,
        leading=44,
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceAfter=16,
    )
    cover_subtitle = ParagraphStyle(
        "CoverSubtitle",
        fontName="BookSerifItalic",
        fontSize=16,
        leading=22,
        textColor=BLUE,
        alignment=TA_CENTER,
        spaceAfter=25,
    )
    cover_author = ParagraphStyle(
        "CoverAuthor",
        fontName="BookSans",
        fontSize=11,
        leading=15,
        textColor=MUTED,
        alignment=TA_CENTER,
    )
    story.extend(
        [
            Paragraph("FIRST LEGO LEAGUE COACHING PHILOSOPHY", cover_kicker),
            HRFlowable(width="72%", thickness=2.2, color=GOLD, spaceAfter=26, hAlign="CENTER"),
            Paragraph("We Use Robots<br/>to Build Kids", cover_title),
            Paragraph("A coach's view from both sides of the judging-room door", cover_subtitle),
            Spacer(1, 0.55 * inch),
            Paragraph("CHAPTERS 1-4 REVIEW EDITION", cover_kicker),
            Paragraph("Coach Ling", cover_author),
            Spacer(1, 1.0 * inch),
            Paragraph("For first-time volunteer coaches", cover_author),
            PageBreak(),
        ]
    )

    story.extend(
        [
            Spacer(1, 0.3 * inch),
            Paragraph("Contents", styles["chapter_title"]),
            HRFlowable(width="100%", thickness=1.3, color=GOLD, spaceAfter=18),
        ]
    )
    for number, (title, _) in enumerate(chapter_data, start=1):
        clean_title = re.sub(r"^Chapter\s+\d+:\s*", "", title)
        story.append(Paragraph(f'<font color="#D69B2D">{number:02d}</font>&nbsp;&nbsp; {inline_markup(clean_title)}', styles["toc"]))
    story.extend(
        [
            Spacer(1, 0.45 * inch),
            HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=12),
            Paragraph(
                "This review edition contains the first four completed chapters of an ongoing manuscript. "
                "It is intended for editorial and family review; wording and placement may change before publication.",
                styles["body"],
            ),
        ]
    )

    for number, (title, lines) in enumerate(chapter_data, start=1):
        story.append(PageBreak())
        clean_title = re.sub(r"^Chapter\s+\d+:\s*", "", title)
        story.extend(
            [
                Spacer(1, 0.35 * inch),
                Paragraph(f"CHAPTER {number}", styles["chapter_label"]),
                Paragraph(inline_markup(clean_title), styles["chapter_title"]),
                HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceAfter=17),
            ]
        )
        story.extend(markdown_story(lines, styles))

    doc.build(story, onFirstPage=draw_cover, onLaterPages=draw_header_footer)
    return OUTPUT


if __name__ == "__main__":
    print(build())
