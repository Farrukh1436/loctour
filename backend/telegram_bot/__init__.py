"""Telegram bot package for LocTur."""

__all__ = ["main"]


def main():
    from .bot import main as _main

    return _main()
