"""Inline and reply keyboards for the bot."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove

from bot.config import TEMPLATES


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Start / main menu buttons."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📄 Buat CV Baru", callback_data="create_cv")],
            [
                InlineKeyboardButton("ℹ Bantuan", callback_data="help"),
                InlineKeyboardButton("📋 Contoh CV", callback_data="example"),
            ],
        ]
    )


def yes_no_keyboard(prefix: str) -> InlineKeyboardMarkup:
    """Yes / No for 'add more' questions."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Ya", callback_data=f"{prefix}_yes"),
                InlineKeyboardButton("❌ Tidak", callback_data=f"{prefix}_no"),
            ]
        ]
    )


def skip_cancel_keyboard(include_back: bool = False) -> InlineKeyboardMarkup:
    """Skip + Cancel (and optional Back)."""
    row = [
        InlineKeyboardButton("⏭ Skip", callback_data="skip"),
        InlineKeyboardButton("🗑 Batal", callback_data="cancel"),
    ]
    buttons = [row]
    if include_back:
        buttons.insert(0, [InlineKeyboardButton("⬅ Kembali", callback_data="back")])
    return InlineKeyboardMarkup(buttons)


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🗑 Batal", callback_data="cancel")]]
    )


def back_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⬅ Kembali", callback_data="back"),
                InlineKeyboardButton("🗑 Batal", callback_data="cancel"),
            ]
        ]
    )


def template_keyboard() -> InlineKeyboardMarkup:
    """Choose CV template."""
    rows = []
    for key, info in TEMPLATES.items():
        rows.append(
            [
                InlineKeyboardButton(
                    f"{info['emoji']} {info['name']}",
                    callback_data=f"template_{key}",
                )
            ]
        )
    rows.append([InlineKeyboardButton("🗑 Batal", callback_data="cancel")])
    return InlineKeyboardMarkup(rows)


def preview_keyboard() -> InlineKeyboardMarkup:
    """After summary preview."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Generate PDF", callback_data="generate")],
            [
                InlineKeyboardButton("✏ Edit Data", callback_data="edit"),
                InlineKeyboardButton("🗑 Batal", callback_data="cancel"),
            ],
        ]
    )


def edit_menu_keyboard() -> InlineKeyboardMarkup:
    """Choose which section to edit."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("👤 Info Pribadi", callback_data="edit_personal")],
            [InlineKeyboardButton("🎓 Pendidikan", callback_data="edit_education")],
            [InlineKeyboardButton("💼 Pengalaman", callback_data="edit_experience")],
            [InlineKeyboardButton("🛠 Skill & Bahasa", callback_data="edit_skills")],
            [InlineKeyboardButton("📜 Sertifikat / Prestasi", callback_data="edit_extra")],
            [InlineKeyboardButton("🔗 Link & Foto", callback_data="edit_links")],
            [InlineKeyboardButton("🎨 Ganti Template", callback_data="edit_template")],
            [InlineKeyboardButton("⬅ Kembali ke Preview", callback_data="back_preview")],
        ]
    )


def photo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⏭ Skip (Tanpa Foto)", callback_data="skip_photo")],
            [InlineKeyboardButton("🗑 Batal", callback_data="cancel")],
        ]
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
