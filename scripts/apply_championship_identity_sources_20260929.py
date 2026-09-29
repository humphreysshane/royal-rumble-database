"""Register new identity sources used by the championship-link audit."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from schema import SOURCES_FIELDS


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "sources.csv"

SOURCES = [
    {
        "source_name": "Wikipedia profile: Bryan Clark / Adam Bomb / Wrath",
        "source_type": "reference",
        "url": "https://en.wikipedia.org/wiki/Bryan_Clark",
        "reliability_tier": "10",
        "tier_label": "Wikipedia/reference",
        "accessed_date": "2026-09-29",
        "notes": "Identity source connecting Bryan Clark's Adam Bomb and Wrath ring names and KroniK title history.",
    },
    {
        "source_name": "Wikipedia profile: Mike Bucci / Nova / Simon Dean",
        "source_type": "reference",
        "url": "https://en.wikipedia.org/wiki/Mike_Bucci",
        "reliability_tier": "10",
        "tier_label": "Wikipedia/reference",
        "accessed_date": "2026-09-29",
        "notes": "Identity source connecting Mike Bucci's Nova, Super Nova, Hollywood Nova and Simon Dean ring names.",
    },
    {
        "source_name": "Wikipedia profile: Steve Keirn / Skinner",
        "source_type": "reference",
        "url": "https://en.wikipedia.org/wiki/Steve_Keirn",
        "reliability_tier": "10",
        "tier_label": "Wikipedia/reference",
        "accessed_date": "2026-09-29",
        "notes": "Identity source connecting Steve Keirn's Skinner and Doink presentations and championship history.",
    },
    {
        "source_name": "Wikipedia profile: Paul Diamond / Max Moon / Kato",
        "source_type": "reference",
        "url": "https://en.wikipedia.org/wiki/Paul_Diamond",
        "reliability_tier": "10",
        "tier_label": "Wikipedia/reference",
        "accessed_date": "2026-09-29",
        "notes": "Identity source connecting Thomas Boric's Paul Diamond, Kato and Max Moon ring names and AWA title history.",
    },
]


def main() -> None:
    with PATH.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    by_url = {row["url"]: row for row in rows if row.get("url")}
    next_id = max(int(m.group(1)) for row in rows if (m := re.fullmatch(r"S(\d+)", row["source_id"]))) + 1
    added = 0
    for source in SOURCES:
        if source["url"] in by_url:
            continue
        row = {field: "" for field in SOURCES_FIELDS}
        row.update(source)
        row["source_id"] = f"S{next_id:03d}"
        next_id += 1
        rows.append(row)
        by_url[source["url"]] = row
        added += 1
    with PATH.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=SOURCES_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Registered {added} new identity source(s).")


if __name__ == "__main__":
    main()
