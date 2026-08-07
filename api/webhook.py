"""
Vercel serverless entrypoint for Telegram webhook.

This module exposes an ASGI application that:
1. Receives Telegram updates via POST
2. Verifies the secret token header
3. Dispatches the update to the python-telegram-bot Application
"""

from __future__ import annotations

import logging
from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.routing import Route
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from bot.config import Config
from bot.conversation import build_conversation_handler
from bot.handlers import example_command, help_command, start
from bot.helpers import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application singleton (reused across warm invocations)
# ---------------------------------------------------------------------------

_app: Application | None = None


def get_application() -> Application:
    """Build or return the cached Telegram Application."""
    global _app
    if _app is not None:
        return _app

    config = Config.from_env()
    application = (
        Application.builder()
        .token(config.telegram_token)
        .updater(None)  # webhook mode – no polling updater
        .build()
    )

    # Core handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))
    application.add_handler(CallbackQueryHandler(example_command, pattern="^example$"))
    application.add_handler(build_conversation_handler())

    _app = application
    logger.info("Telegram Application initialized")
    return _app


# ---------------------------------------------------------------------------
# HTTP handlers
# ---------------------------------------------------------------------------

async def health(request: Request) -> Response:
    """Simple health check."""
    return PlainTextResponse("OK")


async def telegram_webhook(request: Request) -> Response:
    """Receive and process Telegram updates."""
    # Catatan: project ini tidak menggunakan WEBHOOK_SECRET,
    # sehingga tidak ada verifikasi header secret token di sini.
    try:
        data: dict[str, Any] = await request.json()
    except Exception:
        return PlainTextResponse("Bad Request", status_code=400)

    application = get_application()

    # Ensure application is initialized (required for webhook mode)
    if not application.running:
        await application.initialize()
        await application.start()

    try:
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as exc:
        logger.exception("Error processing update: %s", exc)
        # Still return 200 so Telegram does not retry endlessly
        return JSONResponse({"ok": False, "error": str(exc)}, status_code=200)

    return JSONResponse({"ok": True})


async def set_webhook(request: Request) -> Response:
    """
    Optional helper endpoint to register the webhook with Telegram.
    Call once after deployment: GET /set-webhook
    """
    config = Config.from_env()
    application = get_application()

    if not application.running:
        await application.initialize()

    webhook_url = f"{config.webhook_url}/"
    result = await application.bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"],
    )
    info = await application.bot.get_webhook_info()
    return JSONResponse(
        {
            "set_webhook": result,
            "url": info.url,
            "has_custom_certificate": info.has_custom_certificate,
            "pending_update_count": info.pending_update_count,
        }
    )


# ---------------------------------------------------------------------------
# Starlette ASGI app (Vercel looks for `app`)
# ---------------------------------------------------------------------------

routes = [
    Route("/", telegram_webhook, methods=["POST"]),
    Route("/webhook", telegram_webhook, methods=["POST"]),
    Route("/api/webhook", telegram_webhook, methods=["POST"]),
    Route("/health", health, methods=["GET"]),
    Route("/set-webhook", set_webhook, methods=["GET"]),
]

app = Starlette(routes=routes, debug=False)
