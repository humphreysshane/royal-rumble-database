# -*- coding: utf-8 -*-
"""
Builds all rows for the 2000 Royal Rumble -- schema v2.

Sparse like 1994/1996/1998: NO Cageside-style timing analysis exists in
Shane's Word doc for this year -- only the Dan Wahlers narrative history
section, under the "2000 Royal Rumble Stats" Heading-1. No Excel tab either.

SOURCES CONSULTED THIS PASS:
  S046 Dan Wahlers "History of the Royal Rumble" -- 2000 chapter     tier 9

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order is UNKNOWN for 23 of 30 entrants. Explicitly named: D'Lo
    Brown #1, Brian Christopher (Grandmaster Sexay) #2, Rikishi #5, Bob
    Backlund #14, The Rock #24, Big Show #26, Kane #27.
  - No ring/survival times are stated for anyone this year (no Cageside
    section exists).
  - The final stretch IS narrated in useful detail: Rock eliminated Big
    Boss Man and Crash Holly on his way in; Big Show eliminated Test and
    Gangrel; Kane eliminated Val Venis and Prince Albert; in the Final
    Four (Rock, Kane, Big Show, X-Pac), X-Pac eliminated Kane, Big Show
    eliminated X-Pac, and Rock eliminated Big Show for the win.
  - Rikishi is credited with eliminating "seven guys altogether" (a
    CONFIRMED count, but the source names none of the 7 individually) and
    was himself eliminated by an unnamed ~8-man gang-up "halfway through"
    the match -- both left without specific eliminator/eliminated
    wrestler_id assignments rather than guessing. See F125.
  - A MISSED-CALL CONTROVERSY, structurally identical to 1997's Bret Hart/
    Steve Austin case (F081): Big Show dumped Rock over the top rope and
    was ruled the survivor, but "replays would later clearly show that
    Rock's feet hit the floor" before he got back in and eliminated Big
    Show for the actual win. Per the same modeling choice used for 1997,
    NO eliminations.csv row exists for "Big Show eliminates Rock" since it
    was never officiated -- this database represents the officiated match
    record, with the missed call documented here and in events.csv's
    special_rules. See F126.
  - "Viscera" is widely known in general wrestling history to be a later
    ring name used by the same performer (Nelson Frazier Jr.) who wrestled
    as "Mabel" in this database's 1994/1995/1996 builds (wrestler_id
    mabel) -- but S046 does not state that connection directly. Left as a
    separate, new wrestler_id pending a future fact-check pass, the same
    caution already applied to X-Pac/1-2-3 Kid (1999's F118). See F127.
  - Tazz's WWF in-ring debut (defeating Kurt Angle by submission, the
    opening match) is notable trivia mentioned in S046's narrative, but
    NEITHER man is a Rumble entrant this year, and neither has an existing
    wrestler_id in this database yet -- consistent with this database's
    established practice (1996-1999) of only logging other_matches.csv
    rows for wrestlers who already carry a wrestler_id, this match is
    described in prose (historical_significance) rather than given
    structured rows. Both will presumably get proper wrestler_ids once
    either man is an actual Rumble entrant in a later year.
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
EVENT_ID = "RR2000M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S046", "Dan Wahlers, 'History of the Royal Rumble' -- 2000 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Preserved in Shane's original doc; no live URL captured. Gives exact attendance (19,231), full narrative "
     "history (the Triple H/Cactus Jack Street Fight, the Big Show/Rock missed-call finish, Tazz's WWF debut), "
     "and undercard match results. NO Cageside-style timing analysis exists for this year -- see F124."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F124", EVENT_ID, "entrants;eliminations", "*", "entry_number;ring_time;elim_number", "unverified",
     "Like 1994/1996/1998 (F059/F072/F112), 2000 has NO Cageside-style timing analysis in Shane's Word doc -- "
     "only the Dan Wahlers narrative. Entry order is UNKNOWN for 23 of 30 participants (only D'Lo Brown #1, "
     "Brian Christopher #2, Rikishi #5, Bob Backlund #14, The Rock #24, Big Show #26, and Kane #27 are named), "
     "and NO ring/survival times are stated for anyone this year. elim_number is left UNKNOWN throughout -- "
     "only relative elimination CREDIT (who eliminated whom) is known for the narrated final stretch.",
     "S046", "open", "2026-09-16"),
    ("F125", EVENT_ID, "entrants;eliminations", "rikishi", "wrestlers_eliminated_count;eliminated_by_ids", "unverified",
     "Rikishi is credited with eliminating 'seven guys altogether' -- a CONFIRMED count (wrestlers_eliminated_"
     "count=7 on his entrant row) but S046 names none of the 7 individually, so no corresponding eliminations."
     "csv rows were created for them. Rikishi was himself eliminated by an unnamed group of 'about eight guys' "
     "who 'ganged up' on him 'halfway through' the match -- his own eliminated_by_ids is left UNKNOWN rather "
     "than guessing which 8 of the field were involved.",
     "S046", "open", "2026-09-16"),
    ("F126", EVENT_ID, "eliminations", "the-rock;big-show", "elimination_type", "needs_human_judgement",
     "A missed-call controversy structurally identical to 1997's Bret Hart/Steve Austin case (see 1997's "
     "F081). Big Show dumped Rock over the top rope and was ruled the survivor, but 'replays would later "
     "clearly show that Rock's feet hit the floor' before he got back in and eliminated Big Show for the "
     "actual win. Per the same modeling choice used for 1997, NO eliminations.csv row exists for 'Big Show "
     "eliminates Rock' since it was never officiated on-air -- this database represents the officiated match "
     "record (Rock never eliminated, Rock eliminates Big Show for the win) while documenting the missed call "
     "here and in events.csv's special_rules.",
     "S046", "open", "2026-09-16"),
    ("F127", EVENT_ID, "wrestlers", "viscera", "wrestler_id", "needs_human_judgement",
     "Viscera is widely known in general wrestling history to be a later ring name used by the same performer "
     "(Nelson Frazier Jr.) who wrestled as 'Mabel' in this database's 1994/1995/1996 builds (wrestler_id "
     "mabel). S046 does not state that connection directly. Left as a separate, new wrestler_id pending a "
     "future fact-check pass with 2 independent sources -- same caution class as X-Pac/1-2-3 Kid (1999's "
     "F118) and Kama/Bob Holly (1996's F076/F078).",
     "S046", "open", "2026-09-16"),
    ("F128", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 10 previously-unseen wrestlers this pass (Brian Christopher, Christian, Rikishi, "
     "Scott Taylor, Viscera, Chris Jericho, Crash Holly, Prince Albert, Hardcore Holly, Big Show) with zero "
     "bio data in this pass's source -- names only. Left entirely UNKNOWN, same pattern as every prior sparse "
     "year's equivalent flag.",
     "S046", "open", "2026-09-16"),
    ("F129", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-16"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Brian Christopher", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Wrestled as 'Grandmaster Sexay' this event, entering #2. No bio data in this pass's source.", "S046"),
    ("Christian", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in this pass's source.", "S046"),
    ("Rikishi", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #5; eliminated 7 opponents (unnamed individually, see F125) before being gang-eliminated by ~8 wrestlers halfway through the match.", "S046"),
    ("Scott Taylor", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in this pass's source.", "S046"),
    ("Viscera", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Possible identity connection to this database's existing 'mabel' wrestler_id (Nelson Frazier Jr.'s earlier ring name) -- not stated directly by S046, left unmerged. See F127.", "S046"),
    ("Chris Jericho", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Also competed in the same night's I-C Title three-way match. No bio data in this pass's source.", "S046"),
    ("Crash Holly", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Eliminated by The Rock. No bio data in this pass's source.", "S046"),
    ("Prince Albert", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Eliminated by Kane. No bio data in this pass's source.", "S046"),
    ("Hardcore Holly", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Also competed in the same night's I-C Title three-way match. No bio data in this pass's source.", "S046"),
    ("Big Show", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #26 as one of the match's '2nd big star,' eliminating Test and Gangrel before being eliminated by X-Pac, then eliminating X-Pac himself, then eliminated by The Rock for the win amid a missed-call controversy -- see F126.", "S046"),
]

reused = {
    "D'Lo Brown": "d-lo-brown", "Headbanger Mosh": "mosh", "Test": "test",
    "Big Boss Man": "big-boss-man", "Edge": "edge", "Gangrel": "gangrel",
    "The British Bulldog": "british-bulldog", "Bob Backlund": "bob-backlund",
    "Steve Blackman": "steve-blackman", "Chyna": "chyna", "Faarooq": "faarooq",
    "Jesse James": "jesse-james", "Al Snow": "al-snow", "Val Venis": "val-venis",
    "Billy Gunn": "billy-gunn", "Bradshaw": "bradshaw", "Kane": "kane",
    "The Godfather": "the-godfather", "X-Pac": "x-pac", "The Rock": "rocky-maivia",
    # Non-Rumble-entrant reused ids used only in other_matches this year.
    "Hunter Hearst Helmsley": "hunter-hearst-helmsley", "Cactus Jack": "cactus-jack",
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
# ENTRANTS -- 30 named participants; entry order/ring time UNKNOWN except a
# handful of explicitly-named entry numbers.
# ---------------------------------------------------------------------------
all_names = [
    "D'Lo Brown", "Brian Christopher", "Headbanger Mosh", "Christian", "Rikishi", "Test",
    "Big Boss Man", "Edge", "Gangrel", "The British Bulldog", "Bob Backlund", "Scott Taylor",
    "Steve Blackman", "Viscera", "Chris Jericho", "Crash Holly", "Chyna", "Faarooq", "Jesse James",
    "Al Snow", "Val Venis", "Prince Albert", "Hardcore Holly", "Billy Gunn", "Big Show", "Bradshaw",
    "Kane", "The Godfather", "X-Pac", "The Rock",
]
assert len(all_names) == 30

ENTRY_NUMBERS = {
    "D'Lo Brown": 1, "Brian Christopher": 2, "Rikishi": 5, "Bob Backlund": 14,
    "The Rock": 24, "Big Show": 26, "Kane": 27,
}
# name -> (list of eliminator names, data_quality_status)
KNOWN_ELIMINATORS = {
    "Big Boss Man": (["The Rock"], "CONFIRMED"),
    "Crash Holly": (["The Rock"], "CONFIRMED"),
    "Test": (["Big Show"], "CONFIRMED"),
    "Gangrel": (["Big Show"], "CONFIRMED"),
    "Val Venis": (["Kane"], "CONFIRMED"),
    "Prince Albert": (["Kane"], "CONFIRMED"),
    "Kane": (["X-Pac"], "CONFIRMED"),
    "X-Pac": (["Big Show"], "CONFIRMED"),
    "Big Show": (["The Rock"], "CONFIRMED"),
}
ELIM_METHOD = {
    "Big Boss Man": "Deposited on the floor by The Rock shortly after his #24 entrance.",
    "Crash Holly": "Deposited on the floor by The Rock shortly after his #24 entrance.",
    "Test": "Gotten rid of by Big Show 'in short order' after his #26 entrance.",
    "Gangrel": "Gotten rid of by Big Show 'in short order' after his #26 entrance.",
    "Val Venis": "Gotten rid of by Kane after his #27 entrance.",
    "Prince Albert": "Gotten rid of by Kane after his #27 entrance.",
    "Kane": "Spin-kicked out by X-Pac in the Final Four, after X-Pac snuck back in unnoticed from an earlier Rock elimination attempt.",
    "X-Pac": "One-handed out of the ring by Big Show in the Final Four.",
    "Big Show": "The winning elimination -- Rock got back in the ring and eliminated Big Show after Show (wrongly, per replay) believed he had already eliminated Rock -- see F126.",
}

WRESTLED_EARLIER = {"Chris Jericho", "Chyna", "Hardcore Holly", "Jesse James", "Billy Gunn", "Faarooq", "Bradshaw"}

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "The Rock")
    entry = ENTRY_NUMBERS.get(name, "")
    elim_by, dq = KNOWN_ELIMINATORS.get(name, ([], ""))

    note = ""
    if name == "Rikishi":
        note = "Eliminated 7 opponents altogether (CONFIRMED count, individuals unnamed -- see F125); eliminated by an unnamed ~8-man gang-up halfway through the match."
    elif name == "Brian Christopher":
        note = "Wrestled as 'Grandmaster Sexay' this event."
    elif name == "Viscera":
        note = "Possible identity connection to this database's existing 'mabel' wrestler_id -- see F127."
    elif name == "Big Show":
        note = "Eliminated Test and Gangrel; eliminated X-Pac; eliminated (officially) by The Rock for the win amid a missed-call controversy -- see F126."
    elif name == "The Rock":
        note = "Winner. Per S046, Big Show's earlier attempt to eliminate Rock should have counted on replay (feet touched the floor) but was not called -- see F126."
    elif name in WRESTLED_EARLIER:
        note = "Also wrestled earlier on the same card -- see other_matches.csv."

    for eliminator in elim_by:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": "",
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
            "assisting_wrestler_ids": "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": ENTRY_NUMBERS.get(eliminator, ""),
            "elimination_clock_time": "", "elimination_clock_seconds": "",
            "elimination_type": "over_top_rope",
            "elimination_method": ELIM_METHOD.get(name, "UNKNOWN"),
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "TRUE", "is_shared": "FALSE",
            "is_accidental": "FALSE", "is_self_elimination": "FALSE",
            "is_storyline_related": "UNKNOWN", "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE", "simultaneous_group_id": "",
            "data_quality_status": dq,
            "source_ids": "S046",
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
        "tag_team_name": "New Age Outlaws" if name in ("Jesse James", "Billy Gunn") else ("The Acolytes" if name in ("Faarooq", "Bradshaw") else ""),
        "faction_stable": "",
        "current_champion_title": "WWF Intercontinental Championship" if name in ("Chris Jericho",) else ("WWF World Tag Team Championship" if name in ("Jesse James", "Billy Gunn") else ""),
        "championship_level": "",
        "championship_partner": "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        "title_defended_same_card": "TRUE" if name in ("Jesse James", "Billy Gunn") else "FALSE",
        "title_lost_same_card": "FALSE",
        "elim_number": "", "elim_number_status": "N/A" if is_winner else "UNKNOWN",
        "eliminated_by_ids": ";".join(wrestler_ids[e] for e in elim_by),
        "elimination_clock_time": "", "elimination_clock_seconds": "",
        "ring_time": "", "ring_time_seconds": "",
        "ring_time_status": "UNKNOWN",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": 7 if name == "Rikishi" else "",
        "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if wid == "big-show" else "FALSE",
        "is_final_two": "TRUE" if wid in ("rocky-maivia", "big-show") else "UNKNOWN",
        "is_final_three": "UNKNOWN",
        "is_final_four": "TRUE" if wid in ("rocky-maivia", "big-show", "kane", "x-pac") else "UNKNOWN",
        "surprise_entrant": "FALSE", "legend_returning": "TRUE" if name == "Bob Backlund" else "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE",
        "wrestled_earlier_on_card": "TRUE" if name in WRESTLED_EARLIER else "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED" if (entry or is_winner or elim_by) else "PROBABLE",
        "source_ids": "S046",
        "notes": note,
    }
    entrant_rows.append(er)

# Fill in each eliminator's wrestlers_eliminated_ids / counts from elim_rows
# (in addition to Rikishi's separately-stated aggregate count of 7).
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
# wrestler_id in this database).
# ---------------------------------------------------------------------------
other_matches = [
    ("Chris Jericho", 4, "Chyna, Hardcore Holly", "", "Three-Way", "TRUE", "Intercontinental Championship", "FALSE", "Win", "TRUE", "", "7:30", "4th match", "S046", "Pinned Chyna to win the I-C Title (three-way, also involving Hardcore Holly). Also competed in the Rumble match this same night."),
    ("Chyna", 4, "Chris Jericho, Hardcore Holly", "", "Three-Way", "TRUE", "Intercontinental Championship", "TRUE", "Loss", "", "TRUE", "7:30", "4th match", "S046", "Pinned by Jericho, losing the I-C Title. Also competed in the Rumble match this same night."),
    ("Hardcore Holly", 4, "Chris Jericho, Chyna", "", "Three-Way", "TRUE", "Intercontinental Championship", "FALSE", "Loss", "", "", "7:30", "4th match", "S046", "Did not factor in the pinfall (Jericho pinned Chyna). Also competed in the Rumble match this same night."),
    ("Jesse James", 5, "Faarooq, Bradshaw", "Billy Gunn", "Tag Team", "TRUE", "World Tag Team Championship", "TRUE", "Win", "", "", "2:35", "5th match", "S046", "Gunn pinned Bradshaw to retain the tag titles for the New Age Outlaws. Also competed in the Rumble match this same night."),
    ("Billy Gunn", 5, "Faarooq, Bradshaw", "Jesse James", "Tag Team", "TRUE", "World Tag Team Championship", "TRUE", "Win", "", "", "2:35", "5th match", "S046", "Pinned Bradshaw to retain the tag titles for the New Age Outlaws. Also competed in the Rumble match this same night."),
    ("Faarooq", 5, "Jesse James, Billy Gunn", "Bradshaw", "Tag Team", "TRUE", "World Tag Team Championship", "FALSE", "Loss", "", "TRUE", "2:35", "5th match", "S046", "The Acolytes lost the tag title match (Bradshaw pinned). Also competed in the Rumble match this same night."),
    ("Bradshaw", 5, "Jesse James, Billy Gunn", "Faarooq", "Tag Team", "TRUE", "World Tag Team Championship", "FALSE", "Loss", "", "TRUE", "2:35", "5th match", "S046", "Pinned by Gunn, The Acolytes losing the tag title match. Also competed in the Rumble match this same night."),
    ("Hunter Hearst Helmsley", 6, "Cactus Jack", "", "Street Fight", "TRUE", "World Heavyweight Championship", "TRUE", "Win", "", "", "26:48", "6th match", "S046", "Defeated Cactus Jack (Mick Foley) to retain the World Heavyweight Championship in a brutal Street Fight widely regarded as one of the best matches of 2000. Not a Rumble entrant this year."),
    ("Cactus Jack", 6, "Hunter Hearst Helmsley", "", "Street Fight", "TRUE", "World Heavyweight Championship", "FALSE", "Loss", "", "", "26:48", "6th match", "S046", "Lost to Triple H (Pedigreed onto thumbtacks) in a brutal Street Fight widely regarded as one of the best matches of 2000. Not a Rumble entrant this year."),
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
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2000", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2000-01-23", "venue": "Madison Square Garden",
    "city_region": "New York City, New York", "country": "United States",
    "attendance_official": "", "attendance_reported": 19231,
    "entry_interval_seconds": "UNKNOWN", "entrant_count": 30, "duration_total": "51:48",
    "duration_status": "CONFIRMED",
    "winner_id": "rocky-maivia", "runner_up_id": "big-show",
    "final_two_ids": "rocky-maivia;big-show", "final_three_ids": "UNKNOWN",
    "final_four_ids": "rocky-maivia;kane;big-show;x-pac",
    "first_entrant_id": "d-lo-brown", "second_entrant_id": "brian-christopher", "final_entrant_id": "UNKNOWN",
    "first_elimination_id": "UNKNOWN", "last_elimination_before_winner_id": "big-show",
    "eliminations_count": "UNKNOWN", "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": 1,
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Jim Ross, Jerry Lawler", "ring_announcer": "UNKNOWN",
    "referees": "Not identified in the source consulted this pass",
    "special_rules": (
        "A missed-call controversy decided the finish -- Big Show dumped Rock over the top rope and was "
        "believed to have won, but replays showed Rock's feet had touched the floor before Rock got back in "
        "and eliminated Big Show for the actual win. No eliminations.csv row exists for the missed 'Big Show "
        "eliminates Rock' moment since it was never officiated -- see F126, mirroring the same treatment given "
        "to 1997's Bret Hart/Steve Austin missed call (F081)."
    ),
    "title_on_the_line": "FALSE",
    "championship_implications": "None in the Rumble match itself, though Chris Jericho won the WWF Intercontinental Championship from Chyna in a three-way match also involving Hardcore Holly, the New Age Outlaws (Jesse James and Billy Gunn) retained the World Tag Team Championship against The Acolytes (Faarooq and Bradshaw), and Hunter Hearst Helmsley (Triple H) retained the World Heavyweight Championship against Cactus Jack (Mick Foley) in a brutal Street Fight, all earlier on the same card.",
    "winners_reward": "A WWF Championship match against Triple H, but Vince McMahon instead booked a Four-Way Match at WrestleMania 2000 also involving Big Show and Mick Foley, allowing Triple H to retain and leave as champion, per S046",
    "historical_significance": (
        "The Rock's first Royal Rumble win, with Steve Austin sidelined after neck surgery. Triple H vs. Cactus "
        "Jack (Mick Foley) in a Street Fight on the same card is widely regarded as one of the best matches of "
        "2000, featuring a piledriver through a table, a bag of thumbtacks, and a Pedigree onto the tacks for "
        "the finish -- one of the most brutal matches of Foley's career. The undercard also featured Tazz's WWF "
        "in-ring debut, defeating Kurt Angle (also in his first WWF match) by submission via the Tazmission -- "
        "neither man is a Rumble entrant this year, per S046."
    ),
    "notes": (
        "Sparse year -- only 7 of 30 entrants (D'Lo Brown #1, Brian Christopher #2, Rikishi #5, Bob Backlund "
        "#14, The Rock #24, Big Show #26, Kane #27) have a confirmed entry number, and no ring/survival times "
        "are stated for anyone -- see F124. Rikishi's 7 eliminations and his own gang-elimination by ~8 "
        "wrestlers are both credited only as unnamed aggregate counts -- see F125."
    ),
    "data_quality_status": "PROBABLE", "source_ids": "S046",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2000 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
