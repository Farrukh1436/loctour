"""Background task to handle post-payment group onboarding."""
from __future__ import annotations

import asyncio
import logging
from typing import Set

from aiogram import Bot

from .api_client import APIClient
from .config import BotConfig
from .group_invites import send_group_invite


logger = logging.getLogger(__name__)


async def poll_group_join_queue(bot: Bot, api_client: APIClient, config: BotConfig) -> None:
    """Poll backend for confirmed registrations and send invite links."""

    processed_ids: Set[str] = set()

    while True:
        try:
            await _process_pending(bot, api_client, config, processed_ids)
        except Exception:  # pragma: no cover - defensive logging
            logger.exception("Unexpected error while processing group join queue")
        await asyncio.sleep(max(config.poll_interval_seconds, 10))


async def _process_pending(
    bot: Bot,
    api_client: APIClient,
    config: BotConfig,
    processed_ids: Set[str],
) -> None:
    filters = {
        "payment_status": "confirmed",
        "status": "confirmed",
        "group_joined": "false",
    }
    try:
        user_trips = await api_client.list_user_trips(filters=filters)
    except Exception as exc:  # pragma: no cover - upstream errors logged in API client
        logger.error("Failed to fetch pending group joins: %s", exc)
        return

    for user_trip in user_trips:
        user_trip_id = user_trip["id"]
        if user_trip_id in processed_ids:
            continue

        if user_trip.get("group_joined_at"):
            continue

        error_text = (user_trip.get("group_join_error") or "").lower()
        if "awaiting traveler to join" in error_text:
            continue

        success, _ = await send_group_invite(bot, api_client, user_trip)
        if success:
            processed_ids.add(user_trip_id)

