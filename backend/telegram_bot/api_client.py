"""Async HTTP client for interacting with the LocTur backend."""
from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Optional

import httpx

logger = logging.getLogger(__name__)


class APIClientError(RuntimeError):
    """Raised when the backend API returns an error response."""

    def __init__(self, message: str, *, status_code: int | None = None, payload: Any | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class APIClient:
    """Lightweight wrapper around the backend API for bot operations."""

    def __init__(self, base_url: str, bot_token: str, *, timeout: float = 30.0):
        if not base_url.endswith("/"):
            base_url = f"{base_url}/"
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
        self._headers = {"X-Bot-Token": bot_token}

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _request(self, method: str, url: str, *, params: dict | None = None, data: dict | None = None, files: dict | None = None) -> Any:
        response = await self._client.request(method, url, params=params, data=data, files=files, headers=self._headers)
        if response.status_code >= 400:
            content_type = response.headers.get("content-type", "")
            detail: Any
            if "application/json" in content_type:
                detail = response.json()
            else:
                detail = response.text
            logger.warning("Backend API error (%s %s): %s", method, url, detail)
            raise APIClientError(
                f"Backend API request failed with status {response.status_code}",
                status_code=response.status_code,
                payload=detail,
            )
        if response.status_code == 204:
            return None
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        return response.text

    async def _paginate(self, url: str, *, params: dict | None = None) -> List[dict]:
        items: List[dict] = []
        next_url: Optional[str] = url
        query_params = dict(params or {})

        while next_url:
            data = await self._request("GET", next_url, params=query_params)
            if isinstance(data, dict) and "results" in data:
                items.extend(data.get("results") or [])
                # absolute URL, rely on httpx client to handle
                next_url = data.get("next")
                query_params = None  # already included in next
            else:
                if isinstance(data, list):
                    items.extend(data)
                break
        return items

    async def get_traveler_by_telegram_id(self, telegram_id: str) -> Optional[dict]:
        data = await self._request("GET", "travelers/", params={"telegram_id": telegram_id})
        if isinstance(data, dict) and data.get("results"):
            return data["results"][0]
        return None

    async def create_traveler(self, payload: Dict[str, Any]) -> dict:
        return await self._request("POST", "travelers/", data=payload)

    async def update_traveler(self, traveler_id: str, payload: Dict[str, Any]) -> dict:
        return await self._request("PATCH", f"travelers/{traveler_id}/", data=payload)

    async def list_trips(self, *, status: str | None = None) -> List[dict]:
        params: Dict[str, Any] = {}
        if status:
            params["status"] = status
        return await self._paginate("trips/", params=params)

    async def get_trip(self, trip_id: str) -> dict:
        return await self._request("GET", f"trips/{trip_id}/")

    async def create_user_trip(self, payload: Dict[str, Any], *, files: Dict[str, Any]) -> dict:
        return await self._request("POST", "user-trips/", data=payload, files=files)

    async def list_user_trips(self, *, filters: Dict[str, Any]) -> List[dict]:
        return await self._paginate("user-trips/", params=filters)

    async def get_user_trip(self, user_trip_id: str) -> dict:
        return await self._request("GET", f"user-trips/{user_trip_id}/")

    async def report_group_join(self, user_trip_id: str, *, success: bool, error: str | None = None) -> dict:
        data = {"success": "true" if success else "false"}
        if not success:
            data["error"] = error or "Unable to add traveler to group."
        return await self._request("POST", f"user-trips/{user_trip_id}/group-join/", data=data)

    async def link_trip_group(self, trip_id: str, *, chat_id: int | str, invite_link: str | None = None) -> dict:
        data: Dict[str, Any] = {"chat_id": str(chat_id)}
        if invite_link:
            data["invite_link"] = invite_link
        return await self._request("POST", f"trips/{trip_id}/link-group/", data=data)
