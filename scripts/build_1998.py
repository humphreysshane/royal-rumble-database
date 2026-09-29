# -*- coding: utf-8 -*-
"""
Builds all rows for the 1998 Royal Rumble -- schema v2.

Sparse like 1994/1996: NO Cageside-style timing analysis exists in Shane's
Word doc for this year -- only the Dan Wahlers narrative history section,
under the "1998 Royal Rumble Stats" Heading-1. No Excel tab either.

SOURCES CONSULTED THIS PASS:
  S043 Dan Wahlers "History of the Royal Rumble" -- 1998 chapter     tier 9

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order is UNKNOWN for most of the 30 entrants. Explicitly named:
    Cactus Jack #1, Chainsaw Charlie #2, The Rock #4, Honky Tonk Man #19
    (a surprise replacement for an injured Triple H), Steve Austin #24,
    Dude Love #28. Mankind's re-entry (Mick Foley's 2nd of 3 appearances,
    see below) is only placed "a few spots later" than #2 -- no exact
    number given, left UNKNOWN.
  - The final sequence is narrated in detail (Austin's rampage through the
    late-entry "trash" -- Marc Mero, an unspecified DOA member, Dude Love,
    Headbanger Thrasher, Brian Lee, Savio Vega -- then the Austin/Rock
    finish), giving several CONFIRMED/PROBABLE elimination credits, the
    richest detail available for this otherwise sparse year.
  - MICK FOLEY TRIPLE-PERSONA CASE (new structural situation -- see F111):
    Foley wrestled this match three separate times under three different
    gimmicks -- Cactus Jack (#1, eliminated by Chainsaw Charlie/Terry
    Funk), Mankind (re-entered "a few spots later," eliminated Chainsaw
    Charlie, then was eliminated by Goldust), and Dude Love (#28, one of
    the "trash" Austin cleared near the end). This is well-established
    wrestling history -- WWE's own official record treats this as three
    separate Rumble entries, not one wrestler entering once. Modeled here
    as THREE separate entrant rows: a new wrestler_id "cactus-jack", the
    EXISTING "mankind" id (reused -- Foley already has this id from his
    1996/1997 Mankind appearances), and a new wrestler_id "dude-love".
    This deliberately mirrors this database's existing convention of
    giving a distinct gimmick its own wrestler_id when the event's own
    official record counts it as a separate entrant (the precedent used
    for Fake Diesel/Fake Razor Ramon, though those involved different
    real people) -- here the same real person (Michael Francis Foley)
    gets three ids because WWE's own record, and Shane's source, both
    treat this as three distinct entries in the same match. See F111.
  - TRIPLE H'S NON-STANDARD PARTICIPATION (new structural situation -- see
    F113): Triple H (Hunter Hearst Helmsley) was injured (knee) and did
    NOT take his own entry -- his #19 slot went to Honky Tonk Man instead.
    He nonetheless appears in the official Match Results participant list
    because he showed up on crutches mid-match and clobbered Owen Hart
    with one, eliminating him -- interference credit without ever taking
    a numbered entry. Modeled as an entrant row with entry_number blank/
    N/A (not a curtain entrance) but full elimination credit for Owen
    Hart, flagged as a unique entry mechanism.
  - "Kama Mustafa" (Charles Wright's 1998 DOA-affiliated gimmick) reuses
    the existing wrestler_id "kama" (same performer, 1996's Kama), per
    this database's forward-looking-name convention. "Chainsaw Charlie"
    reuses "terry-funk" (his 1997 debut id) for the same reason. "The
    Rock" reuses "rocky-maivia" (established 1997, per that year's
    forward-looking-name decision). "Farooq"/"Phinneus Godwinn"/"Mark
    Mero" are treated as the same spelling-variant typos of Faarooq/
    Phineas Godwinn/Marc Mero already in this database, reusing those ids.
  - The official Match Results participant list names only 29 people
    (Steve Austin the winner, plus 28 others). A 30th, "Brian Lee" (a DOA
    member, per the narrative prose "Brian Lee of DOA"), is named only in
    the narrative and is absent from the official list -- added here as
    the 30th field member, flagged as narrative-only sourcing (see F115),
    the same treatment given to similar single-source-only participants
    in prior years.
  - One DOA member is credited only generically ("one of the members of
    DOA") as eliminated by Austin -- the source does not say whether this
    was Chainz or Eight-Ball. Left OUT of eliminations.csv entirely rather
    than guessing which one -- see F114.
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
EVENT_ID = "RR1998M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S043", "Dan Wahlers, 'History of the Royal Rumble' -- 1998 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Preserved in Shane's original doc; no live URL captured. Gives exact attendance (18,542), full narrative "
     "history (Foley's 3-persona run, Honky Tonk Man's surprise entry, Triple H's crutch interference, the "
     "Austin/Rock finish, the Michaels/Undertaker Casket Match closing angle with Kane), and undercard match "
     "results. NO Cageside-style timing analysis exists for this year -- see F112."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F111", EVENT_ID, "wrestlers;entrants", "cactus-jack;mankind;dude-love", "wrestler_id", "needs_human_judgement",
     "Mick Foley (real name Michael Francis Foley) wrestled this match three separate times under three "
     "different gimmicks -- Cactus Jack (#1), Mankind (re-entered 'a few spots later' than #2, existing "
     "wrestler_id reused from his 1996/1997 Mankind appearances), and Dude Love (#28). Modeled as THREE "
     "separate entrant rows / wrestler_ids rather than one, matching WWE's own official Rumble record (which "
     "counts this as 3 distinct entries) and this database's existing convention of giving a distinct in-story "
     "gimmick its own id when the event's official record treats it as a separate entrant. Flagged for human "
     "review since it is a genuinely novel case (same real person, one match, three personas) rather than a "
     "repeat of the Fake Diesel/Fake Razor Ramon precedent (different real people).",
     "S043", "open", "2026-09-16"),
    ("F112", EVENT_ID, "entrants;eliminations", "*", "entry_number;ring_time;elim_number", "unverified",
     "Like 1994/1996 (F059/F072), 1998 has NO Cageside-style timing analysis in Shane's Word doc -- only the "
     "Dan Wahlers narrative. Entry order is UNKNOWN for 24 of 30 participants (only Cactus Jack #1, Chainsaw "
     "Charlie #2, The Rock #4, Honky Tonk Man #19, Steve Austin #24, and Dude Love #28 are named), and NO ring/"
     "survival times are stated for anyone this year. Elimination order/credits are UNKNOWN except for the "
     "specific narrated sequence (Cactus Jack, Chainsaw Charlie, Mankind, Owen Hart, and Austin's late rampage "
     "through Mero/Thrasher/Brian Lee/Savio Vega/Dude Love, then the Austin/Rock finish).",
     "S043", "open", "2026-09-16"),
    ("F113", EVENT_ID, "entrants", "hunter-hearst-helmsley", "entry_number", "needs_human_judgement",
     "Triple H (Hunter Hearst Helmsley) was injured (knee) and did not take his own entry -- his announced #19 "
     "slot went to Honky Tonk Man as a replacement. He nonetheless appears in the official Match Results "
     "participant list because he later showed up on crutches and eliminated Owen Hart with one, earning "
     "elimination credit without ever taking a numbered curtain entrance. entry_number left blank/N/A rather "
     "than assigning #19 (which belongs to his replacement) or inventing a number -- a unique entry mechanism "
     "not seen in any prior year of this database.",
     "S043", "open", "2026-09-16"),
    ("F114", EVENT_ID, "eliminations", "chainz;eight-ball", "eliminator_wrestler_id", "unverified",
     "S043 credits Steve Austin with eliminating 'one of the members of DOA' during his late rampage, without "
     "naming which one (Chainz or Eight-Ball). No elimination row was created for either wrestler rather than "
     "guessing which one Austin actually eliminated -- per this project's rule against inventing specifics not "
     "in the source. Both remain in entrants.csv with elim_number/eliminated_by_ids UNKNOWN.",
     "S043", "open", "2026-09-16"),
    ("F115", EVENT_ID, "entrants", "brian-lee", "*", "unverified",
     "The official Match Results participant list names only 29 of the expected 30 Rumble entrants (Steve "
     "Austin plus 28 others). A 30th, Brian Lee (a DOA member, real name of the wrestler generally known as "
     "'Skull'), is named only in the narrative prose ('Brian Lee of DOA') and is absent from the official list "
     "-- added here as the 30th field member on narrative-only sourcing, the same treatment given to similar "
     "single-source participants in prior years' builds.",
     "S043", "open", "2026-09-16"),
    ("F116", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 14 previously-unseen wrestlers this pass (Cactus Jack, Steve Blackman, Bradshaw, Tom "
     "Brandi, D-Lo Brown, Chainz, Eight-Ball, Mark Henry, Kurrgan, Dude Love, Mosh, Ken Shamrock, Thrasher, "
     "Brian Lee) with zero bio data in this pass's source -- names only. Left entirely UNKNOWN, same pattern "
     "as every prior sparse year's equivalent flag.",
     "S043", "open", "2026-09-16"),
    ("F117", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-16"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Cactus Jack", "Michael Francis Foley", "PROBABLE", "M", "1965-06-07", "PROBABLE", "", "Bloomington, Indiana, U.S.", "PROBABLE", "", "", "", "", "",
     "One of three Mick Foley personas entered in this match (with Mankind, reused id, and Dude Love) -- see F111. Eliminated by Chainsaw Charlie (Terry Funk) at #1. Bio matches the existing 'mankind' wrestler row (same performer).", "S022;S043"),
    ("Steve Blackman", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in this pass's source.", "S043"),
    ("Bradshaw", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in this pass's source.", "S043"),
    ("Tom Brandi", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in this pass's source.", "S043"),
    ("D-Lo Brown", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in this pass's source.", "S043"),
    ("Chainz", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Member of the Disciples of Apocalypse (DOA). Austin eliminated 'one of the members of DOA' late in the match, but S043 does not specify whether it was Chainz or Eight-Ball -- see F114.", "S043"),
    ("Eight-Ball", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Member of the Disciples of Apocalypse (DOA). Austin eliminated 'one of the members of DOA' late in the match, but S043 does not specify whether it was Chainz or Eight-Ball -- see F114.", "S043"),
    ("Mark Henry", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in this pass's source.", "S043"),
    ("Kurrgan", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in this pass's source.", "S043"),
    ("Dude Love", "Michael Francis Foley", "PROBABLE", "M", "1965-06-07", "PROBABLE", "", "Bloomington, Indiana, U.S.", "PROBABLE", "", "", "", "", "",
     "Third of three Mick Foley personas entered in this match (with Cactus Jack and Mankind, reused id) -- see F111. Entered #28; per S043's context appears to have been eliminated by Steve Austin during his late rampage (PROBABLE, contextually implied rather than explicitly stated -- see eliminations.csv note). Bio matches the existing 'mankind' wrestler row (same performer).", "S022;S043"),
    ("Mosh", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Of the Headbangers tag team. No bio data in this pass's source.", "S043"),
    ("Ken Shamrock", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Also wrestled earlier on the card, losing the I-C Title match to The Rock by DQ. No bio data in this pass's source.", "S043"),
    ("Thrasher", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Of the Headbangers tag team ('Headbanger Thrasher' per S043). Eliminated by Steve Austin late in the match.", "S043"),
    ("Brian Lee", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Member of the Disciples of Apocalypse (DOA). Named only in S043's narrative, absent from the official Match Results participant list -- see F115. Eliminated by Steve Austin late in the match.", "S043"),
]

reused = {
    "Chainsaw Charlie": "terry-funk", "The Rock": "rocky-maivia", "Mankind": "mankind",
    "Honky Tonk Man": "the-honky-tonk-man", "Steve Austin": "steve-austin", "Goldust": "goldust",
    "Mark Mero": "marc-mero", "Owen Hart": "owen-hart", "Hunter Hearst Helmsley": "hunter-hearst-helmsley",
    "Savio Vega": "savio-vega", "Henry Godwinn": "henry-godwinn", "Phinneus Godwinn": "phineas-godwinn",
    "Farooq": "faarooq", "Jeff Jarrett": "jeff-jarrett", "Ahmed Johnson": "ahmed-johnson",
    "Kama Mustafa": "kama", "Vader": "vader",
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
    "Cactus Jack", "Chainsaw Charlie", "Steve Blackman", "The Rock", "Bradshaw", "Tom Brandi",
    "D-Lo Brown", "Chainz", "Eight-Ball", "Farooq", "Henry Godwinn", "Phinneus Godwinn", "Goldust",
    "Owen Hart", "Mark Henry", "Hunter Hearst Helmsley", "Honky Tonk Man", "Jeff Jarrett",
    "Ahmed Johnson", "Kurrgan", "Dude Love", "Mankind", "Mark Mero", "Mosh", "Kama Mustafa",
    "Ken Shamrock", "Thrasher", "Savio Vega", "Steve Austin", "Brian Lee",
]
assert len(all_names) == 30

ENTRY_NUMBERS = {
    "Cactus Jack": 1, "Chainsaw Charlie": 2, "The Rock": 4, "Honky Tonk Man": 19,
    "Steve Austin": 24, "Dude Love": 28,
}
# name -> (list of eliminator names, simultaneous_group_id)
KNOWN_ELIMINATORS = {
    "Cactus Jack": (["Chainsaw Charlie"], ""),
    "Chainsaw Charlie": (["Mankind"], ""),
    "Mankind": (["Goldust"], ""),
    "Owen Hart": (["Hunter Hearst Helmsley"], ""),
    "Mark Mero": (["Steve Austin"], ""),
    "Thrasher": (["Steve Austin"], ""),
    "Brian Lee": (["Steve Austin"], ""),
    "Savio Vega": (["Steve Austin"], ""),
    "Dude Love": (["Steve Austin"], ""),
    "The Rock": (["Steve Austin"], ""),
}
# name -> (elimination_method text, data_quality_status, elimination_type)
ELIM_DETAIL = {
    "Cactus Jack": ("Battered with chairshots by Terry Funk/Chainsaw Charlie early in the match.", "PROBABLE", "over_top_rope"),
    "Chainsaw Charlie": ("Eliminated by Mick Foley's returning Mankind persona, 'right after' Mankind's re-entry.", "CONFIRMED", "over_top_rope"),
    "Mankind": ("Thrown out by Goldust.", "CONFIRMED", "over_top_rope"),
    "Owen Hart": ("Clobbered with a crutch by the injured, non-entrant Triple H, who was not an official numbered entrant this year -- see F113.", "CONFIRMED", "over_top_rope"),
    "Mark Mero": ("Tossed out by Steve Austin during his post-entry rampage.", "CONFIRMED", "over_top_rope"),
    "Thrasher": ("Sent out by Steve Austin.", "CONFIRMED", "over_top_rope"),
    "Brian Lee": ("Sent out by Steve Austin.", "CONFIRMED", "over_top_rope"),
    "Savio Vega": ("Sent out by Steve Austin.", "CONFIRMED", "over_top_rope"),
    "Dude Love": ("Contextually implied to have been eliminated by Austin during the same rampage described immediately after Dude Love's #28 entry ('Austin continued cleaning trash from the ring') -- not explicitly stated as an Austin elimination, so kept PROBABLE/DERIVED rather than CONFIRMED.", "PROBABLE", "over_top_rope"),
    "The Rock": ("Winning elimination -- Stone Cold Stunner followed by a clothesline over the top rope.", "CONFIRMED", "over_top_rope"),
}

WRESTLED_EARLIER = {"Goldust", "The Rock", "Ken Shamrock"}  # same-card undercard appearances -- see other_matches

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Steve Austin")
    entry = ENTRY_NUMBERS.get(name, "")
    elim_by, sim_group = KNOWN_ELIMINATORS.get(name, ([], ""))

    note = ""
    if name == "Mankind":
        note = "Mick Foley's 2nd of 3 personas in this match (with Cactus Jack and Dude Love) -- see F111. Entered 'a few spots later' than #2 (Chainsaw Charlie), no exact entry number stated."
    elif name == "Hunter Hearst Helmsley":
        note = "Injured (knee); did not take his own entry -- his announced #19 slot went to Honky Tonk Man instead. Appears in the official participant list solely because he later interfered on crutches and eliminated Owen Hart -- see F113. entry_number intentionally left blank."
    elif name == "Honky Tonk Man":
        note = "Surprise entrant at #19, replacing the injured Hunter Hearst Helmsley."
    elif name == "Brian Lee":
        note = "Named only in S043's narrative ('Brian Lee of DOA'), absent from the official Match Results participant list -- see F115."
    elif name in ("Chainz", "Eight-Ball"):
        note = "Austin eliminated 'one of the members of DOA' late in the match; S043 does not specify which -- see F114."
    elif name == "Dude Love":
        note = "Mick Foley's 3rd of 3 personas in this match (with Cactus Jack and Mankind, reused id) -- see F111 and eliminations.csv note."
    elif name == "Cactus Jack":
        note = "Mick Foley's 1st of 3 personas in this match (with Mankind, reused id, and Dude Love) -- see F111."
    elif name in WRESTLED_EARLIER:
        note = "Also wrestled earlier on the same card -- see other_matches.csv."

    for eliminator in elim_by:
        method, dq, etype = ELIM_DETAIL.get(name, ("UNKNOWN", "PROBABLE", "over_top_rope"))
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": "",
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
            "assisting_wrestler_ids": "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": ENTRY_NUMBERS.get(eliminator, ""),
            "elimination_clock_time": "", "elimination_clock_seconds": "",
            "elimination_type": etype,
            "elimination_method": method,
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "TRUE", "is_shared": "FALSE",
            "is_accidental": "FALSE", "is_self_elimination": "FALSE",
            "is_storyline_related": "TRUE" if name == "Owen Hart" else "UNKNOWN",
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE", "simultaneous_group_id": sim_group,
            "data_quality_status": dq,
            "source_ids": "S043",
            "notes": "",
        })

    er = {
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": ("N/A" if name == "Hunter Hearst Helmsley" else ("CONFIRMED" if entry else "UNKNOWN")),
        "ring_name_at_time": name, "name_displayed_at_event": name,
        "prior_rumble_appearances_count": "", "rumble_appearance_no": "",
        "is_first_rumble_appearance": "", "previous_rumble_year": "",
        "previous_rumble_result": "", "previous_rumble_elimination_no": "",
        "is_rumble_debut": "", "is_company_debut": "UNKNOWN", "company_debut_date": "",
        "is_returning_wrestler": "TRUE" if name == "Honky Tonk Man" else "",
        "absence_length": "",
        "age_at_event": "", "age_status": "UNKNOWN",
        "billed_height_m_at_event": "", "billed_weight_kg_at_event": "", "billed_from_at_event": "",
        "physical_status": "UNKNOWN",
        "alignment": "", "alignment_status": "UNKNOWN",
        "gimmick_at_event": "", "manager_at_event": "",
        "tag_team_name": "",
        "faction_stable": "Disciples of Apocalypse" if name in ("Chainz", "Eight-Ball", "Brian Lee") else ("Headbangers" if name in ("Mosh", "Thrasher") else ""),
        "current_champion_title": "WWF Intercontinental Championship" if name == "The Rock" else "",
        "championship_level": "Intercontinental" if name == "The Rock" else "",
        "championship_partner": "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        "title_defended_same_card": "TRUE" if name == "The Rock" else "FALSE",
        "title_lost_same_card": "FALSE",
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
        "is_runner_up": "TRUE" if wid == "rocky-maivia" else "FALSE",
        "is_final_two": "TRUE" if wid in ("steve-austin", "rocky-maivia") else "UNKNOWN",
        "is_final_three": "UNKNOWN", "is_final_four": "UNKNOWN",
        "surprise_entrant": "TRUE" if name == "Honky Tonk Man" else "FALSE",
        "legend_returning": "FALSE", "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE",
        "wrestled_earlier_on_card": "TRUE" if name in WRESTLED_EARLIER else "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED" if (entry or is_winner or elim_by) else "PROBABLE",
        "source_ids": "S043",
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
# wrestler_id in this database -- Rumble entrants this year or reused ids
# from prior years -- following the pattern already established 1993-1997).
# ---------------------------------------------------------------------------
other_matches = [
    ("Goldust", 1, "Vader", "", "Singles", "FALSE", "", "FALSE", "Loss", "", "", "7:47", "Opener", "S043", "Pinned by Vader. Also competed in the Rumble match this same night."),
    ("Vader", 1, "Goldust", "", "Singles", "FALSE", "", "FALSE", "Win", "", "", "7:47", "Opener", "S043", "Pinned Goldust. Not a Rumble entrant this year."),
    ("The Rock", 3, "Ken Shamrock", "", "Singles", "TRUE", "Intercontinental Championship", "TRUE", "Win", "", "", "10:53", "3rd match", "S043", "Defeated Shamrock by DQ to retain the I-C Title. Also competed in the Rumble match this same night."),
    ("Ken Shamrock", 3, "The Rock", "", "Singles", "TRUE", "Intercontinental Championship", "FALSE", "Loss", "", "", "10:53", "3rd match", "S043", "Lost to The Rock by DQ. Also competed in the Rumble match this same night."),
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
    "event_id": EVENT_ID, "event_name": "Royal Rumble 1998", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "1998-01-18", "venue": "San Jose Arena",
    "city_region": "San Jose, California", "country": "United States",
    "attendance_official": "", "attendance_reported": 18542,
    "entry_interval_seconds": "UNKNOWN", "entrant_count": 30, "duration_total": "55:24",
    "duration_status": "CONFIRMED",
    "winner_id": "steve-austin", "runner_up_id": "rocky-maivia",
    "final_two_ids": "steve-austin;rocky-maivia", "final_three_ids": "UNKNOWN",
    "final_four_ids": "UNKNOWN",
    "first_entrant_id": "cactus-jack", "second_entrant_id": "terry-funk", "final_entrant_id": "UNKNOWN",
    "first_elimination_id": "UNKNOWN", "last_elimination_before_winner_id": "rocky-maivia",
    "eliminations_count": "UNKNOWN", "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": "UNKNOWN",
    "champions_in_field_count": 1, "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Jim Ross, Jerry Lawler", "ring_announcer": "UNKNOWN",
    "referees": "Not identified in the source consulted this pass",
    "special_rules": (
        "Mick Foley wrestled this match three separate times under three different gimmicks -- Cactus Jack "
        "(#1), Mankind (re-entry, existing id reused), and Dude Love (#28) -- modeled as three separate "
        "entrant rows, see F111. Triple H (Hunter Hearst Helmsley) did not take his own entry (injured knee; "
        "his #19 slot went to Honky Tonk Man) but still appears in the official record via a crutch-assisted "
        "interference elimination of Owen Hart -- see F113."
    ),
    "title_on_the_line": "FALSE",
    "championship_implications": "None in the Rumble match itself, though The Rock successfully defended the WWF Intercontinental Championship against Ken Shamrock by DQ earlier on the same card, and Shawn Michaels retained the WWF Championship against The Undertaker in a Casket Match that closed the show.",
    "winners_reward": "A WWF Championship match against Shawn Michaels at WrestleMania XIV, which Steve Austin won to capture his first WWF World Title, per S043",
    "historical_significance": (
        "Steve Austin's Royal Rumble win kicked off the Attitude Era's defining singles push -- he would go on "
        "to defeat Shawn Michaels for his first WWF Championship at WrestleMania XIV. Mick Foley's unique "
        "performance as three separate entrants in the same match (Cactus Jack, Mankind, Dude Love) is one of "
        "the most famous trivia footnotes in Rumble history. Honky Tonk Man made a surprise return, taking the "
        "injured Triple H's spot at #19. The undercard closed with Shawn Michaels defeating The Undertaker in a "
        "Casket Match, in which Kane helped put Undertaker in the casket and then set it on fire to close the "
        "show, per S043 -- Kane's debut-adjacent WWF angle, though he is not himself a Rumble entrant this year."
    ),
    "notes": (
        "Sparse year -- only 6 of 30 entrants (Cactus Jack #1, Chainsaw Charlie #2, The Rock #4, Honky Tonk Man "
        "#19, Steve Austin #24, Dude Love #28) have a confirmed entry number, and no exact ring/survival times "
        "are stated for anyone -- see F112. The official Match Results participant list is short by one name "
        "versus the expected 30; a 30th (Brian Lee) is added from narrative-only sourcing -- see F115."
    ),
    "data_quality_status": "PROBABLE", "source_ids": "S043",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"1998 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
