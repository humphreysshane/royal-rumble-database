#!/usr/bin/env python3
"""Build a row/field manifest comparing a V39 baseline with this V40 tree."""

import argparse
import csv
from pathlib import Path


KEYS = {
    "entrants.csv": ("event_id", "wrestler_id"),
    "entrances.csv": ("event_id", "wrestler_id"),
    "wrestlers.csv": ("wrestler_id",),
    "families.csv": ("family_id",),
    "sources.csv": ("source_id",),
    "flags.csv": ("flag_id",),
}


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    current = Path(__file__).resolve().parents[1]
    output = []
    for filename, key_fields in KEYS.items():
        old_rows = read(args.baseline / "data" / filename)
        new_rows = read(current / "data" / filename)
        old = {tuple(r[k] for k in key_fields): r for r in old_rows}
        new = {tuple(r[k] for k in key_fields): r for r in new_rows}
        for key in sorted(new):
            row_key = ";".join(key)
            if key not in old:
                output.append({"table": filename, "row_key": row_key, "change_type": "ADDED",
                               "changed_fields": ";".join(new[key].keys()), "reason": "New sourced V40 row."})
                continue
            fields = [field for field in new[key] if old[key].get(field, "") != new[key].get(field, "")]
            if fields:
                reasons = []
                if "promotion_at_event" in fields:
                    reasons.append("event-era WWE/WWF brand or promotion affiliation populated")
                if "wrestled_masked" in fields:
                    reasons.append("per-appearance masked status completed")
                if "billed_weight_kg_at_event" in fields:
                    reasons.append("residual sourced billed weight populated")
                if "deceased_date" in fields:
                    reasons.append("exact-identity deceased date populated")
                if "hall_of_fame_year" in fields:
                    reasons.append("exact performer/persona Hall of Fame year populated")
                if set(fields) <= {"deceased_date_status", "hall_of_fame_year_status"}:
                    reasons.append("new schema status columns initialized blank")
                output.append({"table": filename, "row_key": row_key, "change_type": "CHANGED",
                               "changed_fields": ";".join(fields), "reason": "; ".join(reasons) or "Sourcing/status update."})
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["table", "row_key", "change_type", "changed_fields", "reason"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    print(f"Wrote {len(output)} manifest rows to {args.output}")


if __name__ == "__main__":
    main()
