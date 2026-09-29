#!/usr/bin/env python3
"""
Creates data/notable_moments.csv (schema added to scripts/schema.py as
NOTABLE_MOMENTS_FIELDS) and populates it with the first batch of findings --
the "weird and wonderful" trivia from the 1989-1992 fact-check sweep that
doesn't reduce to a single leaderboard number, so it never had anywhere to
go before now. See IDEAS.md's "exhaustive stats" brief for why this table
exists and what it's for; weapons_incidents.csv and a promotion_at_event
field remain separate, still-unbuilt ideas for more structured findings.

Five entries this batch, all from RR1991M/RR1992M (nothing surfaced yet for
1989/1990 at this depth -- worth another look on a future pass, not
invented here):

  1. RR1991M -- Andre the Giant advertised for the match for weeks, then
     quietly withdrawn ~3 weeks out over health concerns. CONFIRMED: 2
     independent sources agree (Wrestling Inc.'s interview with Bruce
     Prichard, who was there; cultaholic's own separate research).
  2. RR1991M -- Brian Knobbs entered as a late substitute for The Honky
     Tonk Man, who had quit the company weeks earlier. CONFIRMED: 2
     independent sources agree (cultaholic; softwolves.pp.se's long-
     standing fan-maintained WWF substitutions reference).
  3. RR1992M -- Three wrestlers expected for the match missed it for very
     different real-life reasons, replaced by Haku and Nikolai Volkoff:
     Brian Knobbs was stabbed in a road-rage incident 2 weeks prior; Bret
     Hart was written out via a kayfabe 104-degree-fever storyline; Marty
     Jannetty was written out after the Shawn Michaels Superkick angle.
     The Knobbs stabbing is CONFIRMED by 2 independent sources agreeing
     (cultaholic; softwolves.pp.se, which adds specific detail -- stabbed
     4 times by 3 fans on 1992-01-05 in Peoria, IL, alongside Jerry Sags
     and IRS). The REASON for Jannetty's absence is a genuine, preserved
     disagreement: cultaholic frames it as a storyline write-out,
     softwolves.pp.se instead says he "was actually fired" -- both kept in
     the description rather than picking one, kept CONFLICTING.
  4. RR1991M -- Rick Martel's 52:30 survival (already this database's own
     CONFIRMED elimination_clock_time for his elimination, sourced
     S018/S019/S026) was, per cultaholic, the first time any wrestler had
     surpassed the 50-minute mark in Royal Rumble history -- broken the
     very next year by Ric Flair's 59:31 (already documented in
     events.csv's own RR1992M notes). The underlying time is CONFIRMED
     elsewhere in this database already; the "first to pass 50 minutes"
     superlative framing itself is single-sourced this pass, kept
     PROBABLE.
  5. RR1992M -- Per cultaholic, WWE re-recorded the commentary track after
     the fact for Sid Justice's elimination of Hulk Hogan, dubbing in a
     more negative crowd reaction and having Gorilla Monsoon call Sid a
     "thief in the night" -- allegedly overriding what was actually a more
     positive live crowd reaction. Single-sourced this pass (no second,
     independent source found) -- kept PROBABLE/flagged rather than
     asserted as settled, and logged as its own flag so it's visible as
     needing a second source before being treated as solid.

New sources: S133 (Wrestling Inc., specifically the Bruce Prichard
interview on Andre's 1991 withdrawal), S134 (cultaholic.com's "10 Things We
Learned From WWE Royal Rumble" article series -- reusable across the
1990/1991/1992 installments, same convention as S022/S024), S135
(softwolves.pp.se's long-standing fan-maintained WWF/WWE substitutions
reference page).

Usage:
    python3 build_notable_moments_table.py [data_dir]   (default: data)
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
    s_fields, s_rows = load("sources.csv")
    flag_fields, flags = load("flags.csv")

    s_rows.append({
        "source_id": "S133",
        "source_name": "Wrestling Inc. -- Bruce Prichard interview on Andre the Giant's 1991 Royal Rumble withdrawal",
        "source_type": "reputable_publication",
        "url": "",
        "reliability_tier": "9",
        "tier_label": "Contemporary wrestling publication",
        "accessed_date": "2026-09-18",
        "notes": "notable_moments.csv seed batch. First-hand account from a WWE producer who was there at the time.",
    })
    s_rows.append({
        "source_id": "S134",
        "source_name": "cultaholic.com, \"10 Things We Learned From WWE Royal Rumble\" article series (1990/1991/1992 installments)",
        "source_type": "reputable_publication",
        "url": "",
        "reliability_tier": "9",
        "tier_label": "Contemporary wrestling publication",
        "accessed_date": "2026-09-18",
        "notes": "notable_moments.csv seed batch. Treated as ONE reusable source across its several per-year installments, same convention as S022/S024.",
    })
    s_rows.append({
        "source_id": "S135",
        "source_name": "softwolves.pp.se, WWF/WWE Royal Rumble substitutions reference page",
        "source_type": "wrestling_database",
        "url": "",
        "reliability_tier": "12",
        "tier_label": "Other reputable site",
        "accessed_date": "2026-09-18",
        "notes": "notable_moments.csv seed batch. A long-standing, fan-maintained reference specifically tracking advertised-vs-actual Rumble entrants and why substitutions happened; used as independent corroboration for the 1991/1992 substitution stories.",
    })

    moments = [
        {
            "moment_id": "NM001",
            "event_id": "RR1991M",
            "wrestler_ids_involved": "andre-the-giant",
            "category": "notable_absence_or_substitution",
            "title": "Andre the Giant advertised, then quietly withdrawn over health concerns",
            "description": (
                "Andre the Giant was advertised for RR1991M for several weeks before his name was "
                "removed without public explanation, roughly 3 weeks before the event. WWE producer "
                "Bruce Prichard later explained it was purely health-driven: \"It was health issues, "
                "it was the thought that we're not going to get Andre beyond this. Even bringing him "
                "out at number 30 wouldn't have been pretty.\""
            ),
            "data_quality_status": "CONFIRMED",
            "source_ids": "S133;S134",
            "notes": "2 independent sources agree on both the advertised-then-pulled fact and the health rationale.",
        },
        {
            "moment_id": "NM002",
            "event_id": "RR1991M",
            "wrestler_ids_involved": "brian-knobbs;the-honky-tonk-man",
            "category": "notable_absence_or_substitution",
            "title": "Brian Knobbs entered as a late substitute for The Honky Tonk Man",
            "description": (
                "The Honky Tonk Man, advertised for RR1991M, had quit the WWF weeks earlier (shortly "
                "after Christmas 1990). Brian Knobbs of The Nasty Boys took his place as a late "
                "substitution."
            ),
            "data_quality_status": "CONFIRMED",
            "source_ids": "S134;S135",
            "notes": "2 independent sources agree.",
        },
        {
            "moment_id": "NM003",
            "event_id": "RR1992M",
            "wrestler_ids_involved": "brian-knobbs;bret-hart;marty-jannetty;haku;nikolai-volkoff",
            "category": "notable_absence_or_substitution",
            "title": "Three expected entrants missed RR1992M for very different real-life reasons",
            "description": (
                "Brian Knobbs, Bret Hart, and Marty Jannetty were all expected for RR1992M but didn't "
                "appear, replaced in the field by Haku and Nikolai Volkoff. Knobbs was stabbed in a "
                "road-rage incident shortly before the event -- per softwolves.pp.se, stabbed 4 times "
                "by 3 fans on 1992-01-05 in Peoria, IL, while driving to a hotel with Jerry Sags and "
                "IRS after a card. Bret Hart's absence was written into the storyline as a 104-degree "
                "fever. Marty Jannetty's reason is a genuine source disagreement, preserved rather than "
                "picked: cultaholic frames it as being written out following the Shawn Michaels "
                "Superkick angle (the start of the real-life Rockers breakup storyline), while "
                "softwolves.pp.se instead says he \"was actually fired\" around this time."
            ),
            "data_quality_status": "CONFLICTING",
            "source_ids": "S134;S135",
            "notes": (
                "Knobbs stabbing: CONFIRMED, 2 independent sources agree (softwolves.pp.se adds "
                "specific corroborating detail). Bret Hart fever storyline: single-sourced (S134). "
                "Jannetty's reason: genuinely CONFLICTING between the 2 sources -- kept as-is per this "
                "database's standard practice rather than guessed at."
            ),
        },
        {
            "moment_id": "NM004",
            "event_id": "RR1991M",
            "wrestler_ids_involved": "rick-martel",
            "category": "milestone_first",
            "title": "Rick Martel's 52:30 was the first Royal Rumble survival to pass 50 minutes",
            "description": (
                "Rick Martel's 52:30 survival time (this database's own CONFIRMED figure for his "
                "elimination by British Bulldog, S018;S019;S026) was, per cultaholic, the first time "
                "any wrestler had passed the 50-minute mark in Royal Rumble history. The record lasted "
                "exactly one year, broken by Ric Flair's 59:31 at RR1992M -- already documented in "
                "events.csv's RR1992M historical_significance field."
            ),
            "data_quality_status": "PROBABLE",
            "source_ids": "S134",
            "notes": (
                "The underlying 52:30 time is CONFIRMED elsewhere in this database already; only the "
                "'first to pass 50 minutes' superlative framing is single-sourced this pass -- kept "
                "PROBABLE pending a second source for that specific claim."
            ),
        },
        {
            "moment_id": "NM005",
            "event_id": "RR1992M",
            "wrestler_ids_involved": "sid-justice;hulk-hogan",
            "category": "behind_the_scenes",
            "title": "Commentary allegedly re-recorded after the fact for Sid Justice's elimination of Hulk Hogan",
            "description": (
                "Per cultaholic, WWE re-recorded RR1992M's commentary track after the event to make "
                "Sid Justice's elimination of Hulk Hogan sound like a cheap shot rather than reflect "
                "the crowd's actual, reportedly more positive live reaction -- with Gorilla Monsoon "
                "dubbed calling Sid a \"thief in the night\" despite Sid's tactics being standard "
                "battle-royal play."
            ),
            "data_quality_status": "PROBABLE",
            "source_ids": "S134",
            "notes": "Single-sourced this pass -- no independent second source found. See flags.csv F342.",
        },
    ]

    save("notable_moments.csv", NOTABLE_MOMENTS_FIELDS, moments)
    save("sources.csv", s_fields, s_rows)

    counter = 342
    flags.append({
        "flag_id": f"F{counter:03d}",
        "event_id": "",
        "table": "notable_moments",
        "record_id": "",
        "field": "n/a",
        "issue_type": "corrected",
        "description": (
            "Built notable_moments.csv (schema added to scripts/schema.py) per Shane's go-ahead, to "
            "hold the 'weird and wonderful' trivia findings from the fact-check sweep that don't "
            "reduce to a single leaderboard number -- see IDEAS.md's 'exhaustive stats' brief. Seeded "
            "with the first 5 findings from the 1989-1992 sweep (NM001-NM005): Andre the Giant's "
            "advertised-then-withdrawn 1991 appearance, Brian Knobbs's 1991 late substitution for "
            "Honky Tonk Man, three 1992 absences/substitutions (Knobbs stabbed, Hart's kayfabe fever, "
            "Jannetty written out/fired), Rick Martel's first-ever 50+ minute survival, and the "
            "reported re-recorded 1992 commentary for Sid Justice's elimination of Hulk Hogan. "
            "3 new sources (S133-S135)."
        ),
        "source_ids_involved": "S133;S134;S135",
        "status": "resolved",
        "date_logged": "2026-09-18",
    })
    counter += 1
    flags.append({
        "flag_id": f"F{counter:03d}",
        "event_id": "RR1992M",
        "table": "notable_moments",
        "record_id": "NM005",
        "field": "description",
        "issue_type": "unverified",
        "description": (
            "The 'WWE re-recorded RR1992M's commentary track' claim (NM005) is single-sourced this "
            "pass (cultaholic only) -- no second independent source was found confirming the specific "
            "re-recording/dubbing claim, as opposed to the more general (and well-documented) fact "
            "that Sid Justice's win was booked as a heel turn. Kept at PROBABLE rather than CONFIRMED. "
            "Worth another look with a play-by-play source or, ideally, a direct footage comparison if "
            "a video tool becomes available."
        ),
        "source_ids_involved": "S134",
        "status": "open",
        "date_logged": "2026-09-18",
    })

    save("flags.csv", flag_fields, flags)
    print(f"Created notable_moments.csv with {len(moments)} rows.")
    print("Added 3 new sources (S133-S135), 2 new flags (F342-F343).")


if __name__ == "__main__":
    main()
