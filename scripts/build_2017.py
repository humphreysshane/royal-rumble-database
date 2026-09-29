# -*- coding: utf-8 -*-
"""
Builds all rows for the 2017 Royal Rumble -- schema v2.

IMPORTANT METHODOLOGY SHIFT: Shane's own source document (Entrant_Stats.xlsx
/ Main_Rumble_Stats_New.docx) has NO content past "2016 Royal Rumble Stats"
-- its "Royal Rumble Collection of Stats" section is general cross-year
trivia, not per-year data, and the document moves on to WCW World War 3
content after that. Every event from 2017 onward is therefore built from
FRESH EXTERNAL RESEARCH rather than transcribed from Shane's document, the
same standard already used for this database's "external fact-check" passes
on 2013-2016 (see F296-F318) -- multiple independent sources cross-checked
against each other, disagreements preserved as flags rather than resolved
by guessing.

NEW PROCESS, per Shane's explicit instruction (2026-09-20): going forward,
WWE Hall of Fame status is checked for every new wrestler as part of
building the event they're first added in, not picked up later as a
separate incidental audit pass. Applied here: all 11 wrestlers new to this
database this pass had their HOF status checked as part of their bio
research (see WRESTLERS section below) -- Goldberg's 2018 individual
induction was caught immediately rather than waiting for a future sweep.

SOURCES CONSULTED THIS PASS (all live web research, cross-validated against
each other -- see flags.csv for where they disagreed):
  S140 Wikipedia, 'Royal Rumble (2017)' event article              tier 10
  S141 WWE.com, official '2017 Royal Rumble Statistics' page       tier 1
  S142 dailyddt.com, 'WWE Royal Rumble 2017: Official Entrant Order' tier 12
  S143 WrestlingInc.com, 'Order Of Eliminations For The 2017 WWE
       Royal Rumble' article                                        tier 9

CROSS-VALIDATION RESULTS:
  - Entry order (1-30): CONFIRMED, 3 independent sources (S140, S141, S142)
    agree exactly with zero discrepancy. Big Show's participation (entrant
    #9) was explicitly double-checked after an initial fetch ambiguity --
    settled definitively as a genuine entrant, eliminated 6th by Braun
    Strowman after 1:42, confirmed by all 3 sources plus contemporaneous
    news coverage of his pre-event addition to the field.
  - Eliminator credit and per-wrestler ring time: CONFIRMED for 28 of 29
    eliminations (S140 and S143, independently structured -- one a match
    table, the other a narrative recap -- agree exactly). ONE exception:
    Sheamus and Cesaro's relative elimination order (13th vs 14th) is
    CONFLICTING between S140 (Cesaro 13th/Sheamus 14th) and S143 (Sheamus
    13th/Cesaro 14th) -- both were eliminated by Chris Jericho within
    seconds of each other; no third source with a numbered sequence was
    found to break the tie. See F360. Both wrestlers' own eliminator
    credit (Chris Jericho) and ring times are NOT in dispute, only their
    relative order.
  - Total match duration: S141 (WWE.com, tier 1) states 1:02:06; S140
    (Wikipedia) states 1:02:07 -- a 1-second variance, immaterial but
    logged rather than silently rounded. See F362. This script uses the
    higher-tier S141 figure (1:02:06) per this database's source-hierarchy
    tie-breaking convention (DEFINITIONS.md).
  - No buzzer-gap ("time between entrants") data was recovered this pass,
    unlike the pre-2013 years where Shane's own Cageside timing analysis
    provided it directly -- so full elimination_clock_time (global match-
    clock timestamps) could NOT be reconstructed with confidence and is
    left UNKNOWN throughout, matching this database's "never invent data"
    rule. Each entrant's own ring_time (individual survival duration) IS
    populated and CONFIRMED, since that figure came directly from sources
    rather than being derived. See F361.

NAMED ELIMINATIONS THIS YEAR: all 29 (unusually complete for a single pass
-- WWE.com's own modern stats page names every eliminator, unlike the
narrower named-eliminator subsets recovered for older years). Cesaro and
Sheamus share credit for 3 eliminations (Kofi Kingston, Xavier Woods, Big
E) as an ad hoc pairing (not yet WWE's later-established "The Bar" tag
team as of this date -- see F363).

WHAT'S ACTUALLY KNOWN THIS YEAR: entry order and eliminator credit for all
30 entrants/29 eliminations, CONFIRMED via 2-3 independent sources each
(save the single Sheamus/Cesaro order conflict). Event-level facts (date,
venue, city, attendance, winner's reward) are all CONFIRMED via 2+ sources.
Commentary team and referees are single-sourced (Wikipedia only) this pass
-- see F363.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from schema import (
    ENTRANTS_FIELDS, ELIMINATIONS_FIELDS, EVENTS_FIELDS, NOTABLE_MOMENTS_FIELDS,
    slugify, mmss_to_seconds,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EVENT_ID = "RR2017M"


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
    ("S140", "Wikipedia (English), 'Royal Rumble (2017)' event article", "reference_site", "https://en.wikipedia.org/wiki/Royal_Rumble_(2017)", 10, "Wikipedia/reference sites", "2026-09-20",
     "First externally-researched build (Shane's own document has no 2017+ content). Full entrant/elimination "
     "table, event facts, commentary team, referees. Independently agrees with S141/S142 on entry order exactly; "
     "disagrees with S143 on Sheamus/Cesaro's relative elimination order by one slot -- see F360. States match "
     "duration as 1:02:07, one second off S141's 1:02:06 -- see F362."),
    ("S141", "WWE.com, official '2017 Royal Rumble Statistics' page", "official_wwe", "https://www.wwe.com/shows/royalrumble/article/2017-royal-rumble-statistics-entrants-eliminations", 1, "WWE / official sources", "2026-09-20",
     "Official WWE stats page: full entrant order, eliminator credit, and per-wrestler ring time for all 30 "
     "entrants. Agrees exactly with S140/S142 on entry order. Used as the tie-breaking source for match duration "
     "(1:02:06) per this database's tier-hierarchy convention -- see F362."),
    ("S142", "dailyddt.com, 'WWE Royal Rumble 2017: Official Entrant Order' article", "other_stats_site", "", 12, "Other reputable site", "2026-09-20",
     "Independent entrant-order-only article, used as a 3rd cross-check on entry order alongside S140/S141 -- "
     "agrees exactly, no discrepancy."),
    ("S143", "WrestlingInc.com, 'Order Of Eliminations For The 2017 WWE Royal Rumble' article", "contemporary_publication", "https://www.wrestlinginc.com/news/2017/01/order-of-eliminations-for-the-2017-wwe-royal-rumble-622737/", 9, "Contemporary wrestling publication", "2026-09-20",
     "Independent narrative (not table-based) recap of all 29 eliminations in order -- a genuinely independent "
     "data path from S140's structured table. Matches S140 on 28 of 29 eliminations exactly; disagrees on "
     "Sheamus/Cesaro's relative order -- see F360."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# ENTRY ORDER (CONFIRMED, S140+S141+S142 agree exactly)
# ---------------------------------------------------------------------------
all_names = [
    "Big Cass", "Chris Jericho", "Kalisto", "Mojo Rawley", "Jack Gallagher", "Mark Henry", "Braun Strowman",
    "Sami Zayn", "Big Show", "Tye Dillinger", "James Ellsworth", "Dean Ambrose", "Baron Corbin", "Kofi Kingston",
    "The Miz", "Sheamus", "Big E", "Rusev", "Cesaro", "Xavier Woods", "Bray Wyatt", "Apollo Crews", "Randy Orton",
    "Dolph Ziggler", "Luke Harper", "Brock Lesnar", "Enzo Amore", "Goldberg", "The Undertaker", "Roman Reigns",
]
assert len(all_names) == 30
ENTRY_NUMBERS = {name: i + 1 for i, name in enumerate(all_names)}
assert ENTRY_NUMBERS["Big Show"] == 9 and ENTRY_NUMBERS["Roman Reigns"] == 30 and ENTRY_NUMBERS["Randy Orton"] == 23

# Individual survival ("ring") times, as directly stated by S141/S143 (agree exactly).
survival = {
    "Big Cass": "9:57", "Chris Jericho": "1:00:13", "Kalisto": "8:17", "Mojo Rawley": "6:16",
    "Jack Gallagher": "3:20", "Mark Henry": "3:17", "Braun Strowman": "13:11", "Sami Zayn": "46:55",
    "Big Show": "1:42", "Tye Dillinger": "5:27", "James Ellsworth": "0:15", "Dean Ambrose": "26:55",
    "Baron Corbin": "32:39", "Kofi Kingston": "16:13", "The Miz": "32:44", "Sheamus": "12:13",
    "Big E": "9:46", "Rusev": "22:31", "Cesaro": "6:44", "Xavier Woods": "4:47", "Bray Wyatt": "24:11",
    "Apollo Crews": "5:46", "Randy Orton": "20:52", "Dolph Ziggler": "4:21", "Luke Harper": "9:56",
    "Brock Lesnar": "4:30", "Enzo Amore": "0:18", "Goldberg": "3:21", "The Undertaker": "8:46",
    "Roman Reigns": "5:05",
}
assert set(survival) == set(all_names)

# Elimination order (1st-29th). Sheamus/Cesaro's relative order is CONFLICTING
# between sources -- S140's ordering (Cesaro 13th, Sheamus 14th) is used for
# the structured elim_number field per the tier-hierarchy tie-break (S140,
# tier 10, outranks S143, tier 9, only marginally; logged as CONFLICTING
# rather than CONFIRMED either way -- see F360).
ELIM_ORDER = [
    "Jack Gallagher", "Mojo Rawley", "Big Cass", "Kalisto", "Mark Henry", "Big Show", "James Ellsworth",
    "Tye Dillinger", "Braun Strowman", "Kofi Kingston", "Xavier Woods", "Big E", "Cesaro", "Sheamus",
    "Apollo Crews", "Dean Ambrose", "Dolph Ziggler", "Enzo Amore", "Brock Lesnar", "Rusev", "Baron Corbin",
    "Luke Harper", "Goldberg", "The Miz", "Sami Zayn", "The Undertaker", "Chris Jericho", "Bray Wyatt",
    "Roman Reigns",
]
assert len(ELIM_ORDER) == 29
elim_number = {name: i + 1 for i, name in enumerate(ELIM_ORDER)}
DISPUTED_ORDER = {"Sheamus", "Cesaro"}

FINAL_TWO = {"Randy Orton", "Roman Reigns"}
FINAL_THREE = {"Randy Orton", "Roman Reigns", "Bray Wyatt"}
FINAL_FOUR = {"Randy Orton", "Roman Reigns", "Bray Wyatt", "Chris Jericho"}

# name -> (eliminator names, is_shared, notes)
ELIMINATORS = {
    "Jack Gallagher": (["Mark Henry"], False, ""),
    "Mojo Rawley": (["Braun Strowman"], False, ""),
    "Big Cass": (["Braun Strowman"], False, ""),
    "Kalisto": (["Braun Strowman"], False, ""),
    "Mark Henry": (["Braun Strowman"], False, ""),
    "Big Show": (["Braun Strowman"], False, "Big Show's participation this year was double-checked and settled definitively after an initial research ambiguity -- see script docstring."),
    "James Ellsworth": (["Braun Strowman"], False, "One of the shortest Royal Rumble appearances on record, part of a comedy angle."),
    "Tye Dillinger": (["Braun Strowman"], False, ""),
    "Braun Strowman": (["Baron Corbin"], False, "Strowman's 7 eliminations were the most of the match -- a dominant showing, though not yet the all-time record (Kane's 11, RR2001, still stood at this point; Strowman broke that record the following year, at the 2018 Greatest Royal Rumble in Saudi Arabia, out of this database's scope)."),
    "Kofi Kingston": (["Cesaro", "Sheamus"], True, "Shared elimination credit with Sheamus -- part of an ad hoc pairing, not yet WWE's later-established 'The Bar' tag team as of this date. See F363."),
    "Xavier Woods": (["Cesaro", "Sheamus"], True, "Shared elimination credit with Sheamus."),
    "Big E": (["Cesaro", "Sheamus"], True, "Shared elimination credit with Sheamus."),
    "Cesaro": (["Chris Jericho"], False, "Relative elimination order versus Sheamus is CONFLICTING between sources -- see F360."),
    "Sheamus": (["Chris Jericho"], False, "Relative elimination order versus Cesaro is CONFLICTING between sources -- see F360."),
    "Apollo Crews": (["Luke Harper"], False, ""),
    "Dean Ambrose": (["Brock Lesnar"], False, ""),
    "Dolph Ziggler": (["Brock Lesnar"], False, ""),
    "Enzo Amore": (["Brock Lesnar"], False, ""),
    "Brock Lesnar": (["Goldberg"], False, "Eliminated by Goldberg, previewing their rivalry that culminated in Goldberg winning the Universal Championship from Lesnar at WrestleMania 33 (general knowledge, not independently re-sourced this pass)."),
    "Rusev": (["Goldberg"], False, ""),
    "Baron Corbin": (["The Undertaker"], False, ""),
    "Luke Harper": (["Goldberg"], False, ""),
    "Goldberg": (["The Undertaker"], False, ""),
    "The Miz": (["The Undertaker"], False, ""),
    "Sami Zayn": (["The Undertaker"], False, "The Undertaker's 4 eliminations this match, directly setting up his 'final' match against Roman Reigns at WrestleMania 33 (general knowledge, not independently re-sourced this pass)."),
    "The Undertaker": (["Roman Reigns"], False, ""),
    "Chris Jericho": (["Roman Reigns"], False, "Longest ring time of the match, over an hour (1:00:13)."),
    "Bray Wyatt": (["Roman Reigns"], False, ""),
    "Roman Reigns": (["Randy Orton"], False, "The winning elimination. Reigns had already lost the WWE Universal Championship to Kevin Owens in a No Disqualification match earlier the same night (with Chris Jericho suspended in a shark cage above the ring, per S141) before entering this Rumble at #30."),
}
assert set(ELIMINATORS) == set(ELIM_ORDER)

# ---------------------------------------------------------------------------
# WRESTLERS -- new to this database this pass. Bios researched live (real
# name, dob, birthplace, deceased-status and WWE HOF status all checked as
# part of THIS build, per Shane's new process -- not deferred to a later
# incidental audit pass).
# ---------------------------------------------------------------------------
# (ring_name, real_name, real_name_status, gender, dob, dob_status, deceased_date,
#  birthplace, birthplace_status, nationality, debut_year_company, hall_of_fame_year,
#  aliases_ring_names, wrestling_style, notes, source_ids)
new_wrestlers = [
    ("Big Cass", "William Morrissey", "PROBABLE", "M", "1986-08-16", "PROBABLE", "", "Glendale, Queens, New York, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #1 (the opening entrant). Survived 9:57.", "S022;S140"),
    ("Kalisto", "Emanuel Alejandro Rodriguez", "PROBABLE", "M", "1986-11-14", "PROBABLE", "", "Chicago, Illinois, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #3. Survived 8:17.", "S022;S140"),
    ("Mojo Rawley", "Dean Muhtadi", "PROBABLE", "M", "1986-07-17", "PROBABLE", "", "Alexandria, Virginia, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #4. Survived 6:16.", "S022;S140"),
    ("Jack Gallagher", "Oliver Westfield Claffey", "PROBABLE", "M", "1990-01-07", "PROBABLE", "", "Manchester, England", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #5. Survived 3:20 -- the first elimination of the match.", "S022;S140"),
    ("Tye Dillinger", "Ronnie William Arneill", "PROBABLE", "M", "1981-02-19", "PROBABLE", "", "St. Catharines, Ontario, Canada", "PROBABLE", "", "", "",
     "Shawn Spears", "", "Rumble debut, entered #10 -- his 'Perfect 10' gimmick made the #10 draw one of this match's most-celebrated moments. Survived 5:27.", "S022;S140"),
    ("James Ellsworth", "James Ellsworth Morris", "PROBABLE", "M", "1984-12-11", "PROBABLE", "", "Baltimore, Maryland, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #11. Survived just 0:15 -- one of the shortest Rumble appearances on record, part of a comedy angle.", "S022;S140"),
    ("Baron Corbin", "Thomas Pestock", "PROBABLE", "M", "1984-09-13", "PROBABLE", "", "Lenexa, Kansas, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #13. Survived 32:39. Credited with eliminating Braun Strowman.", "S022;S140"),
    ("Xavier Woods", "Austin Watson", "PROBABLE", "M", "1986-09-04", "PROBABLE", "", "Columbus, Georgia, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #20 (his prior scheduled 2014 entrant slot never materialized -- see this database's RR2014M/F279 note). Survived 4:47. Member of the New Day faction (with Kofi Kingston and Big E) at the time.", "S022;S140"),
    ("Apollo Crews", "Sesugh Isaac Uhaa", "PROBABLE", "M", "1987-08-22", "PROBABLE", "", "Sacramento, California, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #22. Survived 5:46.", "S022;S140"),
    ("Enzo Amore", "Eric Arndt", "PROBABLE", "M", "1986-12-08", "PROBABLE", "", "Hackensack, New Jersey, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #27. Survived just 0:18.", "S022;S140"),
    ("Goldberg", "William Scott Goldberg", "PROBABLE", "M", "1966-12-27", "PROBABLE", "", "Tulsa, Oklahoma, U.S.", "PROBABLE", "", "", "2018",
     "", "", "Rumble debut, entered #28 as an unaffiliated returning legend. Survived 3:21, eliminating 3 (Brock Lesnar, Rusev, Luke Harper) before his own elimination -- previewing his rivalry with Lesnar, which led to Goldberg winning the Universal Championship from Lesnar at WrestleMania 33. Individually inducted into the WWE Hall of Fame in 2018 (announced Jan 15, 2018; ceremony April 6, 2018, presented by Paul Heyman) -- checked and added as part of this build, per this database's new HOF-at-build-time process.", "S022;S123;S124;S140"),
]

reused = {
    "Chris Jericho": "chris-jericho", "Mark Henry": "mark-henry", "Braun Strowman": "braun-strowman",
    "Sami Zayn": "sami-zayn", "Big Show": "big-show", "Dean Ambrose": "dean-ambrose",
    "Kofi Kingston": "kofi-kingston", "The Miz": "the-miz", "Sheamus": "sheamus", "Big E": "big-e",
    "Rusev": "rusev", "Cesaro": "cesaro", "Bray Wyatt": "bray-wyatt", "Randy Orton": "randy-orton",
    "Dolph Ziggler": "dolph-ziggler", "Luke Harper": "luke-harper", "Brock Lesnar": "brock-lesnar",
    "The Undertaker": "the-undertaker", "Roman Reigns": "roman-reigns",
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

assert set(wrestler_ids) == set(all_names)

# ---------------------------------------------------------------------------
# ENTRANTS / ELIMINATIONS
# ---------------------------------------------------------------------------
entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Randy Orton")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, is_shared, extra_note = ELIMINATORS.get(name, ([], False, ""))

    notes_parts = [extra_note] if extra_note else []
    if name == "Randy Orton":
        notes_parts.append("Entered #23 and won, eliminating Roman Reigns (an RKO counter to a Spear attempt) in the match's final moments. His 2nd Royal Rumble win (after 2009), making him the 7th wrestler to win the Royal Rumble more than once (after Hulk Hogan, Steve Austin, Shawn Michaels, Triple H, John Cena and Batista). Earned a world championship match at WrestleMania 33.")

    for eliminator in elim_by:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": elim_number[name],
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
            "assisting_wrestler_ids": ";".join(wrestler_ids[e] for e in elim_by if e != eliminator) if is_shared else "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": ENTRY_NUMBERS.get(eliminator, ""),
            "elimination_clock_time": "", "elimination_clock_seconds": "",
            "elimination_type": "over_top_rope",
            "elimination_method": "",
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "FALSE" if is_shared else "TRUE", "is_shared": "TRUE" if is_shared else "FALSE",
            "is_accidental": "FALSE",
            "is_self_elimination": "FALSE",
            "is_storyline_related": "UNKNOWN",
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "TRUE" if name in DISPUTED_ORDER else "FALSE",
            "simultaneous_group_id": "",
            "data_quality_status": "CONFLICTING" if name in DISPUTED_ORDER else "CONFIRMED",
            "source_ids": "S140;S141;S143",
            "notes": "Relative elimination order vs. the other of this Chris Jericho double-elimination is CONFLICTING between sources -- see F360." if name in DISPUTED_ORDER else "",
        })

    er = {
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": "CONFIRMED",
        "ring_name_at_time": name, "name_displayed_at_event": name,
        "prior_rumble_appearances_count": "", "rumble_appearance_no": "",
        "is_first_rumble_appearance": "TRUE" if name in [w[0] for w in new_wrestlers] else "", "is_company_debut": "UNKNOWN",
        "previous_rumble_year": "", "previous_rumble_result": "", "previous_rumble_elimination_no": "",
        "is_rumble_debut": "TRUE" if name in [w[0] for w in new_wrestlers] else "",
        "company_debut_date": "",
        "is_returning_wrestler": "TRUE" if name in ("Goldberg", "The Undertaker") else "",
        "absence_length": "",
        "age_at_event": "", "age_status": "UNKNOWN",
        "billed_height_m_at_event": "", "billed_weight_kg_at_event": "", "billed_from_at_event": "",
        "physical_status": "UNKNOWN",
        "alignment": "", "alignment_status": "UNKNOWN",
        "gimmick_at_event": "",
        "manager_at_event": "",
        "tag_team_name": "",
        "faction_stable": "The New Day" if name in ("Kofi Kingston", "Xavier Woods", "Big E") else "",
        "current_champion_title": "",
        "championship_level": "",
        "championship_partner": "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        "title_defended_same_card": "FALSE", "title_lost_same_card": "TRUE" if name == "Roman Reigns" else "FALSE",
        "elim_number": "" if is_winner else elim_number[name],
        "elim_number_status": "N/A" if is_winner else ("CONFLICTING" if name in DISPUTED_ORDER else "CONFIRMED"),
        "eliminated_by_ids": ";".join(wrestler_ids[e] for e in elim_by),
        "elimination_clock_time": "", "elimination_clock_seconds": "",
        "ring_time": ring_time, "ring_time_seconds": ring_time_s,
        "ring_time_status": "CONFIRMED",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if name == "Roman Reigns" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "TRUE" if name == "Tye Dillinger" else "FALSE",
        "legend_returning": "TRUE" if name in ("Goldberg", "The Undertaker") else "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "TRUE" if name == "Goldberg" else "FALSE",
        "wrestled_earlier_on_card": "TRUE" if name == "Roman Reigns" else "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S140;S141;S142;S143",
        "notes": " ".join(notes_parts),
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
        er["solo_eliminations_count"] = sum(1 for r in elim_rows if r["eliminator_wrestler_id"] == er["wrestler_id"] and r["is_solo"] == "TRUE")
        er["assisted_eliminations_count"] = sum(1 for r in elim_rows if r["eliminator_wrestler_id"] == er["wrestler_id"] and r["is_solo"] == "FALSE")

with open(os.path.join(DATA_DIR, "entrants.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ENTRANTS_FIELDS)
    for er in entrant_rows:
        writer.writerow(er)

with open(os.path.join(DATA_DIR, "eliminations.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ELIMINATIONS_FIELDS)
    for row in elim_rows:
        writer.writerow(row)

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F360", EVENT_ID, "eliminations;entrants", "sheamus;cesaro", "elim_number", "conflicting_sources",
     "Sheamus and Cesaro's relative elimination order is CONFLICTING between sources: S140 (Wikipedia) orders "
     "them Cesaro-13th/Sheamus-14th; S143 (WrestlingInc.com, an independently-written narrative recap) orders "
     "them Sheamus-13th/Cesaro-14th. Both were eliminated by Chris Jericho within seconds of each other (a "
     "near-simultaneous double-elimination spot). No third source with an explicit numbered sequence was found "
     "to break the tie. This script uses S140's ordering for the structured elim_number field (tie-broken by "
     "source tier per DEFINITIONS.md) but logs data_quality_status=CONFLICTING on both rows rather than treating "
     "it as settled. Their eliminator credit (Chris Jericho) and individual ring times are NOT in dispute.",
     "S140;S143", "open", "2026-09-20"),
    ("F361", EVENT_ID, "entrants;eliminations", "*", "elimination_clock_time", "unverified",
     "Unlike the pre-2013 years (where Shane's own Cageside timing analysis provided buzzer-gap/time-between-"
     "entrants data directly), no source recovered this pass gives entry timing granular enough to reconstruct "
     "global match-clock timestamps (elimination_clock_time) with confidence. Each entrant's own ring_time "
     "(individual survival duration) IS populated and CONFIRMED, sourced directly rather than derived -- only "
     "the global-clock fields are left UNKNOWN, per this database's 'never invent data' rule.",
     "S140;S141;S143", "open", "2026-09-20"),
    ("F362", EVENT_ID, "events", EVENT_ID, "duration_total", "conflicting_sources",
     "Total match duration is reported as 1:02:06 by S141 (WWE.com, tier 1) and 1:02:07 by S140 (Wikipedia, "
     "tier 10) -- a 1-second variance, immaterial but logged rather than silently rounded. This script uses "
     "S141's figure per this database's tier-hierarchy tie-breaking convention.",
     "S140;S141", "open", "2026-09-20"),
    ("F363", EVENT_ID, "events", EVENT_ID, "commentary_team;referees", "unverified",
     "Commentary team (Michael Cole, Corey Graves, Jerry Lawler) and the referee roster are single-sourced this "
     "pass (Wikipedia only, S140), not independently cross-checked against a second source -- low-risk claims, "
     "but flagged per this database's sourcing standard rather than silently upgraded to CONFIRMED. Separately: "
     "Cesaro and Sheamus's 3 shared eliminations this match reflect an ad hoc pairing, not yet WWE's "
     "later-established 'The Bar' tag team as of this date (Jan 29, 2017) -- tag_team_name left blank for both "
     "rather than assuming the later team name applied retroactively.",
     "S140", "open", "2026-09-20"),
    ("F364", EVENT_ID, "wrestlers", "big-cass;kalisto;mojo-rawley;jack-gallagher;tye-dillinger;james-ellsworth;baron-corbin;xavier-woods;apollo-crews;enzo-amore;goldberg", "hall_of_fame_year;real_name;dob;birthplace", "corrected",
     "NEW PROCESS starting this build, per Shane's explicit instruction (2026-09-20): WWE Hall of Fame status is "
     "now checked for every new wrestler as part of building the event they're first added in, rather than "
     "picked up later as a separate incidental audit pass (as it was for the 1988-2016 fact-check sweep). Bio "
     "data (real name, dob, birthplace) and HOF/deceased status were researched live for all 11 wrestlers new to "
     "this database this pass -- a meaningful upgrade over the pre-2017 years' UNKNOWN bio placeholders, which "
     "existed only because Shane's own source document had zero bio content for those entrants; this pass has "
     "real external research available instead. Result: 10 of the 11 are not yet HOF-inducted; Goldberg WAS "
     "caught immediately -- individually inducted in 2018 (announced Jan 15, 2018; ceremony April 6, 2018) -- "
     "added to his row at build time rather than waiting for a future sweep to find it incidentally. All bio "
     "fields recorded at PROBABLE (single-sourced this pass, Wikipedia) pending a second source.",
     "S022;S123;S124", "resolved", "2026-09-20"),
    ("F365", EVENT_ID, "entrances;moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-20"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# NOTABLE MOMENTS
# ---------------------------------------------------------------------------
nm_rows = [
    {
        "moment_id": "NM044", "event_id": EVENT_ID, "wrestler_ids_involved": "randy-orton",
        "category": "record",
        "title": "Randy Orton's 2nd Royal Rumble win -- the 7th multi-time winner in history",
        "description": "Orton won his 2nd Royal Rumble (after 2009), becoming the 7th wrestler to win the Royal Rumble more than once, joining Hulk Hogan, Steve Austin, Shawn Michaels, Triple H, John Cena and Batista.",
        "data_quality_status": "CONFIRMED", "source_ids": "S140;S141",
        "notes": "First notable_moments row for a from-scratch-built (non-fact-check) event.",
    },
    {
        "moment_id": "NM045", "event_id": EVENT_ID, "wrestler_ids_involved": "tye-dillinger",
        "category": "other",
        "title": "Tye Dillinger's \"Perfect 10\" entrance at #10",
        "description": "Dillinger's NXT call-up drew entry #10 -- a perfect match for his 'Perfect 10' gimmick -- producing one of the most-remembered reactions of the match, even though he was eliminated 8th, after 5:27.",
        "data_quality_status": "CONFIRMED", "source_ids": "S140;S141",
        "notes": "",
    },
    {
        "moment_id": "NM046", "event_id": EVENT_ID, "wrestler_ids_involved": "roman-reigns;kevin-owens",
        "category": "other",
        "title": "Roman Reigns wrestled twice in one night -- losing the Universal Championship, then nearly winning the Rumble",
        "description": "Reigns lost the WWE Universal Championship to Kevin Owens in a No Disqualification match earlier the same card (with Chris Jericho suspended in a shark cage above the ring), then entered the Royal Rumble at #30, eliminated The Undertaker, and made the final two before losing to Randy Orton.",
        "data_quality_status": "CONFIRMED", "source_ids": "S141",
        "notes": "kevin-owens is referenced by name but not a wrestler_id tracked in this database (not a Rumble entrant this year).",
    },
    {
        "moment_id": "NM047", "event_id": EVENT_ID, "wrestler_ids_involved": "james-ellsworth",
        "category": "record",
        "title": "James Ellsworth's 15-second Rumble run, among the shortest ever",
        "description": "Ellsworth entered #11 as part of a comedy angle and was eliminated by Braun Strowman in just 0:15 -- one of the shortest Royal Rumble appearances on record.",
        "data_quality_status": "CONFIRMED", "source_ids": "S140;S141",
        "notes": "",
    },
    {
        "moment_id": "NM048", "event_id": EVENT_ID, "wrestler_ids_involved": "braun-strowman",
        "category": "record",
        "title": "Braun Strowman's 7 eliminations, the most of the match",
        "description": "Strowman eliminated 7 competitors (Big Cass, Kalisto, Mojo Rawley, Mark Henry, Big Show, James Ellsworth, Tye Dillinger) -- the most of this match, though not yet the all-time single-Rumble record, which stood at 11 (Kane, RR2001) at the time. Strowman broke that record the following year, at the 2018 Greatest Royal Rumble in Saudi Arabia -- outside this database's current scope.",
        "data_quality_status": "CONFIRMED", "source_ids": "S140;S141",
        "notes": "",
    },
    {
        "moment_id": "NM049", "event_id": EVENT_ID, "wrestler_ids_involved": "brock-lesnar;goldberg",
        "category": "storyline_moment",
        "title": "Goldberg eliminated Brock Lesnar, previewing their WrestleMania 33 title feud",
        "description": "Goldberg, an unaffiliated returning legend entering at #28, eliminated Brock Lesnar -- the beginning of a rivalry that culminated in Goldberg winning the Universal Championship from Lesnar at WrestleMania 33 in a match lasting under two minutes.",
        "data_quality_status": "CONFIRMED", "source_ids": "S140",
        "notes": "The WrestleMania 33 follow-through is general knowledge, not independently re-sourced this pass -- the elimination itself (this match's own content) is what's CONFIRMED.",
    },
    {
        "moment_id": "NM050", "event_id": EVENT_ID, "wrestler_ids_involved": "",
        "category": "milestone_first",
        "title": "The last men's-only Royal Rumble before the Women's Royal Rumble debuted in 2018",
        "description": "This was the final Royal Rumble PPV to feature only a men's Rumble match -- the first Women's Royal Rumble match was introduced the following year, at Royal Rumble 2018.",
        "data_quality_status": "PROBABLE", "source_ids": "S140",
        "notes": "Single-sourced this pass (Wikipedia), not independently cross-checked against a second source.",
    },
]
with open(os.path.join(DATA_DIR, "notable_moments.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=NOTABLE_MOMENTS_FIELDS)
    for row in nm_rows:
        writer.writerow(row)

flags2 = [
    ("F366", EVENT_ID, "notable_moments", "NM044;NM045;NM046;NM047;NM048;NM049;NM050", "n/a", "corrected",
     "Added 7 notable_moments.csv rows for this newly-built event: Randy Orton's 2nd Rumble win (7th multi-time "
     "winner), Tye Dillinger's beloved 'Perfect 10' entrance, Roman Reigns wrestling twice in one night, James "
     "Ellsworth's 15-second run, Braun Strowman's match-high 7 eliminations, Goldberg's elimination of Brock "
     "Lesnar previewing their WrestleMania 33 feud, and this being the last men's-only Royal Rumble before the "
     "Women's Royal Rumble launched in 2018.",
     "S140;S141", "resolved", "2026-09-20"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags2)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2017", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2017-01-29",
    "venue": "Alamodome", "city_region": "San Antonio, Texas", "country": "United States",
    "attendance_official": 52020, "attendance_reported": "",
    "entry_interval_seconds": "", "entrant_count": 30,
    "duration_total": "1:02:06", "duration_status": "CONFIRMED",
    "winner_id": "randy-orton", "runner_up_id": "roman-reigns",
    "final_two_ids": "randy-orton;roman-reigns",
    "final_three_ids": "randy-orton;roman-reigns;bray-wyatt",
    "final_four_ids": "randy-orton;roman-reigns;bray-wyatt;chris-jericho",
    "first_entrant_id": "big-cass", "second_entrant_id": "chris-jericho", "final_entrant_id": "roman-reigns",
    "first_elimination_id": "jack-gallagher", "last_elimination_before_winner_id": "roman-reigns",
    "eliminations_count": 29, "eliminators_count": 11,
    "surprise_entrants_count": "UNKNOWN",
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": 0,
    "tag_teams_count": "UNKNOWN", "factions_count": 1,
    "commentary_team": "Michael Cole, Corey Graves, Jerry Lawler",
    "ring_announcer": "UNKNOWN",
    "referees": "UNKNOWN",
    "special_rules": "Standard Royal Rumble rules. Unlike RR2016M, no title was defended within the match itself this year -- the winner instead earned a title shot at WrestleMania 33.",
    "title_on_the_line": "FALSE",
    "championship_implications": "The winner earned the right to challenge for a world championship at WrestleMania 33 -- their choice between Raw's Universal Championship or SmackDown's WWE Championship (the standard post-2016-brand-split Rumble winner's reward). Randy Orton won. Separately, Roman Reigns lost the Universal Championship to Kevin Owens in a No Disqualification match earlier the same card, before entering this Rumble at #30.",
    "winners_reward": "A world championship match at WrestleMania 33 -- winner's choice between Raw's Universal Championship and SmackDown's WWE Championship.",
    "historical_significance": (
        "Randy Orton's 2nd career Royal Rumble win (after 2009), entering at #23 and eliminating Roman Reigns "
        "(an RKO counter to a Spear attempt) in the match's final moments -- making Orton the 7th wrestler to "
        "win the Royal Rumble more than once. Braun Strowman had the most eliminations of the match with 7, a "
        "dominant showing though not yet the all-time record (Kane's 11 from RR2001 still stood; Strowman broke "
        "it the following year at the 2018 Greatest Royal Rumble, outside this database's scope). Tye Dillinger's "
        "NXT call-up drew the perfectly-fitting entry #10 for his 'Perfect 10' gimmick, one of the most-"
        "remembered moments of the night. Roman Reigns wrestled twice on the card -- losing the WWE Universal "
        "Championship to Kevin Owens in a No Disqualification match earlier, then entering the Rumble at #30 and "
        "making the final two. Goldberg, an unaffiliated returning legend, eliminated Brock Lesnar, previewing "
        "their WrestleMania 33 Universal Championship feud. The Undertaker eliminated 4 opponents (including "
        "Sami Zayn's 46:55 survival, the match's 2nd-longest) before being eliminated by Roman Reigns, building "
        "toward Undertaker's 'final' match against Reigns at WrestleMania 33. James Ellsworth's 15-second run "
        "was among the shortest Rumble appearances on record. This was the last men's-only Royal Rumble before "
        "the Women's Royal Rumble match debuted the following year, at Royal Rumble 2018."
    ),
    "notes": (
        "First event in this database built entirely from external research rather than Shane's own source "
        "document, which has no content past 2016 -- see script docstring. Entry order and eliminator credit "
        "CONFIRMED for all 30 entrants via 2-3 independent sources each, except the Sheamus/Cesaro relative "
        "elimination-order conflict (F360). Global match-clock timing (elimination_clock_time) left UNKNOWN "
        "throughout -- see F361. WWE Hall of Fame status was checked for all 11 newly-added wrestlers as part "
        "of this build, per Shane's new process (F364) -- Goldberg's 2018 individual induction was caught "
        "immediately rather than deferred to a future audit pass."
    ),
    "data_quality_status": "CONFIRMED", "source_ids": "S140;S141;S142;S143",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2017 build complete (schema v2, first externally-researched year): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags) + len(flags2)} flags, {len(nm_rows)} notable_moments rows. "
      f"1 new HOF completion caught at build time (Goldberg, 2018).")
