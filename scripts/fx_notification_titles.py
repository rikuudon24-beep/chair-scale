"""Stable GitHub Issue title mapping for FX notification outbox events."""
from __future__ import annotations


def issue_title_candidates(row: dict[str, str]) -> list[str]:
    """Return current and migration-compatible issue titles for one outbox event."""
    timeframe = str(row.get("timeframe", "")).upper()
    event_type = str(row.get("event_type", "")).upper()
    pair = str(row.get("pair", ""))
    direction = str(row.get("direction", ""))
    event_time = str(row.get("event_time", ""))
    if timeframe == "H1" and row.get("event_id"):
        return [f"FX H1 ALERT {row['event_id']}"]
    if timeframe == "H4" and event_type == "EXIT_SIGNAL" and pair and direction and event_time:
        # AUD/NZD uses the new uppercase, candle-keyed title. The lowercase
        # variant retains compatibility with legacy H4 publisher titles.
        return list(dict.fromkeys([
            f"FX EXIT {pair.upper()} {direction.upper()} {event_time}",
            f"FX EXIT {pair.lower()} {direction.lower()} {event_time}",
        ]))
    return []
