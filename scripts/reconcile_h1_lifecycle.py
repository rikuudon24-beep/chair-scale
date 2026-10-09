#!/usr/bin/env python3
"""Project the frozen H1 monitor's source ledgers into the common FX lifecycle contract.

The H1 position/alert CSVs remain the frozen strategy adapter's source of truth.
This script creates/upserts the cross-strategy trade ledger and notification outbox.
It does not fabricate exit timestamps: exit events must reconcile to a CLOSED trade.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from fx_lifecycle_contract import (  # noqa: E402
    EVENT_FIELDS, TRADE_FIELDS, make_trade_id, upsert_ledger, validate_event,
)

POSITIONS = ROOT / "reports/h1_live_positions.csv"
ALERTS = ROOT / "reports/h1_live_alerts.csv"
TRADES = ROOT / "reports/fx_trade_lifecycle.csv"
OUTBOX = ROOT / "reports/fx_notification_outbox.csv"

TP_SL_HORIZON = {
    "eurjpy": (100, 40, 72),
    "usdchf": (40, 40, 48),
    "audnzd": (60, 75, 72),
}


def iso_or_empty(value):
    if value is None or pd.isna(value) or str(value).strip() in ("", "nan", "NaT"):
        return ""
    return pd.Timestamp(value).isoformat()


def main():
    if not POSITIONS.exists() or not ALERTS.exists():
        raise RuntimeError("H1 source ledgers missing; refusing to create an incomplete common ledger")

    positions = pd.read_csv(POSITIONS).fillna("")
    alerts = pd.read_csv(ALERTS).fillna("")
    now = datetime.now(timezone.utc).isoformat()

    # Map exit alerts to their closed position. A missing match is a state-integrity
    # failure, not permission to guess the exit timestamp or price.
    exit_alerts = {}
    for _, a in alerts.iterrows():
        if str(a["kind"]).startswith("EXIT_"):
            key = (str(a["pair"]).lower(), str(a["signal_time"]))
            if key in exit_alerts:
                raise RuntimeError(f"duplicate exit events for one H1 trade: {key}")
            exit_alerts[key] = a

    trade_rows = []
    for _, p in positions.iterrows():
        pair = str(p["pair"]).lower()
        strategy_id = f"h1_{pair}_v1"
        signal_time = iso_or_empty(p["signal_time"])
        trade_id = make_trade_id(strategy_id, pair, signal_time)
        status_map = {
            "OPEN": "OPEN",
            "PENDING": "ENTRY_PENDING",
            "CONFIRMING": "CANDIDATE",
            "CLOSED": "CLOSED",
        }
        old_status = str(p["status"]).upper()
        if old_status not in status_map:
            raise RuntimeError(f"unrecognized H1 position status {old_status!r} for {pair}")
        tp_pips, sl_pips, horizon = TP_SL_HORIZON[pair]
        entry_price = str(p.get("entry_price", ""))
        tp = str(p.get("tp", ""))
        sl = str(p.get("sl", ""))
        event = exit_alerts.get((pair, str(p["signal_time"]))) if old_status == "CLOSED" else None
        # A CLOSED row can also mean failed entry confirmation; that is not a trade.
        is_exit_closed = event is not None
        exit_time = iso_or_empty(p.get("last_checked", "")) if is_exit_closed else ""
        exit_price = str(event["price"]) if is_exit_closed else ""
        exit_reason = str(event["kind"]) if is_exit_closed else ("ENTRY_CONFIRMATION_FAILED" if old_status == "CLOSED" else "")
        gross_pips = ""
        if is_exit_closed and entry_price and exit_price:
            pip_size = 0.01 if "jpy" in pair else 0.0001
            gross_pips = str((float(exit_price) - float(entry_price)) / pip_size)

        trade_rows.append({
            "trade_id": trade_id, "strategy_id": strategy_id, "strategy_version": "v1",
            "pair": pair.upper(), "timeframe": "H1", "direction": str(p["direction"]).upper(),
            "signal_time": signal_time, "entry_time": iso_or_empty(p.get("entry_time", "")),
            "entry_price": entry_price, "initial_sl": sl, "initial_tp": tp,
            "exit_policy": "TP_SL_TIME", "time_limit": f"{horizon}H",
            "status": "CLOSED" if is_exit_closed else status_map[old_status],
            "last_checked_bar_time": iso_or_empty(p.get("last_checked", "")),
            "data_source": "Yahoo Finance chart API via H1 live source",
            "exit_time": exit_time, "exit_price": exit_price, "exit_reason": exit_reason,
            "gross_pips": gross_pips, "net_pips": "",
            "created_at": signal_time, "updated_at": now,
            "closed_at": exit_time if is_exit_closed else "",
        })

    # Preserve closed trades omitted by an adapter bug rather than deleting history.
    existing = {r["trade_id"]: r for r in __import__(
        "fx_lifecycle_contract"
    ).read_ledger(TRADES, TRADE_FIELDS)}
    current_ids = {r["trade_id"] for r in trade_rows}
    for tid, row in existing.items():
        if row.get("status") == "CLOSED" and tid not in current_ids:
            trade_rows.append(row)

    outbox_rows = []
    event_type_map = {
        "ENTRY": "ENTRY_CONFIRMED", "EXIT_TP": "EXIT_TP",
        "EXIT_SL": "EXIT_SL", "EXIT_TIME": "EXIT_TIME",
    }
    for _, a in alerts.iterrows():
        kind = str(a["kind"]).upper()
        if kind not in event_type_map:
            raise RuntimeError(f"unmapped H1 alert type: {kind}")
        pair = str(a["pair"]).lower()
        strategy_id = f"h1_{pair}_v1"
        signal_time = iso_or_empty(a["signal_time"])
        trade_id = make_trade_id(strategy_id, pair, signal_time)
        if kind == "ENTRY":
            event_time = iso_or_empty(a["entry_time"])
        else:
            match = positions[
                (positions["pair"].astype(str).str.lower() == pair)
                & (positions["signal_time"].astype(str) == str(a["signal_time"]))
                & (positions["status"].astype(str).str.upper() == "CLOSED")
            ]
            if match.empty:
                raise RuntimeError(f"exit alert has no CLOSED position: {pair} {signal_time} {kind}")
            event_time = iso_or_empty(match.iloc[-1].get("last_checked", ""))
        if not event_time:
            raise RuntimeError(f"event time missing for {pair} {kind} {signal_time}")
        # Keep legacy alert_id as event_id so the existing Issue publisher remains
        # idempotent and old notifications are not duplicated during migration.
        event_id = str(a["alert_id"])
        row = {
            "event_id": event_id, "trade_id": trade_id, "event_type": event_type_map[kind],
            "event_time": event_time, "pair": pair.upper(), "timeframe": "H1",
            "direction": str(a["direction"]).upper(), "price": str(a["price"]),
            "reason": str(a["message"]), "tp": str(a["tp"]), "sl": str(a["sl"]),
            "strategy_id": strategy_id, "delivery_status": "PENDING",
            "attempt_count": "0", "last_attempt_at": "", "delivered_at": "", "last_error": "",
        }
        validate_event(row)
        outbox_rows.append(row)

    upsert_ledger(TRADES, TRADE_FIELDS, trade_rows, "trade_id")
    upsert_ledger(OUTBOX, EVENT_FIELDS, outbox_rows, "event_id")
    print(f"Common lifecycle projection: {len(trade_rows)} trade rows; {len(outbox_rows)} event rows")
    print(f"Trade ledger: {TRADES}")
    print(f"Notification outbox: {OUTBOX}")


if __name__ == "__main__":
    main()
