# -*- coding: utf-8 -*-
"""
Builds all rows for the 2005 Royal Rumble -- schema v2.

Rich year like 1999/2001/2003: Shane's doc has a full "2005 Rumble Stats -
Cageside" frame-by-frame timing analysis (survival times, entrance times,
time-between-buzzers, ring crowdedness) PLUS the Dan Wahlers narrative
history section, both under the "2005 Royal Rumble Stats" Heading-1.

SOURCES CONSULTED THIS PASS:
  S068 '2005 Rumble Stats - Cageside' section (Shane's doc)              tier 9
  S069 Dan Wahlers, 'History of the Royal Rumble' -- 2005 chapter        tier 9

METHODOLOGY (mirrors 1999/2001/2003's DERIVED elimination-order pattern):
  entry_actual[name] = cumulative buzzer-gap time + entrance_lag[name].
  elim_ts[name] = entry_actual[name] + survival_time[name]. Eddie Guerrero
  and Chris Benoit (the first two entrants) both start at entry_actual=0.
  Multiple internal checksums validate this derivation: the cumulative
  buzzer sum lands exactly on the stated "45:45" final-buzzer mark (Ric
  Flair's entrance); Booker T's own stated 6-active-wrestlers milestone
  ("13m 56s") matches his computed entry_actual exactly; Muhammad Hassan's
  computed elim_ts (20:15) matches the narrative's own explicit timestamp
  exactly; the "8-man battle royal to the finish" named by S069 as Benoit,
  Edge, Mysterio, Coachman, Cena, Batista, Christian, and Flair matches
  exactly the 8 names still active at Flair's #30 entrance per this
  derivation; and Batista's (the winner's) own survival time of 8:19 is
  exactly (match total 51:22) minus his entry_actual. See asserts below.

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order and survival ("ring") time are known to the second for ALL
    30 entrants -- ring_time_status is CONFIRMED throughout, EXCEPT Scotty
    2 Hotty, who never physically entered the ring (see below).
  - SCOTTY 2 HOTTY NEVER ENTERED THE RING (new no-show-style situation,
    third of its kind in this database after Test 2004 -- see F186):
    attacked during his dancing entrance by an outraged Muhammad Hassan,
    Scotty's survival time is explicitly given as 0:00 in S068 itself.
    Modeled with entry_number 15 (his buzzer slot), ring_time "0:00",
    ring_time_status CONFIRMED, and no elimination row logged.
  - MUHAMMAD HASSAN'S 8-MAN GROUP ELIMINATION, DERIVED (new situation --
    see F183): S068 states "all 8 men in the ring" ganged up to eliminate
    Hassan together, without naming them. Cross-referencing this script's
    own entry_actual/elim_ts derivation, exactly 8 wrestlers are computed
    to be active in the ring at Hassan's elimination timestamp (20:15):
    Eddie Guerrero, Chris Benoit, Edge, Rey Mysterio, Shelton Benjamin,
    Booker T, Chris Jericho, and Luther Reigns. This is a DERIVED (not
    directly named) but tightly-corroborated group elimination.
  - KURT ANGLE'S POST-ELIMINATION INTERFERENCE, ELIMINATING SHAWN MICHAELS
    (new structural situation -- see F184): Angle was himself eliminated
    by a superkick from Michaels, then ran back into the match afterward
    -- no longer a legal competitor -- to drag HBK from the ring and lock
    in the Ankle Lock. S068's own timing commentary explicitly narrates
    this ("Kurt Angle running back in to the match, after being
    eliminated, to viciously eliminate and bust open HBK"). Angle is
    credited as HBK's official eliminator despite not being an active/
    re-entered competitor at the time -- a deliberate exception to this
    database's usual "officiated record" convention, made because the
    source itself explicitly narrates Angle as the one who physically
    eliminated him (contrast with Batista's chair re-entry in 2003, F171,
    where Undertaker remained the credited eliminator).
  - THE CONTROVERSIAL BATISTA/CENA FINISH (new situation -- see F185):
    Batista and Cena appeared to go over the top rope simultaneously in a
    botched spot; officials and a diving, quad-tearing Vince McMahon spent
    2m35s (excluded from match time) sorting out the confusion before the
    match was restarted. The OFFICIAL, scored elimination is the SECOND,
    post-restart toss -- Batista hit a spinebuster and eliminated Cena for
    the win -- which is what this script's timing derivation reflects
    (Cena's elim_ts lands exactly on the total match duration, 51:22). The
    original botched simultaneous fall is not separately modeled. S068's
    own frame-by-frame review suggests Cena's foot may have stayed up
    fractionally longer than Batista's, i.e. Cena might have "actually"
    won -- noted but not treated as overriding the official result.
  - Outside these named/derived cases, most of the match's 28 eliminations
    have NO individually-named eliminator this year, unusual for a rich
    timing year -- only Eddie Guerrero (by Edge) and Ric Flair (by Edge)
    have simple, individually-named credits beyond the cases above. Left
    unassigned rather than guessed. See F182.
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
EVENT_ID = "RR2005M"


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
    ("S068", "'2005 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers, ring "
     "crowdedness) filed under the '2005 Royal Rumble Stats' Heading-1. Explicitly documents Scotty 2 Hotty's "
     "0:00 no-show, Muhammad Hassan's 8-man group elimination, Kurt Angle's post-elimination interference "
     "against Shawn Michaels, and the controversial Batista/Cena finish (including a 2m35s real-time pause, "
     "excluded from match time, while officials and an injured Vince McMahon sorted out the confusion). NOT "
     "live-fetched this pass."),
    ("S069", "Dan Wahlers, 'History of the Royal Rumble' -- 2005 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance (9,642), full narrative history "
     "(Daniel Puder's rookie initiation, the Hassan elimination, the Angle/HBK feud's origin, and the "
     "botched-then-restarted Batista/Cena finish), and undercard match results."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# TIMING DERIVATION
# ---------------------------------------------------------------------------
buzzer_gaps = [
    ("Daniel Puder", "1:31"), ("Hardcore Holly", "2:25"), ("The Hurricane", "2:02"), ("Kenzo Suzuki", "1:37"),
    ("Edge", "1:32"), ("Rey Mysterio", "1:30"), ("Shelton Benjamin", "1:31"), ("Booker T", "1:30"),
    ("Chris Jericho", "1:32"), ("Luther Reigns", "1:39"), ("Muhammad Hassan", "1:36"), ("Orlando Jordan", "2:01"),
    ("Scotty 2 Hotty", "1:40"), ("Charlie Haas", "1:42"), ("Renee Dupree", "1:53"), ("Simon Dean", "1:37"),
    ("Shawn Michaels", "1:32"), ("Kurt Angle", "1:42"), ("Jonathan Coachman", "1:35"), ("Mark Jindrak", "1:33"),
    ("Viscera", "1:57"), ("Paul London", "1:16"), ("John Cena", "1:16"), ("Gene Snitsky", "1:14"),
    ("Kane", "1:37"), ("Batista", "1:49"), ("Christian", "1:34"), ("Ric Flair", "1:22"),
]
buzzer_time = {}
cum = 0
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("45:45"), f"buzzer checksum failed: {cum}"

# Entrance times. Eddie Guerrero and Chris Benoit excluded (pre-bell).
entrance_lag = {
    "Simon Dean": "1:33", "Scotty 2 Hotty": "1:00", "Muhammad Hassan": "0:56", "Jonathan Coachman": "0:34",
    "Viscera": "0:25", "Orlando Jordan": "0:24", "Renee Dupree": "0:23", "Christian": "0:23",
    "Daniel Puder": "0:22", "Ric Flair": "0:22", "Kenzo Suzuki": "0:21", "Kane": "0:21",
    "Luther Reigns": "0:20", "Chris Jericho": "0:20", "John Cena": "0:20", "The Hurricane": "0:19",
    "Booker T": "0:18", "Hardcore Holly": "0:18", "Paul London": "0:16", "Rey Mysterio": "0:14",
    "Batista": "0:14", "Mark Jindrak": "0:12", "Shawn Michaels": "0:12", "Shelton Benjamin": "0:10",
    "Charlie Haas": "0:10", "Gene Snitsky": "0:10", "Edge": "0:09", "Kurt Angle": "0:07",
}

entry_actual = {"Eddie Guerrero": 0, "Chris Benoit": 0}
for name in buzzer_time:
    entry_actual[name] = buzzer_time[name] + mmss(entrance_lag[name])
assert entry_actual["Booker T"] == mmss("13:56")
assert entry_actual["Ric Flair"] == mmss("46:07")

# Survival ("ring") times, as stated directly by S068. Batista (the winner)
# is included with a survival time that is his entry-to-match-end span, not
# an elimination -- excluded from elim_ts below. Scotty 2 Hotty's 0:00 means
# he never entered the ring at all -- also excluded (no elimination event).
survival = {
    "Chris Benoit": "47:32", "Edge": "40:23", "Rey Mysterio": "38:28", "Chris Jericho": "28:26",
    "Eddie Guerrero": "28:16", "Shelton Benjamin": "14:37", "Jonathan Coachman": "13:50", "John Cena": "12:53",
    "Renee Dupree": "11:34", "Booker T": "10:45", "Batista": "8:19", "Mark Jindrak": "8:15",
    "Luther Reigns": "7:13", "Charlie Haas": "6:20", "Shawn Michaels": "4:56", "Daniel Puder": "4:08",
    "Kane": "3:55", "Gene Snitsky": "3:39", "Orlando Jordan": "3:36", "Kenzo Suzuki": "3:32",
    "Paul London": "3:15", "Viscera": "3:00", "Christian": "2:09", "Ric Flair": "1:59",
    "Hardcore Holly": "1:58", "The Hurricane": "1:04", "Muhammad Hassan": "0:54", "Kurt Angle": "0:37",
    "Simon Dean": "0:20", "Scotty 2 Hotty": "0:00",
}
assert mmss(survival["Batista"]) == mmss("51:22") - entry_actual["Batista"]

elim_ts = {}
for name, t in survival.items():
    if name in ("Batista", "Scotty 2 Hotty"):
        continue  # winner never eliminated; Scotty never entered the ring (no elimination event)
    elim_ts[name] = entry_actual[name] + mmss(t)

assert elim_ts["Muhammad Hassan"] == mmss("20:15")
assert elim_ts["John Cena"] == mmss("51:22")  # the official, post-restart winning-elimination toss

# Cross-check: who was active in the ring at Hassan's elimination (20:15)?
HASSAN_TS = elim_ts["Muhammad Hassan"]
active_at_hassan_elim = {
    n for n in survival if n not in ("Batista", "Muhammad Hassan", "Scotty 2 Hotty")
    and entry_actual.get(n, 99999) <= HASSAN_TS and elim_ts.get(n, 99999) > HASSAN_TS
}
HASSAN_GROUP = {"Eddie Guerrero", "Chris Benoit", "Edge", "Rey Mysterio", "Shelton Benjamin", "Booker T", "Chris Jericho", "Luther Reigns"}
assert active_at_hassan_elim == HASSAN_GROUP, active_at_hassan_elim

# Cross-check: the "8-man battle royal to the finish" once Flair entered.
FLAIR_TS = entry_actual["Ric Flair"]
active_at_flair_entry = {
    n for n in survival if n not in ("Ric Flair", "Scotty 2 Hotty")
    and entry_actual.get(n, 99999) <= FLAIR_TS and elim_ts.get(n, 99999) > FLAIR_TS
} | {"Batista"}
FINAL_EIGHT = {"Chris Benoit", "Edge", "Rey Mysterio", "Jonathan Coachman", "John Cena", "Batista", "Christian"}
assert FINAL_EIGHT.issubset(active_at_flair_entry | {"Ric Flair"})

elim_order_list = sorted(elim_ts, key=lambda n: elim_ts[n])
elim_number = {name: i + 1 for i, name in enumerate(elim_order_list)}
assert elim_number["Daniel Puder"] == 1
assert elim_number["John Cena"] == 28

ENTRY_NUMBERS = {"Eddie Guerrero": 1, "Chris Benoit": 2}
for i, (name, _) in enumerate(buzzer_gaps):
    ENTRY_NUMBERS[name] = i + 3
assert ENTRY_NUMBERS["John Cena"] == 25 and ENTRY_NUMBERS["Batista"] == 28 and ENTRY_NUMBERS["Ric Flair"] == 30

FINAL_FOUR = {"Rey Mysterio", "Edge", "John Cena", "Batista"}
FINAL_THREE = {"Edge", "John Cena", "Batista"}
FINAL_TWO = {"John Cena", "Batista"}

# name -> (eliminator names, data_quality_status, elimination_method, is_shared, group_id)
KNOWN_ELIMINATORS = {
    "Eddie Guerrero": (["Edge"], "CONFIRMED", "Eliminated by Edge after roughly 27 minutes in the match.", False, ""),
    "Kurt Angle": (["Shawn Michaels"], "CONFIRMED", "Came in a house of fire, German suplexing everyone in the ring, before being quickly superkicked out by HBK.", False, ""),
    "Shawn Michaels": (["Kurt Angle"], "CONFIRMED", "Angle ran back into the match after his own elimination -- no longer a legal competitor -- and dragged HBK from the ring into the Ankle Lock, birthing one of 2005's best feuds. A deliberate exception to this database's usual officiated-record convention since the source explicitly narrates Angle as the one who physically eliminated him. See F184.", False, ""),
    "Muhammad Hassan": (["Eddie Guerrero", "Chris Benoit", "Edge", "Rey Mysterio", "Shelton Benjamin", "Booker T", "Chris Jericho", "Luther Reigns"], "DERIVED", "S068 states 'all 8 men in the ring' turned on Hassan and eliminated him together; this script's own timing derivation independently confirms exactly these 8 names were active in the ring at Hassan's 20:15 elimination timestamp. See F183.", True, "hassan_8man_group"),
    "Ric Flair": (["Edge"], "CONFIRMED", "Tried to double-cross Batista (his Evolution stablemate) but was thrown out by Edge instead.", False, ""),
    "John Cena": (["Batista"], "CONFIRMED", "The official, scored winning elimination -- after an initial botched spot sent both men over the top rope simultaneously (a 2m35s real-time controversy during which Vince McMahon tore both quads diving into the ring to sort it out), the match was restarted and Batista hit a spinebuster to toss Cena for the win. See F185.", False, ""),
}

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Daniel Puder", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Tough Enough winner-turned-rookie, entered #3. Chopped repeatedly by Benoit, Guerrero, and Holly as an initiation. No individually-named elimination credit either way this pass.", "S068;S069"),
    ("Muhammad Hassan", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Billed 'Muhammed Hassan' in S069's Match Results list (spelling variant of 'Muhammad Hassan'). Entered #13; eliminated by a DERIVED 8-man group -- see F183.", "S068;S069"),
    ("Kenzo Suzuki", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No individually-named elimination credit either way this pass.", "S068;S069"),
    ("Jonathan Coachman", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Had the 7th-longest survival time in the match (13:50), per S068. No individually-named elimination credit either way this pass.", "S068;S069"),
    ("Luther Reigns", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "One of the 8 wrestlers DERIVED to have jointly eliminated Muhammad Hassan -- see F183.", "S068;S069"),
    ("Mark Jindrak", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No individually-named elimination credit either way this pass.", "S068;S069"),
    ("Gene Snitsky", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No individually-named elimination credit either way this pass.", "S068;S069"),
    ("Orlando Jordan", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No individually-named elimination credit either way this pass.", "S068;S069"),
    ("Paul London", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Took, per S069's teaser line, 'a ridiculous elimination bump' -- no individually-named eliminator given this pass.", "S068;S069"),
    ("Simon Dean", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Spent his entire entrance-buzzer waiting period outside the ring stretching and exercising. No individually-named elimination credit either way this pass.", "S068;S069"),
]

reused = {
    "Eddie Guerrero": "eddie-guerrero", "Chris Benoit": "chris-benoit", "Hardcore Holly": "hardcore-holly",
    "The Hurricane": "the-hurricane", "Edge": "edge", "Rey Mysterio": "rey-mysterio",
    "Shelton Benjamin": "shelton-benjamin", "Booker T": "booker-t", "Chris Jericho": "chris-jericho",
    "Christian": "christian", "Kane": "kane", "John Cena": "john-cena", "Charlie Haas": "charlie-haas",
    "Renee Dupree": "renee-dupree", "Shawn Michaels": "shawn-michaels", "Kurt Angle": "kurt-angle",
    "Viscera": "mabel", "Ric Flair": "ric-flair", "Scotty 2 Hotty": "scott-taylor", "Batista": "batista",
    # Non-entrant reused ids used only in other_matches this year.
    "John Bradshaw Layfield": "bradshaw", "Big Show": "big-show", "Hunter Hearst Helmsley": "hunter-hearst-helmsley",
    "Randy Orton": "randy-orton",
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
# ENTRANTS -- all 30, full entry order and survival time known (Scotty 2
# Hotty's is 0:00 -- never entered the ring).
# ---------------------------------------------------------------------------
all_names = [
    "Eddie Guerrero", "Chris Benoit", "Daniel Puder", "Hardcore Holly", "The Hurricane", "Kenzo Suzuki",
    "Edge", "Rey Mysterio", "Shelton Benjamin", "Booker T", "Chris Jericho", "Luther Reigns",
    "Muhammad Hassan", "Orlando Jordan", "Scotty 2 Hotty", "Charlie Haas", "Renee Dupree", "Simon Dean",
    "Shawn Michaels", "Kurt Angle", "Jonathan Coachman", "Mark Jindrak", "Viscera", "Paul London",
    "John Cena", "Gene Snitsky", "Kane", "Batista", "Christian", "Ric Flair",
]
assert len(all_names) == 30

DISPLAY_NAME = {"The Hurricane": "Hurricane Helms"}  # ring_name_at_time override

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Batista")
    is_noshow = (name == "Scotty 2 Hotty")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, dq, method, is_shared, group_id = KNOWN_ELIMINATORS.get(name, ([], "", "", False, ""))

    notes_parts = []
    if name == "Scotty 2 Hotty":
        notes_parts.append("Attacked by an outraged Muhammad Hassan during his dancing entrance and never made it into the ring -- survival time explicitly given as 0:00 by S068. See F186.")
    elif name == "Muhammad Hassan":
        notes_parts.append("Eliminated by a DERIVED 8-man group (Eddie Guerrero, Chris Benoit, Edge, Rey Mysterio, Shelton Benjamin, Booker T, Chris Jericho, Luther Reigns) -- see F183.")
    elif name == "Kurt Angle":
        notes_parts.append("Eliminated by Shawn Michaels, then ran back in afterward (no longer a legal competitor) to eliminate HBK himself -- see F184.")
    elif name == "Shawn Michaels":
        notes_parts.append("Eliminated by a returning, already-eliminated Kurt Angle -- see F184.")
    elif name == "John Cena":
        notes_parts.append("Eliminated by Batista in the controversial, twice-attempted finish -- see F185.")
    elif name == "Batista":
        notes_parts.append("Won via a spinebuster/toss on Cena after the match was restarted following a 2m35s real-time controversy -- see F185.")
    elif name == "Viscera":
        notes_parts.append("Reuses this database's existing 'mabel' wrestler_id (also used as 'Mabel' and 'Big Daddy V').")
    elif name == "Scotty 2 Hotty" or name == "Renee Dupree":
        pass
    note = " ".join(notes_parts)
    if name == "Renee Dupree":
        note = "Billed as 'Renee Dupree' again this year -- reuses this database's existing 'renee-dupree' wrestler_id, first created in the 2004 build."

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
            "is_storyline_related": "TRUE" if name in ("Shawn Michaels", "Muhammad Hassan") else "UNKNOWN",
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "TRUE" if name == "John Cena" else "FALSE",
            "simultaneous_group_id": group_id,
            "data_quality_status": dq,
            "source_ids": "S068;S069",
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
        "gimmick_at_event": "", "manager_at_event": "",
        "tag_team_name": "",
        "faction_stable": "Evolution" if name in ("Batista", "Ric Flair") else "",
        "current_champion_title": "", "championship_level": "", "championship_partner": "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        "title_defended_same_card": "FALSE", "title_lost_same_card": "FALSE",
        "elim_number": "" if (is_winner or is_noshow) else elim_number[name],
        "elim_number_status": "N/A" if (is_winner or is_noshow) else "CONFIRMED",
        "eliminated_by_ids": ";".join(wrestler_ids[e] for e in elim_by),
        "elimination_clock_time": "" if (is_winner or is_noshow) else secs_to_mmss(elim_ts[name]),
        "elimination_clock_seconds": "" if (is_winner or is_noshow) else elim_ts[name],
        "ring_time": ring_time, "ring_time_seconds": ring_time_s,
        "ring_time_status": "CONFIRMED",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if name == "John Cena" else "FALSE",
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
        "source_ids": "S068;S069",
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
        er["solo_eliminations_count"] = len([c for c in credited]) if er["wrestler_id"] != "muhammad-hassan" else ""
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
    ("Edge", 1, "Shawn Michaels", "", "Singles", "FALSE", "", "FALSE", "Win", "", "", "18:29", "Opener", "S069", "Pinned Shawn Michaels. Not a Rumble entrant in this match -- Edge is a Rumble entrant this year, see entrants.csv."),
    ("Shawn Michaels", 1, "Edge", "", "Singles", "FALSE", "", "FALSE", "Loss", "", "", "18:29", "Opener", "S069", "Pinned by Edge. Also a Rumble entrant this year -- see entrants.csv."),
    ("John Bradshaw Layfield", 3, "Kurt Angle; The Big Show", "", "Three-Way", "TRUE", "WWE Championship", "TRUE", "Win", "", "TRUE", "11:59", "3rd match", "S069", "Retained the WWE Championship, pinning Angle. Billed as 'John Bradshaw Layfield (JBL)' -- reuses this database's existing 'bradshaw' wrestler_id (same performer, evolved gimmick/name, not a new identity). Not a Rumble entrant this year."),
    ("Big Show", 3, "John Bradshaw Layfield", "Kurt Angle", "Three-Way", "TRUE", "WWE Championship", "FALSE", "Loss", "", "", "11:59", "3rd match", "S069", "Lost the Three-Way to JBL. Not a Rumble entrant this year."),
    ("Kurt Angle", 3, "John Bradshaw Layfield", "The Big Show", "Three-Way", "TRUE", "WWE Championship", "FALSE", "Loss", "", "", "11:59", "3rd match", "S069", "Pinned by JBL. Also a Rumble entrant this year -- see entrants.csv."),
    ("Hunter Hearst Helmsley", 4, "Randy Orton", "", "Singles", "TRUE", "World Heavyweight Championship", "TRUE", "Win", "", "TRUE", "21:27", "4th match", "S069", "Retained the title over Randy Orton. Not a Rumble entrant this year."),
    ("Randy Orton", 4, "Hunter Hearst Helmsley", "", "Singles", "TRUE", "World Heavyweight Championship", "FALSE", "Loss", "", "", "21:27", "4th match", "S069", "Pinned by Triple H. Not a Rumble entrant this year -- first appears as an entrant in this database's 2004 build."),
]
with open(os.path.join(DATA_DIR, "other_matches.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in other_matches:
        name = row[0]
        mnum, opponents, partners, mtype, is_title, title, was_champ, result, won_t, lost_t, duration, position, row_src, notes = row[1:]
        pid = wrestler_ids[name]
        writer.writerow([EVENT_ID, pid, mnum, opponents, partners, mtype, is_title, title, was_champ,
                          result, won_t, lost_t, duration, position, "", "PROBABLE", row_src, notes])

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F182", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "Unusually for a rich timing year, most of the match's 28 eliminations have no individually-named "
     "eliminator -- outside the derived/interference cases documented in F183-F185, only Eddie Guerrero and "
     "Ric Flair (both by Edge) have simple, individually-named credits. Left unassigned rather than guessed.",
     "S068;S069", "open", "2026-09-16"),
    ("F183", EVENT_ID, "eliminations", "muhammad-hassan;eddie-guerrero;chris-benoit;edge;rey-mysterio;shelton-benjamin;booker-t;chris-jericho;luther-reigns", "eliminator_wrestler_id", "unverified",
     "S068 states 'all 8 men in the ring' eliminated Muhammad Hassan together, without naming them. Cross-"
     "referencing this script's own entry_actual/elim_ts timing derivation, exactly 8 wrestlers compute as "
     "active in the ring at Hassan's elimination timestamp (20:15): Eddie Guerrero, Chris Benoit, Edge, Rey "
     "Mysterio, Shelton Benjamin, Booker T, Chris Jericho, and Luther Reigns. Modeled as a DERIVED (not "
     "directly named) 8-way shared elimination -- the names are a tightly-corroborated computation, not a "
     "guess, but are flagged since S068 itself never names them individually.",
     "S068", "open", "2026-09-16"),
    ("F184", EVENT_ID, "eliminations", "kurt-angle;shawn-michaels", "eliminator_wrestler_id", "needs_human_judgement",
     "Kurt Angle was eliminated by a Shawn Michaels superkick, then ran back into the match afterward -- no "
     "longer a legal competitor -- and dragged HBK from the ring into the Ankle Lock. S068's timing commentary "
     "explicitly narrates Angle as the one who 'eliminated' HBK. Angle is credited as HBK's official "
     "eliminator despite not being an active/re-entered competitor at the time -- a deliberate exception to "
     "this database's usual 'officiated record' convention (1997 F081, 2000 F126, 2002 F136, 2003 F171), made "
     "because the source itself explicitly narrates Angle, not an unnamed party, as the one who physically "
     "performed the elimination.",
     "S068;S069", "open", "2026-09-16"),
    ("F185", EVENT_ID, "eliminations", "john-cena;batista", "is_disputed", "needs_human_judgement",
     "Batista and Cena appeared to go over the top rope simultaneously in a botched spot; officials and a "
     "diving, quad-tearing Vince McMahon spent 2m35s (excluded from match time) sorting out the confusion "
     "before the match was restarted, at which point Batista hit a spinebuster to officially eliminate Cena "
     "for the win. This script models only the official, restarted, scored elimination (Cena's computed "
     "elim_ts lands exactly on the total match duration of 51:22). S068's own frame-by-frame review of the "
     "original botched fall suggests Cena's foot may have stayed up fractionally longer than Batista's, "
     "meaning Cena might have 'actually' won the original spot -- noted here but not treated as overriding "
     "the match's official result.",
     "S068;S069", "open", "2026-09-16"),
    ("F186", EVENT_ID, "entrants", "scott-taylor", "ring_time", "needs_human_judgement",
     "Scotty 2 Hotty (this database's existing 'scott-taylor' wrestler_id) was attacked during his dancing "
     "entrance by an outraged Muhammad Hassan and never made it into the ring. S068 itself gives his survival "
     "time as an explicit 0:00. Modeled with entry_number 15 (his buzzer slot), ring_time '0:00', "
     "ring_time_status CONFIRMED, and no elimination row logged -- the third no-show-style case in this "
     "database after Randy Savage (1991), Bastion Booger (1994), Skull (1998), and Test (2004, F175).",
     "S068", "open", "2026-09-16"),
    ("F187", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 10 previously-unseen wrestlers this pass (Daniel Puder, Muhammad Hassan, Kenzo Suzuki, "
     "Jonathan Coachman, Luther Reigns, Mark Jindrak, Gene Snitsky, Orlando Jordan, Paul London, Simon Dean) "
     "with zero bio data in this pass's sources -- names only. Left entirely UNKNOWN, same pattern as every "
     "prior year's equivalent flag.",
     "S068;S069", "open", "2026-09-16"),
    ("F188", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-16"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2005", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2005-01-30", "venue": "Save Mart Center",
    "city_region": "Fresno, California", "country": "United States",
    "attendance_official": "", "attendance_reported": 9642,
    "entry_interval_seconds": 90, "entrant_count": 30, "duration_total": "51:22",
    "duration_status": "CONFIRMED",
    "winner_id": "batista", "runner_up_id": "john-cena",
    "final_two_ids": "batista;john-cena",
    "final_three_ids": "batista;john-cena;edge",
    "final_four_ids": "batista;john-cena;edge;rey-mysterio",
    "first_entrant_id": "eddie-guerrero", "second_entrant_id": "chris-benoit", "final_entrant_id": "ric-flair",
    "first_elimination_id": "daniel-puder", "last_elimination_before_winner_id": "john-cena",
    "eliminations_count": 28, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": "UNKNOWN",
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Jim Ross and Jerry Lawler (RAW); Michael Cole and Tazz (SmackDown!)",
    "ring_announcer": "UNKNOWN",
    "referees": "Not identified in either source consulted this pass",
    "special_rules": (
        "Scotty 2 Hotty was attacked during his entrance and never entered the ring -- see F186. Muhammad "
        "Hassan was eliminated by a DERIVED 8-man group -- see F183. Kurt Angle eliminated Shawn Michaels via "
        "post-elimination interference -- see F184. The finish was controversial: a botched simultaneous "
        "Batista/Cena elimination required a 2m35s real-time pause (during which Vince McMahon tore both "
        "quads) before the match was restarted and officially finished -- see F185."
    ),
    "title_on_the_line": "FALSE",
    "championship_implications": "None in the Rumble match itself, though Edge defeated Shawn Michaels, John Bradshaw Layfield retained the WWE Championship in a Three-Way over Kurt Angle and The Big Show, and Triple H retained the World Heavyweight Championship against Randy Orton, all earlier on the same card. The Undertaker also defeated John Heidenreich in a Casket Match.",
    "winners_reward": "A World Heavyweight Championship match against Triple H at WrestleMania 21, which Batista won after turning face and leaving Evolution, per S069",
    "historical_significance": (
        "Batista's Royal Rumble win launched his face turn and 2005 world title run, defeating his own "
        "Evolution stablemate Triple H at WrestleMania 21. The finish is one of the most controversial in Royal "
        "Rumble history -- a botched simultaneous elimination with Cena led to a 2m35s real-time pause and a "
        "genuine Vince McMahon injury (torn quadriceps in both legs) before the match could be properly "
        "finished. Kurt Angle's post-elimination attack on Shawn Michaels launched one of 2005's best feuds."
    ),
    "notes": (
        "One of this database's richest entry/survival-timing datasets, with all 30 entrants timed to the "
        "second (Scotty 2 Hotty's is 0:00 -- he never entered the ring, see F186). Despite the rich timing "
        "data, eliminator credit is comparatively thin outside a few well-documented cases -- see F182-F185."
    ),
    "data_quality_status": "CONFIRMED", "source_ids": "S068;S069",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2005 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
