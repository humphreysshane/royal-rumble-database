# -*- coding: utf-8 -*-
"""
Builds all rows for the 2003 Royal Rumble -- schema v2.

Rich year like 1999/2001: Shane's doc has a full "2003 Rumble Stats -
Cageside" frame-by-frame timing analysis (survival times, entrance times,
time-between-buzzers, ring crowdedness) PLUS the Dan Wahlers narrative
history section, both under the "2003 Royal Rumble Stats" Heading-1.

SOURCES CONSULTED THIS PASS:
  S065 '2003 Rumble Stats - Cageside' section (Shane's doc)              tier 9
  S066 Dan Wahlers, 'History of the Royal Rumble' -- 2003 chapter        tier 9

METHODOLOGY (mirrors 1999/2001's DERIVED elimination-order pattern):
  entry_actual[name] = cumulative buzzer-gap time + entrance_lag[name].
  elim_ts[name] = entry_actual[name] + survival_time[name] (both given
  directly by S065). All entrants are ranked by elim_ts to derive
  elim_number. Shawn Michaels and Chris Jericho (the first two entrants)
  both start at entry_actual=0, per S065's own note that Jericho's
  pre-bell ambush on Michaels wasn't counted as match time. Multiple
  internal checksums validate this derivation: the cumulative buzzer sum
  lands exactly on the stated "46:15" final-buzzer mark; the "Jericho
  eliminated both Edge and Christian at the time stamp 15m 51s" line
  matches this script's computed elim_ts for both men exactly (951s);
  "Jeff Hardy was eliminated at the time stamp 29m 10s" matches exactly
  (1750s); Brock Lesnar's (the winner's) own survival time of 9:01 is
  exactly (match total 53:47) minus his entry_actual (44:46); and The
  Undertaker's computed elim_ts (the winning elimination) lands exactly
  on the stated match duration of 53:47. See the assert checkpoints below.

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order and survival ("ring") time are known to the second for ALL
    30 entrants -- ring_time_status is CONFIRMED throughout.
  - Eliminator credit: Jericho ambushed Michaels before the bell to open
    the match; Jericho eliminated Edge and Christian together at 15:51
    (of a narrative-stated aggregate of 6 total -- only 3 individually
    named, see F168); Mysterio eliminated Nowinski; Test eliminated
    Jericho (with a returning, already-eliminated Michaels' revenge
    attack on Jericho noted as a contributing factor, not co-credited --
    see F171-style "officiated record" reasoning); Brock Lesnar F5'd Matt
    Hardy and "took care of...Team Angle" (Charlie Haas and Shelton
    Benjamin, eliminated together); The Undertaker eliminated Maven
    (revenge for 2002), Rosey, Cena, Batista, and Kane before Lesnar threw
    Undertaker out for the win. Batista's chair-assisted re-entry after
    his official elimination is noted but NOT modeled as a second entry,
    per this database's "officiated record" convention (1997 F081, 2000
    F126, 2002 F136). See F169-F171.
  - Rosey is present throughout the Cageside timing data (entry #16,
    survival 10:16) but is MISSING from the Dan Wahlers "Match Results"
    paragraph's named participant list -- a document-internal
    inconsistency, flagged rather than silently resolved. See F166.
  - Match duration: Cageside's precise per-second derivation gives 53:47;
    the informal "Match Results" summary line instead states "(56:00)" --
    the same recurring pattern seen in other rich years. The more
    rigorous Cageside figure is used as duration_total. See F167.
  - A-Train is very likely the same performer (Matt Bloom) as this
    database's existing "prince-albert" wrestler_id (used in 1999-2001
    builds) but neither source states that connection directly this pass
    -- left as a separate, new wrestler_id pending a future fact-check
    pass requiring 2 independent sources, the same caution class as
    Scotty 2 Hotty/Scott Taylor (2001's F132) and Viscera/Mabel (2000's
    F127). See F170.
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
EVENT_ID = "RR2003M"


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
    ("S065", "'2003 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers, ring "
     "crowdedness) filed under the '2003 Royal Rumble Stats' Heading-1. States match duration as 53:47, vs. "
     "the Match Results line's '56:00' -- see F167. NOT live-fetched this pass."),
    ("S066", "Dan Wahlers, 'History of the Royal Rumble' -- 2003 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance (14,712), full narrative "
     "history (the Angle/Benoit WWE Title classic, the Triple H/Steiner Worst Match of the Year, the Final "
     "Four of Lesnar/Undertaker/Kane/Batista), and undercard match results. Its 'Match Results' participant "
     "list omits Rosey despite his clear presence in S065's timing data -- see F166."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# TIMING DERIVATION
# ---------------------------------------------------------------------------
buzzer_gaps = [
    ("Chris Nowinski", "1:30"), ("Rey Mysterio", "1:36"), ("Edge", "1:32"), ("Christian", "2:00"),
    ("Chavo Guerrero", "1:32"), ("Yoshihiro Tajiri", "1:36"), ("Bill DeMott", "1:29"), ("Tommy Dreamer", "1:32"),
    ("B-2", "1:55"), ("Rob Van Dam", "1:41"), ("Matt Hardy", "1:38"), ("Eddie Guerrero", "2:01"),
    ("Jeff Hardy", "1:33"), ("Rosey", "1:32"), ("Test", "1:32"), ("John Cena", "1:31"),
    ("Charlie Haas", "1:50"), ("Rikishi", "1:42"), ("Jamal", "1:30"), ("Kane", "1:33"),
    ("Shelton Benjamin", "1:31"), ("Booker T", "1:34"), ("A-Train", "1:42"), ("Maven", "1:59"),
    ("Goldust", "1:32"), ("Batista", "1:46"), ("Brock Lesnar", "1:39"), ("The Undertaker", "1:47"),
]
buzzer_time = {}
cum = 0
for name, gap in buzzer_gaps:
    cum += mmss(gap)
    buzzer_time[name] = cum
assert cum == mmss("46:15"), f"buzzer checksum failed: {cum}"

# Entrance times (buzzer sound -> stepping into the ring). Shawn Michaels and
# Chris Jericho excluded (their contact preceded the official start of the
# match -- Jericho's low-blow ambush on Michaels happened before the bell).
entrance_lag = {
    "Chris Nowinski": "2:57", "John Cena": "1:33", "The Undertaker": "0:45", "Tommy Dreamer": "0:22",
    "Test": "0:21", "Booker T": "0:21", "Kane": "0:20", "Rosey": "0:18", "Batista": "0:18",
    "Brock Lesnar": "0:18", "Matt Hardy": "0:16", "Rikishi": "0:16", "Rey Mysterio": "0:16",
    "Rob Van Dam": "0:14", "Goldust": "0:13", "Chavo Guerrero": "0:12", "Jamal": "0:11",
    "A-Train": "0:11", "Christian": "0:11", "Eddie Guerrero": "0:10", "Edge": "0:10", "Maven": "0:10",
    "Yoshihiro Tajiri": "0:10", "Bill DeMott": "0:09", "Shelton Benjamin": "0:08", "Jeff Hardy": "0:08",
    "B-2": "0:08", "Charlie Haas": "0:07",
}

entry_actual = {"Shawn Michaels": 0, "Chris Jericho": 0}
for name in buzzer_time:
    entry_actual[name] = buzzer_time[name] + mmss(entrance_lag[name])
assert entry_actual["The Undertaker"] == mmss("47:00")

# Survival ("ring") times, as stated directly by S065. Brock Lesnar (the
# winner) is included with a survival time that is his entry-to-match-end
# span, not an elimination -- excluded from elim_ts below.
survival = {
    "Chris Jericho": "38:59", "Rob Van Dam": "33:00", "Matt Hardy": "27:16", "Kane": "20:26",
    "John Cena": "19:39", "Test": "18:48", "Charlie Haas": "17:13", "Eddie Guerrero": "16:30",
    "Jamal": "16:09", "Rikishi": "14:12", "A-Train": "11:35", "Edge": "11:03", "Shelton Benjamin": "10:56",
    "Rosey": "10:16", "Batista": "9:55", "Christian": "9:02", "Brock Lesnar": "9:01", "Maven": "8:21",
    "Jeff Hardy": "7:27", "Chavo Guerrero": "7:10", "The Undertaker": "6:47", "Booker T": "6:21",
    "Rey Mysterio": "5:55", "Yoshihiro Tajiri": "4:41", "Chris Nowinski": "4:39", "Shawn Michaels": "2:30",
    "Bill DeMott": "2:13", "Tommy Dreamer": "0:49", "Goldust": "0:47", "B-2": "0:25",
}
assert mmss(survival["Brock Lesnar"]) == mmss("53:47") - entry_actual["Brock Lesnar"]

elim_ts = {}
for name, t in survival.items():
    if name == "Brock Lesnar":
        continue  # winner, never eliminated
    elim_ts[name] = entry_actual[name] + mmss(t)

assert elim_ts["Edge"] == mmss("15:51") and elim_ts["Christian"] == mmss("15:51")
assert elim_ts["Jeff Hardy"] == mmss("29:10")
assert elim_ts["The Undertaker"] == mmss("53:47")  # the winning elimination

elim_order_list = sorted(elim_ts, key=lambda n: elim_ts[n])
elim_number = {name: i + 1 for i, name in enumerate(elim_order_list)}
assert elim_number["Shawn Michaels"] == 1
assert elim_number["The Undertaker"] == 29

ENTRY_NUMBERS = {"Shawn Michaels": 1, "Chris Jericho": 2}
for i, (name, _) in enumerate(buzzer_gaps):
    ENTRY_NUMBERS[name] = i + 3
assert ENTRY_NUMBERS["Brock Lesnar"] == 29 and ENTRY_NUMBERS["The Undertaker"] == 30

FINAL_FOUR = {"Brock Lesnar", "The Undertaker", "Kane", "Batista"}
FINAL_THREE = {"Brock Lesnar", "The Undertaker", "Kane"}
FINAL_TWO = {"Brock Lesnar", "The Undertaker"}

# name -> (eliminator names, data_quality_status, elimination_method, is_shared, group_id)
KNOWN_ELIMINATORS = {
    "Shawn Michaels": (["Chris Jericho"], "CONFIRMED", "Ambushed from behind with a low blow and busted open with a chair before the bell even rang, then dumped from the ring right away -- not counted as part of match time or Jericho's own survival time.", False, ""),
    "Chris Nowinski": (["Rey Mysterio"], "CONFIRMED", "Slid into the ring after a long, hesitant entrance and lasted only a short time before being tossed by Mysterio.", False, ""),
    "Edge": (["Chris Jericho"], "CONFIRMED", "Eliminated together with Christian at the 15:51 mark -- one of only 3 individually named of Jericho's narrative-stated 6 total eliminations this match. See F168.", False, "jericho_edge_christian"),
    "Christian": (["Chris Jericho"], "CONFIRMED", "Eliminated together with Edge at the 15:51 mark -- one of only 3 individually named of Jericho's narrative-stated 6 total eliminations this match. See F168.", False, "jericho_edge_christian"),
    "Chris Jericho": (["Test"], "CONFIRMED", "Test dumped Jericho after a returning (already-eliminated) Shawn Michaels ran back in, bandaged up, for revenge and helped wear Jericho down -- Michaels' interference is a contributing factor, not co-credited, consistent with this database's 'officiated record' convention.", False, ""),
    "Matt Hardy": (["Brock Lesnar"], "CONFIRMED", "F5'd right out of the ring by Lesnar.", False, ""),
    "Charlie Haas": (["Brock Lesnar"], "CONFIRMED", "Eliminated together with tag partner Shelton Benjamin as 'Team Angle' -- Lesnar 'took care of' both.", False, "lesnar_team_angle"),
    "Shelton Benjamin": (["Brock Lesnar"], "CONFIRMED", "Eliminated together with tag partner Charlie Haas as 'Team Angle' -- Lesnar 'took care of' both.", False, "lesnar_team_angle"),
    "Rosey": (["The Undertaker"], "PROBABLE", "Narrative groups his elimination with Cena's, right after Undertaker's #30 entrance ('Rosie, and John Cena quickly bit the dust') -- but Rosey's own computed elimination timestamp (33:41) is well before Undertaker's actual entry (47:00), so the narrative's 'quickly' framing appears compressed/imprecise. Eliminator kept as Undertaker (the only named candidate) but downgraded to PROBABLE given the timing mismatch. See F169.", False, ""),
    "John Cena": (["The Undertaker"], "CONFIRMED", "Eliminated shortly after Undertaker's #30 entrance, consistent with the narrative and the computed timestamps (Cena eliminated at 47:22, 22 seconds after Undertaker's 47:00 entry).", False, ""),
    "Maven": (["The Undertaker"], "CONFIRMED", "Tried to repeat his famous 2002 dropkick elimination of Undertaker -- this time it didn't work, and Undertaker got his revenge.", False, ""),
    "Batista": (["The Undertaker"], "CONFIRMED", "Thrown out by Undertaker in the Final Four. Batista then came back in with a chair as interference; Undertaker tossed him again, but this is not modeled as a second official entry -- see F171.", False, ""),
    "Kane": (["The Undertaker"], "CONFIRMED", "'Double crossed' and thrown out by Undertaker in the Final Four, setting the Final Two of Lesnar and Undertaker.", False, ""),
    "The Undertaker": (["Brock Lesnar"], "CONFIRMED", "The winning elimination -- Lesnar hoisted Undertaker out while he stood by the ropes, securing his WrestleMania 19 title-match slot.", False, ""),
}

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Chris Nowinski", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Rookie entrant (#3); lingered outside the ring during his own entrance window before finally sliding in, then eliminated by Rey Mysterio. Per S065, this was his final WWE TV appearance until a 2011 'Cena This Is Your Life' cameo.", "S065;S066"),
    ("Rey Mysterio", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #4; eliminated Chris Nowinski.", "S065;S066"),
    ("Chavo Guerrero", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #7 as 'Chavo Guerrero Jr.' per the Match Results list.", "S065;S066"),
    ("Yoshihiro Tajiri", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #8; billed simply as 'Tajiri' in the Match Results list.", "S065;S066"),
    ("Bill DeMott", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #9. No bio data in either source this pass.", "S065;S066"),
    ("Tommy Dreamer", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #10; busted Jericho open hardway with a cane shot.", "S065;S066"),
    ("Eddie Guerrero", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #14. No individually-named elimination credit either way this pass.", "S065;S066"),
    ("John Cena", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #18 to a long rapping entrance; eliminated by The Undertaker.", "S065;S066"),
    ("Charlie Haas", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #19 as one half of 'Team Angle' with Shelton Benjamin; eliminated together by Brock Lesnar.", "S065;S066"),
    ("Jamal", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #21. No individually-named elimination credit either way this pass. Later wrestled as Umaga -- not merged with any future identity absent 2 independent sources.", "S065;S066"),
    ("Shelton Benjamin", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #23 as one half of 'Team Angle' with Charlie Haas; eliminated together by Brock Lesnar.", "S065;S066"),
    ("A-Train", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #25. Very likely the same performer (Matt Bloom) as this database's existing 'prince-albert' wrestler_id, but not stated directly by either source this pass -- left unmerged. See F170.", "S065;S066"),
    ("Batista", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #28; reached the Final Four before being eliminated by The Undertaker, then re-entered with a chair as (uncredited) interference -- see F171.", "S065;S066"),
    ("Brock Lesnar", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Earned his Rumble slot by defeating Big Show in the opening match, then entered #29 and won the Royal Rumble, eliminating Matt Hardy, Team Angle (Haas and Benjamin), and The Undertaker for the win -- setting up his WrestleMania 19 WWE Title match against Kurt Angle.", "S065;S066"),
    ("Chris Benoit", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Not a Rumble entrant this year -- lost a widely-praised WWE Championship match to Kurt Angle earlier on the same card. Created here for reuse in later builds where he is a Rumble entrant.", "S066"),
]

reused = {
    "Shawn Michaels": "shawn-michaels", "Chris Jericho": "chris-jericho", "Edge": "edge",
    "Christian": "christian", "B-2": "bull-buchanan", "Rob Van Dam": "rob-van-dam",
    "Matt Hardy": "matt-hardy", "Jeff Hardy": "jeff-hardy", "Rosey": None,  # placeholder, set below
    "Test": "test", "Rikishi": "rikishi", "Kane": "kane", "Booker T": "booker-t",
    "Maven": "maven", "Goldust": "goldust", "The Undertaker": "the-undertaker",
    # Non-entrant reused ids used only in other_matches this year.
    "Big Show": "big-show", "Kurt Angle": "kurt-angle", "Hunter Hearst Helmsley": "hunter-hearst-helmsley",
    "Scott Steiner": "scott-steiner", "Lance Storm": "lance-storm", "William Regal": "william-regal",
}
# Rosey is new -- correct the placeholder.
del reused["Rosey"]
new_wrestlers.append(
    ("Rosey", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #16 per S065's Cageside timing data, but omitted from S066's 'Match Results' named participant list -- a document-internal inconsistency. See F166.", "S065")
)

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
    "Shawn Michaels", "Chris Jericho", "Chris Nowinski", "Rey Mysterio", "Edge", "Christian",
    "Chavo Guerrero", "Yoshihiro Tajiri", "Bill DeMott", "Tommy Dreamer", "B-2", "Rob Van Dam",
    "Matt Hardy", "Eddie Guerrero", "Jeff Hardy", "Rosey", "Test", "John Cena", "Charlie Haas",
    "Rikishi", "Jamal", "Kane", "Shelton Benjamin", "Booker T", "A-Train", "Maven", "Goldust",
    "Batista", "Brock Lesnar", "The Undertaker",
]
assert len(all_names) == 30

WRESTLED_EARLIER = {"Brock Lesnar"}  # qualifying match vs. Big Show, same card -- see other_matches

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Brock Lesnar")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, dq, method, is_shared, group_id = KNOWN_ELIMINATORS.get(name, ([], "", "", False, ""))

    notes_parts = []
    if name == "The Undertaker":
        notes_parts.append("Returned from a months-long absence at #30. Eliminated Maven, Rosey, Cena, Batista, and Kane before being thrown out by Lesnar for the win.")
    elif name == "Chris Jericho":
        notes_parts.append("Ambushed Michaels before the bell to open the match. Narrative-credited with 6 total eliminations (Michaels, Edge, Christian named; 3 more unnamed) -- see F168. Eliminated by Test.")
    elif name == "Rosey":
        notes_parts.append("Present throughout S065's Cageside timing data but omitted from S066's Match Results participant list -- see F166. Eliminator credit downgraded to PROBABLE -- see F169.")
    elif name == "A-Train":
        notes_parts.append("See F170 -- possible but unverified identity connection to this database's existing prince-albert wrestler_id.")
    elif name == "Batista":
        notes_parts.append("Eliminated by Undertaker, then re-entered with a chair as interference (not modeled as a second official entry) before being tossed again -- see F171.")
    elif name in WRESTLED_EARLIER:
        notes_parts.append("Also wrestled earlier on the same card (qualifying match) -- see other_matches.csv.")
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
            "source_ids": "S065;S066",
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
        "is_returning_wrestler": "TRUE" if name == "The Undertaker" else "",
        "absence_length": "several months" if name == "The Undertaker" else "",
        "age_at_event": "", "age_status": "UNKNOWN",
        "billed_height_m_at_event": "", "billed_weight_kg_at_event": "", "billed_from_at_event": "",
        "physical_status": "UNKNOWN",
        "alignment": "", "alignment_status": "UNKNOWN",
        "gimmick_at_event": "", "manager_at_event": "",
        "tag_team_name": "Team Angle" if name in ("Charlie Haas", "Shelton Benjamin") else "",
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
        "wrestlers_eliminated_count": 6 if name == "Chris Jericho" else "",
        "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if name == "The Undertaker" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "FALSE",
        "legend_returning": "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE",
        "wrestled_earlier_on_card": "TRUE" if name in WRESTLED_EARLIER else "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S065;S066",
        "notes": note,
    }
    entrant_rows.append(er)

# Fill in each eliminator's wrestlers_eliminated_ids / counts from elim_rows
# (Jericho's separately-stated aggregate count of 6 total is kept as-is even
# though only 3 individual elim_rows credit him -- see F168).
elim_credit = {}
for row in elim_rows:
    elim_credit.setdefault(row["eliminator_wrestler_id"], []).append(row["eliminated_wrestler_id"])
for er in entrant_rows:
    credited = elim_credit.get(er["wrestler_id"], [])
    if credited:
        if er["wrestler_id"] != "chris-jericho":
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
# wrestler_id in this database; opponents without one are still recorded
# as free text in the 'opponents' field).
# ---------------------------------------------------------------------------
other_matches = [
    ("Brock Lesnar", 1, "Big Show", "", "Singles (Rumble qualifier)", "FALSE", "", "FALSE", "Win", "", "", "6:15", "Opener", "S066", "Earned his Royal Rumble entry by pinning Big Show."),
    ("Big Show", 1, "Brock Lesnar", "", "Singles (Rumble qualifier)", "FALSE", "", "FALSE", "Loss", "", "", "6:15", "Opener", "S066", "Pinned by Lesnar; did not qualify for the Rumble. Not a Rumble entrant this year."),
    ("Hunter Hearst Helmsley", 4, "Scott Steiner", "", "Singles", "TRUE", "World Heavyweight Championship", "TRUE", "Win", "", "TRUE", "17:00", "4th match", "S066", "Retained the title by DQ over Steiner in what won that year's WON 'Worst Match of the Year.' Not a Rumble entrant this year."),
    ("Scott Steiner", 4, "Hunter Hearst Helmsley", "", "Singles", "TRUE", "World Heavyweight Championship", "FALSE", "Loss", "", "", "17:00", "4th match", "S066", "Lost by DQ to Triple H in what won that year's WON 'Worst Match of the Year.' Not a Rumble entrant this year."),
    ("Kurt Angle", 5, "Chris Benoit", "", "Singles", "TRUE", "WWE Championship", "TRUE", "Win", "", "TRUE", "17:18", "5th match", "S066", "Retained the title by submission over Benoit in what Dan Wahlers calls his pick for 2003 Match of the Year. Not a Rumble entrant this year."),
    ("Chris Benoit", 5, "Kurt Angle", "", "Singles", "TRUE", "WWE Championship", "FALSE", "Loss", "", "", "17:18", "5th match", "S066", "Lost by submission to Angle in a match Dan Wahlers calls his pick for 2003 Match of the Year, receiving a standing ovation despite the loss. Not a Rumble entrant this year -- first appears as an entrant in this database's 2004 build.", ),
    ("Lance Storm", 2, "The Dudley Boys (Bubba Ray and D-Von Dudley)", "William Regal", "Tag Team", "TRUE", "World Tag Team Championship", "TRUE", "Loss", "", "TRUE", "7:26", "2nd match", "S066", "Lost the tag titles when D-Von pinned him. Not a Rumble entrant this year."),
    ("William Regal", 2, "The Dudley Boys (Bubba Ray and D-Von Dudley)", "Lance Storm", "Tag Team", "TRUE", "World Tag Team Championship", "TRUE", "Loss", "", "TRUE", "7:26", "2nd match", "S066", "Lost the tag titles alongside Lance Storm. Not a Rumble entrant this year."),
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
    ("F166", EVENT_ID, "entrants", "rosey", "n/a", "conflicting_sources",
     "Rosey is present throughout S065's Cageside timing data (entry #16, survival time 10:16) but is missing "
     "from S066's Dan Wahlers 'Match Results' named participant list -- a document-internal inconsistency, kept "
     "(not silently dropped) since the timing data's presence is unambiguous.",
     "S065;S066", "open", "2026-09-16"),
    ("F167", EVENT_ID, "events", "RR2003M", "duration_total", "conflicting_sources",
     "S065's precise per-second Cageside derivation gives a match duration of 53:47 (with multiple internal "
     "checksums validating it); S066's informal 'Match Results' summary line instead states '(56:00)'. The more "
     "rigorous Cageside figure (53:47) is used as duration_total, consistent with how this database has handled "
     "the same recurring pattern in other rich years.",
     "S065;S066", "open", "2026-09-16"),
    ("F168", EVENT_ID, "eliminations", "chris-jericho", "eliminator_wrestler_id", "unverified",
     "Chris Jericho is credited with a narrative-stated 6 total eliminations this match, but only 3 are "
     "individually named (Shawn Michaels, Edge, Christian) -- his entrant row's wrestlers_eliminated_count is "
     "kept at the stated aggregate of 6 even though only 3 elimination rows exist, the same pattern used for "
     "Kane's 11-total 2001 record (F131).",
     "S065;S066", "open", "2026-09-16"),
    ("F169", EVENT_ID, "eliminations", "rosey", "data_quality_status", "needs_human_judgement",
     "S066's narrative groups Rosey's elimination with Cena's, immediately after Undertaker's #30 entrance "
     "('Rosie, and John Cena quickly bit the dust'). But Rosey's own computed elimination timestamp, derived "
     "from S065's Cageside data (33:41), is well before Undertaker's actual entry (47:00) -- 13+ minutes "
     "earlier -- while Cena's computed timestamp (47:22) does land right after Undertaker's entry as described. "
     "Undertaker is kept as Rosey's credited eliminator (the only named candidate) but the elimination row's "
     "data_quality_status is downgraded to PROBABLE given this timing mismatch, which reads as narrative "
     "compression/imprecision rather than a literal blow-by-blow account.",
     "S065;S066", "open", "2026-09-16"),
    ("F170", EVENT_ID, "wrestlers", "a-train", "wrestler_id", "needs_human_judgement",
     "A-Train (entrant #25) is very likely the same performer (Matt Bloom) as this database's existing "
     "'prince-albert' wrestler_id (used as 'Albert' in the 1999-2001 builds). Neither source consulted this "
     "pass states that connection directly. Left as a separate, new wrestler_id pending a future fact-check "
     "pass with 2 independent sources -- same caution class as Scotty 2 Hotty/Scott Taylor (2001's F132) and "
     "Viscera/Mabel (2000's F127).",
     "S065;S066", "open", "2026-09-16"),
    ("F171", EVENT_ID, "eliminations", "batista", "n/a", "needs_human_judgement",
     "After being officially eliminated by The Undertaker in the Final Four, Batista 'came back in with a "
     "chair' as interference before Undertaker tossed him again. Not modeled as a second entrant row or "
     "elimination -- Batista's official (first and only legitimate) entry and elimination is what's recorded, "
     "consistent with this database's practice of representing the officiated record (see 1997's F081, 2000's "
     "F126, and 2002's F136 for the same principle).",
     "S066", "open", "2026-09-16"),
    ("F172", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 15 previously-unseen wrestlers this pass (Chris Nowinski, Rey Mysterio, Chavo "
     "Guerrero, Yoshihiro Tajiri, Bill DeMott, Tommy Dreamer, Eddie Guerrero, John Cena, Charlie Haas, Jamal, "
     "Shelton Benjamin, A-Train, Batista, Brock Lesnar, Chris Benoit, Rosey) with zero bio data in this pass's "
     "sources -- names only. Left entirely UNKNOWN, same pattern as every prior year's equivalent flag.",
     "S065;S066", "open", "2026-09-16"),
    ("F173", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-16"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2003", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2003-01-19", "venue": "Fleet Center",
    "city_region": "Boston, Massachusetts", "country": "United States",
    "attendance_official": "", "attendance_reported": 14712,
    "entry_interval_seconds": 90, "entrant_count": 30, "duration_total": "53:47",
    "duration_status": "CONFIRMED",
    "winner_id": "brock-lesnar", "runner_up_id": "the-undertaker",
    "final_two_ids": "brock-lesnar;the-undertaker",
    "final_three_ids": "brock-lesnar;the-undertaker;kane",
    "final_four_ids": "brock-lesnar;the-undertaker;kane;batista",
    "first_entrant_id": "shawn-michaels", "second_entrant_id": "chris-jericho", "final_entrant_id": "the-undertaker",
    "first_elimination_id": "shawn-michaels", "last_elimination_before_winner_id": "the-undertaker",
    "eliminations_count": 29, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": "UNKNOWN",
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": 1, "factions_count": "UNKNOWN",
    "commentary_team": "Jim Ross, Jerry Lawler", "ring_announcer": "UNKNOWN",
    "referees": "Not identified in either source consulted this pass",
    "special_rules": (
        "First Royal Rumble after the 2002 brand extension, pitting Raw and SmackDown! talent together for the "
        "first time since the split. Brock Lesnar had to win a qualifying match against Big Show to earn his "
        "spot in the Rumble -- see other_matches."
    ),
    "title_on_the_line": "FALSE",
    "championship_implications": "None in the Rumble match itself, though Kurt Angle retained the WWE Championship against Chris Benoit (in what Dan Wahlers calls his pick for 2003 Match of the Year), Triple H retained the World Heavyweight Championship by DQ against Scott Steiner, and The Dudley Boyz won the World Tag Team Championship from Lance Storm and William Regal, all earlier on the same card.",
    "winners_reward": "A WWE Championship match against Kurt Angle at WrestleMania 19, which Lesnar won, per S066",
    "historical_significance": (
        "Brock Lesnar's Royal Rumble win, having had to first win a qualifying match to even enter, set up his "
        "WrestleMania 19 WWE Championship victory over Kurt Angle. Chris Jericho's pre-bell ambush of Shawn "
        "Michaels opened the match and set the stage for their acclaimed WrestleMania 19 encounter. The Angle/"
        "Benoit WWE Title match on the undercard finished 2nd in that year's Wrestling Observer Year-End "
        "Awards, while the Triple H/Scott Steiner match won 'Worst Match of the Year.'"
    ),
    "notes": (
        "One of this database's richest entry/survival-timing datasets, with all 30 entrants timed to the "
        "second. Rosey is present in the timing data but omitted from the narrative's named participant list "
        "-- see F166. The Cageside-derived duration (53:47) conflicts with the Match Results line's rounder "
        "'56:00' figure -- see F167."
    ),
    "data_quality_status": "CONFIRMED", "source_ids": "S065;S066",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2003 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
