#!/usr/bin/env python3
"""Close the company-debut and WWE/storyline-return entrant fields.

This is intentionally a one-shot, baseline-guarded research migration.  It
does not infer returns from gaps between Royal Rumble appearances.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ENTRANTS = DATA / "entrants.csv"
EVENTS = DATA / "events.csv"
SOURCES = DATA / "sources.csv"
MANIFEST = ROOT / "DEBUT_RETURN_CHANGED_ROWS.csv"

EXPECTED_ENTRANTS_SHA256 = "ccb89379d10f33a1700f2b80cdeb21855a235f0b6283a30a1ea25a4527401068"
EXPECTED_SOURCES_SHA256 = "b92f76b106f9f35c3656a653e96a666cbdb17ec1c502a9abc4f9f8381f7013c1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_rows(path: Path, rows, fields):
    # Project CSVs are UTF-8 without a BOM; preserve that byte-level convention.
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def add_source_ids(value: str, *source_ids: str) -> str:
    parts = [part for part in value.split(";") if part]
    for source_id in source_ids:
        if source_id not in parts:
            parts.append(source_id)
    return ";".join(parts)


# A company debut means first appearance for WWF/WWE, not first match, first
# main-roster match, first contracted match, or first Royal Rumble.
COMPANY_DEBUTS = {
    ("RR1996M", "vader"): ("S1719", "S1720"),
    ("RR2016M", "aj-styles"): ("S1721", "S1722"),
    ("RR2026M", "powerhouse-hobbs"): ("S1723", "S1724"),
}


# TRUE only where the Rumble appearance itself was documented as a return to
# WWE or to in-ring action following a company, retirement, or injury absence.
# For older alumni cameos, contemporary/official sources often document the
# return without quantifying the layoff; those honest gaps are recorded as
# UNKNOWN instead of reverse-engineering a duration from Rumble chronology.
RETURNS = {
    ("RR1998M", "the-honky-tonk-man"): ("UNKNOWN", ("S1725",)),
    ("RR2000M", "bob-backlund"): ("UNKNOWN", ("S1725",)),
    ("RR2001M", "the-honky-tonk-man"): ("UNKNOWN", ("S1725",)),
    ("RR2001M", "big-show"): ("several months", ("S1725",)),
    ("RR2002M", "goldust"): ("a few years", ("S1725",)),
    ("RR2002M", "mr-perfect"): ("UNKNOWN", ("S1725",)),
    ("RR2003M", "the-undertaker"): ("several months", ("S1725",)),
    ("RR2004M", "mick-foley"): ("UNKNOWN", ("S1725",)),
    ("RR2006M", "rob-van-dam"): ("most of 2005 (reconstructive knee surgery)", ("S1725",)),
    ("RR2008M", "jimmy-snuka"): ("UNKNOWN", ("S1725",)),
    ("RR2008M", "roddy-piper"): ("UNKNOWN", ("S1725",)),
    ("RR2008M", "john-cena"): ("approximately 4 months (torn pectoral)", ("S1725", "S1726")),
    ("RR2010M", "edge"): ("approximately 7 months (torn Achilles tendon)", ("S1725", "S1727")),
    ("RR2013M", "goldust"): ("UNKNOWN", ("S1711",)),
    ("RR2013M", "the-godfather"): ("UNKNOWN", ("S1711",)),
    ("RR2013M", "rey-mysterio"): ("UNKNOWN", ("S1711",)),
    ("RR2015M", "bubba-ray-dudley"): ("UNKNOWN", ("S1712",)),
    ("RR2015M", "the-boogeyman"): ("UNKNOWN", ("S1712",)),
    ("RR2015M", "diamond-dallas-page"): ("UNKNOWN", ("S1712",)),
    ("RR2015M", "zack-ryder"): ("approximately 2 months (injury)", ("S1712",)),
    ("RR2018M", "the-hurricane"): ("UNKNOWN", ("S1713",)),
    ("RR2018M", "rey-mysterio"): ("more than 3 years away from WWE", ("S1713",)),
    ("RR2018W", "lita"): ("UNKNOWN", ("S1714",)),
    ("RR2018W", "torrie-wilson"): ("UNKNOWN", ("S1714",)),
    ("RR2018W", "molly-holly"): ("UNKNOWN", ("S1714",)),
    ("RR2018W", "michelle-mccool"): ("UNKNOWN", ("S1714",)),
    ("RR2018W", "vickie-guerrero"): ("UNKNOWN", ("S1714",)),
    ("RR2018W", "kelly-kelly"): ("UNKNOWN", ("S1714",)),
    ("RR2018W", "jacqueline"): ("UNKNOWN", ("S1714",)),
    ("RR2018W", "beth-phoenix"): ("UNKNOWN", ("S1714",)),
    ("RR2018W", "nikki-bella"): ("UNKNOWN", ("S1714",)),
    ("RR2018W", "brie-bella"): ("UNKNOWN", ("S1714",)),
    ("RR2018W", "trish-stratus"): ("UNKNOWN", ("S1714",)),
    ("RR2019M", "jeff-jarrett"): ("UNKNOWN", ("S1728",)),
    ("RR2020M", "mvp"): ("UNKNOWN", ("S1729",)),
    ("RR2020M", "edge"): ("nearly 9 years (retirement due to neck injury)", ("S1729",)),
    ("RR2020W", "molly-holly"): ("UNKNOWN", ("S1729",)),
    ("RR2020W", "beth-phoenix"): ("UNKNOWN", ("S1729",)),
    ("RR2020W", "kelly-kelly"): ("UNKNOWN", ("S1729",)),
    ("RR2020W", "santino-marella"): ("UNKNOWN", ("S1729",)),
    ("RR2021M", "carlito"): ("more than 10 years away from WWE competition", ("S1730",)),
    ("RR2021M", "kane"): ("UNKNOWN", ("S1730",)),
    ("RR2021M", "the-hurricane"): ("UNKNOWN", ("S1730",)),
    ("RR2021M", "christian"): ("nearly 7 years (retirement due to concussion issues)", ("S1730",)),
    ("RR2021W", "jillian-hall"): ("UNKNOWN", ("S1730",)),
    ("RR2021W", "victoria"): ("UNKNOWN", ("S1730",)),
    ("RR2021W", "torrie-wilson"): ("UNKNOWN", ("S1730",)),
    ("RR2022W", "melina"): ("UNKNOWN", ("S1715",)),
    ("RR2022W", "cameron"): ("UNKNOWN", ("S1715",)),
    ("RR2022W", "ivory"): ("UNKNOWN", ("S1715",)),
    ("RR2022W", "summer-rae"): ("UNKNOWN", ("S1715",)),
    ("RR2022W", "sarah-logan"): ("UNKNOWN", ("S1715",)),
    ("RR2022W", "molly-holly"): ("UNKNOWN", ("S1715",)),
    ("RR2022W", "ronda-rousey"): ("nearly 3 years away from WWE competition", ("S1715",)),
    ("RR2023M", "booker-t"): ("UNKNOWN", ("S1731",)),
    ("RR2023W", "michelle-mccool"): ("UNKNOWN", ("S1731",)),
    ("RR2023W", "nia-jax"): ("more than 1 year away from WWE", ("S1731",)),
    ("RR2024M", "andrade"): ("more than 2 years away from WWE", ("S1716",)),
    ("RR2024W", "naomi"): ("more than 1 year away from WWE", ("S1716",)),
    ("RR2024W", "liv-morgan"): ("more than 6 months (shoulder injury)", ("S1716",)),
    ("RR2025M", "aj-styles"): ("approximately 4 months (foot injury)", ("S1717",)),
    ("RR2025W", "alexa-bliss"): ("approximately 2 years away from WWE competition", ("S1717",)),
    ("RR2025W", "charlotte-flair"): ("more than 1 year (knee injury)", ("S1717",)),
    ("RR2025W", "trish-stratus"): ("UNKNOWN", ("S1717",)),
    ("RR2025W", "nikki-bella"): ("UNKNOWN", ("S1717",)),
    ("RR2026M", "la-knight"): ("approximately 2 months (storyline injury)", ("S1718",)),
    ("RR2026W", "brie-bella"): ("approximately 4 years away from WWE competition", ("S1718",)),
    ("RR2026W", "tiffany-stratton"): ("approximately 7 months (injury)", ("S1718",)),
}


NEW_SOURCES = [
    ["S1711", "WWE.com - John Cena won the 2013 Royal Rumble Match", "official_website", "https://www.wwe.com/shows/royalrumble/2013/royal-rumble-match", "1", "WWE / official sources", "2026-09-24", "Official report explicitly describes Goldust, The Godfather and Rey Mysterio as returning."],
    ["S1712", "WWE.com - Roman Reigns won the 2015 Royal Rumble Match", "official_website", "https://www.wwe.com/shows/royalrumble/2015/2015-royal-rumble-match", "1", "WWE / official sources", "2026-09-24", "Official report documents Bubba Ray Dudley, The Boogeyman, Diamond Dallas Page and Zack Ryder as returns/surprise alumni or injury return."],
    ["S1713", "WWE.com - Five coolest moments from the 2018 Men's Royal Rumble", "official_website", "https://www.wwe.com/shows/royalrumble/2018/article/mens-royal-rumble-match-5-coolest-moments", "1", "WWE / official sources", "2026-09-24", "Official retrospective documents the Hurricane cameo and Rey Mysterio's return after more than three years away."],
    ["S1714", "WWE.com - Five best moments from the 2018 Women's Royal Rumble", "official_website", "https://www.wwe.com/shows/royalrumble/2018/article/5-best-moments-2018-womens-royal-rumble-match", "1", "WWE / official sources", "2026-09-24", "Official retrospective identifies the returning women from WWE's past."],
    ["S1715", "WWE.com - Full Royal Rumble 2022 results", "official_website", "https://www.wwe.com/shows/royalrumble/article/full-royal-rumble-results", "1", "WWE / official sources", "2026-09-24", "Official results document Ronda Rousey's return and the returning alumni in the Women's match."],
    ["S1716", "WWE.com - Complete Royal Rumble 2024 results", "official_website", "https://www.wwe.com/shows/royalrumble/2024/results", "1", "WWE / official sources", "2026-09-24", "Official results explicitly document the returns of Andrade, Naomi and Liv Morgan."],
    ["S1717", "WWE.com - Royal Rumble 2025 results", "official_website", "https://www.wwe.com/shows/royalrumble/2025/results", "1", "WWE / official sources", "2026-09-24", "Official results document the returns of Charlotte Flair, Alexa Bliss, AJ Styles and returning legends."],
    ["S1718", "WWE.com - Complete Royal Rumble 2026 results", "official_website", "https://www.wwe.com/shows/royalrumble/royal-rumble-2026/results", "1", "WWE / official sources", "2026-09-24", "Official results explicitly document LA Knight, Brie Bella and Tiffany Stratton returning."],
    ["S1719", "Wikipedia - Big Van Vader", "reference", "https://en.wikipedia.org/wiki/Big_Van_Vader", "10", "Wikipedia/reference", "2026-09-24", "Biography states Vader's first WWF appearance was the 1996 Royal Rumble."],
    ["S1720", "WWE.com - Vader profile", "official_website", "https://www.wwe.com/superstars/vader", "1", "WWE / official sources", "2026-09-24", "Official WWE career profile used to corroborate Vader's WWF arrival in 1996."],
    ["S1721", "WWE.com - 2016 Royal Rumble Match result", "official_website", "https://www.wwe.com/shows/royalrumble/2016/royal-rumble-match-wwe-world-heavyweight-championship", "1", "WWE / official sources", "2026-09-24", "Official report explicitly calls AJ Styles' Royal Rumble entrance his WWE debut."],
    ["S1722", "Wikipedia - AJ Styles", "reference", "https://en.wikipedia.org/wiki/AJ_Styles", "10", "Wikipedia/reference", "2026-09-24", "Biography independently dates Styles' WWE debut to the 2016 Royal Rumble."],
    ["S1723", "WWE.com - Royal Rumble 2026", "official_website", "https://www.wwe.com/shows/royalrumble/royal-rumble-2026", "1", "WWE / official sources", "2026-09-24", "Official event report explicitly calls Royce Keys' appearance his WWE debut."],
    ["S1724", "Wikipedia - Royal Rumble (2026)", "reference", "https://en.wikipedia.org/wiki/Royal_Rumble_(2026)", "10", "Wikipedia/reference", "2026-09-24", "Independent event summary identifies Royce Keys' WWE debut."],
    ["S1725", "WWE.com - Royal Rumble returns retrospective", "official_website", "https://www.wwe.com/shows/royalrumble/article/coolest-royal-rumble-match", "1", "WWE / official sources", "2026-09-24", "Official retrospective and linked archive material document historic surprise and injury returns."],
    ["S1726", "WWE.com - John Cena Royal Rumble 2008 return", "official_website", "https://www.wwe.com/shows/royalrumble/2012/finkel-royal-rumble-21-24", "1", "WWE / official sources", "2026-09-24", "Official retrospective describes Cena's return to action after pectoral surgery."],
    ["S1727", "WWE.com - All-Time Royal Rumble Match", "official_website", "https://www.wwe.com/shows/royalrumble/all-time-royal-rumble-match", "1", "WWE / official sources", "2026-09-24", "Official retrospective documents Edge's 2010 injury return and absence."],
    ["S1728", "WWE.com - Royal Rumble 2019 results", "official_website", "https://www.wwe.com/shows/royalrumble/2019", "1", "WWE / official sources", "2026-09-24", "Official event coverage documents Jeff Jarrett's WWE return."],
    ["S1729", "WWE.com - Royal Rumble 2020 results", "official_website", "https://www.wwe.com/shows/royalrumble/2020", "1", "WWE / official sources", "2026-09-24", "Official event coverage documents Edge, MVP and returning alumni appearances."],
    ["S1730", "WWE.com - Royal Rumble 2021 results", "official_website", "https://www.wwe.com/shows/royalrumble/2021", "1", "WWE / official sources", "2026-09-24", "Official event coverage documents Christian, Carlito and returning alumni appearances."],
    ["S1731", "WWE.com - Royal Rumble 2023 results", "official_website", "https://www.wwe.com/shows/royalrumble/2023", "1", "WWE / official sources", "2026-09-24", "Official event coverage documents Booker T, Michelle McCool and Nia Jax as returns/surprise alumni."],
]


def main():
    if sha256(ENTRANTS) != EXPECTED_ENTRANTS_SHA256:
        raise SystemExit("entrants.csv baseline hash mismatch; refusing to run")
    if sha256(SOURCES) != EXPECTED_SOURCES_SHA256:
        raise SystemExit("sources.csv baseline hash mismatch; refusing to run")

    entrants, entrant_fields = read_rows(ENTRANTS)
    events, _ = read_rows(EVENTS)
    sources, source_fields = read_rows(SOURCES)
    event_dates = {row["event_id"]: row["event_date"] for row in events}
    keys = {(row["event_id"], row["wrestler_id"]) for row in entrants}
    missing = (set(COMPANY_DEBUTS) | set(RETURNS)) - keys
    if missing:
        raise SystemExit(f"curated entrant keys not found: {sorted(missing)}")

    changes = []
    tracked = ("is_company_debut", "company_debut_date", "is_returning_wrestler", "absence_length", "source_ids")
    for row in entrants:
        key = (row["event_id"], row["wrestler_id"])
        before = {field: row[field] for field in tracked}
        if key in COMPANY_DEBUTS:
            row["is_company_debut"] = "TRUE"
            row["company_debut_date"] = event_dates[row["event_id"]]
            row["source_ids"] = add_source_ids(row["source_ids"], *COMPANY_DEBUTS[key])
        else:
            row["is_company_debut"] = "FALSE"
            row["company_debut_date"] = "N/A"
        if key in RETURNS:
            duration, source_ids = RETURNS[key]
            row["is_returning_wrestler"] = "TRUE"
            row["absence_length"] = duration
            row["source_ids"] = add_source_ids(row["source_ids"], *source_ids)
        else:
            row["is_returning_wrestler"] = "FALSE"
            row["absence_length"] = "N/A"
        after = {field: row[field] for field in tracked}
        if before != after:
            changes.append({
                "event_id": row["event_id"], "wrestler_id": row["wrestler_id"],
                "ring_name_at_time": row["ring_name_at_time"],
                **{f"before_{field}": before[field] for field in tracked},
                **{f"after_{field}": after[field] for field in tracked},
            })

    existing_source_ids = {row["source_id"] for row in sources}
    if existing_source_ids & {row[0] for row in NEW_SOURCES}:
        raise SystemExit("one or more proposed source IDs already exist")
    sources.extend(dict(zip(source_fields, values)) for values in NEW_SOURCES)

    write_rows(ENTRANTS, entrants, entrant_fields)
    write_rows(SOURCES, sources, source_fields)
    manifest_fields = list(changes[0])
    write_rows(MANIFEST, changes, manifest_fields)

    assert all(row["is_company_debut"] in {"TRUE", "FALSE"} for row in entrants)
    assert all(row["company_debut_date"] for row in entrants)
    assert all(row["is_returning_wrestler"] in {"TRUE", "FALSE"} for row in entrants)
    assert all(row["absence_length"] for row in entrants)
    print(f"Updated {len(changes)} entrant rows")
    print(f"Company debuts: {sum(r['is_company_debut'] == 'TRUE' for r in entrants)}")
    print(f"Returns: {sum(r['is_returning_wrestler'] == 'TRUE' for r in entrants)}")
    print(f"Unknown return durations: {sum(r['absence_length'] == 'UNKNOWN' for r in entrants)}")
    print(f"Added {len(NEW_SOURCES)} sources")


if __name__ == "__main__":
    main()
