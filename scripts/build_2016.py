# -*- coding: utf-8 -*-
"""
Builds all rows for the 2016 Royal Rumble -- schema v2.

Like 2009/2011/2012/2013/2014/2015, Shane's doc has NO "Dan Wahlers
History of the Royal Rumble" chapter for 2016 -- only the "2016 Rumble
Stats - Cageside" frame-by-frame timing analysis (this year given as an
actual show-timing TABLE rather than inline prose, unlike every prior
Cageside-only year). Like 2014/2015, this year's buzzer list is FULLY
NAMED (28 named buzzers, matching entrants #3-30 directly) -- full entry
order is known with confidence. This is the richest, most heavily
cross-validated year built so far in this project's no-Wahlers-chapter
era.

SOURCES CONSULTED THIS PASS:
  S107 '2016 Rumble Stats - Cageside' section (Shane's doc)             tier 9
  S108 'Rumble Prediction 2016 - Paddy Power blog' trivia article
       (embedded in Shane's doc, published before the event)            tier 12

METHODOLOGY: entry_actual[name] = cumulative buzzer-gap time + entrance_
lag[name]. Roman Reigns and Rusev (the first two entrants) both start at
entry_actual=0 (pre-bell, per S107's own explicit statement). elim_ts
[name] = entry_actual[name] + survival_time[name]. Reigns's and Kofi
Kingston's RAW (unadjusted) survival times are used for the structured
ring_time/elim_ts fields, matching this database's established practice
of using headline, single-continuous-stretch figures for structured data;
S107's own separately-tracked "adjusted" figures (accounting for their
extended mid-match ring absences while still officially active) are
preserved in full in their entrant notes -- see F292.

Checksums (all verified before writing this script):
  - The cumulative buzzer sum across all 28 buzzers lands exactly on the
    doc's own stated actual final-buzzer mark of 52:37.
  - Triple H's (the winner's) own entry_actual + his own stated 7:49
    survival time lands EXACTLY on the match total (61:43) -- confirming
    he is entrant #30 (the final entrant) and the winner. S107 itself
    notes this 7:49 figure already includes one extra second of padding
    ("I gave Triple H one extra second of survival time at the very end
    of the match because it took about one second after Ambrose was
    eliminated for the bell to ring").
  - Dean Ambrose's own elim_ts computes to 61:42 -- exactly one second
    short of the match total (61:43), consistent with the note above:
    Ambrose was the true final elimination (the runner-up, eliminated by
    Triple H), with the bell ringing about a second later.
  - Luke Harper's own elim_ts computes to EXACTLY 44:18, matching S107's
    own directly-stated timestamp for his elimination ("There were always
    5 to 8 men in the ring between the time stamps of 11m 19s and 44m
    18s. The latter time stamp is when Luke Harper was eliminated by
    Brock Lesnar").
  - Kane's and Big Show's elim_ts (28:19 and 29:10) fall 51 seconds apart
    within the SAME buzzer waiting period S107 describes as containing
    both eliminations "back-to-back" by Braun Strowman -- consistent,
    though not simultaneous (unlike 2015's Kane/Big Show double
    elimination, which WAS simultaneous -- a fun coincidental repeat of
    the exact same 2-man combination a year apart, this time credited to
    a different eliminator).

NAMED ELIMINATIONS THIS YEAR:
  - Luke Harper <- Brock Lesnar (S107, direct + exact timestamp match)
  - Kane <- Braun Strowman (S107, direct: "Strowman's eliminations of
    Kane and Big Show... back-to-back")
  - Big Show <- Braun Strowman (S107, direct, same statement as above)
  - AJ Styles <- Kevin Owens (S107, direct: "Kevin Owens and his
    subsequent elimination of AJ Styles")
  - Brock Lesnar <- Bray Wyatt (+ Wyatt Family group interference) (S107,
    direct but not individually enumerated: "Brock Lesnar was going to be
    eliminated by the entire Wyatt Family... Bray's three thugs unfairly
    entered the ring to deal with Lesnar." Modeled as shared/PROBABLE
    with Bray Wyatt as the one confirmed-active, officially-competing
    eliminator -- the other "thugs" are almost certainly Erick Rowan and
    Luke Harper (both already-eliminated Wyatt Family members at that
    point, interfering from outside per this database's established
    precedent for that scenario, e.g. RR2012M/RR2014M) plus possibly
    Braun Strowman, but S107 does not individually name them, so they are
    NOT added as additional credited eliminators this pass -- see F291.
  - Dean Ambrose <- Triple H (the winning elimination -- not itself
    phrased as "Triple H eliminated Ambrose" by S107 in so many words,
    but inferred with high confidence via the same standard convention
    applied to every winner/runner-up pair built so far in this project:
    the winner performs the match's final, winning elimination. Directly
    supported by S107's own explicit statement that Triple H's survival
    time includes "one extra second...after Ambrose was eliminated," and
    by the checksum confirming Ambrose's elim_ts lands one second before
    the match total.)
All other elimination-eligible entrants have no individually named
eliminator this pass -- left UNKNOWN rather than guessed.

TWO NOTABLE STRUCTURAL/TIMING CURIOSITIES THIS YEAR:
  - Roman Reigns and Kofi Kingston both have RAW survival times that
    include an extended mid-match absence from the ring while still
    officially active in the match (Reigns: entered #1, pulled outside
    and attacked by the League of Nations at 21:00, returned at 51:23,
    survived to 59:48 -- raw 59:48, adjusted 29:25 for the two combined
    active stretches; Kofi: raw 8:10, adjusted 4:29). S107 provides BOTH
    a raw and an absence-adjusted version of several match-wide stats
    (average/median survival time, ring-crowdedness table) for this
    reason -- both are preserved in this database's notes, with the RAW
    figures used for the structured ring_time/elim_ts fields. See F292.
  - Despite being the OFFICIAL 30th (final) entrant by buzzer order,
    Triple H actually physically stepped into the ring BEFORE Sheamus
    (the official 29th entrant), because Sheamus's own entrance was
    interrupted by a Roman Reigns attack and took 4:29 versus Triple H's
    1:17 -- S107 directly notes this. entry_number still follows buzzer
    order per this database's established convention (not actual
    ring-entry order) -- see F293.

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order and survival time are known to the second for ALL 30
    entrants -- matching 2014's completeness.
  - 6 of 29 eliminations have an individually named eliminator this pass
    (5 fully named plus the standard winner/runner-up inference), the
    richest year built so far for this project's no-Wahlers-chapter era.
  - Event-level facts (attendance, venue, exact date, commentary,
    referees, undercard) are UNKNOWN -- no Wahlers chapter exists for
    this year, though the show-timing breakdown this year is unusually
    given as an actual table rather than inline prose. event_date stored
    as '2016-XX-XX', same convention as prior no-Wahlers-chapter years.
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
EVENT_ID = "RR2016M"


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
    ("S107", "'2016 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-17",
     "Frame-by-frame-style timing analysis (survival times, entrance times, fully named time-between-buzzers, "
     "ring crowdedness -- given as an actual show-timing TABLE this year, unlike prior Cageside-only years' "
     "inline prose) filed under the '2016 Royal Rumble Stats' Heading-1. NO separate Dan Wahlers narrative "
     "history chapter exists for this year. Directly narrates 5 individual/group eliminations, extensively "
     "documents Roman Reigns's and Kofi Kingston's extended mid-match ring absences (both raw and adjusted "
     "figures given throughout), and notes Triple H physically entering the ring before Sheamus despite being "
     "the later official entrant. NOT live-fetched this pass."),
    ("S108", "'Rumble Prediction 2016' article, Paddy Power blog (by Josh Powell, published January 20, 2016)", "other_stats_site", "", 12, "Other reputable site", "2026-09-17",
     "A pre-event trend-analysis trivia article embedded in Shane's document, examining height/weight/age/"
     "experience patterns across 780 Royal Rumble entrants (1988-2015) to predict a 'model winner' -- named "
     "Sheamus (who did not win; Triple H did). Used this pass only for a single piece of color trivia in "
     "events.csv notes, not for any structured match data. Historical/statistical claims about entrants prior "
     "to 2016 are NOT independently verified against this database's own records this pass."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# TIMING DERIVATION
# ---------------------------------------------------------------------------
buzzer_gaps = [
    ("AJ Styles", "1:46"), ("Tyler Breeze", "2:09"), ("Curtis Axel", "1:37"), ("Chris Jericho", "1:47"),
    ("Kane", "1:52"), ("Goldust", "1:45"), ("Ryback", "1:44"), ("Kofi Kingston", "1:42"),
    ("Titus O'Neil", "1:44"), ("R-Truth", "1:48"), ("Luke Harper", "2:07"), ("Stardust", "2:12"),
    ("Big Show", "1:58"), ("Neville", "1:47"), ("Braun Strowman", "1:45"), ("Kevin Owens", "1:55"),
    ("Dean Ambrose", "2:05"), ("Sami Zayn", "1:57"), ("Erick Rowan", "1:42"), ("Mark Henry", "1:50"),
    ("Brock Lesnar", "1:47"), ("Jack Swagger", "1:48"), ("Miz", "1:42"), ("Alberto Del Rio", "2:05"),
    ("Bray Wyatt", "1:41"), ("Dolph Ziggler", "3:01"), ("Sheamus", "1:41"), ("Triple H", "1:40"),
]
buzzer_time = {}
cum = 0
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("52:37"), f"buzzer checksum failed: {cum}"

# Entrance times. Roman Reigns and Rusev (pre-bell, the first two
# entrants) are excluded, same treatment as prior years' opening pair.
entrance_lag = {
    "Miz": "7:19", "Sheamus": "4:29", "Triple H": "1:17", "AJ Styles": "1:11", "Luke Harper": "0:44",
    "Bray Wyatt": "0:42", "Big Show": "0:38", "Chris Jericho": "0:34", "Kevin Owens": "0:34",
    "Kane": "0:25", "Kofi Kingston": "0:25", "Curtis Axel": "0:24", "R-Truth": "0:24",
    "Dean Ambrose": "0:24", "Sami Zayn": "0:24", "Goldust": "0:23", "Erick Rowan": "0:22",
    "Tyler Breeze": "0:21", "Ryback": "0:20", "Mark Henry": "0:20", "Brock Lesnar": "0:20",
    "Braun Strowman": "0:19", "Stardust": "0:17", "Neville": "0:17", "Jack Swagger": "0:16",
    "Alberto Del Rio": "0:15", "Titus O'Neil": "0:12", "Dolph Ziggler": "0:12",
}
entry_actual = {"Roman Reigns": 0, "Rusev": 0}
for name in buzzer_time:
    entry_actual[name] = buzzer_time[name] + mmss(entrance_lag[name])

# Survival ("ring") times, as stated directly by S107 (RAW figures -- see
# docstring for Reigns/Kofi's separately-tracked absence-adjusted values,
# preserved in their entrant notes rather than used here).
survival = {
    "Roman Reigns": "59:48", "Chris Jericho": "50:47", "Dean Ambrose": "29:35", "AJ Styles": "27:49",
    "Luke Harper": "23:33", "Kane": "18:43", "Braun Strowman": "17:44", "Stardust": "13:57",
    "Ryback": "12:20", "Bray Wyatt": "10:44", "Neville": "10:01", "Brock Lesnar": "9:12",
    "Titus O'Neil": "8:56", "Kofi Kingston": "8:10", "Triple H": "7:49", "Dolph Ziggler": "7:00",
    "Alberto Del Rio": "6:47", "Goldust": "5:57", "Sami Zayn": "4:32", "Kevin Owens": "4:25",
    "Big Show": "4:21", "Sheamus": "4:18", "Erick Rowan": "4:13", "Miz": "1:38", "Rusev": "1:30",
    "Curtis Axel": "1:08", "Tyler Breeze": "0:57", "R-Truth": "0:37", "Mark Henry": "0:28",
    "Jack Swagger": "0:15",
}
assert set(survival) == set(entry_actual), set(survival) ^ set(entry_actual)
assert len(survival) == 30

MATCH_TOTAL = mmss("61:43")
assert entry_actual["Triple H"] + mmss(survival["Triple H"]) == MATCH_TOTAL

elim_ts = {}
for name, t in survival.items():
    if name == "Triple H":
        continue  # winner, never eliminated
    elim_ts[name] = entry_actual[name] + mmss(t)
assert secs_to_mmss(elim_ts["Dean Ambrose"]) == "61:42"  # 1s short of MATCH_TOTAL -- see docstring, S107's own note
assert secs_to_mmss(elim_ts["Luke Harper"]) == "44:18"  # matches S107's own directly-stated timestamp

elim_order_list = sorted(elim_ts, key=lambda n: elim_ts[n])
elim_number = {name: i + 1 for i, name in enumerate(elim_order_list)}
assert elim_number["Rusev"] == 1
assert elim_number["Dean Ambrose"] == 29  # the winning elimination, last of 29

ENTRY_NUMBERS = {"Roman Reigns": 1, "Rusev": 2}
for i, (name, _) in enumerate(buzzer_gaps):
    ENTRY_NUMBERS[name] = i + 3
assert ENTRY_NUMBERS["AJ Styles"] == 3 and ENTRY_NUMBERS["Triple H"] == 30
assert ENTRY_NUMBERS["Sheamus"] == 29

FINAL_TWO = {"Triple H", "Dean Ambrose"}
FINAL_THREE = {"Triple H", "Dean Ambrose", "Roman Reigns"}
FINAL_FOUR = {"Triple H", "Dean Ambrose", "Roman Reigns", "Sheamus"}

# name -> (eliminator names, data_quality_status, notes, is_shared, group_id)
KNOWN_ELIMINATORS = {
    "Luke Harper": (["Brock Lesnar"], "CONFIRMED",
                     "S107 directly states 'Luke Harper was eliminated by Brock Lesnar,' with a timestamp "
                     "(44:18) matching this script's own computed elim_ts exactly.", False, ""),
    "Kane": (["Braun Strowman"], "CONFIRMED",
              "S107 directly states 'Strowman's eliminations of Kane and Big Show,' describing them as "
              "occurring back-to-back within the same waiting period (this script's own elim_ts computes them "
              "51 seconds apart, consistent with 'back-to-back' rather than simultaneous).", False, ""),
    "Big Show": (["Braun Strowman"], "CONFIRMED",
                  "S107 directly states 'Strowman's eliminations of Kane and Big Show' -- see Kane's note "
                  "above.", False, ""),
    "AJ Styles": (["Kevin Owens"], "CONFIRMED",
                   "S107 directly states 'Kevin Owens and his subsequent elimination of AJ Styles.'", False, ""),
    "Brock Lesnar": (["Bray Wyatt"], "PROBABLE",
                      "S107 directly states 'Brock Lesnar was going to be eliminated by the entire Wyatt "
                      "Family' and separately describes 'Bray's three thugs unfairly entered the ring to deal "
                      "with Lesnar' (with only 5 of the resulting 8 men in the ring counted as officially "
                      "active). Modeled as shared credit with Bray Wyatt (the one Wyatt Family member "
                      "confirmed still officially active/legal at this point) as the sole named eliminator -- "
                      "the other 'thugs' are almost certainly Erick Rowan and/or Luke Harper (both already-"
                      "eliminated Wyatt Family members by this point, interfering from outside, matching this "
                      "database's established precedent for that scenario elsewhere) but S107 does not "
                      "individually name them, so they are NOT added as additional credited eliminators this "
                      "pass. See F291.", True, "wyatt_family_group"),
    "Dean Ambrose": (["Triple H"], "CONFIRMED",
                       "The winning elimination. Not phrased by S107 as 'Triple H eliminated Ambrose' in so "
                       "many words, but inferred via the same standard convention applied to every winner/"
                       "runner-up pair built so far in this project (the winner performs the match's final "
                       "elimination), directly supported by S107's own explicit note that Triple H's survival "
                       "time includes 'one extra second...after Ambrose was eliminated,' and by this script's "
                       "own checksum confirming Ambrose's elim_ts lands exactly one second before the match "
                       "total.", False, ""),
}

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("AJ Styles", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #3. Survived 27:49, the 4th-longest survival time of the match. Per S107, his 'ridiculously long entrance' and the crowd reaction it created led WWE to extend the following waiting period so he and Reigns could fight before the next entrant came out.", "S107"),
    ("Tyler Breeze", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #4. Survived 0:57.", "S107"),
    ("Neville", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #16. Survived 10:01. Per S108 (a pre-event trivia article), Neville was one of several potential 'win on debut' candidates that year's trend analysis flagged as a long shot -- he did not win.", "S107;S108"),
    ("Braun Strowman", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #17. Survived 17:44. Credited with eliminating both Kane and Big Show, back-to-back, in the same waiting period.", "S107"),
    ("Kevin Owens", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #18. Survived 4:25 -- also wrestled Dean Ambrose earlier on the same card (Last Man Standing match). Credited with eliminating AJ Styles.", "S107"),
    ("Sami Zayn", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rumble debut, entered #20. Survived 4:32.", "S107"),
]

reused = {
    "Curtis Axel": "curtis-axel", "Chris Jericho": "chris-jericho", "Kane": "kane", "Goldust": "goldust",
    "Ryback": "ryback", "Kofi Kingston": "kofi-kingston", "Titus O'Neil": "titus-oneil", "R-Truth": "r-truth",
    "Luke Harper": "luke-harper", "Big Show": "big-show", "Dean Ambrose": "dean-ambrose",
    "Erick Rowan": "erick-rowan", "Mark Henry": "mark-henry", "Brock Lesnar": "brock-lesnar",
    "Jack Swagger": "jack-swagger", "Miz": "the-miz", "Alberto Del Rio": "alberto-del-rio",
    "Bray Wyatt": "bray-wyatt", "Dolph Ziggler": "dolph-ziggler", "Sheamus": "sheamus",
    "Triple H": "hunter-hearst-helmsley", "Roman Reigns": "roman-reigns", "Rusev": "rusev",
    "Stardust": "cody-rhodes",
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
    "Roman Reigns", "Rusev", "AJ Styles", "Tyler Breeze", "Curtis Axel", "Chris Jericho", "Kane", "Goldust",
    "Ryback", "Kofi Kingston", "Titus O'Neil", "R-Truth", "Luke Harper", "Stardust", "Big Show", "Neville",
    "Braun Strowman", "Kevin Owens", "Dean Ambrose", "Sami Zayn", "Erick Rowan", "Mark Henry", "Brock Lesnar",
    "Jack Swagger", "Miz", "Alberto Del Rio", "Bray Wyatt", "Dolph Ziggler", "Sheamus", "Triple H",
]
assert len(all_names) == 30

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Triple H")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, dq, method, is_shared, group_id = KNOWN_ELIMINATORS.get(name, ([], "", "", False, ""))

    notes_parts = []
    if name == "Triple H":
        notes_parts.append("Entered #30 (the official final entrant) and won, eliminating Dean Ambrose in the match's final second. Per S107, despite being the LATER official entrant, Triple H physically stepped into the ring BEFORE #29 Sheamus, whose own entrance was interrupted by a Roman Reigns attack and stretched to 4:29 versus Triple H's 1:17. See F293.")
    elif name == "Dean Ambrose":
        notes_parts.append("Eliminated by Triple H in the match's final second -- the winning elimination, and the runner-up spot. Also wrestled Kevin Owens in a Last Man Standing match earlier on the same card.")
    elif name == "Roman Reigns":
        notes_parts.append("Entered #1 (pre-bell) as the reigning WWE Champion, defending the title WITHIN this Royal Rumble match itself (per S107's direct statement that the match 'featured Roman Reigns trying to overcome everybody on the roster but ultimately losing his WWE Championship to Triple H') -- only the second time in Rumble history a world title was decided by the match itself, after Ric Flair in 1992. He lost the championship as a consequence of the match's outcome (Triple H winning), not via any separate same-card title match -- see F296, correcting an earlier pass's erroneous claim that he lost the title to Sheamus earlier that night (no such match exists in the source; Sheamus's own real-world MITB cash-in loss of the title back to Reigns happened in December 2015, a different event entirely, likely the source of the original error). RAW survival time is 59:48 (used for this row's ring_time/elim_ts fields, per this database's standard convention), but S107 separately tracks an ADJUSTED figure of 29:25: Reigns was dragged outside the ring and attacked by the League of Nations starting at the 21:00 mark, was last seen on camera walking to the back at 26:48, and did not return to the ring until 51:23 -- his two active stretches (0:00-21:00 and 51:23-59:48) sum to 29:25. See F292.")
    elif name == "Kofi Kingston":
        notes_parts.append("RAW survival time is 8:10 (used for this row's ring_time/elim_ts fields), but S107 separately tracks an ADJUSTED figure of 4:29 for an extended mid-match absence. His elimination was not shown live on camera -- S107 pins it down via a replay shown minutes later, to within an estimated 4-second margin of confidence. See F292.")
    elif name in ("Kane", "Big Show"):
        notes_parts.append("Eliminated by Braun Strowman, back-to-back with the other in the same waiting period (51 seconds apart). Coincidentally, this exact Kane/Big Show pairing was ALSO eliminated together the previous year (RR2015M), that time simultaneously and by a different eliminator (Roman Reigns).")
    elif name == "Brock Lesnar":
        notes_parts.append("Eliminated in a group interference spot by 'the entire Wyatt Family' per S107, with Bray Wyatt as the only individually-confirmed, officially-active eliminator credited this pass -- see F291. Also eliminated Luke Harper earlier in the match.")
    elif name == "Luke Harper":
        notes_parts.append("Eliminated by Brock Lesnar at the 44:18 mark (exact match to this script's own computed elim_ts).")
    if name == "Stardust":
        notes_parts.append("Billed as 'Stardust' at this event -- the same performer as this database's existing 'cody-rhodes' wrestler_id, reused per this database's established precedent. His exact ring-entry moment was not shown on camera (Reigns's League of Nations attack was airing at the time), but S107 estimates the uncertainty at only a couple of seconds.")
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
            "source_ids": "S107",
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
        "faction_stable": "The Wyatt Family" if name in ("Bray Wyatt", "Luke Harper", "Erick Rowan", "Braun Strowman") else "",
        "current_champion_title": "WWE Championship" if name == "Roman Reigns" else "",
        "championship_level": "World" if name == "Roman Reigns" else "",
        "championship_partner": "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        # NOTE: title_defended_same_card/title_lost_same_card track a SEPARATE title match held
        # elsewhere on the same card (e.g. The Rock 1998) -- they do NOT apply to Reigns here, since
        # his WWE Championship was on the line WITHIN this Royal Rumble match itself, not a distinct
        # undercard bout. Both are FALSE for everyone this year. Corrected -- see F296 and Reigns's note.
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
        "is_runner_up": "TRUE" if name == "Dean Ambrose" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "FALSE",
        "legend_returning": "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE",
        "wrestled_earlier_on_card": "TRUE" if name in ("Dean Ambrose", "Kevin Owens", "Kofi Kingston", "Alberto Del Rio") else "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S107",
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
    ("F289", EVENT_ID, "events", EVENT_ID, "event_date;venue;attendance_reported;commentary_team;referees", "unverified",
     "Like every no-Wahlers-chapter year built so far, Shane's document has no separate Dan Wahlers narrative "
     "history chapter for 2016 -- only the Cageside timing analysis (this year given as an actual timing TABLE "
     "rather than inline prose). Event-level facts (exact date, venue, city, attendance, commentary team, "
     "referees, undercard results) are simply absent from the source and left entirely UNKNOWN this pass. "
     "event_date is stored as '2016-XX-XX'. Pending a future external-research pass.",
     "S107", "open", "2026-09-17"),
    ("F290", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "6 of 29 eliminations have an individually named eliminator this pass (5 fully named by S107 plus the "
     "standard winner/runner-up inference) -- the richest year built so far for this project's "
     "no-Wahlers-chapter era. The remaining 23 elimination-eligible entrants have no named eliminator this "
     "pass. Left UNKNOWN rather than guessed.",
     "S107", "open", "2026-09-17"),
    ("F291", EVENT_ID, "eliminations", "brock-lesnar", "eliminator_wrestler_id", "needs_human_judgement",
     "Brock Lesnar's credited eliminator (Bray Wyatt, shared) undercounts the group involved -- S107 describes "
     "this as 'the entire Wyatt Family' with 'Bray's three thugs unfairly [entering] the ring,' implying "
     "multiple additional interferers beyond Wyatt himself (most likely Erick Rowan and/or Luke Harper, both "
     "already-eliminated Wyatt Family members by this point in the match, interfering from outside -- a known "
     "pattern elsewhere in this database, e.g. RR2012M's Michael Cole, RR2014M's Kane/CM Punk). None are "
     "individually named by S107, so none beyond Wyatt are added as credited eliminators this pass. Pending a "
     "future external-research pass to identify the full group, if recoverable.",
     "S107", "open", "2026-09-17"),
    ("F292", EVENT_ID, "entrants", "roman-reigns;kofi-kingston", "ring_time", "unverified",
     "Roman Reigns and Kofi Kingston both have RAW survival times used for this row's structured ring_time/"
     "elim_ts fields (59:48 and 8:10 respectively), per this database's standard convention. S107 separately "
     "tracks ADJUSTED figures for both (29:25 and 4:29) accounting for extended mid-match absences from the "
     "ring while still officially active in the match -- both figures are preserved in each wrestler's entrant "
     "notes. This is NOT a data conflict -- both numbers are correct under their own respective definitions "
     "(total official participation window vs. time actually active in the ring) -- but a future pass could "
     "consider adding dedicated adjusted-time fields to entrants.csv if this pattern recurs in other years.",
     "S107", "open", "2026-09-17"),
    ("F293", EVENT_ID, "entrants", "hunter-hearst-helmsley;sheamus", "entry_number", "unverified",
     "Despite Triple H being the OFFICIAL 30th (final) entrant by buzzer order and Sheamus the 29th, S107 "
     "directly notes Triple H physically entered the ring BEFORE Sheamus, whose own entrance was interrupted "
     "by a Roman Reigns attack and stretched to 4:29 (versus Triple H's 1:17). entry_number in this database "
     "follows buzzer/official-draw order (the established convention across every year built so far), not "
     "actual physical ring-entry order, so this is preserved as a notable trivia fact in both wrestlers' notes "
     "rather than altering the structured entry_number field.",
     "S107", "open", "2026-09-17"),
    ("F294", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 6 previously-unseen wrestlers this pass (AJ Styles, Tyler Breeze, Neville, Braun "
     "Strowman, Kevin Owens, Sami Zayn) with zero bio data in this pass's source -- names only. Left entirely "
     "UNKNOWN, same pattern as every prior year's equivalent flag. NOTE: 'Stardust' was NOT added as a new "
     "wrestler -- reused this database's existing 'cody-rhodes' wrestler_id per established precedent.",
     "S107", "open", "2026-09-17"),
    ("F295", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-17"),
    ("F296", EVENT_ID, "entrants;events", "roman-reigns;RR2016M", "title_lost_same_card;title_on_the_line;championship_implications;historical_significance", "corrected",
     "CORRECTION (2026-09-17): this year's original build pass incorrectly stated that Roman Reigns lost the "
     "WWE Championship to Sheamus earlier on the same show, before entering the Rumble at #1. S107 itself "
     "directly states the opposite: 'This match featured Roman Reigns trying to overcome everybody on the "
     "roster but ultimately losing his WWE Championship to Triple H' -- i.e. the title was defended WITHIN "
     "the Royal Rumble match itself (only the second time in Rumble history a world title was decided by the "
     "match itself, after Ric Flair in 1992), and Reigns lost it as a consequence of the match's own outcome "
     "when Triple H won, not via any separate same-card bout. No Reigns-vs-Sheamus title match exists anywhere "
     "in the source document. (Likely origin of the error: Sheamus's own real-world MITB cash-in loss of the "
     "title back to Reigns took place in December 2015, a wholly separate event, probably conflated during the "
     "original build.) Corrected: entrants.csv's Roman Reigns row now has title_lost_same_card=FALSE (this "
     "field tracks a distinct same-card title match, which did not occur), events.csv's title_on_the_line is "
     "now TRUE, and championship_implications/special_rules/winners_reward/historical_significance have all "
     "been rewritten to state the correct fact, with a citation to S107's own words.",
     "S107", "resolved", "2026-09-17"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2016", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2016-XX-XX", "venue": "UNKNOWN",
    "city_region": "UNKNOWN", "country": "UNKNOWN",
    "attendance_official": "", "attendance_reported": "",
    "entry_interval_seconds": 90, "entrant_count": 30, "duration_total": "61:43",
    "duration_status": "CONFIRMED",
    "winner_id": "hunter-hearst-helmsley", "runner_up_id": "dean-ambrose",
    "final_two_ids": "hunter-hearst-helmsley;dean-ambrose",
    "final_three_ids": "hunter-hearst-helmsley;dean-ambrose;roman-reigns",
    "final_four_ids": "hunter-hearst-helmsley;dean-ambrose;roman-reigns;sheamus",
    "first_entrant_id": "roman-reigns", "second_entrant_id": "rusev", "final_entrant_id": "hunter-hearst-helmsley",
    "first_elimination_id": "rusev", "last_elimination_before_winner_id": "dean-ambrose",
    "eliminations_count": 29, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": "UNKNOWN",
    "champions_in_field_count": 1, "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": 1,
    "commentary_team": "UNKNOWN",
    "ring_announcer": "UNKNOWN",
    "referees": "UNKNOWN",
    "special_rules": "The WWE Championship, held by Roman Reigns entering the match, was defended WITHIN the Royal Rumble match itself -- only the second time in Rumble history a world title was decided by the match itself, after Ric Flair in 1992 (S107, direct statement). Corrected this pass -- see F296.",
    "title_on_the_line": "TRUE",
    "championship_implications": "CONFIRMED (S107, direct statement): the WWE Championship was on the line inside this Royal Rumble match itself, defended by reigning champion Roman Reigns (this match's #1 entrant). Reigns lost the title as a consequence of the match's outcome when Triple H won the match; no separate same-card title match took place. No other undercard results are recorded in the source document this year. See F296 for a correction to an earlier pass's erroneous claim that Reigns lost the title to Sheamus in a separate match earlier that night.",
    "winners_reward": "The WWE Championship (title was on the line inside the match itself; Triple H became champion by winning the Rumble). See championship_implications and F296.",
    "historical_significance": (
        "Triple H's Royal Rumble win as recorded in this database (his real-world Rumble history includes an "
        "earlier win not yet built into this database as of this pass), entering as the "
        "official 30th (final) entrant and eliminating Dean Ambrose in the match's final second -- and, since "
        "the WWE Championship was on the line inside the match itself (see below), also becoming WWE Champion "
        "by winning it. This match ran "
        "an unusually long 61:43 (the longest Royal Rumble match timed in this document's entire multi-year "
        "data set at the time of writing) and featured Roman Reigns, the reigning WWE Champion, entering at #1 "
        "and defending the title WITHIN the match itself -- only the second time in Rumble history a world "
        "title was decided by the match itself, after Ric Flair in 1992 (S107) -- while also battling the "
        "League of Nations stable through an extended mid-match absence from the ring; he lost the title when "
        "Triple H won the match. See F296 for a correction to an earlier pass's erroneous claim that Reigns "
        "lost the title to Sheamus in a separate match earlier that night. A pre-event trend-analysis trivia article (S108) "
        "had picked Sheamus as the statistical 'model winner' based on historical height/weight/age/experience "
        "patterns -- Sheamus did not win, eliminated among the match's final four. Braun Strowman, in his Rumble "
        "debut, eliminated both Kane and Big Show back-to-back -- the exact same 2-man combination eliminated "
        "together (that time simultaneously) by Roman Reigns the previous year. Brock Lesnar was eliminated in "
        "a group interference spot by 'the entire Wyatt Family.'"
    ),
    "notes": (
        "Like every no-Wahlers-chapter year built so far, this document has no Dan Wahlers narrative chapter "
        "for 2016 -- only the Cageside timing analysis, given this year as an actual timing table. Entry order "
        "and survival times are CONFIRMED to the second for all 30 entrants. 6 of 29 eliminations have named "
        "eliminator credit -- see F290. Event-level facts (date, venue, attendance, commentary, undercard) "
        "remain UNKNOWN -- see F289. Two notable curiosities flagged this pass: Roman Reigns's and Kofi "
        "Kingston's raw-vs-absence-adjusted survival times (F292), and Triple H physically entering the ring "
        "before Sheamus despite being the later official entrant (F293)."
    ),
    "data_quality_status": "PROBABLE", "source_ids": "S107;S108",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2016 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} flags ({sum(1 for fl in flags if fl[-2]=='open')} open).")
