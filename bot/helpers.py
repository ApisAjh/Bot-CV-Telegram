"""Utility helpers for CV Builder Bot."""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure basic logging for the application."""
    logging.basicConfig(
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def clean_text(text: str | None) -> str:
    """Strip and normalize whitespace."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip())


def format_year_range(start: str, end: str) -> str:
    """Format year range for display."""
    start = clean_text(start)
    end = clean_text(end) or "Present"
    return f"{start} – {end}"


def safe_get(data: dict[str, Any], key: str, default: str = "—") -> str:
    """Safely get a string value from user data."""
    value = data.get(key)
    if value is None or (isinstance(value, str) and not value.strip()):
        return default
    return str(value).strip()


def truncate(text: str, max_len: int = 80) -> str:
    """Truncate text with ellipsis if too long."""
    text = clean_text(text)
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def progress_bar(current: int, total: int = 10) -> str:
    """Simple text progress indicator."""
    filled = min(current, total)
    bar = "█" * filled + "░" * (total - filled)
    percent = int((filled / total) * 100) if total else 0
    return f"[{bar}] {percent}%"


def build_summary(user_data: dict[str, Any]) -> str:
    """Build a human-readable summary of collected CV data."""
    lines: list[str] = []

    lines.append("📋 *RINGKASAN CV*\n")

    # Personal
    lines.append("👤 *Informasi Pribadi*")
    lines.append(f"• Nama: {safe_get(user_data, 'full_name')}")
    lines.append(f"• Posisi: {safe_get(user_data, 'position')}")
    lines.append(f"• Tempat, Tgl Lahir: {safe_get(user_data, 'birth_place')}, {safe_get(user_data, 'birth_date')}")
    lines.append(f"• HP: {safe_get(user_data, 'phone')}")
    lines.append(f"• Email: {safe_get(user_data, 'email')}")
    lines.append(f"• Alamat: {safe_get(user_data, 'address')}, {safe_get(user_data, 'city')}")
    if user_data.get("about"):
        lines.append(f"• Tentang: {truncate(user_data['about'], 100)}")

    # Education
    education = user_data.get("education") or []
    if education:
        lines.append("\n🎓 *Pendidikan*")
        for edu in education:
            lines.append(
                f"• {edu.get('school', '—')} — {edu.get('major', '—')} "
                f"({edu.get('start', '?')}–{edu.get('end', '?')})"
            )

    # Experience
    experience = user_data.get("experience") or []
    if experience:
        lines.append("\n💼 *Pengalaman Kerja*")
        for exp in experience:
            lines.append(
                f"• {exp.get('position', '—')} @ {exp.get('company', '—')} "
                f"({exp.get('start', '?')}–{exp.get('end', '?')})"
            )

    # Skills
    skills = user_data.get("skills") or []
    if skills:
        lines.append("\n🛠 *Skill*")
        lines.append("• " + " | ".join(skills[:15]))

    # Languages
    languages = user_data.get("languages") or []
    if languages:
        lines.append("\n🌐 *Bahasa*")
        lines.append("• " + ", ".join(languages))

    # Certificates
    certificates = user_data.get("certificates") or []
    if certificates:
        lines.append("\n📜 *Sertifikat*")
        for cert in certificates:
            lines.append(f"• {cert}")

    # Achievements
    achievements = user_data.get("achievements") or []
    if achievements:
        lines.append("\n🏆 *Prestasi*")
        for ach in achievements:
            lines.append(f"• {ach}")

    # Links
    links = user_data.get("links") or {}
    if any(links.values()):
        lines.append("\n🔗 *Link*")
        for key, val in links.items():
            if val:
                lines.append(f"• {key.title()}: {val}")

    # Photo & Template
    has_photo = "✓" if user_data.get("photo_bytes") else "✗"
    lines.append(f"\n📷 Foto: {has_photo}")
    template = user_data.get("template", "modern")
    from bot.config import TEMPLATES

    tinfo = TEMPLATES.get(template, {})
    lines.append(f"🎨 Template: {tinfo.get('emoji', '')} {tinfo.get('name', template)}")

    return "\n".join(lines)


def clear_user_data(context: Any) -> None:
    """Remove all temporary CV data from context after PDF generation."""
    keys_to_keep = set()  # nothing to keep
    for key in list(context.user_data.keys()):
        if key not in keys_to_keep:
            del context.user_data[key]
    logger.info("User data cleared after PDF generation")
