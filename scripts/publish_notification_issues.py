#!/usr/bin/env python3
import csv, json, os, time, urllib.request, urllib.error

path="reports/current_notification_alerts.csv"
if not os.path.exists(path) or os.path.getsize(path)==0:
    print("No entry alerts.")
    raise SystemExit(0)

token=os.environ["GITHUB_TOKEN"]
repo=os.environ["GITHUB_REPOSITORY"]
base=f"https://api.github.com/repos/{repo}"
headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"}

def api(url, method="GET", body=None):
    last = None
    for attempt in range(1, 4):
        req=urllib.request.Request(url,headers=headers,method=method)
        if body is not None:
            req.data=json.dumps(body).encode()
            req.add_header("Content-Type","application/json")
        try:
            with urllib.request.urlopen(req,timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            last = e
            if e.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise
            time.sleep(attempt * 5)
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            if attempt == 3:
                raise
            time.sleep(attempt * 5)
    raise last

def existing_titles():
    titles=set()
    page=1
    while True:
        issues=api(base+f"/issues?state=all&per_page=100&page={page}")
        batch=[i.get("title","") for i in issues if "pull_request" not in i]
        titles.update(batch)
        if len(issues) < 100:
            return titles
        page += 1

def publish_once(title, body):
    # POST is not idempotent. If the HTTP response is lost after GitHub creates
    # the issue, blindly retrying POST can create duplicates. Re-check first.
    if title in existing_titles():
        print(f"Already published: {title}")
        return

    for attempt in range(1, 4):
        try:
            api(base+"/issues","POST",{"title":title,"body":body})
            print(f"Published: {title}")
            return
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise
        except (urllib.error.URLError, TimeoutError):
            pass

        # The POST may have succeeded even though the client did not receive
        # the response. Never issue another POST until existence is re-checked.
        if title in existing_titles():
            print(f"Published despite uncertain response: {title}")
            return
        time.sleep(attempt * 5)

    raise RuntimeError(f"Could not publish alert safely: {title}")

with open(path,newline="") as f:
    for r in csv.DictReader(f):
        pair=r["pair"]; direction=r["direction"]; signal=r["signal_candle"]
        title=f"FX ALERT {pair} {direction} {signal}"
        body=(
            "## FX entry alert\n\n"
            f"- Pair: {pair}\n"
            f"- Direction: {direction}\n"
            f"- Signal candle (completed H4): {signal}\n"
            f"- Next H4 entry candidate: {r['entry_candidate_h4']}\n"
            "- Rule: frozen H4 state-machine notification rule\n"
            "- Source: Dukascopy bid H4 data refreshed by GitHub Actions\n\n"
            "This issue is a durable notification event. Do not treat it as an execution order."
        )
        publish_once(title, body)
