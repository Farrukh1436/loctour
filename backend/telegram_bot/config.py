"""Configuration helpers for the Telegram bot service."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class BotConfig:
    """Runtime configuration for the Telegram bot."""

    telegram_token: str
    backend_api_base: str
    backend_bot_token: str
    poll_interval_seconds: int = 30
    trips_status_filter: str = "registration"


def _get_env(name: str, default: str | None = None, *, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    if value is None:
        return ""
    return value


def load_config() -> BotConfig:
    """Load configuration from environment variables."""

    telegram_token = _get_env("TELEGRAM_BOT_TOKEN", required=True)
    backend_api_base = _get_env("BACKEND_API_BASE_URL", "http://localhost:8000/api/")
    backend_bot_token = _get_env("BACKEND_BOT_TOKEN", required=True)
    poll_interval_seconds = int(_get_env("GROUP_POLL_INTERVAL", "30"))
    trips_status_filter = _get_env("TRIP_STATUS_FILTER", "registration")

    return BotConfig(
        telegram_token=telegram_token,
        backend_api_base=backend_api_base.rstrip("/") + "/",
        backend_bot_token=backend_bot_token,
        poll_interval_seconds=poll_interval_seconds,
        trips_status_filter=trips_status_filter,
    )
