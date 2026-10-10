#!/usr/bin/env python3
"""Reconcile the manually held AUD/NZD long into the shared FX lifecycle.

Entry timestamp/price are intentionally blank because they were not recorded.
This adapter only publishes an exit signal; it never infers a broker fill or places orders.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fx_lifecycle_contract import (
    EVENT_FIELDS, TRADE_FIELDS, make_event_id, read_ledger, upsert_ledger, validate_event,
)

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "reports/audnzd_exit_state.json"
TRADES = ROOT / "reports/fx_trade_lifecycle.csv"
OUTBOX = ROOT / "reports/fx_notification_outbox.csv"

# Stable manual-position identity, not a fabricated entry timestamp or price.
TRADE_ID = "manual_audnzd_long_position"
STRATEGY_ID = "audnzd_manual_position_exit_v1"


def main() -> None:
    if not STATE.exists():
        raise RuntimeError("AUD/NZD exit state is missing; refusing lifecycle reconciliation")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if str(state.get("pair", "")).replace("/", "").upper() != "AUDNZD":
        raise RuntimeError(f"unexpected pair in AUD/NZD exit state: {state.get('pair')!r}")
    if str(state.get("direction", "")).upper() != "LONG":
        raise RuntimeError(f"unexpected direction in AUD/NZD exit state: {state.get('direction')!r}")

    candle = str(state.get("signal_candle_utc", "")).strip()
    if not candle:
        raise RuntimeError("AUD/NZD exit state has no completed-candle timestamp")
    state_name = str(state.get("state", "")).upper()
    if state_name not in {"EXIT_CANDIDATE", "NO_EXIT_CANDIDATE"}:
        raise RuntimeError(f"unrecognized AUD/NZD exit state: {state_name!r}")
    if state.get("data_status") != "FRESH_CONFIRMED_H4":
        raise RuntimeError("AUD/NZD exit state is not marked FRESH_CONFIRMED_H4")

    existing_trades = {row["trade_id"]: row for row in read_ledger(TRADES, TRADE_FIELDS)}
    existing_events = read_ledger(OUTBOX, EVENT_FIELDS)
    prior = existing_trades.get(TRADE_ID, {})
    prior_status = str(prior.get("status", "")).upper()
    prior_exit_events = [
        row for row in existing_events
        if row.get("trade_id") == TRADE_ID and row.get("event_type", "").upper() == "EXIT_SIGNAL"
    ]
    now = datetime.now(timezone.utc).isoformat()

    # A terminal record must never be reopened by a stale monitor result.
    if prior_status in {"CLOSED", "REJECTED", "CANCELLED"}:
        print(f"AUD/NZD manual lifecycle is terminal ({prior_status}); preserving existing row.")
        return

    event_id = make_event_id(TRADE_ID, "EXIT_SIGNAL", candle)
    existing_event = next((row for row in existing_events if row.get("event_id") == event_id), {})
    has_exit_intent = bool(prior_exit_events) or prior_status == "EXIT_PENDING"
    if state_name == "EXIT_CANDIDATE" or has_exit_intent:
        status = "EXIT_PENDING"
    elif state_name == "NO_EXIT_CANDIDATE":
        status = "OPEN"
    else:
        status = "UNKNOWN"

    trade = {
        "trade_id": TRADE_ID,
        "strategy_id": STRATEGY_ID,
        "strategy_version": "manual-position-monitor-v1",
        "pair": "AUDNZD",
        "timeframe": "H4",
        "direction": "LONG",
        "signal_time": "",
        "entry_time": "",
        "entry_price": "",
        "initial_sl": "",
        "initial_tp": "",
        "exit_policy": "MULTI_SIGNAL_H4_EXIT_CANDIDATE",
        "time_limit": "",
        "status": status,
        "last_checked_bar_time": candle,
        "data_source": "manual_position_exit_monitor; entry details intentionally unknown",
        "exit_time": "",
        "exit_price": "",
        "exit_reason": str(state.get("reasons", "")) if state_name == "EXIT_CANDIDATE" else prior.get("exit_reason", ""),
        "gross_pips": "",
        "net_pips": "",
        "created_at": prior.get("created_at") or now,
        "updated_at": now,
        "closed_at": "",
    }
    upsert_ledger(TRADES, TRADE_FIELDS, [trade], "trade_id")

    if state_name == "EXIT_CANDIDATE":
        event = {
            "event_id": event_id,
            "trade_id": TRADE_ID,
            "event_type": "EXIT_SIGNAL",
            "event_time": candle,
            "pair": "AUDNZD",
            "timeframe": "H4",
            "direction": "LONG",
            "price": str(state.get("signal_close", "")),
            "reason": str(state.get("reasons", "")),
            "tp": "",
            "sl": "",
            "strategy_id": STRATEGY_ID,
            "delivery_status": existing_event.get("delivery_status") or "PENDING",
            "attempt_count": existing_event.get("attempt_count") or "0",
            "last_attempt_at": existing_event.get("last_attempt_at", ""),
            "issue_confirmed_at": existing_event.get("issue_confirmed_at", ""),
            "delivered_at": existing_event.get("delivered_at", ""),
            "last_error": existing_event.get("last_error", ""),
        }
        validate_event(event)
        upsert_ledger(OUTBOX, EVENT_FIELDS, [event], "event_id")

    print(
        f"AUD/NZD manual lifecycle reconciled: status={status}; "
        f"entry_time=unknown; entry_price=unknown; "
        f"exit_events={len(prior_exit_events) + (1 if state_name == 'EXIT_CANDIDATE' and not existing_event else 0)}"
    )


if __name__ == "__main__":
    main()
