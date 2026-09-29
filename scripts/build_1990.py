# -*- coding: utf-8 -*-
"""
Builds all rows for the 1990 Royal Rumble — schema v2.

Same documents-only discipline as 1989: no live web research this pass.

SOURCES CONSULTED THIS PASS:
  S016 "1990 Royal Rumble - Dan Wahlers History of the Royal Rumble" (Shane's doc)   tier 9
  S017 Shane's original research (Entrant_Stats.xlsx, '1990' tab)                    tier 11

IMPORTANT DIFFERENCE FROM 1988/1989: Shane's Word doc has NO Cageside-style
timing analysis and NO Kayfabe Memories review for 1990 -- only the Dan
Wahlers narrative history + a match-results text block. (The document DOES
contain a full Cageside + Dan Wahlers write-up for 1991, but it's misfiled
under the "1990 Royal Rumble Stats" Heading-1 in the .docx -- the actual
sub-heading text says "1991 Rumble Stats - Cageside" / "1991 Royal Rumble --
Dan Wahlers History", and its own narrative is self-evidently about a
different, later event (Sgt. Slaughter/Gulf War angle, Undertaker's Rumble
debut, Ultimate Warrior losing the WWF Title on the undercard, Rick Martel's
survival record "lasting only until the next year" referencing 1990's
Rumble as the past). That 1991 material is NOT used in this build -- it's
saved for the next pass. See flags.csv F0xx.

ALSO IMPORTANT: unlike the 1988/1989 Excel tabs, the 1990 tab's entrant rows
have entry number / elimination number / eliminated-by / ring time filled in
for all 30 people, but EVERY bio/physical column (real name, DOB, height,
weight, billed from, alignment, tag team, champion status) is blank. Bios for
returning wrestlers were reused from wrestlers.csv (already built from
1988/1989) with ages freshly DERIVED for this event's date; bios for the 4
people making their first appearance in this database (Roddy Piper, Dusty
Rhodes, Jimmy Snuka, Earthquake) are UNKNOWN this pass -- no source in
Shane's documents gives their DOB/height/weight, and per the "never invent"
rule, general background knowledge isn't used to fill these in without a
citable source. Same for 3 new non-wrestler personnel (The Genius/Lanny
Poffo, Tony Schiavone, Brother Love, Sapphire) -- ring names only.
"""
import csv
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from schema import (
    ENTRANTS_FIELDS, ELIMINATIONS_FIELDS, EVENTS_FIELDS, slugify, mmss_to_seconds,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EVENT_ID = "RR1990M"
EVENT_DATE = datetime.date(1990, 1, 21)

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S016", "Dan Wahlers, 'History of the Royal Rumble' -- 1990 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Preserved in Shane's original doc; no live URL captured. Full narrative history, and fall-by-fall/duration undercard results. Gives attendance as 16,000."),
    ("S017", "Shane's original research (Entrant_Stats.xlsx, '1990' tab)", "original_document", "", 11, "Original research document", "2026-09-15",
     "Entry number, elimination number, eliminated-by, and ring time are filled in for all 30 entrants; every bio/physical column is blank for this tab, unlike 1988/1989. Pre-Rumble Appearances section (23 people) has full bio data for most, same as prior years."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F015", EVENT_ID, "sources", "n/a", "n/a", "unverified",
     "Shane's Word doc contains a full Cageside-style timing analysis and Dan Wahlers history for "
     "1991, but it is misfiled under the '1990 Royal Rumble Stats' Heading-1 (the sub-heading text "
     "itself correctly says '1991 Rumble Stats - Cageside' / '1991 Royal Rumble -- Dan Wahlers "
     "History', and the narrative is unambiguously about a different, later event -- Sgt. Slaughter's "
     "Gulf War angle, Undertaker's Rumble debut, Ultimate Warrior losing the WWF Title earlier on the "
     "card, and an explicit reference to Rick Martel's 52:30 survival record lasting 'only until the "
     "next year'). That material was NOT used for this 1990 build -- it's the next event to build, and "
     "the document's heading structure needs to be treated as unreliable for 1991 (rely on the "
     "sub-heading text, not the Heading-1 grouping, when building it).",
     "S016", "open", "2026-09-15"),
    ("F016", EVENT_ID, "entrants", "*", "billed_height_m_at_event;billed_weight_kg_at_event;billed_from_at_event;alignment", "unverified",
     "Unlike the 1988/1989 Excel tabs, the 1990 tab's per-entrant bio/physical columns (real name, DOB, "
     "height, weight, billed from, heel/face, tag team, champion status) are entirely blank for all 30 "
     "Rumble entrants. Reused wrestlers' ages were freshly DERIVED from their existing DOB in "
     "wrestlers.csv; height/weight/billed_from/alignment are left blank (UNKNOWN) for this event rather "
     "than silently carrying forward a prior year's figure, since billed stats can and do change year to "
     "year and no 1990-specific source confirms them.",
     "S017", "open", "2026-09-15"),
    ("F017", EVENT_ID, "wrestlers", "roddy-piper;dusty-rhodes;jimmy-snuka;earthquake;the-genius;tony-schiavone;brother-love;sapphire", "real_name;dob;billed_height_m_at_event;billed_weight_kg_at_event;birthplace", "unverified",
     "8 people appear in this database for the first time via 1990 (4 Rumble entrants: Roddy Piper, "
     "Dusty Rhodes, Jimmy Snuka, Earthquake; 4 non-wrestler personnel: The Genius/Lanny Poffo, Tony "
     "Schiavone, Brother Love, Sapphire) with NO bio data available in either of Shane's documents for "
     "this pass. Left entirely UNKNOWN rather than filled from general background knowledge, per the "
     "'never invent, only cited sources' rule -- these are all well-documented public figures and would "
     "be easy to fill in during the internet-research phase.",
     "S017", "open", "2026-09-15"),
    ("F018", EVENT_ID, "entrants", "akeem;earthquake", "ring_time", "unverified",
     "RESOLVED (fact-check pass, see S022/S026): Akeem and Earthquake's identical 02:31 ring time is a "
     "genuine, independently-confirmed coincidence, not a spreadsheet duplication error -- Wikipedia's "
     "Royal Rumble (1990) article gives the exact same 02:31 figure for both entrants, agreeing with S017 "
     "without having any reason to copy its formatting quirks. ring_time_status upgraded to CONFIRMED for "
     "both. Separately, the same cross-check turned up a real gap: Earthquake's elimination is credited to "
     "6 wrestlers jointly per 2 independent sources (Wikipedia and wrestlingrecaps.com's recap), not 5 as "
     "S017 alone showed -- Dino Bravo was missing from the credit list and has been added.",
     "S017;S022;S026", "resolved", "2026-09-15"),
    ("F019", EVENT_ID, "entrants", "*", "ring_time_status", "unverified",
     "Entry order, elimination order, and eliminated-by credits are CONFIRMED (S017's structured table "
     "agrees in every detail it's possible to check against S016's narrative: Ted DiBiase drawing #1 and "
     "lasting ~45 min before Warrior eliminated him; Mr. Perfect eliminating Rick Rude then losing to "
     "Hogan in the final elimination). Exact ring times to the second are PROBABLE only -- S016 doesn't "
     "give per-wrestler timestamps, only round narrative figures, so there's no independent second "
     "source confirming S017's precise seconds the way Cageside did for 1988/1989.",
     "S016;S017", "open", "2026-09-15"),
    ("F020", EVENT_ID, "events;entrances/moves/near_eliminations", "*", "n/a", "out_of_scope_no_tool",
     "No video/computer-vision tool connected this session -- entrances.csv, moves.csv, "
     "near_eliminations.csv, eliminations.csv:location_side stay empty. Same as 1988's F005 / 1989's F013.",
     "", "open", "2026-09-15"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# WRESTLERS -- only NEW people. Reused (not re-added): ted-dibiase, koko-b-ware,
# marty-jannetty, jake-roberts, randy-savage, the-warlord, bret-hart,
# bad-news-brown, andre-the-giant, red-rooster, ax, haku, smash, one-man-gang
# (Akeem), dino-bravo, jim-neidhart, the-ultimate-warrior, rick-martel,
# tito-santana, the-honky-tonk-man, hulk-hogan, shawn-michaels, the-barbarian,
# rick-rude, hercules, mr-perfect, jacques-rougeau, raymond-rougeau, jimmy-hart,
# brutus-beefcake, ronnie-garvin, greg-valentine, jim-duggan, big-bossman,
# slick, bobby-heenan, virgil, sean-mooney, gene-okerlund, mr-fuji,
# sensational-sherri, jesse-ventura, howard-finkel
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Roddy Piper", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S017"),
    ("Dusty Rhodes", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S017"),
    ("Jimmy Snuka", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S017"),
    ("Earthquake", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S017"),
    ("The Genius", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "Lanny Poffo", "", "", "S016's narrative names this person as Lanny Poffo directly (Randy Savage's real-life brother, per the 'Family Member' link in S017 to Randy Savage) -- no DOB/height/weight in either source this pass.", "S016;S017"),
    ("Tony Schiavone", "Tony Schiavone", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Commentator; no DOB/birthplace in either source this pass.", "S017"),
    ("Brother Love", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Interview segment host; no bio data in either source this pass.", "S017"),
    ("Sapphire", "", "UNKNOWN", "F", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Manager to Dusty Rhodes; no bio data in either source this pass.", "S017"),
]

reused = {
    "Ted DiBiase": "ted-dibiase", "Koko B. Ware": "koko-b-ware", "Marty Jannetty": "marty-jannetty",
    "Jake Roberts": "jake-roberts", "Randy Savage": "randy-savage", "The Warlord": "the-warlord",
    "Bret Hart": "bret-hart", "Bad News Brown": "bad-news-brown", "Andre the Giant": "andre-the-giant",
    "Red Rooster": "red-rooster", "Demolition Ax": "ax", "Haku": "haku", "Demolition Smash": "smash",
    "Akeem": "one-man-gang", "Dino Bravo": "dino-bravo", "Jim Neidhart": "jim-neidhart",
    "Ultimate Warrior": "the-ultimate-warrior", "Rick Martel": "rick-martel", "Tito Santana": "tito-santana",
    "Honkytonk Man": "the-honky-tonk-man", "Hulk Hogan": "hulk-hogan", "Shawn Michaels": "shawn-michaels",
    "The Barbarian": "the-barbarian", "Rick Rude": "rick-rude", "Hercules": "hercules", "Mr. Perfect": "mr-perfect",
    "Jacques Rougeau": "jacques-rougeau", "Raymond Rougeau": "raymond-rougeau", "Jimmy Hart": "jimmy-hart",
    "Brutus Beefcake": "brutus-beefcake", "Ron Garvin": "ronnie-garvin", "Greg Valentine": "greg-valentine",
    "Jim Duggan": "jim-duggan", "Big Bossman": "big-bossman", "Slick": "slick", "Bobby Heenan": "bobby-heenan",
    "Virgil": "virgil", "Sean Mooney": "sean-mooney", "Gene Okerlund": "gene-okerlund", "Mr. Fuji": "mr-fuji",
    "Sensational Sherri": "sensational-sherri", "Jesse Ventura": "jesse-ventura", "Howard Finkel": "howard-finkel",
    "Butch Miller": "butch-miller", "Luke Williams": "luke-williams",
}
wrestler_ids = {}
wrestler_ids.update(reused)

with open(os.path.join(DATA_DIR, "wrestlers.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in new_wrestlers:
        ring_name = row[0]
        wid = slugify(ring_name)
        wrestler_ids[ring_name] = wid
        writer.writerow([wid] + list(row))

# ---------------------------------------------------------------------------
# Compute prior-Rumble-appearance history dynamically from the already-built
# entrants.csv (RR1988M, RR1989M), keyed off event_date order in events.csv
# ---------------------------------------------------------------------------
with open(os.path.join(DATA_DIR, "events.csv")) as f:
    prior_events = {r["event_id"]: r["event_date"] for r in csv.DictReader(f)}
with open(os.path.join(DATA_DIR, "entrants.csv")) as f:
    prior_entrants = list(csv.DictReader(f))

history = {}
for r in prior_entrants:
    if prior_events.get(r["event_id"], "9999") >= "1990-01-21":
        continue
    history.setdefault(r["wrestler_id"], []).append(r)
for wid in history:
    history[wid].sort(key=lambda r: prior_events[r["event_id"]])


def age_str(dob_s, ref):
    y, m, d = map(int, dob_s.split("-"))
    dob = datetime.date(y, m, d)
    years = ref.year - dob.year
    months = ref.month - dob.month
    days = ref.day - dob.day
    if days < 0:
        months -= 1
        import calendar
        prev_month = ref.month - 1 or 12
        prev_year = ref.year if ref.month > 1 else ref.year - 1
        days += calendar.monthrange(prev_year, prev_month)[1]
    if months < 0:
        years -= 1
        months += 12
    return f"{years} Years, {months} Months, {days} Days"


with open(os.path.join(DATA_DIR, "wrestlers.csv")) as f:
    all_wrestlers = {r["wrestler_id"]: r for r in csv.DictReader(f)}

# ---------------------------------------------------------------------------
# ENTRANTS in the 30-man Royal Rumble match, in entry order
# ---------------------------------------------------------------------------
# name, entry, elim_no, elim_by[], ring_time, elim_count(this event)
entrants_raw = [
    ("Ted DiBiase", 1, 18, ["Ultimate Warrior"], "44:47", 3),
    ("Koko B. Ware", 2, 1, ["Ted DiBiase"], "01:36", 0),
    ("Marty Jannetty", 3, 2, ["Ted DiBiase"], "01:35", 0),
    ("Jake Roberts", 4, 3, ["Randy Savage"], "10:03", 0),
    ("Randy Savage", 5, 4, ["Dusty Rhodes"], "10:10", 1),
    ("Roddy Piper", 6, 7, ["Bad News Brown"], "12:20", 1),
    ("The Warlord", 7, 5, ["Andre the Giant"], "08:16", 0),
    ("Bret Hart", 8, 9, ["Dusty Rhodes"], "16:16", 0),
    ("Bad News Brown", 9, 6, ["Roddy Piper"], "06:04", 1),
    ("Dusty Rhodes", 10, 12, ["Earthquake"], "18:18", 2),
    ("Andre the Giant", 11, 10, ["Demolition Ax", "Demolition Smash"], "10:16", 2),
    ("Red Rooster", 12, 8, ["Andre the Giant"], "01:58", 0),
    ("Demolition Ax", 13, 13, ["Earthquake"], "12:50", 1),
    ("Haku", 14, 20, ["Hulk Hogan"], "22:31", 2),
    ("Demolition Smash", 15, 16, ["Haku"], "15:01", 2),
    ("Akeem", 16, 11, ["Jimmy Snuka"], "02:31", 0),
    ("Jimmy Snuka", 17, 19, ["Hulk Hogan"], "17:03", 2),
    ("Dino Bravo", 18, 15, ["Ultimate Warrior"], "06:13", 1),
    ("Earthquake", 19, 14, ["Ted DiBiase", "Demolition Smash", "Haku", "Jimmy Snuka", "Jim Neidhart", "Dino Bravo"], "02:31", 2),
    ("Jim Neidhart", 20, 17, ["Ultimate Warrior", "Rick Martel"], "08:42", 1),
    ("Ultimate Warrior", 21, 25, ["Hulk Hogan", "Rick Rude", "The Barbarian"], "14:29", 6),
    ("Rick Martel", 22, 24, ["Ultimate Warrior"], "08:14", 2),
    ("Tito Santana", 23, 21, ["Ultimate Warrior", "Rick Martel"], "05:09", 0),
    ("Honkytonk Man", 24, 22, ["Hulk Hogan"], "04:01", 0),
    ("Hulk Hogan", 25, 0, [], "12:49", 5),
    ("Shawn Michaels", 26, 23, ["Ultimate Warrior"], "00:12", 0),
    ("The Barbarian", 27, 26, ["Hercules"], "05:47", 1),
    ("Rick Rude", 28, 28, ["Mr. Perfect"], "06:29", 2),
    ("Hercules", 29, 27, ["Rick Rude"], "03:02", 1),
    ("Mr. Perfect", 30, 29, ["Hulk Hogan"], "03:32", 1),
]

FINAL_FOUR_ORDER = ["hulk-hogan", "mr-perfect", "rick-rude", "hercules"]
elim_rows = []
entrant_rows = []

for (name, entry, elim_no, elim_by, ring_time, elim_count) in entrants_raw:
    wid = wrestler_ids[name]
    is_winner = (elim_no == 0)
    ring_time_s = mmss_to_seconds(ring_time)

    if elim_by:
        for eliminator in elim_by:
            elim_rows.append({
                "event_id": EVENT_ID, "order_in_match": elim_no,
                "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids.get(eliminator, wid),
                "assisting_wrestler_ids": ";".join(wrestler_ids[e] for e in elim_by if e != eliminator),
                "entry_number_of_eliminated": entry, "entry_number_of_eliminator": "",
                "elimination_clock_time": ring_time, "elimination_clock_seconds": ring_time_s,
                "elimination_type": "over_top_rope", "elimination_method": "UNKNOWN",
                "location_side": "", "location_status": "UNKNOWN",
                "is_solo": "FALSE" if len(elim_by) > 1 else "TRUE",
                "is_shared": "TRUE" if len(elim_by) > 1 else "FALSE",
                "is_accidental": "UNKNOWN", "is_self_elimination": "FALSE",
                "is_storyline_related": "UNKNOWN", "was_already_incapacitated": "UNKNOWN",
                "is_disputed": "FALSE", "simultaneous_group_id": "",
                "data_quality_status": "CONFIRMED", "source_ids": "S016;S017",
                "notes": "",
            })

    prior_hist = history.get(wid, [])
    prior_count = len(prior_hist)
    w = all_wrestlers.get(wid, {})
    dob = w.get("dob", "")
    age = age_str(dob, EVENT_DATE) if dob else ""

    er = {
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": "CONFIRMED",
        "ring_name_at_time": name, "name_displayed_at_event": name,
        "prior_rumble_appearances_count": prior_count,
        "rumble_appearance_no": prior_count + 1,
        "is_first_rumble_appearance": "TRUE" if prior_count == 0 else "FALSE",
        "previous_rumble_year": prior_events[prior_hist[-1]["event_id"]][:4] if prior_hist else "",
        "previous_rumble_result": "", "previous_rumble_elimination_no": "",
        "is_rumble_debut": "TRUE" if prior_count == 0 else "FALSE",
        "is_company_debut": "UNKNOWN", "company_debut_date": "",
        "is_returning_wrestler": "TRUE" if prior_count > 0 else "FALSE", "absence_length": "",
        "age_at_event": age, "age_status": "DERIVED" if age else "UNKNOWN",
        "billed_height_m_at_event": "", "billed_weight_kg_at_event": "",
        "billed_from_at_event": "",
        "physical_status": "UNKNOWN",
        "alignment": "", "alignment_status": "UNKNOWN",
        "gimmick_at_event": "", "manager_at_event": "", "tag_team_name": "Demolition (w/ Smash)" if name == "Demolition Ax" else ("Demolition (w/ Ax)" if name == "Demolition Smash" else ""),
        "faction_stable": "",
        "current_champion_title": "", "championship_level": "", "championship_partner": "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        "title_defended_same_card": "FALSE", "title_lost_same_card": "FALSE",
        "elim_number": elim_no if elim_no else "", "elim_number_status": "CONFIRMED",
        "eliminated_by_ids": ";".join(wrestler_ids.get(e, wid) for e in elim_by),
        "elimination_clock_time": ring_time if elim_by and not is_winner else "",
        "elimination_clock_seconds": ring_time_s if elim_by and not is_winner else "",
        "ring_time": ring_time, "ring_time_seconds": ring_time_s,
        "ring_time_status": "CONFIRMED" if name in ("Akeem", "Earthquake") else "PROBABLE",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": elim_count, "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE", "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if wid == "mr-perfect" else "FALSE",
        "is_final_two": "TRUE" if wid in ("hulk-hogan", "mr-perfect") else "FALSE",
        "is_final_three": "TRUE" if wid in FINAL_FOUR_ORDER[:3] else "FALSE",
        "is_final_four": "TRUE" if wid in FINAL_FOUR_ORDER else "FALSE",
        "surprise_entrant": "FALSE", "legend_returning": "FALSE", "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE", "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",  # WWE HOF didn't exist until 1993
        "data_quality_status": "CONFIRMED", "source_ids": "S016;S017", "notes": "",
    }
    if prior_hist:
        last = prior_hist[-1]
        if last["is_winner"] == "TRUE":
            er["previous_rumble_result"] = "Won"
        elif last["is_runner_up"] == "TRUE":
            er["previous_rumble_result"] = f"Runner-up (elim #{last['elim_number']})"
        else:
            er["previous_rumble_result"] = f"Eliminated (elim #{last['elim_number']})"
        er["previous_rumble_elimination_no"] = last["elim_number"]
    entrant_rows.append(er)

# Back-fill wrestlers_eliminated_ids / solo / assisted counts
elim_map = {}
solo_map = {}
assist_map = {}
for row in elim_rows:
    eid = row["eliminator_wrestler_id"]
    if eid == row["eliminated_wrestler_id"]:
        continue
    elim_map.setdefault(eid, []).append(row["eliminated_wrestler_id"])
    if row["is_solo"] == "TRUE":
        solo_map[eid] = solo_map.get(eid, 0) + 1
    else:
        assist_map[eid] = assist_map.get(eid, 0) + 1

for er in entrant_rows:
    wid = er["wrestler_id"]
    er["wrestlers_eliminated_ids"] = ";".join(elim_map.get(wid, []))
    er["solo_eliminations_count"] = solo_map.get(wid, 0)
    er["assisted_eliminations_count"] = assist_map.get(wid, 0)

with open(os.path.join(DATA_DIR, "entrants.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ENTRANTS_FIELDS)
    for er in entrant_rows:
        writer.writerow(er)

with open(os.path.join(DATA_DIR, "eliminations.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ELIMINATIONS_FIELDS)
    for row in elim_rows:
        writer.writerow(row)

# ---------------------------------------------------------------------------
# TAG TEAMS -- only Demolition (Ax & Smash) is explicitly evidenced as a
# team entry this year (paired together in S016's entrant list); no other
# pairing is stated for the Rumble match field itself.
# ---------------------------------------------------------------------------
tag_teams = [
    ("Demolition", ["Demolition Ax", "Demolition Smash"], "TRUE", 1),
]
with open(os.path.join(DATA_DIR, "tag_teams.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for team_name, members, official, combined in tag_teams:
        writer.writerow([EVENT_ID, team_name, ";".join(wrestler_ids[m] for m in members), "", "",
                          official, "TRUE", "TRUE", "", "FALSE", "TRUE", "FALSE", combined,
                          "PROBABLE", "S017"])

# ---------------------------------------------------------------------------
# SHOW APPEARANCES (Pre-Rumble Appearances, per S017)
# ---------------------------------------------------------------------------
show_appearances = [
    ("Butch Miller", "Wrestler (undercard)", "", "Face", "", "Opener; pinned Jacques Rougeau"),
    ("Luke Williams", "Wrestler (undercard)", "", "Face", "", "Opener"),
    ("Jacques Rougeau", "Wrestler (undercard)", "", "Heel", "", "Opener; pinned by Butch Miller"),
    ("Raymond Rougeau", "Wrestler (undercard)", "", "Heel", "", "Opener"),
    ("Jimmy Hart", "Manager", "Jacques Rougeau, Raymond Rougeau, Earthquake, Dino Bravo, Honkytonk Man, Greg Valentine", "Heel", "", ""),
    ("Brutus Beefcake", "Wrestler (undercard)", "", "Face", "", "Double DQ vs. The Genius (Lanny Poffo)"),
    ("The Genius", "Wrestler (undercard)", "", "Heel", "", "Double DQ vs. Brutus Beefcake"),
    ("Ron Garvin", "Wrestler (undercard)", "", "Face", "", "'I Quit' match, defeated Greg Valentine"),
    ("Greg Valentine", "Wrestler (undercard)", "", "Heel", "", "'I Quit' match, lost to Ronnie Garvin"),
    ("Jim Duggan", "Wrestler (appeared on card)", "", "Face", "", "Match/role not detailed in sources consulted this pass"),
    ("Big Bossman", "Wrestler (appeared on card)", "", "Heel", "", "Match/role not detailed in sources consulted this pass; not a Rumble-match entrant this year"),
    ("Slick", "Manager", "Big Bossman, Akeem", "Heel", "", ""),
    ("Bobby Heenan", "Manager", "Andre the Giant, Rick Rude, Haku", "Heel", "", ""),
    ("Virgil", "Bodyguard/valet", "Ted DiBiase", "Heel", "", ""),
    ("Sean Mooney", "Interviewer", "", "Face", "", ""),
    ("Gene Okerlund", "Interviewer", "", "Face", "", ""),
    ("Mr. Fuji", "Manager", "The Warlord, The Barbarian", "Heel", "", ""),
    ("Sensational Sherri", "Manager", "Randy Savage", "Heel", "", ""),
    ("Jesse Ventura", "Commentator", "", "Heel", "", ""),
    ("Howard Finkel", "Ring announcer", "", "Face", "", ""),
    ("Tony Schiavone", "Commentator", "", "Face", "", ""),
    ("Brother Love", "Interview segment host", "", "Heel", "", ""),
    ("Sapphire", "Manager", "Dusty Rhodes", "Face", "", ""),
]
with open(os.path.join(DATA_DIR, "show_appearances.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for name, role, managed, align, title, notes in show_appearances:
        pid = wrestler_ids.get(name, slugify(name))
        writer.writerow([EVENT_ID, pid, name, role, managed, align, title, notes, "PROBABLE", "S016;S017"])

# ---------------------------------------------------------------------------
# OTHER MATCHES ON THE SAME CARD
# ---------------------------------------------------------------------------
other_matches = [
    ("Butch Miller", 1, "Jacques Rougeau, Raymond Rougeau", "Luke Williams", "Tag", "FALSE", "", "FALSE", "Win", "", "", "13:35", "Opener",
     "S016", "Butch pinned Jacques."),
    ("Luke Williams", 1, "Jacques Rougeau, Raymond Rougeau", "Butch Miller", "Tag", "FALSE", "", "FALSE", "Win", "", "", "13:35", "Opener",
     "S016", ""),
    ("Jacques Rougeau", 1, "Butch Miller, Luke Williams", "Raymond Rougeau", "Tag", "FALSE", "", "FALSE", "Loss", "", "", "13:35", "Opener",
     "S016", "Pinned by Butch Miller."),
    ("Raymond Rougeau", 1, "Butch Miller, Luke Williams", "Jacques Rougeau", "Tag", "FALSE", "", "FALSE", "Loss", "", "", "13:35", "Opener",
     "S016", ""),
    ("The Genius", 2, "Brutus Beefcake", "", "Singles", "FALSE", "", "FALSE", "Double DQ", "", "", "11:07", "2nd match",
     "S016", "Referred to as 'Lanny Poffo' by S016."),
    ("Brutus Beefcake", 2, "The Genius", "", "Singles", "FALSE", "", "FALSE", "Double DQ", "", "", "11:07", "2nd match",
     "S016", ""),
    ("Ron Garvin", 3, "Greg Valentine", "", "Singles ('I Quit' match)", "FALSE", "", "FALSE", "Win", "", "", "16:55", "3rd match",
     "S016", ""),
    ("Greg Valentine", 3, "Ron Garvin", "", "Singles ('I Quit' match)", "FALSE", "", "FALSE", "Loss", "", "", "16:55", "3rd match",
     "S016", ""),
]
with open(os.path.join(DATA_DIR, "other_matches.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for (name, mnum, opponents, partners, mtype, is_title, title, was_champ, result, title_change, duration_note, duration, position, row_src, notes) in other_matches:
        pid = wrestler_ids.get(name, slugify(name))
        writer.writerow([EVENT_ID, pid, mnum, opponents, partners, mtype, is_title, title, was_champ,
                          result, "FALSE", "FALSE", duration, position, "", "PROBABLE", row_src, notes])

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 1990", "match_name": "30-Man Royal Rumble Match",
    "match_type": "Men's", "event_date": "1990-01-21", "venue": "Orlando Arena",
    "city_region": "Orlando, Florida", "country": "United States",
    "attendance_official": "", "attendance_reported": 16000,
    "entry_interval_seconds": 120, "entrant_count": 30, "duration_total": "58:46",
    "duration_status": "CONFIRMED",
    "winner_id": "hulk-hogan", "runner_up_id": "mr-perfect",
    "final_two_ids": "hulk-hogan;mr-perfect", "final_three_ids": "hulk-hogan;mr-perfect;rick-rude",
    "final_four_ids": "hulk-hogan;mr-perfect;rick-rude;hercules",
    "first_entrant_id": "ted-dibiase", "second_entrant_id": "koko-b-ware", "final_entrant_id": "mr-perfect",
    "first_elimination_id": "koko-b-ware", "last_elimination_before_winner_id": "mr-perfect",
    "eliminations_count": 29, "eliminators_count": 16, "surprise_entrants_count": 0,
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": 0,
    "tag_teams_count": 1, "factions_count": "N/A",
    "commentary_team": "Tony Schiavone, Jesse Ventura", "ring_announcer": "Howard Finkel",
    "referees": "Tony Garea, Pat Patterson, Danny Davis, Earl Hebner, Joey Marella, Shane Stevens per S026 (Wikipedia)",
    "special_rules": (
        "First of two consecutive Hogan Royal Rumble wins (1990-1991). No reigning champion in the "
        "field this year (unlike 1989's Savage/Demolition) -- Ultimate Warrior was WWF Champion at the "
        "time but did not compete in the Rumble match itself. Ted DiBiase drew #1 and lasted ~45 minutes "
        "before being eliminated by Ultimate Warrior. Earthquake's elimination is credited to SIX "
        "eliminators jointly (Ted DiBiase, Smash, Haku, Jimmy Snuka, Jim Neidhart, Dino Bravo -- the 6th, "
        "Dino Bravo, was added during the fact-check pass per 2 independent external sources, see F018) "
        "and Ultimate Warrior's final elimination to three (Hogan, Rick Rude, The Barbarian) -- the "
        "largest joint-credit groups seen in the database so far."
    ),
    "title_on_the_line": "FALSE", "championship_implications": "None -- no title was contested in the Rumble match itself",
    "winners_reward": "None identified this pass -- S016 doesn't mention a guaranteed title-shot stipulation for this year's winner",
    "historical_significance": "Widely regarded (per S016's own framing) as one of the most star-studded Royal Rumble fields ever assembled -- Andre the Giant, Bret Hart, Ted DiBiase, Mr. Perfect, Roddy Piper, Dusty Rhodes, Randy Savage, and Ultimate Warrior all in the same 30-man field. Hulk Hogan's first Royal Rumble MATCH appearance and win (he had been WWF Champion during 1988/1989 without competing in either Rumble). S016 notes a backstage detail: Mr. Perfect was reportedly scripted to win, but Hogan (also the reigning champion) overruled it.",
    "notes": "30 confirmed entrants, all identified. See flags.csv F015-F020 for the misfiled-1991-content issue, the blank bio columns, the new-wrestler bio gaps, and the Akeem/Earthquake ring-time coincidence (F018, resolved via S026/Wikipedia independently confirming the 02:31 figure for both and revealing the missing Dino Bravo eliminator credit). Fact-check pass (S026, Wikipedia) independently confirmed date, venue, attendance, duration (58:46 matches exactly, upgraded to CONFIRMED), and filled in the referee crew.",
    "data_quality_status": "CONFIRMED", "source_ids": "S016;S017;S026",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"1990 build complete (schema v2): {len(new_wrestlers)} new wrestlers ({len(reused)} reused), "
      f"{len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, {len(tag_teams)} tag teams, "
      f"{len(show_appearances)} show appearances, {len(other_matches)} other-match rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
