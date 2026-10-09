#!/usr/bin/env python3
"""Audit and repair only one-quote-tick OHLC envelope violations.

Historical files are not silently normalized: every correction is written to an
append-only audit CSV. Violations larger than one tick fail closed for review.
"""
from __future__ import annotations

import csv
import os
import tempfile
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data" / "market"
AUDIT = ROOT / "reports" / "market_data_ohlc_repairs.csv"
AUDIT_FIELDS = [
    "file", "timestamp", "original_open", "original_high", "original_low",
    "original_close", "repaired_high", "repaired_low", "max_violation",
    "tick_size", "repair_reason", "repaired_at_utc",
]


def decimal_places(raw: str) -> int:
    value = raw.strip().lower()
    if "e" in value:
        value = format(Decimal(value), "f")
    return len(value.split(".", 1)[1].rstrip("0")) if "." in value else 0


def analyze_row(row: dict[str, str], pair: str | None = None):
    try:
        values = {key: Decimal(row[key]) for key in ("open", "high", "low", "close")}
    except (KeyError, InvalidOperation) as exc:
        raise ValueError(f"malformed OHLC row: {row}") from exc
    if any(not v.is_finite() or v <= 0 for v in values.values()):
        raise ValueError(f"non-positive/non-finite OHLC row: {row}")

    o, h, l, c = (values[k] for k in ("open", "high", "low", "close"))
    required_high = max(o, c, l)
    required_low = min(o, c, h)
    high_violation = max(Decimal("0"), required_high - h)
    low_violation = max(Decimal("0"), l - required_low)
    violation = max(high_violation, low_violation)
    decimals = max(decimal_places(row[k]) for k in ("open", "high", "low", "close"))
    # Use a conservative minimum FX quote precision so trailing-zero formatting
    # cannot make a one-pip quote look like a fractional-tick anomaly.
    minimum_decimals = 3 if pair and "jpy" in pair.lower() else 5
    decimals = max(decimals, minimum_decimals)
    tick = Decimal(1).scaleb(-decimals)

    if violation == 0:
        return None
    if violation > tick:
        raise ValueError(
            f"OHLC violation exceeds one displayed quote tick ({violation} > {tick}): {row}"
        )

    repaired_high = max(o, h, l, c)
    repaired_low = min(o, h, l, c)
    return {
        "repaired_high": format(repaired_high, "f"),
        "repaired_low": format(repaired_low, "f"),
        "max_violation": format(violation, "f"),
        "tick_size": format(tick, "f"),
    }


def atomic_write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def repair_file(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        if not fields or not {"timestamp", "open", "high", "low", "close"}.issubset(fields):
            return []
        rows = list(reader)

    changes = []
    for row in rows:
        result = analyze_row(row)
        if result is None:
            continue
        audit = {
            "file": str(path.relative_to(ROOT)),
            "timestamp": row["timestamp"],
            "original_open": row["open"],
            "original_high": row["high"],
            "original_low": row["low"],
            "original_close": row["close"],
            "repaired_high": result["repaired_high"],
            "repaired_low": result["repaired_low"],
            "max_violation": result["max_violation"],
            "tick_size": result["tick_size"],
            "repair_reason": "OHLC envelope corrected within one displayed quote tick",
            "repaired_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        row["high"] = result["repaired_high"]
        row["low"] = result["repaired_low"]
        changes.append(audit)

    if changes:
        atomic_write_csv(path, fields, rows)
    return changes


def main():
    files = sorted(DATA_ROOT.glob("*/*.csv"))
    if not files:
        raise SystemExit(f"No market data CSV files found under {DATA_ROOT}")

    # First validate every row before modifying any file. A larger discrepancy
    # stops the run and leaves all source files untouched for manual review.
    all_rows = {}
    for path in files:
        with path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            fields = reader.fieldnames
            if not fields or not {"timestamp", "open", "high", "low", "close"}.issubset(fields):
                continue
            all_rows[path] = list(reader)
            for row in all_rows[path]:
                analyze_row(row, path.stem)  # Raises on any violation larger than one quote tick.

    changes = []
    for path, rows in all_rows.items():
        changed = []
        for row in rows:
            result = analyze_row(row, path.stem)
            if result is not None:
                changed.append({
                    "file": str(path.relative_to(ROOT)),
                    "timestamp": row["timestamp"],
                    "original_open": row["open"],
                    "original_high": row["high"],
                    "original_low": row["low"],
                    "original_close": row["close"],
                    "repaired_high": result["repaired_high"],
                    "repaired_low": result["repaired_low"],
                    "max_violation": result["max_violation"],
                    "tick_size": result["tick_size"],
                    "repair_reason": "OHLC envelope corrected within one displayed quote tick",
                    "repaired_at_utc": datetime.now(timezone.utc).isoformat(),
                })
                row["high"] = result["repaired_high"]
                row["low"] = result["repaired_low"]
        if changed:
            atomic_write_csv(path, list(rows[0].keys()) if rows else ["timestamp", "open", "high", "low", "close"], rows)
            changes.extend(changed)

    if changes:
        existing = []
        if AUDIT.exists():
            with AUDIT.open(newline="", encoding="utf-8") as stream:
                existing = list(csv.DictReader(stream))
        seen = {(r.get("file"), r.get("timestamp"), r.get("original_open"),
                 r.get("original_high"), r.get("original_low"), r.get("original_close")) for r in existing}
        for row in changes:
            key = (row["file"], row["timestamp"], row["original_open"], row["original_high"],
                   row["original_low"], row["original_close"])
            if key not in seen:
                existing.append(row)
                seen.add(key)
        atomic_write_csv(AUDIT, AUDIT_FIELDS, existing)
    print(f"[OHLC AUDIT] files_scanned={len(all_rows)} repaired_rows={len(changes)}")
    if changes:
        print(f"[OHLC AUDIT] audit_file={AUDIT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
