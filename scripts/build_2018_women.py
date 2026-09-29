# -*- coding: utf-8 -*-
"""
Builds all rows for the 2018 Women's Royal Rumble -- schema v2.

Royal Rumble 2018, January 28, 2018, Wells Fargo Center, Philadelphia, PA.
This is the FIRST-EVER Women's Royal Rumble match. It shares a card with
the Men's Royal Rumble match held the same night (see build_2018_men.py)
but is built and stored as a FULLY SEPARATE event/record (event_id
RR2018W, not RR2018M) -- per Shane's explicit instruction (2026-09-20):
"keep them separate."

NEW PROCESS, continuing from RR2017M/RR2018M: WWE Hall of Fame status (and
deceased status) is checked for every new wrestler as part of building the
event they're first added in. Applied here for all 29 wrestlers new to
this database this pass. Beth Phoenix is the only entrant already in the
database (added via her RR2010 men's-match appearance) -- reused, not
rebuilt.

SOURCES CONSULTED THIS PASS (live web research, cross-validated -- see
flags.csv for disagreements). Reuses S144 (Wikipedia 'Royal Rumble (2018)'),
S148 (Cagematch.net event page) and S149 (WWE.com announcer lineup article)
already registered by build_2018_men.py for the same show:
  S152 WWE.com, official 'Full first-ever Women's Royal Rumble Match
       statistics' page                                               tier 1
  S153 WWE.com, 'Alicia Fox injured, out of Royal Rumble Match and
       Mixed Match Challenge' article                                 tier 1
  S154 WWE.com, 'Stephanie McMahon to join commentary for Women's
       Royal Rumble Match this Sunday' article                        tier 1
  S155 Sports Illustrated, 'Ronda Rousey's WWE Debut and Other
       Takeaways From Royal Rumble 2018' (Justin Barrasso, Jan 29 2018) tier 9
  S156 FanSided, 'Why the Ronda Rousey segment at WWE Royal Rumble
       bothered me' (Luke Norris, Jan 29 2018)                         tier 9
  S157 WWE.com, results recap page ('Asuka won the 30-Woman Royal
       Rumble Match; Ronda Rousey crashed post-match celebration')    tier 1
  S158 WWE.com, individual WWE Hall of Fame induction articles
       (Jacqueline 2016; Molly Holly 2021; Michelle McCool 2025)      tier 1
  S159 Wikipedia, 'WWE Hall of Fame' master inductee list (all
       classes) -- used to cross-check induction years                tier 10
  S160 notinhalloffame.com, Vickie Guerrero profile (confirms she has
       never been inducted in her own right)                         tier 12

CROSS-VALIDATION RESULTS:
  - Entry order (1-30) and eliminator/order credit: CONFIRMED, agreeing
    identically between S144's and S152's independently structured tables,
    with S148 (Cagematch) as a 3rd confirming source for entry order. An
    internal arithmetic self-consistency check (each wrestler's own
    "eliminations" total, summed by literally walking the 29-row table,
    matches the totals both S144 and S152 separately report) also
    balanced exactly -- including a specific, deliberate re-check of Nia
    Jax's and Michelle McCool's individual counts (see notes on their
    entrant rows below; a literal walk-through gives Nia Jax 4 solo
    eliminations, not the "5" some secondary write-ups claim).
  - Commentary team: genuinely CONFLICTING. S144 (Wikipedia infobox),
    S148 (Cagematch, in a combined show-wide roster) and S154 (a WWE.com
    article specifically announcing her addition) all agree Stephanie
    McMahon called this match alongside Michael Cole and Corey Graves.
    But S149 (a separate WWE.com 'announcer lineup' article) instead lists
    Renee Young, Beth Phoenix, Tom Phillips and Corey Graves for the
    women's match, with no McMahon. The preponderance of evidence (3
    independent sources, including one dedicated specifically to
    announcing McMahon's booth assignment, corroborated further by
    multiple contemporary outlets covering that same news) supports Cole/
    Graves/McMahon; this script uses that version in the structured field
    but logs both -- see F373. Stephanie McMahon's presence at the
    broadcast desk for this match is not in dispute; only her broadcast
    partners are.
  - "Big Four main event" claim: CONFIRMED, exact wording from S144:
    "This was also the second women's match to main event a WWE pay-per-
    view, and the first to main event one of WWE's 'Big Four' pay-per-
    views." Literal card-order placement (that this was truly the final
    bell of the night) is corroborated circumstantially (S155's recap
    treats it as the show's final segment; S157's own recap references no
    match after it) but not independently re-verified against a raw
    match-by-match running order -- treated as PROBABLE for the literal
    ordering claim, CONFIRMED for the quoted "main event" characterization
    itself.
  - Elimination counts: Michelle McCool's literal total is 5 (4 solo +
    1 shared credit from Vickie Guerrero's 4-way group elimination) --
    NOT "5 solo," a distinction some secondary sources blur. Nia Jax's
    literal total is 4 (all solo) -- some secondary sources claim "5,"
    contradicted by a literal walk-through of S144/S152's own table; that
    higher figure is treated as an error in those secondary sources, not
    logged as a genuine conflicting data point of equal weight.
  - HOF status was checked individually for all 9 returning legends as of
    BOTH January 2018 (was_hof_member_at_time) and today, 2026-09-20
    (wrestlers.csv:hall_of_fame_year, which tracks eventual/ever-inducted
    status, matching this database's existing convention -- e.g. Goldberg's
    RR2017M row). Only Lita, Jacqueline, Beth Phoenix and Trish Stratus
    were already Hall of Famers as of the event date; Michelle McCool,
    Torrie Wilson and Molly Holly have SINCE been inducted (2025, 2019 and
    2021 respectively -- all well after this event); Kelly Kelly and
    Vickie Guerrero have never been inducted in her own right (Vickie
    accepted her late husband Eddie Guerrero's posthumous induction in
    2006 on his behalf -- that is his induction, not hers, per S160).

WHAT'S ACTUALLY KNOWN THIS YEAR: entry order and eliminator credit CONFIRMED
for all 30 entrants/29 eliminations (including both group eliminations).
Event-level facts (date, venue, winner's reward, Rousey/Asuka controversy)
CONFIRMED via 2+ sources. Commentary team is CONFLICTING (see above).
Global match-clock timing (elimination_clock_time) left UNKNOWN throughout,
matching this database's established precedent for externally-researched
years -- individual ring_time (survival duration) IS populated directly
from sources.
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
EVENT_ID = "RR2018W"

# ---------------------------------------------------------------------------
# SOURCES (new this pass; S144/S148/S149 reused from build_2018_men.py)
# ---------------------------------------------------------------------------
sources = [
    ("S152", "WWE.com, official 'Full first-ever Women's Royal Rumble Match statistics' page", "official_wwe", "https://www.wwe.com/shows/royalrumble/2018/article/2018-first-ever-womens-royal-rumble-statistics-entrants-eliminations", 1, "WWE / official sources", "2026-09-20",
     "Official per-wrestler eliminated-by/time table for all 30 entrants, including both group eliminations. "
     "Agrees exactly with S144 on entry order and eliminator/order credit -- an internal arithmetic self-"
     "consistency check (literally walking the 29-row table) confirms the per-wrestler elimination totals match "
     "what both this source and S144 separately report, including specifically re-verifying Nia Jax (4, not 5) "
     "and Michelle McCool (5 total: 4 solo + 1 shared) against secondary sources that overstate these -- see "
     "script docstring."),
    ("S153", "WWE.com, 'Alicia Fox injured, out of Royal Rumble Match and Mixed Match Challenge' article", "official_wwe", "https://www.wwe.com/shows/royalrumble/article/alicia-fox-injured-out-of-royal-rumble-match-and-mixed-match-challenge", 1, "WWE / official sources", "2026-09-20",
     "Official, dated Jan 28 2018: confirms Alicia Fox's original scheduling, her broken-tailbone injury, and her "
     "removal from this match -- corroborated by Wikipedia (S144) stating Kairi Sane replaced her as an entrant."),
    ("S154", "WWE.com, 'Stephanie McMahon to join commentary for Women's Royal Rumble Match this Sunday' article", "official_wwe", "https://www.wwe.com/shows/royalrumble/article/stephanie-mcmahon-to-join-commentary-womens-royal-rumble", 1, "WWE / official sources", "2026-09-20",
     "Independent confirmation of Stephanie McMahon's commentary assignment specifically for this match -- one of "
     "3 sources supporting the Cole/Graves/McMahon commentary lineup over a conflicting WWE.com article (S149) "
     "-- see F373."),
    ("S155", "Sports Illustrated, 'Ronda Rousey's WWE Debut and Other Takeaways From Royal Rumble 2018' (Justin Barrasso)", "contemporary_publication", "https://www.si.com/wrestling/2018/01/29/royal-rumble-2018-wwe-ronda-rousey", 9, "Contemporary wrestling publication", "2026-09-20",
     "Contemporary (next-day) criticism that Ronda Rousey's surprise post-match appearance overshadowed Asuka's "
     "win, and that she was not able to announce her WrestleMania 34 opponent choice on-air. Direct quote used in "
     "notable_moments -- see NM."),
    ("S156", "FanSided, 'Why the Ronda Rousey segment at WWE Royal Rumble bothered me' (Luke Norris)", "contemporary_publication", "https://fansided.com/2018/01/29/wwe-royal-rumble-2018-why-ronda-rousey-segment-bothered-me/", 9, "Contemporary wrestling publication", "2026-09-20",
     "2nd independent contemporary source corroborating S155's criticism of the Rousey/Asuka finish -- makes this "
     "a CONFIRMED (2-source) contemporary controversy rather than a single writer's opinion."),
    ("S157", "WWE.com, results recap page ('Asuka won the 30-Woman Royal Rumble Match; Ronda Rousey crashed post-match celebration')", "official_wwe", "https://www.wwe.com/shows/royalrumble/2018", 1, "WWE / official sources", "2026-09-20",
     "Official recap confirming the winner, the Rousey post-match appearance, and its own framing (via headline) "
     "that this was the show's final segment."),
    ("S158", "WWE.com, individual WWE Hall of Fame induction articles (Jacqueline 2016; Molly Holly 2021; Michelle McCool 2025)", "official_wwe", "", 1, "WWE / official sources", "2026-09-20",
     "Direct primary-source confirmation of individual HOF induction years, checked live as part of this build per "
     "Shane's standing HOF-at-build-time process."),
    ("S159", "Wikipedia, 'WWE Hall of Fame' master inductee list (all classes)", "reference_site", "https://en.wikipedia.org/wiki/WWE_Hall_of_Fame", 10, "Wikipedia/reference sites", "2026-09-20",
     "Cross-check of induction years for Lita (2014), Trish Stratus (2013), Beth Phoenix (2017), Jacqueline "
     "(2016), Michelle McCool (2025), Torrie Wilson (2019), Molly Holly (2021); confirms Kelly Kelly and Vickie "
     "Guerrero absent from every class list through the announced 2026 class."),
    ("S160", "notinhalloffame.com, Vickie Guerrero profile", "other_stats_site", "https://www.notinhalloffame.com/wwe/2678-84-vickie-guerrero", 12, "Other reputable site", "2026-09-20",
     "Secondary confirmation that Vickie Guerrero has never been inducted into the WWE Hall of Fame in her own "
     "right -- her late husband Eddie Guerrero's 2006 posthumous induction is a separate honor, not hers."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# ENTRY ORDER (CONFIRMED, S144+S152+S148 agree exactly)
# ---------------------------------------------------------------------------
all_names = [
    "Sasha Banks", "Becky Lynch", "Sarah Logan", "Mandy Rose", "Lita", "Kairi Sane", "Tamina", "Dana Brooke",
    "Torrie Wilson", "Sonya Deville", "Liv Morgan", "Molly Holly", "Lana", "Michelle McCool", "Ruby Riott",
    "Vickie Guerrero", "Carmella", "Natalya", "Kelly Kelly", "Naomi", "Jacqueline", "Nia Jax", "Ember Moon",
    "Beth Phoenix", "Asuka", "Mickie James", "Nikki Bella", "Brie Bella", "Bayley", "Trish Stratus",
]
assert len(all_names) == 30
ENTRY_NUMBERS = {name: i + 1 for i, name in enumerate(all_names)}
assert ENTRY_NUMBERS["Asuka"] == 25 and ENTRY_NUMBERS["Kairi Sane"] == 6

# Individual survival ("ring") times, as directly stated by S144/S152 (agree exactly).
survival = {
    "Sasha Banks": "54:46", "Becky Lynch": "30:54", "Sarah Logan": "16:30", "Mandy Rose": "3:52", "Lita": "5:51",
    "Kairi Sane": "4:49", "Tamina": "1:34", "Dana Brooke": "2:59", "Torrie Wilson": "3:04", "Sonya Deville": "6:41",
    "Liv Morgan": "5:12", "Molly Holly": "4:04", "Lana": "2:54", "Michelle McCool": "8:38", "Ruby Riott": "11:32",
    "Vickie Guerrero": "0:57", "Carmella": "18:45", "Natalya": "25:34", "Kelly Kelly": "5:02", "Naomi": "6:49",
    "Jacqueline": "1:52", "Nia Jax": "17:56", "Ember Moon": "6:14", "Beth Phoenix": "2:22", "Asuka": "19:41",
    "Mickie James": "8:24", "Nikki Bella": "16:30", "Brie Bella": "11:58", "Bayley": "5:04", "Trish Stratus": "5:36",
}
assert set(survival) == set(all_names)

# Elimination order (1st-29th).
ELIM_ORDER = [
    "Mandy Rose", "Tamina", "Lita", "Kairi Sane", "Dana Brooke", "Torrie Wilson", "Sarah Logan", "Sonya Deville",
    "Liv Morgan", "Molly Holly", "Lana", "Vickie Guerrero", "Michelle McCool", "Becky Lynch", "Jacqueline",
    "Kelly Kelly", "Ruby Riott", "Naomi", "Beth Phoenix", "Ember Moon", "Carmella", "Mickie James", "Nia Jax",
    "Bayley", "Natalya", "Trish Stratus", "Sasha Banks", "Brie Bella", "Nikki Bella",
]
assert len(ELIM_ORDER) == 29
elim_number = {name: i + 1 for i, name in enumerate(ELIM_ORDER)}

FINAL_TWO = {"Asuka", "Nikki Bella"}
FINAL_THREE = {"Asuka", "Nikki Bella", "Brie Bella"}
FINAL_FOUR = {"Asuka", "Nikki Bella", "Brie Bella", "Sasha Banks"}

# name -> (eliminator names, is_shared, notes)
ELIMINATORS = {
    "Mandy Rose": (["Lita"], False, ""),
    "Tamina": (["Lita"], False, ""),
    "Lita": (["Becky Lynch"], False, ""),
    "Kairi Sane": (["Dana Brooke"], False, "Sane entered as a late replacement for Alicia Fox, who was pulled from the match after suffering a broken tailbone shortly before the event."),
    "Dana Brooke": (["Torrie Wilson"], False, ""),
    "Torrie Wilson": (["Sonya Deville"], False, ""),
    "Sarah Logan": (["Molly Holly"], False, ""),
    "Sonya Deville": (["Michelle McCool"], False, ""),
    "Liv Morgan": (["Michelle McCool"], False, ""),
    "Molly Holly": (["Michelle McCool"], False, ""),
    "Lana": (["Michelle McCool"], False, ""),
    "Vickie Guerrero": (["Becky Lynch", "Michelle McCool", "Ruby Riott", "Sasha Banks"], True, "4-way group elimination, a comedic spot -- S144 and S152 agree on all 4 names."),
    "Michelle McCool": (["Natalya"], False, "McCool's 4 solo eliminations (Sonya Deville, Liv Morgan, Molly Holly, Lana) plus her shared credit in Vickie Guerrero's group elimination gave her the match's highest total credited-elimination count (5) -- see event historical_significance."),
    "Becky Lynch": (["Ruby Riott"], False, ""),
    "Jacqueline": (["Nia Jax"], False, ""),
    "Kelly Kelly": (["Nia Jax"], False, ""),
    "Ruby Riott": (["Nia Jax"], False, ""),
    "Naomi": (["Nia Jax"], False, ""),
    "Beth Phoenix": (["Natalya"], False, ""),
    "Ember Moon": (["Asuka"], False, ""),
    "Carmella": (["Nikki Bella"], False, ""),
    "Mickie James": (["Trish Stratus"], False, ""),
    "Nia Jax": (["Asuka", "Bayley", "Brie Bella", "Natalya", "Nikki Bella", "Trish Stratus"], True, "6-way group elimination -- S144 and S152 agree on the identical set of 6 names (listed order differs slightly between the two, the underlying set does not). A literal walk-through confirms Nia Jax's own total is 4 solo eliminations (Jacqueline, Kelly Kelly, Ruby Riott, Naomi) -- she was the VICTIM of this group elimination, not a contributor to one; some secondary sources incorrectly claim she had 5 eliminations, contradicted by this table."),
    "Bayley": (["Sasha Banks"], False, ""),
    "Natalya": (["Trish Stratus"], False, ""),
    "Trish Stratus": (["Sasha Banks"], False, ""),
    "Sasha Banks": (["Brie Bella", "Nikki Bella"], True, "Shared elimination credit by the Bella Twins -- S144 and S152 agree."),
    "Brie Bella": (["Nikki Bella"], False, ""),
    "Nikki Bella": (["Asuka"], False, "The final elimination of the match -- Asuka's winning elimination."),
}
assert set(ELIMINATORS) == set(ELIM_ORDER)

# ---------------------------------------------------------------------------
# WRESTLERS -- new to this database this pass (29 of 30; Beth Phoenix is
# reused from her existing RR2010 record). Bios researched live; WWE Hall of
# Fame and deceased status checked for all 29 as part of this build, per
# Shane's standing process. Real names/DOB/birthplace for the returning
# legends (Lita, Jacqueline, Trish Stratus) were independently web-fetched
# this pass rather than assumed from general knowledge, consistent with
# this database's "never invent data" rule.
# ---------------------------------------------------------------------------
# (ring_name, real_name, real_name_status, gender, dob, dob_status, deceased_date,
#  birthplace, birthplace_status, nationality, debut_year_company, hall_of_fame_year,
#  aliases_ring_names, wrestling_style, notes, source_ids)
new_wrestlers = [
    ("Sasha Banks", "Mercedes Justine Kaestner-Varnado", "PROBABLE", "F", "1992-01-26", "PROBABLE", "", "Fairfield, California, U.S.", "PROBABLE", "", "", "",
     "Mercedes Mone", "", "Entered #1 (the opening entrant), the match's longest individual survival time (54:46). Eliminated 2 solo (Bayley, Trish Stratus) plus a shared credit in Vickie Guerrero's group elimination, before being eliminated by the Bella Twins. Not a WWE Hall of Famer as of this build.", "S022;S144;S152"),
    ("Becky Lynch", "Rebecca Quin", "PROBABLE", "F", "1987-01-30", "PROBABLE", "", "Limerick, Ireland", "PROBABLE", "Irish", "", "",
     "", "", "Rumble debut, entered #2. Survived 30:54, eliminated by Ruby Riott. Not a WWE Hall of Famer as of this build.", "S022;S144"),
    ("Sarah Logan", "Sarah Bridges", "PROBABLE", "F", "1993-09-10", "PROBABLE", "", "Louisville, Kentucky, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #3. Survived 16:30, eliminated by Molly Holly. Not a WWE Hall of Famer as of this build.", "S022;S144"),
    ("Mandy Rose", "Amanda Rose Saccomanno", "PROBABLE", "F", "1990-07-18", "PROBABLE", "", "Westchester County, New York, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #4. Survived 3:52, the first elimination of the match, by Lita. Not a WWE Hall of Famer as of this build.", "S022;S144"),
    ("Lita", "Amy Christine Dumas", "PROBABLE", "F", "1975-04-14", "PROBABLE", "", "Fort Lauderdale, Florida, U.S.", "PROBABLE", "", "", "2014",
     "", "", "Entered #5 as a returning WWE Hall of Famer (inducted 2014, already a Hall of Famer at the time of this event). Survived 5:51, eliminating 2 (Mandy Rose, Tamina) before being eliminated by Becky Lynch.", "S022;S144"),
    ("Kairi Sane", "Kaori Housako", "PROBABLE", "F", "1988-09-23", "PROBABLE", "", "Hikari, Yamaguchi Prefecture, Japan", "PROBABLE", "Japanese", "", "",
     "", "", "Rumble debut, entered #6 as a late replacement for the injured Alicia Fox (broken tailbone). Survived 4:49, eliminated by Dana Brooke. Not a WWE Hall of Famer as of this build.", "S022;S144;S153"),
    ("Tamina", "Sarona Snuka", "UNCERTAIN", "F", "1978-01-10", "PROBABLE", "", "Vancouver, Washington, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #7. Survived 1:34, eliminated by Lita. Real name recorded as 'Sarona Snuka' -- Wikipedia gives a longer legal-name string ('Sarona Moana Marie Reiher Snuka-Polamalu') single-sourced and uncorroborated this pass; the core surname/given-name is cross-confirmed via IMDb. Not a WWE Hall of Famer as of this build.", "S022"),
    ("Dana Brooke", "Ashley Mae Sebera", "PROBABLE", "F", "1988-11-29", "PROBABLE", "", "Seven Hills, Ohio, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #8. Survived 2:59, eliminating Kairi Sane before being eliminated by Torrie Wilson. Not a WWE Hall of Famer as of this build.", "S022;S144"),
    ("Torrie Wilson", "Torrie Anne Wilson", "PROBABLE", "F", "1975-07-24", "PROBABLE", "", "Boise, Idaho, U.S.", "PROBABLE", "", "", "2019",
     "", "", "Entered #9 as a returning WWE alumna -- NOT yet a Hall of Famer at the time of this event (inducted 2019, over a year later). Survived 3:04, eliminating Dana Brooke before being eliminated by Sonya Deville.", "S022;S158;S159"),
    ("Sonya Deville", "Daria Rae Berenato", "PROBABLE", "F", "1993-09-24", "PROBABLE", "", "Shamong Township, New Jersey, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #10. Survived 6:41, eliminating Torrie Wilson before being eliminated by Michelle McCool. Not a WWE Hall of Famer as of this build.", "S022;S144"),
    ("Liv Morgan", "Gionna Jene Daddio", "PROBABLE", "F", "1994-06-08", "PROBABLE", "", "Morristown, New Jersey, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #11. Survived 5:12, eliminated by Michelle McCool. Not a WWE Hall of Famer as of this build.", "S022;S144"),
    ("Molly Holly", "Nora Kristina Greenwald", "PROBABLE", "F", "1977-09-07", "PROBABLE", "", "Forest Lake, Minnesota, U.S.", "PROBABLE", "", "", "2021",
     "", "", "Entered #12 as a returning WWE alumna -- NOT yet a Hall of Famer at the time of this event (inducted 2021, over 3 years later). Survived 4:04, eliminating Sarah Logan before being eliminated by Michelle McCool.", "S022;S158;S159"),
    ("Lana", "Catherine Joy Perry", "PROBABLE", "F", "1985-03-24", "PROBABLE", "", "Gainesville, Florida, U.S.", "PROBABLE", "", "", "",
     "CJ Perry", "", "Rumble debut, entered #13. Survived 2:54, eliminated by Michelle McCool. Not a WWE Hall of Famer as of this build.", "S022;S144"),
    ("Michelle McCool", "Michelle Leigh McCool", "PROBABLE", "F", "1980-01-25", "PROBABLE", "", "Palatka, Florida, U.S.", "PROBABLE", "", "", "2025",
     "", "", "Entered #14 as a returning WWE alumna -- NOT yet a Hall of Famer at the time of this event (inducted 2025, 7 years later, by her husband The Undertaker). Survived 8:38, and had this match's highest total credited-elimination count (5: 4 solo -- Sonya Deville, Liv Morgan, Molly Holly, Lana -- plus a shared credit for Vickie Guerrero) before being eliminated by Natalya.", "S022;S158;S159"),
    ("Ruby Riott", "Dori Elizabeth Prange", "PROBABLE", "F", "1991-01-09", "PROBABLE", "", "Edwardsburg, Michigan, U.S.", "PROBABLE", "", "", "",
     "Ruby Soho", "", "Rumble debut, entered #15. Survived 11:32, eliminating Becky Lynch (plus a shared credit for Vickie Guerrero) before being eliminated by Nia Jax. Not a WWE Hall of Famer as of this build.", "S022;S144"),
    ("Vickie Guerrero", "Vickie Lynn Lara", "PROBABLE", "F", "1968-04-16", "PROBABLE", "", "El Paso, Texas, U.S.", "PROBABLE", "", "", "",
     "", "", "Entered #16 as a returning WWE alumna, a comedic spot. Survived just 0:57, eliminated in a 4-way group elimination (Becky Lynch, Michelle McCool, Ruby Riott, Sasha Banks). Not a WWE Hall of Famer in her own right as of this build -- her late husband Eddie Guerrero's posthumous 2006 induction is a separate honor, not hers; see F374.", "S022;S160"),
    ("Carmella", "Leah Van Dale", "PROBABLE", "F", "1987-10-23", "PROBABLE", "", "Spencer, Massachusetts, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #17. Survived 18:45, eliminated by Nikki Bella. Not a WWE Hall of Famer as of this build.", "S022;S144"),
    ("Natalya", "Natalie Katherine Neidhart", "PROBABLE", "F", "1982-05-27", "PROBABLE", "", "Calgary, Alberta, Canada", "PROBABLE", "Canadian", "", "",
     "", "", "Rumble debut, entered #18. Survived 25:34, eliminating 2 solo (Michelle McCool, Beth Phoenix) plus a shared credit in Nia Jax's group elimination, before being eliminated by Trish Stratus. Not a WWE Hall of Famer as of this build.", "S022;S144"),
    ("Kelly Kelly", "Barbara Jean Blank", "PROBABLE", "F", "1987-01-15", "PROBABLE", "", "Jacksonville, Florida, U.S.", "PROBABLE", "", "", "",
     "", "", "Entered #19 as a returning WWE alumna. Survived 5:02, eliminated by Nia Jax. Never inducted into the WWE Hall of Fame as of this build (2026-09-20).", "S022;S159"),
    ("Naomi", "Trinity LaShawn McCray Fatu", "PROBABLE", "F", "1987-11-30", "PROBABLE", "", "Sanford, Florida, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #20. Survived 6:49, eliminated by Nia Jax. Not a WWE Hall of Famer as of this build.", "S022;S144"),
    ("Jacqueline", "Jacqueline DeLois Moore", "CONFIRMED", "F", "1964-01-06", "CONFIRMED", "", "Dallas, Texas, U.S.", "CONFIRMED", "", "", "2016",
     "", "", "Entered #21 as a returning WWE Hall of Famer (inducted 2016, already a Hall of Famer at the time of this event -- WWE's first Black woman inducted into the Hall of Fame). Survived 1:52, eliminated by Nia Jax.", "S022;S158;S159"),
    ("Nia Jax", "Savelina Fanene", "PROBABLE", "F", "1984-05-29", "PROBABLE", "", "Sydney, New South Wales, Australia", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #22. Eliminated 4 solo (Jacqueline, Kelly Kelly, Ruby Riott, Naomi) -- tied for the match's high eliminator count -- before being eliminated herself in a 6-way group elimination after 17:56. Not a WWE Hall of Famer as of this build.", "S022;S144;S152"),
    ("Ember Moon", "Adrienne Reese", "PROBABLE", "F", "1988-08-31", "PROBABLE", "", "Garland, Texas, U.S.", "PROBABLE", "", "", "",
     "Athena", "", "Rumble debut, entered #23. Survived 6:14, eliminated by Asuka. Now wrestles as 'Athena' elsewhere. Not a WWE Hall of Famer as of this build.", "S022;S144"),
    ("Asuka", "Kanako Urai", "PROBABLE", "F", "1981-09-26", "PROBABLE", "", "Osaka, Japan", "PROBABLE", "Japanese", "", "",
     "", "", "Entered #25 and WON, eliminating 2 solo (Ember Moon, Nikki Bella -- the winning elimination) plus a shared credit in Nia Jax's group elimination. Chose a title match at WrestleMania 34; her post-match moment was overshadowed by Ronda Rousey's surprise appearance -- see notable_moments. Not a WWE Hall of Famer as of this build.", "S022;S144;S152"),
    ("Mickie James", "Mickie Laree James", "PROBABLE", "F", "1979-08-31", "PROBABLE", "", "Richmond, Virginia, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #26. Survived 8:24, eliminated by Trish Stratus. Not a WWE Hall of Famer as of this build (inducted into the separate TNA/Impact Hall of Fame in 2025 -- a different organization, not conflated with WWE HOF status here).", "S022;S144"),
    ("Nikki Bella", "Stephanie Nicole Garcia-Colace", "PROBABLE", "F", "1983-11-21", "PROBABLE", "", "San Diego, California, U.S.", "PROBABLE", "", "", "2020",
     "", "", "Entered #27 as a returning WWE alumna -- NOT yet a Hall of Famer at the time of this event (inducted as one of 'The Bella Twins,' Class of 2020, ceremony held April 2021 -- both well after this event). Survived 16:30, eliminating 2 solo (Carmella, Brie Bella) plus a shared credit in Nia Jax's group elimination, before eliminating Sasha Banks (with Brie Bella) and making the final two -- runner-up to Asuka.", "S022;S158;S159"),
    ("Brie Bella", "Brianna Monique Garcia-Colace", "PROBABLE", "F", "1983-11-21", "PROBABLE", "", "San Diego, California, U.S.", "PROBABLE", "", "", "2020",
     "", "", "Entered #28 as a returning WWE alumna -- NOT yet a Hall of Famer at the time of this event (inducted as one of 'The Bella Twins,' Class of 2020, ceremony held April 2021 -- both well after this event). Survived 11:58, part of the shared elimination of Sasha Banks (with Nikki Bella) and a shared credit in Nia Jax's group elimination, before being eliminated by her twin sister Nikki.", "S022;S158;S159"),
    ("Bayley", "Pamela Rose Martinez", "PROBABLE", "F", "1989-06-15", "PROBABLE", "", "San Jose, California, U.S.", "PROBABLE", "", "", "",
     "", "", "Rumble debut, entered #29. Survived 5:04, part of the 6-way group elimination of Nia Jax, before being eliminated by Sasha Banks. Not a WWE Hall of Famer as of this build.", "S022;S144"),
    ("Trish Stratus", "Patricia Anne Stratigeas", "PROBABLE", "F", "1975-12-18", "PROBABLE", "", "Toronto, Ontario, Canada", "PROBABLE", "Canadian", "", "2013",
     "", "", "Entered #30 (the final entrant) as a returning WWE Hall of Famer (inducted 2013, already a Hall of Famer at the time of this event). Survived 5:36, eliminating 2 solo (Mickie James, Natalya) plus a shared credit in Nia Jax's group elimination, before being eliminated by Sasha Banks.", "S022;S144"),
]

reused = {
    "Beth Phoenix": "beth-phoenix",
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
# Returning alumnae/legends (not full-time WWE roster members in Jan 2018)
LEGENDS = {"Lita", "Jacqueline", "Beth Phoenix", "Trish Stratus", "Michelle McCool", "Torrie Wilson",
           "Molly Holly", "Kelly Kelly", "Vickie Guerrero", "Nikki Bella", "Brie Bella"}
# Already WWE Hall of Famers as of the Jan 28, 2018 event date specifically
HOF_AT_EVENT_TIME = {"Lita", "Jacqueline", "Beth Phoenix", "Trish Stratus"}

entrant_rows = []
elim_rows = []
for name in all_names:
    wid = wrestler_ids[name]
    is_winner = (name == "Asuka")
    entry = ENTRY_NUMBERS[name]
    ring_time = survival[name]
    ring_time_s = mmss_to_seconds(ring_time)

    elim_by, is_shared, extra_note = ELIMINATORS.get(name, ([], False, ""))

    notes_parts = [extra_note] if extra_note else []
    if name == "Asuka":
        notes_parts.append("Entered #25 and won, eliminating Nikki Bella for the winning elimination -- the first "
                            "winner of the first-ever Women's Royal Rumble match. Her post-match celebration and "
                            "WrestleMania 34 opponent announcement was interrupted by Ronda Rousey's surprise "
                            "full-time WWE signing reveal, drawing contemporary criticism -- see notable_moments.")

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
            "simultaneous_group_id": ("grp-vickie-guerrero" if name == "Vickie Guerrero" else "grp-nia-jax" if name == "Nia Jax" else "grp-sasha-banks" if name == "Sasha Banks" else ""),
            "data_quality_status": "CONFIRMED",
            "source_ids": "S144;S152",
            "notes": "",
        })

    er = {
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": "CONFIRMED",
        "ring_name_at_time": name, "name_displayed_at_event": name,
        "prior_rumble_appearances_count": "", "rumble_appearance_no": "",
        "is_first_rumble_appearance": "TRUE" if name in NEW_NAMES else "", "is_company_debut": "UNKNOWN",
        "previous_rumble_year": "", "previous_rumble_result": "", "previous_rumble_elimination_no": "",
        "is_rumble_debut": "TRUE" if name in NEW_NAMES and name not in LEGENDS else "FALSE",
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
        "is_runner_up": "TRUE" if name == "Nikki Bella" else "FALSE",
        "is_final_two": "TRUE" if name in FINAL_TWO else "FALSE",
        "is_final_three": "TRUE" if name in FINAL_THREE else "FALSE",
        "is_final_four": "TRUE" if name in FINAL_FOUR else "FALSE",
        "surprise_entrant": "FALSE",
        "legend_returning": "TRUE" if name in LEGENDS else "FALSE",
        "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "TRUE" if name in LEGENDS else "FALSE",
        "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "TRUE" if name in HOF_AT_EVENT_TIME else "FALSE",
        "data_quality_status": "CONFIRMED",
        "source_ids": "S144;S152",
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
    ("F373", EVENT_ID, "events", EVENT_ID, "commentary_team", "conflicting_sources",
     "The Women's Royal Rumble commentary team is CONFLICTING between sources. S144 (Wikipedia infobox), S148 "
     "(Cagematch.net, in a combined show-wide roster) and S154 (a WWE.com article specifically dedicated to "
     "announcing her booth assignment) all agree the match was called by Michael Cole, Corey Graves and Stephanie "
     "McMahon. But S149 (a separate WWE.com 'Announcer lineup for Royal Rumble and Royal Rumble Kickoff' article) "
     "instead lists Renee Young, Beth Phoenix, Tom Phillips and Corey Graves, with no McMahon. This script uses "
     "the Cole/Graves/McMahon version in the structured commentary_team field, per the preponderance of evidence "
     "(3 independent sources, one dedicated specifically to that news, corroborated by multiple contemporary "
     "outlets covering the same story) -- but the conflict is not resolved to single-source certainty; a targeted "
     "check against a full post-event recap or the DVD/streaming commentary track would settle it. Stephanie "
     "McMahon's presence at the broadcast desk for this match is CONFIRMED regardless; only her broadcast "
     "partners are in dispute.",
     "S144;S148;S149;S154", "open", "2026-09-20"),
    ("F374", EVENT_ID, "wrestlers", "vickie-guerrero", "hall_of_fame_year", "unverified",
     "Vickie Guerrero has never been inducted into the WWE Hall of Fame in her own right, per S159 (the master "
     "inductee list, on which she does not appear) and S160 (a dedicated 'not in Hall of Fame' tracker site). Her "
     "late husband Eddie Guerrero was posthumously inducted in 2006, an honor she accepted on his behalf -- that "
     "is his induction, not hers, and is not recorded on her wrestlers.csv row per this database's convention of "
     "tracking each wrestler's own individual HOF status only.",
     "S159;S160", "resolved", "2026-09-20"),
    ("F375", EVENT_ID, "wrestlers", "tamina", "real_name", "conflicting_sources",
     "Tamina's full legal name is single-sourced this pass (Wikipedia gives 'Sarona Moana Marie Reiher "
     "Snuka-Polamalu') and not independently cross-checked beyond the core 'Sarona Snuka' (confirmed via IMDb) -- "
     "recorded at UNCERTAIN status rather than PROBABLE/CONFIRMED given the length and specificity of the "
     "uncorroborated middle/surname elements.",
     "S022", "open", "2026-09-20"),
    ("F376", EVENT_ID, "wrestlers", "michelle-mccool;torrie-wilson;molly-holly;kelly-kelly;vickie-guerrero;nikki-bella;brie-bella;finn-balor", "hall_of_fame_year", "corrected",
     "Continuing the process established at RR2017M/RR2018M: WWE Hall of Fame status was checked for all 29 "
     "wrestlers new to this database this pass, as part of this build. Of the 9 returning legends/alumnae in this "
     "match's field, only 4 (Lita, Jacqueline, Beth Phoenix, Trish Stratus) were already Hall of Famers as of the "
     "event date (Jan 28, 2018) -- their was_hof_member_at_time is TRUE, everyone else's is FALSE. Michelle "
     "McCool, Torrie Wilson and Molly Holly have SINCE been inducted (2025, 2019, 2021 respectively -- all well "
     "after this event) and their wrestlers.csv hall_of_fame_year fields record those eventual years, matching "
     "this database's existing convention (e.g. Goldberg's RR2017M row records his 2018 induction even though it "
     "postdated that event). Nikki Bella and Brie Bella were inducted together as 'The Bella Twins,' Class of "
     "2020 (ceremony delayed to April 2021) -- also after this event. Kelly Kelly and Vickie Guerrero have never "
     "been inducted in their own right. None of the 29 new wrestlers are deceased.",
     "S022;S158;S159;S160", "resolved", "2026-09-20"),
    ("F377", EVENT_ID, "entrances;moves", "*", "n/a", "out_of_scope_no_tool",
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
        "moment_id": "NM057", "event_id": EVENT_ID, "wrestler_ids_involved": "asuka",
        "category": "milestone_first",
        "title": "Asuka wins the first-ever Women's Royal Rumble match",
        "description": "Asuka entered #25 and won by eliminating Nikki Bella, becoming the first winner in the history of the Women's Royal Rumble match -- the second women's match ever to main event a WWE pay-per-view, and the first to main event one of WWE's 'Big Four' shows (direct Wikipedia characterization).",
        "data_quality_status": "CONFIRMED", "source_ids": "S144;S152",
        "notes": "",
    },
    {
        "moment_id": "NM058", "event_id": EVENT_ID, "wrestler_ids_involved": "",
        "category": "controversy",
        "title": "Ronda Rousey's surprise debut overshadowed Asuka's win, per contemporary criticism",
        "description": "Immediately after Asuka's win, Ronda Rousey's music hit and she came to the ring to confirm her full-time WWE signing -- cutting into what should have been Asuka's championship-opponent-selection moment; Asuka reportedly declined to shake Rousey's hand. Sports Illustrated's Justin Barrasso wrote the next day: \"the show should have finished by celebrating the winner of the women's Rumble. Instead, we were treated to the Ronda Rousey show,\" adding the finish \"ended with her as an afterthought.\" A second outlet, FanSided, made a similar argument the same day. This is a genuine, contemporary (within-24-hours) point of criticism from 2 independent sources.",
        "data_quality_status": "CONFIRMED", "source_ids": "S155;S156;S157",
        "notes": "",
    },
    {
        "moment_id": "NM059", "event_id": EVENT_ID, "wrestler_ids_involved": "",
        "category": "notable_absence_or_substitution",
        "title": "Reigning champions Alexa Bliss and Charlotte Flair were not entrants",
        "description": "The reigning Raw and SmackDown Women's Champions, Alexa Bliss and Charlotte Flair, did not compete in this Rumble despite holding the two women's titles at the time -- both came to the ring only after the match concluded to confront Asuka about her upcoming title choice.",
        "data_quality_status": "CONFIRMED", "source_ids": "S144",
        "notes": "",
    },
    {
        "moment_id": "NM060", "event_id": EVENT_ID, "wrestler_ids_involved": "alicia-fox-not-tracked;kairi-sane",
        "category": "notable_absence_or_substitution",
        "title": "Kairi Sane replaced the injured Alicia Fox",
        "description": "Alicia Fox was originally scheduled to compete but suffered a broken tailbone shortly before the event and was pulled from both this match and the Mixed Match Challenge; Kairi Sane took her place, entering #6.",
        "data_quality_status": "CONFIRMED", "source_ids": "S144;S153",
        "notes": "Alicia Fox is referenced by name but is not herself a wrestler_id in this database, since she was pulled before competing.",
    },
    {
        "moment_id": "NM061", "event_id": EVENT_ID, "wrestler_ids_involved": "nia-jax;michelle-mccool",
        "category": "record",
        "title": "Michelle McCool led all eliminators with 5 credited eliminations; Nia Jax's literal total is 4, not 5",
        "description": "A literal walk-through of the official elimination table gives Michelle McCool the match's highest total credited-elimination count at 5 (4 solo -- Sonya Deville, Liv Morgan, Molly Holly, Lana -- plus a shared credit for Vickie Guerrero's group elimination). Nia Jax, tied for the most SOLO eliminations at 4 (Jacqueline, Kelly Kelly, Ruby Riott, Naomi), had zero group-elimination credits as an eliminator -- she was the victim, not a contributor, of the match's 6-way group elimination. Some secondary sources claim Nia Jax had 5 eliminations; this is contradicted by a literal, independently-verified walk-through of the official WWE.com/Wikipedia table and is treated as an error in those sources.",
        "data_quality_status": "CONFIRMED", "source_ids": "S144;S152",
        "notes": "",
    },
    {
        "moment_id": "NM062", "event_id": EVENT_ID, "wrestler_ids_involved": "nia-jax;asuka;bayley;brie-bella;natalya;nikki-bella;trish-stratus",
        "category": "other",
        "title": "Nia Jax eliminated in a 6-way group elimination",
        "description": "Nia Jax, who had herself eliminated 4 opponents, was eliminated in a single spot by six wrestlers acting together -- Asuka, Bayley, Brie Bella, Natalya, Nikki Bella and Trish Stratus -- after 17:56.",
        "data_quality_status": "CONFIRMED", "source_ids": "S144;S152",
        "notes": "",
    },
    {
        "moment_id": "NM063", "event_id": EVENT_ID, "wrestler_ids_involved": "sasha-banks;nikki-bella;brie-bella",
        "category": "other",
        "title": "Sasha Banks eliminated by the Bella Twins after the match's longest individual survival time",
        "description": "Sasha Banks, the opening (#1) entrant, survived 54:46 -- the longest individual time of the match -- before being eliminated in a shared spot by Nikki Bella and Brie Bella.",
        "data_quality_status": "CONFIRMED", "source_ids": "S144;S152",
        "notes": "",
    },
    {
        "moment_id": "NM064", "event_id": EVENT_ID, "wrestler_ids_involved": "lita;jacqueline;beth-phoenix;trish-stratus;michelle-mccool;torrie-wilson;molly-holly;kelly-kelly;vickie-guerrero",
        "category": "other",
        "title": "Nine returning WWE alumnae brought back for the historic first edition",
        "description": "Lita, Jacqueline, Beth Phoenix, Trish Stratus, Michelle McCool, Torrie Wilson, Molly Holly, Kelly Kelly and Vickie Guerrero all returned for this inaugural match. Of these, only Lita, Jacqueline, Beth Phoenix and Trish Stratus were already WWE Hall of Famers at the time -- McCool, Torrie Wilson and Molly Holly were inducted years later (2025, 2019, 2021), and Kelly Kelly and Vickie Guerrero have never been inducted in their own right.",
        "data_quality_status": "CONFIRMED", "source_ids": "S144;S158;S159;S160",
        "notes": "",
    },
]
with open(os.path.join(DATA_DIR, "notable_moments.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=NOTABLE_MOMENTS_FIELDS)
    for row in nm_rows:
        writer.writerow(row)

flags2 = [
    ("F378", EVENT_ID, "notable_moments", "NM057;NM058;NM059;NM060;NM061;NM062;NM063;NM064", "n/a", "corrected",
     "Added 8 notable_moments.csv rows for this newly-built event: Asuka's historic first win, the Rousey/Asuka "
     "post-match controversy, the absent champions (Bliss/Flair), the Fox/Sane injury replacement, the McCool/Nia "
     "Jax elimination-count correction, the 6-way Nia Jax group elimination, Sasha Banks's match-long survival "
     "time and Bella Twins elimination, and the nine returning alumnae with their individual HOF status noted.",
     "S144;S152;S155;S156;S157;S158;S159;S160", "resolved", "2026-09-20"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags2)

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 2018", "match_name": "Royal Rumble Match",
    "match_type": "Women's", "event_date": "2018-01-28",
    "venue": "Wells Fargo Center", "city_region": "Philadelphia, Pennsylvania", "country": "United States",
    "attendance_official": "", "attendance_reported": 17629,
    "entry_interval_seconds": "", "entrant_count": 30,
    "duration_total": "58:57", "duration_status": "CONFIRMED",
    "winner_id": "asuka", "runner_up_id": "nikki-bella",
    "final_two_ids": "asuka;nikki-bella",
    "final_three_ids": "asuka;nikki-bella;brie-bella",
    "final_four_ids": "asuka;nikki-bella;brie-bella;sasha-banks",
    "first_entrant_id": "sasha-banks", "second_entrant_id": "becky-lynch", "final_entrant_id": "trish-stratus",
    "first_elimination_id": "mandy-rose", "last_elimination_before_winner_id": "nikki-bella",
    "eliminations_count": 29, "eliminators_count": 16,
    "surprise_entrants_count": 0,
    "champions_in_field_count": 0, "hall_of_famers_in_field_count": 4,
    "tag_teams_count": "UNKNOWN", "factions_count": "UNKNOWN",
    "commentary_team": "Michael Cole, Corey Graves, Stephanie McMahon",
    "ring_announcer": "Maria Menounos (special guest ring announcer)",
    "referees": "UNKNOWN",
    "special_rules": "Standard Royal Rumble rules -- the first-ever Women's Royal Rumble match. No title was defended within the match itself; the winner instead earned a title shot at WrestleMania 34.",
    "title_on_the_line": "FALSE",
    "championship_implications": "The winner earned the right to challenge for a women's championship at WrestleMania 34 -- their choice between Raw's Women's Championship (held by Alexa Bliss) or SmackDown's Women's Championship (held by Charlotte Flair), neither of whom competed in this match. Asuka won.",
    "winners_reward": "A women's championship match at WrestleMania 34 -- winner's choice between Raw's Women's Championship and SmackDown's Women's Championship.",
    "historical_significance": (
        "The first-ever Women's Royal Rumble match, won by Asuka (entry #25), eliminating Nikki Bella for the "
        "winning elimination. Per Wikipedia's own characterization, this was 'the second women's match to main "
        "event a WWE pay-per-view, and the first to main event one of WWE's “Big Four” pay-per-views.' "
        "Nine returning WWE alumnae were brought back for the occasion -- Lita, Jacqueline, Beth Phoenix, Trish "
        "Stratus, Michelle McCool, Torrie Wilson, Molly Holly, Kelly Kelly and Vickie Guerrero -- though only the "
        "first four were already WWE Hall of Famers at the time. Michelle McCool led all eliminators with 5 total "
        "credited eliminations (4 solo plus a shared credit); Nia Jax and McCool were tied for the most SOLO "
        "eliminations at 4 apiece, with Nia Jax then eliminated herself in a 6-way group spot (Asuka, Bayley, "
        "Brie Bella, Natalya, Nikki Bella, Trish Stratus). Sasha Banks, the opening entrant, posted the match's "
        "longest individual survival time (54:46) before being eliminated by the Bella Twins. Reigning champions "
        "Alexa Bliss and Charlotte Flair were notably absent as entrants, appearing only after the match to "
        "confront Asuka. Kairi Sane entered as a late replacement for the injured Alicia Fox. Asuka's post-match "
        "celebration was immediately overshadowed by Ronda Rousey's surprise full-time WWE signing reveal, drawing "
        "contemporary criticism from Sports Illustrated and other outlets that the finish sidelined the historic "
        "moment this match represented. Built as a fully separate event/record from RR2018M (the men's Royal "
        "Rumble, held the same night) per Shane's explicit instruction to keep the two matches separate."
    ),
    "notes": (
        "Entry order and eliminator credit CONFIRMED for all 30 entrants via 2+ independent sources each, "
        "including a deliberate literal re-verification of Nia Jax's and Michelle McCool's individual elimination "
        "counts against secondary sources that overstate them -- see F376/NM061. Commentary team is CONFLICTING "
        "between sources -- see F373. Global match-clock timing (elimination_clock_time) left UNKNOWN throughout. "
        "WWE Hall of Fame status was checked for all 29 newly-added wrestlers as part of this build, per Shane's "
        "standing process -- 3 of the 9 returning legends (McCool, Torrie Wilson, Molly Holly) and the Bella Twins "
        "have since been inducted, all well after this event; only 4 were Hall of Famers as of the event date "
        "itself (F376)."
    ),
    "data_quality_status": "CONFLICTING", "source_ids": "S144;S148;S149;S152;S153;S154;S155;S156;S157",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"2018 Women's build complete (first-ever Women's Royal Rumble): {len(new_wrestlers)} new wrestlers "
      f"({len(reused)} reused), {len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, "
      f"{len(sources)} sources logged, {len(flags) + len(flags2)} flags, {len(nm_rows)} notable_moments rows.")
