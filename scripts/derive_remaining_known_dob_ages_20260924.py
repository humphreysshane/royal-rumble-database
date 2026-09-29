#!/usr/bin/env python3
"""Fill the 843 blank ages backed by an existing non-conflicting DOB.

This is a zero-new-research follow-on to Version 32. It deliberately excludes
missing DOBs and DOBs marked UNKNOWN, UNCERTAIN, CONFLICTING, or N/A. The
approved live baseline is guarded by an exact candidate-count check.
"""

from __future__ import annotations

import argparse
import calendar
import csv
from datetime import date
from pathlib import Path


EXCLUDED_DOB_STATUSES = {"UNKNOWN", "UNCERTAIN", "CONFLICTING", "N/A", ""}
EXPECTED_COUNT = 843


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def exact_age(dob: date, event_date: date) -> str:
    years = event_date.year - dob.year
    months = event_date.month - dob.month
    days = event_date.day - dob.day
    if days < 0:
        months -= 1
        previous_month = event_date.month - 1 or 12
        previous_year = event_date.year if event_date.month > 1 else event_date.year - 1
        days += calendar.monthrange(previous_year, previous_month)[1]
    if months < 0:
        years -= 1
        months += 12
    return f"{years} Years, {months} Months, {days} Days"


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()

    entrants_path = args.data_dir / "entrants.csv"
    entrants, entrant_fields = read_csv(entrants_path)
    wrestlers, _ = read_csv(args.data_dir / "wrestlers.csv")
    events, _ = read_csv(args.data_dir / "events.csv")
    wrestler_by_id = {row["wrestler_id"]: row for row in wrestlers}
    event_by_id = {row["event_id"]: row for row in events}

    candidates: list[dict[str, str]] = []
    for entrant in entrants:
        wrestler = wrestler_by_id.get(entrant["wrestler_id"], {})
        if (
            not entrant.get("age_at_event", "").strip()
            and wrestler.get("dob", "").strip()
            and wrestler.get("dob_status", "") not in EXCLUDED_DOB_STATUSES
        ):
            candidates.append(entrant)

    if len(candidates) != EXPECTED_COUNT:
        raise SystemExit(
            f"Refusing to edit: Version 32 cohort is {EXPECTED_COUNT} rows, "
            f"but this baseline contains {len(candidates)} candidates."
        )

    manifest: list[dict[str, str]] = []
    for entrant in candidates:
        wrestler = wrestler_by_id[entrant["wrestler_id"]]
        event = event_by_id[entrant["event_id"]]
        value = exact_age(date.fromisoformat(wrestler["dob"]), date.fromisoformat(event["event_date"]))
        previous_age_status = entrant.get("age_status", "")
        entrant["age_at_event"] = value
        entrant["age_status"] = "DERIVED"
        manifest.append({
            "event_id": entrant["event_id"],
            "wrestler_id": entrant["wrestler_id"],
            "previous_age_status": previous_age_status,
            "dob": wrestler["dob"],
            "dob_status": wrestler.get("dob_status", ""),
            "event_date": event["event_date"],
            "age_at_event": value,
            "age_status": "DERIVED",
            "source_ids_retained": entrant.get("source_ids", ""),
        })

    write_csv(entrants_path, entrants, entrant_fields)
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        write_csv(args.manifest, manifest, [
            "event_id", "wrestler_id", "previous_age_status", "dob", "dob_status",
            "event_date", "age_at_event", "age_status", "source_ids_retained",
        ])
    print(f"Updated {len(manifest)} blank age rows from existing non-conflicting DOBs.")


if __name__ == "__main__":
    main()
