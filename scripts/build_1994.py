# -*- coding: utf-8 -*-
"""
Builds all rows for the 1994 Royal Rumble -- schema v2.

UNLIKE every other year built so far (1988-1993), this event has NO
Cageside-style timing analysis in Shane's Word doc -- only the Dan Wahlers
narrative history section exists under the "1994 Royal Rumble Stats"
Heading-1. No Excel tab either. This makes 1994 the leanest build in the
database: no survival times, no entrance times, no buzzer intervals, no
elimination order, and only a partial entrant list. This is a genuine gap
in the source material, not an oversight -- see F059.

SOURCES CONSULTED THIS PASS:
  S029 Dan Wahlers "History of the Royal Rumble" -- 1994 chapter     tier 9

WHAT'S ACTUALLY KNOWN THIS YEAR:
  - The full 30-man/entry-number structure, individual ring times, and
    elimination order are ALL UNKNOWN -- no source states them.
  - Only 29 participants are named at all (see F061) -- entry_number is
    UNKNOWN for every single one of them, including the two the narrative
    says went in first ("Scott Steiner and Samu of the Headshrinkers were
    the first two entrants" -- exact order between the two is NOT stated).
  - The match's famous, genuinely unique finish: Bret Hart and Lex Luger
    went over the top rope at essentially the same instant. WWF announced
    BOTH as the winner live, to gauge crowd reaction (Luger got booed).
    Dan Wahlers' own text states that replay showed Luger's feet hit the
    floor first, which by the match's own rules would make Bret Hart the
    sole legitimate winner and Luger the final elimination -- but this was
    never corrected on-air or in the official record, and this is the only
    Royal Rumble in history with a co-winner call. Modeled here as BOTH
    Bret Hart and Lex Luger having is_winner=TRUE on their entrant rows
    (so derived win-count stats credit both, matching how this event is
    conventionally remembered/recorded), with events.csv's winner_id
    holding both ids and the full controversy documented in special_rules
    and F060. No elimination row is written for either man -- crediting
    one as "eliminating" the other would mean picking a side in a dispute
    the source itself doesn't resolve.
  - "Crush" is Brian Adams' solo gimmick after Demolition's breakup --
    same person already in this database as "Demolition Crush"
    (wrestler_id demolition-crush, added 1990/1991). Identity merge, not a
    new wrestler.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from schema import (
    ENTRANTS_FIELDS, EVENTS_FIELDS,
    slugify, mmss_to_seconds,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EVENT_ID = "RR1994M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S029", "Dan Wahlers, 'History of the Royal Rumble' -- 1994 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance as 14,500, full narrative "
     "history (the Bret Hart/Lex Luger co-winner finish, the Undertaker/Yokozuna Casket Match, Owen Hart's "
     "heel turn on Bret), and undercard match results. NO Cageside-style timing analysis exists for this year "
     "-- see F059."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F059", EVENT_ID, "entrants;eliminations", "*", "entry_number;ring_time;elim_number", "unverified",
     "Unlike every prior year in this database (1988-1993), 1994 has NO Cageside-style timing analysis in "
     "Shane's Word doc -- only the Dan Wahlers narrative section exists under this year's Heading-1. That "
     "means entry order, ring/survival times, and elimination order are ALL UNKNOWN for every single "
     "participant this year, with the sole exception of Scott Steiner and Samu being named as 'the first two "
     "entrants' (exact order between them not specified). This is the leanest build in the database so far -- "
     "not a processing gap, a genuine gap in the available source material for this specific year.",
     "S029", "open", "2026-09-15"),
    ("F060", EVENT_ID, "events;entrants", "bret-hart;lex-luger", "is_winner", "needs_human_judgement",
     "The only Royal Rumble in history with a co-winner call. Bret Hart and Lex Luger went over the top rope "
     "at essentially the same instant; WWF's announcers declared BOTH the winner live (reportedly to gauge "
     "crowd reaction, since Luger's face turn was a going concern -- he was booed). S029's own text states "
     "that on review of the tape, Luger's feet 'obviously' hit the floor first, which under the match's own "
     "rules would make him the eliminated man and Bret Hart the sole legitimate winner -- but this was never "
     "corrected on-air or in WWF's official record, and the event is conventionally remembered/recorded as a "
     "dual win. Modeled here as BOTH men having is_winner=TRUE (so derived win-count stats credit both, "
     "matching convention) with events.csv's winner_id holding both ids as a semicolon list -- a deliberate "
     "deviation from every other event in this database, which has exactly one winner. No elimination row "
     "exists for either man, since crediting one as eliminating the other would mean silently resolving a "
     "dispute the source itself leaves open.",
     "S029", "open", "2026-09-15"),
    ("F061", EVENT_ID, "entrants", "*", "n/a", "unverified",
     "Only 29 participants are named in S029's Match Results text, one short of the presumed 30-man format "
     "consistent with 1989-1993's established standard (not explicitly re-stated as '30-man' for 1994 in "
     "either source this pass, so NOT assumed here -- entrant_count is left as 29, the actual count of named "
     "participants, rather than invented as 30). One entrant is likely missing from Dan Wahlers' own "
     "enumeration -- worth checking against an external source (Wikipedia/Cagematch) in a future fact-check "
     "pass to identify the 30th man, if one exists.",
     "S029", "open", "2026-09-15"),
    ("F062", EVENT_ID, "wrestlers", "sparky-plugg", "aliases_ring_names", "needs_human_judgement",
     "No source consulted this pass connects 'Sparky Plugg' to any other wrestler already or later in this "
     "database. Left as a fully distinct, fully UNKNOWN-bio new wrestler for now rather than assumed to be a "
     "renamed/returning performer -- worth a specific check in a future fact-check pass, following the same "
     "'don't assume, verify' approach already used successfully for Col. Mustafa (1992's F031, resolved).",
     "S029", "open", "2026-09-15"),
    ("F063", EVENT_ID, "wrestlers", "*", "real_name;dob;billed_height_m_at_event;billed_weight_kg_at_event;birthplace", "unverified",
     "15 wrestlers appear in this database for the first time via 1994 (Bam Bam Bigelow, Adam Bomb, Doink/"
     "Phil Apollo, Diesel, Great Kabuki, Jeff Jarrett, Kwang, Mo, Mabel, Sparky Plugg, Billy Gunn, Bart Gunn, "
     "Rick Steiner, Scott Steiner, Lex Luger) with zero bio data in this pass's source -- names only. Left "
     "entirely UNKNOWN, same pattern as every prior year's equivalent flag.",
     "S029", "open", "2026-09-15"),
    ("F064", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-15"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only.
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Bam Bam Bigelow", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "S029's Rumble participant list shortens this to 'Bam Bigelow', but the same document's own undercard results ('Tatanka pinned Bam Bam Bigelow') confirms the full ring name -- same person, not a separate wrestler. No bio data in either source this pass.", "S029"),
    ("Adam Bomb", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S029"),
    ("Doink", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "Doink The Clown", "", "", "S029 credits this Doink performance specifically to 'Phil Apollo' -- multiple performers played the Doink gimmick over the years, so this wrestler_id represents the Phil Apollo performance specifically, not the gimmick generally. No bio data in either source this pass.", "S029"),
    ("Diesel", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S029"),
    ("Great Kabuki", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S029"),
    ("Jeff Jarrett", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S029"),
    ("Kwang", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No bio data in either source this pass.", "S029"),
    ("Mo", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "Men on a Mission", "", "", "One half of Men on a Mission (w/ Mabel). No bio data in either source this pass.", "S029"),
    ("Mabel", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "Men on a Mission", "", "", "One half of Men on a Mission (w/ Mo). No bio data in either source this pass.", "S029"),
    ("Sparky Plugg", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "No identity connection to any other wrestler stated in either source this pass -- see F062. No bio data in either source this pass.", "S029"),
    ("Billy Gunn", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "The Smoking Gunns", "", "", "One half of The Smoking Gunns (w/ Bart Gunn). No bio data in either source this pass.", "S029"),
    ("Bart Gunn", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "The Smoking Gunns", "", "", "One half of The Smoking Gunns (w/ Billy Gunn). No bio data in either source this pass.", "S029"),
    ("Rick Steiner", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "The Steiner Brothers", "", "", "WWF debut per S028 (1993's chapter noted the Steiners' debut occurred at that show's undercard); first Rumble appearance is 1994. No bio data in either source this pass.", "S029"),
    ("Scott Steiner", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "The Steiner Brothers", "", "", "One of the first two Rumble entrants this year (exact order vs. Samu not specified). No bio data in either source this pass.", "S029"),
    ("Lex Luger", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Co-credited winner of this match alongside Bret Hart -- see F060 for the full controversy. No bio data in either source this pass.", "S029"),
]

reused = {
    "Bob Backlund": "bob-backlund", "Fatu": "fatu", "Owen Hart": "owen-hart",
    "Marty Jannetty": "marty-jannetty", "Rick Martel": "rick-martel", "Shawn Michaels": "shawn-michaels",
    "Samu": "samu", "Randy Savage": "randy-savage", "Tatanka": "tatanka",
    "Genichiro Tenryu": "genichiro-tenryu", "Greg Valentine": "greg-valentine", "Virgil": "virgil",
    "Bret Hart": "bret-hart",
    # "Crush" is Brian Adams' solo gimmick after Demolition's breakup -- same person already in
    # this database as "Demolition Crush" (wrestler_id demolition-crush, added 1990/1991).
    "Crush": "demolition-crush",
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
# ENTRANTS -- 29 named participants, everything except identity is UNKNOWN.
# ---------------------------------------------------------------------------
FIRST_TWO = {"Scott Steiner", "Samu"}
CO_WINNERS = {"Bret Hart", "Lex Luger"}

all_names = [
    "Bob Backlund", "Bam Bam Bigelow", "Adam Bomb", "Crush", "Doink", "Diesel", "Fatu",
    "Great Kabuki", "Owen Hart", "Marty Jannetty", "Jeff Jarrett", "Kwang", "Rick Martel",
    "Mo", "Mabel", "Shawn Michaels", "Sparky Plugg", "Samu", "Randy Savage", "Billy Gunn",
    "Bart Gunn", "Rick Steiner", "Scott Steiner", "Tatanka", "Genichiro Tenryu",
    "Greg Valentine", "Virgil", "Bret Hart", "Lex Luger",
]
assert len(all_names) == 29

entrant_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = name in CO_WINNERS
    note = ""
    if name in FIRST_TWO:
        note = "Confirmed as one of the first two entrants this match (exact order vs. the other not specified in S029) -- see F059."
    if name in CO_WINNERS:
        note = (note + " " if note else "") + "Co-credited winner -- see F060 for the full controversy."

    er = {
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": "", "entry_number_status": "UNKNOWN",
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
        "eliminated_by_ids": "",
        "elimination_clock_time": "", "elimination_clock_seconds": "",
        "ring_time": "", "ring_time_seconds": "",
        "ring_time_status": "UNKNOWN",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "FALSE",
        "is_final_two": "TRUE" if is_winner else "UNKNOWN",
        "is_final_three": "UNKNOWN", "is_final_four": "UNKNOWN",
        "surprise_entrant": "FALSE", "legend_returning": "FALSE", "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE", "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED" if is_winner or name in FIRST_TWO else "PROBABLE",
        "source_ids": "S029",
        "notes": note,
    }
    entrant_rows.append(er)

with open(os.path.join(DATA_DIR, "entrants.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ENTRANTS_FIELDS)
    for er in entrant_rows:
        writer.writerow(er)

# No eliminations.csv rows this year -- see F059/F060 for why.

# ---------------------------------------------------------------------------
# OTHER MATCHES ON THE SAME CARD
# ---------------------------------------------------------------------------
other_matches = [
    ("Tatanka", 1, "Bam Bam Bigelow", "", "Singles", "FALSE", "", "FALSE", "Win", "", "", "8:12", "Opener", "S029", "Pinned Bigelow."),
    ("Bam Bam Bigelow", 1, "Tatanka", "", "Singles", "FALSE", "", "FALSE", "Loss", "", "", "8:12", "Opener", "S029", "Pinned by Tatanka."),
    ("Bret Hart", 2, "Jacques Rougeau, Pierre Ouellet (The Quebecers)", "Owen Hart", "Tag", "TRUE", "World Tag Team Championship", "TRUE", "Loss", "", "TRUE", "16:48", "2nd match", "S029", "Lost the titles via referee's decision when Bret could not continue -- this is the match after which Owen Hart turned heel on his brother."),
    ("Owen Hart", 2, "Jacques Rougeau, Pierre Ouellet (The Quebecers)", "Bret Hart", "Tag", "TRUE", "World Tag Team Championship", "TRUE", "Loss", "", "TRUE", "16:48", "2nd match", "S029", "Turned heel on Bret Hart during/after this match -- a storyline turning point per S029."),
    ("Irwin R. Schyster", 3, "Razor Ramon", "", "Singles", "TRUE", "Intercontinental Championship", "TRUE", "Loss", "", "TRUE", "11:30", "3rd match", "S029", "Pinned by Ramon, who won the IC title."),
    ("The Undertaker", 4, "Yokozuna", "", "Singles", "TRUE", "World Heavyweight Championship", "FALSE", "Loss", "", "", "14:20", "Casket Match", "S029", "Casket Match -- ten midcard heels helped Yokozuna get Undertaker in the casket; Yokozuna retained the title. Followed by the 'Undertaker rises to the ceiling' angle."),
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
    "event_id": EVENT_ID, "event_name": "Royal Rumble 1994", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "1994-01-22", "venue": "Providence Civic Center",
    "city_region": "Providence, Rhode Island", "country": "United States",
    "attendance_official": "", "attendance_reported": 14500,
    "entry_interval_seconds": "UNKNOWN", "entrant_count": 29, "duration_total": "55:08",
    "duration_status": "PROBABLE",
    "winner_id": "bret-hart;lex-luger", "runner_up_id": "UNKNOWN",
    "final_two_ids": "bret-hart;lex-luger", "final_three_ids": "UNKNOWN",
    "final_four_ids": "UNKNOWN",
    "first_entrant_id": "UNKNOWN", "second_entrant_id": "UNKNOWN", "final_entrant_id": "UNKNOWN",
    "first_elimination_id": "UNKNOWN", "last_elimination_before_winner_id": "UNKNOWN",
    "eliminations_count": "UNKNOWN", "eliminators_count": "UNKNOWN",
    "surprise_entrants_count": "UNKNOWN",
    "champions_in_field_count": "UNKNOWN", "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": "N/A",
    "commentary_team": "Vince McMahon, Ted DiBiase", "ring_announcer": "Howard Finkel",
    "referees": "Not identified in either source consulted this pass",
    "special_rules": (
        "THE ONLY ROYAL RUMBLE IN HISTORY WITH A CO-WINNER CALL. Bret Hart and Lex Luger went over the top "
        "rope at essentially the same instant; WWF announced BOTH as the winner live. S029's own text states "
        "that replay showed Luger's feet hit the floor first, which would make Bret Hart the sole legitimate "
        "winner under the match's own rules -- but this was never corrected on-air or in the official record. "
        "See F060 for the full writeup and how this is modeled in the data (both men have is_winner=TRUE; no "
        "eliminations.csv row exists for either, since crediting one as eliminating the other would mean "
        "silently resolving a dispute the source itself leaves open). Scott Steiner and Samu were the first "
        "two entrants (exact order not specified). This is the leanest build in the database so far -- no "
        "Cageside-style timing analysis exists for 1994, so entry order, ring times, and elimination order "
        "are UNKNOWN for every other participant -- see F059."
    ),
    "title_on_the_line": "FALSE", "championship_implications": "None in the Rumble match itself, though the WWF Championship (Yokozuna def. Undertaker, Casket Match) and World Tag Team Championship (The Quebecers def. Bret & Owen Hart) both changed hands or were defended earlier on the same card",
    "winners_reward": "UNKNOWN -- neither source states a guaranteed title-shot stipulation explicitly for this specific year, though the WrestleMania-title-shot convention (established 1993) is generally assumed to have continued; not directly confirmed this pass",
    "historical_significance": "The only Royal Rumble in history with a co-winner call (Bret Hart/Lex Luger) -- see F060. Owen Hart turned heel on his brother Bret during/after their World Tag Team Championship match earlier on the card, kicking off a year-long feud that included an acclaimed WrestleMania X match. The Undertaker/Yokozuna Casket Match closed with the widely-mocked 'Undertaker rises to the ceiling' angle. Rick and Scott Steiner's first Royal Rumble appearance.",
    "notes": "Only 29 of a presumed 30-man field are named in S029 -- see F061. Entry order, ring times, and elimination order/credits are UNKNOWN for every participant this year (no Cageside-style timing analysis exists for 1994, unlike 1988-1993) -- see F059. This is the leanest build in the database so far, a genuine gap in the source material rather than a processing shortfall.",
    "data_quality_status": "PROBABLE", "source_ids": "S029",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"1994 build complete (schema v2): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants (0 eliminations -- see F059/F060), "
      f"{len(other_matches)} other-match rows, {len(sources)} sources logged, {len(flags)} open flags.")
