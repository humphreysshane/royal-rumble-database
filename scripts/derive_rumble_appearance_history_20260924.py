#!/usr/bin/env python3
"""Derive the complete entrant appearance-history layer from existing rows."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ENTRANTS = DATA / "entrants.csv"
EVENTS = DATA / "events.csv"
WRESTLERS = DATA / "wrestlers.csv"
MANIFEST = ROOT / "APPEARANCE_HISTORY_CHANGED_ROWS.csv"

FIELDS = [
    "prior_rumble_appearances_count",
    "rumble_appearance_no",
    "is_first_rumble_appearance",
    "previous_rumble_year",
    "previous_rumble_result",
    "previous_rumble_elimination_no",
    "is_rumble_debut",
]

EXPECTED_BLANKS = {
    "prior_rumble_appearances_count": 1302,
    "rumble_appearance_no": 1362,
    "is_first_rumble_appearance": 1276,
    "previous_rumble_year": 1414,
    "previous_rumble_result": 1394,
    "previous_rumble_elimination_no": 1414,
    "is_rumble_debut": 1162,
}


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_rows(path: Path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def prior_result(row):
    if row["is_winner"] == "TRUE":
        return "Won"
    if row["elim_number_status"] == "N/A" and not row["elim_number"]:
        return "Did not enter"
    if row["is_runner_up"] == "TRUE":
        return f"Runner-up (elim #{row['elim_number']})"
    if row["elim_number"]:
        return f"Eliminated (elim #{row['elim_number']})"
    return "Eliminated (order unknown)"


def main():
    entrant_fields, entrants = read_rows(ENTRANTS)
    _, event_rows = read_rows(EVENTS)
    events = {row["event_id"]: row for row in event_rows}
    _, wrestler_rows = read_rows(WRESTLERS)
    wrestlers = {row["wrestler_id"]: row for row in wrestler_rows}

    blanks = {field: sum(not row[field].strip() for row in entrants) for field in FIELDS}
    already_applied = all(value == 0 for value in blanks.values())
    if blanks != EXPECTED_BLANKS and not already_applied:
        raise SystemExit(f"Baseline guard failed: {blanks} != {EXPECTED_BLANKS}")
    if already_applied:
        print("Appearance-history tier is already complete; no changes made.")
        return

    # Women's match precedes Men's on dual-Rumble cards. This matters for the
    # one same-night crossover, Nia Jax at Royal Rumble 2019.
    def sort_key(row):
        event = events[row["event_id"]]
        division_order = 0 if event["match_type"] == "Women's" else 1
        return (event["event_date"], division_order, int(row["entry_number"] or 999))

    ordered = sorted(entrants, key=sort_key)
    history = defaultdict(list)
    changes = []
    for row in ordered:
        master = wrestlers[row["wrestler_id"]]
        # The historical source files contain a few alias IDs for the same
        # human (Goldberg/Bill Goldberg, Boss Man spelling variants, Foley's
        # three personas). Exact nonblank real_name is the stable person key;
        # wrestler_id remains the fallback where identity is not established.
        identity_key = (master["real_name"].strip().casefold() or row["wrestler_id"])
        prior = history[identity_key]
        prior_count = len(prior)
        previous = prior[-1] if prior else None
        current_event = events[row["event_id"]]
        expected = {
            "prior_rumble_appearances_count": str(prior_count),
            "rumble_appearance_no": str(prior_count + 1),
            "is_first_rumble_appearance": "TRUE" if prior_count == 0 else "FALSE",
            "previous_rumble_year": current_event["event_date"][:4] if False else (
                events[previous["event_id"]]["event_date"][:4] if previous else "N/A"
            ),
            "previous_rumble_result": prior_result(previous) if previous else "N/A",
            "previous_rumble_elimination_no": (
                previous["elim_number"] if previous and previous["elim_number"] else "N/A"
            ),
            "is_rumble_debut": "TRUE" if prior_count == 0 else "FALSE",
        }

        changed_fields = []
        for field in (
            "prior_rumble_appearances_count",
            "rumble_appearance_no",
            "is_first_rumble_appearance",
            "previous_rumble_year",
            "is_rumble_debut",
        ):
            if row[field] != expected[field]:
                row[field] = expected[field]
                changed_fields.append(field)

        for field in ("previous_rumble_result", "previous_rumble_elimination_no"):
            value = expected[field]
            if not row[field]:
                row[field] = value
                changed_fields.append(field)
        if changed_fields:
            changes.append({
                "event_id": row["event_id"],
                "wrestler_id": row["wrestler_id"],
                "changed_fields": ";".join(changed_fields),
                **{field: row[field] for field in FIELDS},
            })
        prior.append(row)

    write_rows(ENTRANTS, entrant_fields, entrants)
    manifest_fields = ["event_id", "wrestler_id", "changed_fields", *FIELDS]
    write_rows(MANIFEST, manifest_fields, changes)
    print(f"Updated {len(changes)} entrant rows.")
    print(f"Filled {sum(len(row['changed_fields'].split(';')) for row in changes)} cells.")
    print(f"Manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
