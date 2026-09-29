# -*- coding: utf-8 -*-
"""
Builds all rows for the 2020 Men's Royal Rumble -- schema v2.

Royal Rumble 2020, January 26, 2020, Minute Maid Park, Houston, Texas. This
is the MEN'S match only. The Women's Royal Rumble held the same night is a
fully separate event/record -- see build_2020_women.py -- per Shane's
standing instruction to keep the two matches separate.

NEW PROCESS, continuing from RR2018M/RR2018W/RR2019M/RR2019W: WWE Hall of
Fame status (and deceased status) is checked for every new wrestler as part
of building the event they're first added in. Applied here for all 7
wrestlers new to this database this pass -- none are HOF-inducted as of
today (2026-09-21); all are alive.

King Corbin (entrant #22) is billed under a post-"King of the Ring 2019"
coronation moniker, but is the SAME underlying character/wrestler_id as this
database's existing "Baron Corbin" (a RR2019M entrant) -- retaining the
"Corbin" surname and in-ring persona, unlike a full gimmick reinvention.
Reused as wrestler_id "baron-corbin" with ring_name_at_time="King Corbin",
matching this database's existing precedent for minor moniker additions
(compare "smash"/"Repo Man" -- a single wrestler_id spanning a ring-name
change, vs. the full-reinvention splits used for husky-harris/bray-wyatt and
diesel/kevin-nash). See F400.

SOURCES CONSULTED THIS PASS (live web research via a dedicated research
agent, cross-validated against each other -- see flags.csv for where they
disagreed -- plus direct follow-up research this build for 5 additional new
wrestlers the agent did not generate fresh bios for, and for 3 championship
win-dates). Per the methodology learned on prior years, no single generic
Wikipedia table-extraction was trusted blind; the agent's first extraction
attempt came back internally inconsistent (a chronologically impossible
cross-credit pattern) and was discarded, then re-pulled with a stricter
row-by-row prompt and cross-checked by wrestler NAME across 4 independent
sources, plus an arithmetic self-consistency check (elimination order 1-29
used exactly once, no gaps/dupes; eliminator-credit tally sums to exactly
29, matching 29 eliminations with zero shared-credit spots this year):
  S184 Wikipedia (English), 'Royal Rumble (2020)' event article           tier 10
  S185 Cagematch.net, event page                                          tier 4
  S186 TheSportster.com (paraphrasing WWE.com's official match recap)     tier 9
  S187 WrestleTalk.com, surprise-entrant listing                          tier 9
  S188 dropthebelt.com, independent entrant/elimination-count aggregator  tier 12
  S189 WhatCulture.com, attendance-figure dispute article                 tier 12
  S190 411Mania.com, attendance-figure article                            tier 12
  S191 Wikipedia, individual bio pages: Keith Lee, Matt Riddle, Aleister
       Black, MVP, The New Day (bio/title cross-checks)                   tier 10
  S192 WWE.com, Oct 4 2019 SmackDown recap ("Brock Lesnar def. Kofi
       Kingston") -- confirms Lesnar's WWE Championship win date          tier 1
  S193 Cageside Seats / WWE.com, Nov 8 2019 SmackDown recap (The New Day
       wins SmackDown Tag Titles from The Revival) -- confirms Kofi
       Kingston & Big E's tag title win date                              tier 9
  S194 Wikipedia, 'Extreme Rules (2019)' event article (Nakamura wins IC
       Championship from Finn Balor) -- confirms Nakamura's IC title date tier 10
  S195 Wikipedia, individual bio pages for Robert Roode, John Hennigan/
       Morrison, Ricochet (Trevor Mann), Karl Anderson, and Luke Gallows/
       Andrew Hankinson -- researched directly this build, since the
       research agent did not generate fresh bios for these 5 (each is a
       genuinely new wrestler_id in THIS DATABASE despite being an
       established WWE performer -- the "new to database" vs "new to WWE"
       distinction flagged for correction after RR2019's build)            tier 10
  S196 Gerweck.net, John Morrison profile -- supplementary source for his
       birthplace/exact debut date, used because Wikipedia's own page
       redirected to a disambiguation/summary page lacking full detail    tier 12

CROSS-VALIDATION RESULTS:
  - Entry order (1-30) and eliminator credit: CONFIRMED across Wikipedia,
    Cagematch, and the WWE.com-sourced recap, cross-checked by name.
    Arithmetic self-consistency check passed: 29 eliminations, zero
    3+-person "group" eliminations, credited-elimination tally reconciles
    exactly to 29 (Lesnar 13, McIntyre 6, Edge 3, Rollins 3, Reigns 2,
    Corbin 1, Orton 1).
  - Winner: Drew McIntyre (entrant #16), eliminating Roman Reigns for the
    win after surviving 34:11 (the match's longest individual time).
  - Keith Lee's and Braun Strowman's eliminator credit is genuinely
    CONFLICTING across THREE different versions (WWE.com's official recap
    vs. Wikipedia vs. Cagematch) -- resolved using the majority/official
    version (Brock Lesnar credited solo on both), which is also the only
    version arithmetically consistent with the widely-documented historical
    fact that Lesnar tied the all-time single-Rumble elimination record
    with 13 eliminations this match. See F396.
  - Kevin Owens's eliminator is also flagged: Wikipedia's table credits
    "Seth Rollins and Akam and Rezar" jointly, reflecting real outside
    interference from the Authors of Pain as part of Rollins's storyline --
    but Akam/Rezar were not competitors in this match, so this database
    does not co-credit non-entrants in the structured eliminator field;
    Rollins alone is credited, with the interference documented in notes.
    See F397.
  - Attendance is genuinely CONFLICTING: WWE's official announced figure is
    42,715 (a Minute Maid Park record); Dave Meltzer (Wrestling Observer,
    cited independently by both WhatCulture.com and 411Mania.com) reported
    the actual attendance was closer to ~36,000. Both figures recorded --
    see F398 (a card-wide dispute, shared with build_2020_women.py, which
    carries its own copy of this flag against its own event_id -- this
    reconciles an initial discrepancy between the two research passes, one
    of which had not surfaced the dispute on its first search attempt).
  - WWE Hall of Fame status was checked individually for all 7 new
    wrestlers as of today (2026-09-21) -- none are inducted; none are
    deceased.
  - CORRECTION applied during this build (not by the research agent):
    5 of the agent's "established, no fresh bio needed" names -- Robert
    Roode, John Morrison, Ricochet, Karl Anderson, and Luke Gallows -- were
    independently verified against this database's live wrestlers.csv and
    found to be genuinely NEW wrestler_ids (none had appeared as an entrant
    in any Royal Rumble 1988-2019 built so far), despite being established
    WWE performers with no prior appearance in THIS database. Full bios
    were researched directly for all 5 rather than left blank. This
    resolves the "new to database" vs. "new to WWE" distinction flagged as
    an open risk after the RR2019 build.

WHAT'S ACTUALLY KNOWN THIS YEAR: entry order and eliminator credit CONFIRMED
for all 30 entrants/29 eliminations (0 shared-credit spots this year -- the
Keith Lee/Braun Strowman dispute resolves to solo Lesnar credit on both, not
a shared spot). Event-level facts (date, venue, championship implications)
CONFIRMED via 2+ sources; attendance is CONFLICTING (see above/flags.csv).
Global match-clock timing (elimination_clock_time) left UNKNOWN throughout,
matching this database's established precedent -- individual ring_time
(survival duration) IS populated directly from sources.
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
EVENT_ID = "RR2020M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S184", "Wikipedia (English), 'Royal Rumble (2020)' event article", "reference_site", "https://en.wikipedia.org/wiki/Royal_Rumble_(2020)", 10, "Wikipedia/reference sites", "2026-09-21",
     "Full entrant/elimination table (a first extraction attempt was internally inconsistent and discarded; a clean "
     "re-extraction was cross-checked against 3 other independent sources), event facts, and the Keith Lee/Braun "
     "Strowman cross-shared elimination-credit version -- see F396."),
    ("S185", "Cagematch.net, event page", "reference_site", "https://www.cagematch.net/?id=1&nr=8017", 4, "Cagematch", "2026-09-21",
     "Independent cross-check of entry order/eliminator credit. Its own Keith Lee/Strowman credit version differs "
     "from both Wikipedia's and the WWE.com-sourced recap's -- a 3rd distinct version -- see F396."),
    ("S186", "TheSportster.com (paraphrasing WWE.com's official 2020 Men's Royal Rumble match recap)", "contemporary_publication", "https://www.thesportster.com/wrestling/every-brock-lesnar-victory-in-2020-royal-rumble/", 9, "Contemporary wrestling publication", "2026-09-21",
     "Paraphrases WWE.com's own recap describing Lesnar's 'simultaneous removal' of Keith Lee and Braun Strowman -- "
     "the majority/official version used in this database's structured eliminator fields, consistent with the "
     "widely-documented 13-elimination record. See F396."),
    ("S187", "WrestleTalk.com, surprise-entrant listing", "contemporary_publication", "https://wrestletalk.com/", 9, "Contemporary wrestling publication", "2026-09-21",
     "Cross-check source for this event's surprise/mystery entrants."),
    ("S188", "dropthebelt.com, independent entrant/elimination-count aggregator", "other_stats_site", "https://dropthebelt.com/", 12, "Other reputable site", "2026-09-21",
     "Independently-built stats aggregator; source of several 'surprise entrant' designations (Robert Roode, "
     "Cesaro, Shelton Benjamin, Luke Gallows) not otherwise universally reported as major surprises."),
    ("S189", "WhatCulture.com, 'The Real Attendance Figure For WWE's Royal Rumble 2020 Revealed'", "other_stats_site", "https://whatculture.com/wwe/the-real-attendance-figure-for-wwes-royal-rumble-2020-revealed", 12, "Other reputable site", "2026-09-21",
     "Cites Dave Meltzer/Wrestling Observer's ~36,000 actual-attendance estimate against WWE's announced 42,715 -- "
     "see F398 (card-wide dispute, shared with build_2020_women.py)."),
    ("S190", "411Mania.com, Royal Rumble 2020 attendance-figures article", "other_stats_site", "https://411mania.com/wrestling/wwe-royal-rumble-2020-attendance-figures/", 12, "Other reputable site", "2026-09-21",
     "2nd independent citation of Dave Meltzer's ~36,000 actual-attendance estimate, corroborating S189 -- see F398."),
    ("S191", "Wikipedia, individual bio pages: Keith Lee, Matt Riddle, Aleister Black, MVP, The New Day", "reference_site", "https://en.wikipedia.org/wiki/Keith_Lee_(wrestler)", 10, "Wikipedia/reference sites", "2026-09-21",
     "Bio-data and title-history cross-check source for Keith Lee and Matt Riddle (2 of this pass's 7 new "
     "wrestlers), plus confirmation of Aleister Black's and MVP's already-in-database status and The New Day's "
     "SmackDown Tag Team Championship reign dates."),
    ("S192", "WWE.com, SmackDown Oct 4, 2019 recap: 'Brock Lesnar def. Kofi Kingston to win WWE Championship'", "official_wwe", "https://www.wwe.com/shows/smackdown/wwe-friday-night-smackdown-oct-4-2019/article/brock-lesnar-def-kofi-kingston", 1, "WWE / official sources", "2026-09-21",
     "Confirms Brock Lesnar won the WWE Championship from Kofi Kingston via a Money in the Bank cash-in on this "
     "date -- used to compute his days_into_reign_at_event field (114 days)."),
    ("S193", "WWE.com, SmackDown Nov 8, 2019 recap (Manchester) -- The New Day wins the SmackDown Tag Team Championship from The Revival", "contemporary_publication", "https://www.wwe.com/shows/smackdown/friday-night-smackdown-nov-8-2019", 9, "Contemporary wrestling publication", "2026-09-21",
     "Confirms Big E & Kofi Kingston (with Xavier Woods, not an entrant) won the SmackDown Tag Team Championship on "
     "this date -- used to compute their days_into_reign_at_event field (79 days). Independently corroborated by "
     "the reign's later-reported 111-day length ending Feb 27, 2020, which back-dates the win to Nov 8, 2019."),
    ("S194", "Wikipedia (English), 'Extreme Rules (2019)' event article", "reference_site", "https://en.wikipedia.org/wiki/Extreme_Rules_(2019)", 10, "Wikipedia/reference sites", "2026-09-21",
     "Confirms Shinsuke Nakamura won the WWE Intercontinental Championship from Finn Balor on July 14, 2019 -- used "
     "to compute his days_into_reign_at_event field (196 days)."),
    ("S195", "Wikipedia, individual bio pages for Robert Roode, John Hennigan (John Morrison), Ricochet (Trevor Mann), Karl Anderson (Chad Allegra), and Luke Gallows (Andrew Hankinson)", "reference_site", "https://en.wikipedia.org/wiki/Bobby_Roode", 10, "Wikipedia/reference sites", "2026-09-21",
     "Bio-data source researched directly this build for 5 wrestlers incorrectly treated as 'no fresh bio needed' "
     "by the research agent -- each is a genuinely new wrestler_id in this database. Real names, DOBs, birthplaces, "
     "nationalities, debut dates and pre-2020 championship histories cross-checked against this single "
     "comprehensive source per wrestler."),
    ("S196", "Gerweck.net, John Morrison profile", "other_stats_site", "https://gerweck.net/2009/10/02/john-morrison/", 12, "Other reputable site", "2026-09-21",
     "Supplementary 2nd source for John Morrison's birthplace and exact pro-wrestling debut date, used because his "
     "Wikipedia page redirected to a disambiguation/summary page lacking that level of detail."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# ENTRY ORDER (CONFIRMED, S184+S185+S186 agree by name)
# ---------------------------------------------------------------------------
all_names = [
    "Brock Lesnar", "Elias", "Erick Rowan", "Robert Roode", "John Morrison", "Kofi Kingston", "Rey Mysterio",
    "Big E", "Cesaro", "Shelton Benjamin", "Shinsuke Nakamura", "MVP", "Keith Lee", "Braun Strowman", "Ricochet",
    "Drew McIntyre", "The Miz", "AJ Styles", "Dolph Ziggler", "Karl Anderson", "Edge", "King Corbin", "Matt Riddle",
    "Luke Gallows", "Randy Orton", "Roman Reigns", "Kevin Owens", "Aleister Black", "Samoa Joe", "Seth Rollins",
]
assert len(all_names) == 30
ENTRY_NUMBERS = {name: i + 1 for i, name in enumerate(all_names)}
assert ENTRY_NUMBERS["Brock Lesnar"] == 1 and ENTRY_NUMBERS["Seth Rollins"] == 30

# Individual survival ("ring") times.
survival = {
    "Brock Lesnar": "26:24", "Elias": "1:00", "Erick Rowan": "0:08", "Robert Roode": "0:41",
    "John Morrison": "0:09", "Kofi Kingston": "5:06", "Rey Mysterio": "2:54", "Big E": "0:53", "Cesaro": "0:18",
    "Shelton Benjamin": "0:37", "Shinsuke Nakamura": "0:20", "MVP": "0:24", "Keith Lee": "3:32",
    "Braun Strowman": "1:50", "Ricochet": "3:09", "Drew McIntyre": "34:11", "The Miz": "0:30", "AJ Styles": "7:49",
    "Dolph Ziggler": "12:20", "Karl Anderson": "9:46", "Edge": "23:43", "King Corbin": "4:06", "Matt Riddle": "0:41",
    "Luke Gallows": "2:00", "Randy Orton": "14:37", "Roman Reigns": "16:01", "Kevin Owens": "6:59",
    "Aleister Black": "5:06", "Samoa Joe": "4:25", "Seth Rollins": "4:01",
}
assert set(survival) == set(all_names)

# Elimination order (1st-29th).
ELIM_ORDER = [
    "Elias", "Erick Rowan", "Robert Roode", "John Morrison", "Rey Mysterio", "Big E", "Kofi Kingston", "Cesaro",
    "Shelton Benjamin", "Shinsuke Nakamura", "MVP", "Keith Lee", "Braun Strowman", "Brock Lesnar", "Ricochet",
    "The Miz", "AJ Styles", "Matt Riddle", "King Corbin", "Luke Gallows", "Karl Anderson", "Dolph Ziggler",
    "Aleister Black", "Kevin Owens", "Samoa Joe", "Seth Rollins", "Randy Orton", "Edge", "Roman Reigns",
]
assert len(ELIM_ORDER) == 29
elim_number = {name: i + 1 for i, name in enumerate(ELIM_ORDER)}

FINAL_TWO = {"Drew McIntyre", "Roman Reigns"}
FINAL_THREE = {"Drew McIntyre", "Roman Reigns", "Edge"}
FINAL_FOUR = {"Drew McIntyre", "Roman Reigns", "Edge", "Randy Orton"}

# name -> (eliminator names, is_shared, notes)
ELIMINATORS = {
    "Elias": (["Brock Lesnar"], False, ""),
    "Erick Rowan": (["Brock Lesnar"], False, ""),
    "Robert Roode": (["Brock Lesnar"], False, "Marked as a surprise entrant by dropthebelt.com (single tier-12 source, not major hype)."),
    "John Morrison": (["Brock Lesnar"], False, ""),
    "Rey Mysterio": (["Brock Lesnar"], False, ""),
    "Big E": (["Brock Lesnar"], False, "Entered as reigning co-SmackDown Tag Team Champion alongside Kofi Kingston (won Nov 8, 2019)."),
    "Kofi Kingston": (["Brock Lesnar"], False, "Entered as reigning co-SmackDown Tag Team Champion alongside Big E (won Nov 8, 2019)."),
    "Cesaro": (["Brock Lesnar"], False, "Marked as a surprise entrant by dropthebelt.com."),
    "Shelton Benjamin": (["Brock Lesnar"], False, "Marked as a surprise entrant by dropthebelt.com -- a nostalgia-adjacent veteran appearance."),
    "Shinsuke Nakamura": (["Brock Lesnar"], False, "Entered as reigning Intercontinental Champion (won from Finn Balor at Extreme Rules, July 14, 2019)."),
    "MVP": (["Brock Lesnar"], False, "Surprise returning-veteran appearance -- first WWE appearance in roughly a decade following his December 2010 release."),
    "Keith Lee": (["Brock Lesnar"], False, "Surprise NXT call-up, entering as reigning NXT North American Champion (won 4 days earlier, Jan 22, 2020, from Roderick Strong). Eliminator credit is genuinely CONFLICTING across 3 sources -- WWE.com's official recap and this database's structured field credit Lesnar solely for eliminating Lee and Braun Strowman together; Wikipedia instead cross-credits Lee's own elimination jointly to Lesnar and Strowman; Cagematch gives yet a 3rd version. See F396."),
    "Braun Strowman": (["Brock Lesnar"], False, "Eliminator credit is genuinely CONFLICTING across 3 sources -- see F396 (same dispute as Keith Lee's entry, immediately above)."),
    "Brock Lesnar": (["Drew McIntyre"], False, "Tied the all-time single-Rumble elimination record with 13 credited eliminations (11 solo, plus Keith Lee and Braun Strowman -- see F396) before being eliminated himself. See NM078."),
    "Ricochet": (["Drew McIntyre"], False, ""),
    "The Miz": (["Drew McIntyre"], False, ""),
    "AJ Styles": (["Edge"], False, ""),
    "Dolph Ziggler": (["Roman Reigns"], False, ""),
    "Karl Anderson": (["Randy Orton"], False, ""),
    "Edge": (["Roman Reigns"], False, "Major surprise in-ring return -- Edge had been retired since 2011 due to a career-threatening neck injury. See NM080."),
    "King Corbin": (["Drew McIntyre"], False, "Billed as 'King Corbin' following his 2019 King of the Ring coronation -- same wrestler_id as this database's existing 'Baron Corbin' entrant (RR2019M). See F400."),
    "Matt Riddle": (["King Corbin"], False, "Surprise call-up -- his first WWE main-roster appearance and first Royal Rumble."),
    "Luke Gallows": (["Edge"], False, "Marked as a surprise entrant by dropthebelt.com."),
    "Randy Orton": (["Edge"], False, ""),
    "Roman Reigns": (["Drew McIntyre"], False, "The winning elimination. Reigns finished as runner-up."),
    "Kevin Owens": (["Seth Rollins"], False, "Part of a brief in-ring alliance with Aleister Black and Samoa Joe before being picked off consecutively by Rollins's group. Wikipedia's table additionally credits outside interference from Akam and Rezar (Authors of Pain, non-entrants in this match) assisting Rollins on this elimination; not co-credited in the structured eliminator field since AOP were not competitors in this match. See F397 and NM081."),
    "Aleister Black": (["Seth Rollins"], False, "Part of the brief Owens/Black/Joe in-ring alliance."),
    "Samoa Joe": (["Seth Rollins"], False, "Part of the brief Owens/Black/Joe in-ring alliance."),
    "Seth Rollins": (["Drew McIntyre"], False, "Backed by outside interference from Akam & Rezar (Authors of Pain) throughout the match, as part of his 'Monday Night Messiah' heel-authority storyline. See NM081."),
}
assert set(ELIMINATORS) == set(ELIM_ORDER)

DISPUTED_ELIM_CREDIT = {"Keith Lee", "Braun Strowman", "Kevin Owens"}

CHAMPS_AT_ENTRY = {"Brock Lesnar", "Kofi Kingston", "Big E", "Shinsuke Nakamura", "Keith Lee"}
CHAMP_INFO = {
    # name -> (title, level, won_date, days_into_reign)
    "Brock Lesnar": ("WWE Championship", "World", "2019-10-04", 114),
    "Kofi Kingston": ("SmackDown Tag Team Championship", "Tag Team", "2019-11-08", 79),
    "Big E": ("SmackDown Tag Team Championship", "Tag Team", "2019-11-08", 79),
    "Shinsuke Nakamura": ("Intercontinental Championship", "Intercontinental/United States", "2019-07-14", 196),
    "Keith Lee": ("NXT North American Championship", "NXT secondary", "2020-01-22", 4),
}

SURPRISE_ENTRANTS = {"Robert Roode", "Cesaro", "Shelton Benjamin", "MVP", "Keith Lee", "Matt Riddle", "Luke Gallows", "Edge"}
LEGENDS = {"Edge", "MVP", "Shelton Benjamin"}

# ---------------------------------------------------------------------------
# WRESTLERS -- new to this database this pass (7 of 30). Bios researched
# live and cross-checked against 2 independent sources where possible; WWE
# Hall of Fame and deceased status checked for all 7 as part of this build,
# per Shane's standing process. 5 of these 7 (Roode, Morrison, Ricochet,
# Anderson, Gallows) are established WWE performers who simply had not
# appeared in any Royal Rumble 1988-2019 already built in this database --
# see docstring's "new to database" vs "new to WWE" correction.
# ---------------------------------------------------------------------------
# (ring_name, real_name, real_name_status, gender, dob, dob_status, deceased_date,
#  birthplace, birthplace_status, nationality, debut_year_company, hall_of_fame_year,
#  aliases_ring_names, wrestling_style, notes, source_ids)
new_wrestlers = [
    ("Robert Roode", "Robert Francis Roode Jr.", "PROBABLE", "M", "1976-05-11", "PROBABLE", "", "Peterborough, Ontario, Canada", "PROBABLE", "Canadian", "June 1998, independent circuit (Ontario, as \"Total\" Lee Awesome)", "",
     "Bobby Roode (main pre-2017 and post-Feb-2021 ring name); \"Total\" Lee Awesome (early indie name)", "Technical/tag-team specialist", "Rumble debut in this database, entered #4. Survived 0:41, eliminated by Brock Lesnar. Two-time TNA World Heavyweight Champion and six-time TNA World Tag Team Champion (with James Storm as Beer Money, Inc.) prior to WWE; also a one-time NXT Champion. Billed as 'Robert Roode' on the WWE main roster from Aug 2017 (reverted to 'Bobby Roode' Feb 2021, outside this event's scope). Not a WWE Hall of Famer as of this build (2026-09-21).", "S195"),
    ("John Morrison", "John Randall Hennigan", "CONFIRMED", "M", "1979-10-03", "CONFIRMED", "", "Palos Verdes, California, U.S.", "PROBABLE", "American", "January 27, 2003, Supreme Pro Wrestling / Ohio Valley Wrestling (OVW)", "",
     "Johnny Nitro; Johnny Mundo (Lucha Underground/independent name)", "High-flying, acrobatic -- signature finisher 'Starship Pain'", "Rumble debut in this database, entered #5. Survived 0:09, eliminated by Brock Lesnar. Won WWE Tough Enough III (2003), debuting via OVW/Raw in 2004; multiple-time WWE Intercontinental, United States, and (with The Miz, also an entrant in this match) WWE Tag Team Champion prior to a mid-2010s departure; returned to WWE in 2019 shortly before this event. Not a WWE Hall of Famer as of this build.", "S195;S196"),
    ("Keith Lee", "Keith Gerald Lee II", "CONFIRMED", "M", "1984-11-08", "CONFIRMED", "", "Wichita Falls, Texas, U.S.", "CONFIRMED", "American", "", "",
     "", "Power-agility hybrid -- \"a big man who moves like a cruiserweight\"", "Rumble debut, entered #13, as reigning NXT North American Champion (won 4 days earlier, Jan 22, 2020, from Roderick Strong). Survived 3:32; elimination credit is CONFLICTING -- see F396. Held the WWN Championship (Oct 2017) and PWG World Championship (March 2018) prior to WWE. Exact pro-wrestling debut date not confirmed this pass -- left blank rather than guessed. Not a WWE Hall of Famer as of this build.", "S191"),
    ("Ricochet", "Trevor Mann", "CONFIRMED", "M", "1988-10-11", "CONFIRMED", "", "Alton, Illinois, U.S.", "CONFIRMED", "American", "October 11, 2003, Chaos Pro Wrestling", "",
     "The Future (early indie name); Prince Puma (Lucha Underground)", "High-flying -- innovative acrobatics and mid-air flexibility", "Rumble debut in this database, entered #15. Survived 3:09, eliminated by Drew McIntyre. Extensive pre-WWE resume: multiple Dragon Gate championships (first gaijin Open the Dream Gate Champion), 2014 NJPW Best of the Super Juniors winner, 3x IWGP Junior Heavyweight Tag Team Champion, PWG World Champion, 2x Lucha Underground Champion; later held the WWE NXT North American, United States, and Intercontinental Championships (subsequent to this event). Not a WWE Hall of Famer as of this build.", "S195"),
    ("Karl Anderson", "Chad Allegra", "CONFIRMED", "M", "1980-01-20", "CONFIRMED", "", "Lincoln Park, Michigan, U.S.", "CONFIRMED", "American", "May 10, 2002, Northern Wrestling Federation (NWF)", "",
     "Machine Gun Karl Anderson (NJPW)", "Tag-team specialist -- technical wrestling and hard-hitting offense", "Rumble debut in this database, entered #20. Survived 9:46, eliminated by Randy Orton. Founding member and mouthpiece of the Bullet Club stable; 4x IWGP Tag Team Champion and 2x WWE Raw Tag Team Champion (both alongside Luke Gallows, also an entrant in this match). Not a WWE Hall of Famer as of this build.", "S195"),
    ("Matt Riddle", "Matthew Frederick Riddle", "CONFIRMED", "M", "1986-01-14", "CONFIRMED", "", "Allentown, Pennsylvania, U.S.", "CONFIRMED", "American", "", "",
     "King Woo; The Original Bro", "MMA/BJJ-influenced grappling, barefoot in-ring style", "Rumble debut, entered #23. Survived just 0:41, eliminated by King Corbin -- his first WWE main-roster call-up and first Royal Rumble. NCAA Division II amateur wrestler and BJJ practitioner; former UFC fighter (four-fight win streak before a 2013 release following a marijuana test failure). NXT Tag Team Champion with Pete Dunne (already in this database, RR2019M) as 'The Broserweights,' winning the 2020 Dusty Rhodes Tag Team Classic. Exact pro-wrestling debut date not confirmed this pass -- left blank rather than guessed. Not a WWE Hall of Famer as of this build.", "S191"),
    ("Luke Gallows", "Andrew William Hankinson", "CONFIRMED", "M", "1983-12-22", "CONFIRMED", "", "", "UNKNOWN", "American", "2005, WWE Tough Enough talent competition", "",
     "Festus (early WWE gimmick); Doc Gallows (Impact/NJPW ring name)", "Large, physical big-man style", "Rumble debut in this database, entered #24. Survived 2:00, eliminated by Edge. 3x IWGP Tag Team Champion and 2x WWE Raw Tag Team Champion, both alongside Karl Anderson (also an entrant in this match) as part of The Good Brothers/Bullet Club. Birthplace not specified in sources consulted this pass -- left blank rather than guessed. Not a WWE Hall of Famer as of this build.", "S195"),
]

reused = {
    "Brock Lesnar": "brock-lesnar", "Elias": "elias", "Erick Rowan": "erick-rowan", "Kofi Kingston": "kofi-kingston",
    "Rey Mysterio": "rey-mysterio", "Big E": "big-e", "Cesaro": "cesaro", "Shelton Benjamin": "shelton-benjamin",
    "Shinsuke Nakamura": "shinsuke-nakamura", "MVP": "mvp", "Braun Strowman": "braun-strowman",
    "Drew McIntyre": "drew-mcintyre", "The Miz": "the-miz", "AJ Styles": "aj-styles", "Dolph Ziggler": "dolph-ziggler",
    "Edge": "edge", "King Corbin": "baron-corbin", "Randy Orton": "randy-orton", "Roman Reigns": "roman-reigns",
    "Kevin Owens": "kevin-owens", "Aleister Black": "aleister-black", "Samoa Joe": "samoa-joe",
    "Seth Rollins": "seth-rollins",
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

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Drew McIntyre")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, is_shared, extra_note = ELIMINATORS.get(name, ([], False, ""))

    notes_parts = [extra_note] if extra_note else []
    if name == "Drew McIntyre":
        notes_parts.append("Entered #16 and won, eliminating Roman Reigns with a Claymore Kick after surviving "
                            "34:11 (the match's longest individual time). Earned a WWE Championship match of his "
                            "choosing at WrestleMania 36, which he used to challenge and defeat Brock Lesnar.")

    champ_title, champ_level, champ_date, champ_days = CHAMP_INFO.get(name, ("", "", "UNKNOWN", ""))

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
            "is_storyline_related": "TRUE" if name == "Seth Rollins" else "UNKNOWN",
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "TRUE" if name in DISPUTED_ELIM_CREDIT else "FALSE",
            "simultaneous_group_id": "",
            "data_quality_status": "CONFLICTING" if name in DISPUTED_ELIM_CREDIT else "CONFIRMED",
            "source_ids": "S184;S185;S186",
            "notes": "",
        })

    er = {
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": "CONFIRMED",
        "ring_name_at_time": name, "name_displayed_at_event": name,
        "prior_rumble_appearances_count": "", "rumble_appearance_no": "",
        "is_first_rumble_appearance": "TRUE" if name in NEW_NAMES else "", "is_company_debut": "UNKNOWN",
        "previous_rumble_year": "", "previous_rumble_result": "", "previous_rumble_elimination_no": "",
        "is_rumble_debut": "TRUE" if name in NEW_NAMES else "FALSE",
        "company_debut_date": "",
        "is_returning_wrestler": "TRUE" if name in LEGENDS else "",
        "absence_length": "",
        "age_at_event": "", "age_status": "UNKNOWN",
        "billed_height_m_at_event": "", "billed_weight_kg_at_event": "", "billed_from_at_event": "",
        "physical_status": "UNKNOWN",
        "alignment": "", "alignment_status": "UNKNOWN",
        "gimmick_at_event": "",
        "manager_at_event": "",
        "tag_team_name": "",
        "faction_stable": "",
        "current_champion_title": champ_title,
        "championship_level": champ_level,
        "championship_partner": "",
        "reign_number": "", "title_won_date": champ_date, "days_into_reign_at_event": champ_days,
        "title_defended_same_card": "FALSE", "title_lost_same_card": "FALSE",
        "elim_number": "" if is_winner else elim_number[name],
        "elim_number_status": "N/A" if is_winner else "CONFIRMED",
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
        "surprise_entrant": "TRUE" if name in SURPRISE_ENTRANTS else "FALSE",
        "legend_returning": "TRUE" if name in LEGENDS else "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "TRUE" if name in LEGENDS else "FALSE",
        "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFLICTING" if name in DISPUTED_ELIM_CREDIT else "CONFIRMED",
        "source_ids": "S184;S185;S186",
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
    ("F396", EVENT_ID, "eliminations", "keith-lee;braun-strowman", "eliminator_wrestler_id", "conflicting_sources",
     "Keith Lee's and Braun Strowman's eliminator credit is genuinely CONFLICTING across three different versions: "
     "WWE.com's official recap (via TheSportster.com's paraphrase, S186) describes Brock Lesnar's 'simultaneous "
     "removal' of both -- sole credit to Lesnar. Wikipedia (S184) instead cross-shares credit -- Lee eliminated by "
     "Lesnar AND Strowman; Strowman eliminated by Lesnar AND Lee. Cagematch (S185) gives a 3rd version -- Lee "
     "eliminated by Lesnar (with Strowman); Strowman eliminated by Lesnar alone. This database uses the "
     "official/majority version (Lesnar credited solo on both), which is also the only version arithmetically "
     "consistent with the widely-documented historical fact that Lesnar tied the all-time single-Rumble elimination "
     "record with 13 credited eliminations this match (11 other solo eliminations + these 2 = 13). All three "
     "versions are preserved here for transparency.",
     "S184;S185;S186", "open", "2026-09-21"),
    ("F397", EVENT_ID, "eliminations", "kevin-owens", "eliminator_wrestler_id", "unverified",
     "Kevin Owens's eliminator credit has a documentation nuance: Wikipedia's table credits 'Seth Rollins and Akam "
     "and Rezar' jointly, reflecting real outside interference from the Authors of Pain (a non-competing tag team) "
     "as part of Seth Rollins's 'Monday Night Messiah' heel-authority storyline. Since Akam and Rezar were not "
     "entrants/competitors in this match, this database does not co-credit non-entrants in the structured "
     "eliminator_wrestler_id/assisting_wrestler_ids fields -- Seth Rollins alone is credited, with the interference "
     "documented in the entrant's notes field instead.",
     "S184;S186", "resolved", "2026-09-21"),
    ("F398", EVENT_ID, "events", EVENT_ID, "attendance_official;attendance_reported", "conflicting_sources",
     "Attendance is genuinely CONFLICTING: WWE's officially announced figure is 42,715 (touted as a Minute Maid "
     "Park attendance record, surpassing a 2011 Taylor Swift concert's 42,095). Dave Meltzer (Wrestling Observer "
     "Newsletter) reported the actual attendance was closer to ~36,000, independently corroborated by two separate "
     "secondary citations of Meltzer (WhatCulture.com and 411Mania.com) rather than resting on a single outlet. "
     "Both figures are recorded in the structured fields (attendance_official=42715, attendance_reported=36000) "
     "rather than silently picking one. This is a card-wide dispute -- build_2020_women.py carries an identical "
     "copy of this flag against its own event_id, since both matches shared the same card/venue/night. (This also "
     "resolves an initial discrepancy between this build's two research passes: the Women's-side research agent's "
     "first search attempt had not surfaced this dispute, while the Men's-side agent found and corroborated it; a "
     "definitive follow-up search confirmed the dispute applies card-wide.)",
     "S184;S189;S190", "open", "2026-09-21"),
    ("F399", EVENT_ID, "wrestlers", "robert-roode;john-morrison;keith-lee;ricochet;karl-anderson;matt-riddle;luke-gallows", "hall_of_fame_year", "corrected",
     "Continuing the process established at RR2017M/RR2018M/RR2018W/RR2019M/RR2019W: WWE Hall of Fame status and "
     "deceased status were checked for all 7 wrestlers new to this database this pass, as part of this build. "
     "Result: none of the 7 are WWE Hall of Fame inductees as of today (2026-09-21); none are deceased.",
     "S184;S195", "resolved", "2026-09-21"),
    ("F400", EVENT_ID, "wrestlers", "baron-corbin", "ring_name_at_time", "corrected",
     "King Corbin (this event's entrant #22) is the same underlying wrestler_id as this database's existing "
     "'Baron Corbin' (a RR2019M entrant) -- a post-'King of the Ring 2019' coronation moniker, not a full character "
     "reinvention: he retains the 'Corbin' surname, in-ring persona, and finishing move. Reused as wrestler_id "
     "'baron-corbin' with this entrant row's ring_name_at_time set to 'King Corbin,' matching this database's "
     "existing precedent for minor ring-name additions spanning a single wrestler_id (compare the 'smash'/'Repo "
     "Man' entrant row from the 1990s batches) rather than the full-identity-reinvention splits used elsewhere in "
     "this database (husky-harris/bray-wyatt; diesel/kevin-nash).",
     "S184;S186", "resolved", "2026-09-21"),
    ("F401", EVENT_ID, "wrestlers", "robert-roode;john-morrison;ricochet;karl-anderson;luke-gallows", "notes", "corrected",
     "5 of this pass's 7 new wrestlers (Robert Roode, John Morrison, Ricochet, Karl Anderson, Luke Gallows) were "
     "initially treated by the research agent as 'established WWE names needing no fresh bio' -- but independent "
     "verification against this database's live wrestlers.csv found none of the 5 had appeared as an entrant in "
     "any Royal Rumble 1988-2019 already built here, making each a genuinely new wrestler_id in THIS DATABASE "
     "despite being an established WWE performer generally. Full bios were researched directly for all 5 as part "
     "of this build rather than left blank -- see S195/S196. This corrects the 'new to database' vs. 'new to WWE' "
     "conflation risk flagged as open after the RR2019 build.",
     "S184;S195", "resolved", "2026-09-21"),
    ("F402", EVENT_ID, "entrances;moves", "*", "n/a", "out_of_scope_no_tool",
     "No video tool connected this session. Same as every prior year's equivalent flag.",
     "", "open", "2026-09-21"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# NOTABLE MOMENTS
# ---------------------------------------------------------------------------
nm_rows = [
    {
        "moment_id": "NM078", "event_id": EVENT_ID, "wrestler_ids_involved": "brock-lesnar",
        "category": "record",
        "title": "Brock Lesnar ties the all-time single-Rumble elimination record with 13",
        "description": "Entering at #1, Brock Lesnar eliminated 13 opponents in a row (11 solo, plus Keith Lee and Braun Strowman -- see F396) before being eliminated himself by Drew McIntyre after surviving 26:24 -- tying the all-time record for most eliminations by a single competitor in one Royal Rumble match.",
        "data_quality_status": "CONFIRMED", "source_ids": "S184;S186",
        "notes": "",
    },
    {
        "moment_id": "NM079", "event_id": EVENT_ID, "wrestler_ids_involved": "drew-mcintyre",
        "category": "milestone_first",
        "title": "Drew McIntyre wins his first Royal Rumble",
        "description": "McIntyre entered #16 and won by eliminating Roman Reigns with a Claymore Kick, surviving 34:11 (the match's longest individual time). He earned a WWE Championship match of his choosing at WrestleMania 36, which he used to challenge and defeat Brock Lesnar -- the same wrestler he had just eliminated from this Rumble.",
        "data_quality_status": "CONFIRMED", "source_ids": "S184;S186",
        "notes": "",
    },
    {
        "moment_id": "NM080", "event_id": EVENT_ID, "wrestler_ids_involved": "edge",
        "category": "milestone_first",
        "title": "Edge's surprise in-ring return",
        "description": "Edge, retired since 2011 due to a career-threatening neck injury and a WWE Hall of Famer, made a surprise in-ring comeback entering #21, surviving 23:43 (the match's 2nd-longest individual time) and eliminating AJ Styles, Luke Gallows and Randy Orton before being eliminated by Roman Reigns. Widely described as the show's marquee angle.",
        "data_quality_status": "CONFIRMED", "source_ids": "S184;S186",
        "notes": "",
    },
    {
        "moment_id": "NM081", "event_id": EVENT_ID, "wrestler_ids_involved": "seth-rollins;kevin-owens;aleister-black;samoa-joe",
        "category": "other",
        "title": "Seth Rollins's 'Monday Night Messiah' alliance picks off a brief Owens/Black/Joe trio",
        "description": "Kevin Owens, Aleister Black, and Samoa Joe briefly formed their own in-ring alliance before being picked off consecutively by Seth Rollins, who was backed throughout the match by outside interference from Akam and Rezar (Authors of Pain) as part of his heel-authority 'Monday Night Messiah' storyline. Owens, Black, Joe and Rollins's associates brawled to the back together after Rollins's own elimination.",
        "data_quality_status": "CONFIRMED", "source_ids": "S184",
        "notes": "",
    },
    {
        "moment_id": "NM082", "event_id": EVENT_ID, "wrestler_ids_involved": "brock-lesnar;kofi-kingston;big-e;shinsuke-nakamura;keith-lee",
        "category": "other",
        "title": "Four different championships were represented in the field",
        "description": "This match featured 5 reigning champions across 4 titles: Brock Lesnar (WWE Championship), Kofi Kingston & Big E (SmackDown Tag Team Championship, as a duo), Shinsuke Nakamura (Intercontinental Championship), and Keith Lee (NXT North American Championship, won just 4 days earlier). None of these titles were defended within the match itself.",
        "data_quality_status": "CONFIRMED", "source_ids": "S184;S192;S193;S194",
        "notes": "",
    },
]
with open(os.path.join(DATA_DIR, "notable_moments.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=NOTABLE_MOMENTS_FIELDS)
    for row in nm_rows:
        writer.writerow(row)

flags2 = [
    ("F403", EVENT_ID, "notable_moments", "NM078;NM079;NM080;NM081;NM082", "n/a", "corrected",
     "Added 5 notable_moments.csv rows for this newly-built event: Brock Lesnar's record-tying 13-elimination run, "
     "Drew McIntyre's first Royal Rumble win, Edge's surprise in-ring return, the Rollins/Authors-of-Pain storyline "
     "picking off the Owens/Black/Joe trio, and the four-championship representation in the field.",
     "S184;S186;S192;S193;S194", "resolved", "2026-09-21"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags2)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2020", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2020-01-26",
    "venue": "Minute Maid Park", "city_region": "Houston, Texas", "country": "United States",
    "attendance_official": 42715, "attendance_reported": 36000,
    "entry_interval_seconds": "", "entrant_count": 30,
    "duration_total": "1:00:10", "duration_status": "CONFIRMED",
    "winner_id": "drew-mcintyre", "runner_up_id": "roman-reigns",
    "final_two_ids": "drew-mcintyre;roman-reigns",
    "final_three_ids": "drew-mcintyre;roman-reigns;edge",
    "final_four_ids": "drew-mcintyre;roman-reigns;edge;randy-orton",
    "first_entrant_id": "brock-lesnar", "second_entrant_id": "elias", "final_entrant_id": "seth-rollins",
    "first_elimination_id": "elias", "last_elimination_before_winner_id": "roman-reigns",
    "eliminations_count": 29, "eliminators_count": 7,
    "surprise_entrants_count": len(SURPRISE_ENTRANTS),
    "champions_in_field_count": len(CHAMPS_AT_ENTRY), "hall_of_famers_in_field_count": 0,
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Michael Cole & Corey Graves (confirmed calling this segment); Tom Phillips and Jerry \"The King\" Lawler also credited on the broadcast infobox; Booker T joined later in the show",
    "ring_announcer": "UNKNOWN",
    "referees": "UNKNOWN",
    "special_rules": "Standard Royal Rumble rules. No title was defended within the match itself -- the winner instead earned a world championship match at WrestleMania 36.",
    "title_on_the_line": "FALSE",
    "championship_implications": "The winner earned the right to challenge for the WWE Championship at WrestleMania 36. Drew McIntyre won and chose to challenge Brock Lesnar (whom he had just eliminated from this Rumble), defeating him at WrestleMania 36. Brock Lesnar (WWE Champion), Kofi Kingston & Big E (SmackDown Tag Team Champions), Shinsuke Nakamura (Intercontinental Champion) and Keith Lee (NXT North American Champion) all entered as reigning champions, though none of those titles were defended in this match.",
    "winners_reward": "A WWE Championship match at WrestleMania 36. McIntyre chose to challenge Brock Lesnar and won.",
    "historical_significance": (
        "Drew McIntyre's first Royal Rumble win, entering #16 and eliminating Roman Reigns after surviving 34:11, "
        "the match's longest individual time -- he went on to defeat Brock Lesnar for the WWE Championship at "
        "WrestleMania 36, having just eliminated Lesnar from this very match. Lesnar himself tied the all-time "
        "single-Rumble elimination record with 13 credited eliminations, entering at #1 and dominating the match's "
        "opening stretch (see NM078; his exact credit on 2 of those 13 is disputed between sources -- F396). Edge's "
        "surprise in-ring return, 9 years after a career-threatening neck injury forced his 2011 retirement, was "
        "the show's marquee angle. Seth Rollins, backed by outside interference from the Authors of Pain as part "
        "of his 'Monday Night Messiah' storyline, eliminated a briefly-allied Kevin Owens, Aleister Black and "
        "Samoa Joe trio before being eliminated himself. Five reigning champions across four titles were "
        "represented in the field. Built as a fully separate event/record from RR2020W (the Women's Royal Rumble, "
        "held the same night) per Shane's standing instruction to keep the two matches separate."
    ),
    "notes": (
        "Entry order and eliminator credit CONFIRMED for all 30 entrants via 3-4 independent sources each, cross-"
        "checked by name after a first, internally-inconsistent Wikipedia table extraction was discarded and "
        "re-pulled cleanly. Keith Lee's and Braun Strowman's eliminator credit is CONFLICTING across 3 distinct "
        "source versions (F396); Kevin Owens's Authors-of-Pain interference is documented but not co-credited "
        "(F397); attendance is CONFLICTING (F398, shared card-wide with RR2020W). Global match-clock timing "
        "(elimination_clock_time) left UNKNOWN throughout. WWE Hall of Fame status was checked for all 7 newly-"
        "added wrestlers as part of this build, per Shane's standing process -- none are inducted as of this build "
        "(F399). 5 of those 7 new wrestlers are established WWE performers incorrectly assumed to need no fresh "
        "bio by initial research, corrected during this build (F401)."
    ),
    "data_quality_status": "CONFLICTING", "source_ids": "S184;S185;S186;S187;S188;S189;S190;S191;S192;S193;S194",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2020 Men's build complete: {len(new_wrestlers)} new wrestlers ({len(reused)} reused), "
      f"{len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, {len(sources)} sources logged, "
      f"{len(flags) + len(flags2)} flags, {len(nm_rows)} notable_moments rows.")
