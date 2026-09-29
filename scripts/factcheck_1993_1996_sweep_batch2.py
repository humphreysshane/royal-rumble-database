#!/usr/bin/env python3
"""
1993-1996 fact-check sweep, batch 2. Continues the deceased-status audit
pattern from batch 1 (F339-F341, 1989-1992) into the next 4 events, and
adds 2 more notable_moments.csv rows.

(1) DECEASED-STATUS AUDIT, same method as batch 1: checked every RR1993M-
    RR1996M entrant's deceased_date field against Wikipedia (S022) cross-
    checked with an independent second source. Found 6 more wrestlers
    confirmed deceased but blank: Bam Bam Bigelow (2007-01-19), King Kong
    Bundy (2019-03-04), Dick Murdoch (1996-06-15 -- NOTE: this row's own
    notes field already said "Deceased (per S031's 'the late Dick
    Murdoch')" but the deceased_date field itself was never actually
    filled in, another instance of the "known but not filled in" pattern
    from batch 1), Owen Hart (1999-05-23 -- confirmed NOT a WWE Hall of
    Famer, a genuine and well-documented case, not an oversight, so no
    hall_of_fame_year added), Vader (2018-06-18), and Jimmy Del Ray
    (2014-12-06, WWE.com's own "Jimmy Del Ray passes away" tribute article
    used as the official-tier source). Also found Yokozuna's 2012 Hall of
    Fame induction (WWE.com, 2 separate pages) missing from his otherwise-
    already-correct deceased_date row.

    Checked but NOT changed, to avoid the opposite mistake (conflating two
    different people): this database's "doink" and "doink-1995"
    wrestler_ids are NOT Matt Borne (who died 2013-06-28) -- per this
    database's own existing, carefully-researched flags F095/F096, both
    ids are already attributed to a different performer, Ray Apollo/Ray
    Licameli, based on external sourcing from the original build pass.
    Ray Apollo appears to still be alive and active online (an apparently
    current @WWEDoink account was found). Also checked and found no death
    evidence for Great Kabuki, Headshrinker Sione, Jacob Blu/Don Harris,
    or The Headhunters -- left as-is rather than guessed at.

(2) 2 new notable_moments.csv rows:
      - RR1993M: Giant Gonzalez's outside-interference elimination of The
        Undertaker -- already well-documented in this database (see flag
        F053, sourced S027;S028) but only as prose in events.csv, never
        surfaced in the notable_moments table the dashboard now has a
        panel for. No new research needed, just made discoverable.
      - RR1996M: the Free-For-All pre-show match (Duke Droese vs. Hunter
        Hearst Helmsley) that decided who got the Rumble's #1 vs. #30
        entry -- newly researched this pass, CONFIRMED by 2 independent
        sources (whatculture.com's general summary; Wikipedia's more
        detailed account, including the Gorilla Monsoon brass-knuckles DQ
        reversal that actually decided it) and independently
        cross-validated against this database's own already-CONFIRMED
        entry_number values for both wrestlers (Droese #30, Helmsley #1)
        -- everything lines up.

New sources: S136 (Wikipedia's Royal Rumble 1993-1996 event articles,
continuing the per-year-range convention of S026), S137 (WWE.com's Jimmy
Del Ray tribute article and Yokozuna Hall of Fame pages), S138
(whatculture.com's "10 Fascinating Royal Rumble Facts" article series,
continuing the per-year-range convention of S134).

Usage:
    python3 factcheck_1993_1996_sweep_batch2.py [data_dir]   (default: data)
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import NOTABLE_MOMENTS_FIELDS

DATA_DIR = sys.argv[1] if len(sys.argv) > 1 else "data"


def load(name):
    path = f"{DATA_DIR}/{name}"
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def save(name, fieldnames, rows):
    path = f"{DATA_DIR}/{name}"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    w_fields, w_rows = load("wrestlers.csv")
    s_fields, s_rows = load("sources.csv")
    flag_fields, flags = load("flags.csv")
    try:
        nm_fields, nm_rows = load("notable_moments.csv")
    except FileNotFoundError:
        nm_fields, nm_rows = NOTABLE_MOMENTS_FIELDS, []

    by_id = {r["wrestler_id"]: r for r in w_rows}

    # ---- new sources -----------------------------------------------------
    s_rows.append({
        "source_id": "S136",
        "source_name": "Wikipedia (English), Royal Rumble (1993)-(1996) event articles",
        "source_type": "reference_site",
        "url": "",
        "reliability_tier": "10",
        "tier_label": "Wikipedia/reference sites",
        "accessed_date": "2026-09-18",
        "notes": ("1993-1996 sweep batch 2. Used for event-level facts and the Free-For-All pre-show "
                  "detail. Continues the per-year-range convention of S026 (1988-1992)."),
    })
    s_rows.append({
        "source_id": "S137",
        "source_name": "WWE.com -- Jimmy Del Ray tribute article; Yokozuna Hall of Fame class pages",
        "source_type": "official_wwe",
        "url": "",
        "reliability_tier": "1",
        "tier_label": "WWE / official sources",
        "accessed_date": "2026-09-18",
        "notes": "1993-1996 sweep batch 2 deceased-status audit.",
    })
    s_rows.append({
        "source_id": "S138",
        "source_name": "whatculture.com, \"10/7 Fascinating/Things Fans Should Know\" Royal Rumble article series (1993/1996 installments)",
        "source_type": "reputable_publication",
        "url": "",
        "reliability_tier": "9",
        "tier_label": "Contemporary wrestling publication",
        "accessed_date": "2026-09-18",
        "notes": ("1993-1996 sweep batch 2. Treated as ONE reusable source across its several "
                  "per-year installments, same convention as S022/S134."),
    })

    # ---- (1) deceased-status + HOF audit -----------------------------------
    fixes = {
        "bam-bam-bigelow": {"deceased_date": "2007-01-19"},
        "king-kong-bundy":  {"deceased_date": "2019-03-04"},
        "dick-murdoch":     {"deceased_date": "1996-06-15"},
        "owen-hart":        {"deceased_date": "1999-05-23"},
        "vader":            {"deceased_date": "2018-06-18"},
        "jimmy-del-ray":    {"deceased_date": "2014-12-06"},
        "yokozuna":         {"hall_of_fame_year": "2012"},
    }
    fixed_ids = []
    for wid, f in fixes.items():
        row = by_id[wid]
        for k, v in f.items():
            row[k] = v
        src = set(filter(None, row["source_ids"].split(";")))
        src.add("S022")
        if "hall_of_fame_year" in f:
            src.add("S137")
        else:
            src.update(["S137"] if wid == "jimmy-del-ray" else ["S136"])
        row["source_ids"] = ";".join(sorted(src))
        fixed_ids.append(wid)
    assert len(fixed_ids) == 7

    counter = 344
    flags.append({
        "flag_id": f"F{counter:03d}",
        "event_id": "",
        "table": "wrestlers",
        "record_id": ";".join(fixed_ids),
        "field": "deceased_date;hall_of_fame_year",
        "issue_type": "corrected",
        "description": (
            "1993-1996 fact-check sweep, continuing the deceased-status audit from batch 1 "
            "(F339-F341): 6 more wrestlers confirmed deceased with a blank deceased_date -- Bam Bam "
            "Bigelow (2007-01-19), King Kong Bundy (2019-03-04), Dick Murdoch (1996-06-15, whose own "
            "row notes already said 'Deceased (per S031)' without the date field ever being filled "
            "in), Owen Hart (1999-05-23; confirmed NOT a WWE Hall of Famer, a genuine documented "
            "case, so hall_of_fame_year intentionally left blank), Vader (2018-06-18), and Jimmy Del "
            "Ray (2014-12-06, per WWE.com's own tribute article). Also added Yokozuna's 2012 Hall of "
            "Fame induction (WWE.com), missing despite his deceased_date already being correct. "
            "Checked but explicitly NOT changed: this database's 'doink'/'doink-1995' wrestler_ids "
            "are, per existing flags F095/F096, a different performer (Ray Apollo/Ray Licameli) than "
            "Matt Borne (d. 2013) -- no evidence of Ray Apollo's death was found, so left alone rather "
            "than wrongly conflated. Great Kabuki, Headshrinker Sione, Jacob Blu/Don Harris, and The "
            "Headhunters were also checked with no death evidence found."
        ),
        "source_ids_involved": "S022;S136;S137",
        "status": "resolved",
        "date_logged": "2026-09-18",
    })
    counter += 1

    # ---- (2) notable_moments additions -------------------------------------
    nm_rows.append({
        "moment_id": "NM006",
        "event_id": "RR1993M",
        "wrestler_ids_involved": "the-undertaker",
        "category": "controversy",
        "title": "Giant Gonzalez interrupted the match to attack The Undertaker -- without ever officially entering it",
        "description": (
            "Giant Gonzalez ran in partway through RR1993M and attacked The Undertaker, causing his "
            "elimination, despite never being an official Rumble entrant (this database's own source "
            "S027 explicitly excludes him from the active-wrestler ring-crowdedness count). Modeled in "
            "this database as a real eliminator credit -- a genuinely unusual case, distinct from every "
            "other year's 'illegally-assisted' eliminations, since those always involved a listed "
            "entrant. See flags.csv F053 for the full treatment."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S027;S028",
        "notes": "Already documented in this database's events.csv prose and F053 -- surfaced here for the notable_moments panel rather than newly researched.",
    })
    nm_rows.append({
        "moment_id": "NM007",
        "event_id": "RR1996M",
        "wrestler_ids_involved": "duke-droese;hunter-hearst-helmsley",
        "category": "storyline_moment",
        "title": "A Free-For-All pre-show match decided who got entry #1 and who got #30",
        "description": (
            "In the first-ever WWF pay-per-view Free-For-All pre-show, Duke Droese faced Hunter "
            "Hearst Helmsley with Rumble entry position on the line: the winner would get the final "
            "#30 spot, the loser would have to enter first at #1. Helmsley pinned Droese, but WWF "
            "president Gorilla Monsoon reversed the decision and disqualified Helmsley for using "
            "brass knuckles -- handing Droese the win and the coveted late entry. Matches this "
            "database's own already-CONFIRMED entry numbers exactly (Droese #30, Helmsley #1)."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S136;S138",
        "notes": "2 independent sources agree; cross-validated against this database's own entrants.csv entry_number values for both wrestlers.",
    })
    flags.append({
        "flag_id": f"F{counter:03d}",
        "event_id": "RR1993M;RR1996M",
        "table": "notable_moments",
        "record_id": "NM006;NM007",
        "field": "n/a",
        "issue_type": "corrected",
        "description": (
            "Added 2 more notable_moments.csv rows for the 1993-1996 batch: RR1993M's Giant Gonzalez "
            "interloper elimination (surfacing existing, already-sourced content into the new table) "
            "and RR1996M's Free-For-All pre-show match that set entry #1/#30 (newly researched, "
            "2 independent sources, cross-validated against this database's own entry numbers). "
            "3 new sources (S136-S138)."
        ),
        "source_ids_involved": "S027;S028;S136;S138",
        "status": "resolved",
        "date_logged": "2026-09-18",
    })

    save("wrestlers.csv", w_fields, w_rows)
    save("sources.csv", s_fields, s_rows)
    save("flags.csv", flag_fields, flags)
    save("notable_moments.csv", nm_fields, nm_rows)

    print(f"Updated {len(fixed_ids)} wrestlers.csv rows (deceased-status + HOF audit).")
    print("Added 2 notable_moments.csv rows (NM006-NM007).")
    print("Added 3 new sources (S136-S138), 2 new flags.")


if __name__ == "__main__":
    main()
