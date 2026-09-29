# -*- coding: utf-8 -*-
"""
Builds all rows for the 2011 Royal Rumble -- schema v2.

Like 2009, Shane's doc has NO "Dan Wahlers History of the Royal Rumble"
chapter for 2011 -- only the "2011 Rumble Stats - Cageside" frame-by-frame
timing analysis. Event-level facts a Wahlers chapter normally supplies
(attendance, venue, exact date, commentary team, referees, undercard
results) are left UNKNOWN this pass, same treatment as 2009.

2011 was the FIRST 40-man Royal Rumble in history (every prior year was a
30-man field) -- the source doc itself calls it "the biggest Royal Rumble
match in history" going in. This is a genuinely new historical fact worth
surfacing.

SOURCES CONSULTED THIS PASS:
  S083 '2011 Rumble Stats - Cageside' section (Shane's doc)              tier 9

METHODOLOGY (mirrors 2009's DERIVED elimination-order pattern):
entry_actual[name] = cumulative buzzer-gap time + entrance_lag[name]. CM
Punk and Daniel Bryan (the first two entrants) both start at entry_actual=0
(pre-bell, no buzzer). elim_ts[name] = entry_actual[name] + survival_time[name].

Checksums (all verified before writing this script -- see asserts below):
  - The cumulative buzzer sum across all 38 buzzers lands exactly on the
    doc's own stated final-buzzer mark of 1:01:29 (Kane's entrance).
  - Alberto Del Rio's (the winner's) own survival-time entry of 9:33 is
    exactly (match total 1:09:52) minus his entry_actual -- confirming it's
    his winning span, not an elimination.
  - Santino Marella's survival-time entry of 12:56, added to his
    entry_actual, lands EXACTLY on the match total (1:09:52) -- meaning
    Santino, not Del Rio, was the literal final wrestler eliminated (his own
    elimination is Del Rio's winning elimination). This matches the doc's
    own aside elsewhere: "Santino is the final man eliminated in the match."
    So the final two are Del Rio (winner) and Santino Marella (runner-up),
    not the 8-man "final segment" group the doc frames loosely -- that
    group is simply everyone still active when Kane (the last entrant)
    came in, not literally the final 4.
  - A cross-check of average/median survival time computed from this
    script's own data (8:42 avg / 5:10 median) closely matches the doc's
    own stated 8:43 avg / 5:11 median (small gap consistent with the doc
    rounding its own average differently) -- an independent sanity check
    that no survival time was mistyped.

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order and survival ("ring") time are known to the second for ALL
    40 entrants -- ring_time_status is CONFIRMED throughout.
  - Eliminator credit is almost entirely absent, EVEN MORE than 2009. The
    doc's only elimination-attribution prose is a vague, non-individualized
    aside: "4 of these 8 guys were thrown out because CM Punk and his New
    Nexus henchmen were constantly engaging in 4 on 1 onslaughts every time
    a new participant entered the ring" -- referring to 4 (unnamed) of the
    8 fastest eliminations among the first 25 entrants. UNLIKE 2009's
    Kozlov derivation (where exactly 3 names fit a tight, unambiguous
    window with no other possible eliminator), this aside names neither
    the 8 nor the 4, and New Nexus itself had 5 members in this match
    (Punk, Husky Harris, Michael McGillicutty, David Otunga, Mason Ryan) --
    too many candidates and too little specificity to DERIVE any individual
    elimination without guessing. Left entirely UNKNOWN -- see F236.
  - The ONE individually attributable elimination is the winning one:
    Alberto Del Rio eliminating Santino Marella in the match's final
    second, per the checksum above.
  - Event-level facts (attendance, venue, date, commentary team, referees,
    undercard results) are entirely UNKNOWN -- no Wahlers chapter exists
    for this year in the source document. event_date is stored as
    '2011-XX-XX' (year is not actually in doubt -- it's the document's own
    section heading and WWE's own official numbering -- only the exact day
    is unconfirmed), same convention established for 2009 -- see F234.
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
EVENT_ID = "RR2011M"


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
    ("S083", "'2011 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers, ring "
     "crowdedness) filed under the '2011 Royal Rumble Stats' Heading-1. NO separate Dan Wahlers narrative "
     "history chapter exists for this year in Shane's document -- event-level facts (attendance, venue, exact "
     "date, commentary, undercard) are correspondingly UNKNOWN this pass. Notes this was the first-ever 40-man "
     "Royal Rumble (previously always 30 men). NOT live-fetched this pass."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# TIMING DERIVATION
# ---------------------------------------------------------------------------
buzzer_gaps = [
    ("Justin Gabriel", "1:31"), ("Zack Ryder", "1:30"), ("William Regal", "1:30"), ("Ted DiBiase", "1:45"),
    ("John Morrison", "1:31"), ("Yoshi Tatsu", "2:02"), ("Husky Harris", "1:37"), ("Chavo Guerrero", "1:22"),
    ("Mark Henry", "1:41"), ("JTG", "1:31"), ("Michael McGillicutty", "1:26"), ("Chris Masters", "1:32"),
    ("David Otunga", "1:30"), ("Tyler Reks", "1:31"), ("Vladimir Kozlov", "1:31"), ("R-Truth", "1:31"),
    ("The Great Khali", "1:30"), ("Mason Ryan", "1:24"), ("Booker T", "1:31"), ("John Cena", "2:09"),
    ("Hornswoggle", "2:23"), ("Tyson Kidd", "2:07"), ("Heath Slater", "1:30"), ("Kofi Kingston", "1:36"),
    ("Jack Swagger", "1:31"), ("Sheamus", "1:40"), ("Rey Mysterio", "1:50"), ("Wade Barrett", "1:40"),
    ("Dolph Ziggler", "1:30"), ("Diesel", "1:31"), ("Drew McIntyre", "1:31"), ("Alex Riley", "1:31"),
    ("Big Show", "1:30"), ("Ezekiel Jackson", "1:44"), ("Santino Marella", "1:36"), ("Alberto Del Rio", "1:39"),
    ("Randy Orton", "1:31"), ("Kane", "1:34"),
]
buzzer_time = {}
cum = 0
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("1:01:29"), f"buzzer checksum failed: {cum}"

# Entrance times. CM Punk and Daniel Bryan (pre-bell, the first two
# entrants) are excluded, same treatment as Rey Mysterio/John Morrison in
# 2009.
entrance_lag = {
    "Alberto Del Rio": "1:55", "Diesel": "0:43", "Big Show": "0:39", "John Cena": "0:37", "The Great Khali": "0:34",
    "Kofi Kingston": "0:26", "Randy Orton": "0:25", "Booker T": "0:24", "Kane": "0:23", "Wade Barrett": "0:20",
    "Ted DiBiase": "0:17", "Dolph Ziggler": "0:17", "Alex Riley": "0:16",
    "Mark Henry": "0:15", "David Otunga": "0:15", "Tyler Reks": "0:15",
    "Hornswoggle": "0:14", "Chavo Guerrero": "0:14",
    "Rey Mysterio": "0:13", "John Morrison": "0:12",
    "Santino Marella": "0:11", "William Regal": "0:11",
    "Zack Ryder": "0:10", "JTG": "0:10", "Jack Swagger": "0:10", "Ezekiel Jackson": "0:10",
    "Yoshi Tatsu": "0:09", "Husky Harris": "0:09", "Chris Masters": "0:09",
    "Vladimir Kozlov": "0:08", "Heath Slater": "0:08", "Sheamus": "0:08",
    "Michael McGillicutty": "0:07", "R-Truth": "0:07", "Mason Ryan": "0:07", "Drew McIntyre": "0:07",
    "Tyson Kidd": "0:06", "Justin Gabriel": "0:05",
}
entry_actual = {"CM Punk": 0, "Daniel Bryan": 0}
for name in buzzer_time:
    entry_actual[name] = buzzer_time[name] + mmss(entrance_lag[name])

# Survival ("ring") times, as stated directly by S083. Alberto Del Rio (the
# winner) is included with a survival time that is his entry-to-match-end
# span, not an elimination -- excluded from elim_ts below.
survival = {
    "CM Punk": "35:21", "John Cena": "34:18", "Wade Barrett": "22:24", "Kofi Kingston": "21:05", "Daniel Bryan": "20:54",
    "Rey Mysterio": "19:08", "Sheamus": "18:17", "Husky Harris": "15:48", "Michael McGillicutty": "15:08",
    "John Morrison": "13:23", "Santino Marella": "12:56", "Ted DiBiase": "12:16", "David Otunga": "11:57",
    "Hornswoggle": "9:40", "Alberto Del Rio": "9:33", "Randy Orton": "8:19", "Ezekiel Jackson": "7:15",
    "Dolph Ziggler": "7:12", "Mark Henry": "7:04", "Yoshi Tatsu": "5:34", "Drew McIntyre": "4:47", "Jack Swagger": "4:41",
    "Mason Ryan": "4:32", "William Regal": "4:08", "Alex Riley": "2:50", "Diesel": "2:46", "Chavo Guerrero": "2:01",
    "Chris Masters": "1:58", "JTG": "1:48", "Kane": "1:36", "Big Show": "1:30", "The Great Khali": "1:16",
    "Booker T": "1:08", "R-Truth": "1:02", "Justin Gabriel": "0:58", "Heath Slater": "0:58", "Tyson Kidd": "0:53",
    "Zack Ryder": "0:43", "Vladimir Kozlov": "0:40", "Tyler Reks": "0:34",
}
assert set(survival) == set(entry_actual), set(survival) ^ set(entry_actual)
assert len(survival) == 40

MATCH_TOTAL = mmss("1:09:52")
assert mmss(survival["Alberto Del Rio"]) == MATCH_TOTAL - entry_actual["Alberto Del Rio"]

elim_ts = {}
for name, t in survival.items():
    if name == "Alberto Del Rio":
        continue  # winner, never eliminated
    elim_ts[name] = entry_actual[name] + mmss(t)
# Santino's own survival time, added to his entry_actual, lands exactly on
# match end -- confirming he (not Del Rio) is the final elimination, i.e.
# the WINNING elimination (Del Rio over Santino).
assert elim_ts["Santino Marella"] == MATCH_TOTAL, elim_ts["Santino Marella"]

elim_order_list = sorted(elim_ts, key=lambda n: elim_ts[n])
elim_number = {name: i + 1 for i, name in enumerate(elim_order_list)}
assert elim_number["Justin Gabriel"] == 1
assert elim_number["Santino Marella"] == 39  # the winning elimination, last of 39

ENTRY_NUMBERS = {"CM Punk": 1, "Daniel Bryan": 2}
for i, (name, _) in enumerate(buzzer_gaps):
    ENTRY_NUMBERS[name] = i + 3
assert ENTRY_NUMBERS["Justin Gabriel"] == 3 and ENTRY_NUMBERS["Kane"] == 40

# Final four determined purely from elim_ts order (the doc's own "8-man
# final segment" framing is looser than this -- it names everyone still
# active once the 40th and final entrant, Kane, came in, not literally the
# last 4 standing).
FINAL_TWO = {"Alberto Del Rio", "Santino Marella"}
FINAL_THREE = {"Alberto Del Rio", "Santino Marella", "Randy Orton"}
FINAL_FOUR = {"Alberto Del Rio", "Santino Marella", "Randy Orton", "Wade Barrett"}

# name -> (eliminator names, data_quality_status, notes, is_shared, group_id)
KNOWN_ELIMINATORS = {
    "Santino Marella": (["Alberto Del Rio"], "PROBABLE",
                         "The winning elimination -- Del Rio eliminated Santino in the match's final second "
                         "to win. The ONLY individually attributable elimination this pass; see script "
                         "docstring and F235/F236 for why the rest of the field has no named eliminator.",
                         False, ""),
}

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Daniel Bryan", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #2 (pre-bell, alongside CM Punk) and survived 20:54. No individually-named elimination credit this pass.", "S083"),
    ("Justin Gabriel", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #3, survived just 0:58 -- among the fastest eliminations of the match, possibly (but not confirmably) one of CM Punk's New Nexus stable's unnamed victims. See F236.", "S083"),
    ("Zack Ryder", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #4, survived 0:43. No individually-named elimination credit this pass.", "S083"),
    ("Yoshi Tatsu", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #8, survived 5:34. No individually-named elimination credit this pass.", "S083"),
    ("Husky Harris", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #9 as a member of CM Punk's New Nexus stable, survived 15:48. Later became Bray Wyatt. No individually-named elimination credit this pass.", "S083"),
    ("Michael McGillicutty", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #13 as a member of CM Punk's New Nexus stable, survived 15:08. Later became Curtis Axel. No individually-named elimination credit this pass.", "S083"),
    ("David Otunga", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #15 as a member of CM Punk's New Nexus stable, survived 11:57. No individually-named elimination credit this pass.", "S083"),
    ("Tyler Reks", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #16, survived just 0:34 -- the shortest survival time of the match. No individually-named elimination credit this pass.", "S083"),
    ("Mason Ryan", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #20 as a member of CM Punk's New Nexus stable, survived 4:32. No individually-named elimination credit this pass.", "S083"),
    ("Tyson Kidd", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #24, survived 0:53. No individually-named elimination credit this pass.", "S083"),
    ("Heath Slater", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #25, survived 0:58. No individually-named elimination credit this pass.", "S083"),
    ("Jack Swagger", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #27, survived 4:41. No individually-named elimination credit this pass.", "S083"),
    ("Sheamus", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #28, billed as 'King Sheamus' at the time following his 2010 King of the Ring win. Survived 18:17. No individually-named elimination credit this pass.", "S083"),
    ("Wade Barrett", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #30, survived 22:24 and was part of the match's final four by elim_ts order. No individually-named elimination credit this pass.", "S083"),
    ("Drew McIntyre", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #33, survived 4:47. No individually-named elimination credit this pass.", "S083"),
    ("Alex Riley", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #34, survived 2:50. No individually-named elimination credit this pass.", "S083"),
    ("Ezekiel Jackson", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #36, survived 7:15. No individually-named elimination credit this pass.", "S083"),
    ("Alberto Del Rio", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #38 and won his first career Royal Rumble, eliminating Santino Marella (the match's final elimination) in the match's very last second -- see checksum in script docstring.", "S083"),
]

reused = {
    "CM Punk": "cm-punk", "William Regal": "william-regal", "Ted DiBiase": "ted-dibiase-jr",
    "John Morrison": "johnny-nitro", "Chavo Guerrero": "chavo-guerrero", "Mark Henry": "mark-henry",
    "JTG": "jtg", "Chris Masters": "chris-masters", "Vladimir Kozlov": "vladimir-kozlov",
    "R-Truth": "r-truth", "The Great Khali": "the-great-khali", "Booker T": "booker-t",
    "John Cena": "john-cena", "Hornswoggle": "hornswoggle", "Kofi Kingston": "kofi-kingston",
    "Rey Mysterio": "rey-mysterio", "Dolph Ziggler": "dolph-ziggler", "Diesel": "diesel",
    "Big Show": "big-show", "Santino Marella": "santino-marella", "Randy Orton": "randy-orton",
    "Kane": "kane",
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
# ENTRANTS -- all 40, full entry order and survival time known.
# ---------------------------------------------------------------------------
all_names = [
    "CM Punk", "Daniel Bryan", "Justin Gabriel", "Zack Ryder", "William Regal", "Ted DiBiase", "John Morrison",
    "Yoshi Tatsu", "Husky Harris", "Chavo Guerrero", "Mark Henry", "JTG", "Michael McGillicutty", "Chris Masters",
    "David Otunga", "Tyler Reks", "Vladimir Kozlov", "R-Truth", "The Great Khali", "Mason Ryan", "Booker T",
    "John Cena", "Hornswoggle", "Tyson Kidd", "Heath Slater", "Kofi Kingston", "Jack Swagger", "Sheamus",
    "Rey Mysterio", "Wade Barrett", "Dolph Ziggler", "Diesel", "Drew McIntyre", "Alex Riley", "Big Show",
    "Ezekiel Jackson", "Santino Marella", "Alberto Del Rio", "Randy Orton", "Kane",
]
assert len(all_names) == 40

DISPLAY_NAME = {"Sheamus": "King Sheamus", "Ted DiBiase": "Ted DiBiase"}

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Alberto Del Rio")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, dq, method, is_shared, group_id = KNOWN_ELIMINATORS.get(name, ([], "", "", False, ""))

    notes_parts = []
    if name == "Alberto Del Rio":
        notes_parts.append("Entered #38 and won his first career Royal Rumble, eliminating Santino Marella in the match's final second -- see checksum in script docstring (Santino's own survival time lands his elim_ts exactly on match end).")
    elif name == "Santino Marella":
        notes_parts.append("Eliminated by Alberto Del Rio in the match's final second -- the winning elimination, and the runner-up spot. S083 separately notes Santino spent 11:47 of his 12:56 total survival time (91.1%) outside the ring after being knocked under the bottom rope without being officially eliminated (his feet never went over the top rope to the floor), per the Rumble's standard elimination rule -- his full ring_time legitimately includes that stretch.")
    elif name == "John Morrison":
        notes_parts.append("Reuses this database's existing 'johnny-nitro' wrestler_id -- same performer, renamed gimmick (not a new identity), consistent with the JBL/Bradshaw, King Booker/Booker T, and 2008/2009 John Morrison precedents.")
    elif name == "Ted DiBiase":
        notes_parts.append("Reuses this database's existing 'ted-dibiase-jr' wrestler_id from the 2009 build (same Legacy-stable performer, billed without the 'Jr.' suffix by this point) -- NOT the same person as 'ted-dibiase' (Ted DiBiase Sr., the Million Dollar Man), a separate existing wrestler_id in this database. Careful disambiguation performed this pass to avoid an incorrect identity merge.")
    elif name == "Sheamus":
        notes_parts.append("Billed as 'King Sheamus' at this event, following his November 2010 King of the Ring win.")
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
            "source_ids": "S083",
            "notes": "",
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
        "faction_stable": "New Nexus" if name in ("CM Punk", "Husky Harris", "Michael McGillicutty", "David Otunga", "Mason Ryan") else "",
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
        "is_runner_up": "TRUE" if name == "Santino Marella" else "FALSE",
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
        "source_ids": "S083",
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
    ("F234", EVENT_ID, "events", EVENT_ID, "event_date;venue;attendance_reported;commentary_team;referees", "unverified",
     "Like 2009, Shane's document has NO separate Dan Wahlers narrative history chapter for 2011 -- only the "
     "Cageside timing analysis. Event-level facts a Wahlers chapter normally supplies (exact date, venue, city, "
     "attendance, commentary team, referees, undercard results) are simply absent from the source and left "
     "entirely UNKNOWN this pass. event_date is stored as '2011-XX-XX' rather than a bare 'UNKNOWN' -- the year "
     "itself is not in doubt (the document's own section heading and WWE's own official numbering), only the "
     "exact month/day are unconfirmed. Pending a future external-research pass.",
     "S083", "open", "2026-09-16"),
    ("F235", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "With no Wahlers narrative to mine, eliminator credit this year is almost entirely absent -- only the "
     "winning elimination (Santino Marella by Alberto Del Rio, see checksum in build_2011.py's docstring) is "
     "individually attributable. The other 38 elimination-eligible entrants have no named eliminator this pass. "
     "Left UNKNOWN rather than guessed.",
     "S083", "open", "2026-09-16"),
    ("F236", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "S083's own prose states '4 of these 8 guys were thrown out because CM Punk and his New Nexus henchmen "
     "were constantly engaging in 4 on 1 onslaughts every time a new participant entered the ring' (referring "
     "to 4 unnamed wrestlers among 8 unnamed fast eliminations within the first 25 entrants). UNLIKE 2009's "
     "Kozlov derivation (F231, where exactly 3 named-by-elimination-count candidates fit an unambiguous window "
     "with no other possible eliminator), this aside names neither the 8 nor the 4, and New Nexus itself had 5 "
     "members in this match (CM Punk, Husky Harris, Michael McGillicutty, David Otunga, Mason Ryan) -- too many "
     "candidates and too little specificity to DERIVE any individual elimination without guessing. "
     "Deliberately NOT converted into elimination rows -- left UNKNOWN per the project's never-invent-data rule.",
     "S083", "open", "2026-09-16"),
    ("F237", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 18 previously-unseen wrestlers this pass (Daniel Bryan, Justin Gabriel, Zack Ryder, "
     "Yoshi Tatsu, Husky Harris, Michael McGillicutty, David Otunga, Tyler Reks, Mason Ryan, Tyson Kidd, Heath "
     "Slater, Jack Swagger, Sheamus, Wade Barrett, Drew McIntyre, Alex Riley, Ezekiel Jackson, Alberto Del Rio) "
     "with zero bio data in this pass's source -- names only. Left entirely UNKNOWN, same pattern as every "
     "prior year's equivalent flag.",
     "S083", "open", "2026-09-16"),
    ("F238", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-16"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2011", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2011-XX-XX", "venue": "UNKNOWN",
    "city_region": "UNKNOWN", "country": "UNKNOWN",
    "attendance_official": "", "attendance_reported": "",
    "entry_interval_seconds": 90, "entrant_count": 40, "duration_total": "1:09:52",
    "duration_status": "CONFIRMED",
    "winner_id": "alberto-del-rio", "runner_up_id": "santino-marella",
    "final_two_ids": "alberto-del-rio;santino-marella",
    "final_three_ids": "alberto-del-rio;santino-marella;randy-orton",
    "final_four_ids": "alberto-del-rio;santino-marella;randy-orton;wade-barrett",
    "first_entrant_id": "cm-punk", "second_entrant_id": "daniel-bryan", "final_entrant_id": "kane",
    "first_elimination_id": "justin-gabriel", "last_elimination_before_winner_id": "santino-marella",
    "eliminations_count": 39, "eliminators_count": "UNKNOWN",
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
        "The FIRST-EVER 40-man Royal Rumble match (every prior year, 1988-2010, was a 30-man field) -- S083 "
        "itself hypes this going in as 'the biggest Royal Rumble match in history.' Alberto Del Rio's first "
        "career Royal Rumble win, eliminating Santino Marella in the match's final second. CM Punk had the "
        "longest survival time (35:21) despite not winning. Tyler Reks set the shortest survival time of the "
        "match at just 0:34. Santino Marella's own breakdown shows he spent 11:47 of his 12:56 total survival "
        "time (91.1%) outside the ring after being knocked under the bottom rope without being officially "
        "eliminated -- his feet never crossed the top rope to the floor, so his ring_time legitimately includes "
        "that entire stretch per the Rumble's standard elimination rule. CM Punk's New Nexus stable (5 members "
        "this match: Punk, Husky Harris, Michael McGillicutty, David Otunga, Mason Ryan) reportedly ganged up "
        "on new entrants throughout, though S083 does not name individual victims -- see F236."
    ),
    "notes": (
        "Like 2009, this document has no Dan Wahlers narrative chapter for 2011 -- only the Cageside timing "
        "analysis. Entry order and survival times are CONFIRMED to the second for all 40 entrants (a rich "
        "dataset), but event-level facts (date, venue, attendance, commentary, undercard) and almost all "
        "eliminator credit are UNKNOWN -- see F234/F235/F236. The only individually attributable elimination "
        "is the winning one (Del Rio over Santino Marella), confirmed via an internal timing checksum: "
        "Santino's own stated survival time, added to his entry_actual, lands exactly on the match's total "
        "duration."
    ),
    "data_quality_status": "PROBABLE", "source_ids": "S083",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2011 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
