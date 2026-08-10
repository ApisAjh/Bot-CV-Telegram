"""All message and callback handlers for CV Builder Bot."""

from __future__ import annotations

import logging
from typing import Any

from telegram import InputFile, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from bot.config import (
    MAX_ACHIEVEMENTS,
    MAX_CERTIFICATES,
    MAX_EDUCATION,
    MAX_EXPERIENCE,
    MAX_PHOTO_SIZE_MB,
    STATE_ABOUT,
    STATE_ACHIEVEMENT,
    STATE_ACHIEVEMENT_MORE,
    STATE_ADDRESS,
    STATE_BIRTH_DATE,
    STATE_BIRTH_PLACE,
    STATE_CERT_MORE,
    STATE_CERT_NAME,
    STATE_CITY,
    STATE_EDU_END,
    STATE_EDU_MAJOR,
    STATE_EDU_MORE,
    STATE_EDU_SCHOOL,
    STATE_EDU_START,
    STATE_EMAIL,
    STATE_EXP_COMPANY,
    STATE_EXP_DESC,
    STATE_EXP_END,
    STATE_EXP_MORE,
    STATE_EXP_POSITION,
    STATE_EXP_START,
    STATE_FULL_NAME,
    STATE_LANGUAGES,
    STATE_LINKS,
    STATE_PHONE,
    STATE_PHOTO,
    STATE_POSITION,
    STATE_PREVIEW,
    STATE_SKILLS,
    STATE_TEMPLATE,
    TEMPLATES,
)
from bot.helpers import build_summary, clean_text, clear_user_data, progress_bar
from bot.keyboards import (
    cancel_keyboard,
    main_menu_keyboard,
    photo_keyboard,
    preview_keyboard,
    skip_cancel_keyboard,
    template_keyboard,
    yes_no_keyboard,
)
from bot.pdf_generator import generate_cv_pdf
from bot.validators import (
    parse_list_input,
    validate_date,
    validate_email,
    validate_phone,
    validate_required,
    validate_url,
    validate_year,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Entry & global commands
# ---------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start – welcome message + main menu."""
    user = update.effective_user
    name = user.first_name if user else "teman"
    text = (
        f"Halo, *{name}*! 👋\n\n"
        "Selamat datang di *Bot CV Telegram*.\n"
        "Saya akan membantu kamu membuat Curriculum Vitae profesional "
        "langsung dari chat Telegram, lalu menghasilkan file PDF siap pakai.\n\n"
        "✨ *Fitur:*\n"
        "• Pengumpulan data langkah demi langkah\n"
        "• Validasi email & nomor HP\n"
        "• Upload foto profil (opsional)\n"
        "• 4 template modern\n"
        "• Preview sebelum generate\n"
        "• PDF tajam & siap dilamar\n\n"
        "⚠️ *DISCLAIMER* ⚠️\n"
        "Bot dapat mengrestart ulang jika kamu meninggalkan bot dalam pembuatan CV dengan waktu lebih dari 10 menit\n\n"
        "Data kamu hanya disimpan sementara dan otomatis dihapus setelah PDF dibuat.\n\n"
        "Pilih menu di bawah untuk mulai:"
    )
    if update.message:
        await update.message.reply_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_keyboard(),
        )
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_keyboard(),
        )
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help information."""
    text = (
        "ℹ *Bantuan Bot CV Telegram*\n\n"
        "*Cara pakai:*\n"
        "1. Tekan *Buat CV Baru*\n"
        "2. Isi data secara bertahap (nama, kontak, pendidikan, dll.)\n"
        "3. Upload foto profil (bisa di-skip)\n"
        "4. Pilih template CV\n"
        "5. Review ringkasan → Generate PDF\n\n"
        "*Perintah:*\n"
        "/start – Menu utama\n"
        "/new – Mulai buat CV baru\n"
        "/cancel – Batalkan proses\n"
        "/help – Tampilkan bantuan ini\n\n"
        "*Tips:*\n"
        "• Gunakan tombol Skip untuk field opsional\n"
        "• Skill & bahasa bisa dipisah koma atau baris baru\n"
        "• Deskripsi pekerjaan boleh multi-baris\n"
        "• Semua data dihapus otomatis setelah PDF selesai"
    )
    target = update.callback_query or update.message
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu_keyboard()
        )


async def example_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show example of filled CV structure."""
    text = (
        "📋 *Contoh Data CV*\n\n"
        "👤 *Informasi Pribadi*\n"
        "Nama: Andi Pratama\n"
        "Posisi: Backend Developer\n"
        "Tempat, Tgl Lahir: Jakarta, 12/03/1998\n"
        "HP: 081234567890\n"
        "Email: andi.pratama@email.com\n"
        "Alamat: Jl. Merdeka No. 10, Jakarta Selatan\n\n"
        "🎓 *Pendidikan*\n"
        "Universitas Indonesia – Teknik Informatika (2016–2020)\n\n"
        "💼 *Pengalaman*\n"
        "Backend Developer @ PT Digital Maju (2021–Present)\n"
        "• Membangun REST API dengan FastAPI & PostgreSQL\n"
        "• Optimasi query & caching Redis\n\n"
        "🛠 *Skill*\n"
        "Python, FastAPI, PostgreSQL, Redis, Docker, Git\n\n"
        "🌐 *Bahasa*\n"
        "Indonesia (Native), English (Professional)\n\n"
        "Tekan *Buat CV Baru* untuk mulai dengan data kamu sendiri."
    )
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu_keyboard()
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the current conversation and clear data."""
    clear_user_data(context)
    text = "❌ Proses pembuatan CV dibatalkan.\n\nKetik /start untuk kembali ke menu utama."
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text)
    elif update.message:
        await update.message.reply_text(text)
    return ConversationHandler.END


# ---------------------------------------------------------------------------
# Start CV creation
# ---------------------------------------------------------------------------

async def start_create_cv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Initialize user_data and ask for full name."""
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "📄 *Mari buat CV profesional kamu!*\n\n"
            f"{progress_bar(1)}\n\n"
            "Langkah 1/10 – *Nama Lengkap*\n"
            "Ketik nama lengkap kamu (contoh: Andi Pratama):",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=cancel_keyboard(),
        )
    else:
        await update.message.reply_text(
            "📄 *Mari buat CV profesional kamu!*\n\n"
            f"{progress_bar(1)}\n\n"
            "Langkah 1/10 – *Nama Lengkap*\n"
            "Ketik nama lengkap kamu (contoh: Andi Pratama):",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=cancel_keyboard(),
        )

    context.user_data.clear()
    context.user_data["education"] = []
    context.user_data["experience"] = []
    context.user_data["skills"] = []
    context.user_data["languages"] = []
    context.user_data["certificates"] = []
    context.user_data["achievements"] = []
    context.user_data["links"] = {}
    context.user_data["_current_edu"] = {}
    context.user_data["_current_exp"] = {}
    return STATE_FULL_NAME


# ---------------------------------------------------------------------------
# Personal information handlers
# ---------------------------------------------------------------------------

async def receive_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_required(update.message.text, "Nama lengkap")
    if not ok:
        await update.message.reply_text(f"⚠️ {result}\n\nKetik nama lengkap kamu:")
        return STATE_FULL_NAME
    context.user_data["full_name"] = result
    await update.message.reply_text(
        f"{progress_bar(2)}\n\n"
        "Langkah 2/10 – *Posisi yang Diinginkan*\n"
        "Contoh: Backend Developer / Graphic Designer / Data Analyst",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=cancel_keyboard(),
    )
    return STATE_POSITION


async def receive_position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_required(update.message.text, "Posisi")
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_POSITION
    context.user_data["position"] = result
    await update.message.reply_text(
        f"{progress_bar(3)}\n\n"
        "Langkah 3/10 – *Tempat Lahir*\n"
        "Contoh: Jakarta / Bandung / Surabaya",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=cancel_keyboard(),
    )
    return STATE_BIRTH_PLACE


async def receive_birth_place(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_required(update.message.text, "Tempat lahir")
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_BIRTH_PLACE
    context.user_data["birth_place"] = result
    await update.message.reply_text(
        f"{progress_bar(3)}\n\n"
        "Langkah 3/10 – *Tanggal Lahir*\n"
        "Format: DD/MM/YYYY atau YYYY\n"
        "Contoh: 15/08/1998",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=cancel_keyboard(),
    )
    return STATE_BIRTH_DATE


async def receive_birth_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_date(update.message.text)
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_BIRTH_DATE
    context.user_data["birth_date"] = result
    await update.message.reply_text(
        f"{progress_bar(4)}\n\n"
        "Langkah 4/10 – *Nomor HP*\n"
        "Contoh: 08123456789 / +628123456789",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=cancel_keyboard(),
    )
    return STATE_PHONE


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_phone(update.message.text)
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_PHONE
    context.user_data["phone"] = result
    await update.message.reply_text(
        f"{progress_bar(5)}\n\n"
        "Langkah 5/10 – *Email*\n"
        "Contoh: nama@email.com",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=cancel_keyboard(),
    )
    return STATE_EMAIL


async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_email(update.message.text)
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_EMAIL
    context.user_data["email"] = result
    await update.message.reply_text(
        f"{progress_bar(6)}\n\n"
        "Langkah 6/10 – *Alamat*\n"
        "Contoh: Jl. Merdeka No. 10, RT 02/RW 03",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=cancel_keyboard(),
    )
    return STATE_ADDRESS


async def receive_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_required(update.message.text, "Alamat")
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_ADDRESS
    context.user_data["address"] = result
    await update.message.reply_text(
        f"{progress_bar(6)}\n\n"
        "Langkah 6/10 – *Kota*\n"
        "Contoh: Jakarta Selatan / Bandung",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=cancel_keyboard(),
    )
    return STATE_CITY


async def receive_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_required(update.message.text, "Kota")
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_CITY
    context.user_data["city"] = result
    await update.message.reply_text(
        f"{progress_bar(7)}\n\n"
        "Langkah 7/10 – *Tentang Saya* (opsional)\n"
        "Tuliskan ringkasan singkat tentang dirimu (2–4 kalimat).\n"
        "Atau tekan Skip jika ingin melewati.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=skip_cancel_keyboard(),
    )
    return STATE_ABOUT


async def receive_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = clean_text(update.message.text)
    if len(text) > 600:
        await update.message.reply_text("⚠️ Terlalu panjang (maks. ~600 karakter). Coba dipersingkat.")
        return STATE_ABOUT
    context.user_data["about"] = text
    return await _ask_education(update, context)


async def skip_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    context.user_data["about"] = ""
    await update.callback_query.edit_message_text("⏭ Tentang Saya dilewati.")
    return await _ask_education(update, context, from_callback=True)


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------

async def _ask_education(
    update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback: bool = False
) -> int:
    msg = (
        f"{progress_bar(8)}\n\n"
        "Langkah 8/10 – *Pendidikan*\n"
        "Nama Sekolah / Universitas:\n"
        "Contoh: Universitas Indonesia\n\n"
        "Atau tekan Skip jika tidak ingin menambahkan."
    )
    if from_callback:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=skip_cancel_keyboard(),
        )
    else:
        await update.message.reply_text(
            msg, parse_mode=ParseMode.MARKDOWN, reply_markup=skip_cancel_keyboard()
        )
    context.user_data["_current_edu"] = {}
    return STATE_EDU_SCHOOL


async def receive_edu_school(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_required(update.message.text, "Nama sekolah/universitas")
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_EDU_SCHOOL
    context.user_data["_current_edu"]["school"] = result
    await update.message.reply_text(
        "Jurusan / Program Studi:\nContoh: Teknik Informatika",
        reply_markup=cancel_keyboard(),
    )
    return STATE_EDU_MAJOR


async def receive_edu_major(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_required(update.message.text, "Jurusan")
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_EDU_MAJOR
    context.user_data["_current_edu"]["major"] = result
    await update.message.reply_text(
        "Tahun Masuk (YYYY):\nContoh: 2016",
        reply_markup=cancel_keyboard(),
    )
    return STATE_EDU_START


async def receive_edu_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_year(update.message.text)
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_EDU_START
    context.user_data["_current_edu"]["start"] = result
    await update.message.reply_text(
        "Tahun Lulus (YYYY) atau ketik *Present* jika masih berlangsung:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=cancel_keyboard(),
    )
    return STATE_EDU_END


async def receive_edu_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_year(update.message.text, allow_present=True)
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_EDU_END
    context.user_data["_current_edu"]["end"] = result
    context.user_data.setdefault("education", []).append(context.user_data["_current_edu"].copy())
    context.user_data["_current_edu"] = {}

    count = len(context.user_data["education"])
    if count >= MAX_EDUCATION:
        await update.message.reply_text(
            f"✅ Pendidikan disimpan ({count}/{MAX_EDUCATION}). Batas maksimal tercapai."
        )
        return await _ask_experience(update, context)

    await update.message.reply_text(
        f"✅ Pendidikan disimpan ({count}).\n\nTambah pendidikan lagi?",
        reply_markup=yes_no_keyboard("edu"),
    )
    return STATE_EDU_MORE


async def edu_more_yes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Tambah pendidikan berikutnya.")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Nama Sekolah / Universitas:",
        reply_markup=cancel_keyboard(),
    )
    return STATE_EDU_SCHOOL


async def edu_more_no(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Lanjut ke Pengalaman Kerja.")
    return await _ask_experience(update, context, from_callback=True)


async def skip_education(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("⏭ Pendidikan dilewati.")
    return await _ask_experience(update, context, from_callback=True)


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------

async def _ask_experience(
    update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback: bool = False
) -> int:
    msg = (
        f"{progress_bar(8)}\n\n"
        "Langkah 8/10 – *Pengalaman Kerja*\n"
        "Nama Perusahaan:\n"
        "Contoh: PT Digital Maju\n\n"
        "Atau tekan Skip jika fresh graduate / tidak ada."
    )
    if from_callback:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=skip_cancel_keyboard(),
        )
    else:
        await update.message.reply_text(
            msg, parse_mode=ParseMode.MARKDOWN, reply_markup=skip_cancel_keyboard()
        )
    context.user_data["_current_exp"] = {}
    return STATE_EXP_COMPANY


async def receive_exp_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_required(update.message.text, "Nama perusahaan")
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_EXP_COMPANY
    context.user_data["_current_exp"]["company"] = result
    await update.message.reply_text(
        "Posisi / Jabatan:\nContoh: Backend Developer",
        reply_markup=cancel_keyboard(),
    )
    return STATE_EXP_POSITION


async def receive_exp_position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_required(update.message.text, "Posisi")
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_EXP_POSITION
    context.user_data["_current_exp"]["position"] = result
    await update.message.reply_text(
        "Tahun Mulai (YYYY):\nContoh: 2021",
        reply_markup=cancel_keyboard(),
    )
    return STATE_EXP_START


async def receive_exp_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_year(update.message.text)
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_EXP_START
    context.user_data["_current_exp"]["start"] = result
    await update.message.reply_text(
        "Tahun Selesai (YYYY) atau ketik *Present*:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=cancel_keyboard(),
    )
    return STATE_EXP_END


async def receive_exp_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_year(update.message.text, allow_present=True)
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_EXP_END
    context.user_data["_current_exp"]["end"] = result
    await update.message.reply_text(
        "Deskripsi Pekerjaan:\n"
        "Jelaskan tanggung jawab / pencapaian (boleh multi-baris).\n"
        "Contoh:\n"
        "• Membangun REST API dengan FastAPI\n"
        "• Optimasi performa database",
        reply_markup=cancel_keyboard(),
    )
    return STATE_EXP_DESC


async def receive_exp_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if len(text) > 800:
        await update.message.reply_text("⚠️ Deskripsi terlalu panjang. Persingkat sedikit.")
        return STATE_EXP_DESC
    context.user_data["_current_exp"]["description"] = text
    context.user_data.setdefault("experience", []).append(context.user_data["_current_exp"].copy())
    context.user_data["_current_exp"] = {}

    count = len(context.user_data["experience"])
    if count >= MAX_EXPERIENCE:
        await update.message.reply_text(
            f"✅ Pengalaman disimpan ({count}/{MAX_EXPERIENCE}). Batas maksimal tercapai."
        )
        return await _ask_skills(update, context)

    await update.message.reply_text(
        f"✅ Pengalaman disimpan ({count}).\n\nTambah pengalaman lagi?",
        reply_markup=yes_no_keyboard("exp"),
    )
    return STATE_EXP_MORE


async def exp_more_yes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Tambah pengalaman berikutnya.")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Nama Perusahaan:",
        reply_markup=cancel_keyboard(),
    )
    return STATE_EXP_COMPANY


async def exp_more_no(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Lanjut ke Skill.")
    return await _ask_skills(update, context, from_callback=True)


async def skip_experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("⏭ Pengalaman kerja dilewati.")
    return await _ask_skills(update, context, from_callback=True)


# ---------------------------------------------------------------------------
# Skills & Languages
# ---------------------------------------------------------------------------

async def _ask_skills(
    update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback: bool = False
) -> int:
    msg = (
        f"{progress_bar(9)}\n\n"
        "Langkah 9/10 – *Skill*\n"
        "Masukkan skill (pisahkan dengan koma atau baris baru).\n"
        "Contoh:\nPython, HTML, CSS, JavaScript, SQL, Excel, Laravel, React"
    )
    if from_callback:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=skip_cancel_keyboard(),
        )
    else:
        await update.message.reply_text(
            msg, parse_mode=ParseMode.MARKDOWN, reply_markup=skip_cancel_keyboard()
        )
    return STATE_SKILLS


async def receive_skills(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    skills = parse_list_input(update.message.text)
    if not skills:
        await update.message.reply_text("⚠️ Minimal satu skill. Atau tekan Skip.")
        return STATE_SKILLS
    context.user_data["skills"] = skills[:20]
    await update.message.reply_text(
        f"✅ {len(context.user_data['skills'])} skill disimpan.\n\n"
        "Sekarang *Bahasa* yang dikuasai (pisahkan koma):\n"
        "Contoh: Indonesia, English, Japanese",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=skip_cancel_keyboard(),
    )
    return STATE_LANGUAGES


async def skip_skills(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    context.user_data["skills"] = []
    await update.callback_query.edit_message_text("⏭ Skill dilewati.")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Bahasa yang dikuasai (pisahkan koma):\nContoh: Indonesia, English",
        reply_markup=skip_cancel_keyboard(),
    )
    return STATE_LANGUAGES


async def receive_languages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    languages = parse_list_input(update.message.text)
    if not languages:
        await update.message.reply_text("⚠️ Minimal satu bahasa. Atau tekan Skip.")
        return STATE_LANGUAGES
    context.user_data["languages"] = languages[:8]
    return await _ask_cert(update, context)


async def skip_languages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    context.user_data["languages"] = []
    await update.callback_query.edit_message_text("⏭ Bahasa dilewati.")
    return await _ask_cert(update, context, from_callback=True)


# ---------------------------------------------------------------------------
# Certificates
# ---------------------------------------------------------------------------

async def _ask_cert(
    update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback: bool = False
) -> int:
    msg = (
        "📜 *Sertifikat* (opsional)\n"
        "Nama sertifikat:\n"
        "Contoh: AWS Certified Cloud Practitioner\n\n"
        "Atau tekan Skip."
    )
    if from_callback:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=skip_cancel_keyboard(),
        )
    else:
        await update.message.reply_text(
            msg, parse_mode=ParseMode.MARKDOWN, reply_markup=skip_cancel_keyboard()
        )
    return STATE_CERT_NAME


async def receive_cert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_required(update.message.text, "Nama sertifikat")
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_CERT_NAME
    context.user_data.setdefault("certificates", []).append(result)
    count = len(context.user_data["certificates"])
    if count >= MAX_CERTIFICATES:
        await update.message.reply_text("✅ Sertifikat disimpan. Batas maksimal tercapai.")
        return await _ask_achievement(update, context)
    await update.message.reply_text(
        f"✅ Sertifikat disimpan ({count}).\nTambah sertifikat lagi?",
        reply_markup=yes_no_keyboard("cert"),
    )
    return STATE_CERT_MORE


async def cert_more_yes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Tambah sertifikat.")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Nama sertifikat:",
        reply_markup=cancel_keyboard(),
    )
    return STATE_CERT_NAME


async def cert_more_no(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Lanjut ke Prestasi.")
    return await _ask_achievement(update, context, from_callback=True)


async def skip_cert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("⏭ Sertifikat dilewati.")
    return await _ask_achievement(update, context, from_callback=True)


# ---------------------------------------------------------------------------
# Achievements
# ---------------------------------------------------------------------------

async def _ask_achievement(
    update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback: bool = False
) -> int:
    msg = (
        "🏆 *Prestasi* (opsional)\n"
        "Tuliskan prestasi:\n"
        "Contoh: Juara 1 Hackathon Nasional 2023\n\n"
        "Atau tekan Skip."
    )
    if from_callback:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=skip_cancel_keyboard(),
        )
    else:
        await update.message.reply_text(
            msg, parse_mode=ParseMode.MARKDOWN, reply_markup=skip_cancel_keyboard()
        )
    return STATE_ACHIEVEMENT


async def receive_achievement(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ok, result = validate_required(update.message.text, "Prestasi")
    if not ok:
        await update.message.reply_text(f"⚠️ {result}")
        return STATE_ACHIEVEMENT
    context.user_data.setdefault("achievements", []).append(result)
    count = len(context.user_data["achievements"])
    if count >= MAX_ACHIEVEMENTS:
        await update.message.reply_text("✅ Prestasi disimpan. Batas maksimal tercapai.")
        return await _ask_links(update, context)
    await update.message.reply_text(
        f"✅ Prestasi disimpan ({count}).\nTambah prestasi lagi?",
        reply_markup=yes_no_keyboard("ach"),
    )
    return STATE_ACHIEVEMENT_MORE


async def ach_more_yes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Tambah prestasi.")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Tuliskan prestasi:",
        reply_markup=cancel_keyboard(),
    )
    return STATE_ACHIEVEMENT


async def ach_more_no(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Lanjut ke Link.")
    return await _ask_links(update, context, from_callback=True)


async def skip_achievement(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("⏭ Prestasi dilewati.")
    return await _ask_links(update, context, from_callback=True)


# ---------------------------------------------------------------------------
# Links
# ---------------------------------------------------------------------------

async def _ask_links(
    update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback: bool = False
) -> int:
    msg = (
        f"{progress_bar(9)}\n\n"
        "🔗 *Link* (opsional)\n"
        "Kirim dalam format berikut (satu baris per link):\n\n"
        "`github: https://github.com/username`\n"
        "`linkedin: https://linkedin.com/in/username`\n"
        "`portfolio: https://portfolio.com`\n"
        "`website: https://example.com`\n\n"
        "Atau tekan Skip."
    )
    if from_callback:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=skip_cancel_keyboard(),
        )
    else:
        await update.message.reply_text(
            msg, parse_mode=ParseMode.MARKDOWN, reply_markup=skip_cancel_keyboard()
        )
    return STATE_LINKS


async def receive_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    links: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        val = val.strip()
        if key in {"github", "linkedin", "portfolio", "website", "behance", "dribbble"} and val:
            ok, cleaned = validate_url(val)
            if ok and cleaned:
                links[key] = cleaned
    context.user_data["links"] = links
    await update.message.reply_text(
        f"✅ {len(links)} link disimpan." if links else "Tidak ada link valid."
    )
    return await _ask_photo(update, context)


async def skip_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    context.user_data["links"] = {}
    await update.callback_query.edit_message_text("⏭ Link dilewati.")
    return await _ask_photo(update, context, from_callback=True)


# ---------------------------------------------------------------------------
# Photo
# ---------------------------------------------------------------------------

async def _ask_photo(
    update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback: bool = False
) -> int:
    msg = (
        f"{progress_bar(10)}\n\n"
        "📷 *Foto Profil* (opsional)\n"
        "Kirim foto profil kamu sekarang.\n"
        "Atau tekan Skip jika tidak ingin menyertakan foto."
    )
    if from_callback:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=photo_keyboard(),
        )
    else:
        await update.message.reply_text(
            msg, parse_mode=ParseMode.MARKDOWN, reply_markup=photo_keyboard()
        )
    return STATE_PHOTO


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photo = update.message.photo[-1]  # highest resolution
    if photo.file_size and photo.file_size > MAX_PHOTO_SIZE_MB * 1024 * 1024:
        await update.message.reply_text(
            f"⚠️ Foto terlalu besar (maks. {MAX_PHOTO_SIZE_MB} MB). Kirim ulang atau Skip."
        )
        return STATE_PHOTO
    try:
        file = await context.bot.get_file(photo.file_id)
        bio = await file.download_as_bytearray()
        context.user_data["photo_bytes"] = bytes(bio)
        await update.message.reply_text("✅ Foto profil diterima.")
    except Exception as exc:
        logger.exception("Photo download failed: %s", exc)
        await update.message.reply_text("⚠️ Gagal mengunduh foto. Lanjut tanpa foto.")
        context.user_data.pop("photo_bytes", None)
    return await _ask_template(update, context)


async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    context.user_data.pop("photo_bytes", None)
    await update.callback_query.edit_message_text("⏭ Foto dilewati.")
    return await _ask_template(update, context, from_callback=True)


# ---------------------------------------------------------------------------
# Template selection & Preview
# ---------------------------------------------------------------------------

async def _ask_template(
    update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback: bool = False
) -> int:
    lines = ["🎨 *Pilih Template CV*\n"]
    for key, info in TEMPLATES.items():
        lines.append(f"{info['emoji']} *{info['name']}*\n{info['description']}\n")
    msg = "\n".join(lines)
    if from_callback:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=template_keyboard(),
        )
    else:
        await update.message.reply_text(
            msg, parse_mode=ParseMode.MARKDOWN, reply_markup=template_keyboard()
        )
    return STATE_TEMPLATE


async def choose_template(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    key = query.data.replace("template_", "")
    if key not in TEMPLATES:
        await query.edit_message_text("Template tidak valid. Pilih lagi.")
        return STATE_TEMPLATE
    context.user_data["template"] = key
    info = TEMPLATES[key]
    await query.edit_message_text(f"✅ Template *{info['name']}* dipilih.", parse_mode=ParseMode.MARKDOWN)
    return await _show_preview(update, context)


async def _show_preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    summary = build_summary(context.user_data)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=summary,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=preview_keyboard(),
    )
    return STATE_PREVIEW


async def show_edit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Simple edit: restart personal flow for simplicity (full section edit can be extended)."""
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "✏ Fitur edit detail sedang dalam pengembangan.\n"
        "Untuk saat ini, kamu bisa *Generate PDF* atau *Batal* lalu mulai ulang.\n\n"
        "Kembali ke preview:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=preview_keyboard(),
    )
    return STATE_PREVIEW


async def back_to_preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()
    return await _show_preview(update, context)


async def generate_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Generate and send the PDF, then clear data."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⏳ Sedang membuat PDF profesional kamu... Mohon tunggu sebentar.")

    try:
        pdf_bytes = generate_cv_pdf(context.user_data)
        name = context.user_data.get("full_name", "CV").replace(" ", "_")
        filename = f"CV_{name}.pdf"

        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=InputFile(pdf_bytes, filename=filename),
            caption=(
                "✅ *CV berhasil dibuat!*\n\n"
                "PDF sudah siap digunakan untuk melamar pekerjaan.\n"
                "Data sementara telah dihapus demi privasi.\n\n"
                "Ketik /start untuk membuat CV baru."
            ),
            parse_mode=ParseMode.MARKDOWN,
        )
        logger.info("PDF generated and sent for user %s", update.effective_user.id if update.effective_user else "?")
    except Exception as exc:
        logger.exception("PDF generation failed: %s", exc)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "❌ Maaf, terjadi kesalahan saat membuat PDF.\n"
                "Silakan coba lagi dengan /start.\n\n"
                f"Detail: `{type(exc).__name__}`"
            ),
            parse_mode=ParseMode.MARKDOWN,
        )
    finally:
        clear_user_data(context)

    return ConversationHandler.END
