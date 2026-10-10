#!/usr/bin/env python3
"""Audit FX monitor schedule health and pending notification outbox events.

GitHub Issue creation is treated as publication, not proof of phone delivery.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

REPO = os.environ.get("GITHUB_REPOSITORY", "local/test")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTBOX_PATH = Path(os.environ.get("FX_OUTBOX_PATH", "/tmp/fx_notification_outbox.csv"))
NOW = datetime.now(timezone.utc)
BASE = f"https://api.github.com/repos/{REPO}"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/json",
    "X-GitHub-Api-Version": "2022-11-28",
}
WORKFLOWS = {
    "H1 live monitor": ("fx-h1-live-monitor.yml", 120),
    "AUD/NZD H4 exit monitor": ("fx-audnzd-h4-exit.yml", 120),
    "generic H4 exit monitor": ("fx-position-exit-monitor.yml", 120),
}


def api(method: str, path: str, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(BASE + path, data=data, headers=HEADERS, method=method)
    try:
        with urlopen(req, timeout=30) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else {}
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {path} failed: HTTP {exc.code}: {body[:500]}") from exc


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp missing timezone: {value}")
    return parsed.astimezone(timezone.utc)


def age_minutes(value: str) -> float:
    return (NOW - parse_time(value)).total_seconds() / 60.0


def audit_schedules(findings: list[str], details: list[dict]) -> None:
    for label, (filename, max_age_minutes) in WORKFLOWS.items():
        path = "/actions/workflows/" + filename + "/runs?branch=main&event=schedule&per_page=10"
        payload = api("GET", path)
        runs = payload.get("workflow_runs", [])
        latest = max(runs, key=lambda run: run.get("run_started_at") or run.get("created_at") or "", default=None)
        if not latest:
            findings.append(f"{label}: no scheduled run is recorded")
            details.append({"workflow": label, "status": "NO_SCHEDULED_RUN"})
            continue
        started = latest.get("run_started_at") or latest.get("created_at") or ""
        try:
            age = age_minutes(started)
        except (ValueError, TypeError) as exc:
            findings.append(f"{label}: latest scheduled run has invalid timestamp ({exc})")
            details.append({"workflow": label, "status": "INVALID_TIMESTAMP", "run_url": latest.get("html_url")})
            continue
        conclusion = latest.get("conclusion") or latest.get("status") or "unknown"
        item = {
            "workflow": label, "run_id": latest.get("id"), "run_url": latest.get("html_url"),
            "started_at": started, "age_minutes": round(age, 1), "conclusion": conclusion,
        }
        details.append(item)
        if age > max_age_minutes:
            findings.append(f"{label}: last scheduled run is {age:.0f} minutes old (limit {max_age_minutes})")
        elif latest.get("status") != "completed" or latest.get("conclusion") != "success":
            findings.append(f"{label}: latest scheduled run is {conclusion} ({latest.get('html_url', 'URL unavailable')})")


def audit_outbox(findings: list[str], details: list[dict]) -> None:
    if not OUTBOX_PATH.exists() or OUTBOX_PATH.stat().st_size == 0:
        findings.append("Shared notification outbox is missing or empty")
        details.append({"outbox": "MISSING_OR_EMPTY"})
        return
    with OUTBOX_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    pending = []
    late = []
    invalid = []
    for row in rows:
        status = (row.get("delivery_status") or "").upper()
        timeframe = (row.get("timeframe") or "").upper()
        event_id = row.get("event_id", "")
        event_time = row.get("event_time", "")
        if status == "PENDING":
            try:
                age = age_minutes(event_time)
                threshold = 120 if timeframe == "H1" else 360 if timeframe == "H4" else None
                item = {"event_id": event_id, "pair": row.get("pair", ""), "event_type": row.get("event_type", ""),
                        "timeframe": timeframe, "age_minutes": round(age, 1), "threshold_minutes": threshold}
                pending.append(item)
                if threshold is None:
                    invalid.append(f"Pending event {event_id} has unknown timeframe {timeframe!r}")
                elif age > threshold:
                    findings.append(f"Pending {timeframe} event {event_id} ({row.get('pair', '')}) is {age:.0f} minutes old; limit {threshold}")
            except (ValueError, TypeError) as exc:
                invalid.append(f"Pending event {event_id} has invalid event_time: {exc}")
        if (row.get("signal_to_issue_status") or "").upper() == "LATE":
            late.append({"event_id": event_id, "pair": row.get("pair", ""), "timeframe": timeframe,
                         "lag_seconds": row.get("signal_to_issue_seconds", "")})
    findings.extend(invalid)
    details.append({"outbox_rows": len(rows), "pending_events": pending, "historical_late_publications": late,
                    "device_delivery_receipt_available": False})
    # Historical late publications are reported for observability but do not repeatedly
    # page the user once a durable Issue has already been created.


def manage_health_issue(findings: list[str], report: dict) -> None:
    title = "FX notification health degradation"
    issues = api("GET", "/issues?state=open&per_page=100")
    current = next((item for item in issues if item.get("title") == title and "pull_request" not in item), None)
    fingerprint = hashlib.sha256("\n".join(sorted(findings)).encode("utf-8")).hexdigest()[:12]
    report["fingerprint"] = fingerprint
    report["status"] = "DEGRADED" if findings else "HEALTHY"
    body = (
        "## FX notification health audit\n\n"
        f"- Status: **{report['status']}**\n"
        f"- Checked at UTC: {report['checked_at']}\n"
        f"- Fingerprint: `{fingerprint}`\n"
        "- This checks scheduled workflow freshness and pending notification publication. "
        "GitHub Issue creation is not proof of ChatGPT/iPhone push receipt.\n\n"
        + ("### Findings\n" + "\n".join(f"- {item}" for item in findings) if findings else "No current degradation detected.")
        + "\n\n### Details\n```json\n" + json.dumps(report["details"], ensure_ascii=False, indent=2) + "\n```"
    )
    if findings:
        if current is None:
            created = api("POST", "/issues", {"title": title, "body": body})
            report["health_issue"] = created.get("html_url")
            print(f"[DEGRADED] Created health issue {created.get('html_url')}")
        elif fingerprint not in (current.get("body") or ""):
            api("POST", f"/issues/{current['number']}/comments", {"body": "## Health audit changed\n\n" + body})
            api("PATCH", f"/issues/{current['number']}", {"body": body})
            report["health_issue"] = current.get("html_url")
            print(f"[DEGRADED] Updated health issue {current.get('html_url')}")
        else:
            report["health_issue"] = current.get("html_url")
            print(f"[DEGRADED] Existing health issue unchanged: {current.get('html_url')}")
    elif current is not None:
        api("POST", f"/issues/{current['number']}/comments", {"body": f"Recovered at {report['checked_at']} UTC. No current scheduled-run or pending-outbox degradation was detected.\n\nDevice push receipt is still not directly measurable."})
        api("PATCH", f"/issues/{current['number']}", {"state": "closed"})
        print(f"[HEALTHY] Closed recovered health issue {current.get('html_url')}")
    else:
        print("[HEALTHY] No scheduled-run or pending-outbox degradation detected.")


def main() -> None:
    findings: list[str] = []
    details: list[dict] = []
    report = {"checked_at": NOW.isoformat(), "details": details}
    audit_schedules(findings, details)
    audit_outbox(findings, details)
    manage_health_issue(findings, report)
    out = Path("reports/fx_notification_health.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if findings:
        print(f"Health audit findings: {len(findings)}")
    else:
        print("Health audit passed.")


if __name__ == "__main__":
    main()
