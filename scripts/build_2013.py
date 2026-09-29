# -*- coding: utf-8 -*-
"""
Builds all rows for the 2013 Royal Rumble -- schema v2.

Like 2009/2011/2012, Shane's doc has NO "Dan Wahlers History of the Royal
Rumble" chapter for 2013 -- only the "2013 Rumble Stats - Cageside" frame-
by-frame timing analysis.

UNLIKE 2009/2011/2012, this year's "time between buzzers" list is UNNAMED
(28 bare durations, not paired with entrant names) -- entry order is NOT
fully recoverable this pass. Only entrants anchored by an explicit prose
statement naming them at a specific numbered position can be placed with
confidence; the other 21 have known survival ("ring") time but UNKNOWN
entry position. This is the first year built so far with this specific
partial-recoverability profile -- see F267.

SOURCES CONSULTED THIS PASS:
  S101 '2013 Rumble Stats - Cageside' section (Shane's doc)             tier 9
  S102 'Looking At A Ton Of Royal Rumble Statistics & Records - SE
       Scoops' article (embedded in Shane's doc's 'Royal Rumble
       Collection of Stats' section)                                    tier 9
  S103 'WWE Royal Rumble Interesting Facts And Stats' article, WrestlingInc
       (embedded in Shane's doc's 'Royal Rumble Collection of Stats'
       section)                                                         tier 9

METHODOLOGY: buzzer gap list index N (1-indexed, N=1..28) is the wait
ENDING at entrant position (N+2) -- entrants #1/#2 are pre-bell, no buzzer.
Verified against 3 explicit prose anchors naming specific entrants at
specific positions (all 3 checked out exactly against this indexing):
  - gap 12 (1:54) ends at #14 -> "Brodus Clay and Rey Mysterio...13th and
    14th entrants" (Clay=13, Mysterio=14)
  - gap 14 (1:58) ends at #16 -> "Darren Young and Bo Dallas...15th and
    16th entrants" (Young=15, Dallas=16)
  - gap 23 (1:22) ends at #25 -> "Kane and Zack Ryder's entrances...24th
    and 25th entrants" (Kane=24, Ryder=25)
entry_actual[name] = cumulative buzzer-gap time (through position's own
gap) + entrance_lag[name]. elim_ts[name] = entry_actual[name] +
survival_time[name] -- computable ONLY for the 6 anchored non-winner
entrants above, plus Ziggler and Jericho (both pre-bell entrants #1/#2 in
some order -- exact order NOT confirmed by any source this pass, but
entry_actual=0 either way, so their elim_ts is still computable without
resolving which of them is #1 vs #2).

Checksum verified before writing this script (the strongest evidence this
pass that the whole buzzer/lag chain is being read correctly): John Cena's
entry_actual, computed purely from the buzzer/entrance-lag chain assuming
he is entrant #19, comes out to EXACTLY 28:56 -- and 28:56 + his own
28:56 stated survival time is not the match here, but his stated 26:11
survival time added to that 28:56 lands EXACTLY on the match's own total
duration of 55:07, confirming (a) he is entrant #19 and (b) he is the
winner (never eliminated -- his own elim_ts would equal the match total,
which is exactly the signature of the WINNING wrestler, not an eliminated
one). This matches TWO independent, directly-stated facts found elsewhere
in Shane's document (S102: "2013 - John Cena (entered at number 19)"; S103:
"John Cena from #19 in 2013" won the match) -- three independent lines of
evidence (two distinct trivia articles plus this script's own internal
arithmetic) agreeing exactly. Strong enough for CONFIRMED, unlike this
year's other entry-number derivations (single-document-only -- DERIVED).

NAMED ELIMINATIONS THIS YEAR: NONE. Unlike 2012, this year's Cageside
prose contains no individually-narrated "X eliminated Y" sentences at all
-- eliminator credit is entirely UNKNOWN for all 29 non-winner entrants.
One aggregate stat is known (not attributable to specific victims): S103
states Sheamus and Ryback each eliminated 5 wrestlers this match (a
match-high tie) -- logged in their notes and in F269, not converted into
elimination rows since no victims are named.

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Survival ("ring") time is known to the second for ALL 30 entrants.
  - Entrance lag is known for 28 of 30 (all but Ziggler/Jericho, the two
    pre-bell entrants).
  - Entry order (entry_number) is confidently known for only 7 of 30:
    Brodus Clay (13), Rey Mysterio (14), Darren Young (15), Bo Dallas (16),
    John Cena (19, CONFIRMED per above), Kane (24), Zack Ryder (25). The
    other 23 (including Ziggler/Jericho, who are confidently #1-and-#2 as
    A SET but not individually ordered) are UNKNOWN this pass. See F267.
  - Winner: John Cena (CONFIRMED, entry #19, per above). Runner-up and
    final-two/three/four are all UNKNOWN this pass -- the elim_ts values
    this script CAN compute (Ziggler 49:48, Jericho 47:54, plus the 5
    anchored group) do not, on their own, identify who was eliminated
    immediately before Cena's win, since 21 other entrants' elim_ts remain
    completely unknown and could fall later than any of these. Left
    UNKNOWN rather than guessed -- see F267.
  - Event-level facts (attendance, venue, exact date, commentary, referees,
    undercard) are entirely UNKNOWN -- no Wahlers chapter exists for this
    year. event_date stored as '2013-XX-XX', same convention as 2009/2011/
    2012.
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
EVENT_ID = "RR2013M"


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
    ("S101", "'2013 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-17",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers -- UNNAMED "
     "this year, unlike 2012 -- ring crowdedness) filed under the '2013 Royal Rumble Stats' Heading-1. NO "
     "separate Dan Wahlers narrative history chapter exists for this year. Contains zero individually-narrated "
     "elimination credits (unlike 2012). NOT live-fetched this pass."),
    ("S102", "'Looking At A Ton Of Royal Rumble Statistics & Records - SE Scoops' article", "reputable_publication", "", 9, "Contemporary wrestling publication", "2026-09-17",
     "Embedded within Shane's doc's 'Royal Rumble Collection of Stats' section (Heading 2). A year-by-year "
     "'winner (entered at number N)' list covering 1988-2014 -- used this pass to confirm 2013's winner (John "
     "Cena) and his entry number (19), independently cross-checked against this script's own buzzer-chain "
     "arithmetic. Also usable for future years' builds (gives 2014's winner/entry-number too). NOT live-fetched "
     "this pass -- read directly from Shane's document."),
    ("S103", "'WWE Royal Rumble Interesting Facts And Stats: Hidden Rumbles, Owen's Win, WCW Connections' article, WrestlingInc", "reputable_publication", "", 9, "Contemporary wrestling publication", "2026-09-17",
     "Embedded within Shane's doc's 'Royal Rumble Collection of Stats' section. A long list of Rumble trivia "
     "bullets; used this pass to independently corroborate John Cena's 2013 win/entry-number ('the only "
     "Superstars to win a 30 man Rumble to draw a number between 9 and 21 was Shawn Michaels in 1996 and John "
     "Cena from #19 in 2013') and to source the 'Sheamus and Ryback eliminated 5 in 2013' stat (tied for most "
     "eliminations by a single competitor this match -- individual victims not named). NOT live-fetched this "
     "pass -- read directly from Shane's document."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# TIMING DERIVATION
# ---------------------------------------------------------------------------
# 28 unnamed buzzer gaps, in chronological order. Index i (0-based) is the
# wait ending at entrant position (i + 3).
buzzer_gaps = [
    "1:38", "1:43", "1:46", "1:39", "1:38", "1:41", "1:45", "1:34", "1:42", "1:29",
    "1:35", "1:54", "1:38", "1:58", "1:29", "1:47", "1:30", "1:42", "1:30", "1:32",
    "1:30", "1:30", "1:22", "1:30", "1:31", "1:29", "1:30", "1:27",
]
assert len(buzzer_gaps) == 28
cum_at_position = {}
_c = 0
for _i, _g in enumerate(buzzer_gaps):
    _c += mmss(_g)
    cum_at_position[_i + 3] = _c
assert secs_to_mmss(cum_at_position[13]) == "18:10"
assert secs_to_mmss(cum_at_position[14]) == "20:04"
assert secs_to_mmss(cum_at_position[15]) == "21:42"
assert secs_to_mmss(cum_at_position[16]) == "23:40"
assert secs_to_mmss(cum_at_position[19]) == "28:26"
assert secs_to_mmss(cum_at_position[24]) == "36:10"
assert secs_to_mmss(cum_at_position[25]) == "37:32"

# Entrance times (28 named -- Ziggler and Jericho excluded, pre-bell entrants).
entrance_lag = {
    "The Godfather": "0:49", "John Cena": "0:30", "Brodus Clay": "0:29", "Goldust": "0:28",
    "The Miz": "0:27", "The Great Khali": "0:26", "Wade Barrett": "0:25", "Sin Cara": "0:22",
    "David Otunga": "0:20", "Ryback": "0:17", "Kane": "0:16", "Santino Marella": "0:15",
    "Cesaro": "0:15", "Heath Slater": "0:14", "Daniel Bryan": "0:14", "Kofi Kingston": "0:12",
    "Titus O'Neil": "0:12", "Damien Sandow": "0:12", "Jinder Mahal": "0:12", "Cody Rhodes": "0:11",
    "Tensai": "0:11", "Drew McIntyre": "0:10", "Darren Young": "0:10", "Bo Dallas": "0:10",
    "Randy Orton": "0:10", "Rey Mysterio": "0:09", "Sheamus": "0:08", "Zack Ryder": "0:08",
}
assert len(entrance_lag) == 28

# Survival ("ring") times, as stated directly by S101 -- all 30.
survival = {
    "Dolph Ziggler": "49:48", "Chris Jericho": "47:54", "Sheamus": "37:16", "Cody Rhodes": "27:30",
    "John Cena": "26:11", "Bo Dallas": "21:33", "Kofi Kingston": "21:07", "Wade Barrett": "17:10",
    "Damien Sandow": "16:14", "Heath Slater": "15:36", "Rey Mysterio": "10:35", "Randy Orton": "10:11",
    "Goldust": "9:14", "Ryback": "8:51", "Cesaro": "7:35", "Titus O'Neil": "7:19",
    "Daniel Bryan": "6:41", "Tensai": "5:27", "The Miz": "4:42", "David Otunga": "4:05",
    "Brodus Clay": "3:18", "Sin Cara": "3:05", "The Great Khali": "2:42", "Darren Young": "2:41",
    "Drew McIntyre": "2:30", "Zack Ryder": "2:26", "Jinder Mahal": "1:58", "Kane": "1:30",
    "Santino Marella": "0:41", "The Godfather": "0:05",
}
assert len(survival) == 30

MATCH_TOTAL = mmss("55:07")

# entry_actual, computable for: the 6 anchored non-winner entrants + Cena
# (all via cum_at_position) and Ziggler/Jericho (both = 0, pre-bell).
ANCHORED_ENTRY_NUMBERS = {
    "Brodus Clay": 13, "Rey Mysterio": 14, "Darren Young": 15, "Bo Dallas": 16,
    "John Cena": 19, "Kane": 24, "Zack Ryder": 25,
}
entry_actual = {"Dolph Ziggler": 0, "Chris Jericho": 0}
for name, pos in ANCHORED_ENTRY_NUMBERS.items():
    entry_actual[name] = cum_at_position[pos] + mmss(entrance_lag[name])
assert secs_to_mmss(entry_actual["John Cena"]) == "28:56"
assert entry_actual["John Cena"] + mmss(survival["John Cena"]) == MATCH_TOTAL, (
    "Cena checksum failed -- entry #19 + 26:11 survival should land exactly on 55:07"
)  # confirms Cena is entrant #19 AND the winner (never eliminated)

elim_ts = {}
for name in list(ANCHORED_ENTRY_NUMBERS) + ["Dolph Ziggler", "Chris Jericho"]:
    if name == "John Cena":
        continue  # winner, never eliminated
    elim_ts[name] = entry_actual[name] + mmss(survival[name])
assert secs_to_mmss(elim_ts["Dolph Ziggler"]) == "49:48"
assert secs_to_mmss(elim_ts["Chris Jericho"]) == "47:54"
assert secs_to_mmss(elim_ts["Brodus Clay"]) == "21:57"
assert secs_to_mmss(elim_ts["Rey Mysterio"]) == "30:48"
assert secs_to_mmss(elim_ts["Darren Young"]) == "24:33"
assert secs_to_mmss(elim_ts["Bo Dallas"]) == "45:23"
assert secs_to_mmss(elim_ts["Kane"]) == "37:56"
assert secs_to_mmss(elim_ts["Zack Ryder"]) == "40:06"
for _v in elim_ts.values():
    assert 0 < _v < MATCH_TOTAL

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Bo Dallas", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #16 (DERIVED -- S101 directly names him as the 16th entrant, cross-checked against this script's own buzzer-chain arithmetic). Survived 21:33, the match's 6th-longest survival time -- unusually long for a lower-card talent at the time, noted directly by S101 ('The name Bo Dallas sticks out like a sore thumb on the above list').", "S101"),
    ("Ryback", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entry position not determinable this pass (unnamed buzzer list, no anchor). Survived 8:51. Per S103, tied with Sheamus for most eliminations by a single competitor in this match (5 each) -- individual victims not named by any source consulted this pass. See F269.", "S101;S103"),
    ("Cesaro", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "Antonio Cesaro", "", "Billed as 'Antonio Cesaro' at this event (see entrants.csv ring_name_at_time) -- stored under the name-stable wrestler_id 'cesaro' since that is how this performer became far better known from 2014 onward, matching this database's established precedent for name-stable IDs across gimmick/ring-name changes (e.g. Steve Austin/Ringmaster, 1996). Entry position not determinable this pass. Survived 7:35.", "S101"),
    ("Titus O'Neil", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entry position not determinable this pass. Survived 7:19.", "S101"),
    ("Tensai", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entry position not determinable this pass. Survived 5:27. Likely the same performer (Matt Bloom) as this database's existing 'prince-albert' wrestler_id (ring names Prince Albert/Albert/A-Train, merged there by the 2003-2007 fact-check pass) -- not stated or otherwise confirmed by any source consulted this pass, so left UNMERGED per the project's 2-source identity-merge rule. See F272.", "S101"),
    ("Brodus Clay", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #13 (DERIVED -- S101 directly names him as the 13th entrant alongside Rey Mysterio as the 14th, cross-checked against this script's own buzzer-chain arithmetic). Survived 3:18.", "S101"),
    ("Sin Cara", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entry position not determinable this pass. Survived 3:05. Possibly the same performer as this database's existing 'hunico' wrestler_id (Alberto Rodriguez took over the Sin Cara gimmick from the original performer, Luis Urive, in September 2012, per general wrestling-history knowledge) -- not stated or otherwise confirmed by any source consulted this pass, so left as a SEPARATE wrestler_id pending 2-source confirmation. See F272.", "S101"),
    ("Darren Young", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #15 (DERIVED -- S101 directly names him as the 15th entrant alongside Bo Dallas as the 16th, cross-checked against this script's own buzzer-chain arithmetic). Survived 2:41.", "S101"),
    ("Damien Sandow", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entry position not determinable this pass. Survived 16:14.", "S101"),
]

reused = {
    "Dolph Ziggler": "dolph-ziggler", "Chris Jericho": "chris-jericho", "Sheamus": "sheamus",
    "Cody Rhodes": "cody-rhodes", "John Cena": "john-cena", "Kofi Kingston": "kofi-kingston",
    "Wade Barrett": "wade-barrett", "Rey Mysterio": "rey-mysterio", "Randy Orton": "randy-orton",
    "Goldust": "goldust", "Daniel Bryan": "daniel-bryan", "The Miz": "the-miz",
    "David Otunga": "david-otunga", "The Great Khali": "the-great-khali", "Drew McIntyre": "drew-mcintyre",
    "Zack Ryder": "zack-ryder", "Jinder Mahal": "jinder-mahal", "Kane": "kane",
    "Santino Marella": "santino-marella", "The Godfather": "the-godfather", "Heath Slater": "heath-slater",
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
# ENTRANTS -- all 30. Survival time known for all; entry order known for
# only 9 (Ziggler, Jericho as a set + the 7 anchored/checksummed names).
# ---------------------------------------------------------------------------
all_names = [
    "Dolph Ziggler", "Chris Jericho", "Sheamus", "Cody Rhodes", "John Cena", "Bo Dallas",
    "Kofi Kingston", "Wade Barrett", "Damien Sandow", "Heath Slater", "Rey Mysterio", "Randy Orton",
    "Goldust", "Ryback", "Cesaro", "Titus O'Neil", "Daniel Bryan", "Tensai", "The Miz", "David Otunga",
    "Brodus Clay", "Sin Cara", "The Great Khali", "Darren Young", "Drew McIntyre", "Zack Ryder",
    "Jinder Mahal", "Kane", "Santino Marella", "The Godfather",
]
assert len(all_names) == 30
assert set(all_names) == set(survival)

DISPLAY_NAME = {"Cesaro": "Antonio Cesaro"}

entrant_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "John Cena")
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    entry = ANCHORED_ENTRY_NUMBERS.get(name, "")
    if entry:
        entry_status = "CONFIRMED" if name == "John Cena" else "DERIVED"
    else:
        entry_status = "UNKNOWN"

    has_elim_ts = name in elim_ts
    row_quality = "CONFIRMED" if is_winner else "PROBABLE"

    notes_parts = []
    if name == "John Cena":
        notes_parts.append(
            "Entered #19 and won his 2nd career Royal Rumble. Directly stated as this match's winner/entry-"
            "number by 2 independent trivia sources found elsewhere in Shane's document (S102: 'entered at "
            "number 19'; S103: 'John Cena from #19 in 2013'), and independently cross-checked against this "
            "script's own buzzer-chain arithmetic, which lands his entry_actual at exactly 28:56 -- adding his "
            "own stated 26:11 survival time lands exactly on the match's 55:07 total, the signature of the "
            "winning (never-eliminated) wrestler. Three independent lines of evidence agreeing exactly."
        )
    elif name in ("Dolph Ziggler", "Chris Jericho"):
        notes_parts.append(
            "One of this match's two pre-bell entrants (#1 and #2, in some order) -- S101 explicitly excludes "
            "both from the entrance-lag list for this reason ('Ziggler and Jericho each had their entrances "
            "during the pre-match segment'). Which of the two drew #1 vs #2 is NOT stated by any source "
            "consulted this pass -- left UNKNOWN rather than guessed, though entry_actual is 0 either way, so "
            "elimination_clock_time is still computable. See F267."
        )
    elif name in ("Brodus Clay", "Rey Mysterio", "Darren Young", "Bo Dallas", "Kane", "Zack Ryder"):
        pair = {
            "Brodus Clay": "Rey Mysterio (14th)", "Rey Mysterio": "Brodus Clay (13th)",
            "Darren Young": "Bo Dallas (16th)", "Bo Dallas": "Darren Young (15th)",
            "Kane": "Zack Ryder (25th)", "Zack Ryder": "Kane (24th)",
        }[name]
        notes_parts.append(
            f"Entry position DERIVED from an explicit S101 prose anchor naming this entrant alongside "
            f"{pair}, cross-checked against this script's own buzzer-gap arithmetic (both agree exactly)."
        )
    if name == "Sheamus":
        notes_parts.append("Per S103, tied with Ryback for most eliminations by a single competitor in this match (5 each) -- individual victims not named by any source consulted this pass. See F269.")
    if name == "Ryback":
        notes_parts.append("Per S103, tied with Sheamus for most eliminations by a single competitor in this match (5 each) -- individual victims not named by any source consulted this pass. See F269.")
    if name == "Cesaro":
        notes_parts.append("Billed as 'Antonio Cesaro' at this event.")
    note = " ".join(notes_parts)

    er = {
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": entry_status,
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
        "faction_stable": "",
        "current_champion_title": "", "championship_level": "", "championship_partner": "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        "title_defended_same_card": "FALSE", "title_lost_same_card": "FALSE",
        "elim_number": "", "elim_number_status": "N/A" if is_winner else "UNKNOWN",
        "eliminated_by_ids": "",
        "elimination_clock_time": secs_to_mmss(elim_ts[name]) if has_elim_ts else "",
        "elimination_clock_seconds": elim_ts[name] if has_elim_ts else "",
        "ring_time": ring_time, "ring_time_seconds": ring_time_s,
        "ring_time_status": "CONFIRMED",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "FALSE",
        "is_final_two": "FALSE", "is_final_three": "FALSE", "is_final_four": "FALSE",
        "surprise_entrant": "FALSE",
        "legend_returning": "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE",
        "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": row_quality,
        "source_ids": "S101;S102;S103" if is_winner else "S101",
        "notes": note,
    }
    entrant_rows.append(er)

with open(os.path.join(DATA_DIR, "entrants.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ENTRANTS_FIELDS)
    for er in entrant_rows:
        writer.writerow(er)

# No eliminations.csv rows this pass -- zero individually-named eliminator
# credit exists anywhere in this year's source (see docstring / F269).

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F267", EVENT_ID, "entrants", "*", "entry_number", "unverified",
     "UNLIKE 2009/2011/2012, this year's 'time between buzzers' list is UNNAMED (28 bare durations only) -- "
     "and because several gap values repeat, full 30-entrant entry order is not reliably derivable from this "
     "document alone. Only 7 entrants are confidently positioned this pass, each anchored by an explicit S101 "
     "prose statement naming them at a specific numbered position (Brodus Clay=13, Rey Mysterio=14, Darren "
     "Young=15, Bo Dallas=16, Kane=24, Zack Ryder=25, cross-checked via buzzer-gap arithmetic; John Cena=19, "
     "additionally corroborated by S102/S103 and marked CONFIRMED rather than DERIVED). Dolph Ziggler and "
     "Chris Jericho are confidently the #1/#2 entrants AS A SET (both pre-bell, per S101's own explicit "
     "statement) but their order relative to EACH OTHER is not stated by any source consulted this pass -- "
     "left UNKNOWN. The remaining 21 entrants have known survival time but entirely UNKNOWN entry position "
     "this pass. Pending a future external fact-check pass (Wikipedia and similar sites typically carry a full "
     "named entry-order table for this era).",
     "S101", "open", "2026-09-17"),
    ("F268", EVENT_ID, "entrants", "dolph-ziggler;chris-jericho;brodus-clay;rey-mysterio;darren-young;bo-dallas;kane;zack-ryder", "elimination_clock_time", "unverified",
     "elimination_clock_time/elimination_clock_seconds are DERIVED (entry_actual + survival, per this script's "
     "buzzer-chain arithmetic) for these 8 entrants despite entry_number itself being UNKNOWN for 2 of them "
     "(Ziggler/Jericho, whose entry_actual is 0 regardless of #1-vs-#2 order). elim_number is left UNKNOWN for "
     "ALL 29 non-winner entrants, including these 8, since their rank within the FULL chronological elimination "
     "order (1-29) can't be determined without also knowing the elim_ts of the other 21 entrants, which remain "
     "entirely unrecoverable this pass. See F267.",
     "S101", "open", "2026-09-17"),
    ("F269", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "UNLIKE 2012, this year's Cageside prose (S101) contains ZERO individually-narrated eliminations -- "
     "eliminator credit is entirely UNKNOWN for all 29 non-winner entrants, and no eliminations.csv rows were "
     "created this pass. One aggregate (non-attributed) stat is known: per S103, Sheamus and Ryback each "
     "eliminated 5 wrestlers in this match, tied for the match high -- individual victims not named by any "
     "source consulted this pass, so not converted into structured elimination rows.",
     "S101;S103", "open", "2026-09-17"),
    ("F270", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 9 previously-unseen wrestlers this pass (Bo Dallas, Ryback, Cesaro, Titus O'Neil, "
     "Tensai, Brodus Clay, Sin Cara, Darren Young, Damien Sandow) with zero bio data in this pass's source -- "
     "names only. Left entirely UNKNOWN, same pattern as every prior year's equivalent flag.",
     "S101", "open", "2026-09-17"),
    ("F271", EVENT_ID, "events", EVENT_ID, "event_date;venue;attendance_reported;commentary_team;referees", "unverified",
     "Like 2009/2011/2012, Shane's document has NO separate Dan Wahlers narrative history chapter for 2013 -- "
     "only the Cageside timing analysis. Event-level facts a Wahlers chapter normally supplies (exact date, "
     "venue, city, attendance, commentary team, referees, undercard results) are simply absent from the source "
     "and left entirely UNKNOWN this pass. event_date is stored as '2013-XX-XX' -- the year itself is not in "
     "doubt, only the exact month/day are unconfirmed. Pending a future external-research pass.",
     "S101", "open", "2026-09-17"),
    ("F272", EVENT_ID, "wrestlers", "tensai;sin-cara", "wrestler_id", "needs_human_judgement",
     "Two likely (but this-pass-unconfirmed) same-performer identity connections spotted while building this "
     "year: (1) 'Tensai' (2013 ring name) is very likely Matt Bloom, the same performer already merged into "
     "this database's 'prince-albert' wrestler_id (Prince Albert/Albert/A-Train, merged by the 2003-2007 "
     "fact-check pass with 2-source confirmation). (2) 'Sin Cara' as of this 2013 event is very likely Alberto "
     "Rodriguez, the same performer as this database's existing 'hunico' wrestler_id (2012 Royal Rumble entry), "
     "who took over the Sin Cara gimmick from the original performer (Luis Urive) in September 2012. Neither "
     "connection is stated or otherwise confirmed by any source consulted THIS pass, so both are left as "
     "separate, unmerged wrestler_ids per the project's 2-source identity-merge rule -- exactly the same "
     "cautious treatment this database gave 'a-train' before its own eventual merge. Flagged here for a future "
     "fact-check pass to resolve with proper citations.",
     "S101", "open", "2026-09-17"),
    ("F273", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-17"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2013", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2013-XX-XX", "venue": "UNKNOWN",
    "city_region": "UNKNOWN", "country": "UNKNOWN",
    "attendance_official": "", "attendance_reported": "",
    "entry_interval_seconds": 90, "entrant_count": 30, "duration_total": "55:07",
    "duration_status": "CONFIRMED",
    "winner_id": "john-cena", "runner_up_id": "",
    "final_two_ids": "", "final_three_ids": "", "final_four_ids": "",
    "first_entrant_id": "", "second_entrant_id": "", "final_entrant_id": "",
    "first_elimination_id": "", "last_elimination_before_winner_id": "",
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
        "John Cena's 2nd career Royal Rumble win (after 2008), entering at #19 -- per S103, one of only two "
        "wrestlers ever to win a 30-man Rumble from a draw between #9 and #21 (the other being Shawn Michaels "
        "in 1996). Dolph Ziggler (49:48) and Chris Jericho (47:54), this match's two pre-bell entrants, posted "
        "the two longest survival times of the match by a wide margin -- Jericho's entrance was a surprise "
        "return. Sheamus and Ryback each eliminated 5 wrestlers, tied for the match high; per S103, 2013 is one "
        "of only two years (with 2005) in which no single competitor eliminated 6 or more. Bo Dallas, then a "
        "lower-card talent, survived 21:33 -- the match's 6th-longest time, noted in S101 as a standout result. "
        "Kane, despite having wrestled in every Rumble since 1996, lasted only 1:30, having already competed in "
        "a tag match earlier on the card. The Godfather made his final Royal Rumble appearance this year, 20 "
        "years after his first (1993, as Papa Shango) -- per S102's trivia, competing under 5 different "
        "gimmicks across his Rumble history."
    ),
    "notes": (
        "Like 2009/2011/2012, this document has no Dan Wahlers narrative chapter for 2013 -- only the Cageside "
        "timing analysis. UNLIKE those years, this year's buzzer-gap list is UNNAMED, so full entry order is "
        "NOT recoverable -- only 9 of 30 entrants (Ziggler/Jericho as a set, plus 7 individually anchored "
        "positions) have known or partially-known entry data; the other 21 have CONFIRMED-quality survival time "
        "but UNKNOWN entry position. See F267/F268. Eliminator credit is entirely UNKNOWN -- zero individually "
        "narrated eliminations exist in this year's source, the sparsest year for eliminator credit built so "
        "far among the post-2007 'Cageside-only' years. See F269. Winner (John Cena, entry #19) is CONFIRMED "
        "via 3 independent lines of evidence (2 separate trivia articles plus this script's own internal "
        "checksum). Runner-up and final-two/three/four are UNKNOWN this pass -- not guessed despite some "
        "candidate elim_ts values being computable, since 21 other entrants' elim_ts remain entirely unknown "
        "and could fall later. Event-level facts (date, venue, attendance, commentary, undercard) remain "
        "UNKNOWN -- see F271. Two identity-merge candidates (Tensai/prince-albert, Sin Cara/hunico) spotted but "
        "left unmerged pending 2-source confirmation -- see F272."
    ),
    "data_quality_status": "PROBABLE", "source_ids": "S101;S102;S103",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2013 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, 0 elimination rows "
      f"(no individually-named eliminator credit exists this year), "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
