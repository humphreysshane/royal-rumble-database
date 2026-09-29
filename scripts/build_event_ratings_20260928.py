#!/usr/bin/env python3
"""Build the first complete Royal Rumble match-ratings reference table.

Each match has two raw observations from its direct Cagematch match page:
the live Cagematch fan aggregate and the Wrestling Observer Newsletter rating
displayed by Cagematch. Scales are preserved and never blended.
"""

import csv
import os
import re
import sys

from schema import EVENT_RATINGS_FIELDS, SOURCES_FIELDS


DATA_DIR = sys.argv[1] if len(sys.argv) > 1 else "data"
ACCESSED = "2026-09-28"

# event_id, Cagematch match number, current fan aggregate, valid votes,
# Cagematch-displayed WON rating.
RATINGS = [
    ("RR1988M", "20858", "5.40", "173", "***1/2"),
    ("RR1989M", "17279", "5.70", "157", "**1/2"),
    ("RR1990M", "20859", "6.67", "158", "***"),
    ("RR1991M", "20860", "5.41", "146", "**1/4"),
    ("RR1992M", "61", "8.60", "429", "***3/4"),
    ("RR1993M", "18890", "4.56", "165", "DUD"),
    ("RR1994M", "19358", "6.00", "136", "**1/2"),
    ("RR1995M", "15470", "4.82", "147", "***1/2"),
    ("RR1996M", "20718", "5.38", "132", "**1/2"),
    ("RR1997M", "20861", "6.87", "196", "***"),
    ("RR1998M", "19625", "5.77", "170", "**1/2"),
    ("RR1999M", "12556", "3.77", "168", "*1/2"),
    ("RR2000M", "206", "6.05", "275", "**3/4"),
    ("RR2001M", "234", "8.63", "399", "***1/4"),
    ("RR2002M", "290", "7.32", "236", "***1/2"),
    ("RR2003M", "344", "7.45", "238", "***1/4"),
    ("RR2004M", "394", "8.54", "305", "***3/4"),
    ("RR2005M", "460", "8.13", "247", "DUD"),
    ("RR2006M", "530", "6.81", "206", "***1/2"),
    ("RR2007M", "595", "8.80", "382", "****"),
    ("RR2008M", "651", "8.26", "339", "****1/4"),
    ("RR2009M", "3528", "7.52", "268", "***1/2"),
    ("RR2010M", "4119", "7.73", "301", "***1/2"),
    ("RR2011M", "4612", "6.47", "229", "***1/2"),
    ("RR2012M", "5133", "5.67", "209", "***1/4"),
    ("RR2013M", "5429", "6.31", "220", "***1/2"),
    ("RR2014M", "5927", "5.06", "260", "***1/4"),
    ("RR2015M", "18427", "1.67", "272", "*3/4"),
    ("RR2016M", "7164", "7.43", "359", "****"),
    ("RR2017M", "8082", "5.48", "384", "***3/4"),
    ("RR2018M", "9123", "8.36", "448", "****1/4"),
    ("RR2018W", "9122", "7.21", "351", "***1/4"),
    ("RR2019M", "10120", "6.45", "312", "***1/4"),
    ("RR2019W", "10117", "6.60", "307", "***1/4"),
    ("RR2020M", "12063", "8.64", "609", "****1/4"),
    ("RR2020W", "12079", "6.58", "225", "***1/2"),
    ("RR2021M", "28129", "6.72", "387", "****1/4"),
    ("RR2021W", "28127", "7.18", "355", "***3/4"),
    ("RR2022M", "47556", "1.80", "559", "**1/4"),
    ("RR2022W", "47551", "4.37", "455", "**1/4"),
    ("RR2023M", "67343", "7.51", "716", "****1/4"),
    ("RR2023W", "67347", "6.64", "582", "***1/2"),
    ("RR2024M", "86097", "5.83", "779", "****1/4"),
    ("RR2024W", "86101", "7.39", "760", "***"),
    ("RR2025M", "108818", "6.21", "905", "****1/2"),
    ("RR2025W", "108814", "5.89", "830", "***1/2"),
    ("RR2026M", "131859", "4.72", "622", "***3/4"),
    ("RR2026W", "131855", "6.17", "583", "***1/2"),
]


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_rows(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


sources_path = os.path.join(DATA_DIR, "sources.csv")
events_path = os.path.join(DATA_DIR, "events.csv")
ratings_path = os.path.join(DATA_DIR, "event_ratings.csv")

sources = read_rows(sources_path)
event_ids = {r["event_id"] for r in read_rows(events_path)}
missing_events = sorted({event_id for event_id, *_ in RATINGS} - event_ids)
if missing_events:
    raise SystemExit(f"Rating rows reference missing events: {missing_events}")

source_by_url = {r.get("url", ""): r["source_id"] for r in sources if r.get("url")}
used_numbers = [
    int(m.group(1))
    for r in sources
    if (m := re.fullmatch(r"S(\d+)", r.get("source_id", "")))
]
next_source_number = max(used_numbers, default=0) + 1

source_for_event = {}
new_source_count = 0
for event_id, match_nr, *_ in RATINGS:
    url = f"https://www.cagematch.net/?id=111&nr={match_nr}"
    source_id = source_by_url.get(url)
    if not source_id:
        source_id = f"S{next_source_number:03d}"
        next_source_number += 1
        new_source_count += 1
        division = "Women's" if event_id.endswith("W") else "Men's"
        sources.append({
            "source_id": source_id,
            "source_name": f"Cagematch - {event_id} {division} Royal Rumble match",
            "source_type": "database",
            "url": url,
            "reliability_tier": "4",
            "tier_label": "Cagematch",
            "accessed_date": ACCESSED,
            "notes": "Direct match page; captured the live fan aggregate, valid-vote count, and the displayed Wrestling Observer Newsletter rating.",
        })
        source_by_url[url] = source_id
    source_for_event[event_id] = source_id

rows = []
rating_number = 1
for event_id, match_nr, fan_rating, votes, won_rating in RATINGS:
    url = f"https://www.cagematch.net/?id=111&nr={match_nr}"
    source_id = source_for_event[event_id]
    rows.append({
        "rating_id": f"RAT{rating_number:03d}",
        "event_id": event_id,
        "source_name": "Cagematch",
        "rating_scale": "out of 10",
        "rating_value": fan_rating,
        "rating_type": "fan_aggregate",
        "review_url": url,
        "rating_status": "PROBABLE",
        "source_ids": source_id,
        "notes": f"Live Cagematch match aggregate from {votes} valid votes when accessed {ACCESSED}; this value can change as new votes are added.",
    })
    rating_number += 1
    rows.append({
        "rating_id": f"RAT{rating_number:03d}",
        "event_id": event_id,
        "source_name": "Wrestling Observer Newsletter (via Cagematch)",
        "rating_scale": "out of 5 stars",
        "rating_value": won_rating,
        "rating_type": "match_rating",
        "review_url": url,
        "rating_status": "PROBABLE",
        "source_ids": source_id,
        "notes": "Cagematch labels this value as the WON rating. It is retained in the original star notation; Cagematch is a secondary report of the Observer rating.",
    })
    rating_number += 1

write_rows(sources_path, SOURCES_FIELDS, sources)
write_rows(ratings_path, EVENT_RATINGS_FIELDS, rows)
print(f"Wrote {len(rows)} rating observations for {len(RATINGS)} events/matches; added {new_source_count} source rows.")
