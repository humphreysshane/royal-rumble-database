# -*- coding: utf-8 -*-
"""
Builds all rows for the 1999 Royal Rumble -- schema v2.

Rich year like 1991/1993/1995/1997: Shane's doc has a full "1999 Rumble
Stats - Cageside" frame-by-frame timing analysis (survival times, entrance
times, time-between-buzzers, ring crowdedness) PLUS the Dan Wahlers
narrative history section, both under the "1999 Royal Rumble Stats"
Heading-1.

SOURCES CONSULTED THIS PASS:
  S044 '1999 Rumble Stats - Cageside' section (Shane's doc)              tier 9
  S045 Dan Wahlers, 'History of the Royal Rumble' -- 1999 chapter        tier 9

METHODOLOGY (mirrors 1997's DERIVED elimination-order pattern, see F083):
  entry_actual[name] = cumulative buzzer-gap time (time elapsed since the
  match started, i.e. since Austin/McMahon's confrontation began) +
  entrance_lag[name] (buzzer-to-ring-entry time). elim_ts[name] =
  entry_actual[name] + survival_time[name] (both given directly by S044).
  All 30 entrants are then ranked by elim_ts to derive elim_number.
  Multiple internal checksums in S044 itself validate this: the cumulative
  buzzer sum lands exactly on the stated "46m 41s" final-buzzer mark, the
  entrance-time sum lands exactly on the stated "9m 38s", and computing who
  was still active when Chyna (the final, #30 entrant) walked out produces
  exactly the 9 names S044 lists by name for the match's final segment
  (Austin, McMahon, Big Boss Man, Triple H, Val Venis, Mark Henry, D-Lo
  Brown, Owen Hart, Chyna) -- all three independently confirming the
  derivation below is correct. See the assert checkpoints in this script.

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order and survival ("ring") time are known to the second for ALL
    30 entrants -- the richest year in the database so far for entry data.
  - Eliminator CREDIT, by contrast, is sparse: only 4 named eliminations
    exist across both sources -- Steve Austin eliminated Owen Hart, Triple
    H, and Jeff Jarrett (explicitly named; Austin is credited with "eight
    guys in total," with the other ~5 left unspecified rather than
    guessed), Chyna eliminated Mark Henry (per S044's ring-crowdedness
    commentary), and Vince McMahon eliminated Steve Austin (the winning
    elimination). Big Boss Man being "the last to go" right before "it was
    down to Austin and Vince again" strongly implies he was Austin's 4th
    named elimination, but this is contextual inference, not a direct
    statement -- kept PROBABLE. See F119.
  - FOUR camera-cut timing uncertainties are explicitly documented by S044
    itself (Droz's entrance -- 24s camera cut; Tiger Ali Singh's entrance
    -- 33s cut; Mabel's elimination -- 22s "lights out" interval; Ken
    Shamrock's entrance -- 13s cut). S044's own stated methodology ("I
    simply took the midpoint of the given time interval endpoints") is
    followed, with each affected entrant's ring_time/entry timing kept
    PROBABLE (with the stated margin of error preserved in notes) rather
    than CONFIRMED, mirroring 1997's F083 treatment of similar camera
    issues. See F120.
  - MABEL'S ELIMINATION is a genuinely unusual case: he was abducted from
    outside the ring by The Undertaker (playing on his then-current dark
    "Ministry"-adjacent storyline) during a "lights out" segment, rather
    than being physically thrown from the ring by an opponent inside it.
    S044 explicitly still counts this as an official Rumble elimination.
    The Undertaker (existing wrestler_id the-undertaker) is credited as
    eliminator despite NOT being a Rumble entrant this year himself (no
    entrant row is added for him) -- a similar "credited eliminator who
    wasn't a numbered entrant" situation to 1998's Triple H/crutch case,
    see F121.
  - Steve Austin and Vince McMahon are both credited with the FULL match
    duration (56:38) as their official ring_time, per S044's explicit
    statement ("I am officially giving them credit for the full match"),
    even though both men were physically absent from the ring for large
    stretches (Austin ambushed backstage, McMahon on commentary). S044's
    own "adjusted for absences" alternate figures (Austin 25:55, McMahon
    6:58) are preserved in each entrant's notes field as a genuinely
    interesting supplementary stat rather than used as the official value.
  - "X-Pac" is widely known in general wrestling history as the same
    performer who wrestled as "1-2-3 Kid" in this database's 1996 build
    (wrestler_id 1-2-3-kid) -- but NEITHER source consulted this pass
    states that connection directly (contrast with the Chainsaw Charlie/
    Terry Funk and Ringmaster/Steve Austin precedents, where the source
    ITSELF made the identity explicit). Per this project's 2-independent-
    source identity-merge rule, X-Pac is left as its own new wrestler_id
    rather than merged, with a flag for a future fact-check pass. See
    F118 -- same caution class as Kama/Bob Holly (1996) and Doink
    (1994/1995).
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
EVENT_ID = "RR1999M"


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
    ("S044", "'1999 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers, ring "
     "crowdedness) filed under the '1999 Royal Rumble Stats' Heading-1. Explicitly documents 4 camera-cut "
     "timing uncertainties (Droz, Tiger Ali Singh, Mabel, Ken Shamrock) and gives Austin/McMahon full-match "
     "credit despite lengthy absences -- see F120 and script docstring. NOT live-fetched this pass."),
    ("S045", "Dan Wahlers, 'History of the Royal Rumble' -- 1999 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance (14,816), full narrative "
     "history (the Rock/Foley 'I Quit' Match, the Austin/McMahon storyline that dominated the Rumble match "
     "itself, Austin's 8 credited eliminations), and undercard match results."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# TIMING DERIVATION
# ---------------------------------------------------------------------------
# (name, buzzer_gap) in chronological order -- "Time Between Buzzers", 28 buzzers
# for entrants #3-#30 (Austin=#1, McMahon=#2 entered before the match/buzzers began).
buzzer_gaps = [
    ("Golga", "1:37"), ("Droz", "1:45"), ("Edge", "1:11"), ("Gillberg", "1:31"),
    ("Steve Blackman", "2:10"), ("Dan Severn", "1:32"), ("Tiger Ali Singh", "1:34"),
    ("Blue Meanie", "1:40"), ("Mabel", "1:30"), ("Road Dogg", "1:34"), ("Gangrel", "2:31"),
    ("Kurrgan", "1:19"), ("Al Snow", "1:26"), ("Goldust", "1:39"), ("Godfather", "1:34"),
    ("Kane", "1:36"), ("Ken Shamrock", "1:51"), ("Billy Gunn", "1:48"), ("Test", "1:36"),
    ("Big Boss Man", "1:31"), ("Triple H", "1:34"), ("Val Venis", "1:32"), ("X-Pac", "1:40"),
    ("Mark Henry", "1:38"), ("Jeff Jarrett", "1:36"), ("D-Lo Brown", "1:44"),
    ("Owen Hart", "2:19"), ("Chyna", "1:43"),
]
buzzer_time = {}
cum = 0
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("46:41"), f"buzzer checksum failed: {cum}"

# Entrance times (buzzer sound -> stepping into the ring). Austin/McMahon excluded
# (their entrances preceded the match). Margin-of-error notes preserved in ELIM_NOTE.
entrance_lag = {
    "Mabel": "1:04", "Godfather": "0:49", "Gillberg": "0:40", "Kane": "0:39",
    "Ken Shamrock": "0:39", "Big Boss Man": "0:35", "Golga": "0:27",
    "Jeff Jarrett": "0:26", "D-Lo Brown": "0:26", "Chyna": "0:25",
    "Tiger Ali Singh": "0:23", "Gangrel": "0:18", "Mark Henry": "0:15",
    "Owen Hart": "0:15", "Dan Severn": "0:14", "Droz": "0:12", "Test": "0:12",
    "Al Snow": "0:12", "Edge": "0:11", "Blue Meanie": "0:10", "Triple H": "0:10",
    "Road Dogg": "0:09", "X-Pac": "0:09", "Steve Blackman": "0:08", "Kurrgan": "0:08",
    "Goldust": "0:08", "Billy Gunn": "0:07", "Val Venis": "0:07",
}
lag_sum = sum(mmss(v) for v in entrance_lag.values())
assert lag_sum == mmss("9:38"), f"entrance-lag checksum failed: {lag_sum}"

entry_actual = {"Steve Austin": 0, "Vince McMahon": 0}
for name in buzzer_time:
    entry_actual[name] = buzzer_time[name] + mmss(entrance_lag[name])
assert entry_actual["Chyna"] == mmss("47:06")

# Survival ("ring") times, as stated directly by S044.
survival = {
    "Steve Austin": "56:38", "Vince McMahon": "56:38", "Big Boss Man": "18:55",
    "Triple H": "14:21", "Val Venis": "12:42", "Droz": "12:38", "Edge": "11:51",
    "Test": "11:49", "Road Dogg": "10:41", "D-Lo Brown": "9:11", "Mark Henry": "7:57",
    "Steve Blackman": "7:21", "Billy Gunn": "7:08", "Kurrgan": "6:54", "Owen Hart": "6:32",
    "X-Pac": "5:44", "Dan Severn": "5:42", "Ken Shamrock": "4:52", "Tiger Ali Singh": "4:06",
    "Goldust": "4:02", "Jeff Jarrett": "3:38", "Blue Meanie": "3:00", "Godfather": "1:39",
    "Mabel": "1:18", "Kane": "0:53", "Al Snow": "0:47", "Chyna": "0:35", "Gangrel": "0:26",
    "Golga": "0:14", "Gillberg": "0:07",
}

elim_ts = {}
for name, t in survival.items():
    if name in ("Steve Austin", "Vince McMahon"):
        continue  # handled separately below -- Austin is the last elimination, McMahon never eliminated
    elim_ts[name] = entry_actual[name] + mmss(t)
elim_ts["Steve Austin"] = mmss("56:38")  # eliminated at the very end by McMahon, the winning elimination

# Checkpoint: everyone still active when Chyna (final entrant, #30) walked in at 47:06
# should be exactly the 9 names S044 names for the match's final segment.
still_active_at_chyna_entry = {n for n, ts in elim_ts.items() if ts > entry_actual["Chyna"]} | {"Vince McMahon"}
FINAL_NINE = {"Steve Austin", "Vince McMahon", "Big Boss Man", "Triple H", "Val Venis",
              "Mark Henry", "D-Lo Brown", "Owen Hart", "Chyna"}
assert still_active_at_chyna_entry == FINAL_NINE, still_active_at_chyna_entry

elim_order_list = sorted(elim_ts, key=lambda n: elim_ts[n])
elim_number = {name: i + 1 for i, name in enumerate(elim_order_list)}
assert elim_number["Golga"] == 1 and elim_number["Gillberg"] == 2
assert elim_number["Steve Austin"] == 29  # last eliminated, McMahon (never eliminated) is the winner

ENTRY_NUMBERS = {"Steve Austin": 1, "Vince McMahon": 2}
for i, (name, _) in enumerate(buzzer_gaps):
    ENTRY_NUMBERS[name] = i + 3
assert ENTRY_NUMBERS["Droz"] == 4 and ENTRY_NUMBERS["Tiger Ali Singh"] == 9 and ENTRY_NUMBERS["Chyna"] == 30

CAMERA_ISSUE = {"Droz", "Tiger Ali Singh", "Mabel", "Ken Shamrock"}
CAMERA_NOTE = {
    "Droz": "S044: camera cut away for 24s right as his entrance buzzer sounded; entrance/survival time is the midpoint estimate, margin of error ~12s.",
    "Tiger Ali Singh": "S044: camera cut away for 33s during his entrance; entrance/survival time is the midpoint estimate, margin of error ~17s.",
    "Mabel": "S044: the arena lights went out for 22s during his abduction by The Undertaker; elimination time is the midpoint estimate, margin of error ~11s -- see F121.",
    "Ken Shamrock": "S044: camera cut away for 13s during his entrance; entrance/survival time is the midpoint estimate, margin of error ~7s.",
}

# name -> (eliminator names, data_quality_status, elimination_method)
KNOWN_ELIMINATORS = {
    "Owen Hart": (["Steve Austin"], "CONFIRMED", "Tossed out by Steve Austin, part of his rampage against everyone chasing the $100,000 McMahon bounty on Austin's own head."),
    "Triple H": (["Steve Austin"], "CONFIRMED", "Tossed out by Steve Austin."),
    "Jeff Jarrett": (["Steve Austin"], "CONFIRMED", "Tossed out by Steve Austin."),
    "Big Boss Man": (["Steve Austin"], "PROBABLE", "Contextually implied as Austin's 4th and final named elimination ('Bossman was the last to go, and it was down to Austin and Vince again') of his stated 8 total -- not explicitly named as an Austin elimination, so kept PROBABLE. See F119."),
    "Mark Henry": (["Chyna"], "CONFIRMED", "Eliminated by Chyna, per S044's ring-crowdedness commentary -- Chyna's only credited elimination this match, and a notable trivia point as she became the first woman to accumulate survival time in a Royal Rumble."),
    "Steve Austin": (["Vince McMahon"], "CONFIRMED", "The winning elimination -- McMahon dumped Austin over the top rope from behind while Austin was distracted by The Rock at ringside."),
    "Mabel": (["The Undertaker"], "CONFIRMED", "Abducted from outside the ring during a 'lights out' angle involving The Undertaker's Ministry-adjacent group -- an outside-interference elimination rather than a standard in-ring toss. The Undertaker was not a Rumble entrant this year (no entrant row added for him) -- see F121."),
}

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Golga", "John Tenta", "CONFIRMED", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Real name given directly in S044's survival-time list ('Golga (John Tenta)').", "S044"),
    ("Droz", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entrance timing affected by a 24-second camera cut -- see F120.", "S044;S045"),
    ("Edge", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S044;S045"),
    ("Gillberg", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Shortest survival time of the match (7 seconds) -- his entrance (40s) was 'more than 5 times as long as his survival time' per S044.", "S044"),
    ("Dan Severn", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S044"),
    ("Tiger Ali Singh", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entrance timing affected by a 33-second camera cut -- see F120.", "S044"),
    ("Blue Meanie", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S044"),
    ("Gangrel", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Also lost the WWF European Championship match to X-Pac earlier on the same card.", "S044;S045"),
    ("Al Snow", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S044"),
    ("The Godfather", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S044"),
    ("Kane", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "S044 notes that, of the (then) 3 Rumble matches including Kane it had timed, his longest survival time was 1m36s -- this appearance (53s) is shorter still.", "S044"),
    ("X-Pac", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Possibly the same performer as '1-2-3 Kid' (this database's 1996 wrestler_id 1-2-3-kid, Sean Waltman) -- neither source consulted this pass states the connection directly, so left as a separate wrestler_id pending future verification. See F118.", "S044;S045"),
    ("Test", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S044"),
    ("Big Boss Man", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Part of Vince McMahon's Corporation; 'the last to go' before the Austin/McMahon final confrontation -- probably Austin's 4th named elimination, see F119.", "S044;S045"),
    ("Val Venis", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S044"),
    ("Chyna", "", "UNKNOWN", "F", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "The final (#30) entrant. Per S044, the first woman to ever accumulate survival time in a Royal Rumble match. Credited with eliminating Mark Henry.", "S044"),
]

reused = {
    "Steve Austin": "steve-austin", "Vince McMahon": "vince-mcmahon", "Road Dogg": "jesse-james",
    "Kurrgan": "kurrgan", "Goldust": "goldust", "Ken Shamrock": "ken-shamrock",
    "Billy Gunn": "billy-gunn", "Triple H": "hunter-hearst-helmsley", "Owen Hart": "owen-hart",
    "Mark Henry": "mark-henry", "Jeff Jarrett": "jeff-jarrett", "D-Lo Brown": "d-lo-brown",
    "Mabel": "mabel", "Steve Blackman": "steve-blackman",
    # Non-entrant, credited as an interference eliminator only -- see F121.
    "The Undertaker": "the-undertaker",
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

# Map the timing-derivation dicts' key spellings to wrestlers.csv-registered names
# where they differ (e.g. "Godfather" in timing data vs "The Godfather" as registered).
NAME_ALIASES = {"Godfather": "The Godfather"}
def wid_of(name):
    return wrestler_ids[NAME_ALIASES.get(name, name)]

# ---------------------------------------------------------------------------
# ENTRANTS -- all 30, full entry order and survival time known.
# ---------------------------------------------------------------------------
all_names = [
    "Steve Austin", "Vince McMahon", "Golga", "Droz", "Edge", "Gillberg", "Steve Blackman",
    "Dan Severn", "Tiger Ali Singh", "Blue Meanie", "Mabel", "Road Dogg", "Gangrel", "Kurrgan",
    "Al Snow", "Goldust", "Godfather", "Kane", "Ken Shamrock", "Billy Gunn", "Test",
    "Big Boss Man", "Triple H", "Val Venis", "X-Pac", "Mark Henry", "Jeff Jarrett",
    "D-Lo Brown", "Owen Hart", "Chyna",
]
assert len(all_names) == 30

FINAL_FOUR = {"Vince McMahon", "Steve Austin", "D-Lo Brown", "Big Boss Man"}
FINAL_THREE = {"Vince McMahon", "Steve Austin", "Big Boss Man"}
FINAL_TWO = {"Vince McMahon", "Steve Austin"}

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wid_of(name)
    is_winner = (name == "Vince McMahon")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)
    ring_time_status = "PROBABLE" if name in CAMERA_ISSUE else "CONFIRMED"

    elim_by, dq, method = KNOWN_ELIMINATORS.get(name, ([], "", ""))

    notes_parts = []
    if name in CAMERA_ISSUE:
        notes_parts.append(CAMERA_NOTE[name])
    if name == "Steve Austin":
        notes_parts.append("Officially credited with the full 56:38 match per S044; adjusted for his backstage-ambush absence, his actual active ring time was 25:55.")
    if name == "Vince McMahon":
        notes_parts.append("Officially credited with the full 56:38 match per S044 (he entered #2 and was never eliminated); adjusted for his commentary-booth absence, his actual active ring time was 6:58.")
    if name == "Road Dogg":
        notes_parts.append("Billed as 'Road Dog Jesse James' in this era; also lost the opening match to Big Boss Man earlier the same night -- see other_matches.csv.")
    if name == "Chyna":
        notes_parts.append("Final (#30) entrant. First woman to accumulate survival time in a Royal Rumble match, per S044.")
    if name == "X-Pac":
        notes_parts.append("See F118 -- possible but unverified identity connection to this database's 1996 wrestler_id 1-2-3-kid.")
    note = " ".join(notes_parts)

    for eliminator in elim_by:
        eliminator_wid = wid_of(eliminator)
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": elim_number[name],
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": eliminator_wid,
            "assisting_wrestler_ids": "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": ENTRY_NUMBERS.get(eliminator, ""),
            "elimination_clock_time": secs_to_mmss(elim_ts[name]),
            "elimination_clock_seconds": elim_ts[name],
            "elimination_type": "over_top_rope",
            "elimination_method": method,
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "TRUE", "is_shared": "FALSE",
            "is_accidental": "FALSE", "is_self_elimination": "FALSE",
            "is_storyline_related": "TRUE" if name in ("Mabel", "Steve Austin") else "UNKNOWN",
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE", "simultaneous_group_id": "",
            "data_quality_status": dq,
            "source_ids": "S044;S045" if name in ("Owen Hart", "Triple H", "Jeff Jarrett", "Big Boss Man", "Steve Austin", "Mabel") else "S044",
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
        "gimmick_at_event": "Sexual Chocolate" if name == "Mark Henry" else "",
        "manager_at_event": "",
        "tag_team_name": "",
        "faction_stable": "The Corporation" if name in ("Vince McMahon", "Big Boss Man") else "",
        "current_champion_title": "WWF Intercontinental Championship" if name == "Ken Shamrock" else "",
        "championship_level": "Intercontinental" if name == "Ken Shamrock" else "",
        "championship_partner": "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        "title_defended_same_card": "TRUE" if name == "Ken Shamrock" else "FALSE",
        "title_lost_same_card": "FALSE",
        "elim_number": "" if is_winner else elim_number[name], "elim_number_status": "N/A" if is_winner else "CONFIRMED",
        "eliminated_by_ids": ";".join(wid_of(e) for e in elim_by),
        "elimination_clock_time": "" if is_winner else secs_to_mmss(elim_ts[name]),
        "elimination_clock_seconds": "" if is_winner else elim_ts[name],
        "ring_time": ring_time, "ring_time_seconds": ring_time_s,
        "ring_time_status": ring_time_status,
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if name == "Steve Austin" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "FALSE", "legend_returning": "FALSE", "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "TRUE" if name == "Dan Severn" else "FALSE",
        "wrestled_earlier_on_card": "TRUE" if name in ("Road Dogg", "Big Boss Man", "Ken Shamrock", "Billy Gunn", "X-Pac", "Gangrel") else "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S044;S045",
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
        er["solo_eliminations_count"] = len(credited)
        er["assisted_eliminations_count"] = 0

with open(os.path.join(DATA_DIR, "entrants.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ENTRANTS_FIELDS)
    for er in entrant_rows:
        writer.writerow(er)

with open(os.path.join(DATA_DIR, "eliminations.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ELIMINATIONS_FIELDS)
    for row in elim_rows:
        writer.writerow(row)

# ---------------------------------------------------------------------------
# OTHER MATCHES ON THE SAME CARD (only wrestlers already carrying a
# wrestler_id in this database).
# ---------------------------------------------------------------------------
other_matches = [
    ("Big Boss Man", 1, "Road Dogg", "", "Singles", "FALSE", "", "FALSE", "Win", "", "", "11:52", "Opener", "S045", "Pinned 'Road Dog' Jesse James. Also competed in the Rumble match this same night."),
    ("Road Dogg", 1, "Big Boss Man", "", "Singles", "FALSE", "", "FALSE", "Loss", "", "", "11:52", "Opener", "S045", "Pinned by Big Boss Man. Also competed in the Rumble match this same night."),
    ("Ken Shamrock", 2, "Billy Gunn", "", "Singles", "TRUE", "Intercontinental Championship", "TRUE", "Win", "", "", "11:52", "2nd match", "S045", "Defeated Billy Gunn via submission to retain the I-C Title. Also competed in the Rumble match this same night."),
    ("Billy Gunn", 2, "Ken Shamrock", "", "Singles", "TRUE", "Intercontinental Championship", "FALSE", "Loss", "", "", "11:52", "2nd match", "S045", "Lost to Ken Shamrock via submission. Also competed in the Rumble match this same night."),
    ("X-Pac", 3, "Gangrel", "", "Singles", "TRUE", "European Championship", "TRUE", "Win", "", "", "5:53", "3rd match", "S045", "Pinned Gangrel to retain the European Title. Also competed in the Rumble match this same night."),
    ("Gangrel", 3, "X-Pac", "", "Singles", "TRUE", "European Championship", "FALSE", "Loss", "", "", "5:53", "3rd match", "S045", "Pinned by X-Pac. Also competed in the Rumble match this same night."),
]
with open(os.path.join(DATA_DIR, "other_matches.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for (name, mnum, opponents, partners, mtype, is_title, title, was_champ, result, won_t, lost_t, duration, position, row_src, notes) in other_matches:
        pid = wid_of(name)
        writer.writerow([EVENT_ID, pid, mnum, opponents, partners, mtype, is_title, title, was_champ,
                          result, won_t, lost_t, duration, position, "", "PROBABLE", row_src, notes])

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F118", EVENT_ID, "wrestlers", "x-pac", "wrestler_id", "needs_human_judgement",
     "X-Pac is widely known in general wrestling history to be the same performer (Sean Waltman) who wrestled "
     "as '1-2-3 Kid' in this database's 1996 build (wrestler_id 1-2-3-kid). Neither source consulted this pass "
     "states that connection directly -- contrast with the Chainsaw Charlie/Terry Funk (1998) and Ringmaster/"
     "Steve Austin (1996) precedents, where the source itself made the identity explicit. Left as a separate, "
     "new wrestler_id pending a future fact-check pass with 2 independent sources -- same caution class as "
     "Kama/Bob Holly (1996's F076/F078) and Doink (1994/1995's F071/F099).",
     "S044;S045", "open", "2026-09-16"),
    ("F119", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "Despite 1999 being this database's richest year yet for entry/survival timing data (all 30 entrants "
     "known to the second), eliminator CREDIT is unusually sparse -- only 4 of 29 eliminations have a named "
     "eliminator across both sources (Steve Austin eliminated Owen Hart, Triple H, and Jeff Jarrett by name; "
     "Chyna eliminated Mark Henry; Vince McMahon eliminated Steve Austin for the win). S045 states Austin "
     "eliminated 'eight guys in total,' and Big Boss Man being 'the last to go' right before the Austin/"
     "McMahon final confrontation strongly implies he was a 4th Austin elimination -- kept PROBABLE rather "
     "than CONFIRMED since it isn't a direct statement. The remaining ~4 of Austin's 8, and all other "
     "eliminator credits, are left UNKNOWN rather than guessed.",
     "S044;S045", "open", "2026-09-16"),
    ("F120", EVENT_ID, "entrants", "droz;tiger-ali-singh;mabel;ken-shamrock", "ring_time;entry_number", "unverified",
     "S044 itself explicitly documents 4 camera-cut timing uncertainties this year -- Droz's entrance (24s "
     "cut), Tiger Ali Singh's entrance (33s cut), Mabel's elimination (22s 'lights out' interval), and Ken "
     "Shamrock's entrance (13s cut) -- and states its own methodology of taking the midpoint of each interval. "
     "That midpoint value is used here with ring_time_status=PROBABLE (margin of error preserved in each "
     "entrant's notes field) rather than CONFIRMED, mirroring 1997's F083 treatment of the same kind of issue.",
     "S044", "open", "2026-09-16"),
    ("F121", EVENT_ID, "eliminations", "mabel", "eliminator_wrestler_id", "needs_human_judgement",
     "Mabel's elimination is a genuinely unusual case -- he was abducted from outside the ring by The "
     "Undertaker during a 'lights out' angle (his Ministry-adjacent storyline group), rather than being "
     "physically thrown from the ring by an opponent inside it. S044 explicitly still counts this as an "
     "official Rumble elimination. The Undertaker (existing wrestler_id the-undertaker) is credited as "
     "eliminator despite not being a Rumble entrant this year -- no entrant row was added for him, similar to "
     "how 1998's Triple H received elimination credit (Owen Hart, via a crutch) without taking a numbered "
     "entry -- see 1998's F113.",
     "S044;S045", "open", "2026-09-16"),
    ("F122", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 16 previously-unseen wrestlers this pass (Golga, Droz, Edge, Gillberg, Dan Severn, "
     "Tiger Ali Singh, Blue Meanie, Gangrel, Al Snow, The Godfather, Kane, X-Pac, Test, Big Boss Man, Val "
     "Venis, Chyna) -- Golga's real name (John Tenta) is given directly by S044 (CONFIRMED); everyone else is "
     "names-only, left entirely UNKNOWN.",
     "S044", "open", "2026-09-16"),
    ("F123", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-16"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 1999", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "1999-01-24", "venue": "Arrowhead Pond",
    "city_region": "Anaheim, California", "country": "United States",
    "attendance_official": "", "attendance_reported": 14816,
    "entry_interval_seconds": 90, "entrant_count": 30, "duration_total": "56:38",
    "duration_status": "CONFIRMED",
    "winner_id": "vince-mcmahon", "runner_up_id": "steve-austin",
    "final_two_ids": "vince-mcmahon;steve-austin",
    "final_three_ids": "vince-mcmahon;steve-austin;big-boss-man",
    "final_four_ids": "vince-mcmahon;steve-austin;d-lo-brown;big-boss-man",
    "first_entrant_id": "steve-austin", "second_entrant_id": "vince-mcmahon", "final_entrant_id": "chyna",
    "first_elimination_id": "golga", "last_elimination_before_winner_id": "steve-austin",
    "eliminations_count": 29, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": "UNKNOWN",
    "champions_in_field_count": 1, "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Michael Cole, Jerry Lawler", "ring_announcer": "UNKNOWN",
    "referees": "Not identified in either source consulted this pass",
    "special_rules": (
        "Vince McMahon rigged the pre-show drawing (via a storyline) to make Steve Austin the #1 entrant, "
        "with new Commissioner Shawn Michaels then assigning McMahon himself #2 -- the only Rumble in this "
        "database where the eventual winner is confirmed to have entered at #2. A $100,000 storyline bounty "
        "was placed on Austin's head by McMahon's Corporation, driving most of the match's minimal wrestling "
        "action. Austin and McMahon were both absent from the ring for large stretches (Austin ambushed and "
        "taken away by ambulance, McMahon on commentary) but were both officially credited with the full "
        "match duration as their survival time -- see script docstring."
    ),
    "title_on_the_line": "FALSE",
    "championship_implications": "None in the Rumble match itself, though The Rock won the WWF Championship from Mick Foley in an 'I Quit' Match earlier on the same card, Ken Shamrock retained the Intercontinental Championship against Billy Gunn, and X-Pac retained the European Championship against Gangrel.",
    "winners_reward": "A WWF Championship match against Vince McMahon (rather than a title match against the actual champion) -- Austin instead got his WrestleMania shot via a Cage Match win over McMahon at St. Valentine's Day Massacre in February 1999, going on to beat The Rock for his 3rd WWF Title at WrestleMania XV, per S045",
    "historical_significance": (
        "Widely regarded as one of the worst-booked Royal Rumble matches in history -- the storyline (Austin "
        "vs. McMahon) completely overshadowed the in-ring action, with Vince McMahon becoming the only "
        "authority-figure/non-wrestler-style entrant to ever win a Royal Rumble. Chyna became the first woman "
        "to ever accumulate survival time in a Royal Rumble match. The undercard's Rock/Foley 'I Quit' Match "
        "is separately regarded as one of the most brutal, historically significant matches of the Attitude "
        "Era (later depicted in the documentary 'Beyond the Mat') -- Foley took a string of unprotected "
        "chairshots that he and others have cited as a contributing factor to his early retirement from full-"
        "time wrestling. Big Show's WWF debut followed one month later at the Austin/McMahon Cage Match "
        "rematch, per S045."
    ),
    "notes": (
        "The richest entry/survival-timing dataset in this database so far -- all 30 entrants timed to the "
        "second -- but eliminator credit is unusually sparse (only 4 of 29 eliminations are directly "
        "credited) -- see F119. Four entrants have camera-cut timing uncertainty -- see F120. Mabel's "
        "elimination (abducted outside the ring by The Undertaker) is a unique case -- see F121."
    ),
    "data_quality_status": "CONFIRMED", "source_ids": "S044;S045",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"1999 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
