"""ConversationHandler definition and state machine for CV creation."""

from __future__ import annotations

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot import handlers
from bot.config import (
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
)


def build_conversation_handler() -> ConversationHandler:
    """Construct the main ConversationHandler for CV building flow."""

    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handlers.start_create_cv, pattern="^create_cv$"),
            CommandHandler("new", handlers.start_create_cv),
        ],
        states={
            STATE_FULL_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_full_name),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_POSITION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_position),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_BIRTH_PLACE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_birth_place),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_BIRTH_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_birth_date),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_phone),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_email),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_ADDRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_address),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_CITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_city),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_ABOUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_about),
                CallbackQueryHandler(handlers.skip_about, pattern="^skip$"),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            # Education
            STATE_EDU_SCHOOL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_edu_school),
                CallbackQueryHandler(handlers.skip_education, pattern="^skip$"),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_EDU_MAJOR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_edu_major),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_EDU_START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_edu_start),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_EDU_END: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_edu_end),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_EDU_MORE: [
                CallbackQueryHandler(handlers.edu_more_yes, pattern="^edu_yes$"),
                CallbackQueryHandler(handlers.edu_more_no, pattern="^edu_no$"),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            # Experience
            STATE_EXP_COMPANY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_exp_company),
                CallbackQueryHandler(handlers.skip_experience, pattern="^skip$"),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_EXP_POSITION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_exp_position),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_EXP_START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_exp_start),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_EXP_END: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_exp_end),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_EXP_DESC: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_exp_desc),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_EXP_MORE: [
                CallbackQueryHandler(handlers.exp_more_yes, pattern="^exp_yes$"),
                CallbackQueryHandler(handlers.exp_more_no, pattern="^exp_no$"),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            # Skills & Languages
            STATE_SKILLS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_skills),
                CallbackQueryHandler(handlers.skip_skills, pattern="^skip$"),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_LANGUAGES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_languages),
                CallbackQueryHandler(handlers.skip_languages, pattern="^skip$"),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            # Certificates
            STATE_CERT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_cert),
                CallbackQueryHandler(handlers.skip_cert, pattern="^skip$"),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_CERT_MORE: [
                CallbackQueryHandler(handlers.cert_more_yes, pattern="^cert_yes$"),
                CallbackQueryHandler(handlers.cert_more_no, pattern="^cert_no$"),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            # Achievements
            STATE_ACHIEVEMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_achievement),
                CallbackQueryHandler(handlers.skip_achievement, pattern="^skip$"),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_ACHIEVEMENT_MORE: [
                CallbackQueryHandler(handlers.ach_more_yes, pattern="^ach_yes$"),
                CallbackQueryHandler(handlers.ach_more_no, pattern="^ach_no$"),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            # Links
            STATE_LINKS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.receive_links),
                CallbackQueryHandler(handlers.skip_links, pattern="^skip$"),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            # Photo
            STATE_PHOTO: [
                MessageHandler(filters.PHOTO, handlers.receive_photo),
                CallbackQueryHandler(handlers.skip_photo, pattern="^skip_photo$"),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            # Template & Preview
            STATE_TEMPLATE: [
                CallbackQueryHandler(handlers.choose_template, pattern="^template_"),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            ],
            STATE_PREVIEW: [
                CallbackQueryHandler(handlers.generate_pdf, pattern="^generate$"),
                CallbackQueryHandler(handlers.show_edit_menu, pattern="^edit$"),
                CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
                CallbackQueryHandler(handlers.back_to_preview, pattern="^back_preview$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            CallbackQueryHandler(handlers.cancel, pattern="^cancel$"),
            CommandHandler("start", handlers.start),
        ],
        allow_reentry=True,
        name="cv_builder",
        persistent=False,
    )
