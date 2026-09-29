#!/usr/bin/env python3
"""Close every source-supported residual P1 physical-profile gap.

This script is deliberately baseline-guarded and idempotent. Unsupported values
remain blank and are recorded in a single open research flag.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ENTRANTS = DATA / "entrants.csv"
SOURCES = DATA / "sources.csv"
FLAGS = DATA / "flags.csv"

EXPECTED_BLANKS = {
    "billed_height_m_at_event": 5,
    "billed_weight_kg_at_event": 18,
    "billed_from_at_event": 15,
    "alignment": 0,
}

# (event_id, wrestler_id): field updates and the source supporting them.
UPDATES = {
    ("RR2022M", "johnny-knoxville"): ({
        "billed_height_m_at_event": "1.85",
        "billed_weight_kg_at_event": "82",
        "billed_from_at_event": "Knoxville, Tennessee",
    }, "S1503"),
    ("RR2022M", "bad-bunny"): ({
        "billed_height_m_at_event": "1.80",
        "billed_weight_kg_at_event": "75",
        "billed_from_at_event": "Vega Baja, Puerto Rico",
    }, "S1508"),
    ("RR2025M", "ishowspeed"): ({"billed_weight_kg_at_event": "66"}, "S1574"),
    ("RR2026M", "el-grande-americano-ii"): ({
        "billed_height_m_at_event": "1.91",
        "billed_weight_kg_at_event": "100",
        "billed_from_at_event": "Gulf of America",
    }, "S890"),
    ("RR2026M", "el-grande-americano-i"): ({
        "billed_height_m_at_event": "1.73",
        "billed_weight_kg_at_event": "92",
        "billed_from_at_event": "Gulf of Mexico",
    }, "S891"),
    ("RR2026M", "la-parka-iii"): ({
        "billed_height_m_at_event": "1.91",
        "billed_weight_kg_at_event": "90",
        "billed_from_at_event": "Mexico City, Mexico",
    }, "S1698"),
    ("RR1995M", "jimmy-del-ray"): ({"billed_from_at_event": "Delray Beach, Florida"}, "S603"),
    ("RR1994M", "bastion-booger"): ({"billed_from_at_event": "The Environment"}, "S1699"),
}

for year in range(2020, 2025):
    UPDATES[(f"RR{year}M", "ricochet")] = (
        {"billed_from_at_event": "Paducah, Kentucky"}, "S899"
    )

NEW_SOURCES = [
    {
        "source_id": "S1698",
        "source_name": "WWE.com Superstar profile: La Parka",
        "source_type": "official_website",
        "url": "https://www.wwe.com/superstars/la-parka-aaa",
        "reliability_tier": "1",
        "tier_label": "Official primary source",
        "accessed_date": "2026-09-24",
        "notes": "Official profile lists 6 ft 3 in, 198 lb and Mexico City, Mexico for the third La Parka incarnation that appeared in RR2026M.",
    },
    {
        "source_id": "S1699",
        "source_name": "WWE.com — WWE's 25 most absurd Superstars",
        "source_type": "official_website",
        "url": "https://www.wwe.com/classics/classic-lists/wwes-most-absurd-superstars",
        "reliability_tier": "1",
        "tier_label": "Official primary source",
        "accessed_date": "2026-09-24",
        "notes": "Official retrospective explicitly states Bastion Booger was billed from The Environment.",
    },
]

RESIDUAL_FLAG = {
    "flag_id": "F559",
    "event_id": "",
    "table": "entrants",
    "record_id": "paul-roma;timothy-well;kevin-thorn;zelina-vega;roxanne-perez;kelani-jordan",
    "field": "billed_from_at_event;billed_weight_kg_at_event",
    "issue_type": "missing_source",
    "description": (
        "Residual P1 physical-profile closeout exhausted registered and targeted profile sources. "
        "No explicit event-era billed-from source was established for Paul Roma (RR1991M), Timothy Well "
        "(RR1995M), or Kevin Thorn (RR2007M). No published billed weight was established for Zelina Vega "
        "(RR2019W/RR2020W/RR2022W-RR2026W), Roxanne Perez (RR2023W-RR2026W), or Kelani Jordan "
        "(RR2026W); their strongest registered profiles omit weight. Fields remain blank rather than inferred."
    ),
    "source_ids_involved": "S540;S607;S746;S943;S1075;S968;S1054;S989;S1073",
    "status": "open",
    "date_logged": "2026-09-24",
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


def append_source_id(existing: str, source_id: str) -> str:
    ids = [value for value in existing.split(";") if value]
    if source_id not in ids:
        ids.append(source_id)
    return ";".join(ids)


def main():
    entrant_fields, entrants = read_rows(ENTRANTS)
    current_blanks = {
        field: sum(not row[field].strip() for row in entrants)
        for field in EXPECTED_BLANKS
    }
    already_applied = all(
        all(row.get(field) == value for field, value in values.items())
        for key, (values, _) in UPDATES.items()
        for row in entrants
        if (row["event_id"], row["wrestler_id"]) == key
    )
    if current_blanks != EXPECTED_BLANKS and not already_applied:
        raise SystemExit(f"Baseline gap guard failed: {current_blanks} != {EXPECTED_BLANKS}")

    index = {(row["event_id"], row["wrestler_id"]): row for row in entrants}
    changed_cells = 0
    for key, (values, source_id) in UPDATES.items():
        if key not in index:
            raise SystemExit(f"Missing target row: {key}")
        row = index[key]
        for field, value in values.items():
            if row[field] not in ("", value):
                raise SystemExit(f"Refusing to overwrite {key} {field}={row[field]!r}")
            if row[field] != value:
                row[field] = value
                changed_cells += 1
        row["physical_status"] = "PROBABLE"
        row["source_ids"] = append_source_id(row["source_ids"], source_id)
    write_rows(ENTRANTS, entrant_fields, entrants)

    source_fields, sources = read_rows(SOURCES)
    existing_sources = {row["source_id"] for row in sources}
    for source in NEW_SOURCES:
        if source["source_id"] not in existing_sources:
            sources.append(source)
    write_rows(SOURCES, source_fields, sources)

    flag_fields, flags = read_rows(FLAGS)
    existing_flags = {row["flag_id"] for row in flags}
    if RESIDUAL_FLAG["flag_id"] not in existing_flags:
        flags.append(RESIDUAL_FLAG)
    write_rows(FLAGS, flag_fields, flags)

    print(f"Updated {changed_cells} previously blank entrant cells across {len(UPDATES)} rows.")
    print("Residual gaps are preserved in open flag F559.")


if __name__ == "__main__":
    main()
