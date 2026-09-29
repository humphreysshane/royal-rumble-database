#!/usr/bin/env python3
"""Apply the 2026-09-28 source-led profile research cohort.

The script is intentionally guarded and idempotent. It updates only the named
wrestler rows and appends only the URL-specific sources used for this cohort.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ACCESSED = "2026-09-28"


PROFILE_SOURCES = [
    ("Roddy Piper profile", "https://www.thesmackdownhotel.com/wrestlers/roddy-piper"),
    ("Dusty Rhodes profile", "https://www.thesmackdownhotel.com/wrestlers/dusty-rhodes"),
    ("Jimmy Snuka profile", "https://www.thesmackdownhotel.com/wrestlers/jimmy-snuka"),
    ("Earthquake / John Tenta profile", "https://www.thesmackdownhotel.com/wrestlers/earthquake-john-tenta"),
    ("Lanny Poffo / The Genius profile", "https://www.thesmackdownhotel.com/wrestlers/lanny-poffo-the-genius"),
    ("Tony Schiavone profile", "https://www.thesmackdownhotel.com/wrestlers/tony-schiavone"),
    ("The Undertaker profile", "https://www.thesmackdownhotel.com/wrestlers/the-undertaker"),
    ("The British Bulldog profile", "https://www.thesmackdownhotel.com/wrestlers/the-british-bulldog"),
    ("Bruce Prichard / Brother Love profile", "https://www.thesmackdownhotel.com/wrestlers/bruce-prichard-brother-love"),
]


UPDATES = {
    "roddy-piper": {
        "nationality": "Canadian",
        "deceased_date_status": "CONFIRMED",
        "hall_of_fame_year_status": "CONFIRMED",
    },
    "dusty-rhodes": {
        "nationality": "American",
        "deceased_date_status": "CONFIRMED",
        "hall_of_fame_year_status": "CONFIRMED",
    },
    "jimmy-snuka": {
        "nationality": "Fijian-American",
        "deceased_date_status": "CONFIRMED",
        "hall_of_fame_year_status": "CONFIRMED",
    },
    "earthquake": {
        "nationality": "Canadian",
        "deceased_date_status": "CONFIRMED",
        "hall_of_fame_year": "2025",
        "hall_of_fame_year_status": "CONFIRMED",
    },
    "the-genius": {
        "nationality": "Canadian-American",
        "deceased_date": "2023-02-02",
        "deceased_date_status": "CONFIRMED",
    },
    "tony-schiavone": {"nationality": "American"},
    "the-undertaker": {
        "nationality": "American",
        "hall_of_fame_year_status": "CONFIRMED",
    },
    "british-bulldog": {
        "nationality": "English",
        "deceased_date_status": "CONFIRMED",
        "hall_of_fame_year_status": "CONFIRMED",
    },
    "brother-love": {"nationality": "American"},
}


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    sources_path = DATA / "sources.csv"
    source_rows, source_fields = read_csv(sources_path)
    by_url = {row["url"]: row for row in source_rows if row.get("url")}
    max_source = max(int(row["source_id"][1:]) for row in source_rows if row.get("source_id", "").startswith("S"))
    source_ids = {}

    for label, url in PROFILE_SOURCES:
        if url in by_url:
            source_ids[url] = by_url[url]["source_id"]
            continue
        max_source += 1
        source_id = f"S{max_source:03d}"
        row = {field: "" for field in source_fields}
        row.update(
            {
                "source_id": source_id,
                "source_name": f"TheSmackDownHotel — {label}",
                "source_type": "wrestling_database",
                "url": url,
                "reliability_tier": "12",
                "tier_label": "Other reputable site",
                "accessed_date": ACCESSED,
                "notes": "Source-led profile pass; used with Wikipedia biography coverage (S022) and existing official/obituary sources where applicable.",
            }
        )
        source_rows.append(row)
        source_ids[url] = source_id

    wrestlers_path = DATA / "wrestlers.csv"
    wrestler_rows, wrestler_fields = read_csv(wrestlers_path)
    indexed = {row["wrestler_id"]: row for row in wrestler_rows}
    if set(UPDATES) - set(indexed):
        raise RuntimeError(f"Missing target wrestler ids: {sorted(set(UPDATES) - set(indexed))}")

    url_by_wrestler = dict(zip(UPDATES, (url for _, url in PROFILE_SOURCES), strict=True))
    changed = 0
    for wrestler_id, changes in UPDATES.items():
        row = indexed[wrestler_id]
        for field, value in changes.items():
            current = row.get(field, "")
            if current not in ("", value):
                raise RuntimeError(f"Refusing to overwrite {wrestler_id}.{field}: {current!r} -> {value!r}")
            if current != value:
                row[field] = value
                changed += 1
        ids = [item for item in row.get("source_ids", "").split(";") if item]
        for source_id in ("S022", source_ids[url_by_wrestler[wrestler_id]]):
            if source_id not in ids:
                ids.append(source_id)
        row["source_ids"] = ";".join(ids)

    write_csv(sources_path, source_rows, source_fields)
    write_csv(wrestlers_path, wrestler_rows, wrestler_fields)
    print(f"Applied {changed} field values across {len(UPDATES)} wrestler rows; source max is S{max_source:03d}.")


if __name__ == "__main__":
    main()
