# -*- coding: utf-8 -*-
"""
Builds all rows for the 1988 Royal Rumble (the first-ever Rumble) — schema v2.

SOURCES CONSULTED THIS PASS (see sources.csv for full registry):
  S001 Wikipedia "Royal Rumble (1988)"            tier 10
  S002 Cagematch "Royal Rumble Match 1988"          tier 4
  S003 Cagematch "WWF Royal Rumble 1988" event page tier 4
  S004 Shane's original Entrant_Stats.xlsx research  tier 11
  S005 Wikipedia "Boris Zhukov"                     tier 10
  S006 Wikipedia "Jim Duggan"                        tier 10
  S007 Wikipedia "One Man Gang"                       tier 10

WHAT WAS ACTUALLY CROSS-CHECKED THIS PASS (be honest about scope):
  - Event facts (date/venue/attendance/winner/participant list) — CONFIRMED,
    S001 + S002/S003 + S004 independently agree.
  - Full entry/elimination order + ring times — CONFIRMED. S001's structured
    table and S004 (Shane's independently compiled research) agree exactly
    on all 20 entries, all 20 elimination numbers, and every ring time down
    to the second. S002 corroborates the winner, the full participant list,
    and the first elimination (Butch Reed by Jake Roberts) but does not
    publish a full structured order/timing table of its own.
  - Bios for 3 of 43 people were individually cross-checked against a second
    source (Jim Duggan, One Man Gang, Boris Zhukov) as a methodology sample.
    Duggan and One Man Gang matched cleanly -> CONFIRMED. Boris Zhukov's DOB
    conflicts between sources -> CONFLICTING, logged in flags.csv, left
    blank rather than guessed.
  - The other 40 people's biographical fields (DOB, height/weight, HOF year,
    birthplace) are PROBABLE: sourced only from Shane's original research so
    far, not yet independently cross-checked. This is flagged as an open
    item, not silently presented as confirmed. See flags.csv.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from schema import (
    SOURCES_FIELDS, FLAGS_FIELDS, WRESTLERS_FIELDS, EVENTS_FIELDS,
    ENTRANTS_FIELDS, ELIMINATIONS_FIELDS, TAG_TEAMS_FIELDS,
    SHOW_APPEARANCES_FIELDS, slugify, mmss_to_seconds,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EVENT_ID = "RR1988M"

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
sources = [
    ("S001", "Wikipedia: Royal Rumble (1988)", "reference_site", "https://en.wikipedia.org/wiki/Royal_Rumble_(1988)", 10, "Wikipedia/reference", "2026-09-15", "Event card + full entrant table"),
    ("S002", "Cagematch: Royal Rumble Match 1988", "database", "https://www.cagematch.net/?id=111&nr=20858", 4, "Cagematch", "2026-09-15", "Participant list, winner, WON rating; no structured order/timing table available via fetch"),
    ("S003", "Cagematch: WWF Royal Rumble 1988 event page", "database", "https://www.cagematch.net/?id=1&nr=1755", 4, "Cagematch", "2026-09-15", "Event page; not fully fetched due to rate limiting, referenced via search results only"),
    ("S004", "Shane's original research (Entrant_Stats.xlsx, '1988' tab)", "original_document", "", 11, "Original research document", "2026-09-15", "Base layer for entrant detail; treated as PROBABLE until independently cross-checked per record"),
    ("S005", "Wikipedia: Boris Zhukov", "reference_site", "https://en.wikipedia.org/wiki/Boris_Zhukov", 10, "Wikipedia/reference", "2026-09-15", "Bio cross-check sample; DOB conflicts with S004"),
    ("S006", "Wikipedia: Jim Duggan", "reference_site", "https://en.wikipedia.org/wiki/Jim_Duggan", 10, "Wikipedia/reference", "2026-09-15", "Bio cross-check sample; matches S004"),
    ("S007", "Wikipedia: One Man Gang", "reference_site", "https://en.wikipedia.org/wiki/One_Man_Gang", 10, "Wikipedia/reference", "2026-09-15", "Bio cross-check sample; matches S004"),
    ("S008", "Cageside Seats: 'Match Times: The 1988 Royal Rumble' (2014)", "contemporary_publication", "https://www.cagesideseats.com/2014/1/21/5329040/match-times-the-1988-royal-rumble", 9, "Contemporary wrestling publication", "2026-09-15", "Independent frame-by-frame timing analysis; also present verbatim in Shane's original doc under a 'Cageside' heading -- fetched live and confirmed to match. Survival times for all 20 entrants agree with S001/S004 within 1-4 seconds (rounding, not a real conflict); total match duration 33:24 sourced from here."),
    ("S009", "Dan Wahlers, 'History of the Royal Rumble' -- 1988 chapter", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15", "Preserved in Shane's original doc; no live URL captured during original scrape. Byline 'Dan Wahlers' given in the doc's own section heading. Gives attendance as 16,200 -- conflicts with S001/S011's 18,000, see flags.csv F007."),
    ("S010", "Scott Keith, Kayfabe Memories review of 1988 Royal Rumble", "contemporary_publication", "", 9, "Contemporary wrestling publication", "2026-09-15", "Preserved in Shane's original doc; byline '- Scott Keith' given directly in-text. Detailed blow-by-blow recap of the Rumble match and full card."),
    ("S011", "KB's Wrestling Reviews: 'Royal Rumble Count-Up: 1988'", "contemporary_publication", "https://kbwrestlingreviews.com/2011/01/08/royal-rumble-count-up-1988/", 9, "Contemporary wrestling publication", "2026-09-15", "Independently corroborates 18,000 attendance, venue and date."),
]
with open(os.path.join(DATA_DIR, "sources.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(sources)

# ---------------------------------------------------------------------------
# FLAGS (open questions / conflicts logged now, resolved later)
# ---------------------------------------------------------------------------
flags = [
    ("F001", EVENT_ID, "wrestlers", "boris-zhukov", "dob", "conflicting_sources",
     "Shane's research gives DOB 1959-12-13 (consistent with his stated age '28 Years, 1 Months' at the 1988 event). Wikipedia gives DOB 1959-01-29. These cannot both be correct. Left blank in wrestlers.csv pending a tie-breaking source (e.g. a newspaper birth record or a source that cites its own basis).",
     "S004;S005", "open", "2026-09-15"),
    ("F002", EVENT_ID, "wrestlers", "boris-zhukov", "billed_weight_kg_at_event", "unverified",
     "Shane's research: 135kg billed at the 1988 event. Wikipedia infobox (current, undated): 115kg (254lb). Not necessarily contradictory since WWF billed weights changed across a wrestler's run and Wikipedia's infobox isn't tied to a specific date -- but the 1988-specific figure isn't independently confirmed. Kept Shane's value as PROBABLE.",
     "S004;S005", "open", "2026-09-15"),
    ("F003", EVENT_ID, "wrestlers", "*", "real_name;dob;billed_height_m_at_event;billed_weight_kg_at_event;birthplace;hall_of_fame_year", "unverified",
     "40 of the 43 people in this event (all except boris-zhukov, jim-duggan, one-man-gang) have biographical data sourced ONLY from Shane's original document (S004) so far. Status set to PROBABLE, not CONFIRMED. Independent cross-checking against Cagematch/ProFightDB wrestler profiles or Wikipedia is a planned follow-up, not yet done for this pass.",
     "S004", "open", "2026-09-15"),
    ("F004", EVENT_ID, "sources", "S003;profightdb", "n/a", "unverified",
     "Cagematch event-card page (S003) and ProFightDB's 1988 Royal Rumble page both failed to load this session -- Cagematch returned HTTP 429 (rate limited) after the first successful fetch, and ProFightDB is stuck in an http/https redirect loop via the fetch tool. Worth retrying in a later session; would add another tier-4/5 cross-check.",
     "S002;S003", "open", "2026-09-15"),
    ("F005", EVENT_ID, "entrances/moves/near_eliminations", "*", "n/a", "out_of_scope_no_tool",
     "No video/computer-vision tool is connected in this session. entrances.csv, moves.csv, near_eliminations.csv, and eliminations.csv:location_side are left empty for every 1988 record rather than estimated from text descriptions. Populating these requires footage review.",
     "", "open", "2026-09-15"),
    ("F006", EVENT_ID, "eliminations", "dino-bravo;one-man-gang", "eliminator_wrestler_id", "unverified",
     "The structured record (S001 Wikipedia table + S004 Shane's research, agreeing) credits One Man Gang with eliminating Dino Bravo, and Jim Duggan with eliminating One Man Gang (the match-winning elimination). Scott Keith's blow-by-blow recap (S010) tells a more specific story: the final sequence was Duggan alone vs. Gang+Bravo double-teaming him; their second double-team attempt 'backfired' and Bravo went out (implying Duggan/the botched spot, not a clean Gang elimination); then 'Duggan ducks one last desperate Gang charge' and Gang goes out (reads more like a self-elimination off a dodged charge than a clean takedown). Kept the structured credits as CONFIRMED (2-source agreement on WHO gets the elimination in the record books), but flagged both eliminations as is_disputed=TRUE with the recap's account in notes -- this is exactly the credited-vs-assisted nuance the spec asks to preserve, not resolve by picking one.",
     "S001;S004;S010", "open", "2026-09-15"),
    ("F007", EVENT_ID, "events", EVENT_ID, "attendance", "conflicting_sources",
     "Two independent sources (S001 Wikipedia, S011 KB's Wrestling Reviews) agree on 18,000 attendance -- CONFIRMED and used as attendance_reported. Dan Wahlers' history (S009, in Shane's original doc) gives 16,200. Since 2 sources outweigh 1, 18,000 is treated as confirmed, but 16,200 is kept in attendance_official rather than discarded -- it may reflect a distinct paid/gate figure rather than a simple error; not independently resolved either way.",
     "S001;S009;S011", "open", "2026-09-15"),
    ("F036", EVENT_ID, "wrestlers", "tito-santana", "birthplace", "conflicting_sources",
     "Fact-check pass: Shane's document (S004) gives birthplace as Tocula, Mexico. Wikipedia (S022) gives "
     "Mission, Texas, USA. Real name (Merced Solis/Solís) and DOB (1953-05-10) both independently confirmed "
     "and matching -- only birthplace disagrees. Kept existing value pending a tiebreaking third source.",
     "S004;S022", "open", "2026-09-15"),
    ("F037", EVENT_ID, "wrestlers", "jim-neidhart", "birthplace", "conflicting_sources",
     "Fact-check pass: Shane's document (S004) gives birthplace as Tampa, Florida. Wikipedia (S022) gives "
     "Montebello, California. Real name and DOB both independently confirmed and matching -- only birthplace "
     "disagrees. Kept existing value pending a tiebreaking third source.",
     "S004;S022", "open", "2026-09-15"),
    ("F038", EVENT_ID, "wrestlers", "sam-houston", "birthplace", "conflicting_sources",
     "Fact-check pass: Shane's document (S004) gives birthplace as Tampa, Florida. Wikipedia (S022) gives "
     "Waco, Texas. Real name and DOB both independently confirmed and matching -- only birthplace disagrees. "
     "Kept existing value pending a tiebreaking third source.",
     "S004;S022", "open", "2026-09-15"),
    ("F039", EVENT_ID, "wrestlers", "danny-davis", "real_name;dob", "conflicting_sources",
     "Fact-check pass: substantial disagreement, not a simple spelling variant. Shane's document (S004) gives "
     "real name 'Dan Marsh', DOB 1956-05-28, birthplace Toronto, Ontario, Canada. Wikipedia (S022) gives real "
     "name 'Daniel Davis', DOB 1956-03-28 (day/month swapped from S004's figure), birthplace Massachusetts "
     "(state only, no city). Both real_name and dob kept at existing (S004) values pending a tiebreaking "
     "third source; birthplace left as-is since Wikipedia's figure is not more specific than what's on file.",
     "S004;S022", "open", "2026-09-15"),
    ("F040", EVENT_ID, "wrestlers", "nikolai-volkoff", "birthplace", "conflicting_sources",
     "Fact-check pass: Shane's document (S004) gives birthplace as 'Socialist Republic of Croatia, SFRY' "
     "(country/political-entity level, no city). Wikipedia (S022) gives 'Split, Croatia (then PR Croatia, "
     "FPR Yugoslavia)' -- same country, but adds a specific city (Split) and a slightly different era name "
     "for the political entity. Real name (Josip Nikolai/Hrvoje Peruzovic -- Wikipedia notes 'Nikolai' is a "
     "kayfabe-invented middle name, not on his birth certificate) and DOB both otherwise consistent. Likely "
     "added precision rather than a true disagreement, but flagged rather than silently merged since the "
     "political-entity naming differs and wasn't independently cross-checked.",
     "S004;S022", "open", "2026-09-15"),
    ("F041", EVENT_ID, "wrestlers", "b-brian-blair", "dob", "conflicting_sources",
     "Fact-check pass: Shane's document (S004) gives DOB 1954-01-12. Wikipedia (S022) gives 1957-01-12 -- "
     "same day/month, year disagrees by 3 years. Real name and birthplace both independently confirmed and "
     "matching. Kept existing value pending a tiebreaking third source.",
     "S004;S022", "open", "2026-09-15"),
    ("F042", EVENT_ID, "wrestlers", "dino-bravo", "birthplace", "conflicting_sources",
     "Fact-check pass: Shane's document (S004) gives birthplace as Laval, Quebec, Canada. Wikipedia (S022) "
     "gives Campobasso, Molise, Italy (his actual birth country before emigrating). Not necessarily a true "
     "contradiction -- Laval is likely his billed/adopted hometown rather than birthplace -- but flagged "
     "since both purport to answer the same 'birthplace' field. Kept existing (Laval) value.",
     "S004;S022", "open", "2026-09-15"),
    ("F043", EVENT_ID, "wrestlers", "haku", "dob", "conflicting_sources",
     "Fact-check pass: Shane's document (S004) gives DOB 1959-02-03. Wikipedia (S022) gives 1959-02-10 -- "
     "same year/month, day disagrees. Real name and birthplace both independently confirmed and matching. "
     "Kept existing value pending a tiebreaking third source.",
     "S004;S022", "open", "2026-09-15"),
    ("F044", EVENT_ID, "wrestlers", "gene-okerlund", "dob;birthplace", "conflicting_sources",
     "Fact-check pass: Shane's document (S004) gives DOB 1942-11-29, birthplace Robbinsdale, Minnesota. "
     "Wikipedia (S022) gives DOB 1942-12-19 and birthplace Brookings, South Dakota -- both fields disagree. "
     "Real name independently confirmed and matching. Both fields kept at existing (S004) values pending a "
     "tiebreaking third source.",
     "S004;S022", "open", "2026-09-15"),
    ("F045", EVENT_ID, "wrestlers", "howard-finkel", "birthplace", "conflicting_sources",
     "Fact-check pass: Shane's document (S004) gives birthplace as New York City, New York. Wikipedia (S022) "
     "gives Newark, New Jersey -- a genuine city-level disagreement, not a rounding/precision difference. "
     "Real name and DOB both independently confirmed and matching. Kept existing value pending a tiebreaking "
     "third source.",
     "S004;S022", "open", "2026-09-15"),
]
with open(os.path.join(DATA_DIR, "flags.csv"), "a", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(flags)

# ---------------------------------------------------------------------------
# WRESTLERS (master roster)
# ---------------------------------------------------------------------------
# ring_name, real_name, real_name_status, gender, dob, dob_status, deceased_date,
# birthplace, birthplace_status, nationality, debut_year_company, hof_year,
# aliases, wrestling_style, notes, source_ids
wrestlers = [
    ("Bret Hart", "Bret Hart", "PROBABLE", "M", "1957-07-02", "PROBABLE", "", "Calgary, Alberta, Canada", "PROBABLE", "Canadian", "", "2006", "", "", "", "S004"),
    ("Tito Santana", "Merced Solis", "PROBABLE", "M", "1953-05-10", "PROBABLE", "", "Tocula, Mexico", "PROBABLE", "Mexican-American", "", "2004", "", "", "", "S004"),
    ("Butch Reed", "Bruce Reed", "PROBABLE", "M", "1954-07-11", "PROBABLE", "", "Kansas City, Missouri", "PROBABLE", "American", "", "", "", "", "", "S004"),
    ("Jim Neidhart", "James Neidhart", "PROBABLE", "M", "1955-02-08", "PROBABLE", "", "Tampa, Florida", "PROBABLE", "American", "", "", "", "", "", "S004"),
    ("Jake Roberts", "Aurelian Smith Jr.", "PROBABLE", "M", "1955-05-30", "PROBABLE", "", "Gainesville, Texas", "PROBABLE", "American", "", "2014", "", "", "", "S004"),
    ("Harley Race", "Harley Leland Race", "PROBABLE", "M", "1943-04-11", "PROBABLE", "", "Quitman, Missouri", "PROBABLE", "American", "", "2004", "", "", "", "S004"),
    ("Jim Brunzell", "James Brunzell", "PROBABLE", "M", "1949-08-13", "PROBABLE", "", "White Bear Lake, Minnesota", "PROBABLE", "American", "", "", "", "", "", "S004"),
    ("Sam Houston", "Michael Maurice Smith", "PROBABLE", "M", "1963-10-11", "PROBABLE", "", "Tampa, Florida", "PROBABLE", "American", "", "", "", "", "", "S004"),
    ("Danny Davis", "Dan Marsh", "PROBABLE", "M", "1956-05-28", "PROBABLE", "", "Toronto, Ontario, Canada", "PROBABLE", "Canadian", "", "", "", "", "", "S004"),
    ("Boris Zhukov", "James Kirk Harrell", "CONFIRMED", "M", "", "CONFLICTING", "", "Roanoke, Virginia", "PROBABLE", "American", "", "", "", "", "DOB conflicts between sources -- see flags.csv F001. Billed as Soviet (gimmick), real background American.", "S004;S005"),
    ("Don Muraco", "Donald Muraco", "PROBABLE", "M", "1949-09-10", "PROBABLE", "", "Sunset Beach, Hawaii", "PROBABLE", "American", "", "2004", "", "", "", "S004"),
    ("Nikolai Volkoff", "Josip Nikolai Peruzović", "PROBABLE", "M", "1947-10-14", "PROBABLE", "2018-07-29", "Socialist Republic of Croatia, SFRY", "PROBABLE", "Croatian-American", "", "2005", "", "", "", "S004"),
    ("Jim Duggan", "James Edward Duggan Jr.", "CONFIRMED", "M", "1954-01-14", "CONFIRMED", "", "Glens Falls, New York", "CONFIRMED", "American", "", "2011", "", "", "Winner of the first-ever Royal Rumble match. Weight: Shane's research says 120kg billed at event; Wikipedia infobox (undated) says 122kg -- 2kg variance not treated as a real conflict (likely lb/kg rounding, both ~264-270lb).", "S004;S006"),
    ("Ron Bass", "Ronald Heard", "PROBABLE", "M", "1948-12-21", "PROBABLE", "", "Harrisburg, Arkansas", "PROBABLE", "American", "", "", "", "", "", "S004"),
    ("B. Brian Blair", "Brian Leslie Blair", "PROBABLE", "M", "1954-01-12", "PROBABLE", "", "Gary, Indiana", "PROBABLE", "American", "", "", "", "", "", "S004"),
    ("Hillbilly Jim", "James Morris", "PROBABLE", "M", "1952-07-05", "PROBABLE", "", "Louisville, Kentucky", "PROBABLE", "American", "", "", "", "", "", "S004"),
    ("Dino Bravo", "Aldolfo Bresciano", "PROBABLE", "M", "1948-08-06", "PROBABLE", "1993-03-10", "Laval, Quebec, Canada", "PROBABLE", "Canadian", "", "", "", "", "Murder in March 1993 remains unsolved.", "S004"),
    ("The Ultimate Warrior", "James Brian Hellwig", "PROBABLE", "M", "1959-06-16", "PROBABLE", "2014-04-08", "Crawfordsville, Indiana", "PROBABLE", "American", "", "2014", "", "", "HOF induction and death both occurred in April 2014, days apart.", "S004"),
    ("One Man Gang", "George Gray", "CONFIRMED", "M", "1960-02-12", "CONFIRMED", "", "Chicago, Illinois", "CONFIRMED", "American", "", "", "Akeem", "", "Repackaged as 'Akeem the African Dream' later in 1988. No HOF induction found on Wikipedia; Shane's doc also has HOF n/a -- consistent.", "S004;S007"),
    ("Junkyard Dog", "Sylvester Ritter", "PROBABLE", "M", "1952-12-13", "PROBABLE", "1998-06-02", "Wadesboro, North Carolina", "PROBABLE", "American", "", "2004", "", "", "", "S004"),
    ("Ricky Steamboat", "Richard Henry Blood", "PROBABLE", "M", "1953-02-28", "PROBABLE", "", "West Point, New York", "PROBABLE", "American", "", "2009", "", "", "", "S004"),
    ("Rick Rude", "Richard Erwin Rood", "PROBABLE", "M", "1958-12-07", "PROBABLE", "1999-04-20", "Robbinsdale, Minnesota", "PROBABLE", "American", "", "", "", "", "", "S004"),
    ("Noriyo Tateno", "Noriyo Tateno", "PROBABLE", "F", "1965-12-01", "PROBABLE", "", "Ashikaga, Tochigi, Japan", "PROBABLE", "Japanese", "", "", "", "", "Half of The Jumping Bomb Angels", "S004"),
    ("Itsuki Yamazaki", "Itsuki Yamazaki", "PROBABLE", "F", "1966-01-03", "PROBABLE", "", "Hyogo, Japan", "PROBABLE", "Japanese", "", "", "", "", "Half of The Jumping Bomb Angels", "S004"),
    ("Leilani Kai", "Patty Seymour", "PROBABLE", "F", "1960-01-23", "PROBABLE", "", "Tampa, Florida", "PROBABLE", "American", "", "", "", "", "", "S004"),
    ("Judy Martin", "Judy Hardee", "PROBABLE", "F", "1955-10-08", "PROBABLE", "", "Columbia, South Carolina", "PROBABLE", "American", "", "", "", "", "", "S004"),
    ("Jimmy Hart", "James Ray Hart", "PROBABLE", "M", "1944-01-01", "PROBABLE", "", "Jackson, Mississippi", "PROBABLE", "American", "", "2005", "", "", "Manager, 'The Mouth of the South'", "S004"),
    ("Haku", "Tonga 'Uli'uli Fifita", "PROBABLE", "M", "1959-02-03", "PROBABLE", "", "Nukuʻalofa, Tonga", "PROBABLE", "Tongan", "", "", "Meng;King Tonga", "", "", "S004"),
    ("Tama", "Samuel Fatu", "PROBABLE", "M", "1965-10-11", "PROBABLE", "", "San Francisco, California", "PROBABLE", "American", "", "", "", "", "", "S004"),
    ("Jim Powers", "James Manley", "PROBABLE", "M", "1958-01-04", "PROBABLE", "", "East Rutherford, New Jersey", "PROBABLE", "American", "", "", "", "", "", "S004"),
    ("Paul Roma", "Paul Centopani", "PROBABLE", "M", "1960-04-29", "PROBABLE", "", "Kensington, New York", "PROBABLE", "American", "", "", "", "", "", "S004"),
    ("Bobby Heenan", "Raymond Louis Heenan", "PROBABLE", "M", "1944-11-01", "PROBABLE", "2017-09-17", "Chicago, Illinois", "PROBABLE", "American", "", "2004", "", "", "Manager, 'The Brain'", "S004"),
    ("Frenchy Martin", "Jean Gagné", "PROBABLE", "M", "1950-05-25", "PROBABLE", "", "Quebec City, Quebec", "PROBABLE", "Canadian", "", "", "", "", "Manager", "S004"),
    ("Jack Tunney", "John Tunney Jr.", "PROBABLE", "M", "1935-01-01", "UNCERTAIN", "2009-01-13", "Toronto, Ontario, Canada", "PROBABLE", "Canadian", "", "", "", "", "On-screen WWF President; DOB year only, day/month uncertain in Shane's source", "S004"),
    ("Hulk Hogan", "Terry Gene Bollea", "PROBABLE", "M", "1953-08-11", "PROBABLE", "", "Augusta, Georgia", "PROBABLE", "American", "", "2005", "", "", "WWF Champion at time of event; not in the Rumble match itself", "S004"),
    ("Andre the Giant", "André René Roussimoff", "PROBABLE", "M", "1946-05-19", "PROBABLE", "1993-01-27", "Grenoble, France", "PROBABLE", "French", "", "1993", "", "", "", "S004"),
    ("Ted DiBiase", "Theodore Marvin DiBiase", "PROBABLE", "M", "1954-01-18", "PROBABLE", "", "Miami, Florida", "PROBABLE", "American", "", "2010", "", "", "", "S004"),
    ("Virgil", "Michael Jones", "PROBABLE", "M", "1962-06-13", "PROBABLE", "", "Nashville, Tennessee", "PROBABLE", "American", "", "", "Vincent", "", "Bodyguard to Ted DiBiase", "S004"),
    ("Vince McMahon", "Vincent Kennedy McMahon", "PROBABLE", "M", "1945-08-24", "PROBABLE", "", "Pinehurst, North Carolina", "PROBABLE", "American", "", "", "", "", "Commentator", "S004"),
    ("Jesse Ventura", "James George Janos", "PROBABLE", "M", "1951-07-15", "PROBABLE", "", "Minneapolis, Minnesota", "PROBABLE", "American", "", "2004", "", "", "Commentator", "S004"),
    ("Gene Okerlund", "Eugene Arthur Okerlund", "PROBABLE", "M", "1942-11-29", "PROBABLE", "2019-01-02", "Robbinsdale, Minnesota", "PROBABLE", "American", "", "2006", "", "", "Interviewer", "S004"),
    ("Craig DeGeorge", "Craig DeGeorge", "PROBABLE", "M", "", "UNKNOWN", "", "", "UNKNOWN", "", "", "", "", "", "Interviewer; DOB/birthplace unknown", "S004"),
    ("Howard Finkel", "Howard Finkel", "PROBABLE", "M", "1950-06-07", "PROBABLE", "2020-04-16", "New York City, New York", "PROBABLE", "American", "", "2009", "", "", "Ring announcer", "S004"),
]

wrestler_ids = {}
with open(os.path.join(DATA_DIR, "wrestlers.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in wrestlers:
        ring_name = row[0]
        wid = slugify(ring_name)
        wrestler_ids[ring_name] = wid
        writer.writerow([wid] + list(row))

# ---------------------------------------------------------------------------
# ENTRANTS in the 20-man Royal Rumble match, in entry order
# ---------------------------------------------------------------------------
# name, entry, elim_no(0=winner), elim_by[], elim_time, ring_time, elim_count,
# age, h, w, billed_from, champ, align, team
entrants_raw = [
    ("Bret Hart", 1, 8, ["Don Muraco"], "", "25:42", 1, "30 Years, 6 Months", 1.83, 106, "Calgary, Alberta, Canada", "", "Heel", "The Hart Foundation (w/ Jim Neidhart)"),
    ("Tito Santana", 2, 2, ["Bret Hart", "Jim Neidhart"], "", "10:41", 0, "34 Years, 8 Months", 1.88, 106, "Mission, Texas", "WWF Tag Team Champion (Strike Force)", "Face", ""),
    ("Butch Reed", 3, 1, ["Jake Roberts"], "3:18", "3:18", 0, "33 Years, 6 Months", 1.88, 119, "Warrensburg, Missouri", "", "Heel", ""),
    ("Jim Neidhart", 4, 6, ["Hillbilly Jim"], "", "19:06", 1, "32 Years, 11 Months", 1.88, 127, "Reno, Nevada", "", "Heel", "The Hart Foundation (w/ Bret Hart)"),
    ("Jake Roberts", 5, 10, ["One Man Gang"], "", "21:52", 2, "32 Years, 7 Months", 1.98, 113, "Stone Mountain, Georgia", "", "Face", ""),
    ("Harley Race", 6, 4, ["Don Muraco"], "", "10:03", 0, "44 Years, 9 Months", 1.85, 111, "Kansas City, Missouri", "", "Heel", ""),
    ("Jim Brunzell", 7, 5, ["Nikolai Volkoff"], "", "12:06", 1, "38 Years, 5 Months", 1.88, 107, "White Bear Lake, Minnesota", "", "Face", ""),
    ("Sam Houston", 8, 7, ["Ron Bass"], "", "14:39", 0, "24 Years, 3 Months", 1.88, 101, "Texas", "", "Face", ""),
    ("Danny Davis", 9, 13, ["Jim Duggan"], "", "17:51", 0, "31 Years, 7 Months", 1.78, 104, "Dover, New Hampshire", "", "Heel", ""),
    ("Boris Zhukov", 10, 3, ["Jake Roberts", "Jim Brunzell"], "2:33", "2:33", 0, "28 Years, 1 Months", 1.88, 135, "Soviet Union", "", "Heel", "The Bolsheviks (w/ Nikolai Volkoff)"),
    ("Don Muraco", 11, 17, ["Dino Bravo", "One Man Gang"], "", "16:16", 3, "38 Years, 4 Months", 1.91, 120, "Sunset Beach, Hawaii", "", "Face", ""),
    ("Nikolai Volkoff", 12, 11, ["Jim Duggan"], "", "11:40", 1, "40 Years, 3 Months", 1.93, 139, "Moscow, RSFSR, Soviet Union", "", "Heel", "The Bolsheviks (w/ Boris Zhukov)"),
    ("Jim Duggan", 13, 0, [], "", "14:43", 3, "34 Years, 0 Months", 1.91, 120, "Glens Falls, New York", "", "Face", ""),
    ("Ron Bass", 14, 16, ["Don Muraco"], "", "10:14", 1, "39 Years, 1 Months", 1.93, 131, "Pampa, Texas", "", "Heel", ""),
    ("B. Brian Blair", 15, 9, ["One Man Gang"], "", "5:50", 0, "34 Years, 0 Months", 1.85, 107, "Gary, Indiana", "", "Face", ""),
    ("Hillbilly Jim", 16, 12, ["One Man Gang"], "", "5:55", 1, "35 Years, 6 Months", 2.01, 150, "Mudlick, Kentucky", "", "Face", ""),
    ("Dino Bravo", 17, 18, ["One Man Gang"], "", "8:12", 3, "39 Years, 5 Months", 1.85, 120, "Montreal, Quebec, Canada", "", "Heel", ""),
    ("The Ultimate Warrior", 18, 14, ["Dino Bravo", "One Man Gang"], "", "3:51", 0, "28 Years, 7 Months", 1.88, 125, "Parts Unknown", "", "Face", ""),
    ("One Man Gang", 19, 19, ["Jim Duggan"], "", "6:50", 6, "27 Years, 11 Months", 2.06, 204, "Halstead Street, Chicago", "", "Heel", ""),
    ("Junkyard Dog", 20, 15, ["Dino Bravo"], "2:08", "2:08", 0, "35 Years, 1 Months", 1.91, 130, "Charlotte, North Carolina", "", "Face", ""),
]

FINAL_FOUR_ORDER = ["jim-duggan", "one-man-gang", "dino-bravo", "don-muraco"]  # winner, RU, 3rd, 4th by elim order desc

elim_rows = []
entrant_rows = []
sim_group_counter = 0

for (name, entry, elim_no, elim_by, elim_time, ring_time, elim_count, age, h, w, billed_from, champ, align, team) in entrants_raw:
    wid = wrestler_ids[name]
    is_winner = (elim_no == 0)
    ring_time_s = mmss_to_seconds(ring_time)

    if elim_by:
        elim_time_display = elim_time if elim_time else ring_time
        elim_time_s = mmss_to_seconds(elim_time_display)
        sim_group = ""
        if len(elim_by) > 1:
            sim_group_counter += 1
            sim_group = f"{EVENT_ID}-G{sim_group_counter}"
        for eliminator in elim_by:
            dispute_key = (name, eliminator)
            disputed_notes = {
                ("Dino Bravo", "One Man Gang"): (
                    "S010 (Scott Keith recap) describes this as a SECOND double-team attempt by "
                    "Bravo+Gang against Duggan that 'backfired' -- reads more like Bravo went out "
                    "as a result of the botched spot than a clean Gang elimination. Structured "
                    "sources (S001/S004) credit Gang outright; kept as the credited eliminator but "
                    "flagged. See flags.csv F006."
                ),
                ("One Man Gang", "Jim Duggan"): (
                    "S010 describes this as 'Duggan ducks one last desperate Gang charge' -- reads "
                    "as Gang going over on his own momentum (self-elimination) rather than a direct "
                    "takedown by Duggan. Structured sources (S001/S004) credit Duggan with the "
                    "match-winning elimination; kept as the credited eliminator but flagged. See "
                    "flags.csv F006."
                ),
            }.get(dispute_key)
            is_disputed = dispute_key in (("Dino Bravo", "One Man Gang"), ("One Man Gang", "Jim Duggan"))
            elim_method = {
                ("Dino Bravo", "One Man Gang"): "backfired double-team spot (per S010)",
                ("One Man Gang", "Jim Duggan"): "ducked charge / possible self-elimination (per S010)",
            }.get(dispute_key, "UNKNOWN")
            row_sources = "S001;S004;S008" + (";S010" if is_disputed else "")
            elim_rows.append({
                "event_id": EVENT_ID, "order_in_match": elim_no,
                "eliminated_wrestler_id": wid, "eliminator_wrestler_id": wrestler_ids[eliminator],
                "assisting_wrestler_ids": ";".join(wrestler_ids[e] for e in elim_by if e != eliminator),
                "entry_number_of_eliminated": entry, "entry_number_of_eliminator": "",
                "elimination_clock_time": elim_time_display, "elimination_clock_seconds": elim_time_s,
                "elimination_type": "over_top_rope", "elimination_method": elim_method,
                "location_side": "", "location_status": "UNKNOWN",
                "is_solo": "FALSE" if len(elim_by) > 1 else "TRUE",
                "is_shared": "TRUE" if len(elim_by) > 1 else "FALSE",
                "is_accidental": "UNKNOWN", "is_self_elimination": "UNCERTAIN" if dispute_key == ("One Man Gang", "Jim Duggan") else "FALSE",
                "is_storyline_related": "UNKNOWN", "was_already_incapacitated": "UNKNOWN",
                "is_disputed": "TRUE" if is_disputed else "FALSE", "simultaneous_group_id": sim_group,
                "data_quality_status": "CONFIRMED", "source_ids": row_sources,
                "notes": disputed_notes or "",
            })
    else:
        elim_time_display, elim_time_s = "", ""

    entrant_rows.append({
        "event_id": EVENT_ID, "wrestler_id": wid, "match_id": EVENT_ID,
        "entry_number": entry, "entry_number_status": "CONFIRMED",
        "ring_name_at_time": name, "name_displayed_at_event": name,
        "prior_rumble_appearances_count": 0, "rumble_appearance_no": 1,
        "is_first_rumble_appearance": "TRUE", "previous_rumble_year": "",
        "previous_rumble_result": "N/A", "previous_rumble_elimination_no": "",
        "is_rumble_debut": "TRUE", "is_company_debut": "UNKNOWN", "company_debut_date": "",
        "is_returning_wrestler": "FALSE", "absence_length": "",
        "age_at_event": age, "age_status": "UNKNOWN" if name == "Boris Zhukov" else "DERIVED",
        "billed_height_m_at_event": h, "billed_weight_kg_at_event": w,
        "billed_from_at_event": billed_from,
        "physical_status": "CONFIRMED" if name in ("Jim Duggan", "One Man Gang") else ("UNCERTAIN" if name == "Boris Zhukov" else "PROBABLE"),
        "alignment": align, "alignment_status": "PROBABLE",
        "gimmick_at_event": "", "manager_at_event": "", "tag_team_name": team, "faction_stable": "",
        "current_champion_title": champ, "championship_level": "Tag Team" if champ else "",
        "championship_partner": "Rick Martel" if name == "Tito Santana" else "",
        "reign_number": "", "title_won_date": "UNKNOWN", "days_into_reign_at_event": "",
        "title_defended_same_card": "FALSE", "title_lost_same_card": "FALSE",
        "elim_number": elim_no if elim_no else "", "elim_number_status": "CONFIRMED",
        "eliminated_by_ids": ";".join(wrestler_ids[e] for e in elim_by),
        "elimination_clock_time": elim_time_display, "elimination_clock_seconds": elim_time_s,
        "ring_time": ring_time, "ring_time_seconds": ring_time_s, "ring_time_status": "CONFIRMED",
        "wrestlers_remaining_when_eliminated": "",
        "wrestlers_eliminated_count": elim_count, "wrestlers_eliminated_ids": "",
        "solo_eliminations_count": "", "assisted_eliminations_count": "",
        "self_eliminated": "FALSE", "is_winner": "TRUE" if is_winner else "FALSE",
        "is_runner_up": "TRUE" if wid == "one-man-gang" else "FALSE",
        "is_final_two": "TRUE" if wid in ("jim-duggan", "one-man-gang") else "FALSE",
        "is_final_three": "TRUE" if wid in FINAL_FOUR_ORDER[:3] else "FALSE",
        "is_final_four": "TRUE" if wid in FINAL_FOUR_ORDER else "FALSE",
        "surprise_entrant": "FALSE", "legend_returning": "FALSE", "celebrity_entrant": "FALSE",
        "non_full_time_wrestler": "FALSE", "wrestled_earlier_on_card": "FALSE",
        "was_hof_member_at_time": "FALSE",  # DERIVED: WWE Hall of Fame didn't exist until 1993; true for every 1988 entrant regardless of later induction
        "data_quality_status": "CONFIRMED", "source_ids": "S001;S004;S008", "notes": "",
    })

# Back-fill wrestlers_eliminated_ids / solo / assisted counts from the elimination log
elim_map = {}
solo_map = {}
assist_map = {}
for row in elim_rows:
    eid = row["eliminator_wrestler_id"]
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
    if wid == "tito-santana":
        er["notes"] = "championship_partner (Rick Martel) recalled from general knowledge of the Strike Force tag team, not from S001/S004 directly -- PROBABLE, needs a citation before treating as confirmed."

with open(os.path.join(DATA_DIR, "entrants.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ENTRANTS_FIELDS)
    for er in entrant_rows:
        writer.writerow(er)

with open(os.path.join(DATA_DIR, "eliminations.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ELIMINATIONS_FIELDS)
    for row in elim_rows:
        writer.writerow(row)

# ---------------------------------------------------------------------------
# TAG TEAMS
# ---------------------------------------------------------------------------
tag_teams = [
    ("The Hart Foundation", ["Bret Hart", "Jim Neidhart"], "TRUE", "TRUE", "TRUE", 1, "FALSE", "TRUE", "TRUE", 1),
    ("Dino Bravo and One Man Gang", ["Dino Bravo", "One Man Gang"], "FALSE", "TRUE", "TRUE", 2, "FALSE", "TRUE", "FALSE", 2),
    ("Jake Roberts and Jim Brunzell", ["Jake Roberts", "Jim Brunzell"], "FALSE", "TRUE", "TRUE", 1, "FALSE", "TRUE", "FALSE", 1),
    ("The Bolsheviks", ["Nikolai Volkoff", "Boris Zhukov"], "TRUE", "TRUE", "UNKNOWN", 0, "UNKNOWN", "TRUE", "TRUE", 0),
]
with open(os.path.join(DATA_DIR, "tag_teams.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for team_name, members, official, consecutive, cooperated, elim_together, fought, allies, champs, combined in tag_teams:
        writer.writerow([EVENT_ID, team_name, ";".join(wrestler_ids[m] for m in members), "", "",
                          official, consecutive, cooperated, elim_together, fought, allies, champs, combined,
                          "PROBABLE", "S004"])

# ---------------------------------------------------------------------------
# SHOW APPEARANCES
# ---------------------------------------------------------------------------
show_appearances = [
    ("Ricky Steamboat", "Wrestler (undercard)", "", "Face", "", "Def. Rick Rude by DQ, singles match"),
    ("Rick Rude", "Wrestler (undercard)", "", "Heel", "", "Lost to Steamboat by DQ"),
    ("Noriyo Tateno", "Wrestler (undercard)", "", "Face", "WWF Women's Tag Team Championship", "Jumping Bomb Angels won the titles 2-1"),
    ("Itsuki Yamazaki", "Wrestler (undercard)", "", "Face", "WWF Women's Tag Team Championship", "Jumping Bomb Angels won the titles 2-1"),
    ("Leilani Kai", "Wrestler (undercard)", "", "Heel", "WWF Women's Tag Team Championship", "Glamour Girls lost the titles"),
    ("Judy Martin", "Wrestler (undercard)", "", "Heel", "WWF Women's Tag Team Championship", "Glamour Girls lost the titles"),
    ("Jimmy Hart", "Manager", "Leilani Kai, Judy Martin, Bret Hart, Jim Neidhart, Danny Davis", "Heel", "", ""),
    ("Haku", "Wrestler (undercard)", "", "Heel", "", "Islanders (w/ Tama) def. Young Stallions"),
    ("Tama", "Wrestler (undercard)", "", "Heel", "", "Islanders (w/ Haku) def. Young Stallions"),
    ("Jim Powers", "Wrestler (undercard)", "", "Face", "", "Young Stallions lost to Islanders"),
    ("Paul Roma", "Wrestler (undercard)", "", "Face", "", "Young Stallions lost to Islanders"),
    ("Bobby Heenan", "Manager", "Andre the Giant", "Heel", "", ""),
    ("Dino Bravo", "Wrestler (strength exhibition)", "", "Heel", "", "Also competed in the Rumble match itself -- see entrants.csv"),
    ("Frenchy Martin", "Manager", "Dino Bravo", "Heel", "", ""),
    ("Jack Tunney", "Authority figure", "", "Face", "", "On-screen WWF President"),
    ("Hulk Hogan", "Wrestler (champion, not in Rumble)", "", "Face", "WWF World Heavyweight Championship", "Champion at the time; did not compete in the Rumble match"),
    ("Andre the Giant", "Wrestler (undercard)", "", "Heel", "", ""),
    ("Ted DiBiase", "Wrestler (undercard)", "", "Heel", "", ""),
    ("Virgil", "Bodyguard/valet", "", "Heel", "", "Accompanied Ted DiBiase"),
    ("Vince McMahon", "Commentator", "", "Face", "", ""),
    ("Jesse Ventura", "Commentator", "", "Heel", "", ""),
    ("Gene Okerlund", "Interviewer", "", "Face", "", ""),
    ("Craig DeGeorge", "Interviewer", "", "Face", "", ""),
    ("Howard Finkel", "Ring announcer", "", "Face", "", ""),
]
with open(os.path.join(DATA_DIR, "show_appearances.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for name, role, managed, align, title, notes in show_appearances:
        pid = wrestler_ids.get(name, slugify(name))
        writer.writerow([EVENT_ID, pid, name, role, managed, align, title, notes, "PROBABLE", "S004"])

# ---------------------------------------------------------------------------
# OTHER MATCHES ON THE SAME CARD (mined from S009/S010 in Shane's doc)
# ---------------------------------------------------------------------------
# wrestler, match#, opponents, partners, type, is_title, title, was_champ_entering, result, won/lost title, duration, position, sources, notes
other_matches = [
    ("Ricky Steamboat", 1, "Rick Rude", "", "Singles", "FALSE", "", "FALSE", "Win (by DQ)", "", "", "17:39", "Opener",
     "S001;S010", "Times vary slightly by source: 17:39 (S001), 17:40 (S010), rounded to 17:00 in S009's recap summary -- treated as rounding, not a conflict."),
    ("Rick Rude", 1, "Ricky Steamboat", "", "Singles", "FALSE", "", "FALSE", "Loss (by DQ)", "", "", "17:39", "Opener",
     "S001;S010", ""),
    ("Noriyo Tateno", 2, "Judy Martin, Leilani Kai", "Itsuki Yamazaki", "Tag (2/3 falls)", "TRUE", "WWF Women's Tag Team Championship", "FALSE", "Win", "TRUE", "", "15:00", "2nd match",
     "S001;S009;S010", "Fall-by-fall detail conflicts between sources: S009 gives falls as Martin pin Yamazaki (7:00), Yamazaki pin Kai (10:00), Tateno pin Martin (15:00). S010 describes fall 1 as Martin pinning (implied Yamazaki) at 6:10, fall 2 as Tateno reversing a Martin powerbomb into a sunset flip at 1:50 (duration of that fall, not clock time), fall 3 (double missile dropkick) finishing at 5:47. The two accounts disagree on who pinned whom in fall 2 -- not resolved, both preserved here rather than picked."),
    ("Itsuki Yamazaki", 2, "Judy Martin, Leilani Kai", "Noriyo Tateno", "Tag (2/3 falls)", "TRUE", "WWF Women's Tag Team Championship", "FALSE", "Win", "TRUE", "", "15:00", "2nd match",
     "S001;S009;S010", "Same fall-detail discrepancy as Tateno's row above."),
    ("Leilani Kai", 2, "Itsuki Yamazaki, Noriyo Tateno", "Judy Martin", "Tag (2/3 falls)", "TRUE", "WWF Women's Tag Team Championship", "TRUE", "Loss", "", "TRUE", "15:00", "2nd match",
     "S001;S009;S010", "Champions entering, lost the titles. Same fall-detail discrepancy noted above."),
    ("Judy Martin", 2, "Itsuki Yamazaki, Noriyo Tateno", "Leilani Kai", "Tag (2/3 falls)", "TRUE", "WWF Women's Tag Team Championship", "TRUE", "Loss", "", "TRUE", "15:00", "2nd match",
     "S001;S009;S010", "Champions entering, lost the titles. Same fall-detail discrepancy noted above."),
    ("Haku", 4, "Jim Powers, Paul Roma", "Tama", "Tag (2/3 falls)", "FALSE", "", "FALSE", "Win", "", "", "14:00", "Show closer",
     "S001;S009;S010", "S009: Roma counted out (7:00), Haku forced Roma to submit (7:00) -- two-fall sweep. S010: Powers counted out on a bad knee bump at 7:50 (fall 1), ref stopped it on Roma's knee at 7:27 (fall 2) -- broadly consistent story (Young Stallions' knee injury), exact fall times differ slightly between sources."),
    ("Tama", 4, "Jim Powers, Paul Roma", "Haku", "Tag (2/3 falls)", "FALSE", "", "FALSE", "Win", "", "", "14:00", "Show closer",
     "S001;S009;S010", "Same as Haku's row above."),
    ("Jim Powers", 4, "Haku, Tama", "Paul Roma", "Tag (2/3 falls)", "FALSE", "", "FALSE", "Loss", "", "", "14:00", "Show closer",
     "S001;S009;S010", "Same as Haku's row above."),
    ("Paul Roma", 4, "Haku, Tama", "Jim Powers", "Tag (2/3 falls)", "FALSE", "", "FALSE", "Loss", "", "", "14:00", "Show closer",
     "S001;S009;S010", "Injured knee on a fall out of the ring per both S009/S010; storyline point, not a real injury per available sources."),
]
with open(os.path.join(DATA_DIR, "other_matches.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for (name, mnum, opponents, partners, mtype, is_title, title, was_champ, result, title_change, duration_note, duration, position, row_src, notes) in other_matches:
        pid = wrestler_ids.get(name, slugify(name))
        won_title = "TRUE" if (title_change == "TRUE" and result == "Win") else "FALSE"
        lost_title = "TRUE" if (was_champ == "TRUE" and result == "Loss") else "FALSE"
        writer.writerow([EVENT_ID, pid, mnum, opponents, partners, mtype, is_title, title, was_champ,
                          result, won_title, lost_title, duration, position, "", "PROBABLE", row_src, notes])

# ---------------------------------------------------------------------------
# EVENTS
# ---------------------------------------------------------------------------
event_row = {
    "event_id": EVENT_ID, "event_name": "Royal Rumble 1988", "match_name": "20-Man Royal Rumble Match",
    "match_type": "Men's", "event_date": "1988-01-24", "venue": "Copps Coliseum",
    "city_region": "Hamilton, Ontario", "country": "Canada",
    "attendance_official": 16200, "attendance_reported": 18000,
    "entry_interval_seconds": 120, "entrant_count": 20, "duration_total": "33:24",
    "duration_status": "CONFIRMED",
    "winner_id": "jim-duggan", "runner_up_id": "one-man-gang",
    "final_two_ids": "jim-duggan;one-man-gang", "final_three_ids": "jim-duggan;one-man-gang;dino-bravo",
    "final_four_ids": "jim-duggan;one-man-gang;dino-bravo;don-muraco",
    "first_entrant_id": "bret-hart", "second_entrant_id": "tito-santana", "final_entrant_id": "junkyard-dog",
    "first_elimination_id": "butch-reed", "last_elimination_before_winner_id": "one-man-gang",
    "eliminations_count": 19, "eliminators_count": 11, "surprise_entrants_count": "UNKNOWN",
    "champions_in_field_count": 1, "hall_of_famers_in_field_count": 0,
    "tag_teams_count": 2, "factions_count": "N/A",
    "commentary_team": "Vince McMahon, Jesse Ventura", "ring_announcer": "Howard Finkel",
    "referees": "Dave Hebner, Earl Hebner, Jim Korderas, Joey Marella worked the card per S026 (Wikipedia) -- confirms S010's ambiguous 'Hebner' credit for the Steamboat-Rude opener was one of these two; which specific referee(s) worked the Rumble match itself specifically is still not identified in any source consulted yet",
    "special_rules": "20-man format (pre-dates the 30-man standard adopted for 1993 onward); Howard Finkel announced a 2-minute entry interval, but S008's timing analysis found actual buzzer-to-buzzer intervals averaged closer to 90 seconds (11 of 18 intervals fell within 5s of 90s vs. only 3 of 18 within 5s of 120s) -- entry_interval_seconds (120) reflects the ANNOUNCED interval, not the actual one; this is 1988 only, still traditional-alignment rules (faces vs. heels), predating 1989's PPV debut and its more explicit 'every man for himself' framing per S010",
    "title_on_the_line": "FALSE", "championship_implications": "None -- no title was contested in the Rumble match itself",
    "winners_reward": "None identified -- no guaranteed title shot was attached to winning the Rumble in 1988; S010 explicitly frames the show as more of a trivia-question gimmick than a serious title angle",
    "historical_significance": "First-ever televised Royal Rumble match; only Rumble held as a free TV special rather than PPV; only Rumble held outside the U.S. until 2026. S009 notes an earlier, non-televised 'Royal Rumble' had taken place a few years prior at a house show in St. Louis -- this event is the first TELEVISED one, not necessarily the literal first use of the name/concept.",
    "notes": "20 confirmed entrants, all identified. See flags.csv for bio verification status and F006/F007 for two disputed eliminations and an attendance discrepancy. Fact-check pass: Wikipedia (S026) independently confirms date, venue, 18,000 reported attendance, winner/runner-up, and commentary team; gives duration as 33:00 vs this database's 33:24 -- a 24-second variance treated as rounding, not a real conflict.",
    "data_quality_status": "CONFIRMED", "source_ids": "S001;S002;S004;S008;S009;S010;S011;S026",
}
with open(os.path.join(DATA_DIR, "events.csv"), "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=EVENTS_FIELDS)
    writer.writerow(event_row)

print(f"1988 build complete (schema v2): {len(wrestlers)} wrestlers, {len(entrant_rows)} entrants, "
      f"{len(elim_rows)} elimination rows, {len(tag_teams)} tag teams, {len(show_appearances)} show appearances, "
      f"{len(sources)} sources logged, {len(flags)} open flags.")
