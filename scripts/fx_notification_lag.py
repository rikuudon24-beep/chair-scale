"""Measure elapsed time from a confirmed signal timestamp to durable Issue creation."""
from __future__ import annotations

from datetime import datetime, timezone


def parse_utc(value: str) -> datetime:
    raw = str(value or "").strip()
    if not raw:
        raise ValueError("timestamp is empty")
    parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp has no timezone: {value!r}")
    return parsed.astimezone(timezone.utc)


def measure_signal_to_issue(signal_time: str, issue_created_at: str, timeframe: str) -> dict[str, str]:
    signal = parse_utc(signal_time)
    created = parse_utc(issue_created_at)
    seconds = (created - signal).total_seconds()
    if seconds < 0:
        return {"issue_created_at": created.isoformat(), "signal_to_issue_seconds": "", "signal_to_issue_status": "TIMESTAMP_ORDER_INVALID"}
    threshold = 2 * 3600 if str(timeframe).upper() == "H1" else 6 * 3600 if str(timeframe).upper() == "H4" else None
    status = "UNKNOWN" if threshold is None else "LATE" if seconds > threshold else "ON_TIME"
    return {
        "issue_created_at": created.isoformat(),
        "signal_to_issue_seconds": str(round(seconds, 3)),
        "signal_to_issue_status": status,
    }
