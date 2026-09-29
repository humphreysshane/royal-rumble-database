# -*- coding: utf-8 -*-
"""
Builds all rows for the 2002 Royal Rumble -- schema v2.

"Narrative-rich sparse" like 2002 was previewed in earlier build docstrings:
NO Cageside-style timing analysis exists in Shane's Word doc for this year
(only the Dan Wahlers narrative section, under the "2002 Royal Rumble
Stats" Heading-1) -- but unlike 1994/1996/1998/2000, the narrative itself
is unusually detailed, naming most of the match's key eliminations blow by
blow even without timing data.

SOURCES CONSULTED THIS PASS:
  S049 Dan Wahlers "History of the Royal Rumble" -- 2002 chapter     tier 9

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - Entry order is known for 12 of 30 entrants -- explicitly named: Rikishi
    #1, Goldust #2, The Undertaker #8, Maven #11, Steve Austin #19, Triple
    H #24, Mr. Perfect #25, Kurt Angle #26, Big Show #27, Kane #28, Rob Van
    Dam #29, Booker T #30. No ring/survival times are stated for anyone
    this year (no Cageside section exists) -- see F135.
  - Eliminator credit, by contrast, is RICH for a sparse year -- 14 of the
    match's 29 eliminations have a named eliminator, more than most of
    this database's Cageside-timed years. The Undertaker eliminated 6
    people (Billy Gunn, Al Snow, Rikishi, Goldust, Matt Hardy, and Jeff
    Hardy) before being eliminated himself by Maven -- one of the most
    famous surprise eliminations in Royal Rumble history. Steve Austin
    eliminated Christian, Perry Saturn, Chuck Palumbo, Val Venis, Test,
    and Booker T before being eliminated by Kurt Angle in the Final Four.
    Kane eliminated Big Show; Booker T eliminated Rob Van Dam; Triple H
    eliminated Mr. Perfect and then Kurt Angle for the win.
  - MATT/JEFF HARDY AND AUSTIN'S POST-ELIMINATION INTERFERENCE (new
    situation -- see F136): after Undertaker eliminated Matt and Jeff
    Hardy, S049 says the two "jumped back in" and were "thrown out again"
    by Undertaker -- but this happened only moments before Maven's famous
    upset elimination of Undertaker, so it reads as extracurricular
    brawling/interference by two men no longer legally in the match rather
    than a genuine second Rumble entry. Likewise, after Steve Austin was
    eliminated by Kurt Angle in the Final Four, S049 says Austin "came
    back in, and laid everyone out with a chair" before Mr. Perfect and
    Triple H's finish. Neither situation is modeled as a second entrant
    row or elimination -- both men's OFFICIAL entry/elimination (their
    first and only legitimate appearance) is what's recorded, consistent
    with this database's practice of representing the officiated record
    (see 1997's F081 and 2000's F126 for the same principle applied to
    disputed finishes).
  - THE HURRICANE's elimination is credited ambiguously to both Steve
    Austin and Triple H together ("After getting rid of him, Austin and
    HHH went at each other") -- modeled as a shared elimination per
    DEFINITIONS.md's group-elimination convention. See F137.
  - ROB VAN DAM's elimination: Triple H hit him with a Pedigree ("to stop
    any chance he had at upstaging him"), but S049 credits the actual
    elimination to Booker T immediately after ("Booker T was #30, and
    quickly disposed of the lifeless RVD") -- Booker T is credited as the
    sole eliminator, with HHH's Pedigree noted as a contributing factor
    rather than a shared credit, since the two blows weren't simultaneous
    or jointly described. See F138.
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
EVENT_ID = "RR2002M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S049", "Dan Wahlers, 'History of the Royal Rumble' -- 2002 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-16",
     "Preserved in Shane's original doc; no live URL captured. Gives exact attendance (12,915), full narrative "
     "history (Maven's famous elimination of The Undertaker, the Final Four of Austin/HHH/Angle/Perfect, "
     "Triple H's win at the then-longest Rumble match ever, 69:22), and undercard match results. NO "
     "Cageside-style timing analysis exists for this year, but eliminator credit is unusually rich for a "
     "sparse year -- see F135."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Booker T", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #30 (the final entrant); eliminated Rob Van Dam, then was Stunnered and eliminated by Steve Austin.", "S049"),
    ("Chuck Palumbo", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Eliminated by Steve Austin.", "S049"),
    ("Diamond Dallas Page", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in this pass's source.", "S049"),
    ("Kurt Angle", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #26. Reached the Final Four, eliminating Steve Austin, before being eliminated by Triple H for the win.", "S049"),
    ("Lance Storm", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in this pass's source.", "S049"),
    ("Maven", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #11. Scored one of the most famous surprise eliminations in Royal Rumble history, dropkicking The Undertaker over the top rope.", "S049"),
    ("Rob Van Dam", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #29; hit a Frog Splash on Kurt Angle before being Pedigreed by Triple H and eliminated by Booker T -- see F138.", "S049"),
    ("The Hurricane", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Ran into Steve Austin and Triple H and was eliminated by the two of them together -- see F137.", "S049"),
]

reused = {
    "Al Snow": "al-snow", "Albert": "prince-albert", "Big Show": "big-show", "Billy Gunn": "billy-gunn",
    "Big Bossman": "big-boss-man", "Bradshaw": "bradshaw", "Christian": "christian",
    "Faarooq": "faarooq", "The Godfather": "the-godfather", "Goldust": "goldust",
    "Jeff Hardy": "jeff-hardy", "Kane": "kane", "Matt Hardy": "matt-hardy",
    "Mr. Perfect": "mr-perfect", "Perry Saturn": "perry-saturn", "Rikishi": "rikishi",
    "Scotty Too Hotty": "scotty-2-hotty", "Steve Austin": "steve-austin", "Test": "test",
    "Triple H": "hunter-hearst-helmsley", "The Undertaker": "the-undertaker", "Val Venis": "val-venis",
    # Non-entrant reused ids used only in other_matches this year.
    "William Regal": "william-regal", "Edge": "edge", "Ric Flair": "ric-flair",
    "Vince McMahon": "vince-mcmahon", "Chris Jericho": "chris-jericho", "The Rock": "rocky-maivia",
    "Tazz": "tazz",
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
# ENTRANTS -- 30 named participants (the official Match Results list totals
# exactly 30 this year, winner included -- no gap-filling needed, unlike 1998).
# ---------------------------------------------------------------------------
all_names = [
    "Al Snow", "Albert", "Big Show", "Billy Gunn", "Booker T", "Big Bossman", "Bradshaw",
    "Christian", "Chuck Palumbo", "Diamond Dallas Page", "Faarooq", "The Godfather", "Goldust",
    "Jeff Hardy", "Kane", "Kurt Angle", "Lance Storm", "Matt Hardy", "Maven", "Mr. Perfect",
    "Perry Saturn", "Rikishi", "Rob Van Dam", "Scotty Too Hotty", "Steve Austin", "Test",
    "The Hurricane", "Triple H", "The Undertaker", "Val Venis",
]
assert len(all_names) == 30

ENTRY_NUMBERS = {
    "Rikishi": 1, "Goldust": 2, "The Undertaker": 8, "Maven": 11, "Steve Austin": 19,
    "Triple H": 24, "Mr. Perfect": 25, "Kurt Angle": 26, "Big Show": 27, "Kane": 28,
    "Rob Van Dam": 29, "Booker T": 30,
}
FINAL_FOUR = {"Steve Austin", "Triple H", "Kurt Angle", "Mr. Perfect"}
FINAL_THREE = {"Triple H", "Kurt Angle", "Mr. Perfect"}
FINAL_TWO = {"Triple H", "Kurt Angle"}

# name -> (eliminator names, data_quality_status, elimination_method, is_shared)
KNOWN_ELIMINATORS = {
    "Billy Gunn": (["The Undertaker"], "CONFIRMED", "One of several midcarders cleared out right after Undertaker's #8 entrance.", False),
    "Al Snow": (["The Undertaker"], "CONFIRMED", "One of several midcarders cleared out right after Undertaker's #8 entrance.", False),
    "Rikishi": (["The Undertaker"], "CONFIRMED", "One of several midcarders cleared out right after Undertaker's #8 entrance.", False),
    "Goldust": (["The Undertaker"], "CONFIRMED", "One of several midcarders cleared out right after Undertaker's #8 entrance.", False),
    "Matt Hardy": (["The Undertaker"], "CONFIRMED", "Thrown out by Undertaker after entering together with Jeff Hardy -- see F136 for the pair's later non-canonical interference.", False),
    "Jeff Hardy": (["The Undertaker"], "CONFIRMED", "Thrown out by Undertaker after entering together with Matt Hardy -- see F136 for the pair's later non-canonical interference.", False),
    "The Undertaker": (["Maven"], "CONFIRMED", "One of the most famous surprise eliminations in Royal Rumble history -- Maven dropkicked Undertaker over the top rope while Undertaker was distracted yelling at the Hardys, who had jumped back in as interference after already being eliminated -- see F136.", False),
    "Christian": (["Steve Austin"], "CONFIRMED", "Stunnered and eliminated by Austin shortly after his #19 entrance.", False),
    "Perry Saturn": (["Steve Austin"], "CONFIRMED", "Stunnered and eliminated by Austin shortly after his #19 entrance.", False),
    "Chuck Palumbo": (["Steve Austin"], "CONFIRMED", "Stunnered and eliminated by Austin shortly after his #19 entrance.", False),
    "Val Venis": (["Steve Austin"], "PROBABLE", "Double-teamed Austin (with Test) before 'eventually they got tossed' -- contextually implied to be by Austin, not an explicit statement.", False),
    "Test": (["Steve Austin"], "PROBABLE", "Double-teamed Austin (with Val Venis) before 'eventually they got tossed' -- contextually implied to be by Austin, not an explicit statement.", False),
    "The Hurricane": (["Steve Austin", "Triple H"], "CONFIRMED", "Ran into both Austin and HHH and was 'gotten rid of' by the two of them together -- modeled as a shared elimination. See F137.", True),
    "Big Show": (["Kane"], "CONFIRMED", "Thrown out by the next entrant, Kane, 'in an impressive show of strength,' shortly after Show himself had chokeslammed everybody.", False),
    "Rob Van Dam": (["Booker T"], "CONFIRMED", "Weakened by a Triple H Pedigree just before Booker T's #30 entrance, then eliminated by Booker T ('quickly disposed of the lifeless RVD') -- see F138.", False),
    "Booker T": (["Steve Austin"], "CONFIRMED", "Stunnered and thrown out by Austin.", False),
    "Steve Austin": (["Kurt Angle"], "CONFIRMED", "Eliminated by Angle in the Final Four.", False),
    "Mr. Perfect": (["Triple H"], "CONFIRMED", "Eliminated by HHH immediately after hitting the Perfectplex on Kurt Angle -- 'HHH was there to ruin everyone's fun, and Hennig's night was done.'", False),
    "Kurt Angle": (["Triple H"], "CONFIRMED", "The winning elimination -- Angle believed he'd already eliminated HHH with an Angle Slam and began celebrating, but HHH came back in and clotheslined him out for the win at 69:22, the longest Royal Rumble match ever at the time.", False),
}

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Triple H")
    entry = ENTRY_NUMBERS.get(name, "")
    elim_by, dq, method, is_shared = KNOWN_ELIMINATORS.get(name, ([], "", "", False))

    note = ""
    if name in ("Matt Hardy", "Jeff Hardy"):
        note = "Eliminated by Undertaker; per S049 both then 'jumped back in' as non-canonical interference shortly before Maven's famous elimination of Undertaker -- not modeled as a second appearance. See F136."
    elif name == "The Undertaker":
        note = "Eliminated 6 opponents (Billy Gunn, Al Snow, Rikishi, Goldust, Matt Hardy, Jeff Hardy) before being famously eliminated by Maven -- see F136."
    elif name == "Steve Austin":
        note = "Eliminated 6 opponents (Christian, Perry Saturn, Chuck Palumbo, Val Venis, Test, Booker T) and shared credit for The Hurricane, before being eliminated by Kurt Angle in the Final Four. Per S049, after his elimination Austin briefly 're-entered' to attack with a chair as non-canonical interference -- not modeled as a second appearance, mirroring the Hardys' situation -- see F136."
    elif name == "Maven":
        note = "One of the most famous surprise eliminations in Royal Rumble history -- eliminated The Undertaker."
    elif name == "Rob Van Dam":
        note = "Hit a Frog Splash on Kurt Angle; weakened by a Triple H Pedigree, then eliminated by Booker T -- see F138."
    elif name == "The Hurricane":
        note = "Shared elimination credit between Steve Austin and Triple H -- see F137."

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
            "is_accidental": "FALSE", "is_self_elimination": "FALSE",
            "is_storyline_related": "UNKNOWN", "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE",
            "simultaneous_group_id": "hurricane_austin_hhh" if name == "The Hurricane" else "",
            "data_quality_status": dq,
            "source_ids": "S049",
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
        "is_returning_wrestler": "TRUE" if name == "Goldust" else "",
        "absence_length": "a few years" if name == "Goldust" else "",
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
        "ring_time": "", "ring_time_seconds": "",
        "ring_time_status": "UNKNOWN",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if name == "Kurt Angle" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "FALSE", "legend_returning": "TRUE" if name == "Mr. Perfect" else "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "TRUE" if name == "Mr. Perfect" else "FALSE",
        "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED" if (entry or is_winner or elim_by) else "PROBABLE",
        "source_ids": "S049",
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
# wrestler_id in this database; opponents without one are recorded as free
# text in the 'opponents' field).
# ---------------------------------------------------------------------------
other_matches = [
    ("William Regal", 2, "Edge", "", "Singles", "TRUE", "Intercontinental Championship", "FALSE", "Win", "TRUE", "", "9:45", "2nd match", "S049", "Pinned Edge to win the I-C Title. Not a Rumble entrant this year."),
    ("Edge", 2, "William Regal", "", "Singles", "TRUE", "Intercontinental Championship", "TRUE", "Loss", "", "TRUE", "9:45", "2nd match", "S049", "Pinned by Regal, losing the I-C Title. Not a Rumble entrant this year."),
    ("Ric Flair", 4, "Vince McMahon", "", "Street Fight", "FALSE", "", "FALSE", "Win", "", "", "14:55", "4th match", "S049", "Defeated Vince McMahon via submission (Figure-Four) in the dueling-GM Street Fight. Not a Rumble entrant this year."),
    ("Vince McMahon", 4, "Ric Flair", "", "Street Fight", "FALSE", "", "FALSE", "Loss", "", "", "14:55", "4th match", "S049", "Submitted to Flair's Figure-Four. Not a Rumble entrant this year."),
    ("Chris Jericho", 5, "The Rock", "", "Singles", "TRUE", "Undisputed Championship", "TRUE", "Win", "", "TRUE", "18:48", "5th match", "S049", "Pinned The Rock (using the ropes for leverage) to retain the Undisputed Championship. Not a Rumble entrant this year."),
    ("The Rock", 5, "Chris Jericho", "", "Singles", "TRUE", "Undisputed Championship", "FALSE", "Loss", "", "", "18:48", "5th match", "S049", "Pinned by Jericho, who used the ropes for leverage. Not a Rumble entrant this year."),
    ("Tazz", 1, "The Dudley Boys (Bubba Ray and D-Von)", "Spike Dudley", "Tag Team", "TRUE", "World Tag Team Championship", "TRUE", "Win", "", "", "5:06", "Opener", "S049", "Made D-Von Dudley submit to retain the tag titles alongside Spike Dudley. Not a Rumble entrant this year."),
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
    ("F135", EVENT_ID, "entrants", "*", "entry_number;ring_time;elim_number", "unverified",
     "Like every other sparse year, 2002 has NO Cageside-style timing analysis in Shane's Word doc -- only the "
     "Dan Wahlers narrative. Entry order is UNKNOWN for 18 of 30 participants (only Rikishi #1, Goldust #2, "
     "The Undertaker #8, Maven #11, Steve Austin #19, Triple H #24, Mr. Perfect #25, Kurt Angle #26, Big Show "
     "#27, Kane #28, Rob Van Dam #29, and Booker T #30 are named), and no ring/survival times or elim_number "
     "values are stated for anyone. UNUSUALLY for a sparse year, though, eliminator credit is rich -- 14 of "
     "29 eliminations have a named eliminator, more than most of this database's Cageside-timed years, thanks "
     "to S049's unusually detailed blow-by-blow narrative.",
     "S049", "open", "2026-09-16"),
    ("F136", EVENT_ID, "entrants", "matt-hardy;jeff-hardy;steve-austin", "*", "needs_human_judgement",
     "S049 describes two instances of wrestlers re-entering the ring after their official elimination as pure "
     "interference, not a genuine second Rumble entry: Matt and Jeff Hardy 'jumped back in' and were 'thrown "
     "out again' by Undertaker moments before Maven's famous elimination of Undertaker, and Steve Austin 'came "
     "back in' to attack with a chair after being eliminated by Kurt Angle in the Final Four. Neither is "
     "modeled as a second entrant row or elimination -- each man's official (first and only legitimate) entry "
     "and elimination is what's recorded, consistent with this database's practice of representing the "
     "officiated record (see 1997's F081 and 2000's F126 for the same principle applied to disputed finishes).",
     "S049", "open", "2026-09-16"),
    ("F137", EVENT_ID, "eliminations", "the-hurricane", "eliminator_wrestler_id", "needs_human_judgement",
     "The Hurricane's elimination is credited ambiguously to both Steve Austin and Triple H together ('After "
     "getting rid of him, Austin and HHH went at each other') -- S049 does not attribute it to one or the "
     "other specifically. Modeled as a shared elimination (is_shared=TRUE, both credited) per DEFINITIONS.md's "
     "group-elimination convention.",
     "S049", "open", "2026-09-16"),
    ("F138", EVENT_ID, "eliminations", "rob-van-dam", "eliminator_wrestler_id", "needs_human_judgement",
     "Triple H hit Rob Van Dam with a Pedigree ('to stop any chance he had at upstaging him'), but S049 "
     "credits the actual elimination to Booker T immediately afterward ('Booker T was #30, and quickly "
     "disposed of the lifeless RVD'). Booker T is credited as the sole eliminator; HHH's Pedigree is noted as "
     "a contributing factor in the elimination_method text rather than given shared credit, since the two "
     "blows are described sequentially rather than jointly.",
     "S049", "open", "2026-09-16"),
    ("F139", EVENT_ID, "wrestlers", "*", "real_name;dob;birthplace", "unverified",
     "Bio data added for 8 previously-unseen wrestlers this pass (Booker T, Chuck Palumbo, Diamond Dallas "
     "Page, Kurt Angle, Lance Storm, Maven, Rob Van Dam, The Hurricane) with zero bio data in this pass's "
     "source -- names only. Left entirely UNKNOWN, same pattern as every prior year's equivalent flag.",
     "S049", "open", "2026-09-16"),
    ("F140", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-16"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2002", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2002-01-20", "venue": "Philips Arena",
    "city_region": "Atlanta, Georgia", "country": "United States",
    "attendance_official": "", "attendance_reported": 12915,
    "entry_interval_seconds": "UNKNOWN", "entrant_count": 30, "duration_total": "69:22",
    "duration_status": "CONFIRMED",
    "winner_id": "hunter-hearst-helmsley", "runner_up_id": "kurt-angle",
    "final_two_ids": "hunter-hearst-helmsley;kurt-angle",
    "final_three_ids": "hunter-hearst-helmsley;kurt-angle;mr-perfect",
    "final_four_ids": "steve-austin;hunter-hearst-helmsley;kurt-angle;mr-perfect",
    "first_entrant_id": "rikishi", "second_entrant_id": "goldust", "final_entrant_id": "booker-t",
    "first_elimination_id": "UNKNOWN", "last_elimination_before_winner_id": "kurt-angle",
    "eliminations_count": 29, "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": "UNKNOWN",
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Jim Ross, Jerry Lawler", "ring_announcer": "UNKNOWN",
    "referees": "Not identified in the source consulted this pass",
    "special_rules": (
        "At 69:22 (1:09:22), this was the longest Royal Rumble match ever at the time, per S049. Maven's "
        "dropkick elimination of The Undertaker is one of the most famous surprise eliminations in Royal "
        "Rumble history. Two separate post-elimination interference incidents occurred (Matt/Jeff Hardy, then "
        "Steve Austin) where an eliminated wrestler briefly re-entered the ring as non-canonical interference "
        "-- neither is modeled as a genuine second entry, see F136."
    ),
    "title_on_the_line": "FALSE",
    "championship_implications": "None in the Rumble match itself, though William Regal won the Intercontinental Championship from Edge, Ric Flair defeated Vince McMahon in a dueling-authority-figures Street Fight, and Chris Jericho retained the Undisputed Championship against The Rock, all earlier on the same card.",
    "winners_reward": "A WWF Undisputed Championship match, though the narrative frames the win as launching Triple H's dominant run through the rest of 2002, per S049",
    "historical_significance": (
        "Triple H's Royal Rumble win, at 69:22 the longest Royal Rumble match ever at the time. Maven's "
        "dropkick elimination of The Undertaker -- a total underdog knocking out one of the promotion's most "
        "dominant stars -- is one of the most famous surprise eliminations in Royal Rumble history. Mr. "
        "Perfect (Curt Hennig) made a surprising return to the WWF after a 6-year absence, reaching the Final "
        "Four before Triple H eliminated him; per S049 this was 'the last notable thing Hennig would do before "
        "his untimely death in 2003.' Ric Flair's return to the company (as co-owner alongside Vince McMahon) "
        "set up the dueling-GM Street Fight on the same card."
    ),
    "notes": (
        "Sparse on timing data -- only 12 of 30 entrants have a confirmed entry number, and no ring/survival "
        "times exist for anyone -- see F135. Unusually for a sparse year, eliminator credit is rich: 14 of 29 "
        "eliminations are directly credited, more than most of this database's Cageside-timed years."
    ),
    "data_quality_status": "PROBABLE", "source_ids": "S049",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2002 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
