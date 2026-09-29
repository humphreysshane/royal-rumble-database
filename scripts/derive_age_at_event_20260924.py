#!/usr/bin/env python3
"""Fill only the 318 approved age_at_event rows derivable from existing data.

Inputs are the already-sourced wrestler DOB and event date. No new factual
source is introduced. The script refuses to run if the approved cohort is no
longer exactly 318 rows, preventing accidental use against a drifted baseline.
"""

from __future__ import annotations

import argparse
import calendar
import csv
from datetime import date
from pathlib import Path


EXCLUDED_STATUSES = {"UNKNOWN", "CONFLICTING", "UNCERTAIN", "N/A"}
EXPECTED_COUNT = 318


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
            and entrant.get("age_status", "") not in EXCLUDED_STATUSES
            and wrestler.get("dob", "").strip()
        ):
            candidates.append(entrant)

    if len(candidates) != EXPECTED_COUNT:
        raise SystemExit(
            f"Refusing to edit: approved cohort is {EXPECTED_COUNT} rows, "
            f"but this baseline contains {len(candidates)} candidates."
        )

    manifest: list[dict[str, str]] = []
    for entrant in candidates:
        wrestler = wrestler_by_id[entrant["wrestler_id"]]
        event = event_by_id[entrant["event_id"]]
        dob = date.fromisoformat(wrestler["dob"])
        event_date = date.fromisoformat(event["event_date"])
        value = exact_age(dob, event_date)
        entrant["age_at_event"] = value
        entrant["age_status"] = "DERIVED"
        manifest.append({
            "event_id": entrant["event_id"],
            "wrestler_id": entrant["wrestler_id"],
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
            "event_id", "wrestler_id", "dob", "dob_status", "event_date",
            "age_at_event", "age_status", "source_ids_retained",
        ])
    print(f"Updated {len(manifest)} age_at_event rows; all statuses set to DERIVED.")


if __name__ == "__main__":
    main()
