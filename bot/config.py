"""Configuration and constants for CV Builder Bot."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Final

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    """Application configuration loaded from environment variables."""

    telegram_token: str
    webhook_url: str
    webhook_secret: str = ""  # opsional, tidak dipakai untuk verifikasi saat ini

    @classmethod
    def from_env(cls) -> "Config":
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        url = os.getenv("WEBHOOK_URL", "").strip().rstrip("/")
        secret = os.getenv("WEBHOOK_SECRET", "").strip()  # opsional

        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not url:
            raise ValueError("WEBHOOK_URL is required")

        return cls(
            telegram_token=token,
            webhook_url=url,
            webhook_secret=secret,
        )


# Conversation states
(
    STATE_FULL_NAME,
    STATE_POSITION,
    STATE_BIRTH_PLACE,
    STATE_BIRTH_DATE,
    STATE_PHONE,
    STATE_EMAIL,
    STATE_ADDRESS,
    STATE_CITY,
    STATE_ABOUT,
    STATE_EDU_SCHOOL,
    STATE_EDU_MAJOR,
    STATE_EDU_START,
    STATE_EDU_END,
    STATE_EDU_MORE,
    STATE_EXP_COMPANY,
    STATE_EXP_POSITION,
    STATE_EXP_START,
    STATE_EXP_END,
    STATE_EXP_DESC,
    STATE_EXP_MORE,
    STATE_SKILLS,
    STATE_LANGUAGES,
    STATE_CERT_NAME,
    STATE_CERT_MORE,
    STATE_ACHIEVEMENT,
    STATE_ACHIEVEMENT_MORE,
    STATE_LINKS,
    STATE_PHOTO,
    STATE_TEMPLATE,
    STATE_PREVIEW,
    STATE_EDIT_CHOICE,
) = range(31)

# Template identifiers
TEMPLATE_MODERN: Final = "modern"
TEMPLATE_PROFESSIONAL: Final = "professional"
TEMPLATE_CREATIVE: Final = "creative"
TEMPLATE_ATS: Final = "ats"

TEMPLATES: Final[dict[str, dict[str, str]]] = {
    TEMPLATE_MODERN: {
        "name": "Modern",
        "emoji": "🎨",
        "description": "Clean sidebar layout, modern typography, accent color highlights.",
    },
    TEMPLATE_PROFESSIONAL: {
        "name": "Professional",
        "emoji": "💼",
        "description": "Classic two-column design, formal structure, ideal for corporate roles.",
    },
    TEMPLATE_CREATIVE: {
        "name": "Creative",
        "emoji": "✨",
        "description": "Bold header, visual skill chips, perfect for design & creative fields.",
    },
    TEMPLATE_ATS: {
        "name": "ATS Friendly",
        "emoji": "📄",
        "description": "Single-column, plain structure optimized for Applicant Tracking Systems.",
    },
}

# Colors (RGB 0-1 for ReportLab)
COLORS: Final[dict[str, tuple[float, float, float]]] = {
    "navy": (0.10, 0.20, 0.35),
    "dark_gray": (0.25, 0.25, 0.28),
    "medium_gray": (0.45, 0.45, 0.48),
    "light_gray": (0.92, 0.93, 0.94),
    "white": (1.0, 1.0, 1.0),
    "black": (0.05, 0.05, 0.05),
    "accent": (0.15, 0.35, 0.55),
    "soft_blue": (0.85, 0.90, 0.95),
}

# Page setup
PAGE_WIDTH: Final = 595.27  # A4
PAGE_HEIGHT: Final = 841.89
MARGIN: Final = 40

# Max items
MAX_EDUCATION: Final = 5
MAX_EXPERIENCE: Final = 8
MAX_SKILLS: Final = 20
MAX_LANGUAGES: Final = 8
MAX_CERTIFICATES: Final = 6
MAX_ACHIEVEMENTS: Final = 6

# Photo constraints
MAX_PHOTO_SIZE_MB: Final = 5
PHOTO_SIZE: Final = 120  # pixels for PDF
