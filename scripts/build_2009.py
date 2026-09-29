# -*- coding: utf-8 -*-
"""
Builds all rows for the 2009 Royal Rumble -- schema v2.

UNLIKE 2008 (and 2003/2005/2007 before it), Shane's doc has NO "Dan
Wahlers History of the Royal Rumble" section for 2009 at all -- only the
"2009 Rumble Stats - Cageside" frame-by-frame timing analysis. That means
event-level facts a Wahlers chapter normally supplies (attendance, venue,
exact date, commentary team, undercard results) are simply not present in
the document and are left UNKNOWN this pass, same treatment as any other
fact absent from the source. This is a NEW situation -- every prior
"sparse" year (1990/1994/1996/2000/2002/2004/2006) was thin on entry
order/timing but still had a Wahlers chapter for event-level facts; 2009
inverts that (rich timing, zero narrative).

SOURCES CONSULTED THIS PASS:
  S082 '2009 Rumble Stats - Cageside' section (Shane's doc)              tier 9

METHODOLOGY (mirrors 2007/2008's DERIVED elimination-order pattern):
entry_actual[name] = cumulative buzzer-gap time + entrance_lag[name].
elim_ts[name] = entry_actual[name] + survival_time[name]. Rey Mysterio and
John Morrison (the first two entrants) both start at entry_actual=0.
Checksums: the cumulative buzzer sum lands exactly on the stated "45:31"
final-buzzer mark (Big Show's entrance); Randy Orton's (the winner's) own
survival time of 48:28 is exactly (match total 58:37) minus his entry_
actual, and his eliminating Triple H is the final, winning elimination
landing exactly on 58:37. See asserts below.

ONE DERIVED GROUP ELIMINATION THIS YEAR: the Cageside prose itself (not a
separate narrative chapter) states "Kozlov entered the match and was
tasked with cleaning the ring of three bodies" during the ~2m04s window
before Triple H's entrance. Cross-referencing this script's own elim_ts
derivation, exactly 3 wrestlers (The Great Khali, MVP, Carlito) have
elimination timestamps falling inside that window, and none of the three
has any other credited eliminator -- DERIVED as Kozlov's 3 eliminations,
the same cross-reference methodology used for 2005's Muhammad Hassan
group (F183) and 2007's Khali 7th-victim derivation (F196).

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order and survival ("ring") time are known to the second for ALL
    30 entrants -- ring_time_status is CONFIRMED throughout.
  - Eliminator credit is otherwise almost entirely absent -- with no
    Wahlers narrative to mine, only Kozlov's DERIVED 3-man cleanup (above)
    is attributable. The other 25 elimination-eligible entrants have no
    named eliminator this pass.
  - Event-level facts (attendance, venue, date, commentary team, referees,
    undercard results) are entirely UNKNOWN -- no Wahlers chapter exists
    for this year in the source document. event_date is left blank rather
    than guessed from outside knowledge, per the project's document-first
    methodology.
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
EVENT_ID = "RR2009M"


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
    ("S082", "'2009 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers, ring "
     "crowdedness) filed under the '2009 Royal Rumble Stats' Heading-1. NO separate Dan Wahlers narrative "
     "history chapter exists for this year in Shane's document -- event-level facts (attendance, venue, exact "
     "date, commentary, undercard) are correspondingly UNKNOWN this pass. NOT live-fetched this pass."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# TIMING DERIVATION
# ---------------------------------------------------------------------------
buzzer_gaps = [
    ("Carlito", "1:32"), ("MVP", "1:46"), ("The Great Khali", "1:33"), ("Vladimir Kozlov", "1:30"),
    ("Triple H", "1:48"), ("Randy Orton", "1:42"), ("JTG", "1:38"), ("Ted DiBiase Jr.", "1:35"),
    ("Chris Jericho", "1:35"), ("Mike Knox", "1:53"), ("The Miz", "1:32"), ("Finlay", "1:37"),
    ("Cody Rhodes", "1:40"), ("The Undertaker", "1:39"), ("Goldust", "1:39"), ("CM Punk", "1:38"),
    ("Mark Henry", "1:31"), ("Shelton Benjamin", "1:32"), ("William Regal", "1:35"), ("Kofi Kingston", "1:33"),
    ("Kane", "1:39"), ("R-Truth", "1:52"), ("Rob Van Dam", "1:33"), ("The Brian Kendrick", "1:36"),
    ("Dolph Ziggler", "1:37"), ("Santino Marella", "1:34"), ("Jim Duggan", "1:38"), ("Big Show", "1:34"),
]
buzzer_time = {}
cum = 0
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("45:31"), f"buzzer checksum failed: {cum}"

# Entrance times. Rey Mysterio and John Morrison (pre-bell) excluded.
entrance_lag = {
    "Big Show": "0:47", "Triple H": "0:32", "The Undertaker": "0:31", "The Great Khali": "0:30",
    "JTG": "0:25", "The Brian Kendrick": "0:25", "Rob Van Dam": "0:24", "Chris Jericho": "0:21", "Kane": "0:20",
    "Randy Orton": "0:18", "Goldust": "0:17", "Mark Henry": "0:17", "Vladimir Kozlov": "0:16", "Jim Duggan": "0:15",
    "Shelton Benjamin": "0:14", "CM Punk": "0:13", "William Regal": "0:13", "Ted DiBiase Jr.": "0:12", "Cody Rhodes": "0:12",
    "R-Truth": "0:12", "Finlay": "0:11", "Kofi Kingston": "0:11", "Santino Marella": "0:11", "Mike Knox": "0:10",
    "The Miz": "0:10", "Dolph Ziggler": "0:09", "Carlito": "0:07", "MVP": "0:06",
}
entry_actual = {"Rey Mysterio": 0, "John Morrison": 0}
for name in buzzer_time:
    entry_actual[name] = buzzer_time[name] + mmss(entrance_lag[name])

# Survival ("ring") times, as stated directly by S082. Randy Orton (the
# winner) is included with a survival time that is his entry-to-match-end
# span, not an elimination -- excluded from elim_ts below.
survival = {
    "Triple H": "49:56", "Rey Mysterio": "49:25", "Randy Orton": "48:28", "Ted DiBiase Jr.": "45:12",
    "Chris Jericho": "37:16", "Cody Rhodes": "37:01", "Mike Knox": "32:43", "The Undertaker": "32:30",
    "Finlay": "29:59", "CM Punk": "22:29", "John Morrison": "19:32", "Kane": "18:21", "Rob Van Dam": "13:56",
    "R-Truth": "12:06", "JTG": "11:58", "Big Show": "9:33", "Kofi Kingston": "6:58", "Carlito": "6:11",
    "William Regal": "4:33", "Shelton Benjamin": "4:17", "MVP": "3:52", "Mark Henry": "3:14", "Jim Duggan": "2:50",
    "Vladimir Kozlov": "2:41", "The Great Khali": "1:31", "The Miz": "1:19", "Goldust": "1:11",
    "Dolph Ziggler": "0:22", "The Brian Kendrick": "0:15", "Santino Marella": "0:02",
}
assert mmss(survival["Randy Orton"]) == mmss("58:37") - entry_actual["Randy Orton"]

elim_ts = {}
for name, t in survival.items():
    if name == "Randy Orton":
        continue  # winner, never eliminated
    elim_ts[name] = entry_actual[name] + mmss(t)
assert elim_ts["Triple H"] == mmss("58:37")  # the winning elimination, by Randy Orton

# Cross-check: Kozlov's stated "cleaning the ring of three bodies" during the
# window before Triple H's entrance.
KOZLOV_WINDOW = (entry_actual["Vladimir Kozlov"], entry_actual["Triple H"])
kozlov_cleanup = [n for n in elim_ts if KOZLOV_WINDOW[0] <= elim_ts[n] < KOZLOV_WINDOW[1] and n != "Vladimir Kozlov"]
assert set(kozlov_cleanup) == {"The Great Khali", "MVP", "Carlito"}, kozlov_cleanup

elim_order_list = sorted(elim_ts, key=lambda n: elim_ts[n])
elim_number = {name: i + 1 for i, name in enumerate(elim_order_list)}
assert elim_number["The Great Khali"] == 1
assert elim_number["Triple H"] == 29

ENTRY_NUMBERS = {"Rey Mysterio": 1, "John Morrison": 2}
for i, (name, _) in enumerate(buzzer_gaps):
    ENTRY_NUMBERS[name] = i + 3
assert ENTRY_NUMBERS["Vladimir Kozlov"] == 6 and ENTRY_NUMBERS["Triple H"] == 7
assert ENTRY_NUMBERS["Big Show"] == 30

FINAL_FOUR = {"Randy Orton", "Triple H", "Ted DiBiase Jr.", "Cody Rhodes"}
FINAL_THREE = {"Randy Orton", "Triple H", "Cody Rhodes"}
FINAL_TWO = {"Randy Orton", "Triple H"}

# name -> (eliminator names, data_quality_status, notes, is_shared, group_id)
KNOWN_ELIMINATORS = {
    "The Great Khali": (["Vladimir Kozlov"], "DERIVED", "DERIVED -- the Cageside prose states Kozlov 'was tasked with cleaning the ring of three bodies' in the window before Triple H's entrance; this script's own elim_ts derivation finds exactly 3 wrestlers (Khali, MVP, Carlito) eliminated inside that window, none with any other credited eliminator. See F231.", False, "kozlov_cleanup"),
    "MVP": (["Vladimir Kozlov"], "DERIVED", "DERIVED as one of Kozlov's 3-man 'cleaning the ring' stretch. See F231.", False, "kozlov_cleanup"),
    "Carlito": (["Vladimir Kozlov"], "DERIVED", "DERIVED as one of Kozlov's 3-man 'cleaning the ring' stretch. See F231.", False, "kozlov_cleanup"),
    "Triple H": (["Randy Orton"], "PROBABLE", "The winning elimination -- Orton outlasted the 3 members of Legacy (DiBiase, Cody Rhodes) and Triple H to win.", False, ""),
}

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Ted DiBiase Jr.", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #10. One of the 3 members of Legacy (with Randy Orton and Cody Rhodes) that this match's storyline centered on. No individually-named elimination credit this pass.", "S082"),
    ("Mike Knox", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #12 and survived 32:43 -- unusually long for a lower-card wrestler, per the Cageside commentary. No individually-named elimination credit this pass.", "S082"),
    ("JTG", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #9. Won a coin flip against his Cryme Tyme partner Shad Gaspard to enter the match -- using a double-sided coin to cheat, per S082. No individually-named elimination credit this pass.", "S082"),
    ("R-Truth", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #24. No individually-named elimination credit this pass.", "S082"),
    ("Vladimir Kozlov", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #6 and DERIVED as eliminating 3 wrestlers (Khali, MVP, Carlito) in a 'cleaning the ring' stretch before Triple H's entrance -- see F231.", "S082"),
    ("The Brian Kendrick", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #26. One of 5 wrestlers who didn't survive long enough to make it to the next buzzer this match. No individually-named elimination credit this pass.", "S082"),
    ("Dolph Ziggler", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #27. One of 5 wrestlers who didn't survive long enough to make it to the next buzzer this match. No individually-named elimination credit this pass.", "S082"),
    ("Kofi Kingston", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #22. No individually-named elimination credit this pass.", "S082"),
]

reused = {
    "Rey Mysterio": "rey-mysterio", "John Morrison": "johnny-nitro", "Carlito": "carlito", "MVP": "mvp",
    "The Great Khali": "the-great-khali", "Triple H": "hunter-hearst-helmsley", "Randy Orton": "randy-orton",
    "Chris Jericho": "chris-jericho", "The Miz": "the-miz", "Finlay": "finlay", "Cody Rhodes": "cody-rhodes",
    "The Undertaker": "the-undertaker", "Goldust": "goldust", "CM Punk": "cm-punk", "Mark Henry": "mark-henry",
    "Shelton Benjamin": "shelton-benjamin", "William Regal": "william-regal", "Kane": "kane",
    "Rob Van Dam": "rob-van-dam", "Santino Marella": "santino-marella", "Jim Duggan": "jim-duggan",
    "Big Show": "big-show",
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
    "Rey Mysterio", "John Morrison", "Carlito", "MVP", "The Great Khali", "Vladimir Kozlov", "Triple H",
    "Randy Orton", "JTG", "Ted DiBiase Jr.", "Chris Jericho", "Mike Knox", "The Miz", "Finlay", "Cody Rhodes",
    "The Undertaker", "Goldust", "CM Punk", "Mark Henry", "Shelton Benjamin", "William Regal", "Kofi Kingston",
    "Kane", "R-Truth", "Rob Van Dam", "The Brian Kendrick", "Dolph Ziggler", "Santino Marella", "Jim Duggan",
    "Big Show",
]
assert len(all_names) == 30

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Randy Orton")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, dq, method, is_shared, group_id = KNOWN_ELIMINATORS.get(name, ([], "", "", False, ""))

    notes_parts = []
    if name == "Randy Orton":
        notes_parts.append("Entered #8 and won his first career Royal Rumble, outlasting the other 2 members of Legacy (Ted DiBiase Jr. and Cody Rhodes) and Triple H, whom he eliminated for the win. No live source consulted this pass individually confirms the eliminator of Legacy's own members, DiBiase and Rhodes -- left UNKNOWN.")
    elif name == "Vladimir Kozlov":
        notes_parts.append("Entered #6. DERIVED as eliminating 3 wrestlers (The Great Khali, MVP, Carlito) in a 'cleaning the ring' stretch before Triple H's entrance. See F231.")
    elif name == "John Morrison":
        notes_parts.append("Reuses this database's existing 'johnny-nitro' wrestler_id -- same performer, renamed gimmick (not a new identity), consistent with the JBL/Bradshaw and King Booker/Booker T precedents.")
    note = " ".join(notes_parts)

    for eliminator in elim_by:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": elim_number[name],
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
            "assisting_wrestler_ids": "",
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
            "source_ids": "S082",
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
        "faction_stable": "Legacy" if name in ("Randy Orton", "Ted DiBiase Jr.", "Cody Rhodes") else "",
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
        "is_runner_up": "TRUE" if name == "Triple H" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "FALSE",
        "legend_returning": "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE",
        "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S082",
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
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F229", EVENT_ID, "events", EVENT_ID, "event_date;venue;attendance_reported;commentary_team;referees", "unverified",
     "Unlike every other year built so far, Shane's document has NO separate Dan Wahlers narrative history "
     "chapter for 2009 -- only the Cageside timing analysis. Event-level facts a Wahlers chapter normally "
     "supplies (exact date, venue, city, attendance, commentary team, referees, undercard results) are simply "
     "absent from the source and left entirely UNKNOWN this pass, rather than filled from outside knowledge. "
     "event_date is stored as '2009-XX-XX' rather than a bare 'UNKNOWN' -- the year itself is not actually in "
     "doubt (it's the document's own section heading and WWE's own official numbering for this event), only "
     "the exact month/day are unconfirmed pending a future external-research pass; this keeps the derived-table "
     "tooling (which buckets career stats by year) working without inventing a specific date.",
     "S082", "open", "2026-09-16"),
    ("F230", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "With no Wahlers narrative to mine, eliminator credit this year is almost entirely absent -- only Vladimir "
     "Kozlov's DERIVED 3-man 'cleaning the ring' stretch (see F231) and the winning elimination (Triple H by "
     "Randy Orton) are attributable. The other 25 elimination-eligible entrants, including Legacy's own Ted "
     "DiBiase Jr. and Cody Rhodes, have no individually-named eliminator this pass. Left UNKNOWN rather than "
     "guessed.",
     "S082", "open", "2026-09-16"),
    ("F231", EVENT_ID, "eliminations", "the-great-khali;mvp;carlito", "eliminator_wrestler_id", "unverified",
     "S082's own prose states Vladimir Kozlov 'was tasked with cleaning the ring of three bodies' during the "
     "window before Triple H's entrance, without individually naming them. Cross-referencing this script's own "
     "elim_ts derivation, exactly 3 wrestlers (The Great Khali, MVP, Carlito) have elimination timestamps "
     "falling inside that exact window, and none has any other credited eliminator this match. DERIVED (not "
     "directly named) but tightly corroborated -- the same derivation pattern used for 2005's Muhammad Hassan "
     "group elimination (F183) and 2007's Khali 7th-victim derivation (F196).",
     "S082", "open", "2026-09-16"),
    ("F232", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 8 previously-unseen wrestlers this pass (Ted DiBiase Jr., Mike Knox, JTG, R-Truth, "
     "Vladimir Kozlov, The Brian Kendrick, Dolph Ziggler, Kofi Kingston) with zero bio data in this pass's "
     "source -- names only. Left entirely UNKNOWN, same pattern as every prior year's equivalent flag.",
     "S082", "open", "2026-09-16"),
    ("F233", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-16"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2009", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2009-XX-XX", "venue": "UNKNOWN",
    "city_region": "UNKNOWN", "country": "UNKNOWN",
    "attendance_official": "", "attendance_reported": "",
    "entry_interval_seconds": 90, "entrant_count": 30, "duration_total": "58:37",
    "duration_status": "CONFIRMED",
    "winner_id": "randy-orton", "runner_up_id": "hunter-hearst-helmsley",
    "final_two_ids": "randy-orton;hunter-hearst-helmsley",
    "final_three_ids": "randy-orton;hunter-hearst-helmsley;cody-rhodes",
    "final_four_ids": "randy-orton;hunter-hearst-helmsley;cody-rhodes;ted-dibiase-jr",
    "first_entrant_id": "rey-mysterio", "second_entrant_id": "johnny-nitro", "final_entrant_id": "big-show",
    "first_elimination_id": "the-great-khali", "last_elimination_before_winner_id": "hunter-hearst-helmsley",
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
        "Randy Orton's first career Royal Rumble win, outlasting his own Legacy stablemates (Ted DiBiase Jr. "
        "and Cody Rhodes) and Triple H, the final elimination. Triple H had the longest survival time (49:56). "
        "Santino Marella's 0:02 survival time set a new shortest-survival record, breaking The Warlord's 1989 "
        "mark. The match's average survival time (16:59) and ring crowdedness (an average of 8.7 competitors "
        "in the ring at any given second, with 15 men in the ring at two points) were both unusually high for "
        "their time, per S082's own comparative analysis against other years it had studied."
    ),
    "notes": (
        "UNLIKE every other year built so far, this document has no Dan Wahlers narrative chapter for 2009 -- "
        "only the Cageside timing analysis. Entry order and survival times are CONFIRMED to the second for all "
        "30 entrants (a rich dataset), but event-level facts (date, venue, attendance, commentary, undercard) "
        "and almost all eliminator credit are UNKNOWN -- see F229/F230. Vladimir Kozlov's 3-man 'cleaning the "
        "ring' elimination stretch is DERIVED via timing cross-reference against the Cageside prose itself -- "
        "see F231."
    ),
    "data_quality_status": "PROBABLE", "source_ids": "S082",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2009 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
