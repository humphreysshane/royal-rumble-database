#!/usr/bin/env python3
"""Apply the exhaustive 2026-09-28 nationality sweep.

The generated manifest supplies 279 rows. The explicit override block below is
the manually reviewed alias/legacy exception queue. No nationality is inferred
from appearance or birthplace; every override corresponds to a biography or
wrestling profile reviewed during this pass.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MANIFEST = ROOT / "research" / "nationality_sweep_20260928.csv"

MANUAL = {
    "1-2-3-kid": "American", "a-train": "American", "aldo-montoya": "American",
    "bill-goldberg": "American", "bob-holly": "American", "cesaro": "Swiss",
    "col-mustafa": "Iranian-American", "craig-degeorge": "American",
    "damien-demento": "American", "demolition-crush": "American",
    "doink": "American", "doink-1995": "American", "doug-gilbert": "American",
    "eight-ball": "American", "finlay": "Northern Irish", "hawk": "American",
    "headhunter-2": "American", "headshrinker-sione": "Tongan",
    "henry-godwinn": "American", "hunter-hearst-helmsley": "American",
    "husky-harris": "American", "jamal": "Samoan-American", "k-kwik": "American",
    "kama": "American", "kato": "Canadian", "kwang": "Puerto Rican",
    "latin-lover": "Mexican", "mankind": "American",
    "michael-mcgillicutty": "American", "mike-knox": "American",
    "phineas-godwinn": "American", "pierroth-jr": "Mexican", "primo": "Puerto Rican",
    "prince-albert": "American", "psicosis": "Mexican", "renee-dupree": "Canadian",
    "rocky-maivia": "American", "saba-simba": "American", "sapphire": "American",
    "scott-taylor": "American", "sin-cara": "Mexican", "sparky-plugg": "American",
    "steven-dunn": "American", "texas-tornado": "American",
    "the-great-tanaka": "American", "timothy-well": "American",
    "tom-brandi": "American", "yoshihiro-tajiri": "Japanese",
    # Manual semantic audit of multiple-badge SDH profiles. These pages can
    # use ancestry/birth-country flags alongside citizenship; nationality is
    # kept separate from ethnicity_heritage in this database.
    "kane": "American", "jinder-mahal": "Canadian", "tiger-ali-singh": "Canadian",
    "rusev": "Bulgarian", "the-great-khali": "Indian", "wade-barrett": "English",
}


def read(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write(path: Path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main():
    manifest_rows, _ = read(MANIFEST)
    manifest = {row["wrestler_id"]: row for row in manifest_rows}
    wrestler_rows, fields = read(DATA / "wrestlers.csv")
    targets = [row for row in wrestler_rows if not row.get("nationality")]
    if len(targets) != 326:
        raise RuntimeError(f"Baseline drift: expected 326 blank nationalities, found {len(targets)}")

    applied = 0
    manual_used = 0
    for row in targets:
        wrestler_id = row["wrestler_id"]
        research = manifest.get(wrestler_id)
        if not research:
            raise RuntimeError(f"Missing manifest row for {wrestler_id}")
        value = MANUAL.get(wrestler_id) or research.get("proposed_nationality", "")
        if not value:
            raise RuntimeError(f"Unresolved nationality for {wrestler_id}")
        row["nationality"] = value
        ids = [item for item in row.get("source_ids", "").split(";") if item]
        # S022 is the project's registered Wikipedia-biography collection.
        # S024 is the registered TheSmackDownHotel profile database.
        if research.get("wikipedia_url") or wrestler_id in MANUAL:
            if "S022" not in ids: ids.append("S022")
        if research.get("sdh_url"):
            if "S024" not in ids: ids.append("S024")
        row["source_ids"] = ";".join(ids)
        applied += 1
        manual_used += wrestler_id in MANUAL

    write(DATA / "wrestlers.csv", wrestler_rows, fields)
    print(f"Applied {applied} nationality values ({manual_used} manually reviewed alias exceptions).")


if __name__ == "__main__": main()
