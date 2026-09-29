# -*- coding: utf-8 -*-
"""
Builds all rows for the 2012 Royal Rumble -- schema v2.

Like 2009 and 2011, Shane's doc has NO "Dan Wahlers History of the Royal
Rumble" chapter for 2012 -- only the "2012 Rumble Stats - Cageside" frame-
by-frame timing analysis. Event-level facts a Wahlers chapter normally
supplies (attendance, venue, exact date, commentary team, referees,
undercard results) are left UNKNOWN this pass.

UNLIKE 2009/2011, though, this year's Cageside section itself is full of
narrative asides that individually name several eliminations -- this is
the richest "no-Wahlers-chapter" year built so far for eliminator credit.

SOURCES CONSULTED THIS PASS:
  S084 '2012 Rumble Stats - Cageside' section (Shane's doc)              tier 9

METHODOLOGY: entry_actual[name] = cumulative buzzer-gap time +
entrance_lag[name]. Miz and Alex Riley (the first two entrants) both start
at entry_actual=0 (pre-bell, no buzzer). elim_ts[name] = entry_actual[name]
+ survival_time[name].

Checksums (all verified before writing this script -- see asserts below):
  - The cumulative buzzer sum across all 28 buzzers lands exactly on the
    doc's own stated final-buzzer mark of 44:45 (Big Show's entrance).
  - Sheamus's (the winner's) own entry_actual, computed purely from the
    buzzer/entrance-lag chain, comes out to EXACTLY 32:33 -- matching the
    doc's own prose ("Sheamus entered the ring at that point," referring
    to its own separately-stated "first 32m 33s of the match" breakpoint)
    word for word. A strong independent cross-check.
  - Chris Jericho's elim_ts (entry_actual + survival) lands exactly on the
    match total (54:53), confirming he -- not Sheamus -- is the final
    elimination, i.e. the WINNING elimination (Sheamus over Jericho).
  - Alex Riley's elim_ts computes to exactly 1:15, matching the doc's own
    aside: "Miz tossed Riley out at 1m 15s into the match."
  - Miz and Cody Rhodes both compute to an identical elim_ts of 45:38,
    matching the doc's own aside that Big Show eliminated them "together
    ... in one fell swoop" (with Cody's feet hitting the floor "a fraction
    of a second before Miz," finer than this data's 1-second resolution).

NAMED ELIMINATIONS THIS YEAR (unusually rich for a no-Wahlers-chapter
year -- all individually narrated in the Cageside prose itself, not
derived by cross-reference):
  - Alex Riley <- Miz ("Miz tossed Riley out at 1m 15s into the match")
  - Justin Gabriel <- Ricardo Rodriguez + Mick Foley, shared ("Ricardo and
    Foley teaming up to throw the final remaining jobber (Gabriel) out")
  - Kharma <- Dolph Ziggler ("When Ziggler eliminated Kharma...")
  - Michael Cole <- Booker T + Jerry Lawler, shared ("Booker T ... teaming
    up with Lawler outside of the ring to eliminate Cole") -- NOTE: both
    Booker T (eliminated at 28:55) and Lawler (eliminated at 17:31) were
    THEMSELVES already-eliminated, acting from ringside on the floor, by
    the time Cole went out at 31:21. Modeled as-is per the source's own
    narration; see F241.
  - Jack Swagger <- Big Show ("Big Show took some time near the end of his
    entrance to eliminate Jack Swagger, who was draped over the top rope
    while Big Show was approaching the ring") -- NOTE: this happened
    BEFORE Big Show's own entry_actual (46:32), i.e. during his entrance
    walk, not after formally entering the ring. See F241.
  - Miz <- Big Show, Cody Rhodes <- Big Show, shared/simultaneous ("eliminated
    together ... in one fell swoop by Big Show") -- also occurred before
    Big Show's own entry_actual; same note as Swagger.
  - Chris Jericho <- Sheamus (the winning elimination)
All other 21 elimination-eligible entrants have no individually named
eliminator this pass -- left UNKNOWN rather than guessed.

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order and survival ("ring") time are known to the second for ALL
    30 entrants -- ring_time_status is CONFIRMED throughout.
  - 8 of 29 eliminations (excluding the winner) have an individually named
    eliminator this pass, all directly narrated by S084 -- easily the
    richest no-Wahlers-chapter year built so far.
  - Event-level facts (attendance, venue, date, commentary team, referees,
    undercard results) are entirely UNKNOWN -- no Wahlers chapter exists
    for this year in the source document. event_date is stored as
    '2012-XX-XX' (year is not actually in doubt -- it's the document's own
    section heading and WWE's own official numbering -- only the exact day
    is unconfirmed), same convention established for 2009/2011.
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
EVENT_ID = "RR2012M"


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
    ("S084", "'2012 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers, ring "
     "crowdedness) filed under the '2012 Royal Rumble Stats' Heading-1. NO separate Dan Wahlers narrative "
     "history chapter exists for this year in Shane's document, but the Cageside prose itself individually "
     "narrates 8 eliminations (see script docstring) -- richer than 2009/2011's near-total absence of "
     "eliminator credit. Event-level facts (attendance, venue, exact date, commentary, undercard) are still "
     "UNKNOWN this pass. NOT live-fetched this pass."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# TIMING DERIVATION
# ---------------------------------------------------------------------------
buzzer_gaps = [
    ("R-Truth", "1:56"), ("Cody Rhodes", "1:31"), ("Justin Gabriel", "1:30"), ("Primo", "1:30"),
    ("Mick Foley", "1:31"), ("Ricardo Rodriguez", "1:30"), ("Santino Marella", "2:11"), ("Epico", "1:55"),
    ("Kofi Kingston", "1:27"), ("Jerry Lawler", "1:30"), ("Ezekiel Jackson", "1:26"), ("Jinder Mahal", "1:30"),
    ("The Great Khali", "1:30"), ("Hunico", "1:30"), ("Booker T", "1:30"), ("Dolph Ziggler", "1:47"),
    ("Jim Duggan", "1:31"), ("Michael Cole", "1:57"), ("Kharma", "1:19"), ("Sheamus", "1:52"),
    ("Road Dogg", "1:30"), ("Jey Uso", "1:28"), ("Jack Swagger", "1:30"), ("Wade Barrett", "1:29"),
    ("David Otunga", "1:30"), ("Randy Orton", "1:30"), ("Chris Jericho", "1:38"), ("Big Show", "1:47"),
]
buzzer_time = {}
cum = 0
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("44:45"), f"buzzer checksum failed: {cum}"

# Entrance times. Miz and Alex Riley (pre-bell, the first two entrants) are
# excluded, same treatment as CM Punk/Daniel Bryan in 2011.
entrance_lag = {
    "Ricardo Rodriguez": "1:03", "Jinder Mahal": "0:56", "Michael Cole": "0:45", "Big Show": "0:34", "The Great Khali": "0:29",
    "Kharma": "0:28", "Wade Barrett": "0:28", "David Otunga": "0:27", "Hunico": "0:25", "Dolph Ziggler": "0:24",
    "Chris Jericho": "0:21", "R-Truth": "0:19", "Jim Duggan": "0:19", "Santino Marella": "0:18", "Booker T": "0:18",
    "Cody Rhodes": "0:16", "Kofi Kingston": "0:16", "Road Dogg": "0:16", "Jerry Lawler": "0:16",
    "Justin Gabriel": "0:15", "Jack Swagger": "0:15", "Mick Foley": "0:14", "Ezekiel Jackson": "0:11", "Jey Uso": "0:11",
    "Epico": "0:10", "Sheamus": "0:10", "Randy Orton": "0:09", "Primo": "0:08",
}
entry_actual = {"Miz": 0, "Alex Riley": 0}
for name in buzzer_time:
    entry_actual[name] = buzzer_time[name] + mmss(entrance_lag[name])
assert entry_actual["Sheamus"] == mmss("32:33"), entry_actual["Sheamus"]  # matches doc's own stated breakpoint

# Survival ("ring") times, as stated directly by S084. Sheamus (the
# winner) is included with a survival time that is his entry-to-match-end
# span, not an elimination -- excluded from elim_ts below.
survival = {
    "Miz": "45:38", "Cody Rhodes": "41:55", "Sheamus": "22:20", "Dolph Ziggler": "19:45", "Kofi Kingston": "17:55",
    "Chris Jericho": "11:34", "Hunico": "9:00", "Jack Swagger": "7:59", "The Great Khali": "7:29", "Jey Uso": "7:03",
    "Mick Foley": "6:33", "Justin Gabriel": "6:13", "Randy Orton": "5:46", "R-Truth": "4:57", "Road Dogg": "4:56",
    "Booker T": "4:40", "Wade Barrett": "3:55", "Ezekiel Jackson": "3:46", "David Otunga": "3:16", "Santino Marella": "2:31",
    "Ricardo Rodriguez": "2:20", "Primo": "1:57", "Big Show": "1:52", "Michael Cole": "1:24", "Jinder Mahal": "1:17",
    "Alex Riley": "1:15", "Kharma": "1:01", "Jim Duggan": "0:57", "Jerry Lawler": "0:44", "Epico": "0:11",
}
assert set(survival) == set(entry_actual), set(survival) ^ set(entry_actual)
assert len(survival) == 30

MATCH_TOTAL = mmss("54:53")
assert mmss(survival["Sheamus"]) == MATCH_TOTAL - entry_actual["Sheamus"]

elim_ts = {}
for name, t in survival.items():
    if name == "Sheamus":
        continue  # winner, never eliminated
    elim_ts[name] = entry_actual[name] + mmss(t)
assert elim_ts["Chris Jericho"] == MATCH_TOTAL, elim_ts["Chris Jericho"]  # the winning elimination, by Sheamus
assert elim_ts["Alex Riley"] == mmss("1:15")  # matches doc's own stated "tossed out at 1m15s"
assert elim_ts["Miz"] == elim_ts["Cody Rhodes"] == mmss("45:38")  # simultaneous, matches doc's "in one fell swoop"

elim_order_list = sorted(elim_ts, key=lambda n: elim_ts[n])
elim_number = {name: i + 1 for i, name in enumerate(elim_order_list)}
assert elim_number["Alex Riley"] == 1
assert elim_number["Chris Jericho"] == 29  # the winning elimination, last of 29

ENTRY_NUMBERS = {"Miz": 1, "Alex Riley": 2}
for i, (name, _) in enumerate(buzzer_gaps):
    ENTRY_NUMBERS[name] = i + 3
assert ENTRY_NUMBERS["R-Truth"] == 3 and ENTRY_NUMBERS["Big Show"] == 30

# Final four determined from elim_ts order -- last eliminated before the
# winner, matching the doc's own "7-man battle royal to the finish" framing
# once Big Show (the final entrant) came in.
FINAL_TWO = {"Sheamus", "Chris Jericho"}
FINAL_THREE = {"Sheamus", "Chris Jericho", "Randy Orton"}
FINAL_FOUR = {"Sheamus", "Chris Jericho", "Randy Orton", "Big Show"}

# name -> (eliminator names, data_quality_status, notes, is_shared, group_id)
KNOWN_ELIMINATORS = {
    "Alex Riley": (["Miz"], "CONFIRMED",
                    "S084 directly states 'Miz tossed Riley out at 1m 15s into the match' -- matches this "
                    "script's own elim_ts computation for Riley exactly (1:15).", False, ""),
    "Justin Gabriel": (["Ricardo Rodriguez", "Mick Foley"], "CONFIRMED",
                        "S084 directly states 'Ricardo and Foley teaming up to throw the final remaining "
                        "jobber (Gabriel) out of the ring.'", True, "gabriel_group"),
    "Kharma": (["Dolph Ziggler"], "CONFIRMED",
               "S084 directly states 'When Ziggler eliminated Kharma, WWE's countdown clock then began to "
               "tick away.'", False, ""),
    "Michael Cole": (["Booker T", "Jerry Lawler"], "CONFIRMED",
                      "S084 directly states Booker T 'played a vital part in teaming up with Lawler outside "
                      "of the ring to eliminate Cole.' NOTE: both Booker T (own elim_ts 28:55) and Lawler (own "
                      "elim_ts 17:31) were themselves already-eliminated, acting from ringside on the floor, "
                      "by the time Cole went out at 31:21 -- an already-eliminated wrestler interfering from "
                      "outside the ring to cause a later elimination, a known (if unusual) Rumble occurrence. "
                      "See F241.", True, "cole_group"),
    "Jack Swagger": (["Big Show"], "CONFIRMED",
                      "S084 directly states 'Big Show took some time near the end of his entrance to "
                      "eliminate Jack Swagger, who was draped over the top rope while Big Show was "
                      "approaching the ring.' NOTE: this occurred BEFORE Big Show's own entry_actual (46:32) "
                      "-- during his entrance walk, not after formally entering the ring. See F241.", False, ""),
    "Miz": (["Big Show"], "CONFIRMED",
             "S084 directly states Miz and Cody Rhodes were 'eliminated together ... in one fell swoop by Big "
             "Show, who pretty much tries to ruin every Royal Rumble match he wrestles in.' Also occurred "
             "before Big Show's own entry_actual -- see F241.", True, "bigshow_double"),
    "Cody Rhodes": (["Big Show"], "CONFIRMED",
                     "S084 directly states 'Cody's feet hit the floor a fraction of a second before Miz' in "
                     "the same Big Show elimination -- both compute to an identical elim_ts of 45:38 at this "
                     "data's 1-second resolution.", True, "bigshow_double"),
    "Chris Jericho": (["Sheamus"], "PROBABLE",
                       "The winning elimination -- Sheamus and Jericho had the ring to themselves for the "
                       "final 7:38 of the match before Sheamus won.", False, ""),
}

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Hunico", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #16, survived 9:00. Came to the ring with Camacho on a low rider bicycle, per S084. No individually-named elimination credit this pass.", "S084"),
    ("Jey Uso", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #24, survived 7:03. No individually-named elimination credit this pass.", "S084"),
    ("Road Dogg", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #23, survived 4:56. No individually-named elimination credit this pass.", "S084"),
    ("Ricardo Rodriguez", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #8, survived 2:20. His lengthy entrance was a parody of Alberto Del Rio's, per S084. Credited (with Mick Foley) for eliminating Justin Gabriel.", "S084"),
    ("Primo", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #6, survived 1:57. No individually-named elimination credit this pass.", "S084"),
    ("Michael Cole", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "WWE commentator entered #20, survived 1:24 -- longer than Jerry Lawler despite Cole having lost to Lawler at WrestleMania 27, a point S084 notes as ironic. Eliminated by Booker T and Jerry Lawler acting from ringside -- see F241.", "S084"),
    ("Jinder Mahal", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #14, survived 1:17. No individually-named elimination credit this pass.", "S084"),
    ("Kharma", "", "UNKNOWN", "F", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #21, survived 1:01. The only woman in this match's field. Eliminated Michael Cole, Dolph Ziggler, and Hunico before being eliminated herself by Ziggler, per S084's own account. No cross-referenced elimination rows created for her 3 credited victims this pass beyond what S084 individually confirms (Cole).", "S084"),
    ("Epico", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #9, survived just 0:11 -- one of the shortest survival times of the match. No individually-named elimination credit this pass.", "S084"),
]

reused = {
    "Miz": "the-miz", "Cody Rhodes": "cody-rhodes", "Sheamus": "sheamus", "Dolph Ziggler": "dolph-ziggler",
    "Kofi Kingston": "kofi-kingston", "Chris Jericho": "chris-jericho", "Jack Swagger": "jack-swagger",
    "The Great Khali": "the-great-khali", "Mick Foley": "mick-foley", "Justin Gabriel": "justin-gabriel",
    "Randy Orton": "randy-orton", "R-Truth": "r-truth", "Booker T": "booker-t", "Wade Barrett": "wade-barrett",
    "Ezekiel Jackson": "ezekiel-jackson", "David Otunga": "david-otunga", "Santino Marella": "santino-marella",
    "Big Show": "big-show", "Alex Riley": "alex-riley", "Jim Duggan": "jim-duggan", "Jerry Lawler": "jerry-lawler",
}

wrestler_ids = {}
wrestler_ids.update(reused)

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
    "Miz", "Alex Riley", "R-Truth", "Cody Rhodes", "Justin Gabriel", "Primo", "Mick Foley", "Ricardo Rodriguez",
    "Santino Marella", "Epico", "Kofi Kingston", "Jerry Lawler", "Ezekiel Jackson", "Jinder Mahal",
    "The Great Khali", "Hunico", "Booker T", "Dolph Ziggler", "Jim Duggan", "Michael Cole", "Kharma", "Sheamus",
    "Road Dogg", "Jey Uso", "Jack Swagger", "Wade Barrett", "David Otunga", "Randy Orton", "Chris Jericho",
    "Big Show",
]
assert len(all_names) == 30

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Sheamus")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, dq, method, is_shared, group_id = KNOWN_ELIMINATORS.get(name, ([], "", "", False, ""))

    notes_parts = []
    if name == "Sheamus":
        notes_parts.append("Entered #22 and won his first career Royal Rumble, eliminating Chris Jericho in the match's final second after the two had the ring to themselves for the final 7:38. His own entry_actual, computed purely from the buzzer/entrance-lag chain, lands exactly on the doc's own independently-stated '32m 33s' breakpoint -- a strong internal cross-check.")
    elif name == "Chris Jericho":
        notes_parts.append("Eliminated by Sheamus in the match's final second -- the winning elimination, and the runner-up spot.")
    elif name == "Kharma":
        notes_parts.append("The only woman in this match's field. S084 credits her with eliminating Michael Cole, Dolph Ziggler, and Hunico before being eliminated herself by Ziggler -- only the Cole elimination is corroborated with enough specificity this pass to log as a credited elimination row (shared with Booker T); the Ziggler/Hunico credits are noted here but not converted into elimination rows absent individual timing corroboration.")
    elif name == "Big Show":
        notes_parts.append("Credited with 3 eliminations (Jack Swagger, and the Miz/Cody Rhodes double) all occurring BEFORE his own entry_actual (46:32) -- i.e. during his ~1:47 entrance walk, interfering from ringside before formally entering the ring. See F241.")
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
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE",
            "simultaneous_group_id": group_id,
            "data_quality_status": dq,
            "source_ids": "S084",
            "notes": "",
        })

    er = {
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": "CONFIRMED",
        "ring_name_at_time": name, "name_displayed_at_event": name,
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
        "faction_stable": "",
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
        "is_runner_up": "TRUE" if name == "Chris Jericho" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "FALSE",
        "legend_returning": "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "TRUE" if name == "Michael Cole" else "FALSE",
        "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S084",
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
    ("F239", EVENT_ID, "events", EVENT_ID, "event_date;venue;attendance_reported;commentary_team;referees", "unverified",
     "Like 2009 and 2011, Shane's document has NO separate Dan Wahlers narrative history chapter for 2012 -- "
     "only the Cageside timing analysis. Event-level facts a Wahlers chapter normally supplies (exact date, "
     "venue, city, attendance, commentary team, referees, undercard results) are simply absent from the source "
     "and left entirely UNKNOWN this pass. event_date is stored as '2012-XX-XX' rather than a bare 'UNKNOWN' -- "
     "the year itself is not in doubt (the document's own section heading and WWE's own official numbering), "
     "only the exact month/day are unconfirmed. Pending a future external-research pass.",
     "S084", "open", "2026-09-16"),
    ("F240", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "8 of 29 eliminations (excluding the winner) have an individually named eliminator this pass, all "
     "directly narrated within S084's Cageside prose itself (see script docstring) -- the richest "
     "no-Wahlers-chapter year built so far. The remaining 21 elimination-eligible entrants have no named "
     "eliminator this pass. Left UNKNOWN rather than guessed.",
     "S084", "open", "2026-09-16"),
    ("F241", EVENT_ID, "eliminations", "jack-swagger;the-miz;cody-rhodes;michael-cole", "elimination_method", "unverified",
     "Two unusual elimination circumstances this year, both directly narrated by S084 and modeled as-is: (1) "
     "Big Show's eliminations of Jack Swagger and the Miz/Cody Rhodes double all occurred BEFORE his own "
     "entry_actual (46:32) -- during his ~1:47 entrance walk, interfering from ringside before formally "
     "entering the ring. (2) Michael Cole's eliminator credit (Booker T + Jerry Lawler) involves two wrestlers "
     "who were THEMSELVES already eliminated (at 28:55 and 17:31 respectively) acting from ringside on the "
     "floor at the time of Cole's elimination (31:21) -- a known but unusual Rumble occurrence where an "
     "eliminated wrestler continues to interfere from outside. Neither circumstance is treated as invalidating "
     "the credited elimination, since both are explicitly how S084 narrates them.",
     "S084", "open", "2026-09-16"),
    ("F242", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 9 previously-unseen wrestlers this pass (Hunico, Jey Uso, Road Dogg, Ricardo "
     "Rodriguez, Primo, Michael Cole, Jinder Mahal, Kharma, Epico) with zero bio data in this pass's source -- "
     "names only. Left entirely UNKNOWN, same pattern as every prior year's equivalent flag.",
     "S084", "open", "2026-09-16"),
    ("F243", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-16"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2012", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2012-XX-XX", "venue": "UNKNOWN",
    "city_region": "UNKNOWN", "country": "UNKNOWN",
    "attendance_official": "", "attendance_reported": "",
    "entry_interval_seconds": 90, "entrant_count": 30, "duration_total": "54:53",
    "duration_status": "CONFIRMED",
    "winner_id": "sheamus", "runner_up_id": "chris-jericho",
    "final_two_ids": "sheamus;chris-jericho",
    "final_three_ids": "sheamus;chris-jericho;randy-orton",
    "final_four_ids": "sheamus;chris-jericho;randy-orton;big-show",
    "first_entrant_id": "the-miz", "second_entrant_id": "alex-riley", "final_entrant_id": "big-show",
    "first_elimination_id": "alex-riley", "last_elimination_before_winner_id": "chris-jericho",
    "eliminations_count": 29, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": "UNKNOWN",
    "champions_in_field_count": "UNKNOWN", "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "UNKNOWN",
    "ring_announcer": "UNKNOWN",
    "referees": "UNKNOWN",
    "special_rules": "",
    "title_on_the_line": "FALSE",
    "championship_implications": "UNKNOWN -- no undercard results are recorded in the source document this year.",
    "winners_reward": "UNKNOWN",
    "historical_significance": (
        "Sheamus's first career Royal Rumble win, eliminating Chris Jericho after the two had the ring to "
        "themselves for the final 7:38 of the match. This match notably featured the entire WWE commentary "
        "team (Michael Cole, Jerry Lawler, Booker T) entering as competitors -- a gimmick not repeated in "
        "most other years. Miz and Cody Rhodes were the two constants in the ring for the majority of the "
        "match before being eliminated together by Big Show in one motion. Kofi Kingston pulled off a widely "
        "remembered walking-handstand escape to save himself from elimination, surviving an additional 7:45 "
        "afterward. Kharma, the only woman in the field, eliminated 3 wrestlers (Cole, Ziggler, Hunico per "
        "S084) before being eliminated herself. Epico had the shortest survival time of the match at just "
        "0:11."
    ),
    "notes": (
        "Like 2009 and 2011, this document has no Dan Wahlers narrative chapter for 2012 -- only the Cageside "
        "timing analysis. Unlike those years, though, the Cageside prose itself individually narrates 8 "
        "eliminations (see F240), making this the richest no-Wahlers-chapter year for eliminator credit built "
        "so far. Entry order and survival times are CONFIRMED to the second for all 30 entrants. Event-level "
        "facts (date, venue, attendance, commentary, undercard) remain UNKNOWN -- see F239."
    ),
    "data_quality_status": "PROBABLE", "source_ids": "S084",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2012 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
