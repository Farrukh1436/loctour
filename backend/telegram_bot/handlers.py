"""Aiogram handlers for the LocTur Telegram bot."""
from __future__ import annotations

import logging
import mimetypes
import re
from dataclasses import dataclass
from typing import Any, Dict

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup, Message

from .api_client import APIClient, APIClientError
from .config import BotConfig
from .formatters import format_trip_summary
from .keyboards import (
    contact_request_keyboard,
    main_menu_keyboard,
    remove_keyboard,
    trips_keyboard,
)
from .group_invites import send_group_invite
from .runtime import get_bot_data
from .states import RegistrationStates

logger = logging.getLogger(__name__)

router = Router(name="registration")

PHONE_PATTERN = re.compile(r"^\+?\d[\d\s()+-]{6,}$")


@dataclass
class Dependencies:
    api_client: APIClient
    config: BotConfig


def _get_dependencies(event: Message | CallbackQuery | ChatJoinRequest) -> Dependencies:
    bot = event.bot
    api_client: APIClient = get_bot_data(bot, "api_client")
    config: BotConfig = get_bot_data(bot, "config")
    return Dependencies(api_client=api_client, config=config)


async def _ensure_main_menu(message: Message, text: str) -> None:
    await message.answer(text, reply_markup=main_menu_keyboard())


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    deps = _get_dependencies(message)
    await state.clear()
    await _ensure_main_menu(
        message,
        f"Hi {message.from_user.full_name}!\nChoose an option below to get started.",
    )
    try:
        trips = await deps.api_client.list_trips(status=deps.config.trips_status_filter)
    except APIClientError as exc:
        logger.warning("Unable to fetch trips on /start: %s", exc)
        return
    if not trips:
        return
    summaries = "\n\n".join(format_trip_summary(trip) for trip in trips[:3])
    await message.answer(
        "Here are the current highlights:\n\n" + summaries,
        disable_web_page_preview=True,
    )


@router.message(Command("link_trip"))
async def cmd_link_trip(message: Message) -> None:
    if message.chat.type not in {"group", "supergroup"}:
        await message.answer("Run this command inside the Telegram group you want to link.")
        return

    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 2:
        await message.answer("Usage: /link_trip <trip_id> [invite_link]")
        return

    trip_id = parts[1].strip()
    invite_link = parts[2].strip() if len(parts) > 2 else None

    deps = _get_dependencies(message)
    try:
        await deps.api_client.link_trip_group(trip_id, chat_id=message.chat.id, invite_link=invite_link)
    except APIClientError as exc:
        detail = exc.payload if isinstance(exc.payload, str) else exc.payload.get("detail") if isinstance(exc.payload, dict) else None
        logger.error("Failed to link trip %s to chat %s: %s", trip_id, message.chat.id, exc)
        await message.answer(detail or "Unable to link this group. Please confirm the trip ID and try again.")
        return

    await message.answer(
        "Group successfully linked to trip. Travelers will now be invited here when confirmed.",
        disable_web_page_preview=True,
    )


@router.callback_query(F.data == "menu:back")
async def cb_back(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await _ensure_main_menu(callback.message, "Main menu:")
    await callback.answer()


@router.callback_query(F.data == "menu:register")
async def cb_register(callback: CallbackQuery, state: FSMContext) -> None:
    deps = _get_dependencies(callback)
    await callback.answer()
    try:
        trips = await deps.api_client.list_trips(status=deps.config.trips_status_filter)
    except APIClientError as exc:
        logger.error("Failed to fetch trips: %s", exc)
        await callback.message.answer("Sorry, we could not load trips. Please try again later.")
        return
    if not trips:
        await callback.message.answer("No trips are open for registration right now. Please check back soon.")
        return
    await callback.message.answer(
        "Pick a trip below to start your registration:",
        reply_markup=trips_keyboard(trips),
    )


@router.callback_query(F.data == "menu:registrations")
async def cb_registrations(callback: CallbackQuery, state: FSMContext) -> None:
    deps = _get_dependencies(callback)
    await callback.answer()
    traveler = await deps.api_client.get_traveler_by_telegram_id(str(callback.from_user.id))
    if not traveler:
        await callback.message.answer(
            "You have no registrations yet. Use the menu to book your first trip!",
            reply_markup=main_menu_keyboard(),
        )
        return
    user_trips = await deps.api_client.list_user_trips(filters={"traveler": traveler["id"]})
    if not user_trips:
        await callback.message.answer(
            "You have no registrations yet. Use the menu to book your first trip!",
            reply_markup=main_menu_keyboard(),
        )
        return

    lines = ["Your registrations:"]
    eligible_buttons: list[list[InlineKeyboardButton]] = []
    for user_trip in user_trips:
        trip = user_trip.get("trip_detail") or {}
        title = trip.get("title", "Trip")
        lines.append(
            f"• <b>{title}</b>: status={user_trip.get('status')}, payment={user_trip.get('payment_status')}"
        )

        trip_has_group = bool((trip.get("group_chat_id") or trip.get("group_invite_link")))
        if (
            user_trip.get("status") == "confirmed"
            and user_trip.get("payment_status") == "confirmed"
            and trip_has_group
        ):
            eligible_buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"Get invite for {title}",
                        callback_data=f"join:{user_trip['id']}",
                    )
                ]
            )

    await callback.message.answer(
        "\n".join(lines),
        reply_markup=main_menu_keyboard(),
    )

    if eligible_buttons:
        await callback.message.answer(
            "Tap below to receive the group invite link again:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=eligible_buttons),
        )


@router.callback_query(F.data.startswith("trip:"))
async def cb_select_trip(callback: CallbackQuery, state: FSMContext) -> None:
    deps = _get_dependencies(callback)
    await callback.answer()
    trip_id = callback.data.split(":", maxsplit=1)[1]
    try:
        trip = await deps.api_client.get_trip(trip_id)
    except APIClientError as exc:
        logger.error("Failed to fetch trip %s: %s", trip_id, exc)
        await callback.message.answer("Unable to load this trip. Please choose another one.")
        return

    traveler = await deps.api_client.get_traveler_by_telegram_id(str(callback.from_user.id))
    suggested_first = (traveler or {}).get("first_name") or callback.from_user.first_name or ""
    suggested_last = (traveler or {}).get("last_name") or callback.from_user.last_name or ""
    suggested_phone = (traveler or {}).get("phone_number") or ""
    extra_info = (traveler or {}).get("extra_info") or ""

    await state.update_data(
        trip_id=trip_id,
        trip_data=trip,
        traveler_id=(traveler or {}).get("id"),
        suggested_first_name=suggested_first,
        suggested_last_name=suggested_last,
        suggested_phone=suggested_phone,
        existing_extra_info=extra_info,
    )

    await callback.message.answer(format_trip_summary(trip), disable_web_page_preview=True)
    await callback.message.answer(
        f"Let's get your details.\nSend your <b>first name</b> (current: <code>{suggested_first or 'not set'}</code>)."
    )
    await state.set_state(RegistrationStates.waiting_for_first_name)


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return value.strip()


@router.message(RegistrationStates.waiting_for_first_name)
async def on_first_name(message: Message, state: FSMContext) -> None:
    text = _normalize_text(message.text)
    if not text:
        await message.answer("Please send a valid first name.")
        return
    await state.update_data(first_name=text)
    data = await state.get_data()
    suggested = data.get("suggested_last_name", "")
    await message.answer(
        f"Great! Now send your <b>last name</b> (current: <code>{suggested or 'not set'}</code>). Send '-' to skip.",
    )
    await state.set_state(RegistrationStates.waiting_for_last_name)


@router.message(RegistrationStates.waiting_for_last_name)
async def on_last_name(message: Message, state: FSMContext) -> None:
    text = _normalize_text(message.text)
    if text == "-" or text.lower() == "skip":
        text = ""
    await state.update_data(last_name=text)
    await message.answer(
        "Please share your phone number. You can type it or use the button below.",
        reply_markup=contact_request_keyboard(),
    )
    await state.set_state(RegistrationStates.waiting_for_phone)


def _extract_phone(message: Message) -> str:
    if message.contact and message.contact.phone_number:
        return message.contact.phone_number
    return _normalize_text(message.text)


@router.message(RegistrationStates.waiting_for_phone)
async def on_phone(message: Message, state: FSMContext) -> None:
    phone_number = _extract_phone(message)
    if not phone_number:
        await message.answer("I didn't catch that phone number. Please try again.")
        return
    if not PHONE_PATTERN.match(phone_number):
        await message.answer("That doesn't look like a valid phone number. Please re-enter it.")
        return
    await state.update_data(phone_number=phone_number)
    await message.answer(
        "Any extra info we should know? (Send '-' to skip.)",
        reply_markup=remove_keyboard(),
    )
    await state.set_state(RegistrationStates.waiting_for_extra_info)


async def _upsert_traveler(message: Message, data: Dict[str, Any], deps: Dependencies) -> dict:
    payload = {
        "first_name": data["first_name"],
        "last_name": data.get("last_name", ""),
        "phone_number": data["phone_number"],
        "telegram_handle": message.from_user.username or "",
        "telegram_id": str(message.from_user.id),
        "extra_info": data.get("extra_info", ""),
    }
    traveler_id = data.get("traveler_id")
    if traveler_id:
        traveler = await deps.api_client.update_traveler(traveler_id, payload)
    else:
        traveler = await deps.api_client.create_traveler(payload)
    return traveler


@router.message(RegistrationStates.waiting_for_extra_info)
async def on_extra_info(message: Message, state: FSMContext) -> None:
    deps = _get_dependencies(message)
    text = _normalize_text(message.text)
    if text.lower() in {"-", "skip"}:
        text = ""
    await state.update_data(extra_info=text)
    data = await state.get_data()

    if data.get("existing_extra_info") and not text:
        data["extra_info"] = data["existing_extra_info"]

    try:
        traveler = await _upsert_traveler(message, data, deps)
    except APIClientError as exc:
        logger.error("Failed to upsert traveler: %s", exc)
        await message.answer("We couldn't save your profile. Please try again later.")
        await state.clear()
        return

    await state.update_data(traveler_id=traveler["id"])
    trip = data["trip_data"]
    default_price = trip.get("default_price", "0")
    await message.answer(
        f"Almost done! Send a photo or PDF of your payment receipt for <b>{trip.get('title')}</b> "
        f"(amount: {default_price}).",
    )
    await state.set_state(RegistrationStates.waiting_for_payment_proof)


async def _download_payment_file(message: Message) -> tuple[bytes, str, str]:
    from io import BytesIO

    if not message.bot:
        raise RuntimeError("Bot instance unavailable for downloading files.")

    buffer = BytesIO()
    filename = "payment_proof.jpg"
    content_type = "image/jpeg"

    if message.photo:
        photo = message.photo[-1]
        await message.bot.download(photo.file_id, destination=buffer)
        filename = f"payment_{photo.file_unique_id}.jpg"
    elif message.document:
        document = message.document
        await message.bot.download(document.file_id, destination=buffer)
        filename = document.file_name or f"payment_{document.file_unique_id}"
        content_type = document.mime_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
    else:
        raise ValueError("Unsupported message type for payment proof.")

    buffer.seek(0)
    return buffer.getvalue(), filename, content_type


@router.message(RegistrationStates.waiting_for_payment_proof)
async def on_payment_proof(message: Message, state: FSMContext) -> None:
    deps = _get_dependencies(message)
    data = await state.get_data()
    if not (message.photo or message.document):
        await message.answer("Please send a photo or document with the payment proof.")
        return

    try:
        file_bytes, filename, content_type = await _download_payment_file(message)
    except ValueError:
        await message.answer("Unsupported file type. Send a photo or PDF.")
        return

    payload = {
        "trip": data["trip_id"],
        "traveler": data["traveler_id"],
        "quoted_price": str(data["trip_data"].get("default_price", "0")),
        "paid_amount": "0",
    }
    caption = _normalize_text(message.caption)
    if caption:
        payload["payment_note"] = caption

    files = {"payment_proof": (filename, file_bytes, content_type)}
    try:
        user_trip = await deps.api_client.create_user_trip(payload, files=files)
    except APIClientError as exc:
        detail = exc.payload or {}
        if isinstance(detail, dict) and "non_field_errors" in detail:
            await message.answer(detail["non_field_errors"][0])
        elif isinstance(detail, dict) and "traveler" in detail:
            await message.answer("It looks like you're already registered for this trip.")
        else:
            logger.error("Failed to create user trip: %s", detail)
            await message.answer("We couldn't submit your registration. Please try again later.")
        await state.clear()
        return

    await message.answer(
        "Thank you! Your payment proof was submitted for review.\n"
        "You'll receive a message once the admins approve it.",
        reply_markup=main_menu_keyboard(),
    )
    await state.clear()

    trip = data["trip_data"]
    try:
        await message.answer(
            f"Trip summary:\n{format_trip_summary(trip)}",
            disable_web_page_preview=True,
        )
    except TelegramForbiddenError:
        pass


@router.chat_join_request()
async def on_chat_join_request(join_request: ChatJoinRequest) -> None:
    deps = _get_dependencies(join_request)
    chat_id = join_request.chat.id
    user_id = join_request.from_user.id
    pending_map: dict[tuple[int, int], str] = get_bot_data(join_request.bot, "pending_group_joins")

    user_trip_id = pending_map.get((chat_id, user_id))
    traveler = None

    if not user_trip_id:
        traveler = await deps.api_client.get_traveler_by_telegram_id(str(user_id))
        if traveler:
            user_trips = await deps.api_client.list_user_trips(filters={"traveler": traveler["id"]})
            for user_trip in user_trips:
                trip = user_trip.get("trip_detail") or {}
                try:
                    configured_chat = int(trip.get("group_chat_id") or 0)
                except (TypeError, ValueError):
                    continue
                if configured_chat == chat_id and user_trip.get("payment_status") == "confirmed":
                    user_trip_id = user_trip["id"]
                    break

    if not user_trip_id:
        await join_request.decline()
        return

    try:
        await join_request.approve()
    except TelegramBadRequest as exc:
        logger.error("Failed to approve join request for %s: %s", user_trip_id, exc)
        await deps.api_client.report_group_join(user_trip_id, success=False, error=str(exc))
        return

    await deps.api_client.report_group_join(user_trip_id, success=True)
    pending_map.pop((chat_id, user_id), None)

    try:
        await join_request.bot.send_message(
            user_id,
            f"Welcome to {join_request.chat.title}! You're now in the group.",
        )
    except TelegramForbiddenError:
        logger.warning("Cannot send welcome message to %s (blocked?).", user_id)
@router.callback_query(F.data.startswith("join:"))
async def cb_join_trip(callback: CallbackQuery) -> None:
    deps = _get_dependencies(callback)
    await callback.answer()
    user_trip_id = callback.data.split(":", maxsplit=1)[1]

    try:
        user_trip = await deps.api_client.get_user_trip(user_trip_id)
    except APIClientError as exc:
        logger.error("Failed to fetch user trip %s for invite request: %s", user_trip_id, exc)
        await callback.message.answer("We couldn't load your registration. Please try again later.")
        return

    if user_trip.get("status") != "confirmed" or user_trip.get("payment_status") != "confirmed":
        await callback.message.answer("This registration is not confirmed yet. Please wait for approval.")
        return

    success, error = await send_group_invite(callback.bot, deps.api_client, user_trip)
    if success:
        await callback.message.answer("Invite sent! Check our chat history for the link.")
    else:
        await callback.message.answer(error or "Unable to send the invite link. Please contact support.")
