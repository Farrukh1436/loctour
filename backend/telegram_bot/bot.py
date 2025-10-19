"""Entrypoint for the LocTur Telegram bot."""
from __future__ import annotations

import asyncio
import logging
from contextlib import suppress

from aiogram import Bot, Dispatcher
try:  # aiogram >= 3.4
    from aiogram.client.default import DefaultBotProperties
except ImportError:  # pragma: no cover - compatibility fallback
    DefaultBotProperties = None  # type: ignore

from .api_client import APIClient
from .config import BotConfig, load_config
from .handlers import router as handlers_router
from .poller import poll_group_join_queue
from .runtime import clear_bot_data, get_bot_data, set_bot_data


async def _setup_logging() -> None:
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        level=logging.INFO,
    )


async def _on_startup(bot: Bot) -> None:
    api_client: APIClient = get_bot_data(bot, "api_client")
    config: BotConfig = get_bot_data(bot, "config")
    set_bot_data(bot, "pending_group_joins", {})
    set_bot_data(bot, "group_join_task", asyncio.create_task(poll_group_join_queue(bot, api_client, config)))
    logging.getLogger(__name__).info("Telegram bot started.")


async def _on_shutdown(bot: Bot) -> None:
    task: asyncio.Task | None = get_bot_data(bot, "group_join_task")
    if task:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
    api_client: APIClient = get_bot_data(bot, "api_client")
    await api_client.aclose()
    clear_bot_data(bot)
    logging.getLogger(__name__).info("Telegram bot stopped.")


async def main() -> None:
    await _setup_logging()
    config = load_config()
    api_client = APIClient(config.backend_api_base, config.backend_bot_token)
    if DefaultBotProperties:
        bot = Bot(config.telegram_token, default=DefaultBotProperties(parse_mode="HTML"))
    else:
        bot = Bot(config.telegram_token, parse_mode="HTML")
    dp = Dispatcher()

    dp.include_router(handlers_router)

    set_bot_data(bot, "api_client", api_client)
    set_bot_data(bot, "config", config)

    dp.startup.register(_on_startup)
    dp.shutdown.register(_on_shutdown)

    try:
        await dp.start_polling(bot)
    finally:
        await api_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
