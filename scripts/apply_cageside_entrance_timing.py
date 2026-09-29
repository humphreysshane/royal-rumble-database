#!/usr/bin/env python3
"""Apply the reviewed Cageside Seats entrance-timing manifest.

The manifest is deliberately static: the research pages were collected once
on 2026-09-24, normalized, and preserved beside this script so a future site
edit cannot silently change the database. Safe to rerun after application.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MANIFEST = Path(__file__).with_name("cageside_entrance_timing_rows.csv")
TARGET = DATA / "entrances.csv"

with (DATA / "entrants.csv").open(encoding="utf-8-sig", newline="") as f:
    entrants = list(csv.DictReader(f))
assert len(entrants) == 1442, f"baseline drift: expected 1442 entrants, found {len(entrants)}"

with MANIFEST.open(encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    rows = list(reader)
assert len(rows) == 1343, f"manifest drift: expected 1343 timing rows, found {len(rows)}"
assert len({(r['event_id'], r['wrestler_id']) for r in rows}) == len(rows)
assert sum(bool(r['entrance_duration_seconds']) for r in rows) == 1122

with TARGET.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print("Applied 1,343 entrance-timing rows (1,122 with ring-entry duration).")
