"""Formatting helpers for bot messages."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from . import strings


def format_trip_summary(trip: Dict[str, Any]) -> str:
    title = trip.get("title", strings.TRIP_DEFAULT_TITLE)
    place = trip.get("place_detail", {}).get("name") or ""
    trip_start = _format_date(trip.get("trip_start"))
    trip_end = _format_date(trip.get("trip_end"))
    price = trip.get("default_price", "N/A")

    lines = [f"<b>{title}</b>"]
    if place:
        lines.append(strings.TRIP_LOCATION.format(location=place))
    if trip_start and trip_end:
        lines.append(strings.TRIP_DATES.format(start=trip_start, end=trip_end))
    elif trip_start:
        lines.append(strings.TRIP_STARTS.format(start=trip_start))
    if price:
        lines.append(strings.TRIP_PRICE.format(price=price))
    description = trip.get("description")
    if description:
        lines.append("")
        lines.append(description)
    return "\n".join(lines)


def _format_date(value: str | None) -> str:
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(str(value))
    except ValueError:
        return str(value)
    return dt.strftime("%d %b %Y")
