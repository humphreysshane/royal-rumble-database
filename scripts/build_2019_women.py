# -*- coding: utf-8 -*-
"""
Builds all rows for the 2019 Women's Royal Rumble -- schema v2.

Royal Rumble 2019, January 27, 2019, Chase Field, Phoenix, Arizona. This is
the WOMEN'S match only. The Men's Royal Rumble held the same night is a
fully separate event/record -- see build_2019_men.py -- per Shane's
explicit instruction (2026-09-20): "keep them separate."

NEW PROCESS, continuing from RR2018M/RR2018W/RR2019M: WWE Hall of Fame
status (and deceased status) is checked for every new wrestler as part of
building the event they're first added in. Applied here for all 14
wrestlers new to this database this pass -- none are HOF-inducted as of
today (2026-09-21); all are alive.

Nia Jax (already in this database from RR2018W) also competes in THIS
match, in addition to a genuine, well-documented same-night appearance in
the MEN'S Royal Rumble -- see build_2019_men.py's docstring/NM066. Her
Women's-division stat line here is built exactly like any other entrant's.

SOURCES CONSULTED THIS PASS (live web research via a dedicated research
agent, cross-validated against each other -- see flags.csv for where they
disagreed). Per the methodology learned on RR2018M/W, no single generic
Wikipedia table-extraction was trusted blind -- a first literal-transcription
attempt came back internally inconsistent (duplicate Draw numbers) and was
discarded; a clean re-extraction (raw markdown table verbatim) was
independently corroborated by ProWrestling Fandom's own row-by-row
transcription and an arithmetic self-consistency check (elimination order
1-29 used exactly once; per-wrestler elimination-credit tally sums to 33 =
29 actual eliminations + 4 shared-credit spots, confirming no 3+-person
"group" eliminations are hiding in the data):
  S173 Wikipedia, 'Royal Rumble (2019)' event article (women's section +
       footnotes), plus individual biography pages for all 14 new
       wrestlers listed below                                           tier 10
  S174 ProWrestling Fandom, 'Royal Rumble 2019' event page (women's
       section)                                                          tier 10
  S175 Cageside Seats, 'Women's Royal Rumble 2019 Match Time and
       Statistics' -- independent fan re-timing from tape                tier 9
  S176 mykhel.com, 'Serial wise entries and eliminations' listicle
       (women's table) -- unreliable on 2 specific credits, see F388     tier 12
  S177 TJR Wrestling, 'WWE Royal Rumble 2019' review                     tier 9
  S178 comicbook.com, Becky Lynch/Lana replacement article               tier 9
  S179 diva-dirt.com, 'Becky Lynch wins the 2019 Women's Royal Rumble'
       recap                                                             tier 12
  S180 heelbynature.com, attendance-figure article (citing Dave Meltzer) tier 12
  S181 WWE.com, WrestleMania 35 'winner-take-all' triple-threat recap
       (title-implication/build context)                                 tier 1
  S182 Gerweck.net, Xia Li wrestler profile (substitute source)          tier 12
  S183 thesmackdownhotel.com, Candice LeRae and Io Shirai/Iyo Sky
       wrestler profiles (substitute sources), plus a consolidated
       259-entry WWE Hall of Fame roster page (HOF cross-check)          tier 12

CROSS-VALIDATION RESULTS:
  - Entry order (1-30) and eliminator/order credit: CONFIRMED across
    Wikipedia and ProWrestling Fandom, cross-checked by name. Arithmetic
    self-consistency check passed (33 total credits = 29 eliminations + 4
    genuinely 2-person shared spots -- Nikki Cross by Billie Kay & Peyton
    Royce; Sarah Logan by Natalya & Kairi Sane; Alexa Bliss by Bayley &
    Carmella; Bayley by Nia Jax & Charlotte Flair -- confirmed as true
    2-person credits, not 3+-person "group" eliminations, across all
    sources).
  - Billie Kay/Peyton Royce eliminator credit: genuinely CONFLICTING. All
    primary/majority sources (S173, S174, S177) agree Lacey Evans
    eliminated both. S176 (mykhel.com) instead claims Charlotte Flair
    eliminated both, AND separately drops Charlotte Flair's co-credit on
    Bayley's elimination (listing only Nia Jax). Both mykhel discrepancies
    are treated as errors in that single tier-12 source against 2-3
    independent, higher/equal-tier sources -- Lacey Evans (not Charlotte
    Flair) and the Nia Jax + Charlotte Flair shared credit on Bayley are
    used in the structured fields, with the disagreement preserved rather
    than silently ignored -- see F388.
  - Mandy Rose / Naomi blown spot: CONFIRMED via a direct Wikipedia
    footnote -- Mandy Rose eliminated Naomi despite having already been
    eliminated herself moments earlier (she reached back in from the floor)
    -- an unusual but officially-recorded credit, not treated as an error.
  - Lana / Becky Lynch entry mechanics: CONFIRMED via a direct Wikipedia
    footnote (quoted in full in F392) -- Lana was assigned entry #28 and
    "came out" as that entrant, but a storyline ankle injury (suffered
    during Rusev's Kickoff Show title match, when he accidentally knocked
    her off the apron) kept her from actually competing. Becky Lynch, who
    had just lost her own SmackDown Women's Championship match to Asuka
    earlier the same card, was allowed by Fit Finlay to take the #28 slot
    -- but only after Carmella (the official #30 entrant) had already
    entered, "with the clock already running on Lana." This database
    records Becky Lynch's OFFICIAL entry_number as 28 (the numbered slot
    she inherited), matching how this database has always treated numbered-
    slot replacements (e.g. RR2018M's Sami Zayn/Tye Dillinger, RR2018W's
    Kairi Sane/Alicia Fox) -- but her CHRONOLOGICALLY LAST physical entry
    (after #30) is preserved in the entrant notes and in final_entrant_id,
    which is set to Carmella (the true #30) rather than Becky Lynch, to
    keep entry_number's meaning consistent database-wide. No separate
    wrestler_id/entrant row is created for Lana, matching this database's
    precedent for scheduled-but-never-entered wrestlers (e.g. RR2018W's
    Alicia Fox).
  - Match duration has a genuine ~47-second spread across sources:
    Wikipedia states 1:12:00 (also calling it "the longest women's Royal
    Rumble match held to date," a record later broken by Bianca Belair in
    2021); ProWrestling Fandom logs 1:11:13; Cageside Seats logs 1:11:24.
    Per the source-tier tie-break, Cageside Seats' tier (9) outranks
    Wikipedia/Fandom's tier (10), so 1:11:24 is used in the structured
    field -- see F390.
  - Attendance is genuinely CONFLICTING, a card-wide dispute shared with
    build_2019_men.py -- WWE's official announced figure is 48,193; Dave
    Meltzer (cited by heelbynature.com) estimated actual attendance at
    ~40,000 with ~32,000 paid. Both figures recorded -- see F389.
  - Commentary team is only PARTIALLY resolved -- Wikipedia's own credits
    split by broadcast brand (Raw: Michael Cole & Renee Young; SmackDown:
    Tom Phillips & Byron Saxton, with Corey Graves and Beth Phoenix also
    named depending on segment) rather than giving one fixed team for this
    specific match -- left flagged rather than asserted as a single team,
    pending a video-based confirmation -- see F391.
  - Sasha Banks did NOT compete in this match -- absent from all
    cross-checked entrant tables. (Working research assumptions initially
    treated her as a probable "already in database" entrant; this was
    caught and corrected before any data was written -- no erroneous row
    exists in entrants.csv for her.)
  - WWE Hall of Fame status was checked individually for all 14 new
    wrestlers as of today (2026-09-21) -- none are inducted; none are
    deceased.

WHAT'S ACTUALLY KNOWN THIS YEAR: entry order and eliminator credit CONFIRMED
for all 30 entrants/29 eliminations (4 of which are shared/2-person
credits; no 3+-person "group" eliminations this year). Event-level facts
(date, venue, title-implication chain to WrestleMania 35) CONFIRMED via 2+
sources; attendance, match duration, commentary team, and one eliminator
credit are CONFLICTING/unresolved to single-source certainty (see above/
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
EVENT_ID = "RR2019W"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S173", "Wikipedia (English), 'Royal Rumble (2019)' event article (women's section) plus individual wrestler biography pages", "reference_site", "https://en.wikipedia.org/wiki/Royal_Rumble_(2019)", 10, "Wikipedia/reference sites", "2026-09-21",
     "Full entrant/elimination table (clean re-extraction after a first, internally-inconsistent pull was "
     "discarded), event facts, footnotes (Mandy Rose/Naomi blown spot; Lana/Becky Lynch entry mechanics), and 14 "
     "individual new-wrestler biography pages."),
    ("S174", "ProWrestling Fandom, 'Royal Rumble 2019' event page (women's section)", "reference_site", "https://prowrestling.fandom.com/wiki/Royal_Rumble_2019", 10, "Wikipedia/reference sites", "2026-09-21",
     "Independent (community-wiki) row-by-row cross-check of the entrant/elimination table, matching S173 on "
     "29/30 rows -- used to corroborate the re-extracted Wikipedia table after the first attempt was discarded."),
    ("S175", "Cageside Seats, 'Women's Royal Rumble 2019 Match Time and Statistics'", "contemporary_publication", "https://www.cagesideseats.com/wwe/2019/2/2/18207923/wwe-royal-rumble-2019-womens-match-time-statistics", 9, "Contemporary wrestling publication", "2026-09-21",
     "Independent (not WWE-sourced) stopwatch re-timing. Its tier (9) wins the source-tier tie-break for match "
     "duration (1:11:24) over Wikipedia/Fandom's 1:12:00/1:11:13 -- see F390."),
    ("S176", "mykhel.com, 'Serial wise entries and eliminations' listicle (women's table)", "other_stats_site", "https://www.mykhel.com/wwe/serial-wise-entries-eliminations-men-women-s-wwe-royal-rumble-2019-109109.html", 12, "Other reputable site", "2026-09-21",
     "Diverges from the majority-sourced table on 2 credits: claims Charlotte Flair (not Lacey Evans) eliminated "
     "Billie Kay and Peyton Royce, and drops Charlotte Flair's shared credit on Bayley's elimination -- both "
     "treated as errors in this single tier-12 source, not adopted -- see F388."),
    ("S177", "TJR Wrestling, 'WWE Royal Rumble 2019 Review'", "contemporary_publication", "https://tjrwrestling.net/review/wwe-royal-rumble-2019-review/", 9, "Contemporary wrestling publication", "2026-09-21",
     "3rd independent cross-check corroborating the majority Lacey Evans (not Charlotte Flair) credit for the "
     "Billie Kay/Peyton Royce eliminations, and a narrative source for the Lana/Becky Lynch sequence."),
    ("S178", "comicbook.com, Becky Lynch/Lana replacement article", "contemporary_publication", "https://comicbook.com/wwe/news/becky-lynch-wwe-royal-rumble/", 9, "Contemporary wrestling publication", "2026-09-21",
     "Contemporary account of Becky Lynch's insertion into Lana's vacated slot, including the detail that fan "
     "chants helped pressure officials into allowing it."),
    ("S179", "diva-dirt.com, 'Becky Lynch wins the 2019 Women's Royal Rumble'", "other_stats_site", "https://www.diva-dirt.com/becky-lynch-wins-the-2019-womens-royal-rumble/", 12, "Other reputable site", "2026-09-21",
     "Dedicated women's-wrestling outlet recap, used as an additional cross-check on the match's narrative "
     "sequence and stakes."),
    ("S180", "heelbynature.com, attendance-figure article citing Dave Meltzer", "other_stats_site", "https://heelbynature.com/wrestling-news/wwe-news/actual-wwe-2019-royal-rumble-attendance-figure/", 12, "Other reputable site", "2026-09-21",
     "Reports Dave Meltzer's ~40,000 actual-attendance / ~32,000-paid estimate against WWE's announced 48,193 -- "
     "see F389 (a card-wide dispute, also carried in build_2019_men.py's F382)."),
    ("S181", "WWE.com, WrestleMania 35 'winner-take-all' triple-threat recap", "official_wwe", "https://www.wwe.com/shows/wrestlemania/wrestlemania-35/ronda-rousey-vs-becky-lynch-vs-charlotte-flair-results", 1, "WWE / official sources", "2026-09-21",
     "Confirms the storyline arc from this Rumble win to the WrestleMania 35 winner-take-all triple threat that "
     "Becky Lynch went on to win, becoming the first woman to hold both women's titles simultaneously."),
    ("S182", "Gerweck.net, Xia Li wrestler profile", "other_stats_site", "https://gerweck.net/2019/01/28/xia-li/", 12, "Other reputable site", "2026-09-21",
     "Substitute 2nd bio-data cross-check source for Xia Li, used because Cagematch.net and ProWrestling Fandom "
     "individual wrestler-page fetches both failed this pass (429 rate-limit / HTTP 402 respectively)."),
    ("S183", "thesmackdownhotel.com, Candice LeRae and Io Shirai/Iyo Sky wrestler profiles, plus a consolidated 259-entry WWE Hall of Fame roster page", "other_stats_site", "https://www.thesmackdownhotel.com/", 12, "Other reputable site", "2026-09-21",
     "Substitute 2nd bio-data cross-check source for Candice LeRae and Io Shirai, used because Cagematch.net and "
     "ProWrestling Fandom individual wrestler-page fetches both failed this pass; its consolidated HOF roster page "
     "was also used to cross-check all 14 new wrestlers' non-induction in a single pass."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# ENTRY ORDER (CONFIRMED, S173+S174+S177 agree by name)
# ---------------------------------------------------------------------------
all_names = [
    "Lacey Evans", "Natalya", "Mandy Rose", "Liv Morgan", "Mickie James", "Ember Moon", "Billie Kay",
    "Nikki Cross", "Peyton Royce", "Tamina", "Xia Li", "Sarah Logan", "Charlotte Flair", "Kairi Sane",
    "Maria Kanellis", "Naomi", "Candice LeRae", "Alicia Fox", "Kacy Catanzaro", "Zelina Vega", "Ruby Riott",
    "Dana Brooke", "Io Shirai", "Rhea Ripley", "Sonya Deville", "Alexa Bliss", "Bayley", "Becky Lynch",
    "Nia Jax", "Carmella",
]
assert len(all_names) == 30
# Becky Lynch's official entry_number is 28 (Lana's inherited slot) even
# though she physically entered the ring chronologically AFTER Carmella
# (#30) -- see docstring and F392. ENTRY_NUMBERS reflects the official slot.
ENTRY_NUMBERS = {name: i + 1 for i, name in enumerate(all_names)}
assert ENTRY_NUMBERS["Becky Lynch"] == 28 and ENTRY_NUMBERS["Carmella"] == 30

# Individual survival ("ring") times (Wikipedia figures; Cageside Seats'
# independent re-timing agrees within a few seconds for all but Ember Moon,
# a 35s variance not treated as a genuine conflict -- both are close enough
# that neither is marked CONFLICTING at the entrant level).
survival = {
    "Lacey Evans": "29:20", "Natalya": "56:01", "Mandy Rose": "25:50", "Liv Morgan": "0:08",
    "Mickie James": "11:38", "Ember Moon": "52:10", "Billie Kay": "9:25", "Nikki Cross": "9:00",
    "Peyton Royce": "8:38", "Tamina": "8:22", "Xia Li": "4:48", "Sarah Logan": "5:38",
    "Charlotte Flair": "50:01", "Kairi Sane": "17:00", "Maria Kanellis": "8:12", "Naomi": "1:28",
    "Candice LeRae": "9:35", "Alicia Fox": "6:55", "Kacy Catanzaro": "10:45", "Zelina Vega": "11:42",
    "Ruby Riott": "13:08", "Dana Brooke": "7:17", "Io Shirai": "13:21", "Rhea Ripley": "7:55",
    "Sonya Deville": "4:26", "Alexa Bliss": "12:59", "Bayley": "14:27", "Becky Lynch": "13:20",
    "Nia Jax": "11:59", "Carmella": "7:12",
}
assert set(survival) == set(all_names)

# Elimination order (1st-29th).
ELIM_ORDER = [
    "Liv Morgan", "Mickie James", "Nikki Cross", "Billie Kay", "Peyton Royce", "Xia Li", "Tamina", "Sarah Logan",
    "Mandy Rose", "Naomi", "Lacey Evans", "Maria Kanellis", "Alicia Fox", "Candice LeRae", "Kairi Sane",
    "Kacy Catanzaro", "Dana Brooke", "Zelina Vega", "Sonya Deville", "Ruby Riott", "Rhea Ripley", "Io Shirai",
    "Natalya", "Ember Moon", "Alexa Bliss", "Carmella", "Bayley", "Nia Jax", "Charlotte Flair",
]
assert len(ELIM_ORDER) == 29
elim_number = {name: i + 1 for i, name in enumerate(ELIM_ORDER)}

FINAL_TWO = {"Becky Lynch", "Charlotte Flair"}
FINAL_THREE = {"Becky Lynch", "Charlotte Flair", "Nia Jax"}
FINAL_FOUR = {"Becky Lynch", "Charlotte Flair", "Nia Jax", "Bayley"}

# name -> (eliminator names, is_shared, notes)
ELIMINATORS = {
    "Liv Morgan": (["Natalya"], False, ""),
    "Mickie James": (["Tamina"], False, ""),
    "Nikki Cross": (["Billie Kay", "Peyton Royce"], True, "Shared elimination credit -- S173/S174/S177 agree ('the IIconics')."),
    "Billie Kay": (["Lacey Evans"], False, "CONFLICTING eliminator credit in one source (mykhel.com claims Charlotte Flair) -- the majority (Wikipedia, Fandom, TJR) agree on Lacey Evans, used here. See F388."),
    "Peyton Royce": (["Lacey Evans"], False, "CONFLICTING eliminator credit in one source (mykhel.com claims Charlotte Flair) -- the majority (Wikipedia, Fandom, TJR) agree on Lacey Evans, used here. See F388."),
    "Xia Li": (["Charlotte Flair"], False, ""),
    "Tamina": (["Charlotte Flair"], False, ""),
    "Sarah Logan": (["Natalya", "Kairi Sane"], True, "Shared elimination credit -- S173/S174 agree."),
    "Mandy Rose": (["Naomi"], False, ""),
    "Naomi": (["Mandy Rose"], False, "Blown-spot elimination, CONFIRMED via a direct Wikipedia footnote: Mandy Rose had already been eliminated moments earlier, but reached back in from the floor and pulled Naomi out anyway -- it stood as her official elimination credit."),
    "Lacey Evans": (["Charlotte Flair"], False, ""),
    "Maria Kanellis": (["Alicia Fox"], False, ""),
    "Alicia Fox": (["Ruby Riott"], False, ""),
    "Candice LeRae": (["Ruby Riott"], False, ""),
    "Kairi Sane": (["Ruby Riott"], False, ""),
    "Kacy Catanzaro": (["Rhea Ripley"], False, ""),
    "Dana Brooke": (["Rhea Ripley"], False, ""),
    "Zelina Vega": (["Rhea Ripley"], False, ""),
    "Sonya Deville": (["Alexa Bliss"], False, ""),
    "Ruby Riott": (["Bayley"], False, ""),
    "Rhea Ripley": (["Bayley"], False, ""),
    "Io Shirai": (["Nia Jax"], False, ""),
    "Natalya": (["Nia Jax"], False, ""),
    "Ember Moon": (["Alexa Bliss"], False, "Cageside Seats' independent re-timing gives 52:45 versus Wikipedia's 52:10 -- a 35-second variance, the largest of the match, but not treated as a genuine conflict (both cluster in the same range)."),
    "Alexa Bliss": (["Bayley", "Carmella"], True, "Shared elimination credit -- S173/S174 agree."),
    "Carmella": (["Charlotte Flair"], False, ""),
    "Bayley": (["Nia Jax", "Charlotte Flair"], True, "Shared elimination credit -- S173/S174/S177 agree. One source (mykhel.com) drops Charlotte Flair's co-credit here, listing only Nia Jax -- treated as an error in that single tier-12 source. See F388."),
    "Nia Jax": (["Becky Lynch"], False, "Nia Jax also competed in the Men's Royal Rumble the same night -- see build_2019_men.py's NM066."),
    "Charlotte Flair": (["Becky Lynch"], False, "The winning elimination. Charlotte Flair finished as runner-up with a match-high 5 credited eliminations (Xia Li, Tamina, Lacey Evans, Carmella, plus a shared credit on Bayley)."),
}
assert set(ELIMINATORS) == set(ELIM_ORDER)

SURPRISE_ENTRANTS = {"Becky Lynch", "Maria Kanellis"}
NON_FULL_TIME = {"Maria Kanellis"}
WRESTLED_EARLIER = {"Becky Lynch"}

# ---------------------------------------------------------------------------
# WRESTLERS -- new to this database this pass (14 of 30). Bios researched
# live and cross-checked against 2 independent sources where possible; WWE
# Hall of Fame and deceased status checked for all 14 as part of this
# build, per Shane's standing process.
# ---------------------------------------------------------------------------
# (ring_name, real_name, real_name_status, gender, dob, dob_status, deceased_date,
#  birthplace, birthplace_status, nationality, debut_year_company, hall_of_fame_year,
#  aliases_ring_names, wrestling_style, notes, source_ids)
new_wrestlers = [
    ("Lacey Evans", "Macey Estrella", "PROBABLE", "F", "1990-03-24", "PROBABLE", "", "Georgia, U.S.", "PROBABLE", "American", "2014, American Premier Wrestling (Statesboro, GA)", "",
     "Macey Evans; Ruby Mobs", "", "Rumble debut and main-roster debut, entered #1. Survived 29:20, eliminating 2 (Billie Kay, Peyton Royce) before being eliminated by Charlotte Flair. Not a WWE Hall of Famer as of this build (2026-09-21).", "S173"),
    ("Billie Kay", "Jessica McKay", "PROBABLE", "F", "1989-06-23", "PROBABLE", "", "Sydney, New South Wales, Australia", "PROBABLE", "Australian", "June 23, 2007, Pro Wrestling Alliance (Australia)", "",
     "Jessie McKay", "", "Rumble debut, entered #7. Survived 9:25, part of the shared elimination of Nikki Cross (with Peyton Royce) before being eliminated by Lacey Evans. Not a WWE Hall of Famer as of this build.", "S173"),
    ("Peyton Royce", "Cassandra Arneill", "PROBABLE", "F", "1992-11-10", "PROBABLE", "", "Sydney, New South Wales, Australia", "PROBABLE", "Australian", "Feb 28, 2009, Pro Wrestling Women's Alliance", "",
     "KC Cassidy (debut name); later Cassie Lee", "", "Rumble debut, entered #9. Survived 8:38, part of the shared elimination of Nikki Cross (with Billie Kay) before being eliminated by Lacey Evans. Not a WWE Hall of Famer as of this build.", "S173"),
    ("Nikki Cross", "Nicola Glencross", "PROBABLE", "F", "1989-04-21", "PROBABLE", "", "Glasgow, Scotland", "PROBABLE", "Scottish", "Sept 20, 2008, Scottish Wrestling Alliance", "",
     "Nikki Storm (pre-WWE independent ring name)", "", "Very recent main-roster call-up (Raw debut Jan 14, 2019). Rumble debut, entered #8. Survived 9:00, eliminated by Billie Kay & Peyton Royce (shared). Not the same person as Nikki Bella. Not a WWE Hall of Famer as of this build.", "S173"),
    ("Xia Li", "Zhao Xia", "CONFIRMED", "F", "1988-07-28", "CONFIRMED", "", "Chongqing, China", "CONFIRMED", "Chinese", "In-ring debut July 13, 2017 (Mae Young Classic); joined WWE Performance Center Jan 2017", "",
     "Lei Ying Lee (later TNA ring name, Sept 2024)", "Competitive wushu martial artist background", "Rumble debut, entered #11. Survived 4:48, eliminated by Charlotte Flair. Not a WWE Hall of Famer as of this build.", "S173;S182"),
    ("Charlotte Flair", "Ashley Elizabeth Fliehr", "CONFIRMED", "F", "1986-04-05", "CONFIRMED", "", "Charlotte, North Carolina, U.S.", "CONFIRMED", "American", "Trained from May 2012; first televised match July 17, 2013 (NXT)", "",
     "Ashley Flair; Charlotte (2013-2016, before adopting 'Charlotte Flair' around Oct 2016)", "", "First appearance in this database -- did NOT compete in RR2018W. Entered #13, finished as runner-up (eliminated by Becky Lynch after 50:01), crediting a match-high 5 eliminations (Xia Li, Tamina, Lacey Evans, Carmella, plus a shared credit on Bayley). Not a WWE Hall of Famer as of this build.", "S173"),
    ("Maria Kanellis", "Mary Louise Kanellis-Bennett", "PROBABLE", "F", "1982-02-25", "PROBABLE", "", "Ottawa, Illinois, U.S.", "PROBABLE", "American", "2004, Ohio Valley Wrestling", "",
     "Maria (used for much of her WWE tenure)", "", "A rare in-ring appearance -- she usually worked as an on-air manager (205 Live) rather than a competitor at this point in her career. Rumble debut, entered #15. Survived 8:12, eliminated by Alicia Fox, with no credited eliminations of her own this match. Not a WWE Hall of Famer as of this build.", "S173"),
    ("Candice LeRae", "Candice Gargano", "PROBABLE", "F", "1985-09-29", "PROBABLE", "", "Riverside, California, U.S.", "PROBABLE", "American", "2002, Empire Wrestling Federation", "",
     "Sweet Candy (2002-2004)", "", "Married to Johnny Gargano (also an entrant in this database's RR2019M record) -- 'LeRae' is a ring name, not her legal surname ('Gargano' is). Rumble debut, entered #17. Survived 9:35, eliminated by Ruby Riott. Not a WWE Hall of Famer as of this build.", "S173;S183"),
    ("Alicia Fox", "Victoria Elizabeth Crawford", "PROBABLE", "F", "1986-06-30", "PROBABLE", "", "Ponte Vedra Beach, Florida, U.S.", "PROBABLE", "American", "July 1, 2006", "",
     "Tori; Vix Crow", "", "Rumble debut, entered #18. Survived 6:55, eliminating Maria Kanellis before being eliminated by Ruby Riott. Not a WWE Hall of Famer as of this build.", "S173"),
    ("Kacy Catanzaro", "Kacy Esther Catanzaro", "CONFIRMED", "F", "1990-01-14", "CONFIRMED", "", "Glen Ridge, New Jersey, U.S.", "CONFIRMED", "American", "In-ring debut April 19, 2018 (NXT); signed Aug 28, 2017", "",
     "Katana Chance (adopted April 19, 2022 -- NOT the same person as her tag partner Kayden Carter)", "", "Pre-wrestling fame as an American Ninja Warrior competitor (2013-2017) -- first woman to complete a City Finals course, viral '#MightyKacy' run. Rumble debut, entered #19. Survived 10:45, eliminated by Rhea Ripley. Released from WWE May 2, 2025. Not a WWE Hall of Famer as of this build.", "S173"),
    ("Zelina Vega", "Thea Megan Trinidad Büdgen", "CONFIRMED", "F", "1990-12-27", "CONFIRMED", "", "Queens, New York City, U.S.", "CONFIRMED", "American", "Feb 20, 2010, National Wrestling Superstars", "",
     "Divina Fly; Snookie Fly; Rosita; Xelina; Queen Zelina; Thea Trinidad", "", "Recently transitioned from an on-air manager role to in-ring competition. Rumble debut, entered #20. Survived 11:42, eliminated by Rhea Ripley. Not a WWE Hall of Famer as of this build.", "S173"),
    ("Io Shirai", "Masami Odate", "PROBABLE", "F", "1990-05-08", "CONFIRMED", "", "Kamakura, Kanagawa, Japan", "CONFIRMED", "Japanese", "March 4, 2007, independent circuit", "",
     "Oyuki; Biba Kasai/Viva Kasai (Mexico, 2010); Hitokiri (2016); later Iyo Sky (adopted upon 2022 WWE main-roster call-up)", "", "NXT call-up (NXT TV debut Oct 2018). Rumble debut, entered #23. Survived 13:21, eliminated by Nia Jax, with no credited eliminations of her own this match. Real-name kanji rendering has a minor discrepancy between sources (both romanize identically as 'Odate Masami'), not treated as a genuine conflict. Not a WWE Hall of Famer as of this build.", "S173;S183"),
    ("Rhea Ripley", "Demi Bennett", "PROBABLE", "F", "1996-10-11", "PROBABLE", "", "Adelaide, South Australia, Australia", "PROBABLE", "Australian", "June 22, 2013, Riot City Wrestling (wrestled under her real name 2013-2017)", "",
     "", "", "NXT UK talent; lost the inaugural NXT UK Women's Championship to Toni Storm on Jan 12, 2019, 15 days before this event -- entered not as champion. Rumble debut, entered #24. Survived 7:55, eliminating 3 (Kacy Catanzaro, Dana Brooke, Zelina Vega) before being eliminated by Bayley. Not a WWE Hall of Famer as of this build.", "S173"),
    ("Alexa Bliss", "Alexis Kaufman", "PROBABLE", "F", "1991-08-09", "PROBABLE", "", "Columbus, Ohio, U.S.", "PROBABLE", "American", "Sept 20, 2013 (NXT); main roster 2016", "",
     "La Luchadora (masked alter-ego gimmick)", "", "Three-time Raw Women's Champion and two-time SmackDown Women's Champion prior to this event (first woman to hold both) -- did not hold a title at the time of this match. Rumble debut, entered #26. Survived 12:59, eliminating 2 (Sonya Deville, Ember Moon) before being eliminated by Bayley & Carmella (shared). Not a WWE Hall of Famer as of this build.", "S173"),
]

reused = {
    "Natalya": "natalya", "Mandy Rose": "mandy-rose", "Liv Morgan": "liv-morgan", "Mickie James": "mickie-james",
    "Ember Moon": "ember-moon", "Tamina": "tamina", "Sarah Logan": "sarah-logan", "Kairi Sane": "kairi-sane",
    "Naomi": "naomi", "Ruby Riott": "ruby-riott", "Dana Brooke": "dana-brooke", "Sonya Deville": "sonya-deville",
    "Bayley": "bayley", "Nia Jax": "nia-jax", "Carmella": "carmella", "Becky Lynch": "becky-lynch",
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
    is_winner = (name == "Becky Lynch")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, is_shared, extra_note = ELIMINATORS.get(name, ([], False, ""))

    notes_parts = [extra_note] if extra_note else []
    if name == "Becky Lynch":
        notes_parts.append("Entered under Lana's official #28 slot -- Lana had 'come out' as that entrant but a "
                            "storyline ankle injury (suffered during Rusev's Kickoff Show title match) kept her "
                            "from competing; Becky Lynch was allowed by Fit Finlay to take the vacated spot, but "
                            "only after Carmella (the official #30 entrant) had already entered, with the clock "
                            "already running on Lana's slot -- making her the chronologically LAST physical entrant "
                            "of the match despite carrying the #28 official number. See F392. Lynch had lost her "
                            "own SmackDown Women's Championship match to Asuka earlier the same card before winning "
                            "this Rumble, eliminating Nia Jax and then Charlotte Flair (the winning elimination) "
                            "after surviving 13:20. Earned a spot in the WrestleMania 35 winner-take-all triple "
                            "threat (with Ronda Rousey and Charlotte Flair), which she won, becoming the first "
                            "woman to hold both women's titles simultaneously and headlining the first-ever "
                            "women's WrestleMania main event.")

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
            "is_storyline_related": "TRUE" if name in ("Naomi", "Becky Lynch") else "UNKNOWN",
            "was_already_incapacitated": "TRUE" if name == "Naomi" else "UNKNOWN",
            "is_disputed": "TRUE" if name in ("Billie Kay", "Peyton Royce") else "FALSE",
            "simultaneous_group_id": "",
            "data_quality_status": "CONFLICTING" if name in ("Billie Kay", "Peyton Royce") else "CONFIRMED",
            "source_ids": "S173;S174;S177",
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
        "current_champion_title": "",
        "championship_level": "",
        "championship_partner": "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
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
        "is_runner_up": "TRUE" if name == "Charlotte Flair" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "TRUE" if name in SURPRISE_ENTRANTS else "FALSE",
        "legend_returning": "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "TRUE" if name in NON_FULL_TIME else "FALSE",
        "wrestled_earlier_on_card": "TRUE" if name in WRESTLED_EARLIER else "FALSE",
        "was_hof_member_at_time": "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S173;S174;S177",
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
    ("F388", EVENT_ID, "eliminations", "billie-kay;peyton-royce;bayley", "eliminator_wrestler_id", "conflicting_sources",
     "Billie Kay's and Peyton Royce's eliminator credit is genuinely CONFLICTING between sources: Wikipedia (S173), "
     "ProWrestling Fandom (S174), and TJR Wrestling (S177) all agree Lacey Evans eliminated both. mykhel.com (S176) "
     "instead claims Charlotte Flair eliminated both -- an outlier against 3 independent, equal-or-higher-tier "
     "sources, not adopted. mykhel.com separately also drops Charlotte Flair's shared co-credit on Bayley's "
     "elimination (listing only Nia Jax) -- also treated as an error in that single source, not adopted; the "
     "shared Nia Jax + Charlotte Flair credit on Bayley is used per the majority. Lacey Evans's own eliminator "
     "credit for Billie Kay/Peyton Royce is NOT in dispute as to WHETHER she eliminated them, only mykhel.com's "
     "single-source substitution of Charlotte Flair.",
     "S173;S174;S176;S177", "open", "2026-09-21"),
    ("F389", EVENT_ID, "events", EVENT_ID, "attendance_official;attendance_reported", "conflicting_sources",
     "Attendance is genuinely CONFLICTING -- a card-wide dispute shared with build_2019_men.py's F382, since both "
     "matches shared the same card/venue/night. WWE's officially announced figure is 48,193; Dave Meltzer "
     "(Wrestling Observer, cited by heelbynature.com) estimated actual bodies in the building at approximately "
     "40,000, with paid attendance around 32,000. Both figures are recorded in the structured fields "
     "(attendance_official=48193, attendance_reported=40000) rather than silently picking one.",
     "S173;S180", "open", "2026-09-21"),
    ("F390", EVENT_ID, "events", EVENT_ID, "duration_total", "conflicting_sources",
     "Match duration has a genuine ~47-second spread across sources: Wikipedia states 1:12:00 (also the source of "
     "the 'longest women's Royal Rumble match held to date' claim, a record later broken by Bianca Belair in "
     "2021); ProWrestling Fandom logs 1:11:13; Cageside Seats logs 1:11:24. Per DEFINITIONS.md's source-tier "
     "tie-break, Cageside Seats' tier (9, contemporary publication) outranks Wikipedia/Fandom's tier (10, "
     "reference site), so 1:11:24 is used in the structured duration_total field.",
     "S173;S174;S175", "resolved", "2026-09-21"),
    ("F391", EVENT_ID, "events", EVENT_ID, "commentary_team", "unverified",
     "Commentary team is only partially resolved. Wikipedia's own broadcast credits split by brand rather than "
     "naming one fixed team for this specific match: Raw portion credited to Michael Cole & Renee Young; SmackDown "
     "portion credited to Tom Phillips & Byron Saxton; Corey Graves and Beth Phoenix are also named depending on "
     "segment. This database records the fullest credited set in the structured field but flags it as needing a "
     "video-based confirmation before treating any single 4-person team as final.",
     "S173", "open", "2026-09-21"),
    ("F392", EVENT_ID, "entrants", "becky-lynch", "entry_number;is_final_entrant", "unverified",
     "Becky Lynch's entry mechanics are unusual and CONFIRMED via a direct Wikipedia footnote (quoted in full): "
     "\"Lana came out as the #28 entrant, but a storyline ankle injury suffered on the pre-show kept her from "
     "competing. Becky Lynch was allowed by Fit Finlay to take her spot after Carmella entered the match, with the "
     "clock already running on Lana.\" This database records Becky Lynch's OFFICIAL entry_number as 28 (the "
     "numbered slot she inherited), matching how numbered-slot replacements have always been treated in this "
     "database (e.g. RR2018M's Sami Zayn/Tye Dillinger, RR2018W's Kairi Sane/Alicia Fox) -- but she was, in "
     "practice, the chronologically LAST physical entrant of the match, entering after #30 Carmella. "
     "final_entrant_id on this event's row is therefore set to Carmella (the true #30) rather than Becky Lynch, to "
     "keep entry_number's meaning consistent database-wide; her true chronological-last status is preserved in her "
     "entrant-row notes instead. No separate wrestler_id/entrant row exists for Lana, matching this database's "
     "precedent for scheduled-but-never-entered wrestlers (e.g. RR2018W's Alicia Fox).",
     "S173;S178", "resolved", "2026-09-21"),
    ("F393", EVENT_ID, "wrestlers", "lacey-evans;billie-kay;peyton-royce;nikki-cross;xia-li;charlotte-flair;maria-kanellis;candice-lerae;alicia-fox;kacy-catanzaro;zelina-vega;io-shirai;rhea-ripley;alexa-bliss", "hall_of_fame_year", "corrected",
     "Continuing the process established at RR2017M/RR2018M/RR2018W/RR2019M: WWE Hall of Fame status and deceased "
     "status were checked for all 14 wrestlers new to this database this pass, as part of this build. Result: none "
     "of the 14 are WWE Hall of Fame inductees as of today (2026-09-21); none are deceased.",
     "S173;S183", "resolved", "2026-09-21"),
    ("F394", EVENT_ID, "entrances;moves", "*", "n/a", "out_of_scope_no_tool",
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
        "moment_id": "NM072", "event_id": EVENT_ID, "wrestler_ids_involved": "becky-lynch",
        "category": "milestone_first",
        "title": "Becky Lynch wins the Royal Rumble hours after losing her own title match",
        "description": "Lynch lost her SmackDown Women's Championship match to Asuka earlier the same card, then was allowed to take injured advertised entrant Lana's vacated #28 slot -- entering, in practice, after #30 Carmella had already gone in. She eliminated Nia Jax and then Charlotte Flair for the winning elimination after surviving 13:20, earning a spot in the WrestleMania 35 winner-take-all triple threat (also featuring Ronda Rousey and Charlotte Flair), which she won -- becoming the first woman to hold both women's titles simultaneously and headlining the first-ever women's WrestleMania main event.",
        "data_quality_status": "CONFIRMED", "source_ids": "S173;S178;S181",
        "notes": "",
    },
    {
        "moment_id": "NM073", "event_id": EVENT_ID, "wrestler_ids_involved": "lana",
        "category": "notable_absence_or_substitution",
        "title": "Lana's storyline injury opened the door for Becky Lynch",
        "description": "Lana was drawn/assigned the #28 slot and came out as that entrant, but a storyline ankle injury -- suffered when Rusev accidentally knocked her off the ring apron during his Kickoff Show US Championship match -- kept her from actually competing. She has no wrestler_id/entrant row in this database, matching this database's precedent for scheduled-but-never-entered wrestlers.",
        "data_quality_status": "CONFIRMED", "source_ids": "S173;S178",
        "notes": "Lana is referenced by name but is not herself a wrestler_id in this database, since she never entered the match.",
    },
    {
        "moment_id": "NM074", "event_id": EVENT_ID, "wrestler_ids_involved": "nia-jax",
        "category": "milestone_first",
        "title": "Nia Jax competed in both Royal Rumble matches the same night",
        "description": "Nia Jax entered #29 in this Women's Royal Rumble (eliminating Io Shirai and Natalya solo, plus a shared credit on Bayley, before being eliminated by Becky Lynch) and later the same night appeared as a surprise entrant in the Men's Royal Rumble as well -- becoming the first person to compete in (and score eliminations in) both Rumble matches on one card. See build_2019_men.py's NM066 for the fuller account, including a legitimate in-ring injury she caused there.",
        "data_quality_status": "CONFIRMED", "source_ids": "S173",
        "notes": "",
    },
    {
        "moment_id": "NM075", "event_id": EVENT_ID, "wrestler_ids_involved": "mandy-rose;naomi",
        "category": "other",
        "title": "Mandy Rose eliminated Naomi despite already being eliminated herself",
        "description": "A direct Wikipedia footnote confirms Mandy Rose, having already been eliminated moments earlier, reached back into the ring from the floor and pulled Naomi out -- an unusual blown-spot moment that nonetheless stood as her official elimination credit.",
        "data_quality_status": "CONFIRMED", "source_ids": "S173",
        "notes": "",
    },
    {
        "moment_id": "NM076", "event_id": EVENT_ID, "wrestler_ids_involved": "natalya",
        "category": "record",
        "title": "Natalya's 56:01 was the longest individual women's Royal Rumble survival time to date",
        "description": "Natalya entered #2 and survived 56:01, the longest individual time in Women's Royal Rumble history at the time -- a record that stood until Bianca Belair broke it in 2021.",
        "data_quality_status": "CONFIRMED", "source_ids": "S173",
        "notes": "",
    },
    {
        "moment_id": "NM077", "event_id": EVENT_ID, "wrestler_ids_involved": "charlotte-flair",
        "category": "record",
        "title": "Charlotte Flair led all eliminators with 5 credited eliminations",
        "description": "Charlotte Flair (entered #13, runner-up) eliminated Xia Li, Tamina, Lacey Evans and Carmella solo, plus a shared credit on Bayley's elimination -- the match's highest total, before being eliminated herself by Becky Lynch for the winning elimination.",
        "data_quality_status": "CONFIRMED", "source_ids": "S173;S174",
        "notes": "",
    },
]
with open(os.path.join(DATA_DIR, "notable_moments.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=NOTABLE_MOMENTS_FIELDS)
    for row in nm_rows:
        writer.writerow(row)

flags2 = [
    ("F395", EVENT_ID, "notable_moments", "NM072;NM073;NM074;NM075;NM076;NM077", "n/a", "corrected",
     "Added 6 notable_moments.csv rows for this newly-built event: Becky Lynch's same-night title-loss-to-Rumble-"
     "win story, Lana's storyline injury/substitution, Nia Jax's same-night double-Rumble appearance, the Mandy "
     "Rose/Naomi blown-spot elimination, Natalya's then-record 56:01 survival time, and Charlotte Flair's "
     "match-high 5 credited eliminations.",
     "S173;S174;S178;S181", "resolved", "2026-09-21"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags2)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2019", "match_name": "Royal Rumble Match",
    "match_type": "Women's", "event_date": "2019-01-27",
    "venue": "Chase Field", "city_region": "Phoenix, Arizona", "country": "United States",
    "attendance_official": 48193, "attendance_reported": 40000,
    "entry_interval_seconds": "", "entrant_count": 30,
    "duration_total": "1:11:24", "duration_status": "CONFLICTING",
    "winner_id": "becky-lynch", "runner_up_id": "charlotte-flair",
    "final_two_ids": "becky-lynch;charlotte-flair",
    "final_three_ids": "becky-lynch;charlotte-flair;nia-jax",
    "final_four_ids": "becky-lynch;charlotte-flair;nia-jax;bayley",
    "first_entrant_id": "lacey-evans", "second_entrant_id": "natalya", "final_entrant_id": "carmella",
    "first_elimination_id": "liv-morgan", "last_elimination_before_winner_id": "charlotte-flair",
    "eliminations_count": 29, "eliminators_count": 17,
    "surprise_entrants_count": len(SURPRISE_ENTRANTS),
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": 0,
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Michael Cole & Renee Young (Raw portion); Tom Phillips & Byron Saxton (SmackDown portion); Corey Graves and Beth Phoenix also credited on some segments",
    "ring_announcer": "Mike Rome",
    "referees": "UNKNOWN",
    "special_rules": "Standard Royal Rumble rules. No title was defended within the match itself -- the winner instead earned a choice of women's championship match at WrestleMania 35.",
    "title_on_the_line": "FALSE",
    "championship_implications": "The winner earned a women's championship match at WrestleMania 35. Becky Lynch won and, via an evolving storyline (including her own real-life suspension angle in early February 2019), the match became a winner-take-all triple threat against Raw Women's Champion Ronda Rousey and SmackDown Women's Champion Charlotte Flair -- neither of whom competed in this Rumble. Lynch won at WrestleMania 35, becoming the first woman to hold both women's titles simultaneously.",
    "winners_reward": "A women's championship match at WrestleMania 35, which evolved into a winner-take-all triple threat against both reigning champions. Becky Lynch won both titles.",
    "historical_significance": (
        "Becky Lynch's Royal Rumble win, remarkable for coming the same night she lost her own SmackDown Women's "
        "Championship match to Asuka -- she was allowed to take injured advertised entrant Lana's vacated #28 "
        "slot, entering, in practice, after #30 Carmella had already gone in (see F392), before eliminating Nia "
        "Jax and then Charlotte Flair for the win. This set up the first-ever women's WrestleMania main event, a "
        "winner-take-all triple threat Lynch won to become the first woman to hold both women's titles "
        "simultaneously. Charlotte Flair, making her first appearance in this database, finished as runner-up with "
        "a match-high 5 credited eliminations. Natalya's 56:01 survival time was the longest in Women's Royal "
        "Rumble history to that point, a record that stood until 2021. Nia Jax, already in this database from "
        "RR2018W, competed in both this match and the Men's Royal Rumble the same night -- see this database's "
        "separate RR2019M record. Mandy Rose eliminated Naomi despite having already been eliminated herself, a "
        "confirmed blown-spot moment. Built as a fully separate event/record from RR2019M (the Men's Royal Rumble, "
        "held the same night) per Shane's explicit instruction to keep the two matches separate."
    ),
    "notes": (
        "Entry order and eliminator credit CONFIRMED for all 30 entrants via 2-3 independent sources each, cross-"
        "checked by name after a first, internally-inconsistent Wikipedia table extraction was discarded and "
        "re-pulled cleanly. One eliminator credit (Billie Kay/Peyton Royce) is CONFLICTING against a single "
        "outlier source -- see F388. Attendance and match duration are CONFLICTING (F389/F390, the former shared "
        "card-wide with RR2019M). Commentary team is only partially resolved, split by broadcast brand per "
        "Wikipedia's own credits (F391). Global match-clock timing (elimination_clock_time) left UNKNOWN "
        "throughout. WWE Hall of Fame status was checked for all 14 newly-added wrestlers as part of this build, "
        "per Shane's standing process -- none are inducted as of this build (F393)."
    ),
    "data_quality_status": "CONFLICTING", "source_ids": "S173;S174;S175;S176;S177;S178;S179;S180;S181",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2019 Women's build complete: {len(new_wrestlers)} new wrestlers ({len(reused)} reused), "
      f"{len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, {len(sources)} sources logged, "
      f"{len(flags) + len(flags2)} flags, {len(nm_rows)} notable_moments rows.")
