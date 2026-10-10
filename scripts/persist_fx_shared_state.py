#!/usr/bin/env python3
"""Persist the shared lifecycle and notification outbox to fx-h1-research.

Uses GitHub's Git Data API and retries if the target branch advances concurrently.
This confirms repository persistence only, never device/ChatGPT push delivery.
"""
from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GITHUB_TOKEN"]
BRANCH = "fx-h1-research"
FILES = [
    "reports/fx_trade_lifecycle.csv",
    "reports/fx_notification_outbox.csv",
]
BASE = f"https://api.github.com/repos/{REPO}"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/json",
}


def api(method: str, path: str, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(BASE + path, data=data, headers=HEADERS, method=method)
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
        return json.loads(raw) if raw else {}


def branch_ref():
    encoded = urllib.parse.quote(BRANCH, safe="")
    return api("GET", f"/git/ref/heads/{encoded}")


def publish_once() -> bool:
    ref = branch_ref()
    parent = ref["object"]["sha"]
    commit = api("GET", f"/git/commits/{parent}")
    entries = []
    changed = False
    for path in FILES:
        local_path = Path(path)
        if not local_path.exists():
            raise RuntimeError(f"cannot persist missing lifecycle file: {path}")
        local = local_path.read_bytes()
        encoded_path = urllib.parse.quote(path, safe="/")
        encoded_branch = urllib.parse.quote(BRANCH, safe="")
        try:
            remote = api("GET", f"/contents/{encoded_path}?ref={encoded_branch}")
            remote_bytes = base64.b64decode("".join(remote.get("content", "").split()))
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
            remote_bytes = None
        if remote_bytes != local:
            changed = True
        entries.append({
            "path": path,
            "mode": "100644",
            "type": "blob",
            "content": local.decode("utf-8"),
        })

    if not changed:
        print("Shared FX lifecycle state unchanged; no commit required.")
        return True

    tree = api("POST", "/git/trees", {
        "base_tree": commit["tree"]["sha"],
        "tree": entries,
    })
    new_commit = api("POST", "/git/commits", {
        "message": "h4bot: persist common FX lifecycle state",
        "tree": tree["sha"],
        "parents": [parent],
    })
    api("PATCH", f"/git/refs/heads/{urllib.parse.quote(BRANCH, safe='')}", {
        "sha": new_commit["sha"],
        "force": False,
    })
    print(f"Persisted shared FX lifecycle state to {BRANCH}: {new_commit['sha']}")
    return True


def main() -> None:
    for attempt in range(1, 4):
        try:
            publish_once()
            return
        except urllib.error.HTTPError as exc:
            # A concurrent branch update can invalidate the parent SHA. Re-read and retry.
            if exc.code not in (409, 422) or attempt == 3:
                raise
            print(f"Shared state branch advanced concurrently; retry {attempt}/3.")
            time.sleep(attempt * 2)
    raise RuntimeError("Unable to persist shared FX lifecycle state after retries")


if __name__ == "__main__":
    main()
