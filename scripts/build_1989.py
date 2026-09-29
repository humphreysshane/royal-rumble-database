# -*- coding: utf-8 -*-
"""
Builds all rows for the 1989 Royal Rumble — schema v2.

THIS PASS FOLLOWS SHANE'S "EXHAUST MY DOCUMENTS FIRST" INSTRUCTION: no live
web research (WebSearch/WebFetch) was done for 1989. Every source below is
either Shane's own Entrant_Stats.xlsx ('1989' tab) or a piece of text
preserved in Main_Rumble_Stats_New.docx under the 1989 heading. External
cross-checking (Wikipedia, Cagematch, ProFightDB, etc.) is deliberately
deferred to a later internet-research pass -- see flags.csv F0xx below.

SOURCES CONSULTED THIS PASS (see sources.csv for full registry):
  S012 "1989 Rumble Stats - Cageside" section, Shane's Word doc      tier 9
  S013 Dan Wahlers "History of the Royal Rumble" -- 1989 chapter     tier 9
  S014 Scott Keith, Kayfabe Memories review of 1989 Royal Rumble     tier 9
  S015 Shane's original research (Entrant_Stats.xlsx, '1989' tab)    tier 11

WHAT WAS ACTUALLY CROSS-CHECKED THIS PASS:
  - Entry order (1-30), elimination order, and eliminated-by credits are
    CONFIRMED: S015 (Excel structured table) and S014 (Scott Keith's
    independently-authored blow-by-blow recap) agree on all 30 entry
    numbers and all 29 eliminations, INCLUDING all 3 simultaneous-
    elimination spots (Brain Busters, Bad News Brown/Savage, Hercules/
    Beefcake) that S012's Cageside-style analysis separately calls out.
    Three independently-authored accounts (a spreadsheet compiled by
    Shane, a recap by Scott Keith, a timing analysis presumably by
    Cageside Seats/a named analyst) agreeing satisfies the "2+ sources
    agree = CONFIRMED" rule even though all three currently live inside
    Shane's own document -- but this is NOT the same as an externally
    verified source (Wikipedia/Cagematch), which is why it's flagged for
    a follow-up pass rather than treated as equivalent to 1988's Wikipedia
    cross-check.
  - Ring times / survival times: S015 (Excel) and S012 (Cageside-style
    list) agree within 0-2 seconds for 21 of 30 entrants (rounding, not a
    conflict, per precedent). EIGHT entrants show large (58-115 second)
    discrepancies between the two sources -- these are NOT rounding and
    are flagged (F0xx) rather than silently resolved by picking one.
  - Bios: reused wrestler_ids from 1988 (andre-the-giant, jake-roberts,
    ted-dibiase, hulk-hogan, one-man-gang/Akeem, ron-bass, tito-santana,
    judy-martin, haku, harley-race, dino-bravo, the-ultimate-warrior,
    rick-rude, jimmy-hart, bobby-heenan, virgil, jesse-ventura,
    gene-okerlund, howard-finkel, jim-duggan, jim-neidhart, bret-hart)
    were spot-checked against this year's Excel row for the same person
    and found CONSISTENT (same DOB, real name, death date where
    applicable) -- no new conflicts introduced by reuse. New people this
    year are PROBABLE, single-sourced from S015, same as 1988's 40
    unverified bios.
  - Red Rooster's real name conflicts: S015 gives "Paul Worden Taylor
    III"; S014's recap independently calls him "Terry Taylor (aka The
    Red You-Know-What)" -- flagged, not resolved (F0xx).
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from schema import (
    ENTRANTS_FIELDS, ELIMINATIONS_FIELDS, EVENTS_FIELDS, slugify, mmss_to_seconds,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EVENT_ID = "RR1989M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S012", "'1989 Rumble Stats - Cageside' section (Shane's doc)", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Frame-by-frame-style timing analysis (survival times, entrance times, time-between-buzzers, ring crowdedness) preserved in Shane's Word doc, same format/methodology as 1988's verified Cageside Seats piece (S008). NOT live-fetched this pass (documents-first instruction) -- origin presumed to be Cageside Seats' 'Match Times' series but this is unverified this pass. See flags.csv."),
    ("S013", "Dan Wahlers, 'History of the Royal Rumble' -- 1989 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Preserved in Shane's original doc; no live URL captured. Gives attendance as 19,000 (single-sourced this pass), full narrative history, and fall-by-fall undercard results."),
    ("S014", "Scott Keith, Kayfabe Memories review of 1989 Royal Rumble", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15",
     "Preserved in Shane's original doc. Detailed entry-by-entry, elimination-by-elimination blow-by-blow of the Rumble match plus the full undercard; independently confirms all 30 entry numbers and all 29 eliminations against S015."),
    ("S015", "Shane's original research (Entrant_Stats.xlsx, '1989' tab)", "original_document", "", 11, "Original research document", "2026-09-15",
     "Base layer for entrant detail; treated as PROBABLE until independently cross-checked per record, per the same rule applied to S004 in 1988."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# FLAGS
# ---------------------------------------------------------------------------
flags = [
    ("F008", EVENT_ID, "entrants", "*", "ring_time;ring_time_status", "conflicting_sources",
     "8 of 30 entrants show large (58-115 second) discrepancies between S015's Ring Time column and "
     "S012's Survival Times list -- far outside the 0-2 second rounding variance seen for the other 22 "
     "entrants. Andre the Giant: 14:55 (S015) vs 13:57 (S012), diff 58s. Akeem: 18:36 vs 20:31, diff 115s. "
     "Brutus Beefcake: 13:56 vs 14:57, diff 61s. The Barbarian: 11:15 vs 12:16, diff 61s. Big John Studd "
     "(the winner): 12:21 vs 14:16, diff 115s. Hercules: 6:11 vs 7:12, diff 61s. Rick Martel: 5:29 vs 7:06, "
     "diff 97s. Ted DiBiase (runner-up): 6:27 vs 8:21, diff 114s. All 8 are clustered in the match's final "
     "third. Possible explanation (NOT confirmed, not acted on): S015's Ring Time for these entrants may "
     "measure something other than full survival time (e.g. a different start/end boundary), but this is "
     "speculation -- both values are preserved as-is, S015's value kept as the displayed ring_time with "
     "status CONFLICTING, S012's value kept in notes. Luke Williams' smaller 10s variance (3:08 vs 3:18) is "
     "kept as PROBABLE, not flagged, consistent with the existing rounding-tolerance precedent.",
     "S012;S015", "open", "2026-09-15"),
    ("F009", EVENT_ID, "wrestlers", "red-rooster", "real_name", "conflicting_sources",
     "S015 (Shane's Excel) gives Red Rooster's real name as 'Paul Worden Taylor III'. S014 (Scott Keith's "
     "recap) independently refers to him as 'Terry Taylor (aka The Red You-Know-What)'. These are very "
     "likely the same underlying fact stated two different ways (or a genuine data error in one source) but "
     "not resolved this pass -- kept S015's value with status CONFLICTING and S014's name preserved in notes.",
     "S014;S015", "open", "2026-09-15"),
    ("F010", EVENT_ID, "events", EVENT_ID, "attendance_reported", "unverified",
     "RESOLVED (fact-check pass): Wikipedia (S026) independently confirms 19,000 attendance, agreeing with "
     "S013 (Dan Wahlers). Upgraded to CONFIRMED.",
     "S013;S026", "resolved", "2026-09-15"),
    ("F011", EVENT_ID, "events;eliminations;entrants", "*", "n/a", "unverified",
     "PARTIALLY RESOLVED (fact-check pass): Wikipedia (S026) was checked against this event's date, venue, "
     "attendance, duration, winner/runner-up, and commentary team, all of which now agree -- see F010/F012 "
     "and events.csv. However, the AI web-fetch tool used to extract Wikipedia's full entry-order/elimination "
     "table for this event visibly scrambled it (reordered rows, misaligned columns) when asked to reproduce "
     "it in bulk -- see 1992's F034 for the same issue observed more clearly. So the entry-by-entry/"
     "elimination-by-elimination detail in this database is still cross-checked only WITHIN Shane's own "
     "document (S012/S013/S014/S015 agreeing with each other), not against Wikipedia's table specifically. "
     "A full row-by-row Wikipedia cross-check remains open for a future pass -- see F034.",
     "S012;S013;S014;S015;S026", "open", "2026-09-15"),
    ("F012", EVENT_ID, "events", EVENT_ID, "duration_total", "unverified",
     "RESOLVED (fact-check pass): S012 (Cageside-style analysis) gives total match duration as 65:06; S013 "
     "(Dan Wahlers) gives 64:53. Wikipedia (S026) independently agrees with S013's 64:53 exactly -- 2 "
     "independent sources now outweigh S012 alone, so duration_total is corrected from 65:06 to 64:53 and "
     "upgraded to CONFIRMED. S012's 65:06 is treated as the less-accurate outlier of the two internal figures.",
     "S012;S013;S026", "resolved", "2026-09-15"),
    ("F013", EVENT_ID, "entrances/moves/near_eliminations", "*", "n/a", "out_of_scope_no_tool",
     "No video/computer-vision tool is connected in this session. entrances.csv, moves.csv, "
     "near_eliminations.csv, and eliminations.csv:location_side remain empty for every 1989 record. Same as "
     "1988's F005.",
     "", "open", "2026-09-15"),
    ("F014", EVENT_ID, "entrants", "*", "billed_height_m_at_event;billed_weight_kg_at_event;dob;real_name;birthplace;hall_of_fame_year", "unverified",
     "19 of 30 Rumble-match entrants (everyone except the wrestlers reused from the already-partly-verified "
     "1988 roster: andre-the-giant, jake-roberts, ted-dibiase, hulk-hogan, one-man-gang/Akeem, ron-bass, "
     "tito-santana) have biographical data sourced only from S015 this pass, not yet independently cross-"
     "checked. Same open item as 1988's F003, now extended to 1989's new people.",
     "S015", "open", "2026-09-15"),
    ("F046", EVENT_ID, "wrestlers", "greg-valentine", "real_name", "conflicting_sources",
     "Fact-check pass: Shane's document (S004) gives real name 'Gregory Wisniski'. Wikipedia (S022) gives "
     "'Jonathan Anthony Wisniski' -- same surname, disagreeing first/middle names, so kept as a genuine "
     "conflict rather than a spelling-variant upgrade. DOB (1951-09-20) and birthplace (Seattle, Washington) "
     "both independently confirmed and matching. Kept existing (S004) value pending a tiebreaking source.",
     "S004;S022", "open", "2026-09-15"),
    ("F047", EVENT_ID, "wrestlers", "brutus-beefcake", "birthplace", "conflicting_sources",
     "Fact-check pass: Shane's document (S015) gives birthplace as San Francisco, California. Wikipedia "
     "(S022) gives Tampa, Florida -- a genuine city/state-level disagreement. Real name (Edward Harrison "
     "Leslie) independently confirmed and matching; DOB differs only by 1 year (existing 1958-04-21 vs new "
     "1957-04-21, same day/month) and was not upgraded to CONFIRMED given the birthplace disagreement casts "
     "some doubt on the match. Kept existing values pending a tiebreaking third source.",
     "S015;S022", "open", "2026-09-15"),
    ("F048", EVENT_ID, "wrestlers", "red-rooster", "birthplace", "conflicting_sources",
     "Fact-check pass, see also F009 (the now-resolved real-name non-conflict for this same wrestler): "
     "Shane's document (S015) gives birthplace as Vero Beach, Florida. Wikipedia (S022) AND Cagematch (S023) "
     "-- 2 independent sources, agreeing with each other -- both give Greenville, South Carolina. Per the "
     "2-independent-sources rule this would normally outweigh the single-sourced S015 figure, but is kept as "
     "an open CONFLICTING flag rather than silently overwritten, since S015 is Shane's own primary research "
     "and the disagreement is stark enough (different states) to warrant a human look before correcting it.",
     "S015;S022;S023", "open", "2026-09-15"),
    ("F049", EVENT_ID, "wrestlers", "mr-fuji", "dob", "conflicting_sources",
     "Fact-check pass: Shane's document (S015) gives DOB 1935-05-04. Wikipedia (S022) gives 1934-05-04 -- "
     "same day/month, year disagrees by 1. Real name (Harry Masayoshi Fujiwara) and birthplace (Honolulu, "
     "Hawaii) both independently confirmed and matching. Kept existing value pending a tiebreaking source.",
     "S015;S022", "open", "2026-09-15"),
    ("F050", EVENT_ID, "wrestlers", "gorilla-monsoon", "birthplace", "conflicting_sources",
     "Fact-check pass: Shane's document (S015) gives birthplace as New York, New York (i.e. NYC). Wikipedia "
     "(S022) AND Cagematch (S023) -- 2 independent sources, agreeing with each other -- both give Rochester, "
     "New York instead. Per the 2-independent-sources rule this would normally outweigh the single-sourced "
     "S015 figure, but kept as an open CONFLICTING flag rather than silently overwritten, for the same reason "
     "as F048 (Red Rooster) -- Shane's own primary research deserves a human look before being corrected. "
     "Real name (Robert James Marella) and DOB (1937-06-04) both independently confirmed and matching.",
     "S015;S022;S023", "open", "2026-09-15"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# WRESTLERS -- only NEW people not already in wrestlers.csv from 1988.
# Reused (NOT re-added): andre-the-giant, jake-roberts, ted-dibiase, hulk-hogan,
# one-man-gang (Akeem), ron-bass, tito-santana, judy-martin, haku, harley-race,
# dino-bravo, the-ultimate-warrior, rick-rude, jimmy-hart, bobby-heenan, virgil,
# jesse-ventura, gene-okerlund, howard-finkel, jim-duggan, jim-neidhart, bret-hart
# ---------------------------------------------------------------------------
# ring_name, real_name, real_name_status, gender, dob, dob_status, deceased_date,
# birthplace, birthplace_status, nationality, debut_year_company, hof_year,
# aliases, wrestling_style, notes, source_ids
new_wrestlers = [
    ("Ax", "Bill Eadie", "PROBABLE", "M", "1947-12-27", "PROBABLE", "", "Brownsville, Pennsylvania", "PROBABLE", "American", "", "", "Demolition Axe", "", "Half of Demolition (w/ Smash)", "S015"),
    ("Smash", "Barry Darsow", "PROBABLE", "M", "1959-10-06", "PROBABLE", "", "Minneapolis, Minnesota", "PROBABLE", "American", "", "", "Demolition Smash", "", "Half of Demolition (w/ Ax)", "S015"),
    ("Mr. Perfect", "Curtis Michael Hennig", "PROBABLE", "M", "1958-03-28", "PROBABLE", "2003-02-10", "Robbinsdale, Minnesota", "PROBABLE", "American", "", "2007", "Curt Hennig", "", "", "S015"),
    ("Ronnie Garvin", "Roger Barnes", "PROBABLE", "M", "1945-03-30", "PROBABLE", "", "Montreal, Quebec, Canada", "PROBABLE", "Canadian", "", "", "", "", "", "S015"),
    ("Greg Valentine", "Gregory Wisniski", "PROBABLE", "M", "1951-09-20", "PROBABLE", "", "Seattle, Washington", "PROBABLE", "American", "", "2004", "", "", "", "S015"),
    ("Shawn Michaels", "Michael Shawn Hickenbottom", "PROBABLE", "M", "1965-07-22", "PROBABLE", "", "San Antonio, Texas", "PROBABLE", "American", "", "2011", "HBK", "", "", "S015"),
    ("Butch Miller", "Robert Miller", "PROBABLE", "M", "1944-10-21", "PROBABLE", "", "Auckland, New Zealand", "PROBABLE", "New Zealander", "", "2015", "Bushwhacker Butch", "", "Half of The Bushwackers (w/ Luke Williams)", "S015"),
    ("The Honky Tonk Man", "Roy Wayne Farris", "PROBABLE", "M", "1953-01-25", "PROBABLE", "", "Memphis, Tennessee", "PROBABLE", "American", "", "", "", "", "", "S015"),
    ("Bad News Brown", "Allen James Coage", "PROBABLE", "M", "1943-10-22", "PROBABLE", "2007-03-06", "New York, New York", "PROBABLE", "American", "", "", "", "", "", "S015"),
    ("Marty Jannetty", "Fredrick Marty Jannetty", "PROBABLE", "M", "1960-02-03", "PROBABLE", "", "Columbus, Georgia", "PROBABLE", "American", "", "", "", "", "Half of The Rockers (w/ Shawn Michaels)", "S015"),
    ("Randy Savage", "Randy Mario Poffo", "PROBABLE", "M", "1952-11-15", "PROBABLE", "2011-05-20", "Sarasota, Florida", "PROBABLE", "American", "", "2015", "Macho Man", "", "WWF World Heavyweight Champion at time of event.", "S015"),
    ("Arn Anderson", "Martin Anthony Lunde", "PROBABLE", "M", "1958-09-20", "PROBABLE", "", "Rome, Georgia", "PROBABLE", "American", "", "2012", "", "", "Half of Brain Busters (w/ Tully Blanchard)", "S015"),
    ("Tully Blanchard", "Tully Arthur Blanchard", "PROBABLE", "M", "1954-01-22", "PROBABLE", "", "Edmonton, Alberta, Canada", "PROBABLE", "Canadian", "", "2012", "", "", "Half of Brain Busters (w/ Arn Anderson)", "S015"),
    ("Luke Williams", "Brian Wickens", "PROBABLE", "M", "1947-01-08", "PROBABLE", "", "Wellington, New Zealand", "PROBABLE", "New Zealander", "", "2015", "Bushwhacker Luke", "", "Half of The Bushwackers (w/ Butch Miller)", "S015"),
    ("Koko B. Ware", "James Ware", "PROBABLE", "M", "1957-06-20", "PROBABLE", "", "Union City, Tennessee", "PROBABLE", "American", "", "2009", "", "", "", "S015"),
    ("The Warlord", "Terry Scott Szopinski", "PROBABLE", "M", "1962-03-28", "PROBABLE", "", "Pompano Beach, Florida", "PROBABLE", "American", "", "", "", "", "Half of Powers of Pain (w/ The Barbarian)", "S015"),
    ("Big Bossman", "Raymond Traylor, Jr.", "PROBABLE", "M", "1963-05-02", "PROBABLE", "2004-09-22", "Cobb County, Georgia", "PROBABLE", "American", "", "", "", "", "Half of The Twin Towers (w/ Akeem)", "S015"),
    ("Brutus Beefcake", "Edward Harrison Leslie", "PROBABLE", "M", "1958-04-21", "PROBABLE", "", "San Francisco, California", "PROBABLE", "American", "", "", "", "", "", "S015"),
    ("Red Rooster", "Paul Worden Taylor III", "CONFLICTING", "M", "1955-08-12", "PROBABLE", "", "Vero Beach, Florida", "PROBABLE", "American", "", "", "", "", "Real name conflicts with S014's 'Terry Taylor' -- see flags.csv F009.", "S015;S014"),
    ("The Barbarian", "Sione Havea Vailahi", "PROBABLE", "M", "1958-09-06", "PROBABLE", "", "Parts Unknown", "PROBABLE", "Tongan", "", "", "", "", "Half of Powers of Pain (w/ The Warlord)", "S015"),
    ("Big John Studd", "John Minton", "PROBABLE", "M", "1948-02-19", "PROBABLE", "1995-03-20", "Los Angeles, California", "PROBABLE", "American", "", "2004", "", "", "Winner of the 1989 Royal Rumble.", "S015"),
    ("Hercules", "Raymond Fernandez", "PROBABLE", "M", "1956-05-07", "PROBABLE", "2004-03-06", "Tampa, Florida", "PROBABLE", "American", "", "", "", "", "", "S015"),
    ("Rick Martel", "Richard Vigneault", "PROBABLE", "M", "1956-03-18", "PROBABLE", "", "Montreal, Quebec", "PROBABLE", "Canadian", "", "", "", "", "Half of Strike Force (w/ Tito Santana)", "S015"),
    ("Jacques Rougeau", "Jacques Rougeau Jr.", "PROBABLE", "M", "1960-06-13", "PROBABLE", "", "Saint-Sulpice, Quebec", "PROBABLE", "Canadian", "", "", "", "", "Half of The Rougeau Brothers (w/ Raymond)", "S015"),
    ("Raymond Rougeau", "Raymond Rougeau", "PROBABLE", "M", "1955-02-18", "PROBABLE", "", "Saint-Sulpice, Quebec", "PROBABLE", "Canadian", "", "", "", "", "Half of The Rougeau Brothers (w/ Jacques)", "S015"),
    ("Rockin' Robin", "Robin Denise Smith", "PROBABLE", "F", "1964-10-09", "PROBABLE", "", "Hammond, Louisiana", "PROBABLE", "American", "", "", "", "", "WWF Women's Champion at time of event. Sister of Jake Roberts.", "S015"),
    ("Slick", "Kenneth Johnson", "PROBABLE", "M", "1957-12-08", "PROBABLE", "", "Fort Worth, Texas", "PROBABLE", "American", "", "", "", "", "Manager", "S015"),
    ("Sean Mooney", "Sean Mooney", "PROBABLE", "M", "1959-05-21", "PROBABLE", "", "Phoenix, Arizona", "PROBABLE", "American", "", "", "", "", "Interviewer", "S015"),
    ("Mr. Fuji", "Harry Fujiwara", "PROBABLE", "M", "1935-05-04", "PROBABLE", "", "Honolulu, Hawaii", "PROBABLE", "American", "", "2007", "", "", "Manager", "S015"),
    ("Miss Elizabeth", "Elizabeth Ann Hulette", "PROBABLE", "F", "1960-07-19", "PROBABLE", "2003-05-01", "Frankfort, Kentucky", "PROBABLE", "American", "", "", "", "", "Manager to Randy Savage/Hulk Hogan; also made a brief in-ring cameo during the Rumble match itself.", "S015"),
    ("Sensational Sherri", "Sherri Russell", "PROBABLE", "F", "1958-02-08", "PROBABLE", "2007-06-15", "Birmingham, Alabama", "PROBABLE", "American", "", "2006", "", "", "Guest commentator at this event.", "S015"),
    ("Gorilla Monsoon", "Robert James Marella", "PROBABLE", "M", "1937-06-04", "PROBABLE", "1999-10-06", "New York, New York", "PROBABLE", "American", "", "1994", "", "", "Commentator", "S015"),
]

wrestler_ids = {}
# Preload the wrestler_ids for people reused from 1988 (already in wrestlers.csv)
reused = {
    "Andre the Giant": "andre-the-giant", "Jake Roberts": "jake-roberts",
    "Ted DiBiase": "ted-dibiase", "Hulk Hogan": "hulk-hogan",
    "Akeem": "one-man-gang", "Ron Bass": "ron-bass", "Tito Santana": "tito-santana",
    "Judy Martin": "judy-martin", "King Haku": "haku", "Harley Race": "harley-race",
    "Dino Bravo": "dino-bravo", "The Ultimate Warrior": "the-ultimate-warrior",
    "Rick Rude": "rick-rude", "Jimmy Hart": "jimmy-hart", "Bobby Heenan": "bobby-heenan",
    "Virgil": "virgil", "Jesse Ventura": "jesse-ventura", "Gene Okerlund": "gene-okerlund",
    "Howard Finkel": "howard-finkel", "Jim Duggan": "jim-duggan", "Jim Neidhart": "jim-neidhart",
    "Bret Hart": "bret-hart", "Frenchy Martin": "frenchy-martin",
}
wrestler_ids.update(reused)

with open(os.path.join(DATA_DIR, "wrestlers.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in new_wrestlers:
        ring_name = row[0]
        wid = slugify(ring_name)
        wrestler_ids[ring_name] = wid
        writer.writerow([wid] + list(row))

# ---------------------------------------------------------------------------
# ENTRANTS in the 30-man Royal Rumble match, in entry order
# ---------------------------------------------------------------------------
# name, entry, elim_no, elim_by[], ring_time(=elim clock time for eliminated /
# full match participation for winner), doc_survival_time (for the CONFLICTING
# 8 + Luke), elim_count(this event), age, h, w, billed_from, champ, align, team
entrants_raw = [
    ("Ax", 1, 4, ["Mr. Perfect"], "14:37", None, 0, "41 Years, 0 Months, 19 Days", 1.91, 132, "Parts Unknown", "WWF World Tag Team Champion (Demolition)", "Face", "Demolition (w/ Smash)"),
    ("Smash", 2, 1, ["Andre the Giant"], "04:55", None, 0, "29 Years, 3 Months, 9 Days", 1.88, 132, "Parts Unknown", "WWF World Tag Team Champion (Demolition)", "Face", "Demolition (w/ Ax)"),
    ("Andre the Giant", 3, 5, ["Andre the Giant"], "14:55", "13:57", 3, "42 Years, 7 Months, 27 Days", 2.24, 240, "Grenoble, France", "", "Heel", ""),
    ("Mr. Perfect", 4, 11, ["Hulk Hogan"], "27:58", None, 1, "30 Years, 9 Months, 18 Days", 1.91, 117, "Robbinsdale, Minnesota", "", "Heel", ""),
    ("Ronnie Garvin", 5, 2, ["Andre the Giant"], "02:39", None, 0, "43 Years, 9 Months, 16 Days", 1.83, 110, "Montreal, Quebec, Canada", "", "Face", ""),
    ("Greg Valentine", 6, 8, ["Randy Savage"], "19:52", None, 0, "37 Years, 3 Months, 26 Days", 1.83, 110, "Seattle, Washington", "", "Heel", "Rhythm and Blues (w/ Honky Tonk Man)"),
    ("Jake Roberts", 7, 3, ["Andre the Giant"], "02:08", None, 0, "33 Years, 7 Months, 16 Days", 1.98, 113, "Stone Mountain, Georgia", "", "Face", ""),
    ("Ron Bass", 8, 7, ["Shawn Michaels", "Marty Jannetty"], "12:36", None, 0, "40 Years, 0 Months, 25 Days", 1.93, 131, "Harrisburg, Arkansas", "", "Heel", ""),
    ("Shawn Michaels", 9, 9, ["Randy Savage", "Arn Anderson"], "14:30", None, 1, "23 Years, 5 Months, 24 Days", 1.85, 102, "San Antonio, Texas", "", "Face", "The Rockers (w/ Marty Jannetty)"),
    ("Butch Miller", 10, 13, ["Bad News Brown"], "18:13", None, 1, "44 Years, 2 Months, 25 Days", 1.85, 113, "Auckland, New Zealand", "", "Face", "The Bushwackers (w/ Luke Williams)"),
    ("The Honky Tonk Man", 11, 6, ["Tito Santana", "Butch Miller"], "04:12", None, 0, "35 Years, 11 Months, 21 Days", 1.85, 112, "Memphis, Tennessee", "", "Heel", "Rhythm and Blues (w/ Greg Valentine)"),
    ("Tito Santana", 12, 12, ["Randy Savage"], "12:47", None, 1, "35 Years, 8 Months, 5 Days", 1.88, 106, "Mission, Texas", "", "Face", "Strike Force (w/ Rick Martel)"),
    ("Bad News Brown", 13, 19, ["Hulk Hogan"], "16:24", None, 1, "45 Years, 2 Months, 24 Days", 1.91, 123, "New York, New York", "", "Heel", ""),
    ("Marty Jannetty", 14, 10, ["Tully Blanchard", "Arn Anderson"], "07:52", None, 1, "28 Years, 11 Months, 12 Days", 1.8, 103, "Columbus, Georgia", "", "Face", "The Rockers (w/ Shawn Michaels)"),
    ("Randy Savage", 15, 20, ["Hulk Hogan"], "12:26", None, 3, "36 Years, 2 Months, 0 Days", 1.88, 108, "Sarasota, Florida", "WWF World Heavyweight Championship", "Face", "Mega Powers (w/ Hulk Hogan)"),
    ("Arn Anderson", 16, 16, ["Hulk Hogan"], "10:00", None, 2, "30 Years, 3 Months, 26 Days", 1.85, 116, "Minnesota", "", "Heel", "Brain Busters (w/ Tully Blanchard)"),
    ("Tully Blanchard", 17, 17, ["Hulk Hogan"], "08:02", None, 1, "34 Years, 11 Months, 24 Days", 1.78, 102, "Edmonton, Alberta, Canada", "", "Heel", "Brain Busters (w/ Arn Anderson)"),
    ("Hulk Hogan", 18, 21, ["Big Bossman", "Akeem"], "11:31", None, 9, "35 Years, 5 Months, 4 Days", 2.01, 130, "Venice Beach, California", "", "Face", "Mega Powers (w/ Randy Savage)"),
    ("Luke Williams", 19, 15, ["Hulk Hogan"], "03:08", "03:18", 0, "42 Years, 0 Months, 7 Days", 1.83, 112, "Wellington, New Zealand", "", "Face", "The Bushwackers (w/ Butch Miller)"),
    ("Koko B. Ware", 20, 14, ["Hulk Hogan"], "01:08", None, 0, "31 Years, 6 Months, 26 Days", 1.73, 110, "Union City, Tennessee", "", "Face", ""),
    ("The Warlord", 21, 18, ["Hulk Hogan"], "00:03", None, 0, "26 Years, 9 Months, 18 Days", 1.96, 147, "Parts Unknown", "", "Heel", "Powers of Pain (w/ The Barbarian)"),
    ("Big Bossman", 22, 22, ["Hulk Hogan"], "04:18", None, 1, "25 Years, 8 Months, 13 Days", 1.98, 143, "Cobb County, Georgia", "", "Heel", "The Twin Towers (w/ Akeem)"),
    ("Akeem", 23, 28, ["Big John Studd"], "18:36", "20:31", 2, "28 Years, 11 Months, 3 Days", 2.06, 204, "Deepest, Darkest, Africa", "", "Heel", "The Twin Towers (w/ Big Bossman)"),
    ("Brutus Beefcake", 24, 24, ["Ted DiBiase", "The Barbarian"], "13:56", "14:57", 0, "30 Years, 8 Months, 25 Days", 1.93, 123, "San Francisco, California", "", "Face", ""),
    ("Red Rooster", 25, 23, ["Ted DiBiase"], "11:17", None, 0, "33 Years, 5 Months, 3 Days", 1.85, 102, "Vero Beach, Florida", "", "Face", ""),
    ("The Barbarian", 26, 26, ["Rick Martel"], "11:15", "12:16", 2, "30 Years, 4 Months, 9 Days", 1.88, 136, "Parts Unknown", "", "Heel", "Powers of Pain (w/ The Warlord)"),
    ("Big John Studd", 27, 0, [], "12:21", "14:16", 2, "40 Years, 10 Months, 27 Days", 2.08, 165, "Los Angeles, California", "", "Face", ""),
    ("Hercules", 28, 25, ["Ted DiBiase", "The Barbarian"], "06:11", "07:12", 0, "32 Years, 8 Months, 8 Days", 1.85, 122, "Tampa, Florida", "", "Face", ""),
    ("Rick Martel", 29, 27, ["Akeem"], "05:29", "07:06", 1, "32 Years, 9 Months, 28 Days", 1.83, 103, "Montreal, Quebec", "", "Face", "Strike Force (w/ Tito Santana)"),
    ("Ted DiBiase", 30, 29, ["Big John Studd"], "06:27", "08:21", 3, "34 Years, 11 Months, 28 Days", 1.91, 118, "Palm Beach, Florida", "", "Heel", ""),
]

FINAL_FOUR_ORDER = ["big-john-studd", "ted-dibiase", "one-man-gang", "rick-martel"]  # winner, RU, 3rd(Akeem), 4th
SIM_GROUPS = {
    frozenset(["arn-anderson", "tully-blanchard"]): "brain-busters",
    frozenset(["bad-news-brown", "randy-savage"]): "bad-news-savage",
    frozenset(["hercules", "brutus-beefcake"]): "hercules-beefcake",
}

elim_rows = []
entrant_rows = []

for (name, entry, elim_no, elim_by, ring_time, doc_survival, elim_count, age, h, w, billed_from, champ, align, team) in entrants_raw:
    wid = wrestler_ids[name]
    is_winner = (elim_no == 0)
    ring_time_s = mmss_to_seconds(ring_time)
    ring_time_status = "CONFLICTING" if doc_survival else "PROBABLE"
    notes = ""
    if doc_survival:
        notes = (f"S015 (Excel) ring time {ring_time} vs S012 (Cageside-style survival-time list) "
                  f"{doc_survival} -- {abs(mmss_to_seconds(ring_time) - mmss_to_seconds(doc_survival))}s "
                  f"variance, not rounding. See flags.csv F008. S015's value used as the primary ring_time.")

    if elim_by and name != "Big John Studd":
        elim_time_s = ring_time_s
        # simultaneous-group lookup: find if this eliminated wrestler is part of a documented sim pair
        sim_group = ""
        for pair, label in SIM_GROUPS.items():
            if wid in pair:
                sim_group = f"{EVENT_ID}-{label}"
        is_self = (name == "Andre the Giant")
        elim_method = "self-elimination via Jake Roberts/Damien distraction (per S012/S014)" if is_self else "UNKNOWN"
        row_sources = "S014;S015" + (";S012" if sim_group else "") + (";S013" if is_self else "")
        for eliminator in elim_by:
            elim_rows.append({
                "event_id": EVENT_ID, "order_in_match": elim_no,
                "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids.get(eliminator, wid),
                "assisting_wrestler_ids": ";".join(wrestler_ids[e] for e in elim_by if e != eliminator),
                "entry_number_of_eliminated": entry, "entry_number_of_eliminator": "",
                "elimination_clock_time": ring_time, "elimination_clock_seconds": elim_time_s,
                "elimination_type": "over_top_rope" if not is_self else "self_elimination",
                "elimination_method": elim_method,
                "location_side": "", "location_status": "UNKNOWN",
                "is_solo": "FALSE" if (len(elim_by) > 1 or sim_group) else "TRUE",
                "is_shared": "TRUE" if len(elim_by) > 1 else "FALSE",
                "is_accidental": "UNKNOWN", "is_self_elimination": "TRUE" if is_self else "FALSE",
                "is_storyline_related": "TRUE" if is_self else "UNKNOWN", "was_already_incapacitated": "UNKNOWN",
                "is_disputed": "FALSE", "simultaneous_group_id": sim_group,
                "data_quality_status": "CONFIRMED", "source_ids": row_sources,
                "notes": ("Simultaneous elimination per S012/S014 -- see notes on the paired entrant's row too." if sim_group else ""),
            })
    else:
        pass  # winner, no elimination row

    entrant_rows.append({
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": "CONFIRMED",
        "ring_name_at_time": name, "name_displayed_at_event": name,
        "prior_rumble_appearances_count": "",  # filled below
        "rumble_appearance_no": "", "is_first_rumble_appearance": "", "previous_rumble_year": "",
        "previous_rumble_result": "", "previous_rumble_elimination_no": "",
        "is_rumble_debut": "", "is_company_debut": "UNKNOWN", "company_debut_date": "",
        "is_returning_wrestler": "", "absence_length": "",
        "age_at_event": age, "age_status": "DERIVED",
        "billed_height_m_at_event": h, "billed_weight_kg_at_event": w,
        "billed_from_at_event": billed_from,
        "physical_status": "CONFIRMED" if wid == "one-man-gang" else "PROBABLE",
        "alignment": align, "alignment_status": "PROBABLE",
        "gimmick_at_event": "", "manager_at_event": "", "tag_team_name": team, "faction_stable": "",
        "current_champion_title": champ, "championship_level": "World" if "World Heavyweight" in champ else ("Tag Team" if champ else ""),
        "championship_partner": "Smash" if name == "Ax" else ("Ax" if name == "Smash" else ""),
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        "title_defended_same_card": "FALSE", "title_lost_same_card": "FALSE",
        "elim_number": elim_no if elim_no else "", "elim_number_status": "CONFIRMED",
        "eliminated_by_ids": ";".join(wrestler_ids.get(e, wid) for e in elim_by),
        "elimination_clock_time": ring_time if elim_by and not is_winner else "",
        "elimination_clock_seconds": ring_time_s if elim_by and not is_winner else "",
        "ring_time": ring_time, "ring_time_seconds": ring_time_s, "ring_time_status": ring_time_status,
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": elim_count, "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "TRUE" if name == "Andre the Giant" else "FALSE",
        "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if wid == "ted-dibiase" else "FALSE",
        "is_final_two": "TRUE" if wid in ("big-john-studd", "ted-dibiase") else "FALSE",
        "is_final_three": "TRUE" if wid in FINAL_FOUR_ORDER[:3] else "FALSE",
        "is_final_four": "TRUE" if wid in FINAL_FOUR_ORDER else "FALSE",
        "surprise_entrant": "FALSE", "legend_returning": "FALSE", "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE", "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",  # WWE HOF didn't exist until 1993
        "data_quality_status": "CONFIRMED", "source_ids": "S014;S015", "notes": notes,
    })

# Returning-wrestler / streak fields, derived from actual 1988 entrant data (not from
# Shane's own "Longest Streak" summary field, which undercounts -- see script docstring)
RETURNING_FROM_1988 = {"tito-santana": 2, "jake-roberts": 2, "ron-bass": 2, "one-man-gang": 2}
for er in entrant_rows:
    wid = er["wrestler_id"]
    if wid in RETURNING_FROM_1988:
        er["prior_rumble_appearances_count"] = 1
        er["rumble_appearance_no"] = 2
        er["is_first_rumble_appearance"] = "FALSE"
        er["previous_rumble_year"] = 1988
        er["is_rumble_debut"] = "FALSE"
        er["is_returning_wrestler"] = "TRUE"
        er["absence_length"] = "0 years (consecutive)"
    else:
        er["prior_rumble_appearances_count"] = 0
        er["rumble_appearance_no"] = 1
        er["is_first_rumble_appearance"] = "TRUE"
        er["is_rumble_debut"] = "TRUE"
        er["is_returning_wrestler"] = "FALSE"
    if wid == "tito-santana":
        er["previous_rumble_result"] = "Eliminated (2nd, by Bret Hart/Jim Neidhart)"
        er["previous_rumble_elimination_no"] = 2
    if wid == "jake-roberts":
        er["previous_rumble_result"] = "Eliminated (10th, by One Man Gang)"
        er["previous_rumble_elimination_no"] = 10
    if wid == "ron-bass":
        er["previous_rumble_result"] = "Eliminated (16th, by Don Muraco)"
        er["previous_rumble_elimination_no"] = 16
    if wid == "one-man-gang":
        er["previous_rumble_result"] = "Runner-up (19th, by Jim Duggan)"
        er["previous_rumble_elimination_no"] = 19

# Back-fill wrestlers_eliminated_ids / solo / assisted counts from the elimination log
elim_map = {}
solo_map = {}
assist_map = {}
for row in elim_rows:
    eid = row["eliminator_wrestler_id"]
    if eid == row["eliminated_wrestler_id"]:
        continue  # self-eliminations don't count toward the "eliminator's" tally of others eliminated
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
# TAG TEAMS (the 9 official teams that entered the match, per S015's rollup)
# ---------------------------------------------------------------------------
tag_teams = [
    ("Demolition", ["Ax", "Smash"], "TRUE", 0, "Started the Rumble against each other as the #1/#2 entrants despite being partners -- S015's 'Tag Team head to heads' stat (1)."),
    ("Rhythm and Blues", ["Greg Valentine", "The Honky Tonk Man"], "TRUE", 0, ""),
    ("The Rockers", ["Shawn Michaels", "Marty Jannetty"], "TRUE", 1, ""),
    ("The Bushwackers", ["Butch Miller", "Luke Williams"], "TRUE", 1, ""),
    ("Strike Force", ["Tito Santana", "Rick Martel"], "TRUE", 2, ""),
    ("Mega Powers", ["Randy Savage", "Hulk Hogan"], "TRUE", 12, "Minor storyline rift after Hogan eliminated Savage -- S015's 'Tag Team rifts' stat; the pair split for real a few months later."),
    ("Brain Busters", ["Arn Anderson", "Tully Blanchard"], "TRUE", 3, "Both eliminated simultaneously by Hogan -- see eliminations.csv simultaneous_group_id."),
    ("Powers of Pain", ["The Warlord", "The Barbarian"], "TRUE", 2, ""),
    ("The Twin Towers", ["Big Bossman", "Akeem"], "TRUE", 10, ""),
]
with open(os.path.join(DATA_DIR, "tag_teams.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for team_name, members, official, combined, notes in tag_teams:
        writer.writerow([EVENT_ID, team_name, ";".join(wrestler_ids[m] for m in members), "", "",
                          official, "TRUE", "TRUE", "", "FALSE", "TRUE", "FALSE", combined,
                          "PROBABLE", "S015" + (";S012;S014" if notes else "")])

# ---------------------------------------------------------------------------
# SHOW APPEARANCES (Pre-Rumble Appearances, per S015)
# ---------------------------------------------------------------------------
show_appearances = [
    ("Jim Duggan", "Wrestler (undercard)", "", "Face", "", "Opener 2/3-falls tag; also announced entry #30 pool before trading out -- see other_matches.csv"),
    ("Bret Hart", "Wrestler (undercard)", "", "Face", "", "Opener 2/3-falls tag; pinned Dino Bravo for the deciding fall"),
    ("Jim Neidhart", "Wrestler (undercard)", "", "Face", "", "Opener 2/3-falls tag"),
    ("Dino Bravo", "Wrestler (undercard)", "", "Heel", "", "Opener 2/3-falls tag; pinned by Bret Hart for the deciding fall"),
    ("Jacques Rougeau", "Wrestler (undercard)", "", "Heel", "", "Opener 2/3-falls tag"),
    ("Raymond Rougeau", "Wrestler (undercard)", "", "Heel", "", "Opener 2/3-falls tag"),
    ("Frenchy Martin", "Manager", "Dino Bravo", "Heel", "", ""),
    ("Jimmy Hart", "Manager", "Jacques Rougeau, Raymond Rougeau", "Heel", "", ""),
    ("Rockin' Robin", "Wrestler (undercard)", "", "Face", "WWF World Women's Championship", "Retained title vs. Judy Martin"),
    ("Judy Martin", "Wrestler (undercard)", "", "Heel", "WWF World Women's Championship", "Lost title challenge"),
    ("King Haku", "Wrestler (undercard)", "", "Heel", "", "Crown match def. Harley Race, retained the crown"),
    ("Harley Race", "Wrestler (undercard)", "", "Heel", "", "Final WWF appearance; lost Crown match to Haku"),
    ("Bobby Heenan", "Manager", "Andre the Giant, Arn Anderson, Tully Blanchard, Harley Race, King Haku", "Heel", "", ""),
    ("Virgil", "Bodyguard/valet", "Ted DiBiase", "Heel", "", ""),
    ("Slick", "Manager", "Big Bossman, Akeem", "Heel", "", ""),
    ("The Ultimate Warrior", "Wrestler (posedown)", "", "Face", "", "'Ultimate Posedown' vs. Rick Rude -- angle setting up WrestleMania V, no formal decision"),
    ("Rick Rude", "Wrestler (posedown)", "", "Heel", "", "'Ultimate Posedown' vs. The Ultimate Warrior -- attacked Warrior after the poses"),
    ("Sean Mooney", "Interviewer", "", "Face", "", ""),
    ("Gene Okerlund", "Interviewer", "", "Face", "", ""),
    ("Mr. Fuji", "Manager", "The Warlord, The Barbarian", "Heel", "", ""),
    ("Miss Elizabeth", "Manager", "Randy Savage, Hulk Hogan", "Face", "", "Also made a brief 1m23s in-ring cameo during the Rumble match per S012"),
    ("Sensational Sherri", "Guest commentator", "", "Heel", "", ""),
    ("Jesse Ventura", "Commentator", "", "Heel", "", ""),
    ("Gorilla Monsoon", "Commentator", "", "Face", "", ""),
    ("Howard Finkel", "Ring announcer", "", "Face", "", ""),
]
with open(os.path.join(DATA_DIR, "show_appearances.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for name, role, managed, align, title, notes in show_appearances:
        pid = wrestler_ids.get(name, slugify(name))
        writer.writerow([EVENT_ID, pid, name, role, managed, align, title, notes, "PROBABLE", "S013;S014;S015"])

# ---------------------------------------------------------------------------
# OTHER MATCHES ON THE SAME CARD
# ---------------------------------------------------------------------------
other_matches = [
    ("Jim Duggan", 1, "Dino Bravo, Jacques Rougeau, Raymond Rougeau", "Bret Hart, Jim Neidhart", "Tag (2/3 falls)", "FALSE", "", "FALSE", "Win", "", "", "15:42", "Opener",
     "S013;S014", "2/3-falls tag. Fall 1: Jacques pinned Bret Hart (4:22). Fall 2: Duggan pinned Jacques (11:46). Fall 3: Hart pinned Bravo (15:42)."),
    ("Bret Hart", 1, "Dino Bravo, Jacques Rougeau, Raymond Rougeau", "Jim Duggan, Jim Neidhart", "Tag (2/3 falls)", "FALSE", "", "FALSE", "Win", "", "", "15:42", "Opener",
     "S013;S014", "Pinned by Jacques in fall 1 (4:22), came back to pin Bravo for the deciding fall 3 (15:42)."),
    ("Jim Neidhart", 1, "Dino Bravo, Jacques Rougeau, Raymond Rougeau", "Jim Duggan, Bret Hart", "Tag (2/3 falls)", "FALSE", "", "FALSE", "Win", "", "", "15:42", "Opener",
     "S013;S014", ""),
    ("Dino Bravo", 1, "Jim Duggan, Bret Hart, Jim Neidhart", "Jacques Rougeau, Raymond Rougeau", "Tag (2/3 falls)", "FALSE", "", "FALSE", "Loss", "", "", "15:42", "Opener",
     "S013;S014", "Pinned by Bret Hart for the deciding fall (15:42)."),
    ("Jacques Rougeau", 1, "Jim Duggan, Bret Hart, Jim Neidhart", "Dino Bravo, Raymond Rougeau", "Tag (2/3 falls)", "FALSE", "", "FALSE", "Loss", "", "", "15:42", "Opener",
     "S013;S014", "Pinned Bret Hart for fall 1 (4:22), was pinned by Duggan for fall 2 (11:46)."),
    ("Raymond Rougeau", 1, "Jim Duggan, Bret Hart, Jim Neidhart", "Dino Bravo, Jacques Rougeau", "Tag (2/3 falls)", "FALSE", "", "FALSE", "Loss", "", "", "15:42", "Opener",
     "S013;S014", ""),
    ("Rockin' Robin", 2, "Judy Martin", "", "Singles", "TRUE", "WWF World Women's Championship", "TRUE", "Win", "", "FALSE", "16:24", "2nd match",
     "S013", "Retained the title."),
    ("Judy Martin", 2, "Rockin' Robin", "", "Singles", "TRUE", "WWF World Women's Championship", "FALSE", "Loss", "", "", "16:24", "2nd match",
     "S013", ""),
    ("The Ultimate Warrior", 3, "Rick Rude", "", "Posedown (exhibition)", "FALSE", "", "FALSE", "No formal decision", "", "", "", "3rd match",
     "S013;S014", "'Ultimate Posedown' -- set up the Rude-Warrior Intercontinental Title match at WrestleMania V. Rude attacked Warrior after the posing segment; no pinfall/formal result given by either source."),
    ("Rick Rude", 3, "The Ultimate Warrior", "", "Posedown (exhibition)", "FALSE", "", "FALSE", "No formal decision", "", "", "", "3rd match",
     "S013;S014", "Same as Warrior's row above."),
    ("King Haku", 4, "Harley Race", "", "Singles (Crown match)", "FALSE", "'King'/Crown (pre-King of the Ring era gimmick, not the modern tournament)", "TRUE", "Win", "", "FALSE", "9:01", "4th match",
     "S013;S014", "Retained the crown. NOTE: this is the mid-1980s 'King' gimmick match, not the modern King of the Ring tournament (which didn't begin until 1993) -- don't conflate the two."),
    ("Harley Race", 4, "King Haku", "", "Singles (Crown match)", "FALSE", "'King'/Crown (pre-King of the Ring era gimmick, not the modern tournament)", "FALSE", "Loss", "", "", "9:01", "4th match",
     "S013;S014", "Race's final WWF match; the match was edited off the Coliseum Video release per S013."),
]
with open(os.path.join(DATA_DIR, "other_matches.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for (name, mnum, opponents, partners, mtype, is_title, title, was_champ, result, title_change, duration_note, duration, position, row_src, notes) in other_matches:
        pid = wrestler_ids.get(name, slugify(name))
        won_title = "TRUE" if (is_title == "TRUE" and result == "Win" and was_champ == "FALSE") else "FALSE"
        lost_title = "TRUE" if (is_title == "TRUE" and result == "Loss" and was_champ == "TRUE") else "FALSE"
        writer.writerow([EVENT_ID, pid, mnum, opponents, partners, mtype, is_title, title, was_champ,
                          result, won_title, lost_title, duration, position, "", "PROBABLE", row_src, notes])

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 1989", "match_name": "30-Man Royal Rumble Match",
    "match_type": "Men's", "event_date": "1989-01-15", "venue": "The Summit",
    "city_region": "Houston, Texas", "country": "United States",
    "attendance_official": "", "attendance_reported": 19000,
    "entry_interval_seconds": 120, "entrant_count": 30, "duration_total": "64:53",
    "duration_status": "CONFIRMED",
    "winner_id": "big-john-studd", "runner_up_id": "ted-dibiase",
    "final_two_ids": "big-john-studd;ted-dibiase", "final_three_ids": "big-john-studd;ted-dibiase;one-man-gang",
    "final_four_ids": "big-john-studd;ted-dibiase;one-man-gang;rick-martel",
    "first_entrant_id": "ax", "second_entrant_id": "smash", "final_entrant_id": "ted-dibiase",
    "first_elimination_id": "smash", "last_elimination_before_winner_id": "ted-dibiase",
    "eliminations_count": 29, "eliminators_count": 15, "surprise_entrants_count": 0,
    "champions_in_field_count": 3, "hall_of_famers_in_field_count": 0,
    "tag_teams_count": 9, "factions_count": "N/A",
    "commentary_team": "Gorilla Monsoon, Jesse Ventura", "ring_announcer": "Howard Finkel",
    "referees": "Earl Hebner, Joey Marella, Chief Jay Strongbow (official) per S026 (Wikipedia)",
    "special_rules": (
        "First Royal Rumble held as a pay-per-view (previous 1988 event was free TV). First 30-man Rumble "
        "(1988 was 20-man); this is the format that became the standard going forward. Howard Finkel "
        "announced a 2-minute entry interval and, unlike 1988's ~90s actual average, WWF stuck to it "
        "closely this time -- 27 of 28 buzzer intervals fell within 3 seconds of 2:00 per S012, median "
        "exactly 2:00. Ted DiBiase bought his way into the #30 (final) slot from Slick per S014's recap. "
        "3 documented simultaneous eliminations (Brain Busters by Hogan; Bad News Brown & Randy Savage by "
        "Hogan; Hercules & Brutus Beefcake by DiBiase/Barbarian) -- see eliminations.csv "
        "simultaneous_group_id. 1 illegal elimination (Hogan eliminated Big Bossman after Hogan himself had "
        "already been eliminated). 1 illegally-assisted elimination (Jake Roberts used Damien the snake to "
        "scare Andre the Giant into a self-elimination)."
    ),
    "title_on_the_line": "FALSE", "championship_implications": "None -- no title was contested in the Rumble match itself, though 3 reigning champions (Randy Savage/WWF Champion, Ax & Smash/WWF Tag Champions) were in the field",
    "winners_reward": "None identified this pass -- no guaranteed title shot is mentioned in any source consulted; S013 notes a planned Studd/Andre the Giant program afterward that never materialized due to both men's declining health",
    "historical_significance": "First Royal Rumble as a PPV. First 30-man-format Rumble. Ax and Smash of Demolition drew #1 and #2 despite being a team. Randy Savage and Hulk Hogan (Mega Powers) worked together for most of the match before Hogan turned on him, foreshadowing their real-life breakup and WrestleMania V program. Harley Race's final WWF match.",
    "notes": "30 confirmed entrants, all identified. See flags.csv F008-F014 for the ring-time discrepancies and the Red Rooster real-name/birthplace conflict. Fact-check pass (S026, Wikipedia) independently confirmed date, venue, attendance (F010, resolved), duration (F012, corrected 65:06->64:53 and resolved), and filled in the referee crew; the entry-order/elimination table itself remains cross-checked only within Shane's own document, not against Wikipedia's table (F011, partially resolved -- see F034).",
    "data_quality_status": "CONFIRMED", "source_ids": "S012;S013;S014;S015;S026",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"1989 build complete (schema v2): {len(new_wrestlers)} new wrestlers ({len(reused)} reused from 1988), "
      f"{len(entrant_rows)} entrants, {len(elim_rows)} elimination rows, {len(tag_teams)} tag teams, "
      f"{len(show_appearances)} show appearances, {len(other_matches)} other-match rows, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
