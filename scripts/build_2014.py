# -*- coding: utf-8 -*-
"""
Builds all rows for the 2014 Royal Rumble -- schema v2.

Like 2009/2011/2012/2013, Shane's doc has NO "Dan Wahlers History of the
Royal Rumble" chapter for 2014 -- only the "2014 Rumble Stats - Cageside"
frame-by-frame timing analysis. UNLIKE 2013, this year's buzzer list is
FULLY NAMED (28 named buzzers, matching entrants #3-30 directly) -- full
entry order is known with confidence, same rich-year pattern as 2011/2012.

This year ALSO has a substantial bonus section -- "2014 VERY INTERESTING -
Advanced Statistics and Analysis for the WWE Royal Rumble" -- written by a
different guest analyst (distinct from the regular Cageside author), who
rewatched full match footage and logged 706 individual events (entrances,
strikes, grapple moves, elimination attempts) to build a partial-credit
elimination system, defense/maneuver/finisher breakdowns, and an
actions-per-minute "rest and relaxation" analysis. Most of this is
aggregate/statistical rather than individually attributable, but it DOES
directly name two things useful here: (1) Kane's only elimination
attempt in the tracked data was against CM Punk, and it succeeded (with
the analyst's own caveat that Kane was already-eliminated at the time);
(2) Sheamus's only successful elimination was Big E (matching the main
Cageside text's separate direct statement).

SOURCES CONSULTED THIS PASS:
  S104 '2014 Rumble Stats - Cageside' section (Shane's doc)             tier 9
  S105 '2014 VERY INTERESTING - Advanced Statistics and Analysis' guest
       analyst section (Shane's doc)                                    tier 9
  S102 'SE Scoops' winner/entry-number list (already registered for 2013 --
       reused here; also covers 2014: "Batista, entered at number 28")
  S103 'WrestlingInc' trivia article (already registered for 2013 --
       reused here; also covers 2014 facts, e.g. Kane's career-eliminations
       record claim)

METHODOLOGY: entry_actual[name] = cumulative buzzer-gap time (all 28
buzzers are named this year, unlike 2013) + entrance_lag[name]. CM Punk
and Seth Rollins (the first two entrants) both start at entry_actual=0
(pre-bell, no buzzer, per S104's own explicit statement). elim_ts[name] =
entry_actual[name] + survival_time[name].

Checksums (all verified before writing this script):
  - The cumulative buzzer sum across all 28 buzzers lands exactly on the
    doc's own stated actual final-buzzer mark of 45:23 (vs. a "perfectly
    timed" theoretical 42:00 the doc itself calls out as a comparison).
  - Batista's (the winner's) own entry_actual + his own stated 12:52
    survival time lands EXACTLY on the match total (55:09) -- the
    signature of the winning, never-eliminated wrestler. Also matches 2
    independent trivia sources found elsewhere in Shane's document (S102:
    "Batista, entered at number 28"; the doc's own aside on Batista's
    career entry-number history, "28, 28, 8, 30, 28", where the final "28"
    is 2014) confirming he is entrant #28.
  - Roman Reigns's own elim_ts, computed the same way, ALSO lands exactly
    on the match total (55:09) -- meaning he is the runner-up, the
    winning elimination. This matches S104's own direct prose ("This
    match featured Roman Reigns tossing out 12 superstars with ease
    before falling victim to Batista").
  - The doc's own 3 grouped elimination-window statements ("X, Y, and Z
    were eliminated in the waiting period between A and B's entrances")
    are fully consistent with this script's own computed elim_ts
    ordering in every case -- each named trio comes out as 3 consecutive,
    tightly-clustered elim_ts values with no other entrant's elim_ts
    falling between them. Strong independent validation of the whole
    derivation chain.
  - "Not Daniel Bryan" (buzzer 28/entrant #30) is resolved to Rey Mysterio
    -- S104's own closing recap explicitly lists the final-entrant-onward
    "10-man Battle Royal to the finish" as "Punk, Rollins, Ambrose,
    Reigns, Sheamus, Cesaro, Harper, Batista, Langston, and Mysterio,"
    naming Mysterio as one of exactly 10 remaining once the 30th (final)
    entrant arrives -- i.e. Mysterio IS that 30th entrant. (Real-world
    context, not itself load-bearing here: fans had been led to expect a
    surprise Daniel Bryan entrance at #30 and reacted badly when it
    turned out to be Mysterio instead -- "Not Daniel Bryan" is the doc
    author's own wry label for the slot, not a wrestler's ring name.)

NAMED ELIMINATIONS THIS YEAR:
  - Kane <- CM Punk (S104, direct: "Kane was eliminated by Punk") -- early,
    matches Kane's own short 0:56 survival time.
  - Big E (Langston) <- Sheamus (S104, direct: "Sheamus...succeeded in
    eliminating Big E"; independently corroborated by S105's defense
    analysis, which separately confirms this was Sheamus's only credited
    elimination all match).
  - Roman Reigns <- Batista (S104, direct + checksum) -- the winning
    elimination.
  - CM Punk <- Kane (S105 only, guest analyst's tracked-event data: "Kane
    actually had a 100% elimination percentage, having only attempted to
    eliminate CM Punk and succeeding" -- NOTE the analyst's own caveat,
    "I believe his percentage should be disqualified due to his already
    being eliminated at the time of his attempt." This does NOT
    contradict Kane's own early elimination by Punk above -- it describes
    a SEPARATE, later event: Kane, already eliminated at 5:44, returned
    to interfere from ringside during Punk's own elimination near the
    match's end (49:15). Modeled as a shared/partial credit (is_shared=
    TRUE, PROBABLE) since Punk's elimination at that late, crowded stage
    of the match almost certainly involved other named opponents too,
    none of whom S105 individually identifies -- see F278.
All other elimination-eligible entrants have no individually named
eliminator this pass -- left UNKNOWN rather than guessed.

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order and survival time are known to the second for ALL 30
    entrants -- the richest year built so far for this project's
    "no-Wahlers-chapter" era, matching 2012's completeness plus a bonus
    statistical-analysis layer 2012 didn't have.
  - 4 named eliminations (see above), richer than 2013 (zero) though not
    as individually rich as 2012 (8).
  - Event-level facts (attendance, venue, exact date, commentary,
    referees, undercard) are UNKNOWN -- no Wahlers chapter exists for
    this year. event_date stored as '2014-XX-XX', same convention as
    2009/2011/2012/2013.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from schema import (
    ENTRANTS_FIELDS, ELIMINATIONS_FIELDS, EVENTS_FIELDS,
    slugify, mmss_to_seconds,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EVENT_ID = "RR2014M"


def mmss(t):
    parts = [int(p) for p in t.split(":")]
    return parts[0] * 60 + parts[1] if len(parts) == 2 else parts[0] * 3600 + parts[1] * 60 + parts[2]


def secs_to_mmss(s):
    m, sec = divmod(int(s), 60)
    return f"{m}:{sec:02d}"


# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S104", "'2014 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-17",
     "Frame-by-frame-style timing analysis (survival times, entrance times, FULLY NAMED time-between-buzzers -- "
     "unlike 2013 -- ring crowdedness) filed under the '2014 Royal Rumble Stats' Heading-1. NO separate Dan "
     "Wahlers narrative history chapter exists for this year. Directly narrates 3 individual eliminations plus "
     "3 grouped elimination-window statements. NOT live-fetched this pass."),
    ("S105", "'2014 VERY INTERESTING - Advanced Statistics and Analysis for the WWE Royal Rumble' guest-analyst section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-17",
     "A different author from the regular Cageside writer, who rewatched full match footage and logged 706 "
     "individual in-match events to build a partial-credit elimination system (total re-derived at 29.0 across "
     "all credited/shared eliminations, vs. WWE's/Wikipedia's inflated 34-person count from over-crediting "
     "shared eliminations), elimination-attempt %, defense stats, maneuver-type analysis, time-between-"
     "eliminations, finisher-rate comparison, and per-wrestler actions-per-minute. Mostly aggregate/statistical "
     "rather than individually attributable, but directly names 1 additional elimination (Kane's interference "
     "elimination of CM Punk) not found in S104. NOT live-fetched this pass."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# TIMING DERIVATION
# ---------------------------------------------------------------------------
buzzer_gaps = [
    ("Damien Sandow", "1:31"), ("Cody Rhodes", "1:31"), ("Kane", "1:32"), ("Alexander Rusev", "1:30"),
    ("Jack Swagger", "1:31"), ("Kofi Kingston", "1:32"), ("Jimmy Uso", "1:31"), ("Goldust", "1:30"),
    ("Dean Ambrose", "2:26"), ("Dolph Ziggler", "1:32"), ("R-Truth", "1:31"), ("Kevin Nash", "1:53"),
    ("Roman Reigns", "1:39"), ("The Great Khali", "1:38"), ("Sheamus", "1:41"), ("The Miz", "1:36"),
    ("Fandango", "1:30"), ("El Torito", "1:32"), ("Antonio Cesaro", "2:09"), ("Luke Harper", "1:32"),
    ("Jey Uso", "1:33"), ("John Bradshaw Layfield", "1:30"), ("Erick Rowan", "1:40"), ("Ryback", "1:33"),
    ("Alberto Del Rio", "1:31"), ("Batista", "1:31"), ("Big E. Langston", "1:47"), ("Not Daniel Bryan", "1:31"),
]
buzzer_time = {}
cum = 0
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("45:23"), f"buzzer checksum failed: {cum}"

# Entrance times. CM Punk and Seth Rollins (pre-bell, the first two
# entrants) are excluded, same treatment as prior years' opening pair.
entrance_lag = {
    "John Bradshaw Layfield": "0:32", "The Great Khali": "0:30", "Kevin Nash": "0:26", "Alexander Rusev": "0:24",
    "El Torito": "0:23", "Antonio Cesaro": "0:18", "Luke Harper": "0:18", "Erick Rowan": "0:18",
    "Jack Swagger": "0:17", "Fandango": "0:17", "Roman Reigns": "0:16", "Kane": "0:14",
    "Alberto Del Rio": "0:13", "Dolph Ziggler": "0:12", "Sheamus": "0:12", "Ryback": "0:12", "Batista": "0:12",
    "Dean Ambrose": "0:11", "Cody Rhodes": "0:10", "Kofi Kingston": "0:10", "Goldust": "0:10",
    "Jey Uso": "0:10", "Not Daniel Bryan": "0:10", "Damien Sandow": "0:09",
    "Jimmy Uso": "0:08", "R-Truth": "0:08", "The Miz": "0:08", "Big E. Langston": "0:08",
}
entry_actual = {"CM Punk": 0, "Seth Rollins": 0}
for name in buzzer_time:
    entry_actual[name] = buzzer_time[name] + mmss(entrance_lag[name])

# Survival ("ring") times, as stated directly by S104. Batista (the
# winner) is included with a survival time that is his entry-to-match-end
# span, not an elimination -- excluded from elim_ts below.
survival = {
    "CM Punk": "49:15", "Seth Rollins": "48:33", "Dean Ambrose": "33:49", "Roman Reigns": "33:44",
    "Sheamus": "28:13", "Cody Rhodes": "20:53", "Antonio Cesaro": "16:59", "Luke Harper": "15:04",
    "Batista": "12:52", "Kofi Kingston": "12:33", "Jack Swagger": "12:08", "The Miz": "12:02",
    "Goldust": "11:51", "Jimmy Uso": "7:47", "Alexander Rusev": "6:43", "Dolph Ziggler": "5:58",
    "Erick Rowan": "4:48", "Jey Uso": "4:22", "Ryback": "3:50", "Alberto Del Rio": "2:48",
    "Fandango": "2:46", "Big E. Langston": "2:42", "Kevin Nash": "2:30", "Damien Sandow": "2:08",
    "Not Daniel Bryan": "2:00", "El Torito": "1:27", "Kane": "0:56", "R-Truth": "0:29",
    "The Great Khali": "0:25", "John Bradshaw Layfield": "0:18",
}
assert set(survival) == set(entry_actual), set(survival) ^ set(entry_actual)
assert len(survival) == 30

MATCH_TOTAL = mmss("55:09")
assert entry_actual["Batista"] + mmss(survival["Batista"]) == MATCH_TOTAL

elim_ts = {}
for name, t in survival.items():
    if name == "Batista":
        continue  # winner, never eliminated
    elim_ts[name] = entry_actual[name] + mmss(t)
assert elim_ts["Roman Reigns"] == MATCH_TOTAL, elim_ts["Roman Reigns"]  # the winning elimination, by Batista
# Grouped elimination-window cross-checks (all 3 confirmed consistent):
_ordered = sorted(elim_ts, key=lambda n: elim_ts[n])
assert _ordered.index("Dolph Ziggler") == _ordered.index("Kofi Kingston") + 1
assert _ordered.index("Kevin Nash") == _ordered.index("Dolph Ziggler") + 1
assert _ordered.index("Cody Rhodes") == _ordered.index("The Great Khali") + 1
assert _ordered.index("Goldust") == _ordered.index("Cody Rhodes") + 1
assert _ordered.index("Ryback") == _ordered.index("Erick Rowan") + 1
assert _ordered.index("Alberto Del Rio") == _ordered.index("Ryback") + 1

elim_order_list = sorted(elim_ts, key=lambda n: elim_ts[n])
elim_number = {name: i + 1 for i, name in enumerate(elim_order_list)}
assert elim_number["Damien Sandow"] == 1
assert elim_number["Roman Reigns"] == 29  # the winning elimination, last of 29

ENTRY_NUMBERS = {"CM Punk": 1, "Seth Rollins": 2}
for i, (name, _) in enumerate(buzzer_gaps):
    ENTRY_NUMBERS[name] = i + 3
assert ENTRY_NUMBERS["Damien Sandow"] == 3 and ENTRY_NUMBERS["Not Daniel Bryan"] == 30
assert ENTRY_NUMBERS["Batista"] == 28  # matches S102/S103 and the doc's own career-number aside

FINAL_TWO = {"Batista", "Roman Reigns"}
FINAL_THREE = {"Batista", "Roman Reigns", "Sheamus"}
FINAL_FOUR = {"Batista", "Roman Reigns", "Sheamus", "CM Punk"}

# name -> (eliminator names, data_quality_status, notes, is_shared, group_id)
KNOWN_ELIMINATORS = {
    "Kane": (["CM Punk"], "CONFIRMED",
             "S104 directly states 'Kane was eliminated by Punk.'", False, ""),
    "Big E. Langston": (["Sheamus"], "CONFIRMED",
                          "S104 directly states Sheamus '...succeeded in eliminating Big E.' Independently "
                          "corroborated by S105's defense analysis, which separately identifies this as "
                          "Sheamus's only credited elimination all match.", False, ""),
    "Roman Reigns": (["Batista"], "CONFIRMED",
                       "The winning elimination. S104 directly states this match 'featured Roman Reigns "
                       "tossing out 12 superstars with ease before falling victim to Batista,' and this "
                       "script's own checksum confirms Reigns's elim_ts lands exactly on the match total.",
                       False, ""),
    "CM Punk": (["Kane"], "PROBABLE",
                 "S105 (the guest-analyst 'advanced stats' section, tracking 706 individually-logged in-match "
                 "events) states Kane's only tracked elimination attempt was against CM Punk, and it "
                 "succeeded -- with the analyst's own caveat that this 'should be disqualified due to his "
                 "already being eliminated at the time of his attempt.' This does NOT contradict Kane's own "
                 "early elimination (by Punk, above, at 0:56) -- it describes a SEPARATE, later event: Kane, "
                 "long since eliminated, interfering from ringside during Punk's own elimination near the "
                 "match's end (49:15), a known Rumble trope with precedent elsewhere in this database (e.g. "
                 "RR2012M's Michael Cole). Modeled as shared/partial credit since Punk's elimination at that "
                 "late, crowded stage of the match almost certainly involved other opponents too, none "
                 "individually named by either source this pass. See F278.", True, "punk_elim_group"),
}

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Seth Rollins", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #2 (pre-bell, alongside CM Punk). Survived 48:33, the 2nd-longest survival time of the match. Part of The Shield stable (with Dean Ambrose and Roman Reigns), per S105's aside that 3 of Reigns's partial-credit eliminations were 'a team up of the entire shield.'", "S104;S105"),
    ("Alexander Rusev", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "Rusev", "", "Rumble debut, entered #6. Survived 6:43. Billed as 'Alexander Rusev' at this event; stored under the name-stable wrestler_id 'rusev' since that is how this performer became known from later in 2014 onward, matching this database's established precedent (e.g. Steve Austin/Ringmaster, 1996).", "S104"),
    ("Jimmy Uso", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #9. Survived 7:47. Twin brother of Jey Uso (already in this database, RR2012M) -- both competed in this match as separate entrants.", "S104"),
    ("Dean Ambrose", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #11. Survived 33:49, the 3rd-longest survival time of the match. Part of The Shield stable (with Seth Rollins and Roman Reigns).", "S104;S105"),
    ("Roman Reigns", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #15. Survived 33:44, the 4th-longest survival time of the match. Eliminated by Batista in the match's final second -- the winning elimination. S104's own headline framing credits him with 12 eliminations, but S105's guest-analyst partial-credit re-analysis (706 individually logged events) puts his TRUE credit at 9.5 -- 3 of his 12 broadcast-credited eliminations were a 3-way Shield team-up (shared with Ambrose/Rollins) and 1 was shared with Batista, so under an even-split system he does not actually set a new single-match record over Kane's 2001 performance (recalculated by the same analyst at 10.5). See F277.", "S104;S105"),
    ("Fandango", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #19. Survived 2:46.", "S104"),
    ("El Torito", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #20 -- a comic-relief 'mascot' entrant (Los Matadores' diminutive tag partner). Survived just 1:27; S104 notes his spots with Punk, Fandango, and Reigns extended the countdown to Cesaro's entrance to 2:09, the match's 2nd-longest buzzer gap.", "S104"),
    ("Luke Harper", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #22. Survived 15:04.", "S104"),
    ("Erick Rowan", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #25. Survived 4:48.", "S104"),
    ("Big E. Langston", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "Big E", "", "Rumble debut, entered #29. Survived just 2:42 with no eliminations to his credit -- S104 calls this 'the most disappointing Royal Rumble performance out of everyone relative to expectations.' Eliminated by Sheamus. Billed as 'Big E. Langston' at this event; stored under the name-stable wrestler_id 'big-e' since that is how this performer became known from later in 2014 onward, matching this database's established precedent.", "S104"),
]

reused = {
    "CM Punk": "cm-punk", "Damien Sandow": "damien-sandow", "Cody Rhodes": "cody-rhodes", "Kane": "kane",
    "Jack Swagger": "jack-swagger", "Kofi Kingston": "kofi-kingston", "Goldust": "goldust",
    "Dolph Ziggler": "dolph-ziggler", "R-Truth": "r-truth", "The Great Khali": "the-great-khali",
    "Sheamus": "sheamus", "The Miz": "the-miz", "Antonio Cesaro": "cesaro", "Jey Uso": "jey-uso",
    "Ryback": "ryback", "Alberto Del Rio": "alberto-del-rio", "Batista": "batista",
    "Not Daniel Bryan": "rey-mysterio",
    "Kevin Nash": "diesel", "John Bradshaw Layfield": "bradshaw",
}

wrestler_ids = {}
wrestler_ids.update(reused)
# Force name-stable wrestler_ids for 2 new-this-year performers whose ring
# name at this event differs from the name they became far better known
# by later -- WITHOUT this, slugify() would produce "alexander-rusev" and
# "big-e-langston" instead of the intended "rusev"/"big-e" (this bug was
# caught and fixed post-deploy -- see F280's note and the live-database
# wrestler_id rename applied before the 2015 build).
wrestler_ids["Alexander Rusev"] = "rusev"
wrestler_ids["Big E. Langston"] = "big-e"

with open(os.path.join(DATA_DIR, "wrestlers.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in new_wrestlers:
        ring_name = row[0]
        wid = wrestler_ids.get(ring_name) or slugify(ring_name)
        wrestler_ids[ring_name] = wid
        writer.writerow([wid] + list(row))

# ---------------------------------------------------------------------------
# ENTRANTS -- all 30, full entry order and survival time known.
# ---------------------------------------------------------------------------
all_names = [
    "CM Punk", "Seth Rollins", "Damien Sandow", "Cody Rhodes", "Kane", "Alexander Rusev", "Jack Swagger",
    "Kofi Kingston", "Jimmy Uso", "Goldust", "Dean Ambrose", "Dolph Ziggler", "R-Truth", "Kevin Nash",
    "Roman Reigns", "The Great Khali", "Sheamus", "The Miz", "Fandango", "El Torito", "Antonio Cesaro",
    "Luke Harper", "Jey Uso", "John Bradshaw Layfield", "Erick Rowan", "Ryback", "Alberto Del Rio",
    "Batista", "Big E. Langston", "Not Daniel Bryan",
]
assert len(all_names) == 30

DISPLAY_NAME = {"Not Daniel Bryan": "Rey Mysterio"}

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Batista")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, dq, method, is_shared, group_id = KNOWN_ELIMINATORS.get(name, ([], "", "", False, ""))

    notes_parts = []
    if name == "Batista":
        notes_parts.append("Entered #28 and won his 3rd career Royal Rumble, eliminating Roman Reigns in the match's final second. Per S104's own aside, Batista's entrance numbers across his career Royal Rumble matches have been 28, 28, 8, 30, 28 -- his 2014 draw matched his very first (2005) and 2nd (2006) draws exactly.")
    elif name == "Roman Reigns":
        notes_parts.append("Eliminated by Batista in the match's final second -- the winning elimination, and the runner-up spot. See wrestlers.csv notes and F277 for the broadcast-credited-12-vs-recalculated-9.5 eliminations discrepancy.")
    elif name == "Not Daniel Bryan":
        notes_parts.append("S104 labels this slot 'Not Daniel Bryan' rather than naming the entrant directly -- resolved to Rey Mysterio via S104's own closing recap, which names him as one of exactly 10 wrestlers remaining once the 30th (final) entrant arrives. See F276.")
    elif name == "Kane":
        notes_parts.append("Eliminated early by CM Punk (0:56 survival). Per S105, Kane later returned to ringside and is credited (PROBABLE, partial/shared credit) with contributing to CM Punk's own elimination near the match's end -- see F278. Michael Cole stated on commentary this was Kane's '15th consecutive' Rumble, but S104 notes this is incorrect: Kane fought John Cena in a singles match at the 2012 Royal Rumble event and did not compete in that year's Rumble match itself -- consistent with this database's own RR2012M build, which does not include Kane as an entrant.")
    elif name == "CM Punk":
        notes_parts.append("Entered #1 (pre-bell). Survived 49:15, the longest of the match -- per S104, the 4th consecutive year the #1 entrant became this match's 'Iron Man' (longest survivor), and Punk's 2nd time doing so himself (also 2013's Iron Man on a note in this database's RR2013M -- see events.csv notes there for a partial parallel, though 2013's Iron Man was Ziggler at #1, not Punk). See Kane note above for his eventual elimination.")
    if name == "Big E. Langston":
        notes_parts.append("Sheamus's only credited elimination this match, per both S104 and S105.")
    note = " ".join(notes_parts)

    for eliminator in elim_by:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": elim_number[name],
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
            "assisting_wrestler_ids": ";".join(wrestler_ids[e] for e in elim_by if e != eliminator) if is_shared else "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": ENTRY_NUMBERS.get(eliminator, ""),
            "elimination_clock_time": secs_to_mmss(elim_ts[name]),
            "elimination_clock_seconds": elim_ts[name],
            "elimination_type": "over_top_rope",
            "elimination_method": method,
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "FALSE" if is_shared else "TRUE", "is_shared": "TRUE" if is_shared else "FALSE",
            "is_accidental": "FALSE",
            "is_self_elimination": "FALSE",
            "is_storyline_related": "UNKNOWN",
            "was_already_incapacitated": "TRUE" if name == "CM Punk" else "UNKNOWN",
            "is_disputed": "FALSE",
            "simultaneous_group_id": group_id,
            "data_quality_status": dq,
            "source_ids": "S104;S105" if name == "CM Punk" else "S104",
            "notes": "Kane was himself already eliminated at 0:56 by the time of this credited assist -- see F278." if name == "CM Punk" else "",
        })

    er = {
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": "CONFIRMED",
        "ring_name_at_time": DISPLAY_NAME.get(name, name), "name_displayed_at_event": DISPLAY_NAME.get(name, name),
        "prior_rumble_appearances_count": "", "rumble_appearance_no": "",
        "is_first_rumble_appearance": "", "previous_rumble_year": "",
        "previous_rumble_result": "", "previous_rumble_elimination_no": "",
        "is_rumble_debut": "", "is_company_debut": "UNKNOWN", "company_debut_date": "",
        "is_returning_wrestler": "", "absence_length": "",
        "age_at_event": "", "age_status": "UNKNOWN",
        "billed_height_m_at_event": "", "billed_weight_kg_at_event": "", "billed_from_at_event": "",
        "physical_status": "UNKNOWN",
        "alignment": "", "alignment_status": "UNKNOWN",
        "gimmick_at_event": "",
        "manager_at_event": "",
        "tag_team_name": "",
        "faction_stable": "The Shield" if name in ("Seth Rollins", "Dean Ambrose", "Roman Reigns") else "",
        "current_champion_title": "", "championship_level": "", "championship_partner": "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        "title_defended_same_card": "FALSE", "title_lost_same_card": "FALSE",
        "elim_number": "" if is_winner else elim_number[name], "elim_number_status": "N/A" if is_winner else "CONFIRMED",
        "eliminated_by_ids": ";".join(wrestler_ids[e] for e in elim_by),
        "elimination_clock_time": "" if is_winner else secs_to_mmss(elim_ts[name]),
        "elimination_clock_seconds": "" if is_winner else elim_ts[name],
        "ring_time": ring_time, "ring_time_seconds": ring_time_s,
        "ring_time_status": "CONFIRMED",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if name == "Roman Reigns" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "TRUE" if name == "Not Daniel Bryan" else "FALSE",
        "legend_returning": "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE",
        "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S104;S105",
        "notes": note,
    }
    entrant_rows.append(er)

# Fill in each eliminator's wrestlers_eliminated_ids / counts from elim_rows.
elim_credit = {}
for row in elim_rows:
    elim_credit.setdefault(row["eliminator_wrestler_id"], []).append(row["eliminated_wrestler_id"])
for er in entrant_rows:
    credited = elim_credit.get(er["wrestler_id"], [])
    if credited:
        er["wrestlers_eliminated_count"] = len(credited)
        er["wrestlers_eliminated_ids"] = ";".join(credited)
        er["solo_eliminations_count"] = sum(1 for r in elim_rows if r["eliminator_wrestler_id"] == er["wrestler_id"] and r["is_solo"] == "TRUE")
        er["assisted_eliminations_count"] = sum(1 for r in elim_rows if r["eliminator_wrestler_id"] == er["wrestler_id"] and r["is_solo"] == "FALSE")

with open(os.path.join(DATA_DIR, "entrants.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ENTRANTS_FIELDS)
    for er in entrant_rows:
        writer.writerow(er)

with open(os.path.join(DATA_DIR, "eliminations.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ELIMINATIONS_FIELDS)
    for row in elim_rows:
        writer.writerow(row)

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F274", EVENT_ID, "events", EVENT_ID, "event_date;venue;attendance_reported;commentary_team;referees", "unverified",
     "Like 2009/2011/2012/2013, Shane's document has NO separate Dan Wahlers narrative history chapter for 2014 "
     "-- only the Cageside timing analysis (plus this year's bonus advanced-stats section, neither of which "
     "covers event-level logistics). Event-level facts (exact date, venue, city, attendance, commentary team, "
     "referees, undercard results) are simply absent from the source and left entirely UNKNOWN this pass. "
     "event_date is stored as '2014-XX-XX' -- the year itself is not in doubt, only the exact month/day are "
     "unconfirmed. Pending a future external-research pass.",
     "S104", "open", "2026-09-17"),
    ("F275", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "4 of 29 eliminations (excluding the winner) have an individually named eliminator this pass (3 from S104, "
     "1 from S105) -- richer than 2013 (zero) but less rich than 2012 (8). The remaining 25 elimination-eligible "
     "entrants have no named eliminator this pass. Left UNKNOWN rather than guessed.",
     "S104;S105", "open", "2026-09-17"),
    ("F276", EVENT_ID, "entrants", "rey-mysterio", "ring_name_at_time", "needs_human_judgement",
     "S104 never names entrant #30 directly -- it labels the slot 'Not Daniel Bryan' (its own wry commentary on "
     "the fact that fans widely expected a surprise Daniel Bryan return at #30 and were instead given a "
     "different wrestler). Resolved to Rey Mysterio via S104's own separate closing recap, which lists the "
     "final 10-man stretch as 'Punk, Rollins, Ambrose, Reigns, Sheamus, Cesaro, Harper, Batista, Langston, and "
     "Mysterio' -- exactly 10 names for the 10 wrestlers remaining once the 30th entrant arrives, with Mysterio "
     "being the only one of those 10 not otherwise already accounted for elsewhere in the buzzer/survival data. "
     "High confidence, but flagged for a future external-research pass to confirm directly (e.g. Wikipedia's "
     "own named entrant table for this event).",
     "S104", "open", "2026-09-17"),
    ("F277", EVENT_ID, "wrestlers", "roman-reigns;kane", "notes", "conflicting_sources",
     "S104's own headline framing credits Roman Reigns with 12 eliminations in this match (widely reported "
     "elsewhere, e.g. Wikipedia's cited 34-person combined elimination count for the whole match, which S105 "
     "explicitly disputes as internally impossible -- 'the math doesn't add up' -- since only 29 eliminations "
     "occurred and shared credits get double/triple counted by naive tallying). S105, a separate guest analyst "
     "who individually tracked all 706 in-match events and split credit evenly on every shared elimination, "
     "recalculates Reigns's TRUE total at 9.5 (3 of his 12 were a 3-way Shield team-up, 1 shared with Batista) "
     "and Kane's 2001 total (recalculated the same way) at 10.5 -- meaning Reigns does NOT actually set a new "
     "single-match elimination record, contrary to how the moment was broadcast/covered. This database records "
     "both figures (S104's 12 and S105's 9.5) in wrestlers.csv notes rather than picking one, since they reflect "
     "two different, both-legitimate counting methodologies (broadcast-style full-credit vs. analyst-style "
     "split-credit) rather than a factual disagreement about what happened.",
     "S104;S105", "open", "2026-09-17"),
    ("F278", EVENT_ID, "eliminations", "cm-punk", "eliminator_wrestler_id", "needs_human_judgement",
     "CM Punk's credited eliminator (Kane, PROBABLE, shared) comes from S105 alone -- a guest analyst's "
     "tracked-event data, with the analyst's own explicit caveat that this credit 'should be disqualified due "
     "to his [Kane's] already being eliminated at the time of his attempt' (Kane's own elimination, by Punk, "
     "happened at 0:56 -- see the separate CONFIRMED elimination row for that). Modeled as a SHARED credit "
     "(is_shared=TRUE) since Punk's own elimination, occurring at 49:15 in a heavily crowded late-match "
     "situation (Rollins, Ambrose, Reigns, Sheamus, Cesaro, Harper, Batista, Mysterio all still active), "
     "almost certainly involved other opponents too -- none individually named by either source this pass. "
     "Pending a future external-research pass to identify the rest of the group, if recoverable.",
     "S105", "open", "2026-09-17"),
    ("F279", EVENT_ID, "entrants", "xavier-woods", "n/a", "unverified",
     "S104 states 'Xavier Woods was listed as an official entrant but did not get a spot in the match' -- no "
     "entrant row was created for him this pass, since no timing/position/survival data exists for him "
     "anywhere in this year's source (unlike, e.g., 2015's Curtis Axel, who has a defined 0:00 ring_time). "
     "Left as a documented anomaly rather than an entrant row with entirely fabricated blank fields. Pending a "
     "future external-research pass to determine which of this year's 30 named entrants (if any) took his "
     "originally-planned slot.",
     "S104", "open", "2026-09-17"),
    ("F280", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 10 previously-unseen wrestlers this pass (Seth Rollins, Rusev, Jimmy Uso, Dean Ambrose, "
     "Roman Reigns, Fandango, El Torito, Luke Harper, Erick Rowan, Big E) with zero bio data in this pass's "
     "source -- names only. Left entirely UNKNOWN, same pattern as every prior year's equivalent flag. NOTE: "
     "Kevin Nash and John Bradshaw Layfield were NOT added as new wrestlers -- both reused this database's "
     "existing 'diesel' and 'bradshaw' wrestler_ids respectively, since those rows' already-CONFIRMED/PROBABLE "
     "real_name fields (Kevin Scott Nash; John Charles Layfield) match this year's billed ring names exactly.",
     "S104", "open", "2026-09-17"),
    ("F281", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-17"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2014", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2014-XX-XX", "venue": "UNKNOWN",
    "city_region": "UNKNOWN", "country": "UNKNOWN",
    "attendance_official": "", "attendance_reported": "",
    "entry_interval_seconds": 90, "entrant_count": 30, "duration_total": "55:09",
    "duration_status": "CONFIRMED",
    "winner_id": "batista", "runner_up_id": "roman-reigns",
    "final_two_ids": "batista;roman-reigns",
    "final_three_ids": "batista;roman-reigns;sheamus",
    "final_four_ids": "batista;roman-reigns;sheamus;cm-punk",
    "first_entrant_id": "cm-punk", "second_entrant_id": "seth-rollins", "final_entrant_id": "rey-mysterio",
    "first_elimination_id": "damien-sandow", "last_elimination_before_winner_id": "roman-reigns",
    "eliminations_count": 29, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": 1,
    "champions_in_field_count": "UNKNOWN", "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": 1,
    "commentary_team": "UNKNOWN",
    "ring_announcer": "UNKNOWN",
    "referees": "UNKNOWN",
    "special_rules": "",
    "title_on_the_line": "FALSE",
    "championship_implications": "UNKNOWN -- no undercard results are recorded in the source document this year.",
    "winners_reward": "UNKNOWN",
    "historical_significance": (
        "Batista's 3rd career Royal Rumble win, entering at #28 (matching his 2005 and 2006 draws exactly) and "
        "eliminating Roman Reigns in the match's final second. This is the moment that sparked a well-known "
        "fan backlash -- Reigns, in his Rumble debut, tossed out a broadcast-credited 12 opponents (recalculated "
        "at 9.5 under an even-split partial-credit system per S105 -- see F277) and was the clear live-crowd "
        "favorite, while Batista, a part-time returning veteran, was booed heavily for winning. CM Punk and Seth "
        "Rollins, this match's two pre-bell entrants (#1/#2), posted the two longest survival times (49:15 and "
        "48:33) -- the 4th consecutive year the #1 entrant became this match's Iron Man. The 30th (final) "
        "entrant was Rey Mysterio, a slot the doc's own author labels 'Not Daniel Bryan' after the surprise "
        "entrance fans had been expecting instead -- see F276. Xavier Woods was reportedly an official entrant "
        "who never actually got a spot in the match -- see F279."
    ),
    "notes": (
        "Like 2009/2011/2012/2013, this document has no Dan Wahlers narrative chapter for 2014 -- only the "
        "Cageside timing analysis, PLUS a substantial bonus 'Advanced Statistics and Analysis' section from a "
        "different guest analyst (706 individually logged in-match events). Entry order and survival times are "
        "CONFIRMED to the second for all 30 entrants -- the richest year built so far for this project's "
        "no-Wahlers-chapter era. 4 of 29 eliminations have named eliminator credit -- see F275. Event-level "
        "facts (date, venue, attendance, commentary, undercard) remain UNKNOWN -- see F274. Two flagged "
        "curiosities this pass: Roman Reigns's broadcast-vs-analyst elimination-count discrepancy (F277) and "
        "Xavier Woods's non-appearance despite being listed as an official entrant (F279)."
    ),
    "data_quality_status": "PROBABLE", "source_ids": "S104;S105;S102;S103",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2014 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
