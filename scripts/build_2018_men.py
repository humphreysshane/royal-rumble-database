# -*- coding: utf-8 -*-
"""
Builds all rows for the 2018 Men's Royal Rumble -- schema v2.

Royal Rumble 2018, January 28, 2018, Wells Fargo Center, Philadelphia, PA.
This is the MEN'S match only. The Women's Royal Rumble held the same night
(the first ever) is a fully separate event/record -- see build_2018_women.py
-- per Shane's explicit instruction (2026-09-20): "keep them separate."

NOT the "Greatest Royal Rumble" (a different, Saudi Arabia special held in
April 2018) -- out of scope for this database.

NEW PROCESS, continuing from RR2017M: WWE Hall of Fame status (and deceased
status) is checked for every new wrestler as part of building the event
they're first added in. Applied here for all 6 wrestlers new to this
database this pass -- none are HOF-inducted as of today (2026-09-20); all
are alive.

SOURCES CONSULTED THIS PASS (all live web research, cross-validated against
each other -- see flags.csv for where they disagreed):
  S144 Wikipedia, 'Royal Rumble (2018)' event article               tier 10
  S145 WWE.com, official 'Full 2018 30-Man Royal Rumble Match
       statistics' page                                              tier 1
  S146 WrestlingInc.com, 'WWE Royal Rumble 2018 Men's Match Orders
       Of Entry And Elimination' article                             tier 9
  S147 Cageside Seats, 'Men's Royal Rumble 2018 Match Time and
       Statistics' -- independent fan re-timing from tape             tier 9
  S148 Cagematch.net, event card page (title-match cross-check;
       also used as a wrestler-bio cross-check source)                tier 4
  S149 WWE.com, 'Announcer lineup for Royal Rumble and Royal Rumble
       Kickoff' article                                               tier 1
  S150 WhatCulture, 'Did Heath Slater Set New WWE Royal Rumble
       Record?' article                                              tier 12
  S151 KhelNow.com, 'Top 13 quickest WWE Royal Rumble eliminations
       of all time' listicle                                         tier 12

CROSS-VALIDATION RESULTS:
  - Entry order (1-30) and eliminator/order credit: CONFIRMED, agreeing
    identically across 3 independently structured sources (S144's table,
    S145's official table, S146's plain-prose sequential list). An internal
    arithmetic self-consistency check (summing each wrestler's credited
    eliminations = 31, matching 29 actual eliminations + 2 shared-credit
    spots) also balanced exactly.
  - Elimination TIMES: mostly CONFIRMED to the second (S144/S145 agree),
    with several trivial (<25s) variances against S147's independent
    re-timing -- not treated as genuine conflicts, just noted. ONE major
    exception: Sheamus's elimination time is genuinely CONFLICTING --
    S145 (WWE.com, tier 1) states 0:20; S144's own footnote plus S147, S150
    and S151 (four independent, differently-sourced re-timings) converge on
    roughly 2-3 seconds instead, with Heath Slater himself claiming as
    little as 0.8s. This script records S145's tier-1 figure in the
    structured field per DEFINITIONS.md's tie-break convention, but logs
    data_quality_status=CONFLICTING with the fan-consensus values preserved
    in flags.csv rather than silently trusting the official number. See
    F367.
  - Total match duration: ~65:27-65:29 across sources, effectively agreeing
    (S144 gives 1:05:27; S147's independent stopwatch analysis gives
    65:29) -- treated as CONFIRMED at this near-identical figure.
  - Card-level detail: Cesaro and Sheamus (as "The Bar") defeated Seth
    Rollins & Jason Jordan for the Raw Tag Team Championship EARLIER on
    this same card, making them the reigning Raw Tag Team Champions at the
    moment they entered this Rumble match (#15 and #11 respectively) --
    CONFIRMED via S144/S148. Rollins, having just lost that title, also
    entered this Rumble later the same night (#18).
  - Entry #10 was advertised as Tye Dillinger, but he was written off via a
    backstage-attack angle before the match and Sami Zayn took the spot --
    CONFIRMED, S144/S146.
  - Rey Mysterio (#27) returned as a surprise after leaving WWE around 2015
    -- at the time of this show he was not under a full-time WWE contract
    (working AAA/Lucha Underground); The Hurricane/Shane Helms (#21) was
    working as a WWE backstage producer, not an active wrestler, at the
    time of his surprise entry.

WHAT'S ACTUALLY KNOWN THIS YEAR: entry order and eliminator credit CONFIRMED
for all 30 entrants/29 eliminations. Event-level facts (date, venue,
attendance, commentary, undercard/title matches) CONFIRMED via 2+ sources.
Global match-clock timing (elimination_clock_time) left UNKNOWN throughout,
matching RR2017M's precedent -- individual ring_time (survival duration) IS
populated directly from sources rather than derived.
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
EVENT_ID = "RR2018M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S144", "Wikipedia (English), 'Royal Rumble (2018)' event article", "reference_site", "https://en.wikipedia.org/wiki/Royal_Rumble_(2018)", 10, "Wikipedia/reference sites", "2026-09-20",
     "Full entrant/elimination table, event facts, commentary, card. Independently agrees with S145/S146 on entry "
     "order exactly. Carries its own footnote acknowledging the Sheamus elimination-time dispute -- see F367."),
    ("S145", "WWE.com, official 'Full 2018 30-Man Royal Rumble Match statistics' page", "official_wwe", "https://www.wwe.com/shows/royalrumble/article/2018-royal-rumble-statistics-entrants-eliminations", 1, "WWE / official sources", "2026-09-20",
     "Official per-wrestler eliminated-by/time table for all 30 entrants. Agrees exactly with S144/S146 on entry "
     "order and eliminator credit. Its 0:20 figure for Sheamus's elimination is a clear outlier versus four "
     "independent fan-timed sources -- see F367."),
    ("S146", "WrestlingInc.com, 'WWE Royal Rumble 2018 Men's Match Orders Of Entry And Elimination' article", "contemporary_publication", "https://www.wrestlinginc.com/news/2018/01/wwe-royal-rumble-2018-men-match-orders-of-entry-and-636433/", 9, "Contemporary wrestling publication", "2026-09-20",
     "Independent, differently-structured (plain sequential list, not a table) cross-check of entry order and "
     "elimination order -- matches S144/S145 exactly on both sequences."),
    ("S147", "Cageside Seats, 'Men's Royal Rumble 2018 Match Time and Statistics' -- independent fan re-timing", "contemporary_publication", "https://www.cagesideseats.com/wwe/2018/2/3/16967818/wwe-royal-rumble-2018-mens-match-time-statistics", 9, "Contemporary wrestling publication", "2026-09-20",
     "Independent (not WWE-sourced) stopwatch re-timing used to stress-test official elimination times. Source of "
     "most minor timing variances noted in this script's docstring, and one of four independent sources "
     "converging on ~2-3s for the Sheamus elimination versus S145's 20s -- see F367."),
    ("S148", "Cagematch.net, event card page and individual wrestler profile pages", "reference_site", "https://www.cagematch.net/?id=1&nr=178577", 4, "Cagematch", "2026-09-20",
     "Card-level title-match cross-check (confirms The Bar won the Raw Tag Team Championship earlier the same "
     "card). Also used as a 2nd, independent cross-check source for new-wrestler bio data alongside S022."),
    ("S149", "WWE.com, 'Announcer lineup for Royal Rumble and Royal Rumble Kickoff' article", "official_wwe", "https://www.wwe.com/shows/royalrumble/article/announcer-lineup-for-royal-rumble-and-royal-rumble-kickoff", 1, "WWE / official sources", "2026-09-20",
     "Official, match-by-match commentary team breakdown -- confirms Michael Cole, Corey Graves, JBL and Jerry "
     "Lawler specifically for the men's Royal Rumble match, corroborated independently by S144's live-recap note."),
    ("S150", "WhatCulture, 'Did Heath Slater Set New WWE Royal Rumble Record?' article", "other_stats_site", "https://whatculture.com/wwe/did-heath-slater-set-new-wwe-royal-rumble-record", 12, "Other reputable site", "2026-09-20",
     "Independent discussion of the Sheamus elimination-time dispute, including Heath Slater's own claimed figure "
     "and an explicit statement that WWE.com's 20-second figure looks wrong on tape -- see F367."),
    ("S151", "KhelNow.com, 'Top 13 quickest WWE Royal Rumble eliminations of all time' listicle", "other_stats_site", "https://khelnow.com/wwe/2024-01-quickest-royal-rumble-eliminations", 12, "Other reputable site", "2026-09-20",
     "A 4th independent figure (2.2s) for the Sheamus elimination, establishing that fan-side trackers cluster "
     "around 2-3 seconds versus WWE.com's outlier 20-second figure -- see F367."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# ENTRY ORDER (CONFIRMED, S144+S145+S146 agree exactly)
# ---------------------------------------------------------------------------
all_names = [
    "Rusev", "Finn Balor", "Rhyno", "Baron Corbin", "Heath Slater", "Elias", "Andrade", "Bray Wyatt", "Big E",
    "Sami Zayn", "Sheamus", "Xavier Woods", "Apollo Crews", "Shinsuke Nakamura", "Cesaro", "Kofi Kingston",
    "Jinder Mahal", "Seth Rollins", "Matt Hardy", "John Cena", "The Hurricane", "Aiden English", "Adam Cole",
    "Randy Orton", "Titus O'Neil", "The Miz", "Rey Mysterio", "Roman Reigns", "Goldust", "Dolph Ziggler",
]
assert len(all_names) == 30
ENTRY_NUMBERS = {name: i + 1 for i, name in enumerate(all_names)}
assert ENTRY_NUMBERS["Shinsuke Nakamura"] == 14 and ENTRY_NUMBERS["Roman Reigns"] == 28

# Individual survival ("ring") times, as directly stated by S144/S145 (agree exactly
# except where noted). Sheamus's figure is the disputed one -- see docstring/F367.
survival = {
    "Rusev": "30:28", "Finn Balor": "57:38", "Rhyno": "2:06", "Baron Corbin": "1:06", "Heath Slater": "0:33",
    "Elias": "26:00", "Andrade": "29:24", "Bray Wyatt": "20:38", "Big E": "14:14", "Sami Zayn": "6:57",
    "Sheamus": "0:20", "Xavier Woods": "8:24", "Apollo Crews": "5:16", "Shinsuke Nakamura": "44:38",
    "Cesaro": "5:08", "Kofi Kingston": "5:41", "Jinder Mahal": "3:48", "Seth Rollins": "19:01",
    "Matt Hardy": "1:17", "John Cena": "29:14", "The Hurricane": "0:45", "Aiden English": "2:16",
    "Adam Cole": "6:52", "Randy Orton": "13:55", "Titus O'Neil": "6:07", "The Miz": "5:20",
    "Rey Mysterio": "9:40", "Roman Reigns": "21:52", "Goldust": "2:43", "Dolph Ziggler": "2:01",
}
assert set(survival) == set(all_names)
SURVIVAL_TIME_DISPUTED = {"Sheamus"}

# Elimination order (1st-29th).
ELIM_ORDER = [
    "Rhyno", "Baron Corbin", "Sheamus", "Heath Slater", "Sami Zayn", "Apollo Crews", "Xavier Woods", "Big E",
    "Cesaro", "Jinder Mahal", "Kofi Kingston", "Rusev", "Matt Hardy", "Bray Wyatt", "Elias", "The Hurricane",
    "Aiden English", "Andrade", "Adam Cole", "Titus O'Neil", "The Miz", "Seth Rollins", "Goldust", "Dolph Ziggler",
    "Randy Orton", "Rey Mysterio", "Finn Balor", "John Cena", "Roman Reigns",
]
assert len(ELIM_ORDER) == 29
elim_number = {name: i + 1 for i, name in enumerate(ELIM_ORDER)}
DISPUTED_ORDER = set()  # elimination ORDER itself is not in dispute this year; only Sheamus's TIME is (see above)

FINAL_TWO = {"Shinsuke Nakamura", "Roman Reigns"}
FINAL_THREE = {"Shinsuke Nakamura", "Roman Reigns", "John Cena"}
FINAL_FOUR = {"Shinsuke Nakamura", "Roman Reigns", "John Cena", "Finn Balor"}

# name -> (eliminator names, is_shared, notes)
ELIMINATORS = {
    "Rhyno": (["Baron Corbin"], False, ""),
    "Baron Corbin": (["Finn Balor"], False, "Cageside Seats' independent re-timing gives 1:00 versus the primary sources' 1:06 -- immaterial variance, not logged as a genuine conflict."),
    "Sheamus": (["Heath Slater"], False, "CONFLICTING elimination time -- WWE.com states 0:20; Wikipedia's own footnote plus 3 independent fan-timed sources (Cageside Seats, WhatCulture, KhelNow.com) converge on roughly 2-3 seconds instead, with Heath Slater himself claiming as little as 0.8 seconds. Logged as CONFLICTING rather than silently picking one -- see F367."),
    "Heath Slater": (["Bray Wyatt"], False, ""),
    "Sami Zayn": (["Shinsuke Nakamura"], False, "Zayn took this slot after advertised entrant Tye Dillinger was written off via a backstage-attack angle before the match."),
    "Apollo Crews": (["Cesaro"], False, ""),
    "Xavier Woods": (["Jinder Mahal"], False, ""),
    "Big E": (["Jinder Mahal"], False, ""),
    "Cesaro": (["Seth Rollins"], False, "Cesaro (with Sheamus, as The Bar) had won the Raw Tag Team Championship earlier the same card, entering this Rumble as reigning tag champion."),
    "Jinder Mahal": (["Kofi Kingston"], False, ""),
    "Kofi Kingston": (["Andrade"], False, "Moments before this elimination, New Day partners Xavier Woods and Big E cushioned a Kingston near-elimination at ringside with a platter of pancakes -- the widely-replayed 'pancake save' -- buying him extra time before he was eliminated shortly after anyway."),
    "Rusev": (["Bray Wyatt", "Matt Hardy"], True, "Shared elimination credit -- S144 and S145 agree."),
    "Matt Hardy": (["Bray Wyatt"], False, "S144's table carries an explicit footnote: Hardy and Wyatt eliminated each other simultaneously in the same spot -- notable in hindsight, since the two became the 'Deleters of Worlds' tag team later in 2018."),
    "Bray Wyatt": (["Matt Hardy"], False, "Simultaneous/mutual elimination with Matt Hardy -- see note on Hardy's row."),
    "Elias": (["John Cena"], False, ""),
    "The Hurricane": (["John Cena"], False, "Shane Helms, working as a WWE backstage producer at the time rather than an active wrestler, entered as a surprise."),
    "Aiden English": (["Finn Balor"], False, ""),
    "Andrade": (["Randy Orton"], False, "Surprise NXT call-up."),
    "Adam Cole": (["Rey Mysterio"], False, "Surprise NXT call-up."),
    "Titus O'Neil": (["Roman Reigns"], False, ""),
    "The Miz": (["Roman Reigns", "Seth Rollins"], True, "Shared elimination credit -- S144 and S145 agree."),
    "Seth Rollins": (["Roman Reigns"], False, "Rollins (with Jason Jordan) lost the Raw Tag Team Championship to The Bar (Cesaro & Sheamus) earlier the same card, before entering this Rumble at #18."),
    "Goldust": (["Dolph Ziggler"], False, ""),
    "Dolph Ziggler": (["Finn Balor"], False, ""),
    "Randy Orton": (["Roman Reigns"], False, ""),
    "Rey Mysterio": (["Finn Balor"], False, "Mysterio's return was his first WWE appearance since leaving around 2015; at the time of this show he was not under a full-time WWE contract (working AAA/Lucha Underground) -- contemporary reporting was uncertain whether this was a one-off nostalgia spot, though he signed a new full-time WWE deal later in 2018 (general knowledge, not independently re-sourced this pass; his eventual 2023 WWE Hall of Fame induction is already tracked separately in this database's wrestlers.csv)."),
    "Finn Balor": (["John Cena"], False, "Longest individual survival time of the match (57:38), agreed across all sources -- the match's 'Iron Man.'"),
    "John Cena": (["Shinsuke Nakamura"], False, "Cena's entry was pre-announced by himself via Twitter on Jan 1, 2018, not a surprise -- framed around his pursuit of a then-record-tying 17th world title (tied with Ric Flair at 16 at the time)."),
    "Roman Reigns": (["Shinsuke Nakamura"], False, "The winning elimination -- Nakamura hit a Kinshasa that Reigns countered into a Spear attempt, then delivered a second Kinshasa for the elimination."),
}
assert set(ELIMINATORS) == set(ELIM_ORDER)

# ---------------------------------------------------------------------------
# WRESTLERS -- new to this database this pass. Bios researched live and
# cross-checked against 2 independent sources (S022 Wikipedia bios + S148
# Cagematch.net profiles) where both agree (CONFIRMED); where they conflict,
# left as a named discrepancy (see flags.csv, F368). WWE Hall of Fame status
# checked for all 6 as part of this build, per Shane's standing process --
# none are inducted as of today (2026-09-20); none are deceased.
# ---------------------------------------------------------------------------
# (ring_name, real_name, real_name_status, gender, dob, dob_status, deceased_date,
#  birthplace, birthplace_status, nationality, debut_year_company, hall_of_fame_year,
#  aliases_ring_names, wrestling_style, notes, source_ids)
new_wrestlers = [
    ("Finn Balor", "Fergal Devitt", "CONFIRMED", "M", "1981-07-25", "CONFIRMED", "", "Bray, County Wicklow, Ireland", "CONFIRMED", "Irish", "", "",
     "Finn Balor", "", "Rumble debut, entered #2. Survived 57:38, the longest individual time of the match, eliminating 4 (Baron Corbin, Aiden English, Rey Mysterio, Dolph Ziggler) before his own elimination by John Cena. Not a WWE Hall of Famer as of this build (2026-09-20).", "S022;S148;S144;S145"),
    ("Elias", "Jeffrey Sciullo", "CONFIRMED", "M", "1987-11-22", "CONFIRMED", "", "Pittsburgh, Pennsylvania, U.S.", "CONFIRMED", "", "", "",
     "", "", "Rumble debut, entered #6. Survived 26:00, eliminated by John Cena. Middle name is CONFLICTING between sources ('Daniel' vs. 'Logan') -- left off this database's real_name field pending resolution; see F368. Not a WWE Hall of Famer as of this build.", "S022;S148"),
    ("Andrade", "Manuel Alfonso Andrade Oropeza", "CONFIRMED", "M", "1989-11-03", "CONFIRMED", "", "Gomez Palacio, Durango, Mexico", "CONFIRMED", "Mexican", "", "",
     "Andrade Cien Almas; Andrade El Idolo", "", "Rumble debut, entered #7 as a surprise NXT call-up, billed as 'Andrade “Cien” Almas' at this event. Survived 29:24, eliminated by Randy Orton. Not a WWE Hall of Famer as of this build.", "S022;S148"),
    ("Shinsuke Nakamura", "Shinsuke Nakamura", "CONFIRMED", "M", "1980-02-24", "CONFIRMED", "", "Kyotango, Kyoto Prefecture, Japan", "CONFIRMED", "Japanese", "", "",
     "", "", "Rumble debut, entered #14 and WON, eliminating 3 (Sami Zayn, John Cena, Roman Reigns) -- the last coming as the match-winning elimination. Chose to challenge for the WWE Championship at WrestleMania 34. Wrestles under his own legal name. Not a WWE Hall of Famer as of this build.", "S022;S148"),
    ("Aiden English", "Matthew Thomas Rehwoldt", "CONFIRMED", "M", "1987-10-07", "CONFIRMED", "", "Chicago, Illinois, U.S.", "CONFIRMED", "", "", "",
     "", "", "Rumble debut, entered #22. Survived 2:16, eliminated by Finn Balor. Not a WWE Hall of Famer as of this build.", "S022;S148"),
    ("Adam Cole", "Austin Kirk Jenkins", "PROBABLE", "M", "1989-07-05", "CONFIRMED", "", "Lancaster, Pennsylvania, U.S.", "CONFLICTING", "", "", "",
     "", "", "Rumble debut, entered #23 as a surprise NXT call-up. Survived 6:52, eliminated by Rey Mysterio. Birthplace is CONFLICTING between sources (Wikipedia: Lancaster, PA; Cagematch.net: Panama City, FL) -- Lancaster is the better-sourced claim (a local paper independently calls him a 'Lancaster County native') but Cagematch's claim isn't refuted anywhere found; see F368. Not a WWE Hall of Famer as of this build.", "S022;S148"),
]

reused = {
    "Rusev": "rusev", "Rhyno": "rhyno", "Baron Corbin": "baron-corbin", "Heath Slater": "heath-slater",
    "Bray Wyatt": "bray-wyatt", "Big E": "big-e", "Sami Zayn": "sami-zayn", "Sheamus": "sheamus",
    "Xavier Woods": "xavier-woods", "Apollo Crews": "apollo-crews", "Cesaro": "cesaro",
    "Kofi Kingston": "kofi-kingston", "Jinder Mahal": "jinder-mahal", "Seth Rollins": "seth-rollins",
    "Matt Hardy": "matt-hardy", "John Cena": "john-cena", "The Hurricane": "the-hurricane",
    "Randy Orton": "randy-orton", "Titus O'Neil": "titus-oneil", "The Miz": "the-miz",
    "Rey Mysterio": "rey-mysterio", "Roman Reigns": "roman-reigns", "Goldust": "goldust",
    "Dolph Ziggler": "dolph-ziggler",
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
NEW_NAMES = [w[0] for w in new_wrestlers]
CHAMPS_AT_ENTRY = {"Cesaro", "Sheamus"}  # won Raw Tag Titles earlier same card, as "The Bar"

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Shinsuke Nakamura")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, is_shared, extra_note = ELIMINATORS.get(name, ([], False, ""))

    notes_parts = [extra_note] if extra_note else []
    if name == "Shinsuke Nakamura":
        notes_parts.append("Entered #14 and won, eliminating Roman Reigns (a Kinshasa, after Reigns countered an "
                            "earlier Kinshasa into a Spear attempt) in the match's final moments. Chose to "
                            "challenge AJ Styles for the WWE Championship at WrestleMania 34.")

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
            "is_disputed": "FALSE",
            "simultaneous_group_id": "",
            "data_quality_status": "CONFIRMED",
            "source_ids": "S144;S145;S146",
            "notes": "",
        })

    er = {
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": "CONFIRMED",
        "ring_name_at_time": name, "name_displayed_at_event": name,
        "prior_rumble_appearances_count": "", "rumble_appearance_no": "",
        "is_first_rumble_appearance": "TRUE" if name in NEW_NAMES else "", "is_company_debut": "UNKNOWN",
        "previous_rumble_year": "", "previous_rumble_result": "", "previous_rumble_elimination_no": "",
        "is_rumble_debut": "TRUE" if name in NEW_NAMES else "",
        "company_debut_date": "",
        "is_returning_wrestler": "TRUE" if name in ("Rey Mysterio", "The Hurricane") else "",
        "absence_length": "",
        "age_at_event": "", "age_status": "UNKNOWN",
        "billed_height_m_at_event": "", "billed_weight_kg_at_event": "", "billed_from_at_event": "",
        "physical_status": "UNKNOWN",
        "alignment": "", "alignment_status": "UNKNOWN",
        "gimmick_at_event": "",
        "manager_at_event": "",
        "tag_team_name": "The Bar" if name in ("Cesaro", "Sheamus") else "",
        "faction_stable": "",
        "current_champion_title": "Raw Tag Team Championship" if name in CHAMPS_AT_ENTRY else "",
        "championship_level": "world_tag_team" if name in CHAMPS_AT_ENTRY else "",
        "championship_partner": ("sheamus" if name == "Cesaro" else "cesaro") if name in CHAMPS_AT_ENTRY else "",
        "reign_number": "", "title_won_date": "2018-01-28" if name in CHAMPS_AT_ENTRY else "UNKNOWN",
        "days_into_reign_at_event": 0 if name in CHAMPS_AT_ENTRY else "",
        "title_defended_same_card": "FALSE",
        "title_lost_same_card": "TRUE" if name == "Seth Rollins" else "FALSE",
        "elim_number": "" if is_winner else elim_number[name],
        "elim_number_status": "N/A" if is_winner else "CONFIRMED",
        "eliminated_by_ids": ";".join(wrestler_ids[e] for e in elim_by),
        "elimination_clock_time": "", "elimination_clock_seconds": "",
        "ring_time": ring_time, "ring_time_seconds": ring_time_s,
        "ring_time_status": "CONFLICTING" if name in SURVIVAL_TIME_DISPUTED else "CONFIRMED",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if name == "Roman Reigns" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "TRUE" if name in ("Andrade", "Adam Cole", "Rey Mysterio", "The Hurricane") else "FALSE",
        "legend_returning": "TRUE" if name in ("Rey Mysterio", "The Hurricane") else "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "TRUE" if name in ("Rey Mysterio", "The Hurricane") else "FALSE",
        "wrestled_earlier_on_card": "TRUE" if name in ("Seth Rollins", "Cesaro", "Sheamus") else "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFLICTING" if name in SURVIVAL_TIME_DISPUTED else "CONFIRMED",
        "source_ids": "S144;S145;S146",
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
    ("F367", EVENT_ID, "entrants", "sheamus", "ring_time", "conflicting_sources",
     "Sheamus's elimination/survival time is genuinely CONFLICTING between sources: S145 (WWE.com, tier 1) states "
     "0:20 (20 seconds); S144 (Wikipedia)'s own footnote gives 0:02; S147 (Cageside Seats' independent fan "
     "re-timing) gives 0:03; S151 (KhelNow.com) gives 2.2 seconds; S150 (WhatCulture) explicitly calls WWE.com's "
     "20-second figure 'clearly wrong given what's visible on tape' without certifying an exact replacement; and "
     "Heath Slater himself has publicly claimed as little as 0.8 seconds. Four independent, differently-sourced "
     "re-timings converge on roughly 2-3 seconds, versus a single official WWE.com figure of 20 seconds -- likely "
     "a WWE.com data-entry error, though no WWE correction confirming that theory was found. This script records "
     "S145's tier-1 figure (0:20) in the structured ring_time field per DEFINITIONS.md's source-tier tie-break "
     "convention, but marks ring_time_status=CONFLICTING (not CONFIRMED) on Sheamus's entrant row rather than "
     "silently trusting the official number over four independent counter-sources. Her eliminator credit (Heath "
     "Slater) and the elimination's position in the order (3rd) are NOT in dispute -- only the exact duration.",
     "S144;S145;S147;S150;S151", "open", "2026-09-20"),
    ("F368", EVENT_ID, "wrestlers", "elias;adam-cole", "real_name;birthplace", "conflicting_sources",
     "Two minor bio-data conflicts surfaced while researching this pass's new wrestlers: (1) Elias's middle name "
     "is given as 'Daniel' by Wikipedia (S022) but 'Logan' by two other independent sources (prowrestling.fandom."
     "com, gerweck.net) -- his first name, surname, DOB and birthplace are consistent across all sources, only "
     "the middle name conflicts, so real_name is left as 'Jeffrey Sciullo' without a middle name rather than "
     "guessing between the two. (2) Adam Cole's birthplace is given as Lancaster, Pennsylvania by Wikipedia (S022, "
     "corroborated by a LancasterOnline article independently calling him a 'Lancaster County native') but as "
     "Panama City, Florida by Cagematch.net (S148) -- Lancaster is the better-sourced claim but Cagematch's claim "
     "was not found refuted anywhere, so birthplace_status is recorded as CONFLICTING rather than CONFIRMED.",
     "S022;S148", "open", "2026-09-20"),
    ("F369", EVENT_ID, "wrestlers", "finn-balor;elias;andrade;shinsuke-nakamura;aiden-english;adam-cole", "hall_of_fame_year", "corrected",
     "Continuing the process established at RR2017M: WWE Hall of Fame status and deceased status were checked for "
     "all 6 wrestlers new to this database this pass, as part of this build rather than a later audit. Result: "
     "none of the 6 are WWE Hall of Fame inductees as of today (2026-09-20); none are deceased. Bio data (real "
     "name, DOB, birthplace) was cross-checked against 2 independent sources (S022 Wikipedia + S148 Cagematch.net) "
     "for 4 of the 6, upgrading those fields to CONFIRMED rather than this database's usual single-source-pass "
     "PROBABLE -- see F368 for the 2 fields where those 2 sources disagreed instead of agreeing.",
     "S022;S148", "resolved", "2026-09-20"),
    ("F370", EVENT_ID, "events", EVENT_ID, "notes", "unverified",
     "Entry #10 was originally advertised as Tye Dillinger (RR2017M's beloved 'Perfect 10'), but he was written "
     "off television via a backstage-attack angle shortly before this event and Sami Zayn took the vacated spot "
     "instead -- CONFIRMED via S144/S146, but Dillinger's own removal-angle detail is not independently "
     "re-sourced beyond Wikipedia this pass.",
     "S144;S146", "open", "2026-09-20"),
    ("F371", EVENT_ID, "entrances;moves", "*", "n/a", "out_of_scope_no_tool",
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
        "moment_id": "NM051", "event_id": EVENT_ID, "wrestler_ids_involved": "shinsuke-nakamura",
        "category": "milestone_first",
        "title": "Shinsuke Nakamura wins the Royal Rumble in his first attempt",
        "description": "Nakamura entered #14 and won by eliminating Roman Reigns, choosing to challenge AJ Styles for the WWE Championship at WrestleMania 34.",
        "data_quality_status": "CONFIRMED", "source_ids": "S144;S145",
        "notes": "",
    },
    {
        "moment_id": "NM052", "event_id": EVENT_ID, "wrestler_ids_involved": "kofi-kingston;xavier-woods;big-e",
        "category": "other",
        "title": "The New Day's 'pancake save' for Kofi Kingston",
        "description": "Xavier Woods and Big E cushioned a near-elimination for Kingston at ringside with a platform of pancakes, a widely-replayed comedic spot -- Kingston was eliminated by Andrade a short time later anyway.",
        "data_quality_status": "CONFIRMED", "source_ids": "S147",
        "notes": "",
    },
    {
        "moment_id": "NM053", "event_id": EVENT_ID, "wrestler_ids_involved": "matt-hardy;bray-wyatt",
        "category": "other",
        "title": "Matt Hardy and Bray Wyatt eliminated each other simultaneously",
        "description": "Wikipedia's table carries an explicit footnote noting Hardy and Wyatt eliminated each other at the same moment -- notable in hindsight since the two became the 'Deleters of Worlds' tag team later in 2018.",
        "data_quality_status": "CONFIRMED", "source_ids": "S144",
        "notes": "",
    },
    {
        "moment_id": "NM054", "event_id": EVENT_ID, "wrestler_ids_involved": "rey-mysterio",
        "category": "notable_absence_or_substitution",
        "title": "Rey Mysterio's surprise return after leaving WWE in 2015",
        "description": "Mysterio entered at #27, his first WWE appearance in roughly 3 years -- at the time he was working AAA/Lucha Underground, with contemporary reporting uncertain whether this was a one-off nostalgia spot. He eliminated Adam Cole before being eliminated himself by Finn Balor, lasting 9:40.",
        "data_quality_status": "CONFIRMED", "source_ids": "S144;S146",
        "notes": "He signed a new full-time WWE deal later in 2018 and was inducted into the WWE Hall of Fame in 2023 (already tracked in wrestlers.csv) -- general knowledge, not independently re-sourced this pass.",
    },
    {
        "moment_id": "NM055", "event_id": EVENT_ID, "wrestler_ids_involved": "finn-balor",
        "category": "record",
        "title": "Finn Balor's 57:38 was the longest individual time of the match",
        "description": "Balor entered #2 and survived 57:38 -- fully agreed across all sources as the match's 'Iron Man' -- while also eliminating 4 opponents (Baron Corbin, Aiden English, Rey Mysterio, Dolph Ziggler), tied for the match high.",
        "data_quality_status": "CONFIRMED", "source_ids": "S144;S145;S147",
        "notes": "",
    },
    {
        "moment_id": "NM056", "event_id": EVENT_ID, "wrestler_ids_involved": "cesaro;sheamus;seth-rollins",
        "category": "other",
        "title": "The Bar won the Raw Tag Team Championship earlier the same card, then Cesaro and Sheamus entered the Rumble as reigning champions",
        "description": "Cesaro and Sheamus (as The Bar) defeated Seth Rollins & Jason Jordan for the Raw Tag Team Championship earlier on this card. Rollins, having just lost the title, also entered the Rumble later that night at #18; Cesaro and Sheamus entered at #15 and #11 respectively as the reigning champions.",
        "data_quality_status": "CONFIRMED", "source_ids": "S144;S148",
        "notes": "",
    },
]
with open(os.path.join(DATA_DIR, "notable_moments.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=NOTABLE_MOMENTS_FIELDS)
    for row in nm_rows:
        writer.writerow(row)

flags2 = [
    ("F372", EVENT_ID, "notable_moments", "NM051;NM052;NM053;NM054;NM055;NM056", "n/a", "corrected",
     "Added 6 notable_moments.csv rows for this newly-built event: Shinsuke Nakamura's Rumble win in his first "
     "attempt, The New Day's 'pancake save,' the Hardy/Wyatt simultaneous elimination, Rey Mysterio's surprise "
     "return, Finn Balor's match-long 57:38 survival time, and The Bar/Seth Rollins Raw Tag Team Championship "
     "swap earlier on the card.",
     "S144;S145;S147;S148", "resolved", "2026-09-20"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags2)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2018", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2018-01-28",
    "venue": "Wells Fargo Center", "city_region": "Philadelphia, Pennsylvania", "country": "United States",
    "attendance_official": "", "attendance_reported": 17629,
    "entry_interval_seconds": "", "entrant_count": 30,
    "duration_total": "1:05:27", "duration_status": "CONFIRMED",
    "winner_id": "shinsuke-nakamura", "runner_up_id": "roman-reigns",
    "final_two_ids": "shinsuke-nakamura;roman-reigns",
    "final_three_ids": "shinsuke-nakamura;roman-reigns;john-cena",
    "final_four_ids": "shinsuke-nakamura;roman-reigns;john-cena;finn-balor",
    "first_entrant_id": "rusev", "second_entrant_id": "finn-balor", "final_entrant_id": "dolph-ziggler",
    "first_elimination_id": "rhyno", "last_elimination_before_winner_id": "roman-reigns",
    "eliminations_count": 29, "eliminators_count": 18,
    "surprise_entrants_count": 4,
    "champions_in_field_count": 2, "hall_of_famers_in_field_count": 0,
    "tag_teams_count": 1, "factions_count": "UNKNOWN",
    "commentary_team": "Michael Cole, Corey Graves, John \"Bradshaw\" Layfield (JBL), Jerry \"The King\" Lawler",
    "ring_announcer": "UNKNOWN",
    "referees": "UNKNOWN",
    "special_rules": "Standard Royal Rumble rules. No title was defended within the match itself this year -- the winner instead earned a title shot at WrestleMania 34.",
    "title_on_the_line": "FALSE",
    "championship_implications": "The winner earned the right to challenge for a world championship at WrestleMania 34 -- their choice between Raw's Universal Championship or SmackDown's WWE Championship. Shinsuke Nakamura won and chose to challenge AJ Styles for the WWE Championship. Separately, The Bar (Cesaro & Sheamus) won the Raw Tag Team Championship from Seth Rollins & Jason Jordan earlier the same card, before all three entered this Rumble.",
    "winners_reward": "A world championship match at WrestleMania 34 -- winner's choice between Raw's Universal Championship and SmackDown's WWE Championship. Nakamura chose the WWE Championship, held by AJ Styles.",
    "historical_significance": (
        "Shinsuke Nakamura's Royal Rumble win in his first attempt, entering at #14 and eliminating Roman Reigns "
        "(a Kinshasa, after Reigns countered an earlier Kinshasa into a Spear attempt) in the match's final "
        "moments. Finn Balor and Roman Reigns tied for the match-high elimination count at 4 apiece, though one "
        "of Reigns's four (The Miz) was a shared credit with Seth Rollins, making Balor the only wrestler with 4 "
        "clean solo eliminations; Balor also posted the longest individual survival time of the match at 57:38. "
        "Rey Mysterio made a surprise return at #27, his first WWE appearance in roughly 3 years, having spent "
        "the intervening time with AAA and Lucha Underground. Andrade (billed as 'Andrade “Cien” Almas') "
        "and Adam Cole both entered as surprise NXT call-ups. Matt Hardy and Bray Wyatt eliminated each other "
        "simultaneously -- a fitting preview, in hindsight, of their 'Deleters of Worlds' tag team later that "
        "year. Cesaro and Sheamus (as The Bar) entered as the reigning Raw Tag Team Champions, having won the "
        "title from Seth Rollins & Jason Jordan earlier the same card; Rollins himself also competed in this "
        "Rumble later that night. This was the second Royal Rumble to share a card with a Women's Royal Rumble "
        "match, held for the first time ever this same night -- see this database's separate RR2018W record."
    ),
    "notes": (
        "Entry order and eliminator credit CONFIRMED for all 30 entrants via 2-3 independent sources each. "
        "Sheamus's individual elimination time is CONFLICTING between the official WWE.com figure (0:20) and "
        "four independent fan-timed re-checks that converge on roughly 2-3 seconds -- see F367; the elimination's "
        "order and eliminator credit are not in dispute, only the exact duration. Global match-clock timing "
        "(elimination_clock_time) left UNKNOWN throughout, matching RR2017M's precedent. WWE Hall of Fame status "
        "was checked for all 6 newly-added wrestlers as part of this build, per Shane's standing process (F369) "
        "-- none are inducted as of this build. Built as a fully separate event/record from RR2018W (the first "
        "Women's Royal Rumble, held the same night) per Shane's explicit instruction to keep the two matches "
        "separate."
    ),
    "data_quality_status": "CONFLICTING", "source_ids": "S144;S145;S146;S147;S148;S149",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2018 Men's build complete: {len(new_wrestlers)} new wrestlers ({len(reused)} reused), "
      f"{len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, {len(sources)} sources logged, "
      f"{len(flags) + len(flags2)} flags, {len(nm_rows)} notable_moments rows.")
