#!/usr/bin/env python3
"""Close the entrant championship profile layer from verified title histories."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ENTRANTS = DATA / "entrants.csv"
SOURCES = DATA / "sources.csv"
MANIFEST = ROOT / "CHAMPIONSHIP_PROFILE_CHANGED_ROWS.csv"

EXPECTED_ENTRANTS_SHA256 = "db6f8bd63550bdd3c774745f1111ac5c21dc175917c057749da3bb03bff45103"
EXPECTED_SOURCES_SHA256 = "1c8c2cfe0104acd310a6213043b9448c0270fca64611d4b39f61a1aa46da5c8f"
EXPECTED_ROWS = 1442
EXPECTED_CHAMPION_ROWS = 133

CHAMP_FIELDS = [
    "current_champion_title",
    "championship_level",
    "championship_partner",
    "reign_number",
    "title_won_date",
    "days_into_reign_at_event",
    "title_defended_same_card",
    "title_lost_same_card",
]

NEW_SOURCES = [
    {
        "source_id": "S1700",
        "source_name": "Wrestling-Titles.com - WWE championship histories index",
        "source_type": "statistics_database",
        "url": "https://www.wrestling-titles.com/wwe/",
        "reliability_tier": "12",
        "tier_label": "Specialist wrestling statistics/reference",
        "accessed_date": "2026-09-24",
        "notes": "Index to chronological WWE/WWF championship lineages; used with event sources to audit champion status on each Royal Rumble date.",
    },
    {
        "source_id": "S1701",
        "source_name": "Wrestling-Titles.com - WWWF/WWF/WWE World Tag Team title history",
        "source_type": "statistics_database",
        "url": "https://www.wrestling-titles.com/wwe/wwe-world-t.html",
        "reliability_tier": "12",
        "tier_label": "Specialist wrestling statistics/reference",
        "accessed_date": "2026-09-24",
        "notes": "Chronological original WWF/WWE World Tag Team lineage, including Demolition's first reign beginning 1988-03-27.",
    },
    {
        "source_id": "S1702",
        "source_name": "WWE.com - Demolition World Tag Team title reign",
        "source_type": "official_website",
        "url": "https://www.wwe.com/classics/titlehistory/worldtagteam/30445413212311",
        "reliability_tier": "1",
        "tier_label": "WWE / official sources",
        "accessed_date": "2026-09-24",
        "notes": "Official reign page gives Demolition's first reign as 1988-03-27 through 1989-07-18.",
    },
    {
        "source_id": "S1703",
        "source_name": "WWE.com - WWE Championship title history",
        "source_type": "official_website",
        "url": "https://www.wwe.com/titlehistory/wwe-championship",
        "reliability_tier": "1",
        "tier_label": "WWE / official sources",
        "accessed_date": "2026-09-24",
        "notes": "Official WWE Championship lineage used to verify Randy Savage's first reign at RR1989M.",
    },
    {
        "source_id": "S1704",
        "source_name": "WWE.com - World Tag Team Championship history (modern lineage)",
        "source_type": "official_website",
        "url": "https://www.wwe.com/titlehistory/raw-tag-team-championship",
        "reliability_tier": "1",
        "tier_label": "WWE / official sources",
        "accessed_date": "2026-09-24",
        "notes": "Official modern Raw/World Tag Team lineage and reign dates.",
    },
    {
        "source_id": "S1705",
        "source_name": "WWE.com - Royal Rumble 2018 Raw Tag Team Championship result",
        "source_type": "official_website",
        "url": "https://www.wwe.com/shows/royalrumble/2018/seth-rollins-jason-jordan-sheamus-cesaro-results",
        "reliability_tier": "1",
        "tier_label": "WWE / official sources",
        "accessed_date": "2026-09-24",
        "notes": "Official result explicitly identifies Cesaro and Sheamus beginning their fourth Raw Tag Team title reign on the card.",
    },
    {
        "source_id": "S1706",
        "source_name": "WWE.com - Raw results, January 5, 2026",
        "source_type": "official_website",
        "url": "https://www.wwe.com/shows/raw/2026-01-05/results",
        "reliability_tier": "1",
        "tier_label": "WWE / official sources",
        "accessed_date": "2026-09-24",
        "notes": "Official results for Becky Lynch's title regain and Rhea Ripley/IYO SKY's Women's Tag Team title win.",
    },
    {
        "source_id": "S1707",
        "source_name": "WWE.com - Women's Intercontinental Championship history",
        "source_type": "official_website",
        "url": "https://www.wwe.com/classics/titlehistory/womens-intercontinental-championship",
        "reliability_tier": "1",
        "tier_label": "WWE / official sources",
        "accessed_date": "2026-09-24",
        "notes": "Official lineage confirms Becky Lynch's second reign began 2026-01-05.",
    },
    {
        "source_id": "S1708",
        "source_name": "WWE.com - NXT Women's Championship history",
        "source_type": "official_website",
        "url": "https://www.wwe.com/titlehistory/nxt-womens-championship",
        "reliability_tier": "1",
        "tier_label": "WWE / official sources",
        "accessed_date": "2026-09-24",
        "notes": "Official lineage confirms Jacy Jayne's second reign began 2025-11-18.",
    },
    {
        "source_id": "S1709",
        "source_name": "WWE.com - Raw results, December 29, 2025",
        "source_type": "official_website",
        "url": "https://www.wwe.com/shows/raw/2025-12-29/results",
        "reliability_tier": "1",
        "tier_label": "WWE / official sources",
        "accessed_date": "2026-09-24",
        "notes": "Official result confirms The Usos won the World Tag Team Championship on 2025-12-29.",
    },
    {
        "source_id": "S1710",
        "source_name": "WWE.com - NXT Gold Rush results, November 18, 2025",
        "source_type": "official_website",
        "url": "https://www.wwe.com/shows/wwenxt/2025-11-18",
        "reliability_tier": "1",
        "tier_label": "WWE / official sources",
        "accessed_date": "2026-09-24",
        "notes": "Official results confirm Jacy Jayne reclaimed the NXT Women's Championship and document Chelsea Green/Ethan Page as AAA Mixed Tag champions.",
    },
]

# Reign number is individual-holder based for tag titles, matching existing
# rows (for example Kofi Kingston and Big E each carry their own count).
REIGN_NUMBER_OVERRIDES = {
    ("RR1989M", "ax"): "1",
    ("RR1989M", "smash"): "1",
    ("RR1989M", "randy-savage"): "1",
    ("RR1997M", "british-bulldog"): "1",
    ("RR1997M", "owen-hart"): "1",
    ("RR2018M", "sheamus"): "4",
    ("RR2018M", "cesaro"): "4",
    ("RR2024M", "finn-balor"): "2",
    ("RR2024M", "gunther"): "1",
    ("RR2024M", "damian-priest"): "2",
    ("RR2024W", "jordynne-grace"): "3",
    ("RR2024W", "asuka"): "4",
    ("RR2024W", "kairi-sane"): "2",
    ("RR2025M", "bron-breakker"): "2",
    ("RR2025M", "joe-hendry"): "1",
    ("RR2025M", "shinsuke-nakamura"): "3",
    ("RR2025W", "lyra-valkyria"): "1",
    ("RR2025W", "chelsea-green"): "1",
    ("RR2025W", "bianca-belair"): "2",
    ("RR2025W", "naomi"): "2",
    ("RR2025W", "candice-lerae"): "1",
    ("RR2025W", "giulia"): "1",
    ("RR2026M", "jey-uso"): "3",
    ("RR2026W", "becky-lynch"): "2",
    ("RR2026W", "chelsea-green"): "1",
    ("RR2026W", "giulia"): "2",
    ("RR2026W", "io-shirai"): "3",
    ("RR2026W", "rhea-ripley"): "1",
    ("RR2026W", "jacy-jayne"): "2",
}

ROW_SOURCE_ADDITIONS = {
    ("RR1989M", "ax"): ["S1700", "S1701", "S1702"],
    ("RR1989M", "smash"): ["S1700", "S1701", "S1702"],
    ("RR1989M", "randy-savage"): ["S1700", "S1703"],
    ("RR2018M", "sheamus"): ["S1704", "S1705"],
    ("RR2018M", "cesaro"): ["S1704", "S1705"],
    ("RR2024M", "finn-balor"): ["S1704"],
    ("RR2024M", "damian-priest"): ["S1704"],
    ("RR2026M", "jey-uso"): ["S1704", "S1709"],
    ("RR2026W", "becky-lynch"): ["S1706", "S1707"],
    ("RR2026W", "chelsea-green"): ["S1710"],
    ("RR2026W", "io-shirai"): ["S1706"],
    ("RR2026W", "rhea-ripley"): ["S1706"],
    ("RR2026W", "jacy-jayne"): ["S1708", "S1710"],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def write_rows(path: Path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def add_source_ids(existing: str, additions: list[str]) -> str:
    values = [value for value in existing.split(";") if value]
    for value in additions:
        if value not in values:
            values.append(value)
    return ";".join(values)


def main():
    entrant_hash = sha256(ENTRANTS)
    source_hash = sha256(SOURCES)
    already_applied = source_hash != EXPECTED_SOURCES_SHA256 and all(
        source["source_id"] in SOURCES.read_text(encoding="utf-8-sig")
        for source in NEW_SOURCES
    )
    if already_applied:
        print("Championship profile tier is already applied; no changes made.")
        return
    if entrant_hash != EXPECTED_ENTRANTS_SHA256 or source_hash != EXPECTED_SOURCES_SHA256:
        raise SystemExit(
            "Baseline guard failed: "
            f"entrants={entrant_hash}, sources={source_hash}"
        )

    entrant_fields, entrants = read_rows(ENTRANTS)
    source_fields, sources = read_rows(SOURCES)
    if len(entrants) != EXPECTED_ROWS:
        raise SystemExit(f"Expected {EXPECTED_ROWS} entrant rows, found {len(entrants)}")
    champion_rows = [row for row in entrants if row["current_champion_title"]]
    if len(champion_rows) != EXPECTED_CHAMPION_ROWS:
        raise SystemExit(
            f"Expected {EXPECTED_CHAMPION_ROWS} populated champion rows, found {len(champion_rows)}"
        )

    existing_source_ids = {row["source_id"] for row in sources}
    if existing_source_ids.intersection(source["source_id"] for source in NEW_SOURCES):
        raise SystemExit("One or more new source IDs already exist")
    sources.extend(NEW_SOURCES)

    changes = []
    for row in entrants:
        before = {field: row[field] for field in CHAMP_FIELDS + ["source_ids"]}
        key = (row["event_id"], row["wrestler_id"])
        is_champion = bool(row["current_champion_title"])

        if not is_champion:
            # The existing event-by-event champion set was audited against the
            # complete title lineages before verified absence was written.
            for field in (
                "current_champion_title",
                "championship_level",
                "championship_partner",
                "reign_number",
                "days_into_reign_at_event",
            ):
                if not row[field]:
                    row[field] = "N/A"
            if row["title_won_date"] in ("", "UNKNOWN"):
                row["title_won_date"] = "N/A"
            # Preserve the two known same-card title losses and every existing
            # FALSE. Only genuinely blank booleans become verified N/A.
            if not row["title_defended_same_card"]:
                row["title_defended_same_card"] = "N/A"
            if not row["title_lost_same_card"]:
                row["title_lost_same_card"] = "N/A"
        else:
            if not row["championship_partner"]:
                row["championship_partner"] = "N/A"
            if key in REIGN_NUMBER_OVERRIDES:
                row["reign_number"] = REIGN_NUMBER_OVERRIDES[key]
            if not row["title_defended_same_card"]:
                row["title_defended_same_card"] = "FALSE"
            if not row["title_lost_same_card"]:
                row["title_lost_same_card"] = "FALSE"

            if key in (("RR1989M", "ax"), ("RR1989M", "smash")):
                row["title_won_date"] = "1988-03-27"
                row["days_into_reign_at_event"] = "294"
            elif key == ("RR1989M", "randy-savage"):
                row["title_won_date"] = "1988-03-27"
                row["days_into_reign_at_event"] = "294"

        # The specialist lineage index is the championship-layer audit source
        # for every row; each row already carries its event-specific source(s).
        row["source_ids"] = add_source_ids(row["source_ids"], ["S1700"])
        if key in ROW_SOURCE_ADDITIONS:
            row["source_ids"] = add_source_ids(
                row["source_ids"], ROW_SOURCE_ADDITIONS[key]
            )

        changed_fields = [
            field for field in CHAMP_FIELDS + ["source_ids"]
            if row[field] != before[field]
        ]
        if changed_fields:
            changes.append({
                "event_id": row["event_id"],
                "wrestler_id": row["wrestler_id"],
                "changed_fields": ";".join(changed_fields),
                **{field: row[field] for field in CHAMP_FIELDS},
                "source_ids": row["source_ids"],
            })

    missing_reign = [
        (row["event_id"], row["wrestler_id"])
        for row in entrants
        if row["current_champion_title"] != "N/A" and not row["reign_number"]
    ]
    incomplete = [
        (row["event_id"], row["wrestler_id"], field)
        for row in entrants
        for field in CHAMP_FIELDS
        if not row[field]
    ]
    if missing_reign or incomplete:
        raise SystemExit(
            f"Championship closeout incomplete: missing_reign={missing_reign}, "
            f"blank_cells={incomplete[:20]}"
        )

    write_rows(ENTRANTS, entrant_fields, entrants)
    write_rows(SOURCES, source_fields, sources)
    manifest_fields = [
        "event_id", "wrestler_id", "changed_fields", *CHAMP_FIELDS, "source_ids"
    ]
    write_rows(MANIFEST, manifest_fields, changes)
    print(f"Updated {len(changes)} entrant rows.")
    print(f"Added {len(NEW_SOURCES)} sources.")
    print(f"Manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
