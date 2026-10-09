# FX Unified Trade Lifecycle & Exit Notification Specification

- Status: **mandatory architecture specification; implementation in progress**
- Repository: `rikuudon24-beep/chair-scale`
- Scope: every FX strategy, timeframe, pair, and live-monitor workflow in this repository
- Purpose: no strategy is considered operationally complete when it only reports entries; it must track each accepted entry through a terminal outcome and notify the user of the exit.

## 1. Non-negotiable rule

**Every entry notification must have a corresponding lifecycle record and an exit-notification path.** Entry-only monitors are candidate detectors, not complete trade-monitoring systems.

A strategy may define its own entry and exit rules, but must use the common lifecycle contract and notification delivery/audit layer. A strategy-specific exit rule is permitted; silently omitting exit monitoring is not.

Research-only backtests and hypothetical candidates must be explicitly labeled as such and must not be presented as actual open positions.

## 2. Common lifecycle

`CANDIDATE -> ENTRY_PENDING -> OPEN -> EXIT_PENDING -> CLOSED`

Additional safe states:
- `REJECTED`: entry confirmation failed; no position was opened.
- `CANCELLED`: pending entry expired or was invalidated by the strategy.
- `UNKNOWN`: market data, state integrity, or monitoring freshness is insufficient to determine whether the position remains open.
- `DELIVERY_PENDING`: an event exists but one or more required notification channels have not acknowledged delivery.
- `ERROR`: the monitor failed; never translate this into `HOLD` or “no exit”.

The lifecycle state and notification-delivery state are separate. A position can be `CLOSED` while its exit notification is still `DELIVERY_PENDING`.

## 3. Required common trade record

Every accepted entry must be persisted with a stable `trade_id` and at minimum:

- `trade_id`, `strategy_id`, `strategy_version`
- `pair`, `timeframe`, `direction`
- `signal_time`, `entry_time`, `entry_price`
- `initial_sl`, `initial_tp`, `exit_policy`, `time_limit` (where applicable)
- `status`, `last_checked_bar_time`, `data_source`
- `exit_time`, `exit_price`, `exit_reason`, `gross_pips`, `net_pips` (when calculable)
- `created_at`, `updated_at`, `closed_at`

Fields that do not apply to a strategy may be null, but the reason must be explicit in its adapter/configuration. Never invent an entry or exit price when unavailable.

## 4. Common event / notification record

Persist each lifecycle event to a durable outbox/audit ledger before attempting delivery.

Required fields:
- `event_id` (deterministic/idempotent), `trade_id`, `event_type`
- `event_time`, `pair`, `timeframe`, `direction`
- `price`, `reason`, `tp`, `sl`, `strategy_id`
- `delivery_status`, `attempt_count`, `last_attempt_at`, `delivered_at`, `last_error`

Event types include `ENTRY_CONFIRMED`, `ENTRY_REJECTED`, `EXIT_TP`, `EXIT_SL`, `EXIT_SIGNAL`, `EXIT_TIME`, `EXIT_MANUAL`, `MONITORING_DEGRADED`, and `MONITORING_RECOVERED`.

The same event ID must not produce duplicate notifications after workflow retries. If a delivery response is ambiguous, check whether the event was already published before retrying a non-idempotent create operation.

## 5. Exit evaluation requirements

1. Evaluate only completed candles unless the strategy explicitly specifies and validates intrabar evaluation.
2. Process **every completed bar since the last durable checkpoint**, not only the latest bar. A skipped hourly/scheduled run must not erase an intermediate TP/SL touch.
3. Apply the strategy's frozen exit policy. Common supported reasons are TP, SL, strategy-specific exit signal, time/horizon exit, and manual/external closure.
4. If TP and SL are both touched within the same candle and lower-resolution data cannot disambiguate, apply the conservative rule `SL first` and record that assumption.
5. Evaluate time exits at the specified horizon candle close; do not silently defer the exit by one more bar.
6. If data is stale, missing, contradictory, or state is corrupt, mark the result `UNKNOWN`/monitoring degraded and raise a diagnostic alert. Never claim `HOLD_NO_EXIT` from invalid data.
7. Once closed, the trade remains in the ledger permanently; subsequent runs must not reopen it or emit a second exit event.
8. Prevent overlapping trades per pair/strategy where the strategy rules require non-overlap; do not apply one strategy's restriction to another without an explicit rule.

## 6. Delivery and user-facing message

The notification dispatcher is channel-independent. It must support:
- durable GitHub Issue/event publication as the currently available fallback channel;
- a future ChatGPT/user push adapter only when a real supported integration exists and is verified.

**GitHub Issues are not equivalent to a direct ChatGPT push notification.** Until a supported ChatGPT delivery channel is actually integrated and tested, report this limitation plainly.

An exit notification must state:
- EXIT (TP / SL / strategy signal / TIME / manual)
- pair, direction, timeframe, strategy
- entry price/time and exit price/time when known
- realized pips/R and cost-adjusted result when calculable
- exit reason and the rule that triggered it
- whether price is a signal close, stop/target execution assumption, or actual broker fill

Do not describe a signal price as a broker fill. The current system is notification/research only and does not execute broker orders.

## 7. Failure handling / integrity

- Each scheduled workflow must have non-overlapping execution or an equivalent locking/concurrency strategy.
- Persist lifecycle and pending notification events atomically where practical; avoid separate writes that can leave a closed position without an exit event.
- Retry transient network/API failures with bounded backoff and idempotency checks.
- Retain a failure diagnostic with run ID, strategy/pair, last completed bar, and traceback/error summary.
- Recovery must reconcile open trades, closed trades, and undelivered events from durable state. If an alert exists but its trade record is missing, flag state-integrity failure rather than silently ignoring it.
- A failed monitor run must not be interpreted as a no-signal/no-exit result.

## 8. Mandatory regression and acceptance tests

Every shared-engine or strategy-adapter change must test at least:
1. Entry creates exactly one trade and one entry event.
2. TP closes trade and creates exactly one exit event.
3. SL closes trade and creates exactly one exit event.
4. Strategy-specific exit closes trade and creates exactly one exit event.
5. Time exit happens at the configured horizon bar close.
6. A skipped run still catches an intermediate TP/SL touch.
7. Same-candle TP+SL follows the conservative configured priority.
8. Re-running after closure does not duplicate or reopen the trade.
9. A failed/ambiguous notification delivery is retried without duplicate publication.
10. Stale/missing data produces `UNKNOWN`/degraded diagnostics, never a false HOLD.
11. An open trade survives workflow restart and branch/state restoration.
12. An undelivered exit event survives restart and is delivered when the channel recovers.
13. Direction, pip size, pair precision, and exit prices are correct for JPY and non-JPY pairs.
14. A synthetic end-to-end trade proves ENTRY -> EXIT -> durable state -> notification delivery.

The workflow must fail if a regression test fails. A green CI run proves code/tests passed, not that a real-market exit or phone push has occurred.

## 9. Current repository baseline (verified 2026-10-09)

| Subsystem | Existing behavior | Required follow-up |
|---|---|---|
| H1 frozen v1 monitor (EURJPY, USDCHF, AUDNZD) | Durable position and alert ledgers; replays completed H1 bars; TP/SL/TIME exits; GitHub Issue publication; lifecycle tests | Migrate to the common contract/dispatcher; test actual durable EXIT event delivery end-to-end |
| H4 current notification state | Detects entry candidates and publishes entry Issues | Connect accepted entries to a common trade ledger and exit-policy adapter; entry detection alone is not complete |
| H4 position exit monitor | Separate `config/active_positions.json` input and `current_exit_alerts.csv` output | Reconcile with common ledger and common event publisher; paginate issue listing and make persistence/retries consistent |
| ChatGPT push | Not verified/implemented | Do not claim available; identify a supported delivery mechanism and prove receipt before marking complete |

Latest checked H1 Actions run `37868287986` completed successfully after the workflow was corrected to fail on regression-test failures. Earlier run `37868264856` showed 7/7 lifecycle regression tests passing. These validate the current H1 code path, but do not by themselves prove real-world entry-to-exit delivery or direct ChatGPT push.

## 10. Implementation order

1. Freeze this common contract and map every existing entry/exit workflow to it.
2. Build a shared lifecycle ledger + event outbox + idempotent notification dispatcher, with unit and synthetic end-to-end tests.
3. Migrate the H1 lifecycle monitor first (it already tracks TP/SL/TIME).
4. Migrate H4 direct-entry notifications and the independent H4 exit monitor to the same contract; remove parallel, conflicting sources of truth only after reconciliation tests pass.
5. Add monitor freshness/health alerts and undelivered-event recovery.
6. Add and verify the user-facing push channel; until then, explicitly label GitHub Issues as the durable fallback.
7. Only declare operational completion after synthetic end-to-end tests pass, workflow runs cleanly, state survives restart, and an exit event is demonstrably delivered. Do not wait for a real trade to occur to test this: use a synthetic trade fixture.
