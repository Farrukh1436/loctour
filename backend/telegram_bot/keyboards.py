"""Reusable keyboards for the Telegram bot."""
from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from . import strings


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=strings.REGISTER_FOR_TRIP, callback_data="menu:register")
    builder.button(text=strings.MY_REGISTRATIONS, callback_data="menu:registrations")
    builder.adjust(1)
    return builder.as_markup()


def contact_request_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=strings.SHARE_PHONE_BUTTON, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
        selective=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def trips_keyboard(trips: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for trip in trips:
        title = trip.get("title", strings.TRIP_DEFAULT_TITLE)
        builder.button(text=title, callback_data=f"trip:{trip['id']}")
    builder.button(text=strings.BACK_TO_MENU, callback_data="menu:back")
    builder.adjust(1)
    return builder.as_markup()
