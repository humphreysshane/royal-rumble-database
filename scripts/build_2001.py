# -*- coding: utf-8 -*-
"""
Builds all rows for the 2001 Royal Rumble -- schema v2.

Rich year like 1991/1993/1995/1997/1999: Shane's doc has a full "2001
Rumble Stats - Cageside" frame-by-frame timing analysis (survival times,
entrance times, time-between-buzzers, ring crowdedness) PLUS the Dan
Wahlers narrative history section, both under the "2001 Royal Rumble
Stats" Heading-1.

SOURCES CONSULTED THIS PASS:
  S047 '2001 Rumble Stats - Cageside' section (Shane's doc)              tier 9
  S048 Dan Wahlers, 'History of the Royal Rumble' -- 2001 chapter        tier 9

METHODOLOGY (mirrors 1999's DERIVED elimination-order pattern):
  entry_actual[name] = cumulative buzzer-gap time + entrance_lag[name].
  elim_ts[name] = entry_actual[name] + survival_time[name] (both given
  directly by S047). All 30 entrants are ranked by elim_ts to derive
  elim_number. Jeff Hardy and Bull Buchanan (the first two entrants) both
  start at entry_actual=0, per S047's own note that their pre-bell contact
  wasn't counted as match time. Multiple internal checksums in S047 itself
  validate this derivation: the cumulative buzzer sum lands exactly on the
  stated "51m 42s" final-buzzer mark; Tazz's and William Regal's named
  elimination timestamps (24:03 and 37:16) land exactly on this script's
  computed values; the 5-eliminations-in-10-seconds span S047 describes
  (43:31-43:41) matches exactly (Bradshaw 43:31, Crash Holly 43:33, Albert
  43:36, Hardcore Holly 43:37, Val Venis 43:41); Hardcore Holly's own
  stated entry (29:32) and elimination (43:37) timestamps both match
  exactly; and computing who was still active when Austin finally entered
  the ring produces exactly the 7 names S047 lists for the match's final
  segment (Kane, Rock, Undertaker, Billy Gunn, Haku, Rikishi, Austin) --
  all independently confirming the derivation below. See the assert
  checkpoints in this script.

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order and survival ("ring") time are known to the second for ALL
    30 entrants, and NO camera-cut timing issues are documented this year
    (unlike 1999's F120) -- ring_time_status is CONFIRMED throughout.
  - Eliminator credit is unusually rich for a Cageside-style year: Kane
    (Honky Tonk Man, Al Snow, Steve Blackman, Perry Saturn, and Rock --
    5 of his record-setting 11 total eliminations named individually),
    Rock (Big Show, Rikishi), Rikishi (The Undertaker), Austin (Billy
    Gunn, and Kane for the win), Matt Hardy and Jeff Hardy (mutual
    elimination of each other, and a shared elimination of Bull Buchanan
    together), and Drew Carey (a self-elimination -- he "smartly
    eliminated himself by jumping over the top rope" after failing to
    bribe Kane). The other ~6 of Kane's 11 total, Big Show's own "couple
    of people," and Undertaker/Kane's joint unnamed victims are left
    unassigned rather than guessed. See F131.
  - STEVE AUSTIN'S UNIQUE DELAYED ENTRY (new structural situation -- see
    F130): Austin drew #27, but Triple H attacked him in the aisle before
    he could enter the ring (payback for Austin costing HHH his title
    shot earlier that night). Austin recovered and, per S047's own timing
    data, his official ring-entry moment (entry_actual) lands just ONE
    SECOND after Rikishi's (the officially-numbered #30 entrant) --
    confirming S047's own claim that Austin, despite drawing #27, was
    actually the LAST man to physically enter the ring, after throwing an
    attacked Rikishi into the ring ahead of him. entry_number is kept at
    27 (his drawn/announced number, this database's standard convention),
    with this flag documenting the actual-entry-order anomaly rather than
    inventing a different field value. final_entrant_id in events.csv is
    kept as rikishi (the officially-numbered 30th entrant) for the same
    reason. Austin's OFFICIAL entrance_lag/survival time in S047 (6:01)
    includes the entire Triple H beatdown; S047's own "adjusted" figure
    (0:17, how long his entrance lasted before the attack) is preserved in
    his notes as a supplementary stat, mirroring how 1999 handled Austin/
    McMahon's official-vs-adjusted survival times.
  - "Scotty 2 Hotty" (buzzer 24, entrant #26) is widely known in general
    wrestling history to be the same performer (Scott Anthony Garland) who
    wrestled as "Scott Taylor" in this database's 2000 build (wrestler_id
    scott-taylor) -- but neither source consulted this pass states that
    connection directly. Left as a separate, new wrestler_id pending a
    future fact-check pass, the same caution already applied to X-Pac/
    1-2-3 Kid (1999's F118) and Viscera/Mabel (2000's F127). See F132.
    By contrast, "Grand Master Sexay" (buzzer 9, entrant #11) is the exact
    same ring name/gimmick already used for this database's existing
    wrestler_id brian-christopher (2000) -- reused directly, not a merge
    question at all.
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
EVENT_ID = "RR2001M"


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
    ("S047", "'2001 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers, ring "
     "crowdedness) filed under the '2001 Royal Rumble Stats' Heading-1. Explicitly documents Steve Austin's "
     "delayed/out-of-order physical entry (drew #27, entered after #30) -- see F130. NOT live-fetched this pass."),
    ("S048", "Dan Wahlers, 'History of the Royal Rumble' -- 2001 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance (17,137), full narrative "
     "history (Kane's record-setting 11 eliminations, the Austin/HHH aisle attack, the Austin/Rock/Kane final "
     "stretch), and undercard match results. States Austin's drawn number as '#26,' which conflicts with "
     "S047's explicit '#27' -- S047's figure is used per this project's preference for the more rigorous "
     "timing-analysis source -- see F130."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# TIMING DERIVATION
# ---------------------------------------------------------------------------
buzzer_gaps = [
    ("Matt Hardy", "1:45"), ("Faarooq", "1:47"), ("Drew Carey", "1:46"), ("Kane", "1:46"),
    ("Raven", "1:46"), ("Al Snow", "1:44"), ("Perry Saturn", "1:49"), ("Steve Blackman", "1:56"),
    ("Grand Master Sexay", "1:46"), ("Honky Tonk Man", "1:53"), ("The Rock", "2:11"),
    ("Goodfather", "1:49"), ("Tazz", "1:46"), ("Bradshaw", "1:59"), ("Albert", "1:53"),
    ("Hardcore Holly", "1:48"), ("K-Kwik", "1:54"), ("Val Venis", "1:54"), ("William Regal", "1:54"),
    ("Test", "1:55"), ("Big Show", "1:50"), ("Crash Holly", "2:00"), ("The Undertaker", "1:53"),
    ("Scotty 2 Hotty", "1:47"), ("Steve Austin", "1:46"), ("Billy Gunn", "1:36"), ("Haku", "1:48"),
    ("Rikishi", "2:01"),
]
buzzer_time = {}
cum = 0
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("51:42"), f"buzzer checksum failed: {cum}"

# Entrance times (buzzer sound -> stepping into the ring). Jeff Hardy and Bull
# Buchanan excluded (their contact preceded the official start of the match).
# Steve Austin's OFFICIAL figure (6:01) includes the entire Triple H beatdown
# in the aisle -- S047's own "adjusted" figure (0:17) is preserved in his notes.
entrance_lag = {
    "Steve Austin": "6:01", "Kane": "1:07", "Drew Carey": "0:56", "Honky Tonk Man": "0:40",
    "Rikishi": "0:35", "Perry Saturn": "0:32", "Scotty 2 Hotty": "0:30", "The Undertaker": "0:23",
    "The Rock": "0:16", "Big Show": "0:15", "Goodfather": "0:14", "Haku": "0:13", "Crash Holly": "0:12",
    "K-Kwik": "0:10", "Bradshaw": "0:09", "William Regal": "0:09", "Grand Master Sexay": "0:09",
    "Tazz": "0:09", "Hardcore Holly": "0:08", "Billy Gunn": "0:08", "Val Venis": "0:07",
    "Matt Hardy": "0:07", "Albert": "0:06", "Steve Blackman": "0:06", "Test": "0:06",
    "Raven": "0:05", "Faarooq": "0:05", "Al Snow": "0:01",
}

entry_actual = {"Jeff Hardy": 0, "Bull Buchanan": 0}
for name in buzzer_time:
    entry_actual[name] = buzzer_time[name] + mmss(entrance_lag[name])
assert entry_actual["Rikishi"] == mmss("52:17")
assert entry_actual["Steve Austin"] == mmss("52:18")
# Confirms S047's own claim: despite drawing #27, Austin's official ring-entry
# moment (52:18) is 1 second AFTER Rikishi's (52:17, the #30 entrant) -- Austin
# really was the last man to physically enter the ring. See F130.
assert entry_actual["Steve Austin"] > entry_actual["Rikishi"]

# Survival ("ring") times, as stated directly by S047.
survival = {
    "Kane": "53:44", "The Rock": "38:44", "Bradshaw": "17:39", "Albert": "15:54",
    "Hardcore Holly": "14:05", "The Undertaker": "10:47", "Val Venis": "10:22",
    "Steve Austin": "9:37", "Raven": "8:52", "K-Kwik": "7:54", "Billy Gunn": "7:23",
    "Al Snow": "7:09", "Jeff Hardy": "6:38", "Perry Saturn": "5:05", "Matt Hardy": "4:45",
    "Steve Blackman": "3:11", "Drew Carey": "2:53", "Haku": "2:52", "Rikishi": "2:35",
    "Crash Holly": "2:30", "Bull Buchanan": "2:09", "Test": "2:09", "William Regal": "2:01",
    "Big Show": "1:23", "Honky Tonk Man": "1:18", "Grand Master Sexay": "1:04", "Faarooq": "0:58",
    "Scotty 2 Hotty": "0:47", "Goodfather": "0:14", "Tazz": "0:10",
}

elim_ts = {}
for name, t in survival.items():
    if name == "Steve Austin":
        continue  # winner, never eliminated
    elim_ts[name] = entry_actual[name] + mmss(t)

assert elim_ts["Tazz"] == mmss("24:03")
assert elim_ts["William Regal"] == mmss("37:16")
assert elim_ts["Hardcore Holly"] == mmss("43:37") and entry_actual["Hardcore Holly"] == mmss("29:32")
FIVE_IN_TEN = {"Bradshaw", "Crash Holly", "Albert", "Hardcore Holly", "Val Venis"}
assert all(mmss("43:31") <= elim_ts[n] <= mmss("43:41") for n in FIVE_IN_TEN)
assert elim_ts["Kane"] == mmss("61:55")  # eliminated in the very last second, the winning elimination

still_active_at_austin_entry = {n for n, ts in elim_ts.items() if ts > entry_actual["Steve Austin"]} | {"Steve Austin"}
FINAL_SEVEN = {"Kane", "The Rock", "The Undertaker", "Billy Gunn", "Haku", "Rikishi", "Steve Austin"}
assert still_active_at_austin_entry == FINAL_SEVEN, still_active_at_austin_entry

elim_order_list = sorted(elim_ts, key=lambda n: elim_ts[n])
elim_number = {name: i + 1 for i, name in enumerate(elim_order_list)}
assert elim_number["Bull Buchanan"] == 1
assert elim_number["Kane"] == 29  # last eliminated, the winning elimination

ENTRY_NUMBERS = {"Jeff Hardy": 1, "Bull Buchanan": 2}
for i, (name, _) in enumerate(buzzer_gaps):
    ENTRY_NUMBERS[name] = i + 3
assert ENTRY_NUMBERS["Matt Hardy"] == 3 and ENTRY_NUMBERS["Drew Carey"] == 5
assert ENTRY_NUMBERS["Honky Tonk Man"] == 12 and ENTRY_NUMBERS["The Undertaker"] == 25
assert ENTRY_NUMBERS["Steve Austin"] == 27 and ENTRY_NUMBERS["Rikishi"] == 30

FINAL_FOUR = {"Steve Austin", "The Rock", "Kane", "Billy Gunn"}
FINAL_THREE = {"Steve Austin", "The Rock", "Kane"}
FINAL_TWO = {"Steve Austin", "Kane"}

# name -> (eliminator names, data_quality_status, elimination_method, is_shared)
KNOWN_ELIMINATORS = {
    "Bull Buchanan": (["Matt Hardy", "Jeff Hardy"], "CONFIRMED", "Eliminated together by Matt and Jeff Hardy, who then immediately began fighting each other.", True),
    "Matt Hardy": (["Jeff Hardy"], "CONFIRMED", "Mutual elimination -- Matt and Jeff Hardy eliminated each other while brawling.", False),
    "Jeff Hardy": (["Matt Hardy"], "CONFIRMED", "Mutual elimination -- Matt and Jeff Hardy eliminated each other while brawling.", False),
    "Drew Carey": (["Drew Carey"], "CONFIRMED", "Self-elimination -- after failing to bribe Kane with cash, Carey 'smartly eliminated himself by jumping over the top rope.'", False),
    "Honky Tonk Man": (["Kane"], "CONFIRMED", "Turned around after his entrance shtick to get bashed in the head with his own guitar, then tossed by Kane -- one of Kane's record-setting 11 eliminations.", False),
    "Al Snow": (["Kane"], "CONFIRMED", "One of Kane's record-setting 11 eliminations.", False),
    "Steve Blackman": (["Kane"], "CONFIRMED", "One of Kane's record-setting 11 eliminations.", False),
    "Perry Saturn": (["Kane"], "CONFIRMED", "One of Kane's record-setting 11 eliminations.", False),
    "Big Show": (["The Rock"], "CONFIRMED", "Tossed by Rock shortly after returning from a months-long absence; Show then retaliated by dragging Rock out and chokeslamming him through a ringside table.", False),
    "The Undertaker": (["Rikishi"], "CONFIRMED", "Eliminated by the #30 entrant, Rikishi.", False),
    "Rikishi": (["The Rock"], "CONFIRMED", "Taken out by Rock, setting the Final Four of Austin, Rock, Kane, and Billy Gunn.", False),
    "Billy Gunn": (["Steve Austin"], "CONFIRMED", "Dumped by Austin in the Final Four.", False),
    "The Rock": (["Kane"], "CONFIRMED", "Kane snuck in and tossed both Austin and Rock, but only Rock actually went out.", False),
    "Kane": (["Steve Austin"], "CONFIRMED", "The winning elimination -- Austin bashed Kane with a steel chair four times, the last shot sending him over the top rope.", False),
}

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Jeff Hardy", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "One of the match's first two entrants (#1); eliminated Matt Hardy (mutual) after the two eliminated Bull Buchanan together.", "S047;S048"),
    ("Bull Buchanan", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "One of the match's first two entrants (#2); eliminated by the Hardys together, the match's first elimination.", "S047;S048"),
    ("Matt Hardy", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #3 per S048. Eliminated Bull Buchanan (with Jeff Hardy), then mutually eliminated Jeff Hardy.", "S047;S048"),
    ("Drew Carey", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Celebrity entrant, entering #5 per S048 to promote a PPV special. Tried to bribe Kane, then self-eliminated by jumping over the top rope.", "S047;S048"),
    ("Raven", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S047;S048"),
    ("Perry Saturn", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "One of Kane's record-setting 11 eliminations.", "S047;S048"),
    ("William Regal", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S047"),
    ("Tazz", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Not an existing wrestler_id despite a mention in this database's 2000 build (undercard-only that year, not a Rumble entrant) -- created fresh here as his first actual Rumble appearance.", "S047;S048"),
    ("K-Kwik", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S047;S048"),
    ("Scotty 2 Hotty", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Possible identity connection to this database's existing 'scott-taylor' wrestler_id (2000) -- not stated directly by either source this pass, left unmerged. See F132.", "S047;S048"),
]

reused = {
    "Faarooq": "faarooq", "Kane": "kane", "Al Snow": "al-snow", "Steve Blackman": "steve-blackman",
    "Grand Master Sexay": "brian-christopher", "Honky Tonk Man": "the-honky-tonk-man",
    "The Rock": "rocky-maivia", "Goodfather": "the-godfather", "Bradshaw": "bradshaw",
    "Albert": "prince-albert", "Hardcore Holly": "hardcore-holly", "Val Venis": "val-venis",
    "Test": "test", "Big Show": "big-show", "Crash Holly": "crash-holly",
    "The Undertaker": "the-undertaker", "Steve Austin": "steve-austin", "Billy Gunn": "billy-gunn",
    "Rikishi": "rikishi", "Haku": "haku",
    # Non-entrant reused ids used only in other_matches this year.
    "Hunter Hearst Helmsley": "hunter-hearst-helmsley", "Chris Jericho": "chris-jericho",
    "Edge": "edge", "Christian": "christian", "Chyna": "chyna",
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
    "Jeff Hardy", "Bull Buchanan", "Matt Hardy", "Faarooq", "Drew Carey", "Kane", "Raven",
    "Al Snow", "Perry Saturn", "Steve Blackman", "Grand Master Sexay", "Honky Tonk Man",
    "The Rock", "Goodfather", "Tazz", "Bradshaw", "Albert", "Hardcore Holly", "K-Kwik",
    "Val Venis", "William Regal", "Test", "Big Show", "Crash Holly", "The Undertaker",
    "Scotty 2 Hotty", "Steve Austin", "Billy Gunn", "Haku", "Rikishi",
]
assert len(all_names) == 30

WRESTLED_EARLIER = {"Chris Jericho", "Edge", "Christian", "Chyna", "Hunter Hearst Helmsley"}  # not Rumble entrants this year -- see other_matches

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Steve Austin")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, dq, method, is_shared = KNOWN_ELIMINATORS.get(name, ([], "", "", False))

    notes_parts = []
    if name == "Steve Austin":
        notes_parts.append(
            "Drew #27 but was attacked in the aisle by Triple H before he could enter the ring -- his OFFICIAL "
            "entrance time (6:01) includes that entire beatdown; adjusted for it, his entrance actually lasted "
            "only 0:17. Per S047's own timing data, Austin's official ring-entry moment lands 1 second AFTER "
            "Rikishi's (the #30 entrant) -- he really was the last man to physically enter the ring despite "
            "holding the #27 draw. entry_number is kept at 27 (his drawn number) rather than 30 -- see F130."
        )
    elif name == "Rikishi":
        notes_parts.append("Officially the #30 (final-numbered) entrant, though Steve Austin's actual physical ring entry came 1 second after his -- see F130.")
    elif name == "Kane":
        notes_parts.append("Set the (then) record for most eliminations in a single Royal Rumble match with 11 total; only 5 are individually named in either source -- see F131.")
    elif name == "Scotty 2 Hotty":
        notes_parts.append("See F132 -- possible but unverified identity connection to this database's 2000 wrestler_id scott-taylor.")
    elif name in WRESTLED_EARLIER:
        notes_parts.append("Also wrestled earlier on the same card -- see other_matches.csv.")
    note = " ".join(notes_parts)

    for eliminator in elim_by:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": elim_number[name],
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
            "assisting_wrestler_ids": "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": ENTRY_NUMBERS.get(eliminator, ""),
            "elimination_clock_time": secs_to_mmss(elim_ts[name]),
            "elimination_clock_seconds": elim_ts[name],
            "elimination_type": "self_elimination" if name == "Drew Carey" else "over_top_rope",
            "elimination_method": method,
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "FALSE" if is_shared else "TRUE", "is_shared": "TRUE" if is_shared else "FALSE",
            "is_accidental": "FALSE",
            "is_self_elimination": "TRUE" if name == "Drew Carey" else "FALSE",
            "is_storyline_related": "TRUE" if name == "Drew Carey" else "UNKNOWN",
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE",
            "simultaneous_group_id": "bull_buchanan_hardys" if name == "Bull Buchanan" else "",
            "data_quality_status": dq,
            "source_ids": "S047;S048",
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
        "is_returning_wrestler": "TRUE" if name == "Big Show" else "",
        "absence_length": "several months" if name == "Big Show" else "",
        "age_at_event": "", "age_status": "UNKNOWN",
        "billed_height_m_at_event": "", "billed_weight_kg_at_event": "", "billed_from_at_event": "",
        "physical_status": "UNKNOWN",
        "alignment": "", "alignment_status": "UNKNOWN",
        "gimmick_at_event": "The One Billy Gunn" if name == "Billy Gunn" else "",
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
        "wrestlers_eliminated_count": 11 if name == "Kane" else "",
        "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "TRUE" if name == "Drew Carey" else "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if name == "Kane" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "TRUE" if name == "Honky Tonk Man" else "FALSE",
        "legend_returning": "FALSE",
        "celebrity_entrant": "TRUE" if name == "Drew Carey" else "FALSE",
        "non_full_time_wrestler": "TRUE" if name == "Drew Carey" else "FALSE",
        "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S047;S048",
        "notes": note,
    }
    entrant_rows.append(er)

# Fill in each eliminator's wrestlers_eliminated_ids / counts from elim_rows
# (Kane's separately-stated aggregate count of 11 total is kept as-is even
# though only 5 individual elim_rows credit him -- see F131).
elim_credit = {}
for row in elim_rows:
    elim_credit.setdefault(row["eliminator_wrestler_id"], []).append(row["eliminated_wrestler_id"])
for er in entrant_rows:
    credited = elim_credit.get(er["wrestler_id"], [])
    if credited:
        if er["wrestler_id"] != "kane":
            er["wrestlers_eliminated_count"] = len(credited)
        er["wrestlers_eliminated_ids"] = ";".join(credited)
        er["solo_eliminations_count"] = len([c for c in credited]) if er["wrestler_id"] != "matt-hardy" and er["wrestler_id"] != "jeff-hardy" else ""
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
# wrestler_id in this database; opponents without one are still recorded
# as free text in the 'opponents' field).
# ---------------------------------------------------------------------------
other_matches = [
    ("Chris Jericho", 2, "Chris Benoit", "", "Singles (Ladder Match)", "TRUE", "Intercontinental Championship", "FALSE", "Win", "TRUE", "", "18:43", "2nd match", "S048", "Defeated Chris Benoit in a Ladder Match to win the I-C Title -- widely regarded as one of the best matches of 2001. Not a Rumble entrant this year."),
    ("Edge", 1, "The Dudley Boys (Bubba Ray and D-Von)", "Christian", "Tag Team", "TRUE", "World Tag Team Championship", "TRUE", "Loss", "", "TRUE", "9:58", "Opener", "S048", "Edge and Christian lost the tag titles when D-Von pinned Edge. Not a Rumble entrant this year."),
    ("Christian", 1, "The Dudley Boys (Bubba Ray and D-Von)", "Edge", "Tag Team", "TRUE", "World Tag Team Championship", "TRUE", "Loss", "", "TRUE", "9:58", "Opener", "S048", "Edge and Christian lost the tag titles when D-Von pinned Edge. Not a Rumble entrant this year."),
    ("Chyna", 3, "Ivory", "", "Singles", "TRUE", "Women's Championship", "FALSE", "Loss", "", "TRUE", "3:27", "3rd match", "S048", "Pinned by Ivory. Not a Rumble entrant this year."),
    ("Hunter Hearst Helmsley", 4, "Kurt Angle", "", "Singles", "TRUE", "World Heavyweight Championship", "FALSE", "Loss", "", "TRUE", "24:18", "4th match", "S048", "Pinned by Kurt Angle, who retained the title. Not a Rumble entrant this year."),
]
with open(os.path.join(DATA_DIR, "other_matches.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for (name, mnum, opponents, partners, mtype, is_title, title, was_champ, result, won_t, lost_t, duration, position, row_src, notes) in other_matches:
        pid = wrestler_ids[name]
        writer.writerow([EVENT_ID, pid, mnum, opponents, partners, mtype, is_title, title, was_champ,
                          result, won_t, lost_t, duration, position, "", "PROBABLE", row_src, notes])

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F130", EVENT_ID, "entrants", "steve-austin;rikishi", "entry_number", "needs_human_judgement",
     "Steve Austin's unique delayed entry. He drew #27, but was attacked in the aisle by Triple H (payback "
     "for costing HHH his title match earlier that night) before he could physically enter the ring. Per "
     "S047's own timing data, Austin's official ring-entry moment lands exactly 1 second AFTER Rikishi's (the "
     "officially-numbered #30 entrant) -- confirming S047's explicit claim that Austin, despite drawing #27, "
     "was actually the LAST man to physically enter the ring, after throwing an already-attacked Rikishi into "
     "the ring ahead of him. entry_number is kept at 27 (his drawn/announced number, this database's standard "
     "convention) rather than reassigned to reflect actual physical order; events.csv's final_entrant_id is "
     "kept as rikishi for the same reason. S048's narrative gives Austin's drawn number as '#26' instead of "
     "S047's explicit '#27' -- a minor discrepancy resolved in favor of S047's more rigorous, purpose-built "
     "timing analysis.",
     "S047;S048", "open", "2026-09-16"),
    ("F131", EVENT_ID, "eliminations", "kane;big-show;the-undertaker", "eliminator_wrestler_id", "unverified",
     "Kane is credited with a (then) record-setting 11 total eliminations this match, but only 5 are "
     "individually named in either source (Honky Tonk Man, Al Snow, Steve Blackman, Perry Saturn, and The "
     "Rock) -- his entrant row's wrestlers_eliminated_count is kept at the CONFIRMED aggregate of 11 even "
     "though only 5 elimination rows exist. Big Show is separately credited with tossing out 'a couple people' "
     "(unnamed) before being eliminated himself, and S048 also states Undertaker and Kane 'combined to throw "
     "a bunch of guys out' (also unnamed) after Undertaker's #25 entrance. None of these unnamed eliminations "
     "were assigned to specific wrestler_ids rather than guessing.",
     "S047;S048", "open", "2026-09-16"),
    ("F132", EVENT_ID, "wrestlers", "scotty-2-hotty", "wrestler_id", "needs_human_judgement",
     "'Scotty 2 Hotty' (entrant #26) is widely known in general wrestling history to be the same performer "
     "(Scott Anthony Garland) who wrestled as 'Scott Taylor' in this database's 2000 build (wrestler_id "
     "scott-taylor). Neither source consulted this pass states that connection directly. Left as a separate, "
     "new wrestler_id pending a future fact-check pass with 2 independent sources -- same caution class as "
     "X-Pac/1-2-3 Kid (1999's F118) and Viscera/Mabel (2000's F127). By contrast, 'Grand Master Sexay' "
     "(entrant #11) reuses the existing brian-christopher id directly -- same ring name/gimmick both years, "
     "not a merge question.",
     "S047;S048", "open", "2026-09-16"),
    ("F133", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 10 previously-unseen wrestlers this pass (Jeff Hardy, Bull Buchanan, Matt Hardy, Drew "
     "Carey, Raven, Perry Saturn, William Regal, Tazz, K-Kwik, Scotty 2 Hotty) with zero bio data in this "
     "pass's source -- names only. Left entirely UNKNOWN, same pattern as every prior year's equivalent flag.",
     "S047;S048", "open", "2026-09-16"),
    ("F134", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-16"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2001", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2001-01-21", "venue": "New Orleans Arena",
    "city_region": "New Orleans, Louisiana", "country": "United States",
    "attendance_official": "", "attendance_reported": 17137,
    "entry_interval_seconds": 120, "entrant_count": 30, "duration_total": "61:55",
    "duration_status": "CONFIRMED",
    "winner_id": "steve-austin", "runner_up_id": "kane",
    "final_two_ids": "steve-austin;kane",
    "final_three_ids": "steve-austin;the-rock;kane",
    "final_four_ids": "steve-austin;the-rock;kane;billy-gunn",
    "first_entrant_id": "jeff-hardy", "second_entrant_id": "bull-buchanan", "final_entrant_id": "rikishi",
    "first_elimination_id": "bull-buchanan", "last_elimination_before_winner_id": "kane",
    "eliminations_count": 29, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": 1,
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Jim Ross, Jerry Lawler", "ring_announcer": "Howard Finkel",
    "referees": "Not identified in either source consulted this pass",
    "special_rules": (
        "Steve Austin drew #27 but was attacked in the aisle by Triple H before he could enter the ring, "
        "recovering just in time for #30 entrant Rikishi's entrance -- Austin threw the already-attacked "
        "Rikishi into the ring, then finally entered himself, making him (per S047's own timing analysis) the "
        "actual last man to physically enter the ring despite not holding the #30 draw -- see F130. Kane set "
        "a (then) record for most eliminations in a single Royal Rumble match, with 11 total."
    ),
    "title_on_the_line": "FALSE",
    "championship_implications": "None in the Rumble match itself, though Chris Jericho won the WWF Intercontinental Championship from Chris Benoit in a Ladder Match, The Dudley Boyz won the World Tag Team Championship from Edge and Christian, Ivory retained the Women's Championship against Chyna, and Kurt Angle retained the World Heavyweight Championship against Triple H, all earlier on the same card.",
    "winners_reward": "A WWF Championship match against The Rock at WrestleMania X-Seven, which Austin won (with help from a returning heel Vince McMahon), going on to his controversial heel turn shortly after, per S048",
    "historical_significance": (
        "Steve Austin's record-tying 3rd Royal Rumble win, achieved despite a unique delayed entry after being "
        "attacked by Triple H -- he was the first man to win the Royal Rumble after being the actual last man "
        "to physically enter the ring (a feat later publicly associated with The Undertaker's #30 entry win in "
        "2007, though that was the officially-numbered final slot rather than the physically-last entry) -- see "
        "F130. Kane's 11 eliminations set a new single-match record. Drew Carey's celebrity cameo appearance "
        "and self-elimination is one of the more memorable comedic moments in Rumble history. The I-C Title "
        "Ladder Match between Chris Jericho and Chris Benoit on the undercard is separately regarded as one of "
        "the best matches of 2001, per S048."
    ),
    "notes": (
        "The 2nd richest entry/survival-timing dataset in this database (after 1999) -- all 30 entrants timed "
        "to the second, with NO camera-cut issues this year. Eliminator credit is unusually rich for a "
        "Cageside-style year (13 credited elimination events), though Kane's stated 11-total is only 5 "
        "individually named -- see F131. Steve Austin's delayed/out-of-order physical entry is a unique "
        "structural case in this database -- see F130."
    ),
    "data_quality_status": "CONFIRMED", "source_ids": "S047;S048",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2001 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
