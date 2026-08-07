"""
Local development runner using long-polling.

Usage:
  1. Copy .env.example → .env and fill TELEGRAM_BOT_TOKEN
  2. python run_local.py

Note: WEBHOOK_URL / WEBHOOK_SECRET are not required for polling mode.
"""

from __future__ import annotations

import asyncio
import logging
import os

from dotenv import load_dotenv
from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from bot.conversation import build_conversation_handler
from bot.handlers import example_command, help_command, start
from bot.helpers import setup_logging

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is required in .env")

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))
    application.add_handler(CallbackQueryHandler(example_command, pattern="^example$"))
    application.add_handler(build_conversation_handler())

    logger.info("Starting CV Builder Bot (polling mode)...")
    application.run_polling(allowed_updates=["message", "callback_query"], drop_pending_updates=True)


if __name__ == "__main__":
    main()
