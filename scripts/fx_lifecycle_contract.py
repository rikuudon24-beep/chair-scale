"""Shared, dependency-free contract for FX trade lifecycle and notification outbox.

This module is intentionally strategy-agnostic. Strategy monitors decide signals and
prices; this module owns stable IDs, state-transition validation, and durable CSV
upserts so entry/exit events can be reconciled across workflows.
"""
from __future__ import annotations

import csv
import hashlib
import os
import tempfile
from pathlib import Path
from typing import Iterable, Mapping

TRADE_STATES = {
    "CANDIDATE", "ENTRY_PENDING", "OPEN", "EXIT_PENDING", "CLOSED",
    "REJECTED", "CANCELLED", "UNKNOWN", "ERROR",
}
TERMINAL_STATES = {"CLOSED", "REJECTED", "CANCELLED"}
ALLOWED_TRANSITIONS = {
    "CANDIDATE": {"ENTRY_PENDING", "OPEN", "REJECTED", "CANCELLED", "UNKNOWN", "ERROR"},
    "ENTRY_PENDING": {"OPEN", "REJECTED", "CANCELLED", "UNKNOWN", "ERROR"},
    "OPEN": {"EXIT_PENDING", "CLOSED", "UNKNOWN", "ERROR"},
    "EXIT_PENDING": {"CLOSED", "OPEN", "UNKNOWN", "ERROR"},
    "UNKNOWN": {"ENTRY_PENDING", "OPEN", "EXIT_PENDING", "CLOSED", "REJECTED", "CANCELLED", "ERROR"},
    "ERROR": {"UNKNOWN", "ENTRY_PENDING", "OPEN", "EXIT_PENDING", "CLOSED"},
    "CLOSED": set(), "REJECTED": set(), "CANCELLED": set(),
}

TRADE_FIELDS = [
    "trade_id", "strategy_id", "strategy_version", "pair", "timeframe",
    "direction", "signal_time", "entry_time", "entry_price", "initial_sl",
    "initial_tp", "exit_policy", "time_limit", "status", "last_checked_bar_time",
    "data_source", "exit_time", "exit_price", "exit_reason", "gross_pips",
    "net_pips", "created_at", "updated_at", "closed_at",
]
EVENT_FIELDS = [
    "event_id", "trade_id", "event_type", "event_time", "pair", "timeframe",
    "direction", "price", "reason", "tp", "sl", "strategy_id",
    "delivery_status", "attempt_count", "last_attempt_at", "delivered_at",
    "last_error",
]
EVENT_TYPES = {
    "ENTRY_CONFIRMED", "ENTRY_REJECTED", "EXIT_TP", "EXIT_SL",
    "EXIT_SIGNAL", "EXIT_TIME", "EXIT_MANUAL", "MONITORING_DEGRADED",
    "MONITORING_RECOVERED",
}
DELIVERY_STATES = {"PENDING", "DELIVERING", "DELIVERED", "FAILED"}


def _stable_id(prefix: str, *parts: object) -> str:
    raw = "|".join("" if part is None else str(part) for part in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
    return f"{prefix}_{digest}"


def make_trade_id(strategy_id: str, pair: str, signal_time: str) -> str:
    """Stable identity for one strategy signal, independent of workflow run."""
    return _stable_id("trade", strategy_id, pair.lower(), signal_time)


def make_event_id(trade_id: str, event_type: str, event_time: str) -> str:
    """Stable identity for one lifecycle event; safe to reuse after a retry."""
    return _stable_id("event", trade_id, event_type.upper(), event_time)


def validate_transition(old_state: str, new_state: str) -> None:
    old_state = old_state.upper()
    new_state = new_state.upper()
    if old_state not in TRADE_STATES:
        raise ValueError(f"unknown current trade state: {old_state}")
    if new_state not in TRADE_STATES:
        raise ValueError(f"unknown target trade state: {new_state}")
    if new_state == old_state:
        return
    if new_state not in ALLOWED_TRANSITIONS[old_state]:
        raise ValueError(f"invalid trade transition: {old_state} -> {new_state}")


def validate_event(event: Mapping[str, object]) -> None:
    missing = [key for key in ("event_id", "trade_id", "event_type", "event_time", "pair", "strategy_id")
               if not str(event.get(key, "")).strip()]
    if missing:
        raise ValueError("event missing required fields: " + ", ".join(missing))
    if str(event["event_type"]).upper() not in EVENT_TYPES:
        raise ValueError(f"unknown event type: {event['event_type']}")
    delivery = str(event.get("delivery_status") or "PENDING").upper()
    if delivery not in DELIVERY_STATES:
        raise ValueError(f"unknown delivery status: {delivery}")


def read_ledger(path: str | Path, fields: list[str]) -> list[dict[str, str]]:
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [{key: (row.get(key) or "") for key in fields} for row in reader]


def upsert_ledger(path: str | Path, fields: list[str], rows: Iterable[Mapping[str, object]],
                  key_field: str) -> list[dict[str, str]]:
    """Atomically upsert records by stable key; repeated calls do not duplicate rows."""
    if key_field not in fields:
        raise ValueError(f"key field {key_field!r} is not in ledger schema")
    path = Path(path)
    current = read_ledger(path, fields)
    by_key = {row.get(key_field, ""): row for row in current if row.get(key_field, "")}
    for incoming in rows:
        row = {field: "" if incoming.get(field) is None else str(incoming.get(field, "")) for field in fields}
        key = row.get(key_field, "")
        if not key:
            raise ValueError(f"cannot upsert row without {key_field}")
        if key in by_key:
            old = by_key[key]
            if key_field == "trade_id" and old.get("status") and row.get("status"):
                old_status = old["status"].upper()
                new_status = row["status"].upper()
                if old_status in TERMINAL_STATES and new_status != old_status:
                    raise ValueError(f"terminal trade cannot change state: {old_status} -> {new_status} ({key})")
                validate_transition(old_status, new_status)
            # Preserve an acknowledged delivery; never downgrade DELIVERED to PENDING.
            if old.get("delivery_status") == "DELIVERED" and row.get("delivery_status") != "DELIVERED":
                row["delivery_status"] = "DELIVERED"
                row["delivered_at"] = old.get("delivered_at", "")
            by_key[key] = row
        else:
            by_key[key] = row
    result = list(by_key.values())
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(result)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise
    return result
