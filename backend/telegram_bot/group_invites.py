"""Utilities for sending group invite links to travelers."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .api_client import APIClient
from .runtime import get_bot_data, set_bot_data
from . import strings


async def send_group_invite(
    bot: Bot,
    api_client: APIClient,
    user_trip: Dict[str, Any],
) -> Tuple[bool, str | None]:
    """Send an invite link to the traveler's Telegram DM.

    Returns (success, error_message). On success the error message is None.
    """
    trip = user_trip.get("trip_detail") or {}
    traveler = user_trip.get("traveler_detail") or {}

    telegram_id = traveler.get("telegram_id")
    if not telegram_id:
        error = strings.TRAVELER_MISSING_TELEGRAM_ID
        await api_client.report_group_join(user_trip["id"], success=False, error=error)
        return False, error

    try:
        user_id = int(telegram_id)
    except (TypeError, ValueError):
        error = strings.INVALID_TELEGRAM_ID
        await api_client.report_group_join(user_trip["id"], success=False, error=error)
        return False, error

    invite_link = (trip.get("group_invite_link") or "").strip()
    chat_id: int | None = None

    if invite_link:
        try:
            chat_id = int(trip.get("group_chat_id"))
        except (TypeError, ValueError):
            chat_id = None
    else:
        group_chat_id = trip.get("group_chat_id")
        if not group_chat_id:
            error = strings.NO_TELEGRAM_GROUP_CONFIGURED
            await api_client.report_group_join(user_trip["id"], success=False, error=error)
            return False, error

        try:
            chat_id = int(group_chat_id)
        except (TypeError, ValueError):
            error = strings.INVALID_CHAT_ID
            await api_client.report_group_join(user_trip["id"], success=False, error=error)
            return False, error

        try:
            invite = await bot.create_chat_invite_link(
                chat_id=chat_id,
                creates_join_request=True,
                member_limit=1,
            )
        except TelegramBadRequest as exc:
            error_text = str(exc)
            # Telegram disallows member_limit when join requests are enabled; retry without it.
            if "member limit" in error_text.lower():
                try:
                    invite = await bot.create_chat_invite_link(
                        chat_id=chat_id,
                        creates_join_request=True,
                    )
                except TelegramBadRequest as retry_exc:
                    error = str(retry_exc)
                    await api_client.report_group_join(user_trip["id"], success=False, error=error)
                    return False, error
            else:
                error = error_text
                await api_client.report_group_join(user_trip["id"], success=False, error=error)
                return False, error

        invite_link = invite.invite_link

    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=strings.JOIN_TRIP_GROUP, url=invite_link)]]
    )

    message = strings.PAYMENT_CONFIRMED_MESSAGE.format(trip_title=trip.get('title'))

    try:
        await bot.send_message(user_id, message, reply_markup=markup, disable_web_page_preview=True)
    except TelegramForbiddenError:
        error = strings.BOT_CANNOT_MESSAGE_TRAVELER
        await api_client.report_group_join(user_trip["id"], success=False, error=error)
        return False, error

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    await api_client.report_group_join(
        user_trip["id"],
        success=False,
        error=f"Awaiting traveler to join via invite link sent at {timestamp}.",
    )

    if chat_id is not None:
        pending_map: Dict[Tuple[int, int], str] = get_bot_data(bot, "pending_group_joins") or {}
        pending_map[(chat_id, user_id)] = user_trip["id"]
        set_bot_data(bot, "pending_group_joins", pending_map)

    return True, None
