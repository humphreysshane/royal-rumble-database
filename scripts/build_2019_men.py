# -*- coding: utf-8 -*-
"""
Builds all rows for the 2019 Men's Royal Rumble -- schema v2.

Royal Rumble 2019, January 27, 2019, Chase Field, Phoenix, Arizona. This is
the MEN'S match only. The Women's Royal Rumble held the same night is a
fully separate event/record -- see build_2019_women.py -- per Shane's
explicit instruction (2026-09-20): "keep them separate."

NEW PROCESS, continuing from RR2018M/RR2018W: WWE Hall of Fame status (and
deceased status) is checked for every new wrestler as part of building the
event they're first added in. Applied here for all 7 wrestlers new to this
database this pass -- none are HOF-inducted as of today (2026-09-21); all
are alive.

Nia Jax (a Women's-division wrestler, already in this database from
RR2018W) is a genuine entrant in THIS men's match -- a real, storyline-
driven cross-division appearance (she attacked advertised entrant R-Truth
and took his spot). Her Men's-division stat line is built here exactly like
any other entrant's; the division-split architecture (2026-09-20) already
supports one wrestler_id carrying independent stat lines in both divisions
-- see IDEAS.md. This is a genuinely unusual, well-documented case (distinct
from Beth Phoenix's precedent, which was one wrestler competing in *both
Rumbles in different years*; Nia Jax competed in *both Rumbles the same
night*, and also appears as an entrant in build_2019_women.py).

SOURCES CONSULTED THIS PASS (live web research via a dedicated research
agent, cross-validated against each other -- see flags.csv for where they
disagreed). Per the methodology learned on RR2018M/W, no single generic
Wikipedia table-extraction was trusted blind; the entrant/elimination table
below was cross-checked by wrestler NAME (not row position) across 5
independent sources, plus an arithmetic self-consistency check (elimination
order 1-29 used exactly once, no gaps/dupes; credited-elimination tally
reconciles against 29 eliminations + 2 shared-credit spots = 31 credits):
  S161 Wikipedia, 'Royal Rumble (2019)' event article, plus its 'WWE Hall
       of Fame (2026)' master inductee list (HOF cross-check)             tier 10
  S162 WWE.com, official '2019 Men's Royal Rumble Match' statistics page
       and results recap                                                 tier 1
  S163 ProWrestling Fandom, 'Royal Rumble 2019' event page                tier 10
  S164 WrestlingInc.com, 'Seth Rollins Wins WWE Men's Royal Rumble Match,
       Order Of Entrants And Eliminations' article                       tier 9
  S165 AllRumbleStats.com, Men's Royal Rumble 2019 statistics page        tier 12
  S166 Cageside Seats, 'Men's Royal Rumble 2019 Match Time and
       Statistics' + companion 'complete list of survival times' article tier 9
  S167 Fightful.com, 'Royal Rumble 2019 Stats' + 'Mustafa Ali Wasn't
       Originally Supposed To Be Eliminated By Nia Jax' + Andrade
       name-shortening reporting (3 companion articles)                  tier 9
  S168 RingsideNews, attendance-figures article ('How Many Fans Were
       Really At The WWE Royal Rumble') + Bodyslam.net, 'Nia Jax
       Genuinely Injured R-Truth At Royal Rumble'                        tier 12
  S169 Cagematch.net, Curt Hawkins and No Way Jose wrestler profiles      tier 4
  S170 Gerweck.net, Johnny Gargano and Mustafa Ali wrestler profiles      tier 12
  S171 mykhel.com, 'Serial wise entries and eliminations' listicle
       (men's table)                                                     tier 12
  S172 TheSmackDownHotel.com, Pete Dunne wrestler profile (substitute
       source -- Cagematch.net rate-limited/429'd on this one profile)   tier 12

CROSS-VALIDATION RESULTS:
  - Entry order (1-30) and eliminator/order credit: CONFIRMED across all 5
    independently structured sources, cross-checked by name. Arithmetic
    self-consistency check passed (see above).
  - Winner: Seth Rollins (entrant #10), eliminating Braun Strowman for the
    win. NOT to be confused with Royal Rumble 2020 (won by Drew McIntyre).
  - TWO elimination-time discrepancies surfaced, handled differently:
    * Jeff Hardy: genuinely CONFLICTING -- S161/S163 (Wikipedia/Fandom,
      likely sharing a common transcription lineage) both give 7:55, while
      S166's two independent Cageside Seats articles and S165 (AllRumble-
      Stats, an independently-built stats aggregator) both give 7:04. Per
      DEFINITIONS.md's source-tier tie-break, S166's tier (9, contemporary
      publication) outranks S161/S163's tier (10, reference site), so 7:04
      is used in the structured field, but ring_time_status is marked
      CONFLICTING rather than silently certain -- see F379.
    * Dean Ambrose (~12:43) and Rey Mysterio (~12:30): each had ONE outlier
      extraction (14:42 for Ambrose from an initial Wikipedia pull; 4:26 for
      Mysterio from an initial ProWrestling Fandom pull) contradicted by 3
      other independent sources apiece. Treated as extraction artifacts, not
      genuine source disagreements -- the majority-agreed figures are used
      with ring_time_status left CONFIRMED, per the same "resolve, don't
      silently guess" standard applied to the RR2019W Billie Kay/Peyton
      Royce eliminator credit -- see F380.
  - Braun Strowman's total credited-elimination count is genuinely
    CONFLICTING: a literal box-score walk of this table (crediting him on
    BOTH shared-elimination spots, Jeff Hardy and Drew McIntyre, alongside
    his 4 solo eliminations) gives 6; Fightful.com's own published stats
    article states "Strowman had the most eliminations, with 5" -- likely
    reflecting a scoring convention that doesn't credit him on the McIntyre
    spot (where Dolph Ziggler did the actual over-the-rope toss, using
    Strowman's back as a platform). Both figures are preserved -- see F381.
  - Attendance is genuinely CONFLICTING: WWE's official announced figure is
    48,193; Dave Meltzer (Wrestling Observer, cited by RingsideNews)
    reported actual bodies in the building at ~40,000, with paid attendance
    around 32,000, and the venue's configured seating capacity for the show
    was only ~43,000 -- making the announced figure implausible on its
    face. Both figures are recorded -- see F382 (this is a card-wide dispute
    shared with build_2019_women.py, which carries its own copy of this
    flag against its own event_id).
  - CORRECTION to this build's initial working assumption: several
    wrestlers previously assumed to be probable entrants are NOT actually
    in this 30-man match -- they appeared elsewhere on the same card
    instead. See F385. This is caught and corrected before being written to
    entrants.csv, not merged as an error.
  - WWE Hall of Fame status was checked individually for all 7 new
    wrestlers as of today (2026-09-21) -- none are inducted; none are
    deceased. Samoa Joe was separately inducted into the ROH Hall of Fame
    (inaugural class, Jan/Feb 2022) -- a different institution, not
    conflated with WWE HOF status here.

WHAT'S ACTUALLY KNOWN THIS YEAR: entry order and eliminator credit CONFIRMED
for all 30 entrants/29 eliminations (2 of which are shared/2-person credits;
no 3+-person "group" eliminations this year). Event-level facts (date,
venue, commentary, title-implication chain to WrestleMania 35) CONFIRMED via
2+ sources; attendance and 2 individual elimination times are CONFLICTING
(see above/flags.csv). Global match-clock timing (elimination_clock_time)
left UNKNOWN throughout, matching this database's established precedent --
individual ring_time (survival duration) IS populated directly from sources.
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
EVENT_ID = "RR2019M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S161", "Wikipedia (English), 'Royal Rumble (2019)' event article, plus 'WWE Hall of Fame (2026)' master inductee list", "reference_site", "https://en.wikipedia.org/wiki/Royal_Rumble_(2019)", 10, "Wikipedia/reference sites", "2026-09-21",
     "Full entrant/elimination table, event facts, commentary, card, and HOF cross-check. Independently agrees with "
     "S162/S163/S164/S165 on entry order by name -- an internal arithmetic self-consistency check confirms no "
     "duplicate/missing elimination-order numbers 1-29."),
    ("S162", "WWE.com, official '2019 Men's Royal Rumble Match' statistics page and results recap", "official_wwe", "https://www.wwe.com/shows/royalrumble/2019/2019-mens-royal-rumble-match", 1, "WWE / official sources", "2026-09-21",
     "Official per-wrestler eliminated-by/time table and results recap. Agrees with S161 on entry order and "
     "eliminator credit."),
    ("S163", "ProWrestling Fandom, 'Royal Rumble 2019' event page", "reference_site", "https://prowrestling.fandom.com/wiki/Royal_Rumble_2019", 10, "Wikipedia/reference sites", "2026-09-21",
     "Independent (community-wiki) cross-check of entry order and elimination order -- matches S161 on the overall "
     "table; shares S161's outlier 14:42 figure for Dean Ambrose, later corrected against 3 other sources -- see "
     "F380."),
    ("S164", "WrestlingInc.com, 'Seth Rollins Wins WWE Men's Royal Rumble Match, Order Of Entrants And Eliminations' article", "contemporary_publication", "https://www.wrestlinginc.com/news/2019/01/seth-rollins-wins-wwe-men-royal-rumble-match-650323/", 9, "Contemporary wrestling publication", "2026-09-21",
     "Independent, differently-structured (plain sequential recap) cross-check of entry order and elimination "
     "order -- matches S161/S162 exactly."),
    ("S165", "AllRumbleStats.com, Men's Royal Rumble 2019 statistics page", "other_stats_site", "https://allrumblestats.com/events/wwe/royal-rumble/royal-rumble-2019-men/", 12, "Other reputable site", "2026-09-21",
     "Independently-built stats aggregator, used as a 3rd/4th cross-check on elimination order and as one of the "
     "two sources favoring 7:04 over 7:55 for Jeff Hardy's survival time -- see F379."),
    ("S166", "Cageside Seats, 'Men's Royal Rumble 2019 Match Time and Statistics' + companion 'complete list of survival times' article", "contemporary_publication", "https://www.cagesideseats.com/wwe/2019/2/2/18207931/wwe-royal-rumble-2019-mens-match-time-statistics", 9, "Contemporary wrestling publication", "2026-09-21",
     "Independent (not WWE-sourced) stopwatch/tape re-timing, used to stress-test official times. One of the two "
     "sources favoring 7:04 over 7:55 for Jeff Hardy's survival time -- its tier-9 rating wins the source-tier "
     "tie-break against tier-10 Wikipedia/Fandom -- see F379."),
    ("S167", "Fightful.com, 'Royal Rumble 2019 Stats' + 'Mustafa Ali Wasn't Originally Supposed To Be Eliminated By Nia Jax' + Andrade name-shortening reporting (3 companion articles)", "contemporary_publication", "https://www.fightful.com/wrestling/royal-rumble-2019-stats-fightfulcom/", 9, "Contemporary wrestling publication", "2026-09-21",
     "Source of the conflicting 'Strowman had 5 eliminations' claim (see F381), the Mustafa Ali/Nia Jax elimination-"
     "origin story (the spot was originally designed for a different, unnamed wrestler who declined it), and "
     "confirmation that Andrade's ring name was officially shortened from 'Andrade \"Cien\" Almas' on Jan 15 2019, "
     "less than 2 weeks before this event."),
    ("S168", "RingsideNews, 'How Many Fans Were Really At The WWE Royal Rumble' + Bodyslam.net, 'Nia Jax Genuinely Injured R-Truth At Royal Rumble'", "other_stats_site", "https://www.ringsidenews.com/2019/01/28/how-many-fans-were-really-at-the-wwe-royal-rumble/", 12, "Other reputable site", "2026-09-21",
     "Reports Dave Meltzer's ~40,000 actual-attendance / ~32,000-paid estimate against WWE's announced 48,193 -- "
     "see F382 -- and Jerry Lawler's podcast account that Nia Jax legitimately hurt R-Truth (ankle and face) during "
     "the scripted attack that let her take his Rumble slot."),
    ("S169", "Cagematch.net, Curt Hawkins and No Way Jose wrestler profiles", "reference_site", "https://www.cagematch.net/?id=2&nr=2749", 4, "Cagematch", "2026-09-21",
     "2nd independent bio-data cross-check source for Curt Hawkins and No Way Jose, alongside S161 (Wikipedia). "
     "Rate-limited (HTTP 429) on further profile pulls this pass -- see S170/S172 for the substitute sources used "
     "for the other 5 new wrestlers."),
    ("S170", "Gerweck.net, Johnny Gargano and Mustafa Ali wrestler profiles", "other_stats_site", "https://gerweck.net/2016/09/02/johnny-gargano/", 12, "Other reputable site", "2026-09-21",
     "Substitute 2nd bio-data cross-check source for Johnny Gargano and Mustafa Ali, used because Cagematch.net "
     "rate-limited further profile pulls this pass."),
    ("S171", "mykhel.com, 'Serial wise entries and eliminations' listicle (men's table)", "other_stats_site", "https://www.mykhel.com/wwe/serial-wise-entries-eliminations-men-women-s-wwe-royal-rumble-2019-109109.html", 12, "Other reputable site", "2026-09-21",
     "Additional cross-check source for entry order; agrees with the primary sources on the men's table (unlike "
     "its documented unreliability on one Women's Royal Rumble eliminator credit -- see build_2019_women.py's F387)."),
    ("S172", "TheSmackDownHotel.com, Pete Dunne wrestler profile", "other_stats_site", "https://www.thesmackdownhotel.com/wrestlers/pete-dunne", 12, "Other reputable site", "2026-09-21",
     "Substitute 2nd bio-data cross-check source for Pete Dunne, used because Cagematch.net's full profile page "
     "was rate-limited/failed to load this pass. Its 'Birmingham' birthplace claim conflicts with Wikipedia's "
     "'Solihull' -- see F384."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# ENTRY ORDER (CONFIRMED, S161+S162+S163+S164+S165 agree by name)
# ---------------------------------------------------------------------------
all_names = [
    "Elias", "Jeff Jarrett", "Shinsuke Nakamura", "Kurt Angle", "Big E", "Johnny Gargano", "Jinder Mahal",
    "Samoa Joe", "Curt Hawkins", "Seth Rollins", "Titus O'Neil", "Kofi Kingston", "Mustafa Ali", "Dean Ambrose",
    "No Way Jose", "Drew McIntyre", "Xavier Woods", "Pete Dunne", "Andrade", "Apollo Crews", "Aleister Black",
    "Shelton Benjamin", "Baron Corbin", "Jeff Hardy", "Rey Mysterio", "Bobby Lashley", "Braun Strowman",
    "Dolph Ziggler", "Randy Orton", "Nia Jax",
]
assert len(all_names) == 30
ENTRY_NUMBERS = {name: i + 1 for i, name in enumerate(all_names)}
assert ENTRY_NUMBERS["Seth Rollins"] == 10 and ENTRY_NUMBERS["Nia Jax"] == 30

# Individual survival ("ring") times. Jeff Hardy's is CONFLICTING (see
# docstring/F379) -- structured field uses the tier-9-source-favored 7:04.
# Dean Ambrose and Rey Mysterio use the majority-agreed figures (F380).
survival = {
    "Elias": "15:07", "Jeff Jarrett": "1:20", "Shinsuke Nakamura": "17:46", "Kurt Angle": "3:15", "Big E": "6:01",
    "Johnny Gargano": "13:50", "Jinder Mahal": "0:29", "Samoa Joe": "23:43", "Curt Hawkins": "4:09",
    "Seth Rollins": "43:00", "Titus O'Neil": "0:04", "Kofi Kingston": "8:54", "Mustafa Ali": "30:00",
    "Dean Ambrose": "12:43", "No Way Jose": "0:03", "Drew McIntyre": "20:05", "Xavier Woods": "0:03",
    "Pete Dunne": "11:13", "Andrade": "26:30", "Apollo Crews": "5:44", "Aleister Black": "6:09",
    "Shelton Benjamin": "9:19", "Baron Corbin": "7:18", "Jeff Hardy": "7:04", "Rey Mysterio": "12:30",
    "Bobby Lashley": "0:12", "Braun Strowman": "14:36", "Dolph Ziggler": "11:34", "Randy Orton": "5:55",
    "Nia Jax": "3:09",
}
assert set(survival) == set(all_names)
SURVIVAL_TIME_DISPUTED = {"Jeff Hardy"}

# Elimination order (1st-29th).
ELIM_ORDER = [
    "Jeff Jarrett", "Kurt Angle", "Jinder Mahal", "Big E", "Elias", "Titus O'Neil", "Curt Hawkins",
    "Shinsuke Nakamura", "Johnny Gargano", "No Way Jose", "Xavier Woods", "Kofi Kingston", "Dean Ambrose",
    "Samoa Joe", "Apollo Crews", "Aleister Black", "Pete Dunne", "Bobby Lashley", "Baron Corbin",
    "Shelton Benjamin", "Jeff Hardy", "Drew McIntyre", "Mustafa Ali", "Nia Jax", "Rey Mysterio", "Randy Orton",
    "Andrade", "Dolph Ziggler", "Braun Strowman",
]
assert len(ELIM_ORDER) == 29
elim_number = {name: i + 1 for i, name in enumerate(ELIM_ORDER)}

FINAL_TWO = {"Seth Rollins", "Braun Strowman"}
FINAL_THREE = {"Seth Rollins", "Braun Strowman", "Dolph Ziggler"}
FINAL_FOUR = {"Seth Rollins", "Braun Strowman", "Dolph Ziggler", "Andrade"}

# name -> (eliminator names, is_shared, notes)
ELIMINATORS = {
    "Jeff Jarrett": (["Elias"], False, "Surprise legend return -- Jarrett was not a WWE roster member at the time (NWA executive)."),
    "Kurt Angle": (["Shinsuke Nakamura"], False, "Entered as Raw General Manager/authority figure, on his farewell tour ahead of his 2019 in-ring retirement (WrestleMania 35)."),
    "Jinder Mahal": (["Johnny Gargano"], False, ""),
    "Big E": (["Samoa Joe"], False, ""),
    "Elias": (["Seth Rollins"], False, ""),
    "Titus O'Neil": (["Curt Hawkins"], False, ""),
    "Curt Hawkins": (["Samoa Joe"], False, ""),
    "Shinsuke Nakamura": (["Mustafa Ali"], False, "Nakamura won the United States Championship from Rusev on the Kickoff Show hours earlier, entering this Rumble as reigning champion."),
    "Johnny Gargano": (["Dean Ambrose"], False, "Gargano entered as reigning NXT North American Champion, having won the title from Ricochet the night before at NXT TakeOver: Phoenix (Jan 26, 2019)."),
    "No Way Jose": (["Samoa Joe"], False, ""),
    "Xavier Woods": (["Drew McIntyre"], False, ""),
    "Kofi Kingston": (["Drew McIntyre"], False, ""),
    "Dean Ambrose": (["Aleister Black"], False, "One of Ambrose's final Rumble appearances before his WWE departure later in 2019 (he left the company and resurfaced as 'Jon Moxley' elsewhere)."),
    "Samoa Joe": (["Mustafa Ali"], False, ""),
    "Apollo Crews": (["Baron Corbin"], False, ""),
    "Aleister Black": (["Baron Corbin"], False, ""),
    "Pete Dunne": (["Drew McIntyre"], False, "Dunne entered as reigning NXT UK Champion (won May 20, 2017; held continuously through this event, would lose the title to WALTER on April 5, 2019)."),
    "Bobby Lashley": (["Seth Rollins"], False, "Lashley entered as reigning Intercontinental Champion, having won the title on Jan 14, 2019, 13 days before this event."),
    "Baron Corbin": (["Braun Strowman"], False, ""),
    "Shelton Benjamin": (["Braun Strowman"], False, "Surprise returning-veteran appearance."),
    "Jeff Hardy": (["Braun Strowman", "Drew McIntyre"], True, "Shared elimination credit -- S161/S162/S165/S166 all agree both Strowman and McIntyre are credited. Hardy's own survival time is CONFLICTING between sources -- see F379."),
    "Drew McIntyre": (["Dolph Ziggler", "Braun Strowman"], True, "Ziggler threw McIntyre out using Braun Strowman's back as a launching platform; both are jointly credited per S161/S163/S165/S172 -- payoff of the McIntyre/Ziggler feud that split their Raw Tag Team Championship-winning duo in Dec 2018."),
    "Mustafa Ali": (["Nia Jax"], False, "This spot was originally designed for a different, unnamed wrestler who declined it out of discomfort being eliminated by a woman; Ali volunteered as the replacement at Jamie Noble's request, per his own later interview -- not connected to Nia Jax's separate, legitimate injuring of R-Truth in the same match (see notable_moments)."),
    "Nia Jax": (["Rey Mysterio"], False, "Nia Jax (a Women's-division wrestler, already in this database from RR2018W) took R-Truth's advertised #30 slot via a scripted attack that legitimately injured him; she also competed in the Women's Royal Rumble the same night -- see notable_moments and build_2019_women.py."),
    "Rey Mysterio": (["Randy Orton"], False, "By this event Mysterio was again a full-time WWE roster member, having re-signed later in 2018 following his RR2018M surprise return."),
    "Randy Orton": (["Andrade"], False, ""),
    "Andrade": (["Braun Strowman"], False, "WWE officially shortened his ring name from 'Andrade \"Cien\" Almas' to simply 'Andrade' on Jan 15, 2019, less than 2 weeks before this event."),
    "Dolph Ziggler": (["Braun Strowman"], False, ""),
    "Braun Strowman": (["Seth Rollins"], False, "The winning elimination. Strowman's own total credited-elimination count is CONFLICTING between sources -- see F381."),
}
assert set(ELIMINATORS) == set(ELIM_ORDER)

CHAMPS_AT_ENTRY = {"Shinsuke Nakamura", "Bobby Lashley", "Johnny Gargano", "Pete Dunne"}
CHAMP_INFO = {
    # name -> (title, level, won_date, days_into_reign)
    "Shinsuke Nakamura": ("United States Championship", "Intercontinental/United States", "2019-01-27", 0),
    "Bobby Lashley": ("Intercontinental Championship", "Intercontinental/United States", "2019-01-14", 13),
    "Johnny Gargano": ("NXT North American Championship", "NXT secondary", "2019-01-26", 1),
    "Pete Dunne": ("NXT UK Championship", "NXT UK", "2017-05-20", 617),
}

SURPRISE_ENTRANTS = {"Jeff Jarrett", "Johnny Gargano", "Pete Dunne", "Shelton Benjamin", "Nia Jax"}
LEGENDS = {"Jeff Jarrett", "Kurt Angle", "Shelton Benjamin"}

# ---------------------------------------------------------------------------
# WRESTLERS -- new to this database this pass (7 of 30). Bios researched
# live and cross-checked against 2 independent sources where possible; WWE
# Hall of Fame and deceased status checked for all 7 as part of this build,
# per Shane's standing process.
# ---------------------------------------------------------------------------
# (ring_name, real_name, real_name_status, gender, dob, dob_status, deceased_date,
#  birthplace, birthplace_status, nationality, debut_year_company, hall_of_fame_year,
#  aliases_ring_names, wrestling_style, notes, source_ids)
new_wrestlers = [
    ("Curt Hawkins", "Brian Myers", "CONFIRMED", "M", "1985-04-20", "CONFIRMED", "", "Glen Cove, New York, U.S.", "CONFIRMED", "American", "2004, New York Wrestling Connection (NYWC)", "",
     "Brian Myers (current TNA/Impact ring name); Brian Majors", "", "Rumble debut, entered #9. Survived 4:09, eliminating Titus O'Neil before being eliminated by Samoa Joe. Famous for a 269-match on-screen 'losing streak' angle (2017-2018). Not a WWE Hall of Famer as of this build (2026-09-21).", "S161;S169"),
    ("Samoa Joe", "Nuufolau Joel Seanoa", "CONFIRMED", "M", "1979-03-17", "CONFIRMED", "", "Huntington Beach, California, U.S.", "CONFIRMED", "American", "December 1999, UIWA West Coast Dojo", "",
     "", "Hybrid/hard-hitting, MMA-influenced striking and submission style", "Rumble debut, entered #8. Survived 23:43, eliminating 3 (Big E, Curt Hawkins, No Way Jose) before being eliminated by Mustafa Ali. Not inducted into the WWE Hall of Fame as of this build (2026-09-21); separately inducted into the ROH Hall of Fame, inaugural class, Jan/Feb 2022 -- a different institution, not conflated with WWE HOF status here.", "S161;S163"),
    ("Johnny Gargano", "John Anthony Nicholas Gargano", "CONFIRMED", "M", "1987-08-14", "CONFIRMED", "", "Lakewood, Ohio, U.S.", "PROBABLE", "American", "July 8, 2005, Cleveland All-Pro Wrestling (CAPW)", "",
     "Cedrick Von Haussen; Joey Gray", "'Lucharesu' -- a self-described mix of British chain wrestling, lucha libre, and puroresu", "Rumble debut, entered #6 as reigning NXT North American Champion (won from Ricochet the night before, Jan 26 2019, at NXT TakeOver: Phoenix). Survived 13:50, eliminating Jinder Mahal before being eliminated by Dean Ambrose. Birthplace given as Lakewood, OH (Wikipedia) vs. Cleveland, OH (Gerweck.net) -- compatible (Lakewood is an inner-ring Cleveland suburb), not a genuine conflict; see F384. Not a WWE Hall of Famer as of this build.", "S161;S170"),
    ("No Way Jose", "Levis Valenzuela Jr.", "CONFIRMED", "M", "1988-05-30", "CONFIRMED", "", "Durham, North Carolina, U.S.", "CONFIRMED", "American", "May 17, 2013, CWF Mid-Atlantic", "",
     "Manny Garcia; Levy Valenz", "", "Rumble debut, entered #15. Survived just 0:03, eliminated by Samoa Joe. Released by WWE in April 2020; worked the independent circuit and Impact Wrestling afterward. Not a WWE Hall of Famer as of this build.", "S161;S169"),
    ("Pete Dunne", "Peter Thomas England", "CONFIRMED", "M", "1993-11-09", "CONFIRMED", "", "Solihull, West Midlands, England", "CONFLICTING", "English", "2007 (trained from age 12 starting 2006); first match at a Holbrooks Festival event in Coventry", "",
     "Tiger Kid; Pete England; Rayo Americano; Streetfighter Ken; later Butch (2022 WWE rebrand); reverted to Pete Dunne, Jan 2024", "Joint-manipulation/finger-bending, stiff striking, British 'strong style'/submission grappling", "Rumble debut, entered #18 as reigning NXT UK Champion (won May 20 2017 from Tyler Bate; held continuously through this event; lost the title April 5 2019 to WALTER). Survived 11:13, eliminated by Drew McIntyre. Birthplace is CONFLICTING between Wikipedia (Solihull) and TheSmackDownHotel.com (Birmingham) -- two distinct towns in the same metro conurbation, not interchangeable; see F384. Not a WWE Hall of Famer as of this build.", "S161;S172"),
    ("Aleister Black", "Tom Büdgen", "CONFIRMED", "M", "1985-05-19", "CONFIRMED", "", "Amsterdam, Netherlands", "CONFIRMED", "Dutch", "June 18, 2002, independent circuit", "",
     "Tommy End (main pre-WWE independent name); later Malakai Black (2020 WWE rebrand); reverted to Aleister Black in a 2025-2026 WWE stint", "Striking-based (kickboxing, pencak silat, Muay Thai)", "Main-roster debut Oct 2018; Rumble debut, entered #21. Survived 6:09, eliminated by Baron Corbin. As of Sept 2026, also credited as the current PROGRESS Men's World Champion on the independent scene. Not a WWE Hall of Famer as of this build.", "S161;S163"),
    ("Mustafa Ali", "Adeel Alam", "CONFIRMED", "M", "1986-03-28", "CONFIRMED", "", "Bolingbrook, Illinois, U.S.", "CONFIRMED", "American", "February 2, 2003, independent circuit", "",
     "Ali Alto; Prince Ali", "High-flying/lucha-influenced -- signature evolved from an inverted 450 splash to a standard 450 splash", "Rumble debut, entered #13. Survived 30:00, eliminating 2 (Shinsuke Nakamura, Samoa Joe) before being eliminated by Nia Jax, in a spot originally designed for a different, unnamed wrestler who declined it -- Ali volunteered as the replacement, per his own later interview. Worked 4 years as a police officer in a Chicago suburb before joining WWE via the 2016 Cruiserweight Classic. Not a WWE Hall of Famer as of this build; also credited with a 2026 TNA storyline/championship win, indicating continued in-ring activity.", "S161;S170"),
]

reused = {
    "Elias": "elias", "Jeff Jarrett": "jeff-jarrett", "Shinsuke Nakamura": "shinsuke-nakamura",
    "Kurt Angle": "kurt-angle", "Big E": "big-e", "Jinder Mahal": "jinder-mahal", "Seth Rollins": "seth-rollins",
    "Titus O'Neil": "titus-oneil", "Kofi Kingston": "kofi-kingston", "Dean Ambrose": "dean-ambrose",
    "Drew McIntyre": "drew-mcintyre", "Xavier Woods": "xavier-woods", "Andrade": "andrade",
    "Apollo Crews": "apollo-crews", "Shelton Benjamin": "shelton-benjamin", "Baron Corbin": "baron-corbin",
    "Jeff Hardy": "jeff-hardy", "Rey Mysterio": "rey-mysterio", "Bobby Lashley": "bobby-lashley",
    "Braun Strowman": "braun-strowman", "Dolph Ziggler": "dolph-ziggler", "Randy Orton": "randy-orton",
    "Nia Jax": "nia-jax",
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
    is_winner = (name == "Seth Rollins")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, is_shared, extra_note = ELIMINATORS.get(name, ([], False, ""))

    notes_parts = [extra_note] if extra_note else []
    if name == "Seth Rollins":
        notes_parts.append("Entered #10 and won, eliminating Braun Strowman for the winning elimination after "
                            "surviving 43:00 (the match's longest individual time). Earned a Universal Championship "
                            "match against Brock Lesnar at WrestleMania 35, which he won.")

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
            "is_storyline_related": "TRUE" if name == "Nia Jax" else "UNKNOWN",
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE",
            "simultaneous_group_id": "",
            "data_quality_status": "CONFIRMED",
            "source_ids": "S161;S162;S164",
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
        "ring_time_status": "CONFLICTING" if name in SURVIVAL_TIME_DISPUTED else "CONFIRMED",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": "", "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if name == "Braun Strowman" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "TRUE" if name in SURPRISE_ENTRANTS else "FALSE",
        "legend_returning": "TRUE" if name in LEGENDS else "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "TRUE" if name in LEGENDS else "FALSE",
        "wrestled_earlier_on_card": "TRUE" if name == "Shinsuke Nakamura" else "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFLICTING" if name in SURVIVAL_TIME_DISPUTED else "CONFIRMED",
        "source_ids": "S161;S162;S164",
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
    ("F379", EVENT_ID, "entrants", "jeff-hardy", "ring_time", "conflicting_sources",
     "Jeff Hardy's survival time is genuinely CONFLICTING between sources: Wikipedia and ProWrestling Fandom "
     "(S161/S163, both tier-10 reference sites, likely sharing a common transcription lineage) give 7:55; "
     "Cageside Seats' two companion articles and AllRumbleStats.com (S166/S165, tier 9 and 12 respectively, "
     "independently built) both give 7:04. Per DEFINITIONS.md's source-tier tie-break convention, S166's tier (9) "
     "outranks S161/S163's tier (10), so 7:04 is used in the structured ring_time field, but ring_time_status is "
     "marked CONFLICTING rather than silently certain. His eliminator credit (shared, Braun Strowman & Drew "
     "McIntyre) and the elimination's position in the order (21st) are NOT in dispute -- only the exact duration.",
     "S161;S163;S165;S166", "open", "2026-09-21"),
    ("F380", EVENT_ID, "entrants", "dean-ambrose;rey-mysterio", "ring_time", "corrected",
     "Two survival-time figures were resolved as extraction artifacts rather than genuine source disagreements: "
     "Dean Ambrose's initial Wikipedia/Fandom pull returned 14:42, contradicted by 3 other independent sources "
     "(WrestlingInc, Cageside Seats, AllRumbleStats) that all agree on ~12:43 -- 12:43 is used. Rey Mysterio's "
     "initial ProWrestling Fandom pull returned an outlier 4:26, contradicted by Wikipedia, Cageside Seats, and "
     "AllRumbleStats, which all independently agree on ~12:30 -- 12:30 is used. Both entrant rows are left at "
     "ring_time_status=CONFIRMED given the 3-source majority agreement in each case, per the same standard applied "
     "to resolving RR2019W's Billie Kay/Peyton Royce eliminator credit against a single outlier source.",
     "S161;S163;S164;S165;S166", "resolved", "2026-09-21"),
    ("F381", EVENT_ID, "entrants", "braun-strowman", "wrestlers_eliminated_count", "conflicting_sources",
     "Braun Strowman's total credited-elimination count is genuinely CONFLICTING: a literal box-score walk of this "
     "event's table (crediting him on both his 4 solo eliminations -- Shelton Benjamin, Baron Corbin, Andrade, "
     "Dolph Ziggler -- plus the two shared-credit spots, Jeff Hardy and Drew McIntyre) gives 6; Fightful.com's own "
     "published stats article states 'Strowman had the most eliminations, with 5.' This likely reflects a scoring "
     "convention that does not credit him on the McIntyre spot, where Dolph Ziggler performed the actual "
     "over-the-rope toss using Strowman's back as a launching platform. This database's derived stats use the "
     "literal box-score total (6, matching how every other shared-credit spot in this database is counted) rather "
     "than silently adopting Fightful's lower figure; both are preserved here for transparency.",
     "S161;S162;S167", "open", "2026-09-21"),
    ("F382", EVENT_ID, "events", EVENT_ID, "attendance_official;attendance_reported", "conflicting_sources",
     "Attendance is genuinely CONFLICTING: WWE's officially announced figure is 48,193; Dave Meltzer (Wrestling "
     "Observer, reported via RingsideNews) estimated actual bodies in the building at approximately 40,000, with "
     "paid attendance around 32,000, and noted the venue's configured seating capacity for the show was only "
     "~43,000 -- making the announced figure implausible on its face. Both figures are recorded in the structured "
     "fields (attendance_official=48193, attendance_reported=40000) rather than silently picking one. This is a "
     "card-wide dispute -- build_2019_women.py carries an identical copy of this flag against its own event_id, "
     "since both matches shared the same card/venue/night.",
     "S161;S168", "open", "2026-09-21"),
    ("F383", EVENT_ID, "wrestlers", "curt-hawkins;samoa-joe;johnny-gargano;no-way-jose;pete-dunne;aleister-black;mustafa-ali", "hall_of_fame_year", "corrected",
     "Continuing the process established at RR2017M/RR2018M/RR2018W: WWE Hall of Fame status and deceased status "
     "were checked for all 7 wrestlers new to this database this pass, as part of this build. Result: none of the "
     "7 are WWE Hall of Fame inductees as of today (2026-09-21); none are deceased. Samoa Joe was separately "
     "inducted into the ROH Hall of Fame (inaugural class, Jan/Feb 2022) -- a different institution, not conflated "
     "with WWE HOF status on his wrestlers.csv row.",
     "S161;S163", "resolved", "2026-09-21"),
    ("F384", EVENT_ID, "wrestlers", "pete-dunne;johnny-gargano", "birthplace", "conflicting_sources",
     "Two birthplace discrepancies surfaced while researching this pass's new wrestlers: (1) Pete Dunne's "
     "birthplace is given as Solihull, West Midlands, England by Wikipedia (S161) but as Birmingham, West "
     "Midlands, England by TheSmackDownHotel.com (S172) -- two distinct towns in the same metro conurbation, not "
     "interchangeable; recorded as CONFLICTING, using Wikipedia's tier-10 claim (Solihull) in the structured "
     "field. (2) Johnny Gargano's birthplace is given as Lakewood, Ohio by Wikipedia (S161) vs. Cleveland, Ohio by "
     "Gerweck.net (S170) -- these ARE compatible (Lakewood is an inner-ring Cleveland suburb), so this is recorded "
     "as PROBABLE rather than CONFLICTING, using the more precise Wikipedia claim.",
     "S161;S170;S172", "open", "2026-09-21"),
    ("F385", EVENT_ID, "entrants", "*", "n/a", "corrected",
     "Initial research working assumptions incorrectly included several wrestlers as probable entrants in this "
     "30-man match who were NOT actually in it -- they appeared elsewhere on the same card instead: The Miz and "
     "Shane McMahon (SmackDown Tag Team Championship match), AJ Styles (WWE Championship match vs. Daniel Bryan), "
     "Kevin Owens (not on this card), Finn Balor (Universal Championship match vs. Brock Lesnar), Big Show (not on "
     "this card), Bobby Roode and Chad Gable (Kickoff Show tag match only), Mojo Rawley (not on this card). This "
     "was caught and corrected during research verification, before being written to entrants.csv -- none of these "
     "9 names appear in this event's entrant/elimination data.",
     "S161;S164", "resolved", "2026-09-21"),
    ("F386", EVENT_ID, "entrances;moves", "*", "n/a", "out_of_scope_no_tool",
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
        "moment_id": "NM065", "event_id": EVENT_ID, "wrestler_ids_involved": "seth-rollins",
        "category": "milestone_first",
        "title": "Seth Rollins wins the Royal Rumble in his first attempt",
        "description": "Rollins entered #10 and won by eliminating Braun Strowman, surviving 43:00 (the match's longest individual time), earning a Universal Championship match against Brock Lesnar at WrestleMania 35 -- which he won, becoming Universal Champion.",
        "data_quality_status": "CONFIRMED", "source_ids": "S161;S162",
        "notes": "",
    },
    {
        "moment_id": "NM066", "event_id": EVENT_ID, "wrestler_ids_involved": "nia-jax",
        "category": "milestone_first",
        "title": "Nia Jax becomes the first person to compete in both Royal Rumble matches on the same night",
        "description": "Nia Jax, a Women's-division wrestler, attacked advertised #30 entrant R-Truth on the ramp before he could enter and took his spot in the Men's Royal Rumble -- becoming the first person to compete in both the men's and women's Rumble matches on the same card, and the first to score an elimination in both (eliminating Mustafa Ali here; see build_2019_women.py for her women's-match appearance). Per Jerry Lawler's own podcast account, the scripted attack legitimately hurt R-Truth (ankle and face).",
        "data_quality_status": "CONFIRMED", "source_ids": "S161;S168",
        "notes": "Cross-references build_2019_women.py -- Nia Jax's wrestler_id (nia-jax) now carries independent stat lines in both divisions for this single night, exercising the division-split architecture beyond its original Beth Phoenix precedent (which spanned different years, not the same night).",
    },
    {
        "moment_id": "NM067", "event_id": EVENT_ID, "wrestler_ids_involved": "mustafa-ali;nia-jax",
        "category": "other",
        "title": "The Mustafa Ali/Nia Jax elimination spot was originally meant for someone else",
        "description": "Per Mustafa Ali's own later interview, the spot in which Nia Jax eliminated him was originally designed for a different, unnamed wrestler who declined it, uncomfortable being eliminated by a woman. Ali volunteered as the replacement, reportedly at Jamie Noble's request. This is a separate matter from Nia Jax's legitimate injuring of R-Truth earlier in the same match (see NM066) -- Ali later suffered an unrelated concussion at a house show in February 2019, not connected to the Rumble.",
        "data_quality_status": "CONFIRMED", "source_ids": "S167",
        "notes": "",
    },
    {
        "moment_id": "NM068", "event_id": EVENT_ID, "wrestler_ids_involved": "braun-strowman",
        "category": "record",
        "title": "Braun Strowman led all eliminators, with a disputed exact total",
        "description": "Braun Strowman was widely reported as having the most eliminations of the match. A literal box-score walk of the table gives him 6 (4 solo -- Shelton Benjamin, Baron Corbin, Andrade, Dolph Ziggler -- plus shared credits on Jeff Hardy and Drew McIntyre); Fightful.com's own published stats article instead states 5, likely not crediting him on the McIntyre spot. See flags.csv F381.",
        "data_quality_status": "CONFLICTING", "source_ids": "S161;S162;S167",
        "notes": "",
    },
    {
        "moment_id": "NM069", "event_id": EVENT_ID, "wrestler_ids_involved": "shinsuke-nakamura",
        "category": "other",
        "title": "Shinsuke Nakamura won the United States Championship hours before entering the Rumble",
        "description": "Nakamura defeated Rusev to win the United States Championship on the Kickoff Show, then entered the Men's Royal Rumble at #3 as reigning champion -- the only confirmed Rumble entrant who also wrestled earlier on the same card.",
        "data_quality_status": "CONFIRMED", "source_ids": "S161;S167",
        "notes": "",
    },
    {
        "moment_id": "NM070", "event_id": EVENT_ID, "wrestler_ids_involved": "johnny-gargano;pete-dunne",
        "category": "other",
        "title": "Two reigning NXT/NXT UK champions entered as surprise call-ups",
        "description": "Johnny Gargano entered #6 as reigning NXT North American Champion (won from Ricochet the night before at NXT TakeOver: Phoenix); Pete Dunne entered #18 as reigning NXT UK Champion (a reign stretching back to May 2017). Neither title was on the line in this non-title match.",
        "data_quality_status": "CONFIRMED", "source_ids": "S161;S162",
        "notes": "",
    },
    {
        "moment_id": "NM071", "event_id": EVENT_ID, "wrestler_ids_involved": "drew-mcintyre;dolph-ziggler",
        "category": "other",
        "title": "Ziggler/McIntyre Rumble spot paid off their late-2018 tag team split",
        "description": "Drew McIntyre and Dolph Ziggler had been a Raw Tag Team Championship-winning duo (won Sept 3, 2018) who lost the titles Oct 22, 2018 and split in December 2018 after a steel cage match. Ziggler eliminated McIntyre from this Rumble by launching him over Braun Strowman's back, a storyline payoff of that feud -- neither man held a title at the time.",
        "data_quality_status": "CONFIRMED", "source_ids": "S161;S167",
        "notes": "",
    },
]
with open(os.path.join(DATA_DIR, "notable_moments.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=NOTABLE_MOMENTS_FIELDS)
    for row in nm_rows:
        writer.writerow(row)

flags2 = [
    ("F387", EVENT_ID, "notable_moments", "NM065;NM066;NM067;NM068;NM069;NM070;NM071", "n/a", "corrected",
     "Added 7 notable_moments.csv rows for this newly-built event: Seth Rollins's Rumble win in his first attempt, "
     "Nia Jax's historic same-night double-Rumble appearance, the Mustafa Ali/Nia Jax elimination-origin story, "
     "the disputed Braun Strowman elimination count, Shinsuke Nakamura's same-card US Title win, the two NXT/NXT "
     "UK champions entering as surprise call-ups, and the Ziggler/McIntyre Rumble-spot storyline payoff.",
     "S161;S162;S167;S168", "resolved", "2026-09-21"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags2)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2019", "match_name": "Royal Rumble Match",
    "match_type": "Men's", "event_date": "2019-01-27",
    "venue": "Chase Field", "city_region": "Phoenix, Arizona", "country": "United States",
    "attendance_official": 48193, "attendance_reported": 40000,
    "entry_interval_seconds": "", "entrant_count": 30,
    "duration_total": "57:30", "duration_status": "CONFIRMED",
    "winner_id": "seth-rollins", "runner_up_id": "braun-strowman",
    "final_two_ids": "seth-rollins;braun-strowman",
    "final_three_ids": "seth-rollins;braun-strowman;dolph-ziggler",
    "final_four_ids": "seth-rollins;braun-strowman;dolph-ziggler;andrade",
    "first_entrant_id": "elias", "second_entrant_id": "jeff-jarrett", "final_entrant_id": "nia-jax",
    "first_elimination_id": "jeff-jarrett", "last_elimination_before_winner_id": "braun-strowman",
    "eliminations_count": 29, "eliminators_count": 20,
    "surprise_entrants_count": len(SURPRISE_ENTRANTS),
    "champions_in_field_count": len(CHAMPS_AT_ENTRY), "hall_of_famers_in_field_count": 0,
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Michael Cole, Corey Graves, Jerry \"The King\" Lawler, John \"Bradshaw\" Layfield (JBL)",
    "ring_announcer": "Greg Hamilton",
    "referees": "UNKNOWN",
    "special_rules": "Standard Royal Rumble rules. No title was defended within the match itself -- the winner instead earned a world championship match at WrestleMania 35.",
    "title_on_the_line": "FALSE",
    "championship_implications": "The winner earned the right to challenge for a world championship at WrestleMania 35. Seth Rollins won and was announced 2 days later as challenging Brock Lesnar for the Universal Championship, which he won at WrestleMania 35. Shinsuke Nakamura (US Champion), Bobby Lashley (Intercontinental Champion), Johnny Gargano (NXT North American Champion) and Pete Dunne (NXT UK Champion) all entered as reigning champions, though none of those titles were defended in this match.",
    "winners_reward": "A world championship match at WrestleMania 35. Rollins chose to challenge Brock Lesnar for the Universal Championship and won.",
    "historical_significance": (
        "Seth Rollins's Royal Rumble win in his first attempt, entering #10 and eliminating Braun Strowman after "
        "surviving 43:00, the match's longest individual time -- he went on to win the Universal Championship from "
        "Brock Lesnar at WrestleMania 35. This match is also notable for Nia Jax's historic appearance: a "
        "Women's-division wrestler who attacked advertised entrant R-Truth and took his #30 slot, becoming the "
        "first person to compete in (and score an elimination in) both Royal Rumble matches on the same night -- "
        "she also appears in this database's separate RR2019W record for her Women's Royal Rumble appearance the "
        "same evening. Braun Strowman's total credited-elimination count is disputed between a literal box-score "
        "tally (6) and Fightful.com's published figure (5) -- see F381. Two reigning NXT-brand champions, Johnny "
        "Gargano (NXT North American) and Pete Dunne (NXT UK), entered as surprise call-ups, alongside two main-"
        "roster champions, Shinsuke Nakamura (who won the US Championship on the Kickoff Show hours earlier) and "
        "Bobby Lashley (Intercontinental Champion). Drew McIntyre and Dolph Ziggler's elimination spot paid off "
        "their late-2018 Raw Tag Team Championship-winning duo's storyline split. Built as a fully separate event/"
        "record from RR2019W (the Women's Royal Rumble, held the same night) per Shane's explicit instruction to "
        "keep the two matches separate."
    ),
    "notes": (
        "Entry order and eliminator credit CONFIRMED for all 30 entrants via 4-5 independent sources each, cross-"
        "checked by name (not row position) per the methodology established after RR2019 research revealed "
        "automated Wikipedia table extraction can silently reorder rows. Jeff Hardy's survival time is CONFLICTING "
        "(F379); Braun Strowman's total elimination count is CONFLICTING (F381); attendance is CONFLICTING "
        "(F382, shared with RR2019W). Global match-clock timing (elimination_clock_time) left UNKNOWN throughout. "
        "WWE Hall of Fame status was checked for all 7 newly-added wrestlers as part of this build, per Shane's "
        "standing process -- none are inducted as of this build (F383)."
    ),
    "data_quality_status": "CONFLICTING", "source_ids": "S161;S162;S163;S164;S165;S166;S167;S168;S171",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2019 Men's build complete: {len(new_wrestlers)} new wrestlers ({len(reused)} reused), "
      f"{len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, {len(sources)} sources logged, "
      f"{len(flags) + len(flags2)} flags, {len(nm_rows)} notable_moments rows.")
