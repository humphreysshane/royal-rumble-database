#!/usr/bin/env python3
"""Populate ethnicity/heritage only from public first-person identification.

Nationality, birthplace, surname, family inference, appearance, gimmick and
third-party biographical labeling are deliberately insufficient.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WRESTLERS = DATA / "wrestlers.csv"
SOURCES = DATA / "sources.csv"
MANIFEST = ROOT / "ETHNICITY_HERITAGE_CHANGED_ROWS.csv"

EXPECTED_WRESTLERS_SHA256 = "4766d14eb2600386314036a1ad7eb1decc196aebd6ebc987be3e7ba7a4ca6603"
EXPECTED_SOURCES_SHA256 = "226b4d84bcbad65c396a4c125c135eade22587d52bf0d7049f55e2b6c38a36a1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_rows(path: Path, rows, fields):
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


# Values reproduce the wrestler's own terminology as closely as practical.
# One direct source = PROBABLE; two independent agreeing direct sources =
# CONFIRMED, following DEFINITIONS.md.
VERIFIED = {
    "naomi": ("African-American", "PROBABLE", ("S1732",)),
    "titus-oneil": ("African-American", "PROBABLE", ("S1732",)),
    "r-truth": ("African-American", "PROBABLE", ("S1732",)),
    "melina": ("Mexican heritage", "PROBABLE", ("S1733",)),
    "alberto-del-rio": ("Mexican", "PROBABLE", ("S1734",)),
    "rey-mysterio": ("Mexican heritage", "CONFIRMED", ("S1735", "S1736")),
    "elijah-burke": ("African-American", "PROBABLE", ("S1737",)),
    "kalisto": ("Mexican-American", "PROBABLE", ("S1738",)),
    "bianca-belair": ("African-American", "PROBABLE", ("S1739",)),
    "roman-reigns": ("Samoan heritage", "PROBABLE", ("S1740",)),
    "jey-uso": ("Samoan", "CONFIRMED", ("S1741", "S1742")),
    "jimmy-uso": ("Samoan", "PROBABLE", ("S1741",)),
    "damian-priest": ("Hispanic/Latino heritage", "PROBABLE", ("S1743",)),
    "dominik-mysterio": ("Hispanic/Latino heritage", "PROBABLE", ("S1743",)),
    "raquel-rodriguez": ("Hispanic/Latino heritage", "PROBABLE", ("S1743",)),
    "santos-escobar": ("Hispanic/Latino heritage", "PROBABLE", ("S1743",)),
    "jinder-mahal": ("Punjabi heritage", "CONFIRMED", ("S1744", "S1745")),
    "sami-zayn": ("Arab; Syrian", "CONFIRMED", ("S1746", "S1747")),
    "rocky-maivia": ("Black and Samoan", "CONFIRMED", ("S1748", "S1749")),
    "batista": ("Greek and Filipino heritage", "PROBABLE", ("S1750",)),
    "mustafa-ali": ("Indian and Pakistani heritage", "CONFIRMED", ("S1751", "S1752")),
}


NEW_SOURCES = [
    ["S1732", "WWE.com - Naomi, Titus O'Neil and R-Truth discuss identity and Black culture", "official_website", "https://www.wwe.com/article/naomi-titus-oneil-r-truth-identity-culture-black-history-month", "1", "WWE / official sources", "2026-09-24", "Direct first-person interview: all three identify themselves as African-American and discuss their culture."],
    ["S1733", "WWE.com - A complete Diva: Melina", "official_website", "https://www.wwe.com/superstars/divas/16662898/summerskin/melina/completediva", "1", "WWE / official sources", "2026-09-24", "Melina directly states that her Mexican heritage is part of who she is."],
    ["S1734", "WWE.com - Alberto Del Rio on his Mexican identity", "official_website", "https://www.wwe.com/shows/raw/2013-01-21/is-alberto-del-rio-wwes-newest-mexican-hero", "1", "WWE / official sources", "2026-09-24", "Del Rio directly states that he is proud to be Mexican."],
    ["S1735", "WWE.com - Rey Mysterio reflects on Mexico and his heritage", "official_website", "https://www.wwe.com/inside/news/archive/mexico", "1", "WWE / official sources", "2026-09-24", "Mysterio directly states that his parents are Mexican and describes this as his heritage."],
    ["S1736", "WWE.com - Rey Mysterio: A made man", "official_website", "https://www.wwe.com/inside/superstarink/articles/reymysterio?page=1", "1", "WWE / official sources", "2026-09-24", "Independent direct quote: Mysterio describes his MEXICAN tattoo as his culture and identity."],
    ["S1737", "WWE.com - Elijah Burke on Black History Month", "official_website", "https://www.wwe.com/superstars/releasedtalent/elijahburke/eexperiencearchive/elijahexp2-18-07", "1", "WWE / official sources", "2026-09-24", "First-person column in which Burke repeatedly identifies himself as African-American."],
    ["S1738", "WWE.com - Kalisto on Hispanic Heritage Month", "official_website", "https://www.wwe.com/worldwide/article/kalisto-blogs-about-national-hispanic-heritage-month", "1", "WWE / official sources", "2026-09-24", "First-person column: Kalisto explicitly describes himself as a second-generation Mexican-American."],
    ["S1739", "WWE.com - Bianca Belair discusses her family history", "official_website", "https://www.wwe.com/shows/wwenxt/article/bianca-belair-family-history-black-history-month", "1", "WWE / official sources", "2026-09-24", "Direct interview in which Belair describes African-American history as her roots and family history."],
    ["S1740", "WWE.com - Roman Reigns discusses his Samoan heritage", "official_website", "https://www.wwe.com/article/roman-reigns-inked-magazine-cover", "1", "WWE / official sources", "2026-09-24", "Official summary of Reigns' first-person Inked interview about honoring his Samoan heritage."],
    ["S1741", "WWE.com - The Usos' theme channels Samoan heritage", "official_website", "https://www.wwe.com/inside/wwemusic/usos-david-dallas-music", "1", "WWE / official sources", "2026-09-24", "Jimmy and Jey Uso directly discuss representing their Samoan heritage."],
    ["S1742", "Wrestling Inc - Jey Uso discusses Samoan identity", "news_interview", "https://www.wrestlinginc.com/news/2021/05/jey-uso-on-being-proud-of-roman-reigns-nia-jax-tamina-succeeding-as-samoans-in-wwe/", "7", "Reputable wrestling publication", "2026-09-24", "Direct interview: Jey repeatedly identifies himself, Jimmy and their family as Samoan."],
    ["S1743", "WWE.com - Superstars celebrate Hispanic Heritage Month", "official_website", "https://www.wwe.com/article/wwe-superstars-celebrate-hispanic-heritage-month", "1", "WWE / official sources", "2026-09-24", "Damian Priest, Dominik Mysterio, Raquel Rodriguez and Santos Escobar lend their own voices to shared Hispanic/Latino traditions, culture and roots."],
    ["S1744", "Oklafan - Jinder Mahal interview on Punjabi heritage", "news_interview", "https://www.oklafan.com/interviews/print/9190/", "7", "Reputable wrestling publication", "2026-09-24", "Direct interview: Mahal describes learning Punjabi first and discusses his Indian/Punjabi heritage."],
    ["S1745", "Sportsnet - Jinder Mahal profile and interview", "news_interview", "https://www.sportsnet.ca/more/big-read-jinder-mahal-game-changer-wwe/", "7", "Reputable sports publication", "2026-09-24", "Independent direct interview: Mahal says he thinks in Punjabi and is proud of his heritage."],
    ["S1746", "The National - Sami Zayn on his Syrian identity", "news_interview", "https://www.thenationalnews.com/sport/wwe-superstar-sami-zayn-feels-at-home-wrestling-in-abu-dhabi-1.115073", "7", "Reputable news publication", "2026-09-24", "Direct interview: Zayn identifies himself as Arabic and 100 percent Syrian."],
    ["S1747", "Sports Illustrated - Sami Zayn Syria fundraiser Q&A", "news_interview", "https://www.si.com/extra-mustard/2017/09/09/sami-zayn-syria-fundraiser", "7", "Reputable sports publication", "2026-09-24", "Independent interview/profile centered on Zayn's Syrian heritage and his own Syria work."],
    ["S1748", "Men's Health - Dwayne Johnson interview", "news_interview", "https://www.menshealth.com/entertainment/a41822648/dwayne-johnson-the-rock-black-adam-interview/", "7", "Reputable publication", "2026-09-24", "Johnson directly states that he is half Black and half Samoan."],
    ["S1749", "TIME - Dwayne Johnson TIME 100 Gala transcript", "news_interview", "https://time.com/5576958/time-100-2019-dwayne-johnson-toast/", "7", "Reputable publication", "2026-09-24", "Independent first-person transcript: Johnson again states that he is half Black and half Samoan."],
    ["S1750", "Greek Reporter - Dave Bautista heritage interview", "news_interview", "https://greekreporter.com/2014/07/23/dave-batista-talks-greek-heritage-and-guardians-of-the-galaxy-video/", "7", "Reputable interview publication", "2026-09-24", "Direct interview in which Bautista discusses both his Greek and Filipino backgrounds and identifies as half-Greek."],
    ["S1751", "Mid-Day - Mustafa Ali interview on Indian and Pakistani roots", "news_interview", "https://www.mid-day.com/amp/sports/other-sports/article/mustafa-ali--the-police-officer-who-became-a-wwe-wrestler-19899165", "7", "Reputable news publication", "2026-09-24", "Direct interview: Ali identifies himself as half-Indian and explains his Pakistani father and Indian mother."],
    ["S1752", "The Johnson Transcript - Mustafa Ali interview", "news_interview", "https://johnsontranscript.com/2013/07/17/prince-mustafa-ali-interview/", "9", "Interview/transcript", "2026-09-24", "Independent direct interview: Ali states that his father is from Pakistan and his mother is from India."],
]


def main():
    if sha256(WRESTLERS) != EXPECTED_WRESTLERS_SHA256:
        raise SystemExit("wrestlers.csv baseline hash mismatch; refusing to run")
    if sha256(SOURCES) != EXPECTED_SOURCES_SHA256:
        raise SystemExit("sources.csv baseline hash mismatch; refusing to run")

    wrestlers, wrestler_fields = read_rows(WRESTLERS)
    sources, source_fields = read_rows(SOURCES)
    ids = {row["wrestler_id"] for row in wrestlers}
    if set(VERIFIED) - ids:
        raise SystemExit(f"curated wrestler IDs missing: {sorted(set(VERIFIED) - ids)}")

    changes = []
    for row in wrestlers:
        before = {field: row[field] for field in ("ethnicity_heritage", "ethnicity_heritage_status", "source_ids")}
        if row["wrestler_id"] in VERIFIED:
            value, status, source_ids = VERIFIED[row["wrestler_id"]]
            row["ethnicity_heritage"] = value
            row["ethnicity_heritage_status"] = status
            row["source_ids"] = add_source_ids(row["source_ids"], *source_ids)
        else:
            row["ethnicity_heritage"] = ""
            row["ethnicity_heritage_status"] = "UNKNOWN"
        after = {field: row[field] for field in before}
        if before != after:
            changes.append({
                "wrestler_id": row["wrestler_id"], "ring_name": row["ring_name"],
                **{f"before_{field}": before[field] for field in before},
                **{f"after_{field}": after[field] for field in before},
            })

    existing = {row["source_id"] for row in sources}
    new_ids = {row[0] for row in NEW_SOURCES}
    if existing & new_ids:
        raise SystemExit(f"source IDs already exist: {sorted(existing & new_ids)}")
    sources.extend(dict(zip(source_fields, values)) for values in NEW_SOURCES)

    write_rows(WRESTLERS, wrestlers, wrestler_fields)
    write_rows(SOURCES, sources, source_fields)
    write_rows(MANIFEST, changes, list(changes[0]))

    assert len(changes) == len(wrestlers) == 530
    assert all(row["ethnicity_heritage_status"] in {"CONFIRMED", "PROBABLE", "UNKNOWN"} for row in wrestlers)
    assert all(bool(row["ethnicity_heritage"]) == (row["ethnicity_heritage_status"] != "UNKNOWN") for row in wrestlers)
    print(f"Updated {len(changes)} wrestler rows")
    print(f"Populated self-identified heritage: {len(VERIFIED)}")
    print(f"Confirmed: {sum(r['ethnicity_heritage_status'] == 'CONFIRMED' for r in wrestlers)}")
    print(f"Probable: {sum(r['ethnicity_heritage_status'] == 'PROBABLE' for r in wrestlers)}")
    print(f"Unknown: {sum(r['ethnicity_heritage_status'] == 'UNKNOWN' for r in wrestlers)}")
    print(f"Added {len(NEW_SOURCES)} sources")


if __name__ == "__main__":
    main()
