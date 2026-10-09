#!/usr/bin/env python3
"""Acknowledge outbox events only after their durable GitHub Issue exists.

H1 entry alerts use the deterministic event ID title. H4 exit alerts retain the
legacy title format so integration does not create duplicate issues for old signals.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from fx_lifecycle_contract import EVENT_FIELDS, read_ledger, upsert_ledger

path = "reports/fx_notification_outbox.csv"
if not os.path.exists(path):
    raise SystemExit("Common notification outbox is missing; cannot acknowledge delivery.")
token = os.environ["GITHUB_TOKEN"]
repo = os.environ["GITHUB_REPOSITORY"]
base = f"https://api.github.com/repos/{repo}"
headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
titles = set()
page = 1
while True:
    req = Request(base + f"/issues?state=all&per_page=100&page={page}", headers=headers)
    with urlopen(req, timeout=30) as response:
        batch = json.load(response)
    titles.update(issue.get("title", "") for issue in batch if "pull_request" not in issue)
    if len(batch) < 100:
        break
    page += 1

rows = read_ledger(path, EVENT_FIELDS)
now = datetime.now(timezone.utc).isoformat()
acknowledged = 0
for row in rows:
    if row.get("delivery_status") == "DELIVERED":
        continue
    event_type = row.get("event_type", "").upper()
    if event_type in {"ENTRY_CONFIRMED", "ENTRY_REJECTED"}:
        title = f"FX H1 ALERT {row['event_id']}"
    elif event_type == "EXIT_SIGNAL" and row.get("timeframe", "").upper() == "H4":
        # Match the existing H4 publisher's title to avoid duplicate issues during migration.
        title = (
            f"FX EXIT {row.get('pair', '').lower()} "
            f"{row.get('direction', '').lower()} {row.get('event_time', '')}"
        )
    else:
        # Unknown event/channel mapping must remain pending rather than falsely delivered.
        row["delivery_status"] = "PENDING"
        row["last_error"] = f"No issue-title mapping for event type/timeframe: {event_type}/{row.get('timeframe', '')}"
        continue

    if title in titles:
        row["delivery_status"] = "DELIVERED"
        row["delivered_at"] = now
        row["last_attempt_at"] = now
        row["attempt_count"] = str(int(row.get("attempt_count") or "0") + 1)
        row["last_error"] = ""
        acknowledged += 1
    else:
        row["delivery_status"] = "PENDING"
        row["last_attempt_at"] = now
        row["attempt_count"] = str(int(row.get("attempt_count") or "0") + 1)
        row["last_error"] = f"Durable Issue not found yet for title: {title}; will retry on next scheduled run."
upsert_ledger(path, EVENT_FIELDS, rows, "event_id")
print(f"Outbox delivery acknowledgements: {acknowledged}/{len(rows)} events confirmed in GitHub Issues")
