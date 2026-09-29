# -*- coding: utf-8 -*-
"""
Builds all rows for the 2015 Royal Rumble -- schema v2.

Like 2009/2011/2012/2013/2014, Shane's doc has NO "Dan Wahlers History of
the Royal Rumble" chapter for 2015 -- only the "2015 Rumble Stats -
Cageside" frame-by-frame timing analysis. Like 2014, this year's buzzer
list is FULLY NAMED (28 named buzzers, matching entrants #3-30 directly)
-- full entry order is known with confidence.

SOURCES CONSULTED THIS PASS:
  S106 '2015 Rumble Stats - Cageside' section (Shane's doc)             tier 9

METHODOLOGY: entry_actual[name] = cumulative buzzer-gap time + entrance_
lag[name]. The Miz and R-Truth (the first two entrants) both start at
entry_actual=0 (pre-bell, per S106's own explicit statement). elim_ts
[name] = entry_actual[name] + survival_time[name].

Checksums (all verified before writing this script):
  - The cumulative buzzer sum across all 28 buzzers lands exactly on the
    doc's own stated actual final-buzzer mark of 50:21.
  - Roman Reigns's (the winner's) own entry_actual + his own stated 27:30
    survival time lands EXACTLY on the match total (59:35) -- the
    signature of the winning, never-eliminated wrestler, and confirms he
    is entrant #19.
  - Rusev's own elim_ts computes to 59:34 -- ONE SECOND short of the
    match total (59:35), not an error: S106 explicitly notes "There was a
    one or two second delay between the time that Rusev's feet hit the
    floor and the bell ringing to signify the end of the match. I counted
    this extra second as part of the match time" -- i.e. the match's own
    documented 59:35 total includes ~1 extra second beyond Rusev's actual
    elimination instant. Rusev is still unambiguously the final
    elimination (the runner-up).
  - Kane's and Big Show's elim_ts both compute to an IDENTICAL 57:13 --
    matching S106's own direct statement that Reigns "eliminated Big Show
    and Kane" together, and explaining the match's false-ending-bell
    moment (S106: "A false match-ending bell rang at 6m 55s into this
    final stretch, right when Reigns appeared to be the winner when he
    eliminated Big Show and Kane... I ignored this bell, because Rusev
    was still a survivor" -- confirming that immediately after this
    double elimination, exactly 2 men (Reigns, Rusev) remained, not 3).

STRUCTURAL NOTE -- no true "final three" moment: because Kane and Big
Show were eliminated SIMULTANEOUSLY (the same double-elimination spot),
the match went directly from 4 competitors (Reigns, Rusev, Kane, Big
Show) to 2 (Reigns, Rusev) -- there was never a point where exactly 3
remained. is_final_three is left FALSE for all entrants this year rather
than arbitrarily picking one of Kane/Big Show to omit -- see F286.

NAMED ELIMINATIONS THIS YEAR: all 3 individually narrated by S106, all
credited to the winner during the match's final stretch:
  - Big Show <- Roman Reigns (shared/simultaneous with Kane)
  - Kane <- Roman Reigns (shared/simultaneous with Big Show)
  - Rusev <- Roman Reigns (the winning elimination)
All other elimination-eligible entrants have no individually named
eliminator this pass -- left UNKNOWN rather than guessed.

TWO UNUSUAL PARTICIPATION CASES THIS YEAR (both directly addressed by
S106's own methodology notes):
  - Curtis Axel: counted as one of the 30 OFFICIAL entrants (his buzzer
    sounds, entrant #6) despite never actually making it into the ring --
    he was attacked by Erick Rowan (substituting for him) before he could
    enter, so his survival/ring_time is a defined 0:00. His elim_ts is
    still computed via the normal formula (entry_actual + 0), representing
    the moment his non-entry was effectively decided, not a standard
    over-the-rope elimination -- see F284.
  - Erick Rowan: explicitly NOT counted as an official competitor --
    S106: "I did not count Erick Rowan as an official competitor in the
    match even though he entered the ring in place of Curtis Axel. The
    commentators emphasized the point that Rowan was not a legal
    participant, and so I treated his appearance...like any other run-in
    or interference." NO entrant row created for him this pass (he
    already exists in this database as a wrestler from RR2014M, but this
    match's entrants.csv intentionally excludes him) -- see F284. He is
    credited by S106 with being the one who eventually tossed out Erick
    Rowan the interloper himself... no wait, Bray Wyatt tossed Rowan back
    out of the ring after ~0:51 (S106) -- not modeled as an
    eliminations.csv row either, since Rowan was never an official
    participant to begin with.
The Rock also made a well-documented, non-competing interference
appearance late in the match (endorsing Reigns, then physically attacking
the already-eliminated Big Show and Kane at ringside) -- mentioned in
events.csv notes only, not modeled as an entrant or elimination row.

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order and survival time are known to the second for ALL 30
    official entrants.
  - 3 of 29 eliminations have an individually named eliminator, all
    credited to the winner (Roman Reigns) -- less individually-rich than
    2012/2014's more spread-out credit, but all 3 are high-confidence,
    directly narrated, and internally cross-validated via the identical
    Kane/Big Show elim_ts checksum above.
  - Event-level facts (attendance, venue, exact date, commentary,
    referees, undercard) are UNKNOWN -- no Wahlers chapter exists for
    this year. event_date stored as '2015-XX-XX', same convention as
    prior no-Wahlers-chapter years. (The show's own Philadelphia setting
    IS mentioned in passing -- "Cole talks about Philadelphia" -- treated
    as PROBABLE city info, not a full venue/attendance confirmation.)
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
EVENT_ID = "RR2015M"


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
    ("S106", "'2015 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-17",
     "Frame-by-frame-style timing analysis (survival times, entrance times, fully named time-between-buzzers, "
     "ring crowdedness) filed under the '2015 Royal Rumble Stats' Heading-1. NO separate Dan Wahlers narrative "
     "history chapter exists for this year. Directly narrates 3 individual eliminations (all credited to the "
     "winner) and extensively documents 2 unusual participation cases (Curtis Axel, Erick Rowan) plus a "
     "detailed methodology comparison against WWE's own published survival times (several named discrepancies "
     "attributed to WWE's inconsistent inclusion of entrance time). NOT live-fetched this pass."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# TIMING DERIVATION
# ---------------------------------------------------------------------------
buzzer_gaps = [
    ("Bubba Ray Dudley", "1:30"), ("Luke Harper", "2:35"), ("Bray Wyatt", "1:39"), ("Curtis Axel", "1:39"),
    ("The Boogeyman", "1:56"), ("Sin Cara", "2:08"), ("Zack Ryder", "1:48"), ("Daniel Bryan", "1:48"),
    ("Fandango", "1:42"), ("Tyson Kidd", "1:38"), ("Stardust", "1:27"), ("Diamond Dallas Page", "1:53"),
    ("Rusev", "2:09"), ("Goldust", "2:08"), ("Kofi Kingston", "1:45"), ("Adam Rose", "1:43"),
    ("Roman Reigns", "2:07"), ("Big E", "1:36"), ("Damien Mizdow", "1:41"), ("Jack Swagger", "1:40"),
    ("Ryback", "1:43"), ("Kane", "1:43"), ("Dean Ambrose", "1:31"), ("Titus O'Neil", "1:34"),
    ("Bad News Barrett", "1:47"), ("Cesaro", "1:53"), ("Big Show", "1:49"), ("Dolph Ziggler", "1:49"),
]
buzzer_time = {}
cum = 0
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("50:21"), f"buzzer checksum failed: {cum}"

# Entrance times. The Miz and R-Truth (pre-bell, the first two entrants)
# are excluded, same treatment as prior years' opening pair.
entrance_lag = {
    "The Boogeyman": "0:57", "Adam Rose": "0:53", "Damien Mizdow": "0:51", "Bubba Ray Dudley": "0:40",
    "Bray Wyatt": "0:33", "Roman Reigns": "0:30", "Luke Harper": "0:27", "Titus O'Neil": "0:27",
    "Stardust": "0:26", "Curtis Axel": "0:25", "Rusev": "0:24", "Bad News Barrett": "0:24",
    "Cesaro": "0:22", "Diamond Dallas Page": "0:21", "Kane": "0:20", "Big Show": "0:20",
    "Daniel Bryan": "0:18", "Jack Swagger": "0:18", "Ryback": "0:17", "Fandango": "0:16",
    "Tyson Kidd": "0:16", "Goldust": "0:16", "Big E": "0:16", "Kofi Kingston": "0:15",
    "Sin Cara": "0:15", "Zack Ryder": "0:14", "Dean Ambrose": "0:12", "Dolph Ziggler": "0:11",
}
entry_actual = {"The Miz": 0, "R-Truth": 0}
for name in buzzer_time:
    entry_actual[name] = buzzer_time[name] + mmss(entrance_lag[name])

# Survival ("ring") times, as stated directly by S106. Roman Reigns (the
# winner) is included with a survival time that is his entry-to-match-end
# span, not an elimination -- excluded from elim_ts below.
survival = {
    "Bray Wyatt": "46:58", "Rusev": "35:18", "Roman Reigns": "27:30", "Kane": "16:55", "Big E": "14:49",
    "Dean Ambrose": "13:30", "Jack Swagger": "12:50", "Stardust": "12:25", "Ryback": "11:00",
    "Daniel Bryan": "10:11", "Big Show": "8:21", "Fandango": "7:36", "Goldust": "6:21",
    "Bad News Barrett": "5:47", "Cesaro": "4:56", "Bubba Ray Dudley": "4:44", "Luke Harper": "4:17",
    "R-Truth": "4:13", "The Miz": "4:01", "Kofi Kingston": "2:51", "Diamond Dallas Page": "2:28",
    "Tyson Kidd": "2:26", "Dolph Ziggler": "2:20", "The Boogeyman": "0:48", "Sin Cara": "0:37",
    "Zack Ryder": "0:34", "Damien Mizdow": "0:18", "Adam Rose": "0:10", "Titus O'Neil": "0:05",
    "Curtis Axel": "0:00",
}
assert set(survival) == set(entry_actual), set(survival) ^ set(entry_actual)
assert len(survival) == 30

MATCH_TOTAL = mmss("59:35")
assert entry_actual["Roman Reigns"] + mmss(survival["Roman Reigns"]) == MATCH_TOTAL

elim_ts = {}
for name, t in survival.items():
    if name == "Roman Reigns":
        continue  # winner, never eliminated
    elim_ts[name] = entry_actual[name] + mmss(t)
assert secs_to_mmss(elim_ts["Rusev"]) == "59:34"  # 1s short of MATCH_TOTAL -- see docstring, S106's own note
assert elim_ts["Kane"] == elim_ts["Big Show"] == mmss("57:13")  # simultaneous double elimination by Reigns

elim_order_list = sorted(elim_ts, key=lambda n: elim_ts[n])
elim_number = {name: i + 1 for i, name in enumerate(elim_order_list)}
assert elim_number["The Miz"] == 1
assert elim_number["Rusev"] == 29  # the winning elimination, last of 29

ENTRY_NUMBERS = {"The Miz": 1, "R-Truth": 2}
for i, (name, _) in enumerate(buzzer_gaps):
    ENTRY_NUMBERS[name] = i + 3
assert ENTRY_NUMBERS["Bubba Ray Dudley"] == 3 and ENTRY_NUMBERS["Dolph Ziggler"] == 30
assert ENTRY_NUMBERS["Roman Reigns"] == 19

FINAL_TWO = {"Roman Reigns", "Rusev"}
FINAL_THREE = set()  # no true "final three" moment this year -- see docstring / F286
FINAL_FOUR = {"Roman Reigns", "Rusev", "Kane", "Big Show"}

# name -> (eliminator names, data_quality_status, notes, is_shared, group_id)
KNOWN_ELIMINATORS = {
    "Big Show": (["Roman Reigns"], "CONFIRMED",
                  "S106 directly states Reigns 'eliminated Big Show and Kane' together, in the same spot that "
                  "caused a false match-ending bell.", True, "reigns_double"),
    "Kane": (["Roman Reigns"], "CONFIRMED",
              "S106 directly states Reigns 'eliminated Big Show and Kane' together -- both compute to an "
              "identical elim_ts of 57:13 at this data's 1-second resolution, confirming the simultaneous "
              "nature of the spot.", True, "reigns_double"),
    "Rusev": (["Roman Reigns"], "CONFIRMED",
               "The winning elimination. S106 directly states 'Rusev only survived for 20 more seconds before "
               "Reigns easily tossed him out.'", False, ""),
}

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Bubba Ray Dudley", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #3. Survived 4:44. Per S106, WWE's own published survival time for him (5:22) differs from this document's calculation (4:44) because WWE counted his ~0:40 entrance as part of his survival time -- adding the two together (5:24) lands within 2 seconds of WWE's figure. Not treated as a genuine data CONFLICT for this database's own ring_time field, which follows this project's own entrance-vs-ring-time definitions (see DEFINITIONS.md) rather than WWE's inconsistent methodology -- see F285.", "S106"),
    ("Bray Wyatt", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #5. Survived 46:58, the longest of the match. Per S106, dominated the match's opening ~15 minutes in a series of one-on-one eliminations before the ring began filling up. Also tossed the interloper Erick Rowan (substituting for Curtis Axel) back out of the ring after about 0:51 -- not modeled as a credited elimination since Rowan was never an official competitor.", "S106"),
    ("Curtis Axel", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #6 (his buzzer sounded) but was attacked and substituted for by Erick Rowan before he could actually enter the ring -- counted by S106 as one of the 30 official entrants regardless, with a defined ring_time/survival of 0:00. See F284.", "S106"),
    ("The Boogeyman", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #8. Survived just 0:48, though his entrance (0:57) and a 'spook-off' spot with Bray Wyatt extended that waiting period to over 2 minutes.", "S106"),
    ("Adam Rose", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #16. Survived just 0:10. Per S106, stood on the apron in disbelief before entering as the rosebuds (his entourage) carried Kofi Kingston around ringside.", "S106"),
]

reused = {
    "The Miz": "the-miz", "R-Truth": "r-truth", "Luke Harper": "luke-harper", "Sin Cara": "sin-cara",
    "Zack Ryder": "zack-ryder", "Daniel Bryan": "daniel-bryan", "Fandango": "fandango",
    "Tyson Kidd": "tyson-kidd", "Diamond Dallas Page": "diamond-dallas-page", "Rusev": "rusev",
    "Goldust": "goldust", "Kofi Kingston": "kofi-kingston", "Roman Reigns": "roman-reigns",
    "Big E": "big-e", "Jack Swagger": "jack-swagger", "Ryback": "ryback", "Kane": "kane",
    "Dean Ambrose": "dean-ambrose", "Titus O'Neil": "titus-oneil", "Cesaro": "cesaro",
    "Big Show": "big-show", "Dolph Ziggler": "dolph-ziggler",
    "Stardust": "cody-rhodes", "Damien Mizdow": "damien-sandow", "Bad News Barrett": "wade-barrett",
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
# ENTRANTS -- all 30 official entrants (Erick Rowan excluded, see docstring).
# ---------------------------------------------------------------------------
all_names = [
    "The Miz", "R-Truth", "Bubba Ray Dudley", "Luke Harper", "Bray Wyatt", "Curtis Axel", "The Boogeyman",
    "Sin Cara", "Zack Ryder", "Daniel Bryan", "Fandango", "Tyson Kidd", "Stardust", "Diamond Dallas Page",
    "Rusev", "Goldust", "Kofi Kingston", "Adam Rose", "Roman Reigns", "Big E", "Damien Mizdow", "Jack Swagger",
    "Ryback", "Kane", "Dean Ambrose", "Titus O'Neil", "Bad News Barrett", "Cesaro", "Big Show", "Dolph Ziggler",
]
assert len(all_names) == 30

DISPLAY_NAME = {"Stardust": "Stardust", "Damien Mizdow": "Damien Mizdow", "Bad News Barrett": "Bad News Barrett"}
# Note: "Adam Rose" is new too -- added to new_wrestlers below (see fix).

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Roman Reigns")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, dq, method, is_shared, group_id = KNOWN_ELIMINATORS.get(name, ([], "", "", False, ""))

    notes_parts = []
    if name == "Roman Reigns":
        notes_parts.append("Entered #19 and won his 1st career Royal Rumble, eliminating Rusev roughly 20 seconds after Rusev re-entered the ring following an interference sequence. Per S106, Reigns was 'booed out of the building' by the live Philadelphia crowd, still smarting over Daniel Bryan's early elimination -- even a surprise late appearance and endorsement from The Rock (who also physically confronted the already-eliminated Big Show and Kane at ringside) could not turn the crowd. Not modeled as entrant/elimination rows since Rock never officially competed.")
    elif name == "Rusev":
        notes_parts.append("Eliminated by Roman Reigns in the match's final moments -- the winning elimination, and the runner-up spot. Per S106, Rusev rolled to the floor after a Kane chokeslam and hid outside the ring for 9:19 (about 26.4% of his total survival time) before re-entering just before his actual elimination. His elim_ts computes to 59:34, one second short of the match's own stated 59:35 total -- S106 explicitly attributes this to a 1-2 second delay between Rusev's feet hitting the floor and the bell ringing, which it counted as part of the official match time.")
    elif name in ("Kane", "Big Show"):
        notes_parts.append("Eliminated together by Roman Reigns in a simultaneous double-elimination (both entrants' elim_ts compute to an identical 57:13) that triggered a false match-ending bell, since Rusev was still an active competitor. The Rock physically confronted both wrestlers at ringside afterward, per S106.")
    elif name == "Curtis Axel":
        notes_parts.append("Counted as an official entrant (buzzer sounded, entry #6) but never actually entered the ring -- attacked by Erick Rowan, who substituted for him. Survival/ring_time is a defined 0:00 per S106's own explicit methodology choice; no eliminator credited (not a standard over-the-rope elimination). See F284.")
    elif name == "Daniel Bryan":
        notes_parts.append("Eliminated relatively early (10:11 survival, 10th-longest of the match) to an extremely negative crowd reaction -- S106 opens this year's recap around this exact moment ('an extremely negative reaction from the live crowd...once Daniel Bryan was tossed out of the ring like a mid-carder').")
    if name == "Stardust":
        notes_parts.append("Billed as 'Stardust' at this event -- the same performer as this database's existing 'cody-rhodes' wrestler_id, reused per this database's established precedent for in-career gimmick/ring-name changes.")
    if name == "Damien Mizdow":
        notes_parts.append("Billed as 'Damien Mizdow' at this event -- the same performer as this database's existing 'damien-sandow' wrestler_id, reused per this database's established precedent.")
    if name == "Bad News Barrett":
        notes_parts.append("Billed as 'Bad News Barrett' at this event -- the same performer as this database's existing 'wade-barrett' wrestler_id, reused per this database's established precedent.")
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
            "source_ids": "S106",
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
        "is_runner_up": "TRUE" if name == "Rusev" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "TRUE" if name == "Diamond Dallas Page" else "FALSE",
        "legend_returning": "TRUE" if name == "Diamond Dallas Page" else "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "TRUE" if name in ("Diamond Dallas Page", "The Boogeyman") else "FALSE",
        "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED" if name != "Curtis Axel" else "PROBABLE",
        "source_ids": "S106",
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
    ("F282", EVENT_ID, "events", EVENT_ID, "event_date;venue;attendance_reported;commentary_team;referees", "unverified",
     "Like 2009/2011/2012/2013/2014, Shane's document has NO separate Dan Wahlers narrative history chapter for "
     "2015 -- only the Cageside timing analysis. Event-level facts (exact date, venue, attendance, commentary "
     "team, referees, undercard results) are simply absent from the source and left entirely UNKNOWN this pass, "
     "except that the host city is very likely Philadelphia (S106: 'Cole talks about Philadelphia') -- kept as "
     "PROBABLE-level color in event notes rather than promoted to the structured city_region field without a "
     "second source. event_date is stored as '2015-XX-XX'. Pending a future external-research pass.",
     "S106", "open", "2026-09-17"),
    ("F283", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "3 of 29 eliminations have an individually named eliminator this pass, all credited to the winner (Roman "
     "Reigns) during the match's final stretch, and internally cross-validated via the identical elim_ts "
     "computed for the simultaneous Kane/Big Show double-elimination. The remaining 26 elimination-eligible "
     "entrants have no named eliminator this pass. Left UNKNOWN rather than guessed.",
     "S106", "open", "2026-09-17"),
    ("F284", EVENT_ID, "entrants", "curtis-axel;erick-rowan", "n/a", "needs_human_judgement",
     "Two unusual, directly-addressed participation cases this year: (1) Curtis Axel is counted as an official "
     "entrant (entry #6) with a defined ring_time of 0:00, despite never functionally entering the ring, per "
     "S106's own explicit methodology choice -- he was attacked and substituted for by Erick Rowan before he "
     "could enter. (2) Erick Rowan is explicitly NOT counted as an official competitor by S106 ('The "
     "commentators emphasized the point that Rowan was not a legal participant, and so I treated his "
     "appearance...like any other run-in or interference') -- no entrant row was created for him in this "
     "match, even though he already exists in this database as a wrestler (from RR2014M). Both treatments "
     "follow the source's own explicit, stated methodology rather than this database inventing a convention.",
     "S106", "open", "2026-09-17"),
    ("F285", EVENT_ID, "entrants", "*", "ring_time", "unverified",
     "S106 extensively documents multiple specific discrepancies between its own calculated survival times and "
     "WWE's own officially published survival times for this match (named examples: Bubba Ray Dudley, Adam "
     "Rose, Titus O'Neil, Dean Ambrose), attributing most of them to WWE inconsistently including entrance time "
     "as part of 'survival time' for some wrestlers but not others. This database's ring_time field follows "
     "this project's own DEFINITIONS.md convention (ring-entry to elimination, excluding entrance walk) rather "
     "than WWE's own inconsistent methodology, so these are NOT modeled as CONFLICTING data -- they are a "
     "documented difference in what is being measured, not a factual disagreement about what happened. Dean "
     "Ambrose is the one exception S106 itself cannot explain (WWE's site lists 10:40 vs. this document's "
     "13:30, a gap too large to be accounted for by entrance time alone) -- flagged here as a genuine "
     "unresolved discrepancy pending a future external-research pass.",
     "S106", "open", "2026-09-17"),
    ("F286", EVENT_ID, "entrants", "roman-reigns;rusev;kane;big-show", "is_final_three", "needs_human_judgement",
     "Because Kane and Big Show were eliminated SIMULTANEOUSLY (the same Roman Reigns double-elimination spot), "
     "this match went directly from 4 competitors remaining (Reigns, Rusev, Kane, Big Show) to 2 (Reigns, "
     "Rusev) -- there was never a moment with exactly 3 wrestlers in the ring. is_final_three is left FALSE for "
     "all entrants this year rather than arbitrarily selecting one of Kane/Big Show to represent a 'final "
     "three' state that never actually existed. A genuinely unusual structural fact worth surfacing -- the "
     "only year built so far with a true 4-to-2 collapse at the finish.",
     "S106", "open", "2026-09-17"),
    ("F287", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 4 previously-unseen wrestlers this pass (Bubba Ray Dudley, Bray Wyatt, Curtis Axel, "
     "The Boogeyman, Adam Rose) with zero bio data in this pass's source -- names only. Left entirely UNKNOWN, "
     "same pattern as every prior year's equivalent flag. NOTE: 'Stardust', 'Damien Mizdow', and 'Bad News "
     "Barrett' were NOT added as new wrestlers -- all 3 reused this database's existing 'cody-rhodes', "
     "'damien-sandow', and 'wade-barrett' wrestler_ids respectively (well-documented in-career gimmick/ring-"
     "name changes for the same performers).",
     "S106", "open", "2026-09-17"),
    ("F288", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-17"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2015", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2015-XX-XX", "venue": "UNKNOWN",
    "city_region": "Philadelphia, Pennsylvania (PROBABLE -- see F282)", "country": "United States",
    "attendance_official": "", "attendance_reported": "",
    "entry_interval_seconds": 90, "entrant_count": 30, "duration_total": "59:35",
    "duration_status": "CONFIRMED",
    "winner_id": "roman-reigns", "runner_up_id": "rusev",
    "final_two_ids": "roman-reigns;rusev",
    "final_three_ids": "",
    "final_four_ids": "roman-reigns;rusev;kane;big-show",
    "first_entrant_id": "the-miz", "second_entrant_id": "r-truth", "final_entrant_id": "dolph-ziggler",
    "first_elimination_id": "the-miz", "last_elimination_before_winner_id": "rusev",
    "eliminations_count": 29, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": 1,
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
        "Roman Reigns's 1st career Royal Rumble win, entering at #19 and eliminating Rusev in the match's final "
        "moments -- famously met with heavy boos from the live Philadelphia crowd, still upset over Daniel "
        "Bryan's comparatively early elimination (10:11 survival, 10th-longest of the match). A surprise "
        "late appearance from The Rock, endorsing Reigns and physically confronting the already-eliminated Big "
        "Show and Kane, did not turn the crowd. Bray Wyatt posted the match's longest survival time (46:58), "
        "dominating the opening ~15 minutes with a series of one-on-one eliminations. Curtis Axel was counted "
        "as an official entrant with a 0:00 survival time after being attacked and substituted for by Erick "
        "Rowan before he could enter the ring -- Rowan himself is explicitly excluded as an official competitor "
        "by the source. The match's finish featured a simultaneous double-elimination (Big Show and Kane, both "
        "by Reigns) that triggered a false match-ending bell, since Rusev was still an active competitor -- "
        "meaning the match went directly from 4 competitors to 2, with no true 'final three' moment."
    ),
    "notes": (
        "Like 2009/2011/2012/2013/2014, this document has no Dan Wahlers narrative chapter for 2015 -- only the "
        "Cageside timing analysis. Entry order and survival times are CONFIRMED to the second for all 30 "
        "official entrants. 3 of 29 eliminations have named eliminator credit, all credited to the winner -- "
        "see F283. Event-level facts (exact date, venue, attendance, commentary, undercard) remain UNKNOWN -- "
        "see F282. Two unusual participation cases (Curtis Axel, Erick Rowan) are modeled per the source's own "
        "explicit methodology -- see F284. This is the only year built so far with a genuine 4-to-2 finish "
        "collapse (no 'final three' moment) -- see F286."
    ),
    "data_quality_status": "PROBABLE", "source_ids": "S106",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2015 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
