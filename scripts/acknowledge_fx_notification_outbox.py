#!/usr/bin/env python3
"""Acknowledge durable GitHub Issue publication and measure signal-to-Issue lag.

This does not claim that a ChatGPT/iOS push was delivered or seen.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from fx_lifecycle_contract import EVENT_FIELDS, read_ledger, upsert_ledger
from fx_notification_lag import measure_signal_to_issue
from fx_notification_titles import issue_title_candidates

path = "reports/fx_notification_outbox.csv"


def api_json(url: str, headers: dict[str, str]):
    req = Request(url, headers=headers)
    with urlopen(req, timeout=30) as response:
        return json.load(response)


def reconcile_rows(rows: list[dict[str, str]], issues: list[dict], now: str) -> tuple[list[dict[str, str]], int, int]:
    issue_by_title = {
        issue.get("title", ""): issue
        for issue in issues
        if "pull_request" not in issue and issue.get("title")
    }
    confirmed = 0
    late = 0
    for row in rows:
        candidates = issue_title_candidates(row)
        if not candidates:
            if row.get("delivery_status", "").upper() not in {"ISSUE_CONFIRMED", "DELIVERED"}:
                event_type = row.get("event_type", "").upper()
                row["delivery_status"] = "PENDING"
                row["last_error"] = f"No issue-title mapping for event type/timeframe: {event_type}/{row.get('timeframe', '')}"
            continue

        matched = next((issue_by_title[title] for title in candidates if title in issue_by_title), None)
        if not matched:
            if row.get("delivery_status", "").upper() not in {"ISSUE_CONFIRMED", "DELIVERED"}:
                row["delivery_status"] = "PENDING"
                row["last_attempt_at"] = now
                row["attempt_count"] = str(int(row.get("attempt_count") or "0") + 1)
                row["last_error"] = f"Durable Issue not found for any supported title: {' | '.join(candidates)}; will retry on next scheduled run."
            continue

        created_at = str(matched.get("created_at", "")).strip()
        if created_at:
            try:
                lag = measure_signal_to_issue(row.get("event_time", ""), created_at, row.get("timeframe", ""))
                row.update(lag)
                if lag["signal_to_issue_status"] == "LATE":
                    late += 1
            except (ValueError, TypeError) as exc:
                row["signal_to_issue_status"] = "UNKNOWN"
                row["signal_to_issue_seconds"] = ""
                row["issue_created_at"] = created_at
                row["last_error"] = f"Issue exists but signal-to-Issue lag could not be calculated: {exc}"
        else:
            row["signal_to_issue_status"] = "UNKNOWN"
            row["last_error"] = "Issue exists but its created_at timestamp was unavailable."

        row["delivery_status"] = "ISSUE_CONFIRMED"
        row["issue_confirmed_at"] = row.get("issue_confirmed_at") or now
        row["delivered_at"] = ""
        row["last_attempt_at"] = now
        row["attempt_count"] = str(int(row.get("attempt_count") or "0") + 1)
        lag_text = (
            f"signal-to-Issue={row.get('signal_to_issue_seconds')}s ({row.get('signal_to_issue_status')})"
            if row.get("signal_to_issue_seconds") else f"signal-to-Issue={row.get('signal_to_issue_status', 'UNKNOWN')}"
        )
        row["last_error"] = f"GitHub Issue exists; {lag_text}. ChatGPT/iPhone push receipt is not verified."
        confirmed += 1
    return rows, confirmed, late


def main() -> None:
    if not os.path.exists(path):
        raise SystemExit("Common notification outbox is missing; cannot acknowledge publication.")
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    base = f"https://api.github.com/repos/{repo}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    issues = []
    page = 1
    while True:
        batch = api_json(base + f"/issues?state=all&per_page=100&page={page}", headers)
        issues.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    rows = read_ledger(path, EVENT_FIELDS)
    now = datetime.now(timezone.utc).isoformat()
    rows, confirmed, late = reconcile_rows(rows, issues, now)
    upsert_ledger(path, EVENT_FIELDS, rows, "event_id")
    print(
        f"GitHub Issue publication confirmed: {confirmed}/{len(rows)}; "
        f"late signal-to-Issue: {late}; iPhone/ChatGPT push delivery remains unverified"
    )


if __name__ == "__main__":
    main()
