"""Professional CV PDF generation using ReportLab."""

from __future__ import annotations

import io
import logging
from typing import Any

from PIL import Image as PILImage
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from bot.config import (
    COLORS,
    MARGIN,
    PAGE_HEIGHT,
    PAGE_WIDTH,
    PHOTO_SIZE,
    TEMPLATE_ATS,
    TEMPLATE_CREATIVE,
    TEMPLATE_MODERN,
    TEMPLATE_PROFESSIONAL,
)
from bot.helpers import format_year_range, safe_get

logger = logging.getLogger(__name__)

# Convert 0-1 RGB to ReportLab Color
def _c(key: str) -> Color:
    r, g, b = COLORS[key]
    return Color(r, g, b)


class ColoredBox(Flowable):
    """Simple colored rectangle used as accent / section background."""

    def __init__(self, width: float, height: float, color: Color):
        super().__init__()
        self.width = width
        self.height = height
        self.color = color

    def draw(self) -> None:
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)


class SkillChip(Flowable):
    """Modern skill badge / chip."""

    def __init__(self, text: str, bg: Color, fg: Color, padding: float = 4):
        super().__init__()
        self.text = text
        self.bg = bg
        self.fg = fg
        self.padding = padding
        self._w = 0.0
        self._h = 14.0

    def wrap(self, availWidth: float, availHeight: float) -> tuple[float, float]:
        self.canv.setFont("Helvetica", 8)
        tw = self.canv.stringWidth(self.text, "Helvetica", 8)
        self._w = tw + self.padding * 2 + 4
        return self._w, self._h

    def draw(self) -> None:
        self.canv.setFillColor(self.bg)
        self.canv.roundRect(0, 0, self._w, self._h, 3, fill=1, stroke=0)
        self.canv.setFillColor(self.fg)
        self.canv.setFont("Helvetica", 8)
        self.canv.drawString(self.padding + 2, 3.5, self.text)


def _make_styles() -> dict[str, ParagraphStyle]:
    styles = getSampleStyleSheet()
    custom = {
        "name": ParagraphStyle(
            "CVName",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=_c("navy"),
            spaceAfter=2,
            leading=24,
        ),
        "position": ParagraphStyle(
            "CVPosition",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            textColor=_c("accent"),
            spaceAfter=6,
            leading=14,
        ),
        "section": ParagraphStyle(
            "CVSection",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=_c("navy"),
            spaceBefore=10,
            spaceAfter=4,
            leading=14,
        ),
        "body": ParagraphStyle(
            "CVBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=_c("dark_gray"),
            leading=12,
            alignment=TA_JUSTIFY,
        ),
        "small": ParagraphStyle(
            "CVSmall",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=_c("medium_gray"),
            leading=10,
        ),
        "contact": ParagraphStyle(
            "CVContact",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=_c("dark_gray"),
            leading=11,
        ),
        "job_title": ParagraphStyle(
            "CVJobTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            textColor=_c("black"),
            leading=12,
        ),
        "company": ParagraphStyle(
            "CVCompany",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=_c("accent"),
            leading=11,
        ),
        "bullet": ParagraphStyle(
            "CVBullet",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            textColor=_c("dark_gray"),
            leading=11,
            leftIndent=8,
        ),
        "chip_text": ParagraphStyle(
            "CVChip",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=_c("navy"),
            leading=10,
        ),
    }
    return custom


def _process_photo(photo_bytes: bytes | None) -> Image | None:
    """Resize and prepare profile photo for PDF."""
    if not photo_bytes:
        return None
    try:
        img = PILImage.open(io.BytesIO(photo_bytes))
        img = img.convert("RGB")
        # Center crop to square
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img = img.resize((PHOTO_SIZE, PHOTO_SIZE), PILImage.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85, optimize=True)
        buf.seek(0)
        return Image(buf, width=PHOTO_SIZE * 0.55, height=PHOTO_SIZE * 0.55)
    except Exception as exc:
        logger.warning("Failed to process photo: %s", exc)
        return None


def _section_header(title: str, styles: dict) -> list:
    """Section title + thin accent line."""
    return [
        Paragraph(title.upper(), styles["section"]),
        HRFlowable(
            width="100%",
            thickness=1.2,
            color=_c("navy"),
            spaceBefore=0,
            spaceAfter=6,
        ),
    ]


def _build_header(data: dict[str, Any], styles: dict, photo: Image | None) -> list:
    """Build the top header block."""
    name = safe_get(data, "full_name", "Nama Lengkap")
    position = safe_get(data, "position", "")
    phone = safe_get(data, "phone", "")
    email = safe_get(data, "email", "")
    address = safe_get(data, "address", "")
    city = safe_get(data, "city", "")
    location = ", ".join(filter(None, [address, city])) if address or city else ""

    links = data.get("links") or {}
    contact_parts = []
    if phone:
        contact_parts.append(phone)
    if email:
        contact_parts.append(email)
    if location:
        contact_parts.append(location)
    for key in ("github", "linkedin", "portfolio", "website"):
        val = links.get(key)
        if val:
            contact_parts.append(val.replace("https://", "").replace("http://", ""))

    contact_line = "  •  ".join(contact_parts)

    left_content = [
        Paragraph(name, styles["name"]),
        Paragraph(position, styles["position"]) if position else Spacer(1, 2),
        Paragraph(contact_line, styles["contact"]) if contact_line else Spacer(1, 1),
    ]

    if photo:
        table_data = [[left_content, photo]]
        table = Table(table_data, colWidths=[PAGE_WIDTH - 2 * MARGIN - 80, 75])
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return [table, Spacer(1, 8)]
    return left_content + [Spacer(1, 6)]


def _build_about(data: dict[str, Any], styles: dict) -> list:
    about = data.get("about")
    if not about:
        return []
    elements = _section_header("Tentang Saya", styles)
    elements.append(Paragraph(about, styles["body"]))
    elements.append(Spacer(1, 4))
    return elements


def _build_experience(data: dict[str, Any], styles: dict) -> list:
    experience = data.get("experience") or []
    if not experience:
        return []
    # Sort newest first (by start year descending)
    def sort_key(e: dict) -> int:
        try:
            return int(e.get("start", "0") or "0")
        except ValueError:
            return 0

    experience = sorted(experience, key=sort_key, reverse=True)

    elements = _section_header("Pengalaman Kerja", styles)
    for exp in experience:
        company = exp.get("company", "—")
        pos = exp.get("position", "—")
        years = format_year_range(exp.get("start", ""), exp.get("end", ""))
        desc = exp.get("description", "")

        header = f"<b>{pos}</b>  —  {company}  |  {years}"
        elements.append(Paragraph(header, styles["job_title"]))
        if desc:
            # Split description into bullets if user used newlines or •
            bullets = [b.strip(" •-\t") for b in desc.replace("•", "\n").split("\n") if b.strip()]
            for b in bullets:
                elements.append(Paragraph(f"• {b}", styles["bullet"]))
        elements.append(Spacer(1, 4))
    return elements


def _build_education(data: dict[str, Any], styles: dict) -> list:
    education = data.get("education") or []
    if not education:
        return []

    def sort_key(e: dict) -> int:
        try:
            return int(e.get("start", "0") or "0")
        except ValueError:
            return 0

    education = sorted(education, key=sort_key, reverse=True)

    elements = _section_header("Pendidikan", styles)
    for edu in education:
        school = edu.get("school", "—")
        major = edu.get("major", "")
        years = format_year_range(edu.get("start", ""), edu.get("end", ""))
        line = f"<b>{school}</b>"
        if major:
            line += f"  —  {major}"
        line += f"  |  {years}"
        elements.append(Paragraph(line, styles["job_title"]))
        elements.append(Spacer(1, 3))
    return elements


def _build_skills(data: dict[str, Any], styles: dict) -> list:
    skills = data.get("skills") or []
    if not skills:
        return []
    elements = _section_header("Skill", styles)
    # Chip-style using paragraph with separators (reliable across templates)
    chip_line = "  ·  ".join(skills)
    elements.append(Paragraph(chip_line, styles["chip_text"]))
    elements.append(Spacer(1, 4))
    return elements


def _build_languages(data: dict[str, Any], styles: dict) -> list:
    languages = data.get("languages") or []
    if not languages:
        return []
    elements = _section_header("Bahasa", styles)
    for lang in languages:
        elements.append(Paragraph(f"• {lang}", styles["bullet"]))
    elements.append(Spacer(1, 2))
    return elements


def _build_certificates(data: dict[str, Any], styles: dict) -> list:
    certs = data.get("certificates") or []
    if not certs:
        return []
    elements = _section_header("Sertifikat", styles)
    for c in certs:
        elements.append(Paragraph(f"• {c}", styles["bullet"]))
    elements.append(Spacer(1, 2))
    return elements


def _build_achievements(data: dict[str, Any], styles: dict) -> list:
    achievements = data.get("achievements") or []
    if not achievements:
        return []
    elements = _section_header("Prestasi", styles)
    for a in achievements:
        elements.append(Paragraph(f"• {a}", styles["bullet"]))
    elements.append(Spacer(1, 2))
    return elements


def generate_cv_pdf(user_data: dict[str, Any]) -> bytes:
    """
    Generate a professional CV PDF from collected user data.
    Returns PDF as bytes.
    """
    template = user_data.get("template", TEMPLATE_MODERN)
    styles = _make_styles()
    photo = _process_photo(user_data.get("photo_bytes"))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN - 5,
        bottomMargin=MARGIN,
    )

    story: list = []

    # Header
    story.extend(_build_header(user_data, styles, photo))
    story.append(
        HRFlowable(
            width="100%",
            thickness=2,
            color=_c("navy"),
            spaceBefore=2,
            spaceAfter=8,
        )
    )

    # Body sections – order optimized for readability
    story.extend(_build_about(user_data, styles))
    story.extend(_build_experience(user_data, styles))
    story.extend(_build_education(user_data, styles))
    story.extend(_build_skills(user_data, styles))
    story.extend(_build_languages(user_data, styles))
    story.extend(_build_certificates(user_data, styles))
    story.extend(_build_achievements(user_data, styles))

    # Subtle template accent at the very bottom
    story.append(Spacer(1, 12))
    story.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=_c("light_gray"),
            spaceBefore=4,
            spaceAfter=2,
        )
    )
    story.append(
        Paragraph(
            f"Generated with Bot CV Telegram  •  Template: {template.title()}",
            styles["small"],
        )
    )

    try:
        doc.build(story)
    except Exception as exc:
        logger.exception("PDF build failed: %s", exc)
        raise

    buffer.seek(0)
    return buffer.read()
