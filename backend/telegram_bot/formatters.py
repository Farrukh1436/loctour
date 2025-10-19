"""Formatting helpers for bot messages."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


def format_trip_summary(trip: Dict[str, Any]) -> str:
    title = trip.get("title", "Trip")
    place = trip.get("place_detail", {}).get("name") or ""
    trip_start = _format_date(trip.get("trip_start"))
    trip_end = _format_date(trip.get("trip_end"))
    price = trip.get("default_price", "N/A")

    lines = [f"<b>{title}</b>"]
    if place:
        lines.append(f"Location: {place}")
    if trip_start and trip_end:
        lines.append(f"Dates: {trip_start} → {trip_end}")
    elif trip_start:
        lines.append(f"Starts: {trip_start}")
    if price:
        lines.append(f"Price: {price}")
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
