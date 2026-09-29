#!/usr/bin/env python3
"""Apply the sourced V40 consolidated research tranche.

This script is intentionally conservative: a scraped event-table row is used only
when its entrant name resolves to exactly one entrant in that year's two Royal
Rumble rosters. Ambiguous or malformed rows remain blank for later research.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DEFAULT_INPUT = ROOT / "scripts" / "research_inputs" / "promotion_brand_rows_2003_2026.json"


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode()
    value = re.sub(r"\[[^]]*]", "", value)
    value = re.sub(r"\s*\*+\s*$", "", value)
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip().lower()
    for prefix in ("dirty ", "the original "):
        if value.startswith(prefix):
            value = value[len(prefix):]
    return value


ALIASES = {
    "christopher nowinski": "chris nowinski",
    "tajiri": "yoshihiro tajiri",
    "goldberg": "bill goldberg",
    "sylvan": "sylvan grenier",
    "rene dupree": "rene dupree",
    "montel vontavious porter": "mvp",
    "seth freakin rollins": "seth rollins",
    "andrade cien almas": "andrade",
    "shotzi blackheart": "shotzi",
    "hurricane helms": "the hurricane",
    "gene snitsky": "snitsky",
    "matt riddle": "riddle",
    "ted dibiase jr": "ted dibiase",
    "b 2": "bull buchanan",
    "kane1": "kane",
    "queen zelina": "zelina vega",
    "zelina": "zelina vega",
    "mighty molly": "molly holly",
    "nattie": "natalya",
    "io shirai": "iyo sky",
    "michin": "mia yim",
    "ishowspeed": "ishowspeed",
}

BRAND_OVERRIDES = {
    (2010, "jtg"): "SmackDown",
    (2010, "the great khali"): "SmackDown",
    (2010, "beth phoenix"): "Raw",
    (2010, "kane"): "SmackDown",
    (2010, "mvp"): "SmackDown",
    (2010, "carlito"): "Raw",
    (2010, "the miz"): "Raw",
    (2010, "yoshi tatsu"): "ECW",
    (2010, "mark henry"): "Raw",
    (2010, "chris masters"): "SmackDown",
    (2010, "kofi kingston"): "Raw",
}


def canonical(value: str) -> str:
    n = norm(value)
    return ALIASES.get(n, n)


def add_source(source_rows, name, url, notes):
    for row in source_rows:
        if row.get("url") == url:
            return row["source_id"]
    highest = max((int(r["source_id"][1:]) for r in source_rows if re.fullmatch(r"S\d+", r.get("source_id", ""))), default=0)
    source_id = f"S{highest + 1:03d}"
    source_rows.append({
        "source_id": source_id,
        "source_name": name,
        "source_type": "reference",
        "url": url,
        "reliability_tier": "10",
        "tier_label": "Wikipedia/reference",
        "accessed_date": "2026-09-25",
        "notes": notes,
    })
    return source_id


def append_source_ids(existing: str, source_id: str) -> str:
    values = [v.strip() for v in (existing or "").split(";") if v.strip()]
    if source_id not in values:
        values.append(source_id)
    return ";".join(values)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--brand-json", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()

    entrant_fields, entrants = read_csv(DATA / "entrants.csv")
    wrestler_fields, wrestlers = read_csv(DATA / "wrestlers.csv")
    source_fields, sources = read_csv(DATA / "sources.csv")

    for field in ("deceased_date_status", "hall_of_fame_year_status"):
        if field not in wrestler_fields:
            insert_after = "deceased_date" if field == "deceased_date_status" else "hall_of_fame_year"
            wrestler_fields.insert(wrestler_fields.index(insert_after) + 1, field)
            for row in wrestlers:
                row[field] = ""

    by_wrestler = {r["wrestler_id"]: r for r in wrestlers}
    roster_names: dict[tuple[int, str], dict[str, set[int]]] = {}
    for index, row in enumerate(entrants):
        year_match = re.search(r"(\d{4})", row["event_id"])
        if not year_match:
            continue
        year = int(year_match.group(1))
        division = "Women's" if row["event_id"].endswith("W") else "Men's"
        names = {canonical(row.get("ring_name_at_time", "")), canonical(row.get("name_displayed_at_event", ""))}
        wrestler = by_wrestler.get(row["wrestler_id"], {})
        names.add(canonical(wrestler.get("ring_name", "")))
        names.update(canonical(v) for v in wrestler.get("aliases_ring_names", "").split(";") if v.strip())
        for name in names - {""}:
            roster_names.setdefault((year, division), {}).setdefault(name, set()).add(index)

    event_source_ids = {}
    years = sorted({int(re.search(r"\d{4}", e["event_id"]).group()) for e in entrants if re.search(r"\d{4}", e["event_id"])})
    for year in years:
        url = f"https://en.wikipedia.org/wiki/{year}_Royal_Rumble"
        event_source_ids[year] = add_source(
            sources,
            f"{year} Royal Rumble — Wikipedia",
            url,
            "Event article and structured Royal Rumble entrant table; used for brand/promotion affiliation.",
        )

    updated = 0
    # Before the March 2002 brand split, Royal Rumble entrants were WWF roster members.
    for row in entrants:
        year_match = re.search(r"(\d{4})", row["event_id"])
        if not year_match or row.get("promotion_at_event"):
            continue
        year = int(year_match.group(1))
        if year <= 2002 or 2012 <= year <= 2016:
            row["promotion_at_event"] = "WWF" if year <= 2002 else "WWE"
            row["promotion_at_event_status"] = "PROBABLE"
            row["source_ids"] = append_source_ids(row.get("source_ids", ""), event_source_ids[year])
            updated += 1

    raw_rows = json.loads(args.brand_json.read_text(encoding="utf-8-sig"))
    skipped = []
    valid_brands = {"Raw", "SmackDown", "ECW", "NXT", "NXT UK", "205 Live", "TNA", "AAA", "Unaffiliated"}
    for item in raw_rows:
        year = int(item["year"])
        name = canonical(item["entrant"].replace("�", "e"))
        candidates = set()
        for division in ("Men's", "Women's"):
            candidates |= roster_names.get((year, division), {}).get(name, set())
        override = BRAND_OVERRIDES.get((year, name))
        if len(candidates) != 1 and not (candidates and name in {"nia jax", "mighty molly", "el grande americano"}):
            skipped.append((year, item["entrant"], "ambiguous_or_unmatched"))
            continue
        brand = (override or item["brand"]).replace("SmackDown!", "SmackDown").strip()
        brand = re.sub(r"\s*\(HOF\)$", "", brand)
        if brand in {"HOF", "Legend", "Unbranded", "Celebrity"}:
            brand = "Unaffiliated"
        elif brand == "Impact":
            brand = "TNA"
        elif brand == "NXT/HOF":
            brand = "NXT"
        if brand not in valid_brands:
            skipped.append((year, item["entrant"], f"invalid_brand:{brand}"))
            continue
        for index in candidates:
            row = entrants[index]
            if not row.get("promotion_at_event"):
                row["promotion_at_event"] = brand
                row["promotion_at_event_status"] = "PROBABLE"
                row["source_ids"] = append_source_ids(row.get("source_ids", ""), event_source_ids[year])
                updated += 1

    manual_event_brands = {
        ("RR2004M", "renee-dupree"): "Raw",
        ("RR2004M", "test"): "Raw",
        ("RR2005M", "renee-dupree"): "SmackDown",
        ("RR2025M", "akira-tozawa"): "Raw",
    }
    for row in entrants:
        brand = manual_event_brands.get((row["event_id"], row["wrestler_id"]))
        if brand and not row.get("promotion_at_event"):
            year = int(re.search(r"\d{4}", row["event_id"]).group())
            row["promotion_at_event"] = brand
            row["promotion_at_event_status"] = "PROBABLE"
            row["source_ids"] = append_source_ids(row.get("source_ids", ""), event_source_ids[year])
            updated += 1

    write_csv(DATA / "entrants.csv", entrant_fields, entrants)
    write_csv(DATA / "wrestlers.csv", wrestler_fields, wrestlers)
    write_csv(DATA / "sources.csv", source_fields, sources)
    print(f"promotion rows updated: {updated}")
    print(f"scraped rows skipped: {len(skipped)}")
    for item in skipped[:40]:
        print("  SKIP", item)


if __name__ == "__main__":
    main()
