#!/usr/bin/env python3
"""Reconcile registered H4 position-exit signals into the shared lifecycle ledger.

This adapter does not infer broker fills. EXIT_TRIGGERED means EXIT_PENDING, not
CLOSED; the signal-close price is recorded only on the notification event.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from fx_lifecycle_contract import (  # noqa: E402
    EVENT_FIELDS, TRADE_FIELDS, make_event_id, make_trade_id,
    read_ledger, upsert_ledger, validate_event,
)

CONFIG = ROOT / "config/active_positions.json"
STATE = ROOT / "reports/current_position_exit_state.csv"
ALERTS = ROOT / "reports/current_exit_alerts.csv"
TRADES = ROOT / "reports/fx_trade_lifecycle.csv"
OUTBOX = ROOT / "reports/fx_notification_outbox.csv"
STRATEGY_ID = "h4_position_exit_v1"


def iso(value) -> str:
    if value is None or pd.isna(value) or not str(value).strip():
        return ""
    return pd.Timestamp(value).isoformat()


def main() -> None:
    if not CONFIG.exists() or not STATE.exists() or not ALERTS.exists():
        raise RuntimeError("H4 config/state/alerts missing; refusing partial lifecycle reconciliation")

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    positions = [p for p in config.get("positions", []) if p.get("status") == "open"]
    state_df = pd.read_csv(STATE, dtype=str).fillna("")
    alerts_df = pd.read_csv(ALERTS, dtype=str).fillna("")
    state_by_id = {}
    for _, row in state_df.iterrows():
        pid = str(row.get("id", ""))
        if not pid or pid in state_by_id:
            raise RuntimeError(f"missing/duplicate H4 position state ID: {pid!r}")
        state_by_id[pid] = row.to_dict()

    alert_by_id = {}
    for _, row in alerts_df.iterrows():
        pid = str(row.get("id", ""))
        ts = iso(row.get("exit_signal_timestamp", ""))
        key = (pid, ts)
        if not pid or not ts or key in alert_by_id:
            raise RuntimeError(f"missing/duplicate H4 exit alert identity: {key!r}")
        alert_by_id[key] = row.to_dict()

    existing_trades = {r["trade_id"]: r for r in read_ledger(TRADES, TRADE_FIELDS)}
    # Preserve exit intent across UNKNOWN/degraded runs as well as repeated EXIT_TRIGGERED runs.
    existing_outbox = read_ledger(OUTBOX, EVENT_FIELDS)
    exit_signal_trade_ids = {
        r["trade_id"] for r in existing_outbox
        if r.get("event_type", "").upper() == "EXIT_SIGNAL"
    }
    trade_rows = []
    outbox_rows = []
    now = datetime.now(timezone.utc).isoformat()

    for pos in positions:
        pid = str(pos.get("id", ""))
        pair = str(pos.get("pair", "")).lower()
        direction = str(pos.get("direction", "")).lower()
        entry_time = iso(pos.get("entry_timestamp", ""))
        entry_price = str(pos.get("reference_entry_price", ""))
        if not all((pid, pair, direction in ("long", "short"), entry_time, entry_price)):
            raise RuntimeError(f"incomplete registered H4 position: {pos!r}")
        if pid not in state_by_id:
            raise RuntimeError(f"H4 position has no evaluated state row: {pid}")
        state = state_by_id[pid]
        state_name = str(state.get("state", "")).upper()
        if state_name not in ("HOLD_NO_EXIT", "EXIT_TRIGGERED", "UNKNOWN"):
            raise RuntimeError(f"unrecognized H4 state {state_name!r} for {pid}")

        # Use entry timestamp only as a stable legacy-position identity because
        # the old config does not preserve the original entry signal timestamp.
        trade_id = make_trade_id(STRATEGY_ID, pair, entry_time)
        prior = existing_trades.get(trade_id, {})
        prior_status = str(prior.get("status", "")).upper()
        if state_name == "EXIT_TRIGGERED":
            status = "EXIT_PENDING"
        elif state_name == "UNKNOWN":
            status = "UNKNOWN"
        else:
            # A prior exit signal remains pending until an external/manual close
            # is confirmed; a later HOLD result must not erase that signal.
            status = "EXIT_PENDING" if (
                prior_status == "EXIT_PENDING" or trade_id in exit_signal_trade_ids
            ) else "OPEN"

        trade_rows.append({
            "trade_id": trade_id, "strategy_id": STRATEGY_ID, "strategy_version": "v1",
            "pair": pair.upper(), "timeframe": "H4", "direction": direction.upper(),
            "signal_time": "", "entry_time": entry_time, "entry_price": entry_price,
            "initial_sl": "", "initial_tp": "", "exit_policy": "PLUS50_THEN_DI_EXIT_SIGNAL",
            "time_limit": "", "status": status,
            "last_checked_bar_time": iso(state.get("latest_completed_h4", "")),
            "data_source": str(pos.get("source", "legacy_registered_h4_position")),
            # No actual broker fill is available: do not populate exit time/price.
            "exit_time": "", "exit_price": "", "exit_reason": (
                str(state.get("exit_reason", "")) if state_name == "EXIT_TRIGGERED" else ""
            ),
            "gross_pips": "", "net_pips": "",
            "created_at": prior.get("created_at") or entry_time,
            "updated_at": now, "closed_at": "",
        })

        if state_name == "EXIT_TRIGGERED":
            ts = iso(state.get("exit_signal_timestamp", ""))
            match = alert_by_id.get((pid, ts))
            if not match:
                raise RuntimeError(f"EXIT_TRIGGERED state has no matching alert row: {pid} {ts}")
            event_id = make_event_id(trade_id, "EXIT_SIGNAL", ts)
            prior_event = next(
                (row for row in existing_outbox if row.get("event_id") == event_id), {}
            )
            event = {
                "event_id": event_id, "trade_id": trade_id, "event_type": "EXIT_SIGNAL",
                "event_time": ts, "pair": pair.upper(), "timeframe": "H4",
                "direction": direction.upper(), "price": str(match.get("exit_signal_price", "")),
                "reason": str(match.get("exit_reason", "")), "tp": "", "sl": "",
                "strategy_id": STRATEGY_ID,
                # Reconciliation must not reset retry/delivery state for a stable event.
                "delivery_status": prior_event.get("delivery_status") or "PENDING",
                "attempt_count": prior_event.get("attempt_count") or "0",
                "last_attempt_at": prior_event.get("last_attempt_at", ""),
                "delivered_at": prior_event.get("delivered_at", ""),
                "last_error": prior_event.get("last_error", ""),
            }
            validate_event(event)
            outbox_rows.append(event)

    # Keep history if a registered position is later removed from config.
    current_ids = {r["trade_id"] for r in trade_rows}
    for tid, row in existing_trades.items():
        if row.get("status", "").upper() == "CLOSED" and tid not in current_ids:
            trade_rows.append(row)

    # Persist the durable notification intent first. If the subsequent trade-ledger
    # write fails, the next run can reconstruct the trade from the same stable event.
    upsert_ledger(OUTBOX, EVENT_FIELDS, outbox_rows, "event_id")
    upsert_ledger(TRADES, TRADE_FIELDS, trade_rows, "trade_id")
    print(f"H4 lifecycle reconciliation: {len(trade_rows)} trade rows; {len(outbox_rows)} exit events")


if __name__ == "__main__":
    main()
