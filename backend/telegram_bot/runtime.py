"""Runtime helpers for storing bot-scoped state."""
from __future__ import annotations

from typing import Any, Dict

from aiogram import Bot

_BOT_STATE: Dict[int, Dict[str, Any]] = {}


def set_bot_data(bot: Bot, key: str, value: Any) -> None:
    _BOT_STATE.setdefault(id(bot), {})[key] = value


def get_bot_data(bot: Bot, key: str, default: Any | None = None) -> Any:
    return _BOT_STATE.setdefault(id(bot), {}).get(key, default)


def pop_bot_data(bot: Bot, key: str, default: Any | None = None) -> Any:
    state = _BOT_STATE.setdefault(id(bot), {})
    return state.pop(key, default)


def clear_bot_data(bot: Bot) -> None:
    _BOT_STATE.pop(id(bot), None)

