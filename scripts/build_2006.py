# -*- coding: utf-8 -*-
"""
Builds all rows for the 2006 Royal Rumble -- schema v2.

Sparse year like 2002/2004: NO Cageside-style timing analysis exists in
Shane's Word doc for this year -- only the Dan Wahlers narrative section,
under the "2006 Royal Rumble Stats" Heading-1. Unlike 2002/2004, this
narrative is comparatively thin: entry order is known for only 3 of 30
entrants, and eliminator credit covers only a handful of the match's 29
eliminations.

SOURCES CONSULTED THIS PASS:
  S070 Dan Wahlers, "History of the Royal Rumble" -- 2006 chapter     tier 9

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order is known for only 3 of 30 entrants -- Triple H #1, Rey
    Mysterio #2, Bobby Lashley #8. No ring/survival times or elim_number
    values are stated for anyone. See F189.
  - The Match Results "Other participants" list names only 29 of the
    stated 30 entrants (the winner, Mysterio, plus 28 others) -- one
    slot's occupant is UNKNOWN. entrant_count is kept at 30 (WWE's
    official record) with only 29 wrestler rows created this pass. See
    F190 -- a mirror-image of 2003's Rosey omission (F166), this time an
    entire slot rather than one named-but-uncounted wrestler.
  - Triple H is credited with eliminating both Ric Flair and Big Show
    "early on," yet Big Show is separately credited (with Kane) for
    eliminating Bobby Lashley, who entered at #8 -- with no exact
    timestamps this year, there is no way to sequence these, so both
    facts are kept as stated rather than treated as contradictory. See
    F191.
  - SHANE MCMAHON'S INTERFERENCE ELIMINATION OF SHAWN MICHAELS (new
    structural situation, distinct from 2005's Kurt Angle/HBK case -- see
    F192): Shane McMahon was never a Rumble entrant at all this year, yet
    the narrative explicitly states he eliminated Michaels "from behind"
    while Michaels was distracted by Vince McMahon. A new, non-entrant
    wrestler_id is created for Shane McMahon solely to carry this
    elimination credit, following the same "officiated record" exception
    reasoning used for Angle/HBK (2005's F184) -- the source explicitly
    narrates a named individual as the one who physically performed the
    elimination, so that individual is credited even though not a legal
    competitor.
  - Rey Mysterio's Royal Rumble win, at 62:12, broke Chris Benoit's
    then-standing 2004 longevity record of 61:37.
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
EVENT_ID = "RR2006M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S070", "Dan Wahlers, 'History of the Royal Rumble' -- 2006 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance (14,500), full narrative "
     "history (Triple H's dominant opening stretch, the Eddie Guerrero tribute angle around Rey Mysterio's "
     "win, Shane McMahon's interference elimination of Shawn Michaels, and Rey Mysterio's then-record 62:12 "
     "performance), and undercard match results. NO Cageside-style timing analysis exists for this year, and "
     "entry order/eliminator credit is thinner than most other sparse years in this database -- see F189."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Bobby Lashley", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #8; made to look strong in confrontations with Big Show and Kane before the two of them eliminated him together.", "S070"),
    ("Carlito", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No individually-named elimination credit either way this pass.", "S070"),
    ("Joey Mercury", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "One half of MNM with Johnny Nitro; 'made a nice showing' and was kept in the match a long time, per S070. No individually-named elimination credit either way this pass.", "S070"),
    ("Road Warrior Animal", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No individually-named elimination credit either way this pass.", "S070"),
    ("Super Crazy", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No individually-named elimination credit either way this pass.", "S070"),
    ("Trevor Murdoch", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No individually-named elimination credit either way this pass.", "S070"),
    ("Chris Masters", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No individually-named elimination credit either way this pass.", "S070"),
    ("Eugene", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No individually-named elimination credit either way this pass.", "S070"),
    ("Johnny Nitro", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "One half of MNM with Joey Mercury; 'made a nice showing' and was kept in the match a long time, per S070. No individually-named elimination credit either way this pass.", "S070"),
    ("Psicosis", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No individually-named elimination credit either way this pass; not mentioned in the narrative body, only the Match Results participant list.", "S070"),
    ("Sylvan Grenier", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No individually-named elimination credit either way this pass; not mentioned in the narrative body, only the Match Results participant list.", "S070"),
    ("Shane McMahon", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Not a Rumble entrant this year -- created solely to carry the eliminator credit for Shawn Michaels' elimination, which the narrative explicitly attributes to Shane despite him never being a legal competitor in the match. See F192.", "S070"),
]

reused = {
    "Triple H": "hunter-hearst-helmsley", "Rey Mysterio": "rey-mysterio", "Simon Dean": "simon-dean",
    "Ric Flair": "ric-flair", "The Big Show": "big-show", "Kane": "kane", "Booker T": "booker-t",
    "Orlando Jordan": "orlando-jordan", "Chavo Guerrero": "chavo-guerrero", "Matt Hardy": "matt-hardy",
    "Tatanka": "tatanka", "Shelton Benjamin": "shelton-benjamin", "Goldust": "goldust",
    "Chris Benoit": "chris-benoit", "Viscera": "mabel", "Randy Orton": "randy-orton",
    "Shawn Michaels": "shawn-michaels", "Rob Van Dam": "rob-van-dam",
    # Non-entrant reused ids used only in other_matches this year.
    "John Cena": "john-cena", "Edge": "edge", "Kurt Angle": "kurt-angle", "Mark Henry": "mark-henry",
    "Gregory Helms": "the-hurricane", "Nunzio": "nunzio", "Paul London": "paul-london",
    "John Bradshaw Layfield": "bradshaw", "Vince McMahon": "vince-mcmahon",
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
# ENTRANTS -- 29 of the stated 30 slots are named (see F190).
# ---------------------------------------------------------------------------
all_names = [
    "Triple H", "Rey Mysterio", "Simon Dean", "Psicosis", "Ric Flair", "The Big Show", "Sylvan Grenier",
    "Bobby Lashley", "Kane", "Carlito", "Booker T", "Joey Mercury", "Road Warrior Animal", "Orlando Jordan",
    "Chavo Guerrero", "Matt Hardy", "Tatanka", "Super Crazy", "Trevor Murdoch", "Chris Masters",
    "Shelton Benjamin", "Eugene", "Goldust", "Chris Benoit", "Viscera", "Randy Orton", "Johnny Nitro",
    "Shawn Michaels", "Rob Van Dam",
]
assert len(all_names) == 29  # 1 of the official 30 slots is UNKNOWN -- see F190

ENTRY_NUMBERS = {"Triple H": 1, "Rey Mysterio": 2, "Bobby Lashley": 8}
FINAL_FOUR = {"Triple H", "Rey Mysterio", "Randy Orton", "Rob Van Dam"}
FINAL_THREE = {"Triple H", "Rey Mysterio", "Randy Orton"}
FINAL_TWO = {"Rey Mysterio", "Randy Orton"}

# name -> (eliminator names, data_quality_status, elimination_method, is_shared, group_id)
KNOWN_ELIMINATORS = {
    "Ric Flair": (["Triple H"], "CONFIRMED", "Eliminated early on by Triple H, lasting only a little more than a minute -- the fans were upset at how carelessly he was tossed.", False, ""),
    "The Big Show": (["Triple H"], "CONFIRMED", "Eliminated by Triple H -- narrated as 'early on' alongside Flair, though Show is separately credited (with Kane) for eliminating Bobby Lashley (#8) later in the match; no exact timestamps exist this year to resolve the sequencing. See F191.", False, ""),
    "Bobby Lashley": (["The Big Show", "Kane"], "CONFIRMED", "Made to look strong in confrontations with both men before they eliminated him together.", True, "lashley_show_kane"),
    "Chavo Guerrero": (["Triple H"], "CONFIRMED", "Pushed off the top rope by Triple H as he was getting ready to hit a Frog Splash; the fans booed the move.", False, ""),
    "Matt Hardy": (["Viscera"], "CONFIRMED", "'Dry humped, and then eliminated by Viscera.'", False, ""),
    "Shawn Michaels": (["Shane McMahon"], "CONFIRMED", "Fended off attacks from pretty much everyone in the match (Vince McMahon had promised a reward for eliminating him), before being eliminated from behind by Shane McMahon -- who was never a legal competitor in the match. See F192.", False, ""),
    "Triple H": (["Rey Mysterio"], "CONFIRMED", "Double-teamed Mysterio 2-on-1 with Orton in the final four, but Rey defied the odds and sent HHH out. Triple H lasted 60:09 in the match.", False, ""),
    "Randy Orton": (["Rey Mysterio"], "CONFIRMED", "The winning elimination -- Mysterio pulled Orton over the top rope with a body-scissors-like maneuver, winning at 62:12 and breaking Chris Benoit's 2004 longevity record (61:37).", False, ""),
}

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Rey Mysterio")
    entry = ENTRY_NUMBERS.get(name, "")
    elim_by, dq, method, is_shared, group_id = KNOWN_ELIMINATORS.get(name, ([], "", "", False, ""))

    note = ""
    if name == "Rey Mysterio":
        note = "Won at 62:12, breaking Chris Benoit's 2004 longevity record of 61:37. Eliminated Triple H and Randy Orton (the winning elimination) in the final stretch."
    elif name == "Triple H":
        note = "Eliminated Ric Flair and Big Show, then Chavo Guerrero, before lasting 60:09 and being eliminated by Rey Mysterio in the final three."
    elif name == "The Big Show":
        note = "Eliminated by Triple H -- see F191 for the narrative's loose 'early on' framing versus his later credited elimination of Bobby Lashley."
    elif name == "Shawn Michaels":
        note = "Eliminated via interference by Shane McMahon (never a legal competitor this match) while being distracted by Vince McMahon, who had promised a reward for eliminating HBK. See F192."
    elif name == "Viscera":
        note = "Reuses this database's existing 'mabel' wrestler_id (also used as 'Mabel' and 'Big Daddy V')."
    elif name in ("Johnny Nitro", "Joey Mercury"):
        note = "One half of MNM; 'made a nice showing' and was kept in the match a long time, per S070."
    elif name == "Rob Van Dam":
        note = "One of the final four; eliminated first among them (no eliminator named)."

    for eliminator in elim_by:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": "",
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
            "assisting_wrestler_ids": ";".join(wrestler_ids[e] for e in elim_by if e != eliminator) if is_shared else "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": ENTRY_NUMBERS.get(eliminator, ""),
            "elimination_clock_time": "", "elimination_clock_seconds": "",
            "elimination_type": "over_top_rope",
            "elimination_method": method,
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "FALSE" if is_shared else "TRUE", "is_shared": "TRUE" if is_shared else "FALSE",
            "is_accidental": "FALSE",
            "is_self_elimination": "FALSE",
            "is_storyline_related": "TRUE" if name == "Shawn Michaels" else "UNKNOWN",
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE",
            "simultaneous_group_id": group_id,
            "data_quality_status": dq,
            "source_ids": "S070",
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
        "is_returning_wrestler": "TRUE" if name == "Rob Van Dam" else "",
        "absence_length": "most of 2005, reconstructive knee surgery" if name == "Rob Van Dam" else "",
        "age_at_event": "", "age_status": "UNKNOWN",
        "billed_height_m_at_event": "", "billed_weight_kg_at_event": "", "billed_from_at_event": "",
        "physical_status": "UNKNOWN",
        "alignment": "", "alignment_status": "UNKNOWN",
        "gimmick_at_event": "", "manager_at_event": "",
        "tag_team_name": "MNM" if name in ("Johnny Nitro", "Joey Mercury") else "",
        "faction_stable": "",
        "current_champion_title": "", "championship_level": "", "championship_partner": "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        "title_defended_same_card": "FALSE", "title_lost_same_card": "FALSE",
        "elim_number": "", "elim_number_status": "N/A" if is_winner else "UNKNOWN",
        "eliminated_by_ids": ";".join(wrestler_ids[e] for e in elim_by),
        "elimination_clock_time": "", "elimination_clock_seconds": "",
        "ring_time": "", "ring_time_seconds": "",
        "ring_time_status": "UNKNOWN",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if name == "Randy Orton" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "FALSE",
        "legend_returning": "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE",
        "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED" if (entry or is_winner or elim_by) else "PROBABLE",
        "source_ids": "S070",
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
# wrestler_id in this database; opponents without one are still recorded
# as free text in the 'opponents' field).
# ---------------------------------------------------------------------------
other_matches = [
    ("Gregory Helms", 1, "Kid Kash; Sho Funaki; Nunzio; Jamie Noble; Paul London", "", "Six-Man (Cruiserweight Open Invitational)", "TRUE", "World Cruiserweight Championship", "FALSE", "Win", "TRUE", "", "7:10", "Opener", "S070", "Won the vacant Cruiserweight Championship, pinning Funaki. Billed as 'Gregory Helms' -- reuses this database's existing 'the-hurricane' wrestler_id (same performer, evolved gimmick/name, not a new identity). Not a Rumble entrant this year."),
    ("Nunzio", 1, "Gregory Helms; Kid Kash; Sho Funaki; Jamie Noble; Paul London", "", "Six-Man (Cruiserweight Open Invitational)", "TRUE", "World Cruiserweight Championship", "FALSE", "Loss", "", "", "7:10", "Opener", "S070", "Did not win the vacant Cruiserweight title. Not a Rumble entrant this year."),
    ("Paul London", 1, "Gregory Helms; Kid Kash; Sho Funaki; Nunzio; Jamie Noble", "", "Six-Man (Cruiserweight Open Invitational)", "TRUE", "World Cruiserweight Championship", "FALSE", "Loss", "", "", "7:10", "Opener", "S070", "Did not win the vacant Cruiserweight title. Not a Rumble entrant this year."),
    ("John Cena", 4, "Edge", "", "Singles", "TRUE", "WWE Championship", "FALSE", "Win", "TRUE", "", "14:02", "4th match", "S070", "Regained the WWE Title he had lost three weeks earlier at New Year's Revolution. Not a Rumble entrant this year."),
    ("Edge", 4, "John Cena", "", "Singles", "TRUE", "WWE Championship", "TRUE", "Loss", "", "TRUE", "14:02", "4th match", "S070", "Lost the WWE Title back to Cena. Not a Rumble entrant this year."),
    ("Kurt Angle", 5, "Mark Henry", "", "Singles", "TRUE", "World Heavyweight Championship", "TRUE", "Win", "", "TRUE", "7:00", "Main event", "S070", "Retained the World Heavyweight Championship in the show's main event, which S070 calls 'an awful match.' The Undertaker appeared at the end to challenge for a future title match. Not a Rumble entrant this year."),
    ("Mark Henry", 5, "Kurt Angle", "", "Singles", "TRUE", "World Heavyweight Championship", "FALSE", "Loss", "", "", "7:00", "Main event", "S070", "Lost to Kurt Angle in the main event. Not a Rumble entrant this year."),
    ("John Bradshaw Layfield", 3, "The Boogeyman", "", "Singles", "FALSE", "", "FALSE", "Loss", "", "", "1:45", "3rd match", "S070", "Lost to The Boogeyman in a quick match. Billed as 'JBL' -- reuses this database's existing 'bradshaw' wrestler_id. Not a Rumble entrant this year."),
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
    ("F189", EVENT_ID, "entrants", "*", "entry_number;ring_time;elim_number", "unverified",
     "Like 2002/2004, 2006 has NO Cageside-style timing analysis in Shane's Word doc -- only the Dan Wahlers "
     "narrative, and it is thinner than most other sparse years. Entry order is UNKNOWN for 26 of 30 slots "
     "(only Triple H #1, Rey Mysterio #2, and Bobby Lashley #8 are named), and no ring/survival times or "
     "elim_number values are stated for anyone.",
     "S070", "open", "2026-09-16"),
    ("F190", EVENT_ID, "entrants", "*", "n/a", "unverified",
     "S070's 'Other participants' list, plus the named winner, totals only 29 names against a stated field of "
     "30 -- one slot's occupant is UNKNOWN. entrant_count is kept at 30 (the official record) with only 29 "
     "wrestler rows created this pass; the missing 30th name is left blank rather than guessed. A mirror-image "
     "of 2003's Rosey omission (F166), this time an entire unnamed slot rather than a named-but-uncounted "
     "wrestler.",
     "S070", "open", "2026-09-16"),
    ("F191", EVENT_ID, "eliminations", "the-big-show", "n/a", "needs_human_judgement",
     "S070 states Triple H eliminated both Ric Flair and Big Show 'early on,' yet also credits Big Show "
     "(jointly with Kane) for eliminating Bobby Lashley, who entered at #8. With no exact timestamps this "
     "year, there is no way to determine whether Big Show's elimination of Lashley preceded or followed his "
     "own elimination by Triple H -- both facts are kept as stated rather than treated as a contradiction to "
     "silently resolve.",
     "S070", "open", "2026-09-16"),
    ("F192", EVENT_ID, "eliminations", "shane-mcmahon;shawn-michaels", "eliminator_wrestler_id", "needs_human_judgement",
     "Shane McMahon was never a Rumble entrant this year, yet S070 explicitly states he eliminated Shawn "
     "Michaels 'from behind' while Michaels was distracted by Vince McMahon (who had promised a reward for "
     "eliminating HBK). A new, non-entrant wrestler_id was created for Shane McMahon solely to carry this "
     "elimination credit -- a deliberate exception to this database's usual 'officiated record' convention "
     "(1997 F081, 2000 F126, 2002 F136, 2003 F171), the same reasoning applied to Kurt Angle's 2005 "
     "post-elimination interference against HBK (F184), but distinct in that Shane was never a legal "
     "competitor at all this year, not merely an already-eliminated one.",
     "S070", "open", "2026-09-16"),
    ("F193", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 12 previously-unseen wrestlers this pass (Bobby Lashley, Carlito, Joey Mercury, Road "
     "Warrior Animal, Super Crazy, Trevor Murdoch, Chris Masters, Eugene, Johnny Nitro, Psicosis, Sylvan "
     "Grenier, Shane McMahon) with zero bio data in this pass's source -- names only. Left entirely UNKNOWN, "
     "same pattern as every prior year's equivalent flag.",
     "S070", "open", "2026-09-16"),
    ("F194", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-16"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2006", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2006-01-29", "venue": "American Airlines Arena",
    "city_region": "Miami, Florida", "country": "United States",
    "attendance_official": "", "attendance_reported": 14500,
    "entry_interval_seconds": "UNKNOWN", "entrant_count": 30, "duration_total": "62:12",
    "duration_status": "CONFIRMED",
    "winner_id": "rey-mysterio", "runner_up_id": "randy-orton",
    "final_two_ids": "rey-mysterio;randy-orton",
    "final_three_ids": "hunter-hearst-helmsley;rey-mysterio;randy-orton",
    "final_four_ids": "hunter-hearst-helmsley;rey-mysterio;randy-orton;rob-van-dam",
    "first_entrant_id": "hunter-hearst-helmsley", "second_entrant_id": "rey-mysterio", "final_entrant_id": "UNKNOWN",
    "first_elimination_id": "UNKNOWN", "last_elimination_before_winner_id": "randy-orton",
    "eliminations_count": 29, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": "UNKNOWN",
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Joey Styles and Jerry Lawler (RAW); Michael Cole and Tazz (SmackDown!)",
    "ring_announcer": "UNKNOWN",
    "referees": "Not identified in the source consulted this pass",
    "special_rules": (
        "Uniquely, the Royal Rumble Match was placed in the middle of the card rather than as the main event "
        "or de facto show-closer -- a decision Dan Wahlers' narrative criticizes at length. The final entrant's "
        "identity (#30) is not stated -- see F189/F190."
    ),
    "title_on_the_line": "FALSE",
    "championship_implications": "None in the Rumble match itself, though Gregory Helms won the vacant World Cruiserweight Championship, John Cena regained the WWE Championship from Edge, and Kurt Angle retained the World Heavyweight Championship against Mark Henry in the main event, all on the same card.",
    "winners_reward": "A World Heavyweight Championship opportunity, folded into the ongoing Eddie Guerrero tribute storyline around Mysterio, per S070",
    "historical_significance": (
        "Rey Mysterio's Royal Rumble win, at 62:12, broke Chris Benoit's then-standing 2004 record (61:37) for "
        "longest individual performance in a single Royal Rumble match. S070 calls this 'by far the worst "
        "Royal Rumble since 1999,' criticizing the mid-card placement of the Rumble match and an underwhelming "
        "main event."
    ),
    "notes": (
        "The sparsest entry-timing dataset among this database's sparse years -- only 3 of 30 entry numbers "
        "are known (see F189), and the named participant list is one slot short of the stated 30-man field "
        "(see F190). Eliminator credit covers only 8 of the match's 29 eliminations."
    ),
    "data_quality_status": "PROBABLE", "source_ids": "S070",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2006 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
