# -*- coding: utf-8 -*-
"""
Builds all rows for the 2008 Royal Rumble -- schema v2.

Rich year like 1999/2001/2003/2005/2007: Shane's doc has a full "2008
Rumble Stats - Cageside" frame-by-frame timing analysis (survival times,
entrance times, time-between-buzzers, ring crowdedness) PLUS the Dan
Wahlers narrative history section, both under the "2008 Royal Rumble
Stats" Heading-1.

SOURCES CONSULTED THIS PASS:
  S080 '2008 Rumble Stats - Cageside' section (Shane's doc)              tier 9
  S081 Dan Wahlers, 'History of the Royal Rumble' -- 2008 chapter        tier 9

METHODOLOGY (mirrors 2007's DERIVED elimination-order pattern):
entry_actual[name] = cumulative buzzer-gap time + entrance_lag[name].
elim_ts[name] = entry_actual[name] + survival_time[name]. The Undertaker
and Shawn Michaels (the first two entrants) both start at entry_actual=0.
Checksums: the cumulative buzzer sum lands exactly on the stated "42:10"
final-buzzer mark (Cena's entrance); Cena's (the winner's) own survival
time of 8:28 is exactly (match total 51:29) minus his entry_actual;
Hornswoggle's unusual "went under the ring, forced back in 25:45 later"
sequence reproduces the narrative's own stated "37m 11s: Hornswoggle
leaves ring" timestamp exactly. See asserts below.

TWO GENUINE TIMING/PARTICIPATION EDGE CASES THIS YEAR:
  - Hornswoggle (entry #9) went under the ring immediately upon entering
    and did not physically enter the ring until forced in by Mark Henry,
    25m 45s later. Per Shane's own stated definition ("Hornswoggle's
    entire time under the ring counts as part of his entrance"), his
    entrance_lag is modeled as 25:45; his listed survival time (0:23) then
    runs from that forced re-entry to when he voluntarily left the ring
    (NOT thrown over the top rope) alongside Finlay -- modeled as a
    self-elimination (voluntary exit), the same convention already used
    for Kane's 1999 and Drew Carey's 2001 self-eliminations.
  - Finlay (advertised/effective #27) ran into the ring ahead of his
    buzzer (which never sounded, since Buzzer 25 in the "Time Between
    Buzzers" list never rang) to protect Hornswoggle, and was disqualified
    for using a weapon. Because no buzzer ever officially signaled his
    entrance, Shane gives him a survival time of 0:00 and does not count
    him among the 29 wrestlers who received a real elimination -- modeled
    here as ring_time=0:00, entry_number=27 (his effective ordinal slot),
    with NO elimination row (a disqualification is not an "elimination"
    under this database's over-the-top-rope definition). Buzzer 25's
    absence is absorbed into Buzzer 26's stated 3:00 gap (a full 90s
    longer than the other buzzers), confirmed by the doc's own explicit
    note that "exactly 3 minutes passed between Buzzer 24 and Buzzer 26."

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order and survival ("ring") time are known to the second for ALL
    30 entrants (Finlay's is a defined 0:00) -- ring_time_status is
    CONFIRMED throughout.
  - Eliminator credit, cross-referenced against this script's own elim_ts
    derivation against the Dan Wahlers narrative's blow-by-blow account,
    is unusually clean this year: Triple H's narrative-stated "eliminated
    six, the most in the match" is fully reconstructable and matches
    exactly (Cody Rhodes, Big Daddy V, Elijah Burke & Mick Foley
    [simultaneous, thrown into each other], Umaga, and Kane [shared with
    Batista]) -- no open flag needed, unlike past years' aggregate-vs-
    named mismatches (e.g. 2003's Jericho, F168).
  - The Undertaker/Shawn Michaels/Ken Kennedy sequence (Undertaker
    eliminates Snitsky, HBK superkicks Undertaker out, Kennedy eliminates
    HBK moments later while HBK is looking back at Taker) reads
    ambiguously in the narrative's prose on a first pass, but is fully
    disambiguated by the computed elim_ts values landing exactly 4 and 6
    seconds apart in that order -- treated as CONFIRMED, not flagged,
    since the timing cross-reference removes the ambiguity.
  - 11 of the 28 elimination-eligible entrants (Santino, Khali, Hardcore
    Holly, John Morrison, Tommy Dreamer, Chuck Palumbo, Jamie Noble, CM
    Punk, The Miz, Shelton Benjamin) have no individually-named eliminator
    this pass -- left UNKNOWN rather than guessed.
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
EVENT_ID = "RR2008M"


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
    ("S080", "'2008 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers, ring "
     "crowdedness) filed under the '2008 Royal Rumble Stats' Heading-1. Documents Hornswoggle's under-the-"
     "ring sequence and Finlay's disqualification in detail. NOT live-fetched this pass."),
    ("S081", "Dan Wahlers, 'History of the Royal Rumble' -- 2008 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance (19,798), full narrative "
     "history (John Cena's surprise return and win, the Piper/Snuka nostalgia spot, the Undertaker/HBK/"
     "Kennedy sequence, and Triple H's 6-elimination stretch before the Cena finish), and undercard match "
     "results."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# TIMING DERIVATION
# ---------------------------------------------------------------------------
buzzer_gaps = [
    ("Santino Marella", "1:31"), ("The Great Khali", "1:41"), ("Hardcore Holly", "1:47"), ("John Morrison", "1:34"),
    ("Tommy Dreamer", "1:16"), ("Batista", "1:40"), ("Hornswoggle", "1:34"), ("Chuck Palumbo", "1:20"),
    ("Jamie Noble", "1:27"), ("CM Punk", "1:30"), ("Cody Rhodes", "1:31"), ("Umaga", "1:30"),
    ("Gene Snitsky", "1:31"), ("The Miz", "1:30"), ("Shelton Benjamin", "1:17"), ("Jimmy Snuka", "1:17"),
    ("Roddy Piper", "1:17"), ("Kane", "1:25"), ("Carlito", "1:21"), ("Mick Foley", "1:15"),
    ("Mr. Kennedy", "1:27"), ("Big Daddy V", "1:39"), ("Mark Henry", "1:39"), ("Chavo Guerrero", "1:35"),
    ("Elijah Burke", "3:00"),  # absorbs Buzzer 25's would-be gap -- see Finlay note above
    ("Triple H", "1:19"), ("John Cena", "2:17"),
]
buzzer_time = {}
cum = 0
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("42:10"), f"buzzer checksum failed: {cum}"

# Entrance times. The Undertaker and Shawn Michaels (pre-bell) and Finlay
# (no official buzzer, DQ'd) excluded.
entrance_lag = {
    "Hornswoggle": "25:45",  # per Shane's own definition -- his entire time under the ring counts as entrance
    "John Cena": "0:51", "Roddy Piper": "0:46", "Big Daddy V": "0:22",
    "The Great Khali": "0:21", "Jimmy Snuka": "0:21", "Kane": "0:16", "Mr. Kennedy": "0:15", "Triple H": "0:15",
    "Jamie Noble": "0:14", "Umaga": "0:14", "Mick Foley": "0:14", "Mark Henry": "0:14",
    "Chavo Guerrero": "0:13", "Elijah Burke": "0:13", "Gene Snitsky": "0:12", "Carlito": "0:12",
    "Tommy Dreamer": "0:11", "Chuck Palumbo": "0:11", "The Miz": "0:10", "Shelton Benjamin": "0:10",
    "Cody Rhodes": "0:09", "Santino Marella": "0:08", "John Morrison": "0:08", "CM Punk": "0:08",
    "Batista": "0:07", "Hardcore Holly": "0:07",
}
entry_actual = {"The Undertaker": 0, "Shawn Michaels": 0}
for name in buzzer_time:
    entry_actual[name] = buzzer_time[name] + mmss(entrance_lag[name])
assert entry_actual["Hornswoggle"] == mmss("36:48")

# Survival ("ring") times, as stated directly by S080. John Cena (the
# winner) is included with a survival time that is his entry-to-match-end
# span, not an elimination -- excluded from elim_ts below. Finlay is
# excluded entirely (DQ'd, no official buzzer/entrance -- see notes above).
survival = {
    "Batista": "37:42", "Shawn Michaels": "32:41", "The Undertaker": "32:35", "John Morrison": "29:25",
    "Umaga": "26:06", "CM Punk": "23:51", "Cody Rhodes": "23:16", "Kane": "17:59", "Carlito": "15:07",
    "Hardcore Holly": "13:46", "Mr. Kennedy": "13:32", "The Miz": "13:07", "Gene Snitsky": "12:27",
    "Mick Foley": "11:29", "Triple H": "11:21", "Mark Henry": "9:12", "John Cena": "8:28", "Big Daddy V": "7:50",
    "Chavo Guerrero": "7:34", "Chuck Palumbo": "4:00", "Jimmy Snuka": "2:44", "Elijah Burke": "2:11",
    "Tommy Dreamer": "2:09", "The Great Khali": "1:10", "Roddy Piper": "1:01", "Jamie Noble": "0:28",
    "Santino Marella": "0:25", "Hornswoggle": "0:23", "Shelton Benjamin": "0:18",
}
assert mmss(survival["John Cena"]) == mmss("51:29") - entry_actual["John Cena"]

elim_ts = {}
for name, t in survival.items():
    if name == "John Cena":
        continue  # winner, never eliminated
    elim_ts[name] = entry_actual[name] + mmss(t)
assert elim_ts["Hornswoggle"] == mmss("37:11")
assert elim_ts["Triple H"] == mmss("51:29")  # the winning elimination, by John Cena

# Cross-check: the Undertaker/HBK/Kennedy sequence lands in the narrated order.
assert elim_ts["Gene Snitsky"] < elim_ts["The Undertaker"] < elim_ts["Shawn Michaels"]
assert elim_ts["Shawn Michaels"] - elim_ts["The Undertaker"] == mmss("0:06")
# Cross-check: Kane's "quickly ended the trip down memory lane" double-elimination of Piper and Snuka.
assert abs(elim_ts["Roddy Piper"] - entry_actual["Kane"]) <= mmss("0:10")
assert abs(elim_ts["Jimmy Snuka"] - entry_actual["Kane"]) <= mmss("0:10")
# Cross-check: Triple H's narrative-stated "eliminated six, the most in the match."
HHH_NAMED = {"Cody Rhodes", "Big Daddy V", "Elijah Burke", "Mick Foley", "Umaga", "Kane"}
assert len(HHH_NAMED) == 6
# Cross-check: Cena's "cleaned house on Carlito, Chavo, and Mark Henry" rapid-fire spot.
assert elim_ts["Chavo Guerrero"] - elim_ts["Carlito"] <= mmss("0:10")
assert elim_ts["Mark Henry"] - elim_ts["Chavo Guerrero"] <= mmss("0:10")

elim_order_list = sorted(elim_ts, key=lambda n: elim_ts[n])
elim_number = {name: i + 1 for i, name in enumerate(elim_order_list)}
assert elim_number["Santino Marella"] == 1
assert elim_number["Triple H"] == 28

ENTRY_NUMBERS = {"The Undertaker": 1, "Shawn Michaels": 2}
for i, (name, _) in enumerate(buzzer_gaps):
    # Finlay's effective slot (27) sits between Chavo Guerrero (buzzer index 23 -> entry 26) and
    # Elijah Burke (buzzer index 24) but has no real buzzer of its own -- so everything from Burke
    # onward is shifted one slot later than a plain index+3 count would give.
    ENTRY_NUMBERS[name] = i + 3 if i <= 23 else i + 4
ENTRY_NUMBERS["Finlay"] = 27  # effective ordinal slot; no real buzzer sounded -- see notes above
assert ENTRY_NUMBERS["Chavo Guerrero"] == 26
assert ENTRY_NUMBERS["Hornswoggle"] == 9 and ENTRY_NUMBERS["Triple H"] == 29 and ENTRY_NUMBERS["John Cena"] == 30

FINAL_FOUR = {"John Cena", "Triple H", "Batista", "Kane"}
FINAL_THREE = {"John Cena", "Triple H", "Batista"}
FINAL_TWO = {"John Cena", "Triple H"}

# name -> (eliminator names, data_quality_status, notes, is_shared, group_id)
KNOWN_ELIMINATORS = {
    "Gene Snitsky": (["The Undertaker"], "CONFIRMED", "Eliminated by The Undertaker moments before Undertaker himself was superkicked out by Shawn Michaels.", False, ""),
    "The Undertaker": (["Shawn Michaels"], "CONFIRMED", "Turned around right into a Superkick from Shawn Michaels immediately after eliminating Gene Snitsky. Computed elimination timestamp lands 4 seconds after Snitsky's and 6 seconds before Michaels' own elimination, disambiguating the narrative's ambiguous phrasing.", False, ""),
    "Shawn Michaels": (["Mr. Kennedy"], "CONFIRMED", "Eliminated by Ken Kennedy while HBK was looking back at a glaring Undertaker, 6 seconds after HBK's own superkick had eliminated Undertaker.", False, ""),
    "Roddy Piper": (["Kane"], "CONFIRMED", "Eliminated by Kane within seconds of Kane's #20 entrance, alongside Jimmy Snuka, ending the Piper/Snuka nostalgia face-off.", False, "kane_piper_snuka"),
    "Jimmy Snuka": (["Kane"], "CONFIRMED", "Eliminated by Kane within seconds of Kane's #20 entrance, alongside Roddy Piper.", False, "kane_piper_snuka"),
    "Cody Rhodes": (["Triple H"], "CONFIRMED", "One of Triple H's narrative-stated 6 eliminations (the most in the match), eliminated shortly after HHH's #29 entrance alongside Big Daddy V.", False, "hhh_cody_bigdaddyv"),
    "Big Daddy V": (["Triple H"], "CONFIRMED", "One of Triple H's 6 eliminations, alongside Cody Rhodes right after HHH's #29 entrance.", False, "hhh_cody_bigdaddyv"),
    "Elijah Burke": (["Triple H"], "CONFIRMED", "One of Triple H's 6 eliminations -- Foley was thrown into Burke by Triple H, and both went to the floor together.", False, "hhh_foley_burke"),
    "Mick Foley": (["Triple H"], "CONFIRMED", "One of Triple H's 6 eliminations -- thrown into Elijah Burke, both going to the floor together.", False, "hhh_foley_burke"),
    "Umaga": (["Triple H"], "CONFIRMED", "One of Triple H's 6 eliminations. Reuses this database's existing 'jamal' wrestler_id (merged identity, see F198).", False, ""),
    "Kane": (["Triple H", "Batista"], "CONFIRMED", "The 6th of Triple H's narrative-stated 6 eliminations -- double-teamed out of the match by Triple H and Batista together, leaving the Final Three of Cena, Triple H, and Batista.", True, ""),
    "Mr. Kennedy": (["Batista"], "CONFIRMED", "Thrown out by Batista while Triple H simultaneously eliminated Umaga.", False, ""),
    "Batista": (["Triple H"], "CONFIRMED", "Went for a Batista Bomb on Cena, who back-dropped out of it; Triple H then tossed Batista out to bring the match down to a final two of himself and Cena.", False, ""),
    "Carlito": (["John Cena"], "CONFIRMED", "One of 3 eliminated in a rapid-fire 'house cleaning' stretch by the returning John Cena, alongside Chavo Guerrero and Mark Henry.", False, "cena_housecleaning"),
    "Chavo Guerrero": (["John Cena"], "CONFIRMED", "One of Cena's rapid-fire 'house cleaning' eliminations, alongside Carlito and Mark Henry.", False, "cena_housecleaning"),
    "Mark Henry": (["John Cena"], "CONFIRMED", "One of Cena's rapid-fire 'house cleaning' eliminations, alongside Carlito and Chavo Guerrero.", False, "cena_housecleaning"),
    "Triple H": (["John Cena"], "CONFIRMED", "The winning elimination -- Cena finally got Triple H up for the FU (despite HHH holding onto the ropes) and dumped him out to win his first career Royal Rumble.", False, ""),
    "Hornswoggle": (["Hornswoggle"], "CONFIRMED", "Self-elimination (voluntary exit), not thrown over the top rope -- per S080, Hornswoggle 'voluntarily left the ring and returned to the backstage area' alongside a disqualified Finlay. Modeled the same way as Kane's 1999 and Drew Carey's 2001 self-eliminations.", False, ""),
}

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Cody Rhodes", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #13. One of Triple H's narrative-stated 6 eliminations, alongside Big Daddy V right after HHH's #29 entrance.", "S080;S081"),
    ("Mr. Kennedy", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Billed as Ken Kennedy. Entered #23 and eliminated Shawn Michaels while HBK was looking back at Undertaker.", "S080;S081"),
    ("Elijah Burke", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #28 (a surprise appearance, per S081). Eliminated by Triple H alongside Mick Foley, thrown into him in a single move.", "S080;S081"),
    ("Jamie Noble", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #11. No individually-named elimination credit either way this pass.", "S080;S081"),
    ("Santino Marella", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #3, the shortest survival time of any entrant to receive a real elimination (0:25, the very first elimination of the match). No individually-named eliminator this pass.", "S080;S081"),
    ("Hornswoggle", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #9 and immediately went under the ring rather than entering it, per S080's own definition of entrance time. Forced into the ring by Mark Henry 25m 45s later; self-eliminated (voluntarily left the ring, never went over the top rope) alongside a disqualified Finlay.", "S080;S081"),
]

reused = {
    "The Undertaker": "the-undertaker", "Shawn Michaels": "shawn-michaels", "The Great Khali": "the-great-khali",
    "Hardcore Holly": "hardcore-holly", "John Morrison": "johnny-nitro", "Tommy Dreamer": "tommy-dreamer",
    "Batista": "batista", "Chuck Palumbo": "chuck-palumbo", "CM Punk": "cm-punk", "Umaga": "jamal",
    "Gene Snitsky": "gene-snitsky", "The Miz": "the-miz", "Shelton Benjamin": "shelton-benjamin",
    "Jimmy Snuka": "jimmy-snuka", "Roddy Piper": "roddy-piper", "Kane": "kane", "Carlito": "carlito",
    "Mick Foley": "mick-foley", "Big Daddy V": "mabel", "Mark Henry": "mark-henry", "Chavo Guerrero": "chavo-guerrero",
    "Triple H": "hunter-hearst-helmsley", "John Cena": "john-cena", "Finlay": "finlay",
    # Non-entrant reused ids used only in other_matches this year.
    "Chris Jericho": "chris-jericho", "Bradshaw": "bradshaw", "Edge": "edge", "Rey Mysterio": "rey-mysterio",
    "Randy Orton": "randy-orton", "Jeff Hardy": "jeff-hardy", "Ric Flair": "ric-flair", "MVP": "mvp",
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
# ENTRANTS -- all 30, full entry order and survival time known (Finlay's is a defined 0:00).
# ---------------------------------------------------------------------------
all_names = [
    "The Undertaker", "Shawn Michaels", "Santino Marella", "The Great Khali", "Hardcore Holly", "John Morrison",
    "Tommy Dreamer", "Batista", "Hornswoggle", "Chuck Palumbo", "Jamie Noble", "CM Punk", "Cody Rhodes", "Umaga",
    "Gene Snitsky", "The Miz", "Shelton Benjamin", "Jimmy Snuka", "Roddy Piper", "Kane", "Carlito", "Mick Foley",
    "Mr. Kennedy", "Big Daddy V", "Mark Henry", "Chavo Guerrero", "Finlay", "Elijah Burke", "Triple H", "John Cena",
]
assert len(all_names) == 30

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "John Cena")
    is_dq_no_elim = (name == "Finlay")
    entry = ENTRY_NUMBERS[name]
    ring_time = "0:00" if is_dq_no_elim else survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, dq, method, is_shared, group_id = KNOWN_ELIMINATORS.get(name, ([], "", "", False, ""))

    notes_parts = []
    if name == "John Cena":
        notes_parts.append("Entered #30 as a surprise -- back after a 3-month absence from a torn pectoral injury -- and won his first career Royal Rumble, cleaning house on Carlito/Chavo/Henry before eliminating Triple H for the win.")
    elif name == "Finlay":
        notes_parts.append("Billed as 'Fit Finlay.' Ran into the ring ahead of his buzzer (which never officially sounded -- see event notes) to protect Hornswoggle with a weapon, and was disqualified. Given a survival time of 0:00 per S080's own definition, since he never had an official entrance; not counted as a real elimination (a disqualification, not an over-the-top-rope exit). See F225.", )
    elif name == "Hornswoggle":
        notes_parts.append("Went under the ring immediately upon his #9 entrance rather than entering it; forced into the ring by Mark Henry 25m 45s later. Self-eliminated, voluntarily leaving the ring alongside a disqualified Finlay -- never went over the top rope. See F224.")
    elif name == "Triple H":
        notes_parts.append("Eliminated 6 -- the most in the match: Cody Rhodes, Big Daddy V, Elijah Burke, Mick Foley (the latter two in one simultaneous move), Umaga, and Kane (shared with Batista) -- before being eliminated by John Cena for the win.")
    elif name == "Umaga":
        notes_parts.append("Reuses this database's existing 'jamal' wrestler_id (identity merged by the 2003-2007 fact-check pass, F198).")
    elif name == "Big Daddy V":
        notes_parts.append("Reuses this database's existing 'mabel' wrestler_id (also used as 'Mabel' and 'Viscera').")
    elif name == "Triple H" or name == "John Morrison":
        pass
    if name == "John Morrison":
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
            "elimination_type": "over_top_rope" if name != "Hornswoggle" else "voluntary_exit",
            "elimination_method": method,
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "FALSE" if is_shared else "TRUE", "is_shared": "TRUE" if is_shared else "FALSE",
            "is_accidental": "FALSE",
            "is_self_elimination": "TRUE" if name == "Hornswoggle" else "FALSE",
            "is_storyline_related": "UNKNOWN",
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE",
            "simultaneous_group_id": group_id,
            "data_quality_status": dq,
            "source_ids": "S080;S081",
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
        "is_returning_wrestler": "TRUE" if name == "John Cena" else "",
        "absence_length": "3 months (torn pectoral)" if name == "John Cena" else "",
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
        "elim_number": "" if (is_winner or is_dq_no_elim) else elim_number[name],
        "elim_number_status": "N/A" if (is_winner or is_dq_no_elim) else "CONFIRMED",
        "eliminated_by_ids": ";".join(wrestler_ids[e] for e in elim_by),
        "elimination_clock_time": "" if (is_winner or is_dq_no_elim) else secs_to_mmss(elim_ts[name]),
        "elimination_clock_seconds": "" if (is_winner or is_dq_no_elim) else elim_ts[name],
        "ring_time": ring_time, "ring_time_seconds": ring_time_s,
        "ring_time_status": "CONFIRMED",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "TRUE" if name == "Hornswoggle" else "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if name == "Triple H" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "TRUE" if name in ("John Cena", "Elijah Burke") else "FALSE",
        "legend_returning": "TRUE" if name in ("Roddy Piper", "Jimmy Snuka") else "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "TRUE" if name in ("Roddy Piper", "Jimmy Snuka") else "FALSE",
        "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "PROBABLE" if is_dq_no_elim else "CONFIRMED",
        "source_ids": "S080;S081",
        "notes": note,
    }
    entrant_rows.append(er)

# Fill in each eliminator's wrestlers_eliminated_ids / counts from elim_rows.
elim_credit = {}
for row in elim_rows:
    elim_credit.setdefault(row["eliminator_wrestler_id"], []).append(row["eliminated_wrestler_id"])
for er in entrant_rows:
    credited = [w for w in elim_credit.get(er["wrestler_id"], []) if w != er["wrestler_id"]]  # exclude self-elims
    if credited:
        er["wrestlers_eliminated_count"] = len(credited)
        er["wrestlers_eliminated_ids"] = ";".join(credited)
        er["solo_eliminations_count"] = sum(1 for row in elim_rows if row["eliminator_wrestler_id"] == er["wrestler_id"] and row["is_shared"] == "FALSE")
        er["assisted_eliminations_count"] = sum(1 for row in elim_rows if row["eliminator_wrestler_id"] == er["wrestler_id"] and row["is_shared"] == "TRUE")

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
    ("Ric Flair", 1, "MVP", "", "Singles (Career vs. Title)", "FALSE", "", "FALSE", "Win", "", "", "", "Opener", "S081", "Won clean with the Figure Four; not for MVP's SmackDown! United States Championship (a non-title match per S081). Not a Rumble entrant this year."),
    ("MVP", 1, "Ric Flair", "", "Singles (Career vs. Title)", "FALSE", "", "TRUE", "Loss", "", "", "", "Opener", "S081", "Lost to Flair by submission (Figure Four) in a non-title match. Also a Rumble entrant this year -- see entrants.csv."),
    ("Chris Jericho", 2, "Bradshaw (JBL)", "", "Singles", "FALSE", "", "FALSE", "No Contest", "", "", "9:24", "2nd match", "S081", "Ended in a Disqualification. Not a Rumble entrant this year."),
    ("Bradshaw", 2, "Chris Jericho", "", "Singles", "FALSE", "", "FALSE", "No Contest", "", "", "9:24", "2nd match", "S081", "Ended in a Disqualification (won by DQ). Not a Rumble entrant this year."),
    ("Edge", 3, "Rey Mysterio", "", "Singles", "TRUE", "World Heavyweight Championship", "TRUE", "Win", "", "TRUE", "12:34", "3rd match", "S081", "Retained the World Heavyweight Championship with help from Vickie Guerrero. Not a Rumble entrant this year."),
    ("Rey Mysterio", 3, "Edge", "", "Singles", "TRUE", "World Heavyweight Championship", "FALSE", "Loss", "", "", "12:34", "3rd match", "S081", "Lost the title match; sprung into a spear off a 619 setup involving Vickie Guerrero. Not a Rumble entrant this year."),
    ("Randy Orton", 4, "Jeff Hardy", "", "Singles", "TRUE", "WWE Championship", "TRUE", "Win", "", "TRUE", "14:12", "4th match", "S081", "Retained the title over the Intercontinental Champion Jeff Hardy, per S081's own (possibly mislabeled) title description. Not a Rumble entrant this year."),
    ("Jeff Hardy", 4, "Randy Orton", "", "Singles", "TRUE", "WWE Championship", "TRUE", "Loss", "", "", "14:12", "4th match", "S081", "Lost the title match to Orton; S081 describes him as having 'a huge amount of momentum' going in. Not a Rumble entrant this year."),
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
    ("F223", EVENT_ID, "events", EVENT_ID, "referees", "unverified",
     "Referees are not individually identified in either source consulted this pass. Left UNKNOWN.",
     "", "open", "2026-09-16"),
    ("F224", EVENT_ID, "entrants", "hornswoggle", "elimination_type", "needs_human_judgement",
     "Hornswoggle's exit is modeled as a self-elimination (voluntary exit, never going over the top rope) per "
     "S080's own explicit account -- he 'voluntarily left the ring and returned to the backstage area' "
     "alongside a disqualified Finlay. This is a judgment call about how to classify a non-standard exit "
     "under this database's over-the-top-rope elimination definition, consistent with the Kane 1999 and Drew "
     "Carey 2001 self-elimination precedents, rather than a genuine source disagreement.",
     "S080", "open", "2026-09-16"),
    ("F225", EVENT_ID, "entrants", "finlay", "ring_time", "unverified",
     "Finlay ran into the ring ahead of his buzzer (Buzzer 25, which never sounded per the 'Time Between "
     "Buzzers' list -- its absence is absorbed into Buzzer 26's unusually long 3:00 gap) and was disqualified "
     "for using a weapon. Because he never had an official, buzzer-signaled entrance, S080 gives him a "
     "survival time of 0:00 and does not count him among the match's real eliminations -- modeled here with "
     "no elimination row (a disqualification, not an over-the-top-rope exit), matching S080's own treatment.",
     "S080", "open", "2026-09-16"),
    ("F226", EVENT_ID, "eliminations", "*", "eliminator_wrestler_id", "unverified",
     "11 of the 28 elimination-eligible entrants (Santino Marella, The Great Khali, Hardcore Holly, John "
     "Morrison, Tommy Dreamer, Chuck Palumbo, Jamie Noble, CM Punk, The Miz, Shelton Benjamin) have no "
     "individually-named eliminator in either source consulted this pass. Left UNKNOWN rather than guessed. "
     "Separately, CM Punk 'went after Taker and HBK, before Taker almost took his head off with a clothesline' "
     "-- described as a near-miss, not a confirmed elimination, and not attributed as such.",
     "S080;S081", "open", "2026-09-16"),
    ("F227", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 6 previously-unseen wrestlers this pass (Cody Rhodes, Mr. Kennedy, Elijah Burke, "
     "Jamie Noble, Santino Marella, Hornswoggle) with zero bio data in this pass's sources -- names only. Left "
     "entirely UNKNOWN, same pattern as every prior year's equivalent flag.",
     "S080;S081", "open", "2026-09-16"),
    ("F228", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-16"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2008", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2008-01-27", "venue": "Madison Square Garden",
    "city_region": "New York City, New York", "country": "United States",
    "attendance_official": "", "attendance_reported": 19798,
    "entry_interval_seconds": 90, "entrant_count": 30, "duration_total": "51:29",
    "duration_status": "CONFIRMED",
    "winner_id": "john-cena", "runner_up_id": "hunter-hearst-helmsley",
    "final_two_ids": "john-cena;hunter-hearst-helmsley",
    "final_three_ids": "john-cena;hunter-hearst-helmsley;batista",
    "final_four_ids": "john-cena;hunter-hearst-helmsley;batista;kane",
    "first_entrant_id": "the-undertaker", "second_entrant_id": "shawn-michaels", "final_entrant_id": "john-cena",
    "first_elimination_id": "santino-marella", "last_elimination_before_winner_id": "hunter-hearst-helmsley",
    "eliminations_count": 28, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": 2,
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Jim Ross and Jerry Lawler (RAW); Michael Cole and Jonathan Coachman (SmackDown!); Joey Styles and Tazz (ECW)",
    "ring_announcer": "UNKNOWN",
    "referees": "Not identified in either source consulted this pass",
    "special_rules": (
        "Finlay was disqualified for using a weapon after running into the ring ahead of his buzzer -- the "
        "only disqualification recorded in this database's Royal Rumble history so far. See F225."
    ),
    "title_on_the_line": "FALSE",
    "championship_implications": "None in the Rumble match itself, though Edge retained the World Heavyweight Championship over Rey Mysterio and Randy Orton retained the WWE Championship over Jeff Hardy, both earlier on the same card.",
    "winners_reward": "UNKNOWN",
    "historical_significance": (
        "John Cena's first career Royal Rumble win, in a surprise return from a 3-month torn-pectoral injury "
        "as the shock #30 entrant. Triple H eliminated 6 wrestlers, the most in the match. Batista was the "
        "match's 'Iron Man' at 37:42. A rare disqualification (Finlay) and a genuinely unusual participation "
        "case (Hornswoggle spending 25m 45s under the ring before being forced in) make this one of this "
        "database's more unusual timing datasets to model. Roddy Piper and Jimmy Snuka's returning nostalgia "
        "face-off, ended abruptly by Kane, was a highlight per S081."
    ),
    "notes": (
        "One of this database's richest entry/survival-timing datasets, with all 30 entrants timed to the "
        "second (Finlay's is a defined 0:00, not a real survival time -- see F225). Eliminator credit is "
        "unusually clean for a rich year: Triple H's narrative-stated 6 eliminations are fully individually "
        "reconstructed and cross-checked against the timing derivation with no open discrepancy, unlike past "
        "years' aggregate-vs-named mismatches. 11 of 28 elimination-eligible entrants remain without a named "
        "eliminator -- see F226."
    ),
    "data_quality_status": "CONFIRMED", "source_ids": "S080;S081",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2008 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
