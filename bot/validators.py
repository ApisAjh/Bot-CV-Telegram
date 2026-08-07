"""Input validation helpers."""

from __future__ import annotations

import re
from typing import Tuple

# Simple but practical email regex
EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)

# Indonesian & international phone patterns
PHONE_RE = re.compile(
    r"^(\+62|62|0)[\s\-]?[0-9]{2,4}[\s\-]?[0-9]{3,4}[\s\-]?[0-9]{3,5}$"
    r"|^(\+[1-9]\d{0,3})[\s\-]?[0-9\s\-]{7,15}$"
)

YEAR_RE = re.compile(r"^(19|20)\d{2}$")
DATE_RE = re.compile(
    r"^(\d{1,2}[/\-\.]\d{1,2}[/\-\.](19|20)\d{2})$"  # DD/MM/YYYY
    r"|^((19|20)\d{2})$"  # YYYY only
)


def validate_email(text: str) -> Tuple[bool, str]:
    """Validate email address. Returns (is_valid, cleaned_or_error)."""
    cleaned = text.strip().lower()
    if not cleaned:
        return False, "Email tidak boleh kosong."
    if not EMAIL_RE.match(cleaned):
        return False, "Format email tidak valid. Contoh: nama@email.com"
    if len(cleaned) > 100:
        return False, "Email terlalu panjang."
    return True, cleaned


def validate_phone(text: str) -> Tuple[bool, str]:
    """Validate phone number (ID + international). Returns (is_valid, cleaned_or_error)."""
    cleaned = re.sub(r"[\s\-]", "", text.strip())
    if not cleaned:
        return False, "Nomor HP tidak boleh kosong."
    # Re-add original spacing-ish for display, but validate digits
    display = text.strip()
    if not PHONE_RE.match(display) and not re.match(r"^(\+?\d{8,15})$", cleaned):
        return False, (
            "Format nomor HP tidak valid.\n"
            "Contoh: 08123456789 / +628123456789 / 0812-3456-7890"
        )
    if len(cleaned) > 20:
        return False, "Nomor HP terlalu panjang."
    return True, display


def validate_required(text: str, field_name: str = "Field") -> Tuple[bool, str]:
    """Ensure non-empty text after stripping."""
    cleaned = text.strip()
    if not cleaned:
        return False, f"{field_name} tidak boleh kosong."
    if len(cleaned) > 200:
        return False, f"{field_name} terlalu panjang (maks. 200 karakter)."
    return True, cleaned


def validate_year(text: str, allow_present: bool = False) -> Tuple[bool, str]:
    """Validate a year (YYYY) or 'Present' / 'Sekarang'."""
    cleaned = text.strip()
    lower = cleaned.lower()
    if allow_present and lower in {"present", "sekarang", "now", "current", "-"}:
        return True, "Present"
    if not YEAR_RE.match(cleaned):
        return False, "Tahun harus 4 digit (contoh: 2020). Gunakan 'Present' jika masih berlangsung."
    year = int(cleaned)
    if year < 1950 or year > 2035:
        return False, "Tahun di luar rentang wajar (1950–2035)."
    return True, cleaned


def validate_date(text: str) -> Tuple[bool, str]:
    """Validate birth date (DD/MM/YYYY or YYYY)."""
    cleaned = text.strip()
    if not cleaned:
        return False, "Tanggal lahir tidak boleh kosong."
    if not DATE_RE.match(cleaned):
        return False, "Format tanggal: DD/MM/YYYY atau YYYY. Contoh: 15/08/1998"
    return True, cleaned


def validate_url(text: str, allow_empty: bool = True) -> Tuple[bool, str]:
    """Basic URL validation for optional links."""
    cleaned = text.strip()
    if not cleaned:
        return True if allow_empty else (False, "URL tidak boleh kosong."), ""
    if not re.match(r"^https?://", cleaned, re.I):
        # Auto-prepend https if missing
        if re.match(r"^[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", cleaned):
            cleaned = "https://" + cleaned
        else:
            return False, "URL harus diawali http:// atau https://"
    if len(cleaned) > 200:
        return False, "URL terlalu panjang."
    return True, cleaned


def parse_list_input(text: str) -> list[str]:
    """
    Parse multi-value input separated by comma, newline, or pipe.
    Used for skills and languages.
    """
    parts = re.split(r"[,|\n]+", text)
    result = []
    seen = set()
    for p in parts:
        item = p.strip()
        if item and item.lower() not in seen:
            seen.add(item.lower())
            result.append(item)
    return result
