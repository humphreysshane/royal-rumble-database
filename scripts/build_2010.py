# -*- coding: utf-8 -*-
"""
Builds all rows for the 2010 Royal Rumble -- schema v2.

UNIQUE SITUATION: unlike every other year in this database, Shane's Word
doc has ZERO content for 2010 -- literally just an empty "2010 Royal
Rumble Stats" Heading-1 with nothing under it (confirmed by direct
paragraph-by-paragraph inspection). This is a genuine gap in the source
material, not a processing error. Per Shane's explicit instruction, this
one year is built from EXTERNAL research (breaking the project's normal
document-first phasing, as a one-time approved exception) rather than left
as a bare stub or skipped.

Research was done via a dedicated multi-source pass (12 independent pages
across Wikipedia, Cagematch, ProFightDB, WWE.com's own official history/
stats pages, and several reputable wrestling news/recap sites), applying
this project's normal 2-source-for-CONFIRMED rule throughout. See sources
S085-S096 below for the full list and what each contributed.

WHAT'S DIFFERENT FROM A SHANE'S-DOCUMENT YEAR: there is no Cageside-style
frame-by-frame timing data for 2010 anywhere in the researched sources (no
site tracked buzzer-by-buzzer entrance times or per-wrestler survival
times to the second the way Shane's own blog-style posts do for other
years). What IS available and well-corroborated: the full entry order
(1-30), the full elimination chain (who eliminated whom, in order 1-29),
event-level facts (date, venue, attendance, commentary), and a handful of
specific individually-sourced clock times (the winner's ring time, the
match's total duration). Per-wrestler ring_time/elimination_clock_time is
therefore UNKNOWN for most entrants -- this is a genuine gap in what
research turned up, not an oversight, and is NOT filled with an assumed
90-second-interval model (that would be inventing data; Shane's own
documented years show real buzzer gaps vary considerably, e.g. 1:16 to
2:23 in 2011, so a flat assumption would be actively misleading).

SOURCES CONSULTED THIS PASS:
  S085 Wikipedia, "Royal Rumble (2010)"                                  tier 10
  S086 Wikipedia, "Royal Rumble match" (records/stats article)           tier 10
  S087 Cagematch.net, WWE Royal Rumble 2010 event + match pages          tier 4
  S088 ProFightDB, WWE Royal Rumble 2010 card                            tier 5
  S089 WWE.com, official Royal Rumble 2010 history page + "Top 25 Royal
       Rumble Match Statistics" page                                     tier 1
  S090 Rajah.com, "Royal Rumble 2010 List of Entrants & Eliminations"    tier 12
  S091 OnlineWorldOfWrestling.com, WWE Royal Rumble 2010 results         tier 12
  S092 WrestlingNewsSource.com, "Full WWE Royal Rumble 2010 Entrants &
       Eliminations List"                                                tier 12
  S093 TJR Wrestling, "WWE Royal Rumble 2010 Review"                     tier 7
  S094 TheSmackdownHotel.com, WWE Royal Rumble 2010 match card & results tier 12
  S095 TheSportster, "Edge's 8 Royal Rumble Appearances, Ranked"         tier 12
  S096 Cageside Seats, "WWE Royal Rumble 2010 Match Time and Statistics" tier 7

CONFIRMED (2+ independently agreeing sources):
  - Date (Jan 31, 2010), venue (Philips Arena, Atlanta, GA), attendance
    (16,697) -- 3-5 sources each.
  - Full 30-man entry order -- 5 sources agree exactly.
  - Full 29-elimination chain (who eliminated whom, in order) -- 4 sources
    agree exactly, and the chain is internally consistent (accounts for
    all 29 non-winner entrants with no gaps or overlaps).
  - Winner (Edge), runner-up (John Cena), final four (Edge, Cena, Batista,
    Shawn Michaels).
  - Total match duration (49:24) -- 2 sources (a 3rd, single-sourced
    "49:23" is noted but treated as a 1-second rounding discrepancy, not a
    genuine conflict worth a flag).
  - Edge's winning ring time (7:19, a Rumble record for shortest winning
    time until Brock Lesnar broke it in 2022) -- 3 sources including
    WWE.com's own official stats page. An initial single-source figure of
    "7:37" was checked against this and rejected as a likely transcription
    error (contradicted 3-to-1).
  - Shawn Michaels' 6 credited eliminations (Triple H, Ted DiBiase, John
    Morrison, Cody Rhodes, Carlito solo, plus the shared McIntyre
    elimination with Triple H) -- verified by directly tallying the
    sourced elimination chain itself, cross-checked against 2 sources.
    A single-source claim of "10" (TJR's recap) does not reconcile with
    the full chain and is treated as an error in that recap, not entered.
  - Beth Phoenix as the second woman ever to compete in a standard 30-man
    Royal Rumble match (after Chyna in 1999 and 2000) -- stated directly
    by WWE.com's own official recap.
  - Kane's 2010 Rumble being his 12th career appearance -- this figure
    (from a single external source, TJR) is independently reproduced by
    this database's OWN running entrant count (11 prior appearances,
    1999-2009, before this build) once this year is added -- a DERIVED
    internal cross-check, not a second external source, but a real one.

PROBABLE (single source only):
  - John Cena's approximate ring time as the longest-surviving loser
    (~22:11, WrestlingNewsSource only, not cross-checked against a second
    source) -- included as PROBABLE.
  - Commentary team, ring announcers, backstage interviewer (Wikipedia
    only for the full breakdown, though the Cole/Lawler/Striker portion of
    commentary is independently corroborated by OWW).

CONFLICTING (sources disagree, both preserved, see flags.csv):
  - 3 of 5 undercard title-match times differ by a few seconds to a
    minute between Wikipedia and ProFightDB/Cagematch -- both figures are
    preserved in the other_matches.csv notes field rather than picking
    one; match_duration left blank on those rows. See F247.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from schema import (
    ENTRANTS_FIELDS, ELIMINATIONS_FIELDS, EVENTS_FIELDS, OTHER_MATCHES_FIELDS,
    slugify, mmss_to_seconds,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EVENT_ID = "RR2010M"


def mmss(t):
    parts = [int(p) for p in t.split(":")]
    return parts[0] * 60 + parts[1] if len(parts) == 2 else parts[0] * 3600 + parts[1] * 60 + parts[2]


# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S085", "Wikipedia, 'Royal Rumble (2010)'", "wikipedia", "https://en.wikipedia.org/wiki/Royal_Rumble_(2010)", 10, "Wikipedia and similar reference sites", "2026-09-16",
     "Full event card, entrant/elimination table, date/venue/attendance, commentary team. Live-fetched this pass."),
    ("S086", "Wikipedia, 'Royal Rumble match' (records/stats article)", "wikipedia", "https://en.wikipedia.org/wiki/Royal_Rumble_match", 10, "Wikipedia and similar reference sites", "2026-09-16",
     "General Royal Rumble match records article; used to cross-check Edge's shortest-winning-time record and Beth Phoenix's status as the 2nd woman to compete in a standard 30-man Rumble. Live-fetched this pass."),
    ("S087", "Cagematch.net, WWE Royal Rumble 2010 event + match pages", "cagematch", "https://www.cagematch.net/?id=1&nr=44791", 4, "Cagematch", "2026-09-16",
     "Independent entrant/elimination table used to cross-verify the full 30-man order and 29-elimination chain against Wikipedia. Live-fetched this pass; the dedicated card sub-page could not be reached (rate-limited) so undercard match times from this source are taken via ProFightDB's mirror of the same data instead."),
    ("S088", "ProFightDB, WWE Royal Rumble 2010 card", "other_stats_site", "http://www.profightdb.com/cards/wwe/royal-rumble-3910-8287.html", 5, "ProFightDB / Internet Wrestling Database", "2026-09-16",
     "Independent card listing with undercard match times; used to cross-check event facts and flag 3 undercard-time discrepancies against Wikipedia. Live-fetched this pass."),
    ("S089", "WWE.com, official Royal Rumble 2010 history page + 'Top 25 Royal Rumble Match Statistics' page", "wwe_official", "https://www.wwe.com/shows/royalrumble/history/2010", 1, "WWE / official sources", "2026-09-16",
     "WWE's own official record of the event and of Edge's shortest-winning-time record (7:19) and Beth Phoenix's 'only the second Diva' status. Highest-tier source used this pass. Live-fetched this pass."),
    ("S090", "Rajah.com, 'Royal Rumble 2010 List of Entrants & Eliminations'", "other_stats_site", "https://rajah.com/node/18354", 12, "Other reputable statistical/historical wrestling sites", "2026-09-16",
     "Independent entrant/elimination list, used as a 4th cross-check on the full order and chain. Live-fetched this pass."),
    ("S091", "OnlineWorldOfWrestling.com, WWE Royal Rumble 2010 results", "other_stats_site", "https://www.onlineworldofwrestling.com/results/wwe/wweppv/royalrumble/royalrumble10/", 12, "Other reputable statistical/historical wrestling sites", "2026-09-16",
     "Independent results/commentary-team cross-check. Live-fetched this pass."),
    ("S092", "WrestlingNewsSource.com, 'Full WWE Royal Rumble 2010 Entrants & Eliminations List'", "other_stats_site", "https://www.wrestlingnewssource.com/news/14543/Full-WWE-Royal-Rumble-2010-Entrants-Eliminations-List/", 12, "Other reputable statistical/historical wrestling sites", "2026-09-16",
     "5th independent cross-check on entry/elimination order; sole source for John Cena's approximate ~22:11 ring time (PROBABLE, not cross-checked) and for the 49:23 (vs. 49:24 elsewhere) minor duration discrepancy. Live-fetched this pass."),
    ("S093", "TJR Wrestling, 'WWE Royal Rumble 2010 Review'", "wrestling_publication", "https://tjrwrestling.net/review/tjr-review-wwe-royal-rumble-2010/", 7, "Wrestling Observer / reputable wrestling publications", "2026-09-16",
     "Recap/review; sole source for Kane's '12th Rumble appearance' framing (independently reproduced by this database's own running count, see script docstring) and for a since-rejected '10 eliminations for Michaels' figure that does not reconcile with the sourced chain. Live-fetched this pass."),
    ("S094", "TheSmackdownHotel.com, WWE Royal Rumble 2010 match card & results", "other_stats_site", "https://www.thesmackdownhotel.com/events-results/ppv-special/wwe-royal-rumble-2010", 12, "Other reputable statistical/historical wrestling sites", "2026-09-16",
     "Card/date/venue cross-check. Live-fetched this pass."),
    ("S095", "TheSportster, \"Edge's 8 Royal Rumble Appearances, Ranked\"", "other_stats_site", "https://www.thesportster.com/wwe-edge-royal-rumble-appearances-ranked/", 12, "Other reputable statistical/historical wrestling sites", "2026-09-16",
     "3rd independent source for Edge's 7:19 winning-time record. Live-fetched this pass."),
    ("S096", "Cageside Seats, 'WWE Royal Rumble 2010 Match Time and Statistics'", "wrestling_publication", "https://www.cagesideseats.com/wwe/2017/1/22/14343366/wwe-royal-rumble-2010-match-time-statistics", 7, "Wrestling Observer / reputable wrestling publications", "2026-09-16",
     "Duration/statistics cross-check. Live-fetched this pass."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)
SRC = "S085;S086;S087;S088;S089;S090;S091;S092"

# ---------------------------------------------------------------------------
# ENTRY ORDER (CONFIRMED -- 5 independent sources agree exactly)
# ---------------------------------------------------------------------------
ENTRY_NUMBERS = {
    "Dolph Ziggler": 1, "Evan Bourne": 2, "CM Punk": 3, "JTG": 4, "The Great Khali": 5,
    "Beth Phoenix": 6, "Zack Ryder": 7, "Triple H": 8, "Drew McIntyre": 9, "Ted DiBiase": 10,
    "John Morrison": 11, "Kane": 12, "Cody Rhodes": 13, "MVP": 14, "Carlito": 15,
    "The Miz": 16, "Matt Hardy": 17, "Shawn Michaels": 18, "John Cena": 19, "Shelton Benjamin": 20,
    "Yoshi Tatsu": 21, "Big Show": 22, "Mark Henry": 23, "Chris Masters": 24, "R-Truth": 25,
    "Jack Swagger": 26, "Kofi Kingston": 27, "Chris Jericho": 28, "Edge": 29, "Batista": 30,
}
assert len(ENTRY_NUMBERS) == 30

# ---------------------------------------------------------------------------
# ELIMINATION CHAIN (CONFIRMED -- 4 independent sources agree exactly; the
# chain is internally consistent, accounting for all 29 non-winner
# entrants with no gaps or overlaps).
# name -> (order_in_match, [eliminator names], is_shared, is_self)
# ---------------------------------------------------------------------------
ELIMINATION_CHAIN = {
    "Evan Bourne": (1, ["CM Punk"], False, False),
    "Dolph Ziggler": (2, ["CM Punk"], False, False),
    "JTG": (3, ["CM Punk"], False, False),
    "The Great Khali": (4, ["Beth Phoenix"], False, False),
    "Beth Phoenix": (5, ["CM Punk"], False, False),
    "Zack Ryder": (6, ["CM Punk"], False, False),
    "CM Punk": (7, ["Triple H"], False, False),
    "The Miz": (8, ["MVP"], False, False),
    "MVP": (9, [], False, True),  # self-eliminated
    "Matt Hardy": (10, ["Kane"], False, False),
    "Kane": (11, ["Triple H"], False, False),
    "Carlito": (12, ["Shawn Michaels"], False, False),
    "Cody Rhodes": (13, ["Shawn Michaels"], False, False),
    "Ted DiBiase": (14, ["Shawn Michaels"], False, False),
    "John Morrison": (15, ["Shawn Michaels"], False, False),
    "Drew McIntyre": (16, ["Triple H", "Shawn Michaels"], True, False),
    "Triple H": (17, ["Shawn Michaels"], False, False),
    "Shelton Benjamin": (18, ["John Cena"], False, False),
    "Yoshi Tatsu": (19, ["John Cena"], False, False),
    "Chris Masters": (20, ["Big Show"], False, False),
    "Mark Henry": (21, ["R-Truth"], False, False),
    "Big Show": (22, ["R-Truth"], False, False),
    "Jack Swagger": (23, ["Kofi Kingston"], False, False),
    "R-Truth": (24, ["Kofi Kingston"], False, False),
    "Kofi Kingston": (25, ["John Cena"], False, False),
    "Chris Jericho": (26, ["Edge"], False, False),
    "Shawn Michaels": (27, ["Batista"], False, False),
    "Batista": (28, ["John Cena"], False, False),
    "John Cena": (29, ["Edge"], False, False),  # the winning elimination
}
assert len(ELIMINATION_CHAIN) == 29
assert set(ELIMINATION_CHAIN) | {"Edge"} == set(ENTRY_NUMBERS)

FINAL_TWO = {"Edge", "John Cena"}
FINAL_THREE = {"Edge", "John Cena", "Batista"}
FINAL_FOUR = {"Edge", "John Cena", "Batista", "Shawn Michaels"}

# Individually-sourced clock times (everything else is UNKNOWN -- no
# per-wrestler timing graphic exists for this year in any researched
# source, unlike Shane's own document years).
MATCH_TOTAL = "49:24"
RING_TIME = {
    "Edge": ("7:19", "CONFIRMED"),      # WWE.com official + 2 more sources
    "John Cena": ("22:11", "PROBABLE"),  # single source (WrestlingNewsSource), not cross-checked
}
# John Cena, as the final elimination, necessarily goes out at the exact
# match-ending instant -- DERIVED from the definition of how a Rumble
# ends (the last two are narrowed to one at that moment), not guessed.
ELIM_CLOCK = {"John Cena": (MATCH_TOTAL, "DERIVED")}

# ---------------------------------------------------------------------------
# WRESTLERS -- new people only (only 2 this year -- most of the 2010 field
# already exists in this database from the 2009/2011 builds).
# ---------------------------------------------------------------------------
new_wrestlers = [
    ("Evan Bourne", "", "UNKNOWN", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #2. One of CM Punk's first 5 victims in Punk's extended elimination stretch to open the match. No exact ring time known this pass -- no per-wrestler timing data exists for this externally-researched year.", SRC),
    ("Beth Phoenix", "", "UNKNOWN", "F", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Entered #6 -- only the second woman ever to compete in a standard 30-man Royal Rumble match, after Chyna (1999 and 2000), per WWE.com's own official recap. Eliminated The Great Khali by distracting him with a kiss before hauling him over the top rope; was eliminated herself by CM Punk shortly after. No exact ring time known this pass.", SRC),
]

reused = {
    "Dolph Ziggler": "dolph-ziggler", "CM Punk": "cm-punk", "JTG": "jtg", "The Great Khali": "the-great-khali",
    "Zack Ryder": "zack-ryder", "Triple H": "hunter-hearst-helmsley", "Drew McIntyre": "drew-mcintyre",
    "Ted DiBiase": "ted-dibiase-jr", "John Morrison": "johnny-nitro", "Kane": "kane", "Cody Rhodes": "cody-rhodes",
    "MVP": "mvp", "Carlito": "carlito", "The Miz": "the-miz", "Matt Hardy": "matt-hardy",
    "Shawn Michaels": "shawn-michaels", "John Cena": "john-cena", "Shelton Benjamin": "shelton-benjamin",
    "Yoshi Tatsu": "yoshi-tatsu", "Big Show": "big-show", "Mark Henry": "mark-henry", "Chris Masters": "chris-masters",
    "R-Truth": "r-truth", "Jack Swagger": "jack-swagger", "Kofi Kingston": "kofi-kingston",
    "Chris Jericho": "chris-jericho", "Edge": "edge", "Batista": "batista",
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
# ENTRANTS -- all 30, full entry order and elimination order known;
# per-wrestler ring_time UNKNOWN except Edge/John Cena (see above).
# ---------------------------------------------------------------------------
all_names = sorted(ENTRY_NUMBERS, key=lambda n: ENTRY_NUMBERS[n])

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Edge")
    entry = ENTRY_NUMBERS[name]

    if is_winner:
        elim_no, elim_by, is_shared, is_self = None, [], False, False
    else:
        elim_no, elim_by, is_shared, is_self = ELIMINATION_CHAIN[name]

    ring_time, ring_time_status = RING_TIME.get(name, ("", "UNKNOWN"))
    ring_time_s = mmss_to_seconds(ring_time) if ring_time else ""
    elim_clock, elim_clock_status = ELIM_CLOCK.get(name, ("", ""))
    elim_clock_s = mmss(elim_clock) if elim_clock else ""

    notes_parts = []
    if name == "Edge":
        notes_parts.append("Entered #29 (a surprise return from a torn Achilles tendon suffered mid-2009) and won his first career Royal Rumble by eliminating John Cena. His 7:19 ring time set the record for shortest time spent in the match by a winner, a record that stood until Brock Lesnar broke it in 2022 -- confirmed by WWE.com's own official stats page plus 2 more independent sources.")
    elif name == "John Cena":
        notes_parts.append("Runner-up, eliminated by Edge in the match's final moment (elimination_clock_time DERIVED as equal to the match's total duration, since the final two are necessarily narrowed to one at that exact instant). His own ring time is reported by only 1 source (~22:11, PROBABLE, not cross-checked) as the longest-surviving entrant of the match.")
    elif name == "Shawn Michaels":
        notes_parts.append("Credited with 6 eliminations this match (Triple H, Ted DiBiase, John Morrison, Cody Rhodes, Carlito solo, plus the shared Drew McIntyre elimination with Triple H) -- the most of any wrestler in the match, verified directly against the sourced elimination chain. A single-source claim of 10 eliminations (TJR's recap) does not reconcile with this chain and was not used.")
    elif name == "CM Punk":
        notes_parts.append("Eliminated 5 wrestlers (Evan Bourne, Dolph Ziggler, JTG, Beth Phoenix, Zack Ryder) in an extended stretch near the start of the match before being eliminated himself by Triple H.")
    elif name == "MVP":
        notes_parts.append("Self-eliminated (order #9) -- modeled with is_self_elimination=TRUE, same convention as Kane (1999), Drew Carey (2001), and Hornswoggle (2008).")
    elif name == "Beth Phoenix":
        notes_parts.append("Only the second woman ever to compete in a standard 30-man Royal Rumble match, after Chyna (1999 and 2000), per WWE.com's own official recap. Eliminated The Great Khali by distracting him with a kiss before hauling him over the top rope.")
    elif name == "Kane":
        notes_parts.append("This database's own running count shows this is Kane's 12th career Royal Rumble appearance (11 prior, 1999-2009, before this build) -- independently matching a single external source's claim (TJR) via this database's own internal data rather than a second external source.")
    elif name == "Ted DiBiase":
        notes_parts.append("Reuses this database's existing 'ted-dibiase-jr' wrestler_id (same Legacy-stable performer as the 2009/2011 builds) -- NOT the same person as 'ted-dibiase' (Ted DiBiase Sr., the Million Dollar Man), a separate existing wrestler_id in this database. Careful disambiguation performed this pass to avoid an incorrect identity merge.")
    elif name == "John Morrison":
        notes_parts.append("Reuses this database's existing 'johnny-nitro' wrestler_id -- same performer, renamed gimmick, consistent with prior-year precedent.")
    elif name == "Triple H":
        notes_parts.append("Reuses this database's existing 'hunter-hearst-helmsley' wrestler_id, consistent with prior-year precedent.")
    note = " ".join(notes_parts)

    for eliminator in elim_by:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": elim_no,
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
            "assisting_wrestler_ids": ";".join(wrestler_ids[e] for e in elim_by if e != eliminator) if is_shared else "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": ENTRY_NUMBERS.get(eliminator, ""),
            "elimination_clock_time": elim_clock, "elimination_clock_seconds": elim_clock_s,
            "elimination_type": "over_top_rope",
            "elimination_method": "",
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "FALSE" if is_shared else "TRUE", "is_shared": "TRUE" if is_shared else "FALSE",
            "is_accidental": "FALSE",
            "is_self_elimination": "FALSE",
            "is_storyline_related": "UNKNOWN",
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE",
            "simultaneous_group_id": "mcintyre_double" if name == "Drew McIntyre" else "",
            "data_quality_status": "CONFIRMED",
            "source_ids": SRC,
            "notes": "",
        })
    if is_self:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": elim_no,
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wid,
            "assisting_wrestler_ids": "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": entry,
            "elimination_clock_time": "", "elimination_clock_seconds": "",
            "elimination_type": "voluntary_exit",
            "elimination_method": "",
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "TRUE", "is_shared": "FALSE",
            "is_accidental": "UNKNOWN",
            "is_self_elimination": "TRUE",
            "is_storyline_related": "UNKNOWN",
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE",
            "simultaneous_group_id": "",
            "data_quality_status": "CONFIRMED",
            "source_ids": SRC,
            "notes": "Self-eliminated -- see script docstring/notes for convention precedent.",
        })

    er = {
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": "CONFIRMED",
        "ring_name_at_time": name, "name_displayed_at_event": name,
        "prior_rumble_appearances_count": "", "rumble_appearance_no": "",
        "is_first_rumble_appearance": "", "previous_rumble_year": "",
        "previous_rumble_result": "", "previous_rumble_elimination_no": "",
        "is_rumble_debut": "", "is_company_debut": "UNKNOWN", "company_debut_date": "",
        "is_returning_wrestler": "TRUE" if name == "Edge" else "",
        "absence_length": "~8 months (torn Achilles tendon, mid-2009)" if name == "Edge" else "",
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
        "elim_number": "" if is_winner else elim_no, "elim_number_status": "N/A" if is_winner else "CONFIRMED",
        "eliminated_by_ids": ";".join(wrestler_ids[e] for e in elim_by) if elim_by else (wid if is_self else ""),
        "elimination_clock_time": elim_clock, "elimination_clock_seconds": elim_clock_s,
        "ring_time": ring_time, "ring_time_seconds": ring_time_s,
        "ring_time_status": ring_time_status,
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "TRUE" if is_self else "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if name == "John Cena" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "TRUE" if name == "Edge" else "FALSE",
        "legend_returning": "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE",
        "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": SRC,
        "notes": note,
    }
    entrant_rows.append(er)

# Fill in each eliminator's wrestlers_eliminated_ids / counts from elim_rows
# (excluding self-eliminations from eliminator credit).
elim_credit = {}
for row in elim_rows:
    if row["eliminator_wrestler_id"] != row["eliminated_wrestler_id"]:
        elim_credit.setdefault(row["eliminator_wrestler_id"], []).append(row["eliminated_wrestler_id"])
for er in entrant_rows:
    credited = elim_credit.get(er["wrestler_id"], [])
    if credited:
        er["wrestlers_eliminated_count"] = len(credited)
        er["wrestlers_eliminated_ids"] = ";".join(credited)
        er["solo_eliminations_count"] = sum(1 for r in elim_rows if r["eliminator_wrestler_id"] == er["wrestler_id"] and r["eliminated_wrestler_id"] != er["wrestler_id"] and r["is_solo"] == "TRUE")
        er["assisted_eliminations_count"] = sum(1 for r in elim_rows if r["eliminator_wrestler_id"] == er["wrestler_id"] and r["eliminated_wrestler_id"] != er["wrestler_id"] and r["is_solo"] == "FALSE")

with open(os.path.join(DATA_DIR, "entrants.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ENTRANTS_FIELDS)
    for er in entrant_rows:
        writer.writerow(er)

with open(os.path.join(DATA_DIR, "eliminations.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ELIMINATIONS_FIELDS)
    for row in elim_rows:
        writer.writerow(row)

# ---------------------------------------------------------------------------
# OTHER MATCHES -- undercard, only wrestlers who already have a
# wrestler_id (per this database's established convention). Mickie James
# and Michelle McCool (Women's Title match) and the 10-Diva tag match are
# skipped -- none of those participants exist in this database yet, and
# creating new wrestler_ids solely for an undercard appearance is outside
# this project's scope (the Royal Rumble MATCH is the focus).
# ---------------------------------------------------------------------------
other_matches = [
    # (wrestler, match#, opponents, match_type, champ_match, title, was_champ, result, notes)
    ("Christian", 1, "Ezekiel Jackson", "Singles", "TRUE", "ECW Championship", "TRUE", "won",
     "Retained. Match time CONFLICTING between sources (11:49 per Wikipedia, 11:59 per ProFightDB) -- both preserved here, neither picked. See F247."),
    ("Ezekiel Jackson", 1, "Christian", "Singles", "TRUE", "ECW Championship", "FALSE", "lost", ""),
    ("The Miz", 2, "MVP", "Singles", "TRUE", "WWE United States Championship", "TRUE", "won",
     "Retained. Match time agrees across sources (7:30)."),
    ("MVP", 2, "The Miz", "Singles", "TRUE", "WWE United States Championship", "FALSE", "lost", ""),
    ("Sheamus", 3, "Randy Orton", "Singles", "TRUE", "WWE Championship", "TRUE", "won",
     "Retained by disqualification. Match time CONFLICTING between sources (11:24 per Wikipedia, 12:24 per ProFightDB) -- both preserved here, neither picked. See F247."),
    ("Randy Orton", 3, "Sheamus", "Singles", "TRUE", "WWE Championship", "FALSE", "lost", ""),
    ("The Undertaker", 4, "Rey Mysterio", "Singles", "TRUE", "World Heavyweight Championship", "TRUE", "won",
     "Retained. Match time CONFLICTING between sources by 2 seconds only (11:09 per Wikipedia, 11:07 per ProFightDB) -- a negligible discrepancy, both noted rather than picked. See F247."),
    ("Rey Mysterio", 4, "The Undertaker", "Singles", "TRUE", "World Heavyweight Championship", "FALSE", "lost", ""),
]
# Existing wrestler_ids for undercard-only participants (not Rumble
# entrants this year, so not in the `reused` dict above).
UNDERCARD_IDS = {
    "Christian": "christian", "Ezekiel Jackson": "ezekiel-jackson",
    "Sheamus": "sheamus", "Randy Orton": "randy-orton",
    "The Undertaker": "the-undertaker", "Rey Mysterio": "rey-mysterio",
}

other_match_rows = []
for wname, num, opp, mtype, is_champ_match, title, was_champ, result, note in other_matches:
    wid = wrestler_ids.get(wname) or reused.get(wname) or UNDERCARD_IDS.get(wname)
    if not wid:
        continue
    other_match_rows.append({
        "event_id": EVENT_ID, "wrestler_id": wid, "match_number_on_card": num,
        "opponents": opp, "partners": "", "match_type": mtype,
        "championship_match": is_champ_match, "title_involved": title,
        "was_champion_entering": was_champ, "result": result,
        "won_title": "TRUE" if (result == "won" and was_champ == "FALSE") else "FALSE",
        "lost_title": "TRUE" if (result == "lost" and was_champ == "TRUE") else "FALSE",
        "match_duration": "", "position_on_card": num, "time_before_rumble": "TRUE",
        "data_quality_status": "CONFIRMED" if "CONFLICTING" not in note else "CONFLICTING",
        "source_ids": "S085;S088", "notes": note,
    })
with open(os.path.join(DATA_DIR, "other_matches.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=OTHER_MATCHES_FIELDS)
    for row in other_match_rows:
        writer.writerow(row)

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F244", EVENT_ID, "events;entrants;eliminations", "*", "n/a", "external_research_exception",
     "Shane's document has NO content whatsoever for 2010 (confirmed by direct paragraph-by-paragraph "
     "inspection -- a bare empty Heading-1). Per Shane's explicit instruction (session of 2026-09-16), this "
     "one year was built from external research rather than left as a stub or skipped, as a one-time approved "
     "exception to the project's normal document-first phasing. See script docstring for the full source list "
     "and methodology.",
     SRC, "open", "2026-09-16"),
    ("F245", EVENT_ID, "entrants", "*", "ring_time;elimination_clock_time", "unverified",
     "No per-wrestler timing graphic (Cageside-style buzzer/entrance/survival data) exists in any researched "
     "source for this year, unlike Shane's own document years. Only 2 individual clock times are known: Edge's "
     "7:19 winning ring time (CONFIRMED, 3 sources) and John Cena's approximate 22:11 ring time (PROBABLE, 1 "
     "source). Deliberately NOT filled with an assumed 90-second-interval model for the other 28 entrants -- "
     "Shane's own documented years show real buzzer gaps vary considerably (e.g. 1:16-2:23 in 2011), so a flat "
     "assumption would be actively misleading, not merely incomplete. Left UNKNOWN.",
     SRC, "open", "2026-09-16"),
    ("F246", EVENT_ID, "wrestlers", "evan-bourne;beth-phoenix", "real_name;dob;birthplace", "unverified",
     "Bio data added for 2 previously-unseen wrestlers this pass (Evan Bourne, Beth Phoenix) with zero bio "
     "data gathered this pass -- names only. Left entirely UNKNOWN, same pattern as every prior year's "
     "equivalent flag.",
     SRC, "open", "2026-09-16"),
    ("F247", EVENT_ID, "other_matches", "christian;ezekiel-jackson;sheamus;randy-orton;the-undertaker;rey-mysterio", "match_duration", "conflicting",
     "3 of the 4 corroborated undercard title matches have match-time figures that differ between Wikipedia "
     "and ProFightDB (ECW Title: 11:49 vs 11:59; WWE Title: 11:24 vs 12:24; World Heavyweight Title: 11:09 vs "
     "11:07, a negligible 2-second gap). A third independent source (Cagematch's own dedicated card page) "
     "could not be reached this pass (rate-limited) to break the tie. Both figures are preserved in each "
     "match's notes field rather than picking one; match_duration itself left blank on the affected rows. The "
     "WWE Women's Championship match (Mickie James def. Michelle McCool) and the 10-Diva tag match are not "
     "logged in other_matches.csv at all -- neither Mickie James nor Michelle McCool (nor most of the 10-Diva "
     "match's participants) exist as wrestler_ids in this database yet, and creating new entries solely for an "
     "undercard appearance is outside this project's current scope (the Royal Rumble MATCH itself is the "
     "focus). Flagging this gap rather than silently omitting it.",
     "S085;S088", "open", "2026-09-16"),
    ("F248", EVENT_ID, "events;entrances/moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-16"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2010", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2010-01-31", "venue": "Philips Arena",
    "city_region": "Atlanta, Georgia", "country": "United States",
    "attendance_official": "", "attendance_reported": 16697,
    "entry_interval_seconds": 90, "entrant_count": 30, "duration_total": MATCH_TOTAL,
    "duration_status": "CONFIRMED",
    "winner_id": "edge", "runner_up_id": "john-cena",
    "final_two_ids": "edge;john-cena",
    "final_three_ids": "edge;john-cena;batista",
    "final_four_ids": "edge;john-cena;batista;shawn-michaels",
    "first_entrant_id": "dolph-ziggler", "second_entrant_id": "evan-bourne", "final_entrant_id": "batista",
    "first_elimination_id": "evan-bourne", "last_elimination_before_winner_id": "john-cena",
    "eliminations_count": 29, "eliminators_count": 12,
    "surprise_entrants_count": 1,
    "champions_in_field_count": "UNKNOWN", "hall_of_famers_in_field_count": "UNKNOWN",
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Michael Cole and Jerry Lawler (Raw); Matt Striker (SmackDown)",
    "ring_announcer": "Justin Roberts (Raw), Tony Chimel (SmackDown), Savannah (ECW)",
    "referees": "UNKNOWN",
    "special_rules": "",
    "title_on_the_line": "FALSE",
    "championship_implications": "No title implications for the Rumble match itself; see other_matches.csv for the 4 undercard title matches on the same show.",
    "winners_reward": "UNKNOWN -- no WrestleMania main-event stipulation was yet standard for the Rumble winner in 2010 (that convention solidified in later years); not stated by any researched source for this specific event.",
    "historical_significance": (
        "Edge's only career Royal Rumble win, achieved as a surprise #29 entrant returning from a torn "
        "Achilles tendon suffered mid-2009. His 7:19 ring time set the record for shortest time spent in the "
        "match by a winner, standing until Brock Lesnar broke it in 2022. Beth Phoenix became only the second "
        "woman ever to compete in a standard 30-man Royal Rumble match, after Chyna (1999 and 2000), "
        "eliminating The Great Khali by distracting him with a kiss before being eliminated herself by CM "
        "Punk. CM Punk eliminated 5 wrestlers in an extended stretch near the start of the match. Shawn "
        "Michaels was credited with 6 eliminations, the most of any wrestler this match. This was Kane's 12th "
        "career Royal Rumble appearance, per this database's own running count. This was also the final "
        "Royal Rumble to feature the ECW Championship on the card, as the ECW brand was dissolved the "
        "following month (February 2010)."
    ),
    "notes": (
        "UNIQUE among every year in this database: Shane's source document has zero content for 2010, so this "
        "year was built entirely from external research (a Shane-approved one-time exception to the project's "
        "document-first methodology) rather than his own compiled document. Entry order and the full "
        "elimination chain are CONFIRMED via 4-5 independently agreeing sources each. Event-level facts (date, "
        "venue, attendance, commentary) are also CONFIRMED, unlike the single-source-document 2009/2011/2012 "
        "builds -- research years and document years end up with different strengths and gaps. Per-wrestler "
        "ring/elimination-clock timing is UNKNOWN for all but 2 entrants (Edge, John Cena), since no source "
        "tracked this to the second the way Shane's own document does for other years -- see F245. 4 of 5 "
        "undercard title matches are logged, with 3 having a minor CONFLICTING time discrepancy between "
        "sources -- see F247."
    ),
    "data_quality_status": "CONFIRMED", "source_ids": SRC,
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2010 build complete (schema v2, EXTERNAL RESEARCH year): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(other_match_rows)} other_matches rows, {len(sources)} sources logged, {len(flags)} open flags.")
