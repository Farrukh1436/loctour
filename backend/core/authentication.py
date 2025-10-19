"""Custom authentication backends."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication, exceptions

from .models import BotToken


@dataclass
class BotUser:
    """Lightweight user-like object for bot integrations."""

    token: BotToken

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_staff(self) -> bool:
        return False

    @property
    def is_active(self) -> bool:
        return True

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"BotUser<{self.token.name}>"


class BotTokenAuthentication(authentication.BaseAuthentication):
    """Authenticate Telegram bot requests via `X-Bot-Token` header."""

    keyword = "X-Bot-Token"

    def authenticate(self, request) -> Optional[Tuple[BotUser, BotToken]]:
        token_value = request.headers.get(self.keyword)
        if not token_value:
            return None

        try:
            token = BotToken.objects.get(token=token_value, is_active=True)
        except BotToken.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("Invalid bot token.") from exc

        return BotUser(token=token), token

    def authenticate_header(self, request) -> str:
        return self.keyword
