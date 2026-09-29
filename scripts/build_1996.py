# -*- coding: utf-8 -*-
"""
Builds all rows for the 1996 Royal Rumble -- schema v2.

Sparse like 1994: NO Cageside-style timing analysis exists in Shane's Word
doc for this year -- only the Dan Wahlers narrative history section, under
the "1996 Royal Rumble Stats" Heading-1. No Excel tab either.

SOURCES CONSULTED THIS PASS:
  S032 Dan Wahlers "History of the Royal Rumble" -- 1996 chapter     tier 9

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order is UNKNOWN for 28 of 30 entrants. Only the first two are
    named: Triple H (Hunter Hearst Helmsley, #1) and Henry Godwinn (#2).
  - Ring/survival times are UNKNOWN for everyone except Triple H, whose
    "48 minutes" survival is stated directly in prose (not to the exact
    second, so kept PROBABLE rather than CONFIRMED -- see F073). No formal
    elimination credit exists for his own elimination.
  - The final sequence IS narrated in detail: "Diesel had just tossed Kama
    out, and turned around to get Superkicked out of the ring by Michaels."
    This gives 2 CONFIRMED eliminator credits -- Kama (by Diesel) and
    Diesel (by Shawn Michaels, the winning elimination) -- the richest
    single detail available for this otherwise sparse year.
  - "Davey Boy Smith" is British Bulldog's real name, already in this
    database (wrestler_id british-bulldog, since 1988/1991/1992/1995) --
    not a new wrestler, just credited by his real name this year rather
    than his ring name.
  - "Ringmaster (Steve Austin)" is deliberately given the wrestler_id
    steve-austin (not the-ringmaster) despite "The Ringmaster" being his
    ring name at this specific event, because S032 itself notes Vince
    McMahon referred to him as "Steve Austin" on commentary even then, and
    this performer reappears under his far-more-famous name in later years
    already in this document (e.g. 1997's chapter, not yet built as of
    this pass) -- using a name-stable id now avoids creating an avoidable
    duplicate later. See F077.
  - "Kama" and "Bob Holly" are each left as their OWN new wrestler_ids,
    NOT merged with any existing entry (Papa Shango/1993, Sparky Plugg/
    1994) despite superficial resemblance in wrestling history generally,
    because neither this pass's source nor any prior year's confirms the
    connection -- inventing it would violate the same rule already applied
    to "Doink" in 1995 (F071). See F076/F078.
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
EVENT_ID = "RR1996M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S032", "Dan Wahlers, 'History of the Royal Rumble' -- 1996 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance as 9,600, full narrative "
     "history (Bret Hart/Undertaker title match with Diesel interference, Steve Austin's Rumble debut as The "
     "Ringmaster, the Michaels/Diesel final sequence), and undercard match results. NO Cageside-style timing "
     "analysis exists for this year -- see F072."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F072", EVENT_ID, "entrants;eliminations", "*", "entry_number;ring_time;elim_number", "unverified",
     "Like 1994 (F059), 1996 has NO Cageside-style timing analysis in Shane's Word doc -- only the Dan "
     "Wahlers narrative. Entry order and ring/survival times are UNKNOWN for 28 of 30 participants; only "
     "Triple H (#1) and Henry Godwinn (#2) have a confirmed entry number, and only Triple H has any stated "
     "survival time (an approximate '48 minutes', not exact seconds -- see F073). Elimination order/credits "
     "are UNKNOWN for everyone except the final sequence (Kama by Diesel, Diesel by Shawn Michaels).",
     "S032", "open", "2026-09-15"),
    ("F073", EVENT_ID, "entrants", "hunter-hearst-helmsley", "ring_time", "unverified",
     "S032 states Triple H 'lasted longest going 48 minutes' but gives no exact second-level timestamp and "
     "no eliminator credit for his own elimination. Ring time kept as '48:00' with PROBABLE status "
     "(approximate, not a precise timing-analysis figure like 1993/1995's entrants) -- elim_number and "
     "eliminated_by_ids left UNKNOWN.",
     "S032", "open", "2026-09-15"),
    ("F074", EVENT_ID, "wrestlers", "*", "real_name;dob;billed_height_m_at_event;billed_weight_kg_at_event;birthplace", "unverified",
     "15 wrestlers appear in this database for the first time via 1996 (1-2-3 Kid, Dory Funk Jr., Doug "
     "Gilbert, Hakushi, Hunter Hearst Helmsley, Bob Holly, Barry Horowitz, Kama, Takao Omori, The Ringmaster/"
     "Steve Austin, Headhunter #1, Headhunter #2, Vader, Savio Vega, Isaac Yankem) with zero bio data in this "
     "pass's source -- names only. Left entirely UNKNOWN, same pattern as every prior year's equivalent flag.",
     "S032", "open", "2026-09-15"),
    ("F075", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-15"),
    ("F076", EVENT_ID, "wrestlers", "kama", "aliases_ring_names", "needs_human_judgement",
     "No source consulted this pass connects 'Kama' to any other wrestler already in this database (e.g. "
     "Papa Shango, added 1993). Left as a fully distinct, fully UNKNOWN-bio new wrestler for now, following "
     "the same 'don't assume, verify' approach already used for 'Doink' (1995's F071) -- worth a specific "
     "check in a future fact-check pass.",
     "S032", "open", "2026-09-15"),
    ("F077", EVENT_ID, "wrestlers", "steve-austin", "ring_name;aliases_ring_names", "needs_human_judgement",
     "Steve Austin's Royal Rumble debut, wrestling as 'The Ringmaster' -- S032 itself notes Vince McMahon "
     "referred to him as 'Steve Austin' on commentary even at this event. Deliberately given the wrestler_id "
     "steve-austin rather than the-ringmaster, anticipating this performer's reappearance under his more "
     "famous ring name in later years of this document -- a forward-looking naming choice, flagged here since "
     "it deviates from this database's usual practice of slugifying the AT-EVENT ring name.",
     "S032", "open", "2026-09-15"),
    ("F078", EVENT_ID, "wrestlers", "bob-holly", "aliases_ring_names", "needs_human_judgement",
     "No source consulted this pass connects 'Bob Holly' to any other wrestler already in this database (e.g. "
     "Sparky Plugg, added 1994). Left as a fully distinct, fully UNKNOWN-bio new wrestler for now, same "
     "caution as F076/F071 -- worth a specific check in a future fact-check pass.",
     "S032", "open", "2026-09-15"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("1-2-3 Kid", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S032"),
    ("Dory Funk Jr.", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Veteran, described as 'legendary' per S032. No bio data in either source this pass.", "S032"),
    ("Doug Gilbert", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Representing the USWA per S032. No bio data in either source this pass.", "S032"),
    ("Hakushi", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S032"),
    ("Hunter Hearst Helmsley", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "Triple H", "", "", "First Rumble entrant (#1); lasted longest at ~48 minutes per S032 -- see F073.", "S032"),
    ("Bob Holly", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No identity connection to any other wrestler stated in either source this pass -- see F078. No bio data in either source this pass.", "S032"),
    ("Barry Horowitz", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S032"),
    ("Kama", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Eliminated Kama... eliminated BY Diesel per S032's final-sequence narration -- see F076 for the identity caution. No bio data in either source this pass.", "S032"),
    ("Takao Omori", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Representing All-Japan Pro Wrestling per S032. No bio data in either source this pass.", "S032"),
    ("The Ringmaster", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Steve Austin's Royal Rumble debut gimmick -- see F077 for why this wrestler_id is steve-austin rather than the-ringmaster. No bio data in either source this pass.", "S032"),
    ("Headhunter #1", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S032"),
    ("Headhunter #2", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S032"),
    ("Vader", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "First WWF appearance per S032 -- 'at the beginning of what could have been a very successful run for him in the company.' No bio data in either source this pass.", "S032"),
    ("Savio Vega", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S032"),
    ("Isaac Yankem", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S032"),
]

reused = {
    "Bob Backlund": "bob-backlund", "Diesel": "diesel", "Duke Droese": "duke-droese",
    "Fatu": "fatu", "Henry Godwinn": "henry-godwinn", "Owen Hart": "owen-hart",
    "Marty Jannetty": "marty-jannetty", "Jerry Lawler": "jerry-lawler", "Mabel": "mabel",
    "Aldo Montoya": "aldo-montoya", "Jake Roberts": "jake-roberts", "Tatanka": "tatanka",
    "Yokozuna": "yokozuna", "Shawn Michaels": "shawn-michaels",
    # "Davey Boy Smith" is British Bulldog's real name -- same person, already in this database
    # (wrestler_id british-bulldog, since 1988/1991/1992/1995), credited by real name this year.
    "Davey Boy Smith": "british-bulldog",
}
wrestler_ids = {}
wrestler_ids.update(reused)
# Deliberate wrestler_id override -- see F077.
wrestler_ids["The Ringmaster"] = "steve-austin"

with open(os.path.join(DATA_DIR, "wrestlers.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in new_wrestlers:
        ring_name = row[0]
        wid = wrestler_ids.get(ring_name) or slugify(ring_name)
        wrestler_ids[ring_name] = wid
        writer.writerow([wid] + list(row))

# ---------------------------------------------------------------------------
# ENTRANTS -- 30 named participants; entry order/ring time UNKNOWN except
# the first two and Triple H's approximate survival time.
# ---------------------------------------------------------------------------
all_names = [
    "1-2-3 Kid", "Bob Backlund", "Diesel", "Duke Droese", "Fatu", "Dory Funk Jr.", "Doug Gilbert",
    "Henry Godwinn", "Hakushi", "Owen Hart", "Hunter Hearst Helmsley", "Bob Holly", "Barry Horowitz",
    "Marty Jannetty", "Kama", "Jerry Lawler", "Mabel", "Aldo Montoya", "Takao Omori", "The Ringmaster",
    "Jake Roberts", "Davey Boy Smith", "Headhunter #1", "Headhunter #2", "Tatanka", "Vader",
    "Savio Vega", "Isaac Yankem", "Yokozuna", "Shawn Michaels",
]
assert len(all_names) == 30

ENTRY_NUMBERS = {"Hunter Hearst Helmsley": 1, "Henry Godwinn": 2}
KNOWN_ELIMINATORS = {
    "Kama": (["Diesel"], ""),
    "Diesel": (["Shawn Michaels"], ""),
}

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Shawn Michaels")
    entry = ENTRY_NUMBERS.get(name, "")
    ring_time = "48:00" if name == "Hunter Hearst Helmsley" else ""
    ring_time_s = mmss_to_seconds(ring_time) if ring_time else ""
    elim_by, sim_group = KNOWN_ELIMINATORS.get(name, ([], ""))

    note = ""
    if name == "Hunter Hearst Helmsley":
        note = "Approximate '48 minutes' survival time per S032's prose, not exact seconds -- see F073. No formal elimination credit stated."

    for eliminator in elim_by:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": "",
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
            "assisting_wrestler_ids": "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": "",
            "elimination_clock_time": "", "elimination_clock_seconds": "",
            "elimination_type": "over_top_rope",
            "elimination_method": (
                "Diesel tossed Kama out." if name == "Kama" else
                "Diesel turned around after eliminating Kama and was superkicked out by Michaels -- the winning elimination." if name == "Diesel" else "UNKNOWN"
            ),
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "TRUE", "is_shared": "FALSE",
            "is_accidental": "FALSE", "is_self_elimination": "FALSE",
            "is_storyline_related": "UNKNOWN", "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE", "simultaneous_group_id": sim_group,
            "data_quality_status": "CONFIRMED",
            "source_ids": "S032",
            "notes": "",
        })

    er = {
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": "CONFIRMED" if entry else "UNKNOWN",
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
        "gimmick_at_event": "", "manager_at_event": "",
        "tag_team_name": "",
        "faction_stable": "",
        "current_champion_title": "", "championship_level": "", "championship_partner": "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        "title_defended_same_card": "FALSE", "title_lost_same_card": "FALSE",
        "elim_number": "", "elim_number_status": "N/A" if is_winner else "UNKNOWN",
        "eliminated_by_ids": ";".join(wrestler_ids[e] for e in elim_by),
        "elimination_clock_time": "", "elimination_clock_seconds": "",
        "ring_time": ring_time, "ring_time_seconds": ring_time_s,
        "ring_time_status": "PROBABLE" if name == "Hunter Hearst Helmsley" else "UNKNOWN",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if wid == "diesel" else "FALSE",
        "is_final_two": "TRUE" if wid in ("shawn-michaels", "diesel") else "UNKNOWN",
        "is_final_three": "UNKNOWN", "is_final_four": "UNKNOWN",
        "surprise_entrant": "FALSE", "legend_returning": "FALSE", "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE", "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED" if entry or is_winner or name in ("Kama", "Diesel") else "PROBABLE",
        "source_ids": "S032",
        "notes": note,
    }
    entrant_rows.append(er)

with open(os.path.join(DATA_DIR, "entrants.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ENTRANTS_FIELDS)
    for er in entrant_rows:
        writer.writerow(er)

with open(os.path.join(DATA_DIR, "eliminations.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ELIMINATIONS_FIELDS)
    for row in elim_rows:
        writer.writerow(row)

# ---------------------------------------------------------------------------
# OTHER MATCHES ON THE SAME CARD
# ---------------------------------------------------------------------------
other_matches = [
    ("British Bulldog", 1, "Goldust", "", "Singles", "TRUE", "Intercontinental Championship", "FALSE", "Loss", "", "", "14:17", "3rd match", "S032", "Pinned by Goldust, who won the IC title. Listed here under his usual ring name; competed in the Rumble match this same night under his real name, Davey Boy Smith -- see script docstring."),
    ("The Undertaker", 4, "Bret Hart", "", "Singles", "TRUE", "World Heavyweight Championship", "FALSE", "Win", "", "", "28:31", "World Title Match", "S032", "Won by DQ after Diesel pulled the referee out and flipped off Undertaker mid-count -- Bret Hart retains the title despite the DQ loss."),
    ("Bret Hart", 4, "The Undertaker", "", "Singles", "TRUE", "World Heavyweight Championship", "TRUE", "Win", "", "TRUE", "28:31", "World Title Match", "S032", "Retained the title via DQ (Diesel interference) despite Undertaker winning the match itself."),
]
with open(os.path.join(DATA_DIR, "other_matches.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for (name, mnum, opponents, partners, mtype, is_title, title, was_champ, result, won_t, lost_t, duration, position, row_src, notes) in other_matches:
        pid = wrestler_ids.get(name, slugify(name))
        writer.writerow([EVENT_ID, pid, mnum, opponents, partners, mtype, is_title, title, was_champ,
                          result, won_t, lost_t, duration, position, "", "PROBABLE", row_src, notes])

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 1996", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "1996-01-21", "venue": "Selland Arena",
    "city_region": "Fresno, California", "country": "United States",
    "attendance_official": "", "attendance_reported": 9600,
    "entry_interval_seconds": "UNKNOWN", "entrant_count": 30, "duration_total": "58:49",
    "duration_status": "PROBABLE",
    "winner_id": "shawn-michaels", "runner_up_id": "diesel",
    "final_two_ids": "shawn-michaels;diesel", "final_three_ids": "UNKNOWN",
    "final_four_ids": "UNKNOWN",
    "first_entrant_id": "hunter-hearst-helmsley", "second_entrant_id": "henry-godwinn", "final_entrant_id": "UNKNOWN",
    "first_elimination_id": "UNKNOWN", "last_elimination_before_winner_id": "diesel",
    "eliminations_count": "UNKNOWN", "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": "UNKNOWN",
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": "N/A",
    "commentary_team": "Vince McMahon, Mr. Perfect", "ring_announcer": "Howard Finkel",
    "referees": "Not identified in either source consulted this pass",
    "special_rules": (
        "The WWF Championship match (Bret Hart vs. Undertaker) went on LAST this year instead of the Royal "
        "Rumble match itself -- the start of a trend that continued for several years per S032. Diesel "
        "interfered in that title match, pulling the referee during a count and costing Undertaker the win "
        "(Bret retained via DQ). Steve Austin made his Royal Rumble debut wrestling as 'The Ringmaster' -- see "
        "F077. This is the leanest build in the database aside from 1994 -- no Cageside-style timing analysis "
        "exists for 1996, so entry order and ring times are UNKNOWN for all but a handful of participants -- "
        "see F072."
    ),
    "title_on_the_line": "FALSE", "championship_implications": "None in the Rumble match itself, though the WWF Championship (Undertaker def. Bret Hart by pinfall/submission-equivalent, but Bret retained via DQ due to Diesel's interference) was contested LAST on the same card, after the Rumble match",
    "winners_reward": "A WWF Championship match against Bret Hart at WrestleMania XII (an Iron Man Match), per S032",
    "historical_significance": "Shawn Michaels' second consecutive Royal Rumble win. Steve Austin's Royal Rumble debut, wrestling as The Ringmaster -- 5 years before becoming Stone Cold Steve Austin, the future face of the company. Vader's WWF debut. Triple H's Royal Rumble debut, lasting the longest of anyone in the match (~48 minutes) despite not winning.",
    "notes": "Only 2 of 30 entrants (Triple H #1, Henry Godwinn #2) have a confirmed entry number, and only Triple H has any stated ring time -- see F072/F073. This is the leanest build in the database aside from 1994, a genuine gap in the source material for this specific year rather than a processing shortfall.",
    "data_quality_status": "PROBABLE", "source_ids": "S032",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"1996 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
