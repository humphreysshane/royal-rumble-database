# -*- coding: utf-8 -*-
"""
Builds all rows for the 2020 Women's Royal Rumble -- schema v2.

Royal Rumble 2020, January 26, 2020, Minute Maid Park, Houston, Texas. This
is the WOMEN'S match only. The Men's Royal Rumble held the same night is a
fully separate event/record -- see build_2020_men.py -- per Shane's
standing instruction to keep the two matches separate.

NEW PROCESS, continuing from RR2018M/RR2018W/RR2019M/RR2019W/RR2020M: WWE
Hall of Fame status (and deceased status) is checked for every new wrestler
as part of building the event they're first added in. Applied here for all
9 wrestlers new to this database this pass -- none are HOF-inducted as of
today (2026-09-21); all are alive.

Two of these 9 (Bianca Belair, Shayna Baszler) are the SAME "new to database"
vs. "new to WWE" correction applied in build_2020_men.py: the research agent
initially did not flag them as needing bios (both were already NXT-level
performers with prior WWE-adjacent TV exposure), but neither had appeared as
an entrant in any Royal Rumble 1988-2019 already built in this database --
both were independently verified as genuinely new wrestler_ids and given
full bios researched directly for this build. See F409.

"Santina Marella" (entrant #29) is Santino Marella's comedic drag alter-ego
-- reused as this database's existing "santino-marella" wrestler_id, with
ring_name_at_time="Santina Marella", per the same minor-moniker-reuse
convention documented in build_2020_men.py's F400 for King Corbin/Baron
Corbin.

SOURCES CONSULTED THIS PASS (live web research via a dedicated research
agent, cross-validated against each other -- see flags.csv for where they
disagreed -- plus direct follow-up research this build for 2 additional new
wrestlers the agent did not generate fresh bios for). Per the methodology
learned on prior years, the agent's primary entrant/elimination table came
from a verbatim row-by-row Wikipedia pull, cross-checked by wrestler NAME
against 2 other independent sources, plus an arithmetic self-consistency
check (elimination order 1-29 used exactly once, no gaps/dupes; eliminator-
credit tally sums to 30, reconciling exactly with 29 actual eliminations
plus 1 double-count from the single 2-person shared-credit spot):
  S197 Wikipedia (English), 'Royal Rumble (2020)' event article (women's
       section)                                                           tier 10
  S198 Cultaholic.com, order-of-entry/order-of-elimination table          tier 9
  S199 Bleacher Report, event recap (internally self-contradictory on
       Bianca Belair's elimination count in one place -- not adopted
       where it conflicts with the dedicated record-tracking source)      tier 9
  S200 Fightful.com, dedicated elimination-record article (Baszler/Belair
       co-holders of the Women's Royal Rumble elimination record)         tier 9
  S201 Fightful.com, 'Charlotte Flair Wins WWE Women's Royal Rumble
       Match' article                                                     tier 9
  S202 CBS Sports, event recap                                            tier 9
  S203 KB Wrestling Reviews, event review                                 tier 12
  S204 411mania.com, attendance-figures article                          tier 12
  S205 WhatCulture.com, attendance-figure dispute article                 tier 12
  S206 Wrestling-Online.com, attendance/Minute Maid Park record article   tier 12
  S207 Fightful.com, 'Rhea Ripley Defeats Shayna Baszler, Wins NXT
       Women's Championship' article                                      tier 9
  S208 FanBuzz.com, Shayna Baszler's 416-day NXT Women's Championship
       reign-length article                                               tier 12
  S209 Wikipedia (English), 'The Kabuki Warriors' article                 tier 10
  S210 Wikipedia plus secondary bio sites (ringhistory.com,
       thesmackdownhotel.com, IMDb/Geni, thefamousbirthdays.com,
       sescoops.com) -- individual bio pages for all 9 new wrestlers this
       pass, including the 2 (Bianca Belair, Shayna Baszler) researched
       directly this build rather than by the research agent              tier 10/12
  S211 411mania.com, Shayna Baszler's own retrospective account of nearly
       being excluded from this match (single-source, her own account)    tier 12

CROSS-VALIDATION RESULTS:
  - Entry order (1-30) and eliminator credit: CONFIRMED across Wikipedia,
    Cultaholic, and Bleacher Report, cross-checked by name (one trivial
    typo caught -- "Tegan Knox" for Tegan Nox in one source, not adopted).
    Arithmetic self-consistency check passed on the first extraction
    attempt -- no discard/re-pull needed this year, unlike RR2019W.
  - Winner: Charlotte Flair (entrant #17), eliminating Shayna Baszler for
    the win after surviving 27:19 (her personal in-ring clock).
  - Mercedes Martinez is the match's only shared/2-person elimination
    credit (eliminated jointly by Mandy Rose and Sonya Deville) -- CONFIRMED
    across all cross-checked sources, no dispute.
  - Champion-status CORRECTIONS applied during this build (working
    assumptions from before this pass's research, corrected rather than
    assumed): Kairi Sane (not Alexa Bliss/Nikki Cross) was the reigning
    WWE Women's Tag Team Champion at this event, alongside Asuka as The
    Kabuki Warriors (won Oct 6, 2019; Bliss/Cross did not win the titles
    until WrestleMania 36, months later). Toni Storm and Shayna Baszler
    both entered as FORMER, not reigning, champions -- Storm lost the NXT
    UK Women's Championship to Kay Lee Ray on Aug 31, 2019; Baszler lost
    the NXT Women's Championship to Rhea Ripley on Dec 18-19, 2019, both
    well before this Jan 26, 2020 event. See F404.
  - Mia Yim's real surname is genuinely CONFLICTING between sources: two
    sources give "Stephanie Hym Bell," one gives "Stephanie Hym Lee" --
    see F405.
  - Attendance is genuinely CONFLICTING -- a card-wide dispute shared with
    build_2020_men.py's F398. This build's own first research pass had NOT
    surfaced this dispute (unlike the Men's-side pass, which found it
    immediately); a definitive follow-up search this build confirmed the
    dispute is real and applies card-wide -- see F406.
  - Match duration (54:20) appears in only one directly-verified source
    (Wikipedia's infobox) -- flagged as solidly sourced but not
    independently multi-source-confirmed as a standalone figure -- see
    F407.
  - Commentary team is only partially resolved, matching RR2019W's F391
    precedent -- see F408.
  - Two single-source narrative claims (Shayna Baszler's own account of
    nearly being excluded from the match; Beth Phoenix being busted open
    after hitting the ring post) are recorded but flagged as uncorroborated
    -- see F410.
  - Two chronology mix-ups were caught and corrected during research
    verification, not written to the database in error: Chelsea Green's
    fastest-elimination time in THIS match (0:12) is unrelated to a
    separate, later "fastest elimination" record associated with her at
    the 2023 Royal Rumble (a different event, 3 years later); and the
    Shayna Baszler/Becky Lynch rivalry that led to their WrestleMania 36
    match began weeks after this Rumble (Feb 10, 2020, on Raw), not as an
    immediate post-match angle on the night itself. See F411.
  - WWE Hall of Fame status was checked individually for all 9 new
    wrestlers as of today (2026-09-21) -- none are inducted; none are
    deceased.

WHAT'S ACTUALLY KNOWN THIS YEAR: entry order and eliminator credit CONFIRMED
for all 30 entrants/29 eliminations (1 of which is a shared/2-person credit
-- Mercedes Martinez). Event-level facts (date, venue, championship
implications) CONFIRMED via 2+ sources; attendance, match duration, and
commentary team are CONFLICTING/only-partially-resolved (see above/
flags.csv). Global match-clock timing (elimination_clock_time) left UNKNOWN
throughout -- individual ring_time (survival duration) IS populated
directly from sources.
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
EVENT_ID = "RR2020W"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S197", "Wikipedia (English), 'Royal Rumble (2020)' event article (women's section)", "reference_site", "https://en.wikipedia.org/wiki/Royal_Rumble_(2020)", 10, "Wikipedia/reference sites", "2026-09-21",
     "Full entrant/elimination table, event facts, and the Mercedes Martinez shared-elimination credit -- CONFIRMED "
     "on the first extraction attempt, cross-checked against 2 other independent sources."),
    ("S198", "Cultaholic.com, order-of-entry/order-of-elimination table for the men's and women's 2020 Royal Rumble matches", "contemporary_publication", "https://cultaholic.com/posts/order-of-entry-and-elimination-for-mens-and-womens-2020-wwe-royal-rumble-matches", 9, "Contemporary wrestling publication", "2026-09-21",
     "Independent cross-check of entry order and elimination order, matching S197 on all 30 rows except one trivial "
     "typo ('Tegan Knox' for Tegan Nox, not adopted)."),
    ("S199", "Bleacher Report, 'WWE Royal Rumble 2020 Results, Winners, Grades, Reaction and Highlights'", "contemporary_publication", "https://bleacherreport.com/articles/2873207-wwe-royal-rumble-2020-results-winners-grades-reaction-and-highlights", 9, "Contemporary wrestling publication", "2026-09-21",
     "3rd independent cross-check on entry/elimination order. Internally self-contradictory on Bianca Belair's "
     "elimination count in one place (stating both '7' and '6'); discounted as an unreliable secondary detail given "
     "it conflicts with S200's dedicated record-tracking article and with itself -- not adopted."),
    ("S200", "Fightful.com, dedicated article on Shayna Baszler and Bianca Belair co-holding the Women's Royal Rumble elimination record", "contemporary_publication", "https://www.fightful.com/wrestling/shayna-baszler-bianca-belair-are-co-holders-women-s-royal-rumble-record-most-eliminations/", 9, "Contemporary wrestling publication", "2026-09-21",
     "Authoritative source for the tied 8-elimination record (breaking Nia Jax's prior record of 7) -- see NM083."),
    ("S201", "Fightful.com, 'Charlotte Flair Wins WWE Women's Royal Rumble Match'", "contemporary_publication", "https://www.fightful.com/wrestling/charlotte-flair-wins-wwe-women-s-royal-rumble-match/", 9, "Contemporary wrestling publication", "2026-09-21",
     "Cross-check source for the match's winner/runner-up and finish sequence."),
    ("S202", "CBS Sports, Royal Rumble 2020 results/recap live blog", "contemporary_publication", "https://www.cbssports.com/wwe/news/2020-wwe-royal-rumble-results-recap-grades-winners-shocking-return-a-match-lead-epic-show/live", 9, "Contemporary wrestling publication", "2026-09-21",
     "Cross-check source for the match duration and the single-sourced Beth Phoenix busted-open claim -- see F410."),
    ("S203", "KB Wrestling Reviews, event review", "other_stats_site", "https://kbwrestlingreviews.com/2020/01/26/royal-rumble-2020-you-take-the-good-with-the-bad/", 12, "Other reputable site", "2026-09-21",
     "Critical-reception source (graded the match a 'B') and corroboration of the Santina Marella self-elimination "
     "spot."),
    ("S204", "411mania.com, 'Royal Rumble Attendance Lower Than Reported, Interest Down From Last Year'", "other_stats_site", "https://411mania.com/wrestling/royal-rumble-attendance-lower-than-reported-interest-down-from-last-year/", 12, "Other reputable site", "2026-09-21",
     "Cites Dave Meltzer/Wrestling Observer directly: 'The actual number, according to Dave Meltzer, was 36,000' -- "
     "see F406 (card-wide dispute, shared with build_2020_men.py's F398)."),
    ("S205", "WhatCulture.com, 'The Real Attendance Figure For WWE's Royal Rumble 2020 Revealed'", "other_stats_site", "https://whatculture.com/wwe/the-real-attendance-figure-for-wwes-royal-rumble-2020-revealed", 12, "Other reputable site", "2026-09-21",
     "2nd independent citation of Dave Meltzer's ~36,000 estimate, corroborating S204 -- see F406."),
    ("S206", "Wrestling-Online.com, 'Royal Rumble 2020 Attendance Breaks Record For Minute Maid Park'", "other_stats_site", "https://www.wrestling-online.com/wwe/royal-rumble-2020-attendance-breaks-record-for-minute-maid-park/", 12, "Other reputable site", "2026-09-21",
     "Source for the official 42,715 attendance figure and its Minute Maid Park record framing."),
    ("S207", "Fightful.com, 'Rhea Ripley Defeats Shayna Baszler, Wins NXT Women's Championship'", "contemporary_publication", "https://www.fightful.com/wrestling/rhea-ripley-defeats-shayna-baszler-win-nxt-women-s-championship/", 9, "Contemporary wrestling publication", "2026-09-21",
     "Confirms Shayna Baszler lost the NXT Women's Championship to Rhea Ripley on Dec 18-19, 2019 -- establishing "
     "Baszler as a FORMER, not reigning, champion at this Jan 26, 2020 event. See F404."),
    ("S208", "FanBuzz.com, article on Shayna Baszler's 416-day NXT Women's Championship reign length", "other_stats_site", "https://fanbuzz.com/pro-wrestling/wwe/shayna-baszler-nxt-championship-reign/", 12, "Other reputable site", "2026-09-21",
     "Independently corroborates S207's Dec 2019 title-loss date via the reign's reported 416-day length."),
    ("S209", "Wikipedia (English), 'The Kabuki Warriors' article", "reference_site", "https://en.wikipedia.org/wiki/The_Kabuki_Warriors", 10, "Wikipedia/reference sites", "2026-09-21",
     "Confirms Asuka & Kairi Sane won the WWE Women's Tag Team Championship on Oct 6, 2019 (held through April 4, "
     "2020) -- establishing Kairi Sane as the field's one reigning champion-entrant. See F404."),
    ("S210", "Wikipedia plus secondary bio sites (ringhistory.com, thesmackdownhotel.com, IMDb/Geni, thefamousbirthdays.com, sescoops.com) -- individual bio pages for all 9 new wrestlers", "reference_site", "https://en.wikipedia.org/wiki/Bianca_Belair", 10, "Wikipedia/reference sites", "2026-09-21",
     "Bio-data cross-check source for all 9 wrestlers new to this database this pass -- Dakota Kai, Mia Yim, "
     "Chelsea Green, Tegan Nox, Shotzi Blackheart, Mercedes Martinez, and Toni Storm (researched by the agent), "
     "plus Bianca Belair and Shayna Baszler (researched directly this build after being incorrectly treated as "
     "'no fresh bio needed' -- see F409)."),
    ("S211", "411mania.com, article on Shayna Baszler's own retrospective account of nearly being excluded from this match", "other_stats_site", "https://411mania.com/wrestling/shayna-baszler-2020-royal-rumble-nearly-pulled/", 12, "Other reputable site", "2026-09-21",
     "Single-source (her own account, via a later YouTube interview) narrative -- not independently corroborated "
     "by a second party. See F410."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# ENTRY ORDER (CONFIRMED, S197+S198+S199 agree by name)
# ---------------------------------------------------------------------------
all_names = [
    "Alexa Bliss", "Bianca Belair", "Molly Holly", "Nikki Cross", "Lana", "Mercedes Martinez", "Liv Morgan",
    "Mandy Rose", "Candice LeRae", "Sonya Deville", "Kairi Sane", "Mia Yim", "Dana Brooke", "Tamina", "Dakota Kai",
    "Chelsea Green", "Charlotte Flair", "Naomi", "Beth Phoenix", "Toni Storm", "Kelly Kelly", "Sarah Logan",
    "Natalya", "Xia Li", "Zelina Vega", "Shotzi Blackheart", "Carmella", "Tegan Nox", "Santina Marella",
    "Shayna Baszler",
]
assert len(all_names) == 30
ENTRY_NUMBERS = {name: i + 1 for i, name in enumerate(all_names)}
assert ENTRY_NUMBERS["Charlotte Flair"] == 17 and ENTRY_NUMBERS["Shayna Baszler"] == 30

# Individual survival ("ring") times.
survival = {
    "Alexa Bliss": "26:34", "Bianca Belair": "33:20", "Molly Holly": "10:21", "Nikki Cross": "15:08",
    "Lana": "2:29", "Mercedes Martinez": "8:14", "Liv Morgan": "0:44", "Mandy Rose": "8:49",
    "Candice LeRae": "9:01", "Sonya Deville": "5:31", "Kairi Sane": "5:22", "Mia Yim": "6:30",
    "Dana Brooke": "5:26", "Tamina": "0:39", "Dakota Kai": "1:32", "Chelsea Green": "0:12",
    "Charlotte Flair": "27:19", "Naomi": "22:01", "Beth Phoenix": "23:05", "Toni Storm": "18:40",
    "Kelly Kelly": "2:29", "Sarah Logan": "0:28", "Natalya": "14:43", "Xia Li": "10:49", "Zelina Vega": "9:31",
    "Shotzi Blackheart": "7:57", "Carmella": "6:36", "Tegan Nox": "3:50", "Santina Marella": "1:01",
    "Shayna Baszler": "4:27",
}
assert set(survival) == set(all_names)

# Elimination order (1st-29th).
ELIM_ORDER = [
    "Lana", "Liv Morgan", "Molly Holly", "Mercedes Martinez", "Nikki Cross", "Mandy Rose", "Sonya Deville",
    "Candice LeRae", "Kairi Sane", "Tamina", "Mia Yim", "Dakota Kai", "Chelsea Green", "Dana Brooke", "Alexa Bliss",
    "Bianca Belair", "Sarah Logan", "Kelly Kelly", "Santina Marella", "Xia Li", "Tegan Nox", "Zelina Vega",
    "Shotzi Blackheart", "Carmella", "Toni Storm", "Naomi", "Natalya", "Beth Phoenix", "Shayna Baszler",
]
assert len(ELIM_ORDER) == 29
elim_number = {name: i + 1 for i, name in enumerate(ELIM_ORDER)}

FINAL_TWO = {"Charlotte Flair", "Shayna Baszler"}
FINAL_THREE = {"Charlotte Flair", "Shayna Baszler", "Beth Phoenix"}
FINAL_FOUR = {"Charlotte Flair", "Shayna Baszler", "Beth Phoenix", "Natalya"}

# name -> (eliminator names, is_shared, notes)
ELIMINATORS = {
    "Lana": (["Liv Morgan"], False, ""),
    "Liv Morgan": (["Lana"], False, ""),
    "Molly Holly": (["Bianca Belair"], False, "Legend/nostalgia return, billed 'Molly Holly' -- already in this database from RR2018W."),
    "Mercedes Martinez": (["Mandy Rose", "Sonya Deville"], True, "Shared elimination credit -- S197/S198/S199 agree. Mercedes Martinez had only just signed with WWE in January 2020, making this appearance essentially her WWE in-ring debut."),
    "Nikki Cross": (["Bianca Belair"], False, ""),
    "Mandy Rose": (["Bianca Belair"], False, "Earlier in the match, Mandy Rose was saved from apparent elimination by Otis in a storyline spot (the Fire & Desire/Heavy Machinery angle) -- see NM087."),
    "Sonya Deville": (["Bianca Belair"], False, ""),
    "Candice LeRae": (["Bianca Belair"], False, ""),
    "Kairi Sane": (["Alexa Bliss"], False, "Entered as reigning WWE Women's Tag Team Champion alongside Asuka (The Kabuki Warriors, won Oct 6, 2019); Asuka did not enter this match. See F404."),
    "Tamina": (["Bianca Belair"], False, ""),
    "Mia Yim": (["Alexa Bliss"], False, ""),
    "Dakota Kai": (["Chelsea Green"], False, ""),
    "Chelsea Green": (["Alexa Bliss"], False, "Survived only 0:12, one of the shortest individual times in the match -- not to be confused with a separate, later fastest-elimination association at the 2023 Royal Rumble, a different event 3 years after this one. See F411."),
    "Dana Brooke": (["Bianca Belair"], False, ""),
    "Alexa Bliss": (["Bianca Belair"], False, ""),
    "Bianca Belair": (["Charlotte Flair"], False, "Tied the then-record for most eliminations in a single Women's Royal Rumble match, with 8 (alongside Shayna Baszler) -- breaking Nia Jax's previous record of 7. See NM083."),
    "Sarah Logan": (["Charlotte Flair"], False, ""),
    "Kelly Kelly": (["Charlotte Flair"], False, "Legend/part-timer nostalgia return, already in this database."),
    "Santina Marella": (["Santina Marella"], False, "SELF-ELIMINATION. Santino Marella returned in his comedic 'Santina' drag persona and eliminated himself using his own 'Cobra' sock-puppet finishing move. Reused wrestler_id ('santino-marella'), ring_name_at_time='Santina Marella'. See NM085."),
    "Xia Li": (["Shayna Baszler"], False, ""),
    "Tegan Nox": (["Shayna Baszler"], False, ""),
    "Zelina Vega": (["Shayna Baszler"], False, ""),
    "Shotzi Blackheart": (["Shayna Baszler"], False, "Very recent signee -- reported to the WWE Performance Center in November 2019, just over 2 months before this event."),
    "Carmella": (["Shayna Baszler"], False, ""),
    "Toni Storm": (["Shayna Baszler"], False, "Entered as a FORMER (not reigning) NXT UK Women's Champion -- lost the title to Kay Lee Ray on Aug 31, 2019, roughly 5 months before this event. See F404."),
    "Naomi": (["Shayna Baszler"], False, ""),
    "Natalya": (["Beth Phoenix"], False, ""),
    "Beth Phoenix": (["Shayna Baszler"], False, "Legend/Hall-of-Fame one-off return, already in this database. Per a single, uncorroborated source (CBS Sports), Phoenix was busted open after her head struck the ring post during the match. See F410."),
    "Shayna Baszler": (["Charlotte Flair"], False, "The winning elimination. Baszler finished as runner-up, tying Bianca Belair for the match's most credited eliminations (8 apiece) -- see NM083. Entered as a FORMER, not reigning, NXT Women's Champion -- lost the title to Rhea Ripley Dec 18-19, 2019. See F404. Per Baszler's own later retrospective account (a single, uncorroborated source), she was nearly excluded from the match two days beforehand before being reinstated. See F410."),
}
assert set(ELIMINATORS) == set(ELIM_ORDER)

CHAMPS_AT_ENTRY = {"Kairi Sane"}
CHAMP_INFO = {
    # name -> (title, level, won_date, days_into_reign)
    "Kairi Sane": ("WWE Women's Tag Team Championship", "Women's Tag Team", "2019-10-06", 112),
}

SURPRISE_ENTRANTS = {"Molly Holly", "Kelly Kelly", "Beth Phoenix", "Santina Marella"}
NON_FULL_TIME = {"Molly Holly", "Kelly Kelly", "Beth Phoenix", "Santina Marella"}

# ---------------------------------------------------------------------------
# WRESTLERS -- new to this database this pass (9 of 30). Bios researched
# live and cross-checked against 2 independent sources where possible; WWE
# Hall of Fame and deceased status checked for all 9 as part of this build,
# per Shane's standing process. 2 of these 9 (Bianca Belair, Shayna
# Baszler) are established NXT/WWE performers who simply had not appeared
# in any Royal Rumble 1988-2019 already built in this database -- see
# docstring's "new to database" vs "new to WWE" correction.
# ---------------------------------------------------------------------------
# (ring_name, real_name, real_name_status, gender, dob, dob_status, deceased_date,
#  birthplace, birthplace_status, nationality, debut_year_company, hall_of_fame_year,
#  aliases_ring_names, wrestling_style, notes, source_ids)
new_wrestlers = [
    ("Bianca Belair", "Bianca Nicole Crawford (nee Blair)", "CONFIRMED", "F", "1989-04-09", "CONFIRMED", "", "Knoxville, Tennessee, U.S.", "CONFIRMED", "American", "September 29, 2016, WWE NXT", "",
     "", "Powerhouse style, noted for exceptional strength", "Rumble debut in this database, entered #2. Survived 33:20, tying the then-record for most eliminations in a single Women's Royal Rumble match with 8 (alongside Shayna Baszler), breaking Nia Jax's previous record of 7 -- before being eliminated by Charlotte Flair. Former track-and-field athlete (hurdles) at the University of South Carolina, Texas A&M, and the University of Tennessee (All-SEC, All-American); also competed in CrossFit and powerlifting before her 2016 wrestling signing. Had not yet made her main-roster debut at the time of this event (that came April 5, 2020, at WrestleMania 36); competed as an NXT talent here. Not a WWE Hall of Famer as of this build (2026-09-21).", "S210"),
    ("Mercedes Martinez", "Jazmin Benitez", "CONFIRMED", "F", "1980-11-17", "CONFIRMED", "", "Waterbury, Connecticut, U.S.", "CONFIRMED", "American", "November 2000, independent circuit", "",
     "", "Hard-hitting technical, mixed-martial-arts-influenced", "Rumble debut, entered #6. Survived 8:14, part of a shared elimination credit alongside Sonya Deville and Mandy Rose's joint elimination of her. Nearly two-decade independent veteran; 3x WSU Champion, 2x Shimmer Champion, 1x Shine Champion, multiple WXW Women's Championship reigns; mainstay of Ring of Honor's women's division. Signed her WWE contract in January 2020, reporting to the Performance Center right around this event -- making this appearance essentially her WWE in-ring debut. Not a WWE Hall of Famer as of this build.", "S210"),
    ("Dakota Kai", "Cheree Georgina Crowley", "CONFIRMED", "F", "1988-05-06", "CONFIRMED", "", "Auckland, New Zealand", "CONFIRMED", "New Zealander", "2007, New Zealand independent circuit (as 'Evie')", "",
     "Evie", "Hard-hitting technical/striking hybrid", "Rumble debut, entered #15. Survived 1:32, eliminated by Chelsea Green. First woman to receive a contract with Pro Wrestling Zero1 (Japan, 2014); won the inaugural IPW New Zealand Women's Championship (2012) and the Artist of Stardom Championship in Stardom (2015); signed with WWE Dec 2016, competed in the 2017 Mae Young Classic; had already appeared on WWE main-roster TV in the Nov 2019 Survivor Series invasion angle prior to this, her first Royal Rumble. Not a WWE Hall of Famer as of this build.", "S210"),
    ("Chelsea Green", "Chelsea Anne Green", "CONFIRMED", "F", "1991-04-04", "CONFIRMED", "", "Victoria, British Columbia, Canada", "CONFIRMED", "Canadian", "2014, ECCW (Elite Canadian Championship Wrestling)", "",
     "Laurel Van Ness (Impact/TNA ring name); Reklusa (Lucha Underground)", "High-energy/character-driven, athletic offense; trained by Lance Storm", "Rumble debut, entered #16. Survived just 0:12, eliminated by Alexa Bliss -- among the shortest individual times in the match, not to be confused with a separate 2023 Royal Rumble fastest-elimination association (F411). As 'Laurel Van Ness' in Impact/TNA, won the Impact Knockouts Championship (Nov 2017); worked Lucha Underground as 'Reklusa' (2018); signed with WWE Aug 3, 2018, NXT debut Oct 26, 2018. Not a WWE Hall of Famer as of this build.", "S210"),
    ("Toni Storm", "Toni Rossall", "CONFIRMED", "F", "1995-10-19", "CONFIRMED", "", "Auckland, New Zealand", "CONFIRMED", "New Zealand-born, Australia-billed", "2009 (age 13), Australian/New Zealand independent circuit", "",
     "", "All-around technical/power hybrid", "Rumble debut, entered #20. Survived 18:40, eliminated by Shayna Baszler. Won the inaugural Progress Women's Championship (2017) and wXw Women's Championship (twice); in Japan's Stardom, held the SWA World Championship for a record-setting 612 days and the World of Stardom Championship (258-day reign ending June 2018); won the 2018 WWE Mae Young Classic, defeating Io Shirai (already in this database, RR2019W) in the final. Entered this match as a FORMER, not reigning, NXT UK Women's Champion -- her reign ran Jan 12, 2019 to Aug 31, 2019 (lost to Kay Lee Ray), roughly 5 months before this event. See F404. Not a WWE Hall of Famer as of this build.", "S210"),
    ("Kelly Kelly", "Barbara Jean Blank", "PROBABLE", "F", "1987-01-15", "PROBABLE", "", "Jacksonville, Florida, U.S.", "PROBABLE", "American", "", "",
     "Kelly", "", "PLACEHOLDER -- see note: this row is superseded, Kelly Kelly already exists in this database (wrestler_id 'kelly-kelly') and is REUSED, not newly added. Left unused; see reused dict.", "S210"),
]
# NOTE: the placeholder "Kelly Kelly" tuple above is intentionally never
# written -- Kelly Kelly is an existing wrestler_id (see reused dict below)
# and must not be re-added. It is left in source only as a guard-comment
# reminder and is excluded from new_wrestlers immediately below.
new_wrestlers = [w for w in new_wrestlers if w[0] != "Kelly Kelly"]
new_wrestlers += [
    ("Mia Yim", "Stephanie Hym Bell", "CONFLICTING", "F", "1989-04-16", "CONFIRMED", "", "Los Angeles, California, U.S.", "CONFIRMED", "American", "", "",
     "Jade (TNA/Impact ring name)", "All-around/striking, cross-trained in lucha libre", "Rumble debut, entered #12. Survived 6:30, eliminated by Alexa Bliss. Won the inaugural Shine Championship and Shine Tag Titles (2014); as 'Jade' in TNA/Impact, won the TNA Knockouts Championship (April 2016) as part of The Dollhouse; signed with WWE after the Mae Young Classic, NXT debut Oct 2018. Real surname is CONFLICTING between sources -- 'Bell' (2 sources) vs. 'Lee' (1 source), both agree on 'Hym' as a middle name -- see F405. Not a WWE Hall of Famer as of this build.", "S210"),
    ("Tegan Nox", "Steffanie Newell", "PROBABLE", "F", "1994-11-15", "PROBABLE", "", "Bargoed, Wales", "PROBABLE", "Welsh", "2014, Attack! Pro Wrestling", "",
     "Nixon Newell", "High-flying; finisher is a step-up knee strike/shining wizard", "Rumble debut, entered #28. Survived 3:50, eliminated by Shayna Baszler. Formed 'Bayside High' tag team with Mark Andrews (Attack! Tag Champions, 2016); signed with WWE for the 2017 Mae Young Classic but tore her ACL beforehand; returned to NXT April 2018, then suffered a severe multi-ligament knee injury in the 2018 Mae Young Classic quarterfinal vs. Rhea Ripley (already in this database, RR2019W). Not a WWE Hall of Famer as of this build.", "S210"),
    ("Shotzi Blackheart", "Ashley Louise Urbanski", "CONFIRMED", "F", "1992-03-14", "CONFIRMED", "", "Santa Clara County, California, U.S.", "CONFIRMED", "American", "2014, Hoodslam (Oakland, CA)", "",
     "Missy Highasshit (early Hoodslam character)", "High-risk/hardcore-adjacent, 'tank girl' alternative persona", "Rumble debut, entered #26. Survived 7:57, eliminated by Shayna Baszler. Won the Shine Nova Championship (May 2019); offered an NXT contract by William Regal at Evolve 137 (Oct 11, 2019), signed that month, reported to the WWE Performance Center in November 2019 -- meaning she was a very recent signee at the time of this Rumble. Of Filipino descent. Not a WWE Hall of Famer as of this build.", "S210"),
    ("Shayna Baszler", "Shayna Andrea Baszler", "CONFIRMED", "F", "1980-08-08", "CONFIRMED", "", "Sioux Falls, South Dakota, U.S.", "CONFIRMED", "American", "September 26, 2015, Quintessential Pro Wrestling (Reno, NV)", "",
     "The Queen of Spades", "Technical submission specialist -- catch wrestling and Brazilian jiu-jitsu", "Rumble debut in this database, entered #30, finishing as runner-up (eliminated by Charlotte Flair for the winning elimination) after tying Bianca Belair for the match's most credited eliminations (8 apiece) -- see NM083. Two-time NXT Women's Champion (2018-2019) prior to this event, but had lost the title to Rhea Ripley on Dec 18-19, 2019 (a 416-day reign), roughly 5 weeks before this Rumble -- entering as a FORMER, not reigning, champion. See F404. Pre-wrestling MMA career 2003-2017 (15-11 professional record; competed in UFC, Invicta FC, Strikeforce, and EliteXC) before transitioning to pro wrestling in 2015; signed with WWE/NXT Oct 3, 2017 after the Mae Young Classic. Per her own later retrospective account (a single, uncorroborated source), she was nearly excluded from this match two days beforehand before being reinstated. See F410. Not a WWE Hall of Famer as of this build.", "S210;S211"),
]
assert len(new_wrestlers) == 9

reused = {
    "Alexa Bliss": "alexa-bliss", "Nikki Cross": "nikki-cross", "Molly Holly": "molly-holly", "Lana": "lana",
    "Liv Morgan": "liv-morgan", "Mandy Rose": "mandy-rose", "Candice LeRae": "candice-lerae",
    "Sonya Deville": "sonya-deville", "Kairi Sane": "kairi-sane", "Dana Brooke": "dana-brooke", "Tamina": "tamina",
    "Charlotte Flair": "charlotte-flair", "Naomi": "naomi", "Beth Phoenix": "beth-phoenix",
    "Kelly Kelly": "kelly-kelly", "Sarah Logan": "sarah-logan", "Natalya": "natalya", "Xia Li": "xia-li",
    "Zelina Vega": "zelina-vega", "Carmella": "carmella", "Santina Marella": "santino-marella",
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
    is_winner = (name == "Charlotte Flair")
    is_self_elim = (name == "Santina Marella")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, is_shared, extra_note = ELIMINATORS.get(name, ([], False, ""))

    notes_parts = [extra_note] if extra_note else []
    if name == "Charlotte Flair":
        notes_parts.append("Entered #17 and won, eliminating Shayna Baszler for the winning elimination after "
                            "surviving 27:19 (her personal in-ring clock). Cut a post-match victory promo described "
                            "by recaps as tonally ambiguous, neither clearly face nor heel.")

    champ_title, champ_level, champ_date, champ_days = CHAMP_INFO.get(name, ("", "", "UNKNOWN", ""))

    for eliminator in elim_by:
        elim_rows.append({
            "event_id": EVENT_ID, "order_in_match": elim_number[name],
            "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
            "assisting_wrestler_ids": ";".join(wrestler_ids[e] for e in elim_by if e != eliminator) if is_shared else "",
            "entry_number_of_eliminated": entry, "entry_number_of_eliminator": ENTRY_NUMBERS.get(eliminator, ""),
            "elimination_clock_time": "", "elimination_clock_seconds": "",
            "elimination_type": "self_elimination" if is_self_elim else "over_top_rope",
            "elimination_method": "",
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "FALSE" if (is_shared or is_self_elim) else "TRUE", "is_shared": "TRUE" if is_shared else "FALSE",
            "is_accidental": "FALSE",
            "is_self_elimination": "TRUE" if is_self_elim else "FALSE",
            "is_storyline_related": "TRUE" if name in ("Mandy Rose", "Santina Marella") else "UNKNOWN",
            "was_already_incapacitated": "UNKNOWN",
            "is_disputed": "FALSE",
            "simultaneous_group_id": "",
            "data_quality_status": "CONFIRMED",
            "source_ids": "S197;S198;S199",
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
        "is_returning_wrestler": "TRUE" if name in NON_FULL_TIME else "",
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
        "self_eliminated": "TRUE" if is_self_elim else "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if name == "Shayna Baszler" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "TRUE" if name in SURPRISE_ENTRANTS else "FALSE",
        "legend_returning": "TRUE" if name in NON_FULL_TIME else "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "TRUE" if name in NON_FULL_TIME else "FALSE",
        "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S197;S198;S199",
        "notes": " ".join(notes_parts),
    }
    entrant_rows.append(er)

# Fill in each eliminator's wrestlers_eliminated_ids / counts from elim_rows.
# (Santina Marella's self-elimination row has eliminator == eliminated, so it
# is deliberately excluded from elim_credit -- a self-elimination is not
# counted as a credited elimination of anyone else.)
elim_credit = {}
for row in elim_rows:
    if row["eliminator_wrestler_id"] == row["eliminated_wrestler_id"]:
        continue
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
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F404", EVENT_ID, "entrants", "kairi-sane;toni-storm;shayna-baszler", "current_champion_title", "corrected",
     "Champion-status CORRECTIONS applied during this build: Kairi Sane (not Alexa Bliss/Nikki Cross) was the "
     "reigning WWE Women's Tag Team Champion at this event, alongside Asuka as The Kabuki Warriors (won Oct 6, "
     "2019; Bliss/Cross did not win the titles until WrestleMania 36, months later -- an initial working assumption "
     "corrected before any data was written). Toni Storm entered as a FORMER NXT UK Women's Champion (lost to Kay "
     "Lee Ray Aug 31, 2019). Shayna Baszler entered as a FORMER NXT Women's Champion (lost to Rhea Ripley Dec "
     "18-19, 2019, a 416-day reign). Neither Storm nor Baszler is recorded with a current_champion_title on their "
     "entrant rows, matching their correct former-champion status.",
     "S209;S207;S208", "resolved", "2026-09-21"),
    ("F405", EVENT_ID, "wrestlers", "mia-yim", "real_name", "conflicting_sources",
     "Mia Yim's real surname is genuinely CONFLICTING between sources: two sources give 'Stephanie Hym Bell' "
     "(Wikipedia, thefamousbirthdays.com) while one gives 'Stephanie Hym Lee' (ringhistory.com). All sources agree "
     "on 'Hym' as a middle name. The majority-sourced 'Bell' is used in the structured real_name field, with "
     "real_name_status marked CONFLICTING rather than silently certain.",
     "S210", "open", "2026-09-21"),
    ("F406", EVENT_ID, "events", EVENT_ID, "attendance_official;attendance_reported", "conflicting_sources",
     "Attendance is genuinely CONFLICTING -- a card-wide dispute shared with build_2020_men.py's F398, since both "
     "matches shared the same card/venue/night. WWE's officially announced figure is 42,715; Dave Meltzer "
     "(Wrestling Observer) reported the actual attendance was closer to ~36,000, independently corroborated by two "
     "separate secondary citations (411mania.com and WhatCulture.com). This build's own first research pass had "
     "not surfaced this dispute; a definitive follow-up search confirmed it is real and applies card-wide, "
     "reconciling the discrepancy against build_2020_men.py's independently-sourced finding.",
     "S204;S205;S206", "open", "2026-09-21"),
    ("F407", EVENT_ID, "events", EVENT_ID, "duration_total", "unverified",
     "Match duration (54:20, per Wikipedia's infobox) appears in only one directly-verified source this pass -- "
     "individual survival times were well corroborated across sources, but this single bell-to-bell total figure "
     "was not independently found in a second source. Recorded as solidly sourced but not multi-source-confirmed "
     "as a standalone figure, pending a future corroborating source.",
     "S197", "open", "2026-09-21"),
    ("F408", EVENT_ID, "events", EVENT_ID, "commentary_team", "unverified",
     "Commentary team is only partially resolved, matching RR2019W's F391 precedent. The 4-person broadcast-wide "
     "roster (Michael Cole, Corey Graves, Tom Phillips, Jerry Lawler, with Booker T joining later) is solidly "
     "confirmed for the overall show, but a dedicated source assigning which pairing specifically called the "
     "Women's Royal Rumble segment (as opposed to other matches on the card) was not found this pass -- flagged as "
     "needing a video-based or segment-specific confirmation before treating any single pairing as final for this "
     "match.",
     "S197", "open", "2026-09-21"),
    ("F409", EVENT_ID, "wrestlers", "bianca-belair;shayna-baszler", "notes", "corrected",
     "2 of this pass's 9 new wrestlers (Bianca Belair, Shayna Baszler) were initially treated by the research agent "
     "as established performers not needing bios, since both had prior NXT/WWE-adjacent TV exposure -- but "
     "independent verification against this database's live wrestlers.csv found neither had appeared as an "
     "entrant in any Royal Rumble 1988-2019 already built here, making each a genuinely new wrestler_id in THIS "
     "DATABASE. Full bios were researched directly for both as part of this build rather than left blank -- see "
     "S210. This is the same 'new to database' vs. 'new to WWE' correction applied in build_2020_men.py's F401.",
     "S197;S210", "resolved", "2026-09-21"),
    ("F410", EVENT_ID, "entrants", "shayna-baszler;beth-phoenix", "notes", "unverified",
     "Two single-source narrative claims are recorded but flagged as uncorroborated: (1) Per Shayna Baszler's own "
     "later retrospective account (a YouTube interview, cited via 411mania.com), Paul Heyman called her two days "
     "before the show to tell her she would not be in the Rumble, and she was reinstated only after an NXT "
     "rehearsal that Saturday, reportedly after Triple H advocated for her -- her own account, not independently "
     "corroborated by a second party. (2) Per CBS Sports, Beth Phoenix bled after her head 'bounced off the top of "
     "the ring post' during the match -- also not independently corroborated elsewhere this pass. Both are "
     "preserved in entrant notes rather than treated as fully CONFIRMED.",
     "S202;S211", "open", "2026-09-21"),
    ("F411", EVENT_ID, "entrants", "chelsea-green;shayna-baszler", "notes", "corrected",
     "Two chronology mix-ups were caught and corrected during research verification, not written to the database "
     "in error: (1) Chelsea Green's 0:12 survival time in THIS match is unrelated to a separate, later "
     "fastest-elimination association tied to her at the 2023 Royal Rumble (a different event 3 years after this "
     "one, eliminated in 5 seconds by Rhea Ripley) -- search results for 'Chelsea Green fastest elimination' "
     "conflate the two events, and only the 2020 figure (0:12) belongs on this event's row. (2) The Shayna "
     "Baszler/Becky Lynch rivalry that led to their WrestleMania 36 match began weeks after this Rumble -- Baszler "
     "attacked Raw Women's Champion Becky Lynch on the February 10, 2020 episode of Raw -- not as an immediate "
     "post-match angle on the night of this event itself, and no such angle is recorded on this event's row.",
     "S197", "resolved", "2026-09-21"),
    ("F412", EVENT_ID, "entrances;moves", "*", "n/a", "out_of_scope_no_tool",
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
        "moment_id": "NM083", "event_id": EVENT_ID, "wrestler_ids_involved": "shayna-baszler;bianca-belair",
        "category": "record",
        "title": "Shayna Baszler and Bianca Belair tie for the most eliminations in Women's Royal Rumble history",
        "description": "Both Shayna Baszler (entrant #30, runner-up) and Bianca Belair (entrant #2) recorded 8 credited eliminations apiece, tying for the most eliminations by a single competitor in Women's Royal Rumble history and breaking the prior record of 7, held by Nia Jax (RR2018W).",
        "data_quality_status": "CONFIRMED", "source_ids": "S200;S197",
        "notes": "",
    },
    {
        "moment_id": "NM084", "event_id": EVENT_ID, "wrestler_ids_involved": "charlotte-flair",
        "category": "milestone_first",
        "title": "Charlotte Flair wins her first Royal Rumble",
        "description": "Charlotte Flair entered #17 and won by eliminating Shayna Baszler after surviving 27:19, becoming the first Royal Rumble winner in this database's separate RR2020W record. Her post-match promo was described by contemporary recaps as tonally ambiguous, neither clearly face nor heel.",
        "data_quality_status": "CONFIRMED", "source_ids": "S197;S201",
        "notes": "",
    },
    {
        "moment_id": "NM085", "event_id": EVENT_ID, "wrestler_ids_involved": "santino-marella",
        "category": "other",
        "title": "Santino Marella returns as 'Santina' for a comedic self-elimination",
        "description": "Santino Marella returned in his 'Santina' drag persona at #29 and eliminated himself using his own 'Cobra' sock-puppet finishing move on himself -- confirmed by 2+ independent sources.",
        "data_quality_status": "CONFIRMED", "source_ids": "S198;S203;S202",
        "notes": "",
    },
    {
        "moment_id": "NM086", "event_id": EVENT_ID, "wrestler_ids_involved": "kairi-sane",
        "category": "other",
        "title": "Kairi Sane entered as a reigning champion, correcting an initial working assumption",
        "description": "Kairi Sane entered #11 as reigning WWE Women's Tag Team Champion alongside Asuka (The Kabuki Warriors, won Oct 6, 2019) -- not Alexa Bliss and Nikki Cross, who did not win the titles until WrestleMania 36 months later, an assumption corrected during this build's research. See F404.",
        "data_quality_status": "CONFIRMED", "source_ids": "S209",
        "notes": "",
    },
    {
        "moment_id": "NM087", "event_id": EVENT_ID, "wrestler_ids_involved": "mandy-rose",
        "category": "other",
        "title": "Otis 'saves' Mandy Rose in a storyline interference spot",
        "description": "Earlier in the match, Mandy Rose was saved from apparent elimination by Otis in a storyline spot connected to the Fire & Desire/Heavy Machinery angle -- praised across multiple contemporary recaps as a standout moment.",
        "data_quality_status": "CONFIRMED", "source_ids": "S202;S203",
        "notes": "",
    },
]
with open(os.path.join(DATA_DIR, "notable_moments.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=NOTABLE_MOMENTS_FIELDS)
    for row in nm_rows:
        writer.writerow(row)

flags2 = [
    ("F413", EVENT_ID, "notable_moments", "NM083;NM084;NM085;NM086;NM087", "n/a", "corrected",
     "Added 5 notable_moments.csv rows for this newly-built event: the tied 8-elimination record between Shayna "
     "Baszler and Bianca Belair, Charlotte Flair's first Royal Rumble win, Santino Marella's comedic 'Santina' "
     "self-elimination, Kairi Sane's corrected champion-status entry, and the Otis/Mandy Rose storyline spot.",
     "S200;S197;S198;S209;S202", "resolved", "2026-09-21"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags2)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2020", "match_name": "Royal Rumble Match",
    "match_type": "Women's", "event_date": "2020-01-26",
    "venue": "Minute Maid Park", "city_region": "Houston, Texas", "country": "United States",
    "attendance_official": 42715, "attendance_reported": 36000,
    "entry_interval_seconds": "", "entrant_count": 30,
    "duration_total": "54:20", "duration_status": "PROBABLE",
    "winner_id": "charlotte-flair", "runner_up_id": "shayna-baszler",
    "final_two_ids": "charlotte-flair;shayna-baszler",
    "final_three_ids": "charlotte-flair;shayna-baszler;beth-phoenix",
    "final_four_ids": "charlotte-flair;shayna-baszler;beth-phoenix;natalya",
    "first_entrant_id": "alexa-bliss", "second_entrant_id": "bianca-belair", "final_entrant_id": "shayna-baszler",
    "first_elimination_id": "lana", "last_elimination_before_winner_id": "shayna-baszler",
    "eliminations_count": 29, "eliminators_count": 9,
    "surprise_entrants_count": len(SURPRISE_ENTRANTS),
    "champions_in_field_count": len(CHAMPS_AT_ENTRY), "hall_of_famers_in_field_count": 0,
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Michael Cole, Corey Graves, Tom Phillips, Jerry \"The King\" Lawler (broadcast-wide roster; specific segment assignment unconfirmed -- see F408); Booker T joined later in the show",
    "ring_announcer": "UNKNOWN",
    "referees": "UNKNOWN",
    "special_rules": "Standard Royal Rumble rules. No title was defended within the match itself -- the winner instead earned a women's championship match at WrestleMania 36.",
    "title_on_the_line": "FALSE",
    "championship_implications": "The winner earned a women's championship match at WrestleMania 36. Charlotte Flair won this Rumble. Kairi Sane entered as reigning WWE Women's Tag Team Champion (with Asuka, who did not compete); Toni Storm and Shayna Baszler both entered as recently-former (not reigning) champions of their respective titles -- see F404.",
    "winners_reward": "A women's championship match at WrestleMania 36.",
    "historical_significance": (
        "Charlotte Flair's first Royal Rumble win, entering #17 and eliminating Shayna Baszler for the win after "
        "surviving 27:19. Shayna Baszler and Bianca Belair tied for the most eliminations in Women's Royal Rumble "
        "history with 8 apiece, breaking Nia Jax's prior record of 7 (see NM083) -- Belair, making her first "
        "appearance in this database, had not yet debuted on the WWE main roster at the time of this event. "
        "Santino Marella returned in his comedic 'Santina' persona for a self-elimination (NM085). Kairi Sane "
        "entered as the field's one reigning champion, correcting an initial working assumption about who held the "
        "WWE Women's Tag Team Championship at this point (NM086/F404). Mercedes Martinez, signed to WWE only weeks "
        "earlier, made what amounted to her in-ring WWE debut here. Built as a fully separate event/record from "
        "RR2020M (the Men's Royal Rumble, held the same night) per Shane's standing instruction to keep the two "
        "matches separate."
    ),
    "notes": (
        "Entry order and eliminator credit CONFIRMED for all 30 entrants via 2-3 independent sources each on the "
        "first extraction attempt (no discard/re-pull needed this year). Mercedes Martinez's is the match's only "
        "shared/2-person elimination credit, not disputed. Champion-status corrections applied for 3 entrants "
        "(F404). Mia Yim's real surname is CONFLICTING (F405). Attendance is CONFLICTING (F406, shared card-wide "
        "with RR2020M). Match duration and commentary-team segment assignment are only partially verified (F407/"
        "F408). 2 of this pass's 9 new wrestlers (Bianca Belair, Shayna Baszler) were incorrectly assumed to need "
        "no fresh bio by initial research, corrected during this build (F409). Two single-source narrative claims "
        "are preserved but flagged uncorroborated (F410). Global match-clock timing (elimination_clock_time) left "
        "UNKNOWN throughout. WWE Hall of Fame status was checked for all 9 newly-added wrestlers as part of this "
        "build, per Shane's standing process -- none are inducted as of this build."
    ),
    "data_quality_status": "CONFLICTING", "source_ids": "S197;S198;S199;S200;S201;S202;S204;S205;S206;S207;S208;S209",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2020 Women's build complete: {len(new_wrestlers)} new wrestlers ({len(reused)} reused), "
      f"{len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, {len(sources)} sources logged, "
      f"{len(flags) + len(flags2)} flags, {len(nm_rows)} notable_moments rows.")
