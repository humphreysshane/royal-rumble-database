#!/usr/bin/env python3
"""Reapply the reviewed manifest after dual-badge and alias audit."""

from __future__ import annotations

import csv
from pathlib import Path

from apply_nationality_sweep_20260928 import MANUAL


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MANIFEST = ROOT / "research" / "nationality_sweep_20260928.csv"


def load(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def main():
    manifest_rows, _ = load(MANIFEST)
    manifest = {row["wrestler_id"]: row for row in manifest_rows}
    rows, fields = load(DATA / "wrestlers.csv")
    changed = 0
    for wrestler_id, research in manifest.items():
        value = MANUAL.get(wrestler_id) or research.get("proposed_nationality", "")
        if not value:
            raise RuntimeError(f"Unresolved audited nationality: {wrestler_id}")
        row = next((item for item in rows if item["wrestler_id"] == wrestler_id), None)
        if row is None:
            raise RuntimeError(f"Missing wrestler: {wrestler_id}")
        if row["nationality"] != value:
            row["nationality"] = value
            changed += 1
    with (DATA / "wrestlers.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    print(f"Reapplied audited sweep; {changed} nationality values changed after semantic review.")


if __name__ == "__main__": main()
