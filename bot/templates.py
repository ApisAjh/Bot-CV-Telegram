"""Template metadata and preview helpers (extendable for future visual previews)."""

from __future__ import annotations

from bot.config import TEMPLATES


def get_template_info(key: str) -> dict[str, str]:
    """Return template metadata or empty dict if unknown."""
    return TEMPLATES.get(key, {})


def list_templates() -> list[tuple[str, dict[str, str]]]:
    """Return ordered list of (key, info) pairs."""
    return list(TEMPLATES.items())
