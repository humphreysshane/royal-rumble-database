# -*- coding: utf-8 -*-
"""
Builds all rows for the 2004 Royal Rumble -- schema v2.

"Narrative-rich sparse" like 2002: NO Cageside-style timing analysis exists
in Shane's Word doc for this year (only the Dan Wahlers narrative section,
under the "2004 Royal Rumble Stats" Heading-1) -- but the narrative is
unusually detailed, naming most of the match's key eliminations and several
explicit entry numbers even without timing data.

SOURCES CONSULTED THIS PASS:
  S067 Dan Wahlers, "History of the Royal Rumble" -- 2004 chapter     tier 9

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order is known for 11 of 30 entrants -- explicitly named: Chris
    Benoit #1, Randy Orton #2, Bradshaw #5, Kane #12, Shelton Benjamin #17,
    Kurt Angle #19, [Test advertised / Mick Foley actual] #21, Big Show #24,
    Chris Jericho #25, John Cena #28, Rob Van Dam #29 (implied, entering
    immediately after Cena and before Goldberg), Bill Goldberg #30. No
    ring/survival times are stated for anyone this year -- see F174. The
    "Participants were:" list in the Match Results paragraph gives all 30
    names but is NOT in entry order (its position-6 name, Bradshaw, is
    explicitly stated elsewhere as entry #5) -- only the explicitly-numbered
    positions above are treated as known.
  - TEST'S NO-SHOW, REPLACED BY MICK FOLEY (new structural situation --
    see F175): Test was advertised for #21 but is shown "lying beat up in
    the back" -- Foley (the storyline attacker) enters in his place to the
    crowd's delight. Both get an entrant row at #21: Test with
    ring_time="00:00" and no elimination logged (mirroring this database's
    established no-show precedent -- Randy Savage 1991, Bastion Booger
    1994, Skull 1998), and Mick Foley as the wrestler who actually entered
    and competed at that slot.
  - MICK FOLEY'S SIMULTANEOUS SELF-ELIMINATION (new structural situation
    -- see F176): Foley's "Cactus Jack clothesline spot" is described as
    eliminating "both guys" -- Foley takes Randy Orton over the top rope
    with him in a mutual/simultaneous spot. Modeled as two elimination
    rows sharing a simultaneous_group_id: Orton eliminated by Foley, and
    Foley self-eliminated (is_self_elimination=TRUE, self_eliminated=TRUE),
    the same convention used for Drew Carey (2001) and Kane (1999).
  - Eliminator credit is rich for a sparse year: Chris Benoit eliminated
    Bradshaw, Rhyno, Matt Morgan, A-Train, and (jointly with Orton) Ernest
    Miller before winning by eliminating Big Show; Booker T eliminated
    Kane; Orton eliminated Shelton Benjamin and (jointly with Benoit)
    Ernest Miller before being eliminated by Foley; Chris Jericho
    eliminated Christian; Bill Goldberg eliminated Charlie Haas, Nunzio,
    and Billy Gunn before being eliminated by Kurt Angle (with an
    uncredited Brock Lesnar F5 run-in as a contributing factor -- see
    F178, mirroring 2002's Triple H/Booker T/RVD situation, F138); The
    Big Show eliminated John Cena, Rob Van Dam, Chris Jericho, and Kurt
    Angle before being eliminated by Chris Benoit for the win.
  - Match duration: the narrative states Benoit won "at 61:37," while the
    Match Results summary line instead states "(1:01:38)" -- a 1-second
    rounding-level discrepancy rather than a substantive conflict. The
    narrative's more specific figure (61:37) is used. See F179.
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
EVENT_ID = "RR2004M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S067", "Dan Wahlers, 'History of the Royal Rumble' -- 2004 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance (17,289), full narrative "
     "history (Chris Benoit's championship-quest storyline, Test's backstage-attack no-show replaced by Mick "
     "Foley, the Foley/Orton double-elimination spot, Goldberg's dominant run before Lesnar's F5 run-in, and "
     "The Big Show's last-stand performance), and undercard match results. NO Cageside-style timing analysis "
     "exists for this year, but eliminator credit and explicit entry numbers are unusually rich for a sparse "
     "year -- see F174."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Randy Orton", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #2. Eliminated Shelton Benjamin and (jointly with Benoit) Ernest Miller before being eliminated by Mick Foley in a simultaneous double-clothesline spot -- see F176.", "S067"),
    ("Rhyno", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Eliminated by Chris Benoit.", "S067"),
    ("Matt Morgan", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Eliminated by Chris Benoit.", "S067"),
    ("Spike Dudley", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No individually-named elimination credit either way this pass.", "S067"),
    ("Renee Dupree", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Billed as 'Renee Dupree' in this database's source doc (more commonly spelled 'Rene Dupree'/'Rene Duprée'). No individually-named elimination credit either way this pass.", "S067"),
    ("Ernest Miller", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Billed as 'The Cat.' Did his dance routine for comic relief, then was eliminated jointly by Chris Benoit and Randy Orton.", "S067"),
    ("Rico", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No individually-named elimination credit either way this pass.", "S067"),
    ("Mick Foley", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #21 under his real name (not a gimmick) as a surprise replacement for the advertised, storyline-attacked Test -- see F175. Eliminated Randy Orton in a simultaneous self-elimination spot ('Cactus Jack clothesline') -- see F176. Same performer as this database's existing mankind/cactus-jack/dude-love wrestler_ids (all separate, gimmick-based ids per this database's established convention -- see the '3 Faces of Foley' 1998 build), not merged with them.", "S067"),
    ("Nunzio", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Per S067, was 'technically in the match' but shown sitting on the floor outside the ring for a stretch before eventually being speared and eliminated by Bill Goldberg.", "S067"),
    ("Bill Goldberg", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #30, his only career Royal Rumble appearance. Spread dominance with spears (Big Show, Billy Gunn, Kurt Angle, Nunzio), eliminating Charlie Haas, Nunzio, and Billy Gunn, before Brock Lesnar's uncredited F5 run-in set up his elimination by Kurt Angle -- see F178.", "S067"),
]

reused = {
    "Chris Benoit": "chris-benoit",
    "Yoshihiro Tajiri": "yoshihiro-tajiri", "Bradshaw": "bradshaw", "Matt Hardy": "matt-hardy",
    "Scott Steiner": "scott-steiner", "Hurricane Helms": "the-hurricane", "Booker T": "booker-t",
    "Kane": "kane", "Rikishi": "rikishi", "A-Train": "a-train", "Shelton Benjamin": "shelton-benjamin",
    "Kurt Angle": "kurt-angle", "Christian": "christian", "The Big Show": "big-show",
    "Chris Jericho": "chris-jericho", "Charlie Haas": "charlie-haas", "Billy Gunn": "billy-gunn",
    "John Cena": "john-cena", "Rob Van Dam": "rob-van-dam", "Test": "test", "Mark Henry": "mark-henry",
    # Non-entrant reused ids used only in other_matches this year.
    "Ric Flair": "ric-flair", "Batista": "batista", "Rey Mysterio": "rey-mysterio",
    "Eddie Guerrero": "eddie-guerrero", "Chavo Guerrero": "chavo-guerrero", "Brock Lesnar": "brock-lesnar",
    "Hardcore Holly": "hardcore-holly", "Hunter Hearst Helmsley": "hunter-hearst-helmsley",
    "Shawn Michaels": "shawn-michaels",
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
# ENTRANTS -- 31 rows (30 official Rumble slots + Test's no-show row sharing
# entry #21 with his replacement, Mick Foley).
# ---------------------------------------------------------------------------
all_names = [
    "Chris Benoit", "Randy Orton", "Mark Henry", "Yoshihiro Tajiri", "Rhyno", "Bradshaw", "Matt Hardy",
    "Scott Steiner", "Matt Morgan", "Hurricane Helms", "Booker T", "Spike Dudley", "Kane", "Rikishi",
    "Renee Dupree", "A-Train", "Shelton Benjamin", "Ernest Miller", "Kurt Angle", "Rico", "Mick Foley",
    "Christian", "Nunzio", "The Big Show", "Chris Jericho", "Charlie Haas", "Billy Gunn", "John Cena",
    "Rob Van Dam", "Bill Goldberg",
]
assert len(all_names) == 30  # + Test's no-show row (sharing entry #21 with Foley) = 31 entrant rows total

ENTRY_NUMBERS = {
    "Chris Benoit": 1, "Randy Orton": 2, "Bradshaw": 5, "Kane": 12, "Shelton Benjamin": 17,
    "Kurt Angle": 19, "Test": 21, "Mick Foley": 21, "The Big Show": 24, "Chris Jericho": 25,
    "John Cena": 28, "Rob Van Dam": 29, "Bill Goldberg": 30,
}
FINAL_FOUR = {"Chris Benoit", "Kurt Angle", "Chris Jericho", "The Big Show"}
FINAL_THREE = {"Chris Benoit", "Kurt Angle", "The Big Show"}
FINAL_TWO = {"Chris Benoit", "The Big Show"}

# name -> (eliminator names, data_quality_status, elimination_method, is_shared, group_id)
KNOWN_ELIMINATORS = {
    "Bradshaw": (["Chris Benoit"], "CONFIRMED", "The first man eliminated, shortly after his #5 entrance.", False, ""),
    "Kane": (["Booker T"], "CONFIRMED", "Kane cleaned house without eliminating anyone, then was tossed by Booker T while distracted by The Undertaker's gong sounding (a false-alarm tease of a surprise Taker appearance).", False, ""),
    "Rhyno": (["Chris Benoit"], "CONFIRMED", "One of several midcarders eliminated by Benoit along the way.", False, ""),
    "Matt Morgan": (["Chris Benoit"], "CONFIRMED", "One of several midcarders eliminated by Benoit along the way.", False, ""),
    "A-Train": (["Chris Benoit"], "CONFIRMED", "One of several midcarders eliminated by Benoit along the way.", False, ""),
    "Shelton Benjamin": (["Randy Orton"], "CONFIRMED", "Made an appearance at #17 but 'didn't last long courtesy of Orton.'", False, ""),
    "Ernest Miller": (["Chris Benoit", "Randy Orton"], "CONFIRMED", "Did his 'Cat' dance routine for comic relief, then was 'rudely shown the exit' by Benoit and Orton together.", True, "miller_benoit_orton"),
    "Randy Orton": (["Mick Foley"], "CONFIRMED", "Worn down by Foley (JR: 'He's not a coward, by god!'), then taken over the top rope together with Foley in the 'Cactus Jack clothesline' spot -- a simultaneous double-elimination. See F176.", False, "foley_orton_double_clothesline"),
    "Mick Foley": (["Mick Foley"], "CONFIRMED", "Self-eliminated in the same 'Cactus Jack clothesline' spot that eliminated Randy Orton -- both men went over the top rope together, with the brawl continuing on the floor. See F176.", False, "foley_orton_double_clothesline"),
    "Christian": (["Chris Jericho"], "CONFIRMED", "Tried to eliminate Jericho from behind (the start of their feud, as the two were 'still technically friends' beforehand) but ended up being the one tossed out by Y2J.", False, ""),
    "Charlie Haas": (["Bill Goldberg"], "CONFIRMED", "One of three eliminated by a dominant Goldberg run (with Nunzio and Billy Gunn).", False, "goldberg_run"),
    "Nunzio": (["Bill Goldberg"], "CONFIRMED", "Per S067, was 'technically in the match' while sitting on the floor outside the ring for a stretch, before being speared and eliminated by Goldberg (one of three, with Charlie Haas and Billy Gunn).", False, "goldberg_run"),
    "Billy Gunn": (["Bill Goldberg"], "CONFIRMED", "One of three eliminated by a dominant Goldberg run (with Charlie Haas and Nunzio).", False, "goldberg_run"),
    "Bill Goldberg": (["Kurt Angle"], "CONFIRMED", "Went for a Jackhammer on Big Show, but Brock Lesnar ran in and hit Goldberg with an F5 (setting up their dubious WrestleMania XX match) -- a stunned Goldberg was then thrown out by Kurt Angle. Lesnar's run-in is a contributing factor, not co-credited, consistent with this database's 'officiated record' convention. See F178.", False, ""),
    "John Cena": (["The Big Show"], "CONFIRMED", "Thrown out by Big Show after a 5-man finisher gang-up (with Benoit, Jericho, RVD, Angle) failed to budge him; Cena landed awkwardly on his knee.", False, ""),
    "Rob Van Dam": (["The Big Show"], "CONFIRMED", "Eliminated by Big Show immediately after Cena, as part of the same dominant stretch.", False, ""),
    "Chris Jericho": (["The Big Show"], "CONFIRMED", "Tossed by Show, did a Shawn Michaels-style 'skin the cat' to get back in, before finally being chokeslammed out.", False, ""),
    "Kurt Angle": (["The Big Show"], "CONFIRMED", "Went for the ankle lock on Show, who stayed in it a long time before kicking Angle out.", False, ""),
    "The Big Show": (["Chris Benoit"], "CONFIRMED", "The winning elimination at 61:37 -- Show had Benoit up for a press slam, Benoit escaped into a front face lock, and slowly pulled Show off his feet and over the top rope.", False, ""),
}

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Chris Benoit")
    entry = ENTRY_NUMBERS.get(name, "")
    elim_by, dq, method, is_shared, group_id = KNOWN_ELIMINATORS.get(name, ([], "", "", False, ""))

    note = ""
    if name == "Chris Benoit":
        note = "Went the distance from #1 to the finish -- the match's central storyline. Eliminated Bradshaw, Rhyno, Matt Morgan, A-Train, and (jointly with Orton) Ernest Miller, then Big Show for the win."
    elif name == "Randy Orton":
        note = "Eliminated Shelton Benjamin and (jointly with Benoit) Ernest Miller, before a simultaneous double-elimination with Mick Foley -- see F176."
    elif name == "Mick Foley":
        note = "Entered #21 as a surprise replacement for the advertised-but-attacked Test -- see F175. Self-eliminated while taking Orton over the top rope in the same spot -- see F176."
    elif name == "Nunzio":
        note = "Per S067, was 'technically in the match' while shown sitting on the floor outside the ring for a stretch -- an unusual, not fully explained situation, left as narrated rather than modeled as a formal near-elimination (no timestamp given). Eventually eliminated by Goldberg."
    elif name == "Bill Goldberg":
        note = "Entered #30, his only career Royal Rumble appearance. Dominant early run (3 eliminations) undone by an uncredited Lesnar F5 run-in before Angle eliminated him -- see F178."
    elif name == "The Big Show":
        note = "Final opponent for Benoit -- eliminated Cena, RVD, Jericho, and Angle before losing the match."
    elif name == "Renee Dupree":
        note = "Billed as 'Renee Dupree' in Shane's source doc (more commonly spelled 'Rene Dupree')."

    for eliminator in elim_by:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": "",
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
            "assisting_wrestler_ids": ";".join(wrestler_ids[e] for e in elim_by if e != eliminator) if is_shared else "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": ENTRY_NUMBERS.get(eliminator, ""),
            "elimination_clock_time": "", "elimination_clock_seconds": "",
            "elimination_type": "self_elimination" if (name == "Mick Foley" and eliminator == "Mick Foley") else "over_top_rope",
            "elimination_method": method,
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "FALSE" if is_shared else "TRUE", "is_shared": "TRUE" if is_shared else "FALSE",
            "is_accidental": "FALSE",
            "is_self_elimination": "TRUE" if (name == "Mick Foley" and eliminator == "Mick Foley") else "FALSE",
            "is_storyline_related": "TRUE" if name in ("Mick Foley", "Randy Orton") and group_id == "foley_orton_double_clothesline" else "UNKNOWN",
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE",
            "simultaneous_group_id": group_id,
            "data_quality_status": dq,
            "source_ids": "S067",
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
        "gimmick_at_event": "The Cat" if name == "Ernest Miller" else "",
        "manager_at_event": "",
        "tag_team_name": "",
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
        "self_eliminated": "TRUE" if name == "Mick Foley" else "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if name == "The Big Show" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "TRUE" if name == "Mick Foley" else "FALSE",
        "legend_returning": "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "TRUE" if name == "Bill Goldberg" else "FALSE",
        "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED" if (entry or is_winner or elim_by) else "PROBABLE",
        "source_ids": "S067",
        "notes": note,
    }
    entrant_rows.append(er)

# Test's no-show row -- advertised #21, replaced by Mick Foley after a
# storyline backstage attack. Same convention as Randy Savage (1991),
# Bastion Booger (1994), and Skull (1998).
test_row = {
    "event_id": EVENT_ID, "wrestler_id": "test", "match_id": EVENT_ID,
    "entry_number": 21, "entry_number_status": "CONFIRMED",
    "ring_name_at_time": "Test", "name_displayed_at_event": "Test",
    "prior_rumble_appearances_count": "", "rumble_appearance_no": "",
    "is_first_rumble_appearance": "", "previous_rumble_year": "",
    "previous_rumble_result": "", "previous_rumble_elimination_no": "",
    "is_rumble_debut": "", "is_company_debut": "UNKNOWN", "company_debut_date": "",
    "is_returning_wrestler": "", "absence_length": "",
    "age_at_event": "", "age_status": "UNKNOWN",
    "billed_height_m_at_event": "", "billed_weight_kg_at_event": "", "billed_from_at_event": "",
    "physical_status": "UNKNOWN",
    "alignment": "", "alignment_status": "UNKNOWN",
    "gimmick_at_event": "", "manager_at_event": "", "tag_team_name": "", "faction_stable": "",
    "current_champion_title": "", "championship_level": "", "championship_partner": "",
    "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
    "title_defended_same_card": "FALSE", "title_lost_same_card": "FALSE",
    "elim_number": "", "elim_number_status": "N/A",
    "eliminated_by_ids": "",
    "elimination_clock_time": "", "elimination_clock_seconds": "",
    "ring_time": "0:00", "ring_time_seconds": 0,
    "ring_time_status": "CONFIRMED",
    "wrestlers_remaining_when_eliminated": "",
    "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
    "solo_eliminations_count": "", "assisted_eliminations_count": "",
    "self_eliminated": "FALSE", "is_winner": "FALSE", "is_runner_up": "FALSE",
    "is_final_two": "FALSE", "is_final_three": "FALSE", "is_final_four": "FALSE",
    "surprise_entrant": "FALSE", "legend_returning": "FALSE", "celebrity_entrant": "FALSE",
    "non_full_time_wrestler": "FALSE", "wrestled_earlier_on_card": "FALSE",
    "was_hof_member_at_time": "FALSE",
    "data_quality_status": "CONFIRMED", "source_ids": "S067",
    "notes": "Advertised for entry #21 but shown 'lying beat up in the back' after a storyline attack -- never entered the ring. Mick Foley, the attacker, entered in his place at the same slot -- see F175. Did not wrestle and was not eliminated (no over-the-rope event occurred).",
}
entrant_rows.append(test_row)

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
    ("Ric Flair", 2, "The Dudley Boys (Bubba Ray and D-Von)", "Batista", "Tag Team (Tables Match)", "TRUE", "World Tag Team Championship", "TRUE", "Win", "", "TRUE", "5:29", "2nd match", "S067", "Retained the tag titles with Batista in a Tables Match. Not a Rumble entrant this year."),
    ("Batista", 2, "The Dudley Boys (Bubba Ray and D-Von)", "Ric Flair", "Tag Team (Tables Match)", "TRUE", "World Tag Team Championship", "TRUE", "Win", "", "TRUE", "5:29", "2nd match", "S067", "Retained the tag titles with Ric Flair in a Tables Match. Not a Rumble entrant this year -- first appears as an entrant in this database's 2003 build."),
    ("Rey Mysterio", 3, "Jamie Noble", "", "Singles", "TRUE", "World Cruiserweight Championship", "TRUE", "Win", "", "TRUE", "3:06", "3rd match", "S067", "Retained the Cruiserweight Championship. Not a Rumble entrant this year."),
    ("Eddie Guerrero", 4, "Chavo Guerrero", "", "Singles", "FALSE", "", "FALSE", "Win", "", "", "8:02", "4th match", "S067", "Pinned Chavo Guerrero Jr. Not a Rumble entrant this year."),
    ("Chavo Guerrero", 4, "Eddie Guerrero", "", "Singles", "FALSE", "", "FALSE", "Loss", "", "", "8:02", "4th match", "S067", "Pinned by Eddie Guerrero. Not a Rumble entrant this year."),
    ("Brock Lesnar", 5, "Hardcore Holly", "", "Singles", "TRUE", "WWE Championship", "TRUE", "Win", "", "TRUE", "6:22", "5th match", "S067", "Retained the WWE Championship over Hardcore Holly, then made an uncredited run-in during the Rumble match to F5 Bill Goldberg -- see F178. Not a Rumble entrant this year."),
    ("Hardcore Holly", 5, "Brock Lesnar", "", "Singles", "TRUE", "WWE Championship", "FALSE", "Loss", "", "", "6:22", "5th match", "S067", "Pinned by Brock Lesnar. Not a Rumble entrant this year."),
    ("Hunter Hearst Helmsley", 6, "Shawn Michaels", "", "Singles (Last Man Standing)", "TRUE", "World Heavyweight Championship", "TRUE", "No Contest", "", "", "23:05", "6th match", "S067", "Fought Shawn Michaels to a double-count-out-style No Contest when neither man could answer the ten count; Triple H retained the title. Not a Rumble entrant this year."),
    ("Shawn Michaels", 6, "Hunter Hearst Helmsley", "", "Singles (Last Man Standing)", "TRUE", "World Heavyweight Championship", "FALSE", "No Contest", "", "", "23:05", "6th match", "S067", "Fought Triple H to a double-count-out-style No Contest when neither man could answer the ten count. Not a Rumble entrant this year -- first appears as an entrant in this database's 2003 build."),
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
    ("F174", EVENT_ID, "entrants", "*", "entry_number;ring_time;elim_number", "unverified",
     "Like 2002, 2004 has NO Cageside-style timing analysis in Shane's Word doc -- only the Dan Wahlers "
     "narrative. Entry order is UNKNOWN for 19 of 30 slots (only Chris Benoit #1, Randy Orton #2, Bradshaw #5, "
     "Kane #12, Shelton Benjamin #17, Kurt Angle #19, Test/Mick Foley #21, Big Show #24, Chris Jericho #25, "
     "John Cena #28, Rob Van Dam #29 [implied], and Bill Goldberg #30 are named), and no ring/survival times or "
     "elim_number values are stated for anyone. The 'Participants were:' list in the Match Results paragraph "
     "gives all 30 names but is NOT in entry order (e.g. its 6th-listed name, Bradshaw, is separately stated "
     "as entry #5) so it was not used to infer entry_number.",
     "S067", "open", "2026-09-16"),
    ("F175", EVENT_ID, "entrants", "test;mick-foley", "entry_number", "needs_human_judgement",
     "Test was advertised for entry #21 but is shown 'lying beat up in the back' after a storyline attack -- he "
     "never entered the ring. Mick Foley, revealed as the attacker, entered in his place to the crowd's "
     "delight. Modeled with two entrant rows sharing entry_number 21: Test (ring_time 00:00, no elimination "
     "logged, the same no-show convention used for Randy Savage 1991, Bastion Booger 1994, and Skull 1998) and "
     "Mick Foley (the wrestler who actually competed at that slot).",
     "S067", "open", "2026-09-16"),
    ("F176", EVENT_ID, "eliminations", "mick-foley;randy-orton", "n/a", "needs_human_judgement",
     "Foley's 'Cactus Jack clothesline spot' is described as eliminating 'both guys' -- Foley and Randy Orton "
     "went over the top rope together in a single simultaneous spot, with the brawl continuing on the floor. "
     "Modeled as two elimination rows sharing simultaneous_group_id 'foley_orton_double_clothesline': Orton "
     "eliminated by Foley, and Foley self-eliminated (is_self_elimination=TRUE, self_eliminated=TRUE) -- the "
     "same self-elimination convention used for Drew Carey (2001) and Kane (1999's self-elimination case).",
     "S067", "open", "2026-09-16"),
    ("F177", EVENT_ID, "eliminations", "ernest-miller", "eliminator_wrestler_id", "needs_human_judgement",
     "Ernest 'The Cat' Miller's elimination is credited jointly to Chris Benoit and Randy Orton together ('was "
     "rudely shown the exit by Benoit and Orton') -- S067 does not attribute it to one or the other "
     "specifically. Modeled as a shared elimination (is_shared=TRUE, both credited) per DEFINITIONS.md's "
     "group-elimination convention, the same approach used for The Hurricane's 2002 elimination (F137).",
     "S067", "open", "2026-09-16"),
    ("F178", EVENT_ID, "eliminations", "bill-goldberg;kurt-angle;brock-lesnar", "eliminator_wrestler_id", "needs_human_judgement",
     "Bill Goldberg went for a Jackhammer on Big Show, but Brock Lesnar ran in and hit Goldberg with an F5 "
     "(building toward their WrestleMania XX match) -- a stunned Goldberg was then thrown out by Kurt Angle. "
     "Kurt Angle is credited as the sole eliminator; Lesnar's F5 run-in is noted as a contributing factor in "
     "the elimination_method text rather than given shared credit, since Lesnar was never a Rumble entrant and "
     "the actual over-the-rope toss is attributed to Angle -- the same reasoning applied to 2002's Triple H/"
     "Booker T/RVD situation (F138).",
     "S067", "open", "2026-09-16"),
    ("F179", EVENT_ID, "events", "RR2004M", "duration_total", "conflicting_sources",
     "The narrative states Chris Benoit won 'at 61:37'; the Match Results summary line instead states "
     "'(1:01:38)' -- a 1-second, rounding-level discrepancy rather than a substantive conflict (61:37 and "
     "1:01:38 differ by exactly 1 second). The narrative's figure (61:37) is used as duration_total.",
     "S067", "open", "2026-09-16"),
    ("F180", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 11 previously-unseen wrestlers this pass (Chris Benoit, Randy Orton, Rhyno, Matt "
     "Morgan, Spike Dudley, Renee Dupree, Ernest Miller, Rico, Mick Foley, Nunzio, Bill Goldberg) with zero "
     "bio data in this pass's source -- names only. Left entirely UNKNOWN, same pattern as every prior year's "
     "equivalent flag.",
     "S067", "open", "2026-09-16"),
    ("F181", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-16"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2004", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2004-01-25", "venue": "Wachovia Center",
    "city_region": "Philadelphia, Pennsylvania", "country": "United States",
    "attendance_official": "", "attendance_reported": 17289,
    "entry_interval_seconds": "UNKNOWN", "entrant_count": 30, "duration_total": "61:37",
    "duration_status": "CONFIRMED",
    "winner_id": "chris-benoit", "runner_up_id": "big-show",
    "final_two_ids": "chris-benoit;big-show",
    "final_three_ids": "chris-benoit;kurt-angle;big-show",
    "final_four_ids": "chris-benoit;kurt-angle;chris-jericho;big-show",
    "first_entrant_id": "chris-benoit", "second_entrant_id": "randy-orton", "final_entrant_id": "bill-goldberg",
    "first_elimination_id": "bradshaw", "last_elimination_before_winner_id": "big-show",
    "eliminations_count": 28, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": 1,
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Jim Ross and Jerry Lawler (RAW); Michael Cole and Tazz (SmackDown!)",
    "ring_announcer": "UNKNOWN",
    "referees": "Not identified in the source consulted this pass",
    "special_rules": (
        "Test was advertised for entry #21 but was shown beaten up backstage; Mick Foley, his storyline "
        "attacker, entered in his place -- see F175. Considered one of the best Royal Rumble matches of "
        "all-time, built almost entirely around Chris Benoit's championship-quest storyline."
    ),
    "title_on_the_line": "FALSE",
    "championship_implications": "None in the Rumble match itself, though Ric Flair and Batista retained the World Tag Team Championship, Rey Mysterio retained the World Cruiserweight Championship, and Brock Lesnar retained the WWE Championship against Hardcore Holly, all earlier on the same card. Triple H and Shawn Michaels also fought to a widely-praised Last Man Standing No Contest for the World Heavyweight Championship.",
    "winners_reward": "A WWE Championship match against Triple H at WrestleMania XX, which Benoit won, per S067",
    "historical_significance": (
        "Chris Benoit's Royal Rumble win, going the distance from #1 to the finish at 61:37, set up his "
        "WrestleMania XX WWE/World Heavyweight Championship win -- a match S067 says finished 2nd in that "
        "year's Wrestling Observer Year-End Awards. Widely regarded as one of the best Royal Rumble matches "
        "ever. Bill Goldberg's only career Royal Rumble appearance. Mick Foley's surprise replacement of an "
        "attacked Test is a unique structural case in this database -- see F175."
    ),
    "notes": (
        "Sparse on timing data like 2002 -- only 12 of 30 slots have a confirmed entry number (11 wrestlers "
        "plus Test's no-show), and no ring/survival times exist for anyone -- see F174. Unusually for a sparse "
        "year, eliminator credit is rich, covering 20 of the match's 28 eliminations."
    ),
    "data_quality_status": "PROBABLE", "source_ids": "S067",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2004 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
