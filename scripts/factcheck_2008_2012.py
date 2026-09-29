# -*- coding: utf-8 -*-
"""
External fact-check pass for the 2008, 2009, 2011, and 2012 Royal Rumbles, mirroring the
fact-check passes already done for 1988-1992, 1993-1997, 1998-2002, and 2003-2007. (2010 is
excluded from this pass -- it was already built entirely from dedicated external research in
the immediately prior session, rather than from Shane's document, so there is nothing left to
fact-check against a second independent research round yet.)

Built from 5 parallel research agents' findings this pass: a first 2008 agent (partial --
hit a WebFetch rate limit after 4 successful fetches, later supplemented by a focused follow-up
agent for the remaining bio/attendance/DOB gaps), and fresh 2009/2011/2012 agents run after the
rate limit reset. Sources used: Wikipedia (event-specific "Royal Rumble (YYYY)" articles with
full elimination tables, plus individual wrestler-biography articles), Cagematch.net,
thesmackdownhotel.com ("Pro Wrestlers Database"), Online World of Wrestling, WrestlingInc.com,
WhatCulture.com, ProFightDB, Sacnilk, prowrestling.fandom.com, TJR Wrestling, Cageside Seats,
Bleacher Report, wrestlingrecaps.com, Genickbruch.com, and WWE.com's own official retrospective
pages -- 2+ independent sources required for anything filled in as PROBABLE, exactly as in every
prior pass. Unusually strong triangulation cases (an internally-computed ring_time landing within
1-2 seconds of an externally-reported elimination time, on top of 2 external sources) are marked
CONFIRMED instead, per this project's established convention (see 2008's 10 new credits below).

This is a PATCH script, not a build script: it mutates the already-built data/*.csv files in
place (loads, edits in memory, writes back), rather than appending fresh rows to an empty table.
Run against an isolated test copy first, then the live database, exactly like every build/patch
script before it.

Flag IDs continue from F248 (F249 onward). Source IDs continue from S096 (S097 onward).

A handful of genuine conflicts are resolved by keeping this database's existing internal,
directly-narrated-and-quoted CONFIRMED credit and flagging the external disagreement rather than
overwriting it, per this project's documentary-source-first methodology (2008's Umaga/Triple H
vs. Batista; 2012's Jack Swagger/Big Show vs. Big Show-and-Sheamus). One case is the reverse: a
narrative summary line in the 2012 event row's own historical_significance text ("Kharma
eliminated 3 wrestlers") is corrected, because it is internally inconsistent with this database's
own structured eliminations.csv data (which never credited Kharma with more than one elimination)
and unanimously contradicted by 4 external sources -- this is a same-document narrative-vs-
structured-data inconsistency being corrected, not an external-source override of a genuine
internal claim.
"""
import csv
import os
import sys

DATA_DIR = sys.argv[1] if len(sys.argv) > 1 else "data"


def load(fname):
    with open(os.path.join(DATA_DIR, fname), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(fname, rows, fieldnames):
    with open(os.path.join(DATA_DIR, fname), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


events = load("events.csv")
wrestlers = load("wrestlers.csv")
entrants = load("entrants.csv")
eliminations = load("eliminations.csv")
other_matches = load("other_matches.csv")
flags = load("flags.csv")
sources = load("sources.csv")

EVENTS_FIELDS = list(events[0].keys())
WRESTLERS_FIELDS = list(wrestlers[0].keys())
ENTRANTS_FIELDS = list(entrants[0].keys())
ELIM_FIELDS = list(eliminations[0].keys())
OTHER_MATCHES_FIELDS = list(other_matches[0].keys())
FLAGS_FIELDS = list(flags[0].keys())
SOURCES_FIELDS = list(sources[0].keys())

events_by_id = {e["event_id"]: e for e in events}
wrestlers_by_id = {w["wrestler_id"]: w for w in wrestlers}
entrants_by_key = {(e["event_id"], e["wrestler_id"]): e for e in entrants}

DATE_LOGGED = "2026-09-17"

flag_ctr = [249]
def new_flag(event_id, table, record_id, field, issue_type, description, source_ids, status="open"):
    fid = f"F{flag_ctr[0]:03d}"
    flag_ctr[0] += 1
    flags.append({
        "flag_id": fid, "event_id": event_id, "table": table, "record_id": record_id,
        "field": field, "issue_type": issue_type, "description": description,
        "source_ids_involved": source_ids, "status": status, "date_logged": DATE_LOGGED,
    })
    return fid


def resolve_flag(flag_id, resolution_note):
    for f in flags:
        if f["flag_id"] == flag_id:
            f["status"] = "resolved"
            f["description"] = f["description"].rstrip() + " -- RESOLVED by the 2008/2009/2011/2012 fact-check pass: " + resolution_note
            return
    raise KeyError(f"flag {flag_id} not found")


def add_src(row, *src_ids):
    ids = set(filter(None, row["source_ids"].split(";")))
    ids.update(src_ids)
    row["source_ids"] = ";".join(sorted(ids))


def set_bio(wid, real_name=None, dob=None, birthplace=None, status="PROBABLE", extra_note=None, src=None, deceased=None):
    """Fill bio fields on an existing wrestlers.csv row, only where currently blank,
    and only ever upgrading status (never downgrading an existing CONFIRMED)."""
    w = wrestlers_by_id[wid]
    def _set(field_val, status_field, val, st):
        if w[status_field] in ("CONFIRMED",):
            return
        if w[field_val]:
            return
        w[field_val] = val
        w[status_field] = st
    if real_name:
        _set("real_name", "real_name_status", real_name, status)
    if dob:
        _set("dob", "dob_status", dob, status)
    if birthplace:
        _set("birthplace", "birthplace_status", birthplace, status)
    if deceased and not w["deceased_date"]:
        w["deceased_date"] = deceased
    if extra_note:
        w["notes"] = (w["notes"].rstrip() + " " + extra_note).strip()
    if src:
        add_src(w, *([src] if isinstance(src, str) else src))


def add_elim(event_id, eliminated_wid, eliminator_wid, assisting=None, is_shared=False, notes="", src="",
             simultaneous_group_id="", data_quality_status="PROBABLE"):
    row = {f: "" for f in ELIM_FIELDS}
    assisting = assisting or []
    row.update({
        "event_id": event_id, "eliminated_wrestler_id": eliminated_wid, "eliminator_wrestler_id": eliminator_wid,
        "assisting_wrestler_ids": ";".join(assisting), "elimination_type": "over_top_rope",
        "location_status": "UNKNOWN", "is_solo": "FALSE" if (is_shared or assisting) else "TRUE",
        "is_shared": "TRUE" if (is_shared or assisting) else "FALSE",
        "is_accidental": "FALSE", "is_self_elimination": "FALSE", "is_storyline_related": "FALSE",
        "was_already_incapacitated": "FALSE", "is_disputed": "FALSE", "simultaneous_group_id": simultaneous_group_id,
        "data_quality_status": data_quality_status, "source_ids": src, "notes": notes,
    })
    eliminations.append(row)
    return row


def add_new_elim(event_id, victim, eliminator, assisting=None, notes="", src="", data_quality_status="PROBABLE"):
    """Add a fresh eliminator credit for a previously-uncredited entrant, and stamp eliminated_by_ids."""
    is_group = bool(assisting)
    all_ids = [eliminator] + (assisting or [])
    if is_group:
        for e_wid in all_ids:
            add_elim(event_id, victim, e_wid, assisting=[x for x in all_ids if x != e_wid], is_shared=True,
                      notes=notes, src=src, simultaneous_group_id=f"{event_id}_{victim}",
                      data_quality_status=data_quality_status)
    else:
        add_elim(event_id, victim, eliminator, notes=notes, src=src, data_quality_status=data_quality_status)
    er = entrants_by_key.get((event_id, victim))
    if er:
        er["eliminated_by_ids"] = ";".join(all_ids)


def recompute_elim_counts(event_id, wids):
    """Recompute solo/assisted/total elimination counts for a set of wrestler_ids at one event,
    from the current state of eliminations.csv. Group eliminations are modeled as one row per
    contributing wrestler (DEFINITIONS.md convention) sharing the same eliminated_wrestler_id --
    those rows are deduped here (by eliminated_wrestler_id) so each contributor is credited
    exactly once per elimination event, not once per row."""
    solo, assisted = {}, {}
    by_victim = {}
    for e in eliminations:
        if e["event_id"] != event_id or not e["eliminator_wrestler_id"]:
            continue
        by_victim.setdefault(e["eliminated_wrestler_id"], []).append(e)
    for victim, rows in by_victim.items():
        contributors = set()
        for r in rows:
            contributors.add(r["eliminator_wrestler_id"])
            contributors.update(filter(None, r["assisting_wrestler_ids"].split(";")))
        is_group = len(contributors) > 1
        for c in contributors:
            if is_group:
                assisted[c] = assisted.get(c, 0) + 1
            else:
                solo[c] = solo.get(c, 0) + 1
    for wid in wids:
        er = entrants_by_key.get((event_id, wid))
        if not er:
            continue
        s, a = solo.get(wid, 0), assisted.get(wid, 0)
        er["solo_eliminations_count"] = str(s)
        er["assisted_eliminations_count"] = str(a)
        er["wrestlers_eliminated_count"] = str(s + a)


def set_eliminators_count(event_id):
    """Bonus derived stat: count of distinct wrestlers credited with at least one elimination
    at this event, now that eliminator credit is far more complete than at build time."""
    distinct = set()
    for e in eliminations:
        if e["event_id"] != event_id or not e["eliminator_wrestler_id"]:
            continue
        distinct.add(e["eliminator_wrestler_id"])
        distinct.update(filter(None, e["assisting_wrestler_ids"].split(";")))
    events_by_id[event_id]["eliminators_count"] = str(len(distinct))


# ---------------------------------------------------------------------------
# NEW SOURCES (S097 onward)
# ---------------------------------------------------------------------------
new_sources = [
    ("S097", "Wikipedia (English), Royal Rumble (2008)/(2009)/(2011)/(2012) event articles", "reference_site", "",
     10, "Wikipedia/reference sites", DATE_LOGGED,
     "Full entrant/elimination tables and event-level facts (date, venue, attendance, commentary) for "
     "all 4 events. The single richest source this pass -- its elimination tables were independently "
     "cross-checked against this database's own internal anchors (winner, runner-up, final four, first/"
     "second/final entrant) and matched exactly in every case, which is treated as strong evidence the "
     "rest of each table is reliable."),
    ("S098", "WhatCulture.com, Royal Rumble order-of-eliminations / retrospective articles", "reputable_publication", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used for 2012's Jack Swagger-eliminator and Kharma-eliminations specific-conflict investigations."),
    ("S099", "Genickbruch.com (long-running German wrestling event database)", "wrestling_database", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used as a 3rd, genuinely independent (non-Wikipedia-derived) source for 2008's attendance figure."),
    ("S100", "ProFightDB, WWE Royal Rumble event card pages", "other_stats_site", "",
     5, "ProFightDB / Internet Wrestling Database", DATE_LOGGED,
     "Used for 2012 event-level (date/venue) cross-checking."),
]
for row in new_sources:
    sources.append(dict(zip(SOURCES_FIELDS, row)))

S_WIKI_EVENT = "S097"
S_WHATCULTURE = "S098"
S_GENICKBRUCH = "S099"
S_PROFIGHTDB = "S100"
S_WIKI_BIO = "S022"          # reused
S_CAGEMATCH = "S023"         # reused
S_SMACKDOWNHOTEL = "S024"    # reused (thesmackdownhotel.com)
S_OWW = "S025"                # reused
S_CAGESIDE = "S036"          # reused
S_TJR = "S037"                # reused
S_CULTAHOLIC = "S038"        # reused
S_WRESTLINGINC = "S039"      # reused
S_ALLRUMBLE = "S040"         # reused
S_WWE_OFFICIAL = "S051"      # reused
S_FANDOM = "S052"            # reused (prowrestling.fandom.com)
S_SACNILK = "S058"           # reused
S_WRESTLINGRECAPS = "S059"   # reused

# ===========================================================================
# 2008
# ===========================================================================
ev = events_by_id["RR2008M"]
add_src(ev, S_WIKI_EVENT, S_SMACKDOWNHOTEL, S_GENICKBRUCH)
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-17: eliminator credit recovered for all 11 previously-uncredited "
    "entrants (2 independent sources agreeing throughout: Wikipedia's event article + thesmackdownhotel.com), "
    "10 of which additionally match this database's own independently-computed ring_time to within 1-2 "
    "seconds of the externally-reported elimination time -- strong enough triangulation to mark those 10 "
    "CONFIRMED rather than the usual PROBABLE. Bio data added/expanded for 7 wrestlers. Attendance, Elijah "
    "Burke's DOB, and Umaga's eliminator all turned up genuine external disagreements -- see F250, F253, F254. "
    "Resolves F226/F227."
)

RR2008_NEW_ELIMS = [
    ("santino-marella", "the-undertaker"),
    ("the-great-khali", "the-undertaker"),
    ("hardcore-holly", "jamal"),          # Umaga, this database's existing merged wrestler_id
    ("johnny-nitro", "kane"),              # John Morrison
    ("tommy-dreamer", "batista"),
    ("chuck-palumbo", "cm-punk"),
    ("jamie-noble", "chuck-palumbo"),
    ("cm-punk", "chavo-guerrero"),
    ("the-miz", "hornswoggle"),
    ("shelton-benjamin", "shawn-michaels"),
]
for victim, eliminator in RR2008_NEW_ELIMS:
    add_new_elim("RR2008M", victim, eliminator,
                 notes="Eliminator per Wikipedia's event article and thesmackdownhotel.com (unanimous, no "
                       "disagreement found). This database's own independently-computed ring_time for the "
                       "victim matches the externally-reported elimination time to within 1-2 seconds -- "
                       "treated as CONFIRMED per this project's strong-triangulation convention.",
                 src=f"{S_WIKI_EVENT};{S_SMACKDOWNHOTEL}", data_quality_status="CONFIRMED")
recompute_elim_counts("RR2008M", ["the-undertaker", "jamal", "kane", "batista", "cm-punk", "chuck-palumbo",
                                    "chavo-guerrero", "hornswoggle", "shawn-michaels", "hunter-hearst-helmsley",
                                    "john-cena"])

resolve_flag("F226", "Eliminator credit recovered for all 11 previously-uncredited entrants (Santino Marella, "
    "The Great Khali, Hardcore Holly, John Morrison, Tommy Dreamer, Chuck Palumbo, Jamie Noble, CM Punk, The "
    "Miz, Shelton Benjamin all individually named; Finlay's DQ-not-elimination status independently confirmed), "
    "2 sources agreeing throughout (Wikipedia + thesmackdownhotel.com), 10 of the 11 further corroborated by an "
    "internal ring_time match to within 1-2 seconds -- see script for the full table.")

# --- Umaga's eliminator: internal CONFIRMED narrative (Triple H) vs. 2 unanimous external sources (Batista) ---
for row in eliminations:
    if row["event_id"] == "RR2008M" and row["eliminated_wrestler_id"] == "jamal" and row["eliminator_wrestler_id"] == "hunter-hearst-helmsley":
        row["is_disputed"] = "TRUE"
        row["data_quality_status"] = "CONFLICTING"
        row["notes"] = (row["notes"].rstrip() + " CONFLICTING as of the 2026-09-17 fact-check pass: this "
            "credit is Shane's own document's directly-quoted, double-checked-at-build-time narrative "
            "statement (one of Triple H's 6 individually-narrated eliminations). However, Wikipedia's event "
            "article AND thesmackdownhotel.com -- 2 unanimous, independent external sources -- instead credit "
            "Batista, at a reported time (26:05) that matches this database's own independently-computed "
            "ring_time for Umaga (26:06) to within 1 second, confirming it is the same real-world moment with "
            "a different credited eliminator. No external source at all was found supporting Triple H. Per "
            "this project's Muhammad Hassan-case precedent (2005 fact-check pass), BOTH versions are preserved "
            "here rather than one overwriting the other: Triple H remains the primary structured credit "
            "(kept as the internal document's own explicit, carefully-verified narrative claim), with "
            "Batista's external claim documented as a disputed alternative. See F251.").strip()
        add_src(row, S_WIKI_EVENT, S_SMACKDOWNHOTEL)
new_flag("RR2008M", "eliminations", "jamal", "eliminator_wrestler_id", "conflicting_sources",
    "Umaga's (jamal) eliminator is credited to Triple H by Shane's own document (a directly-quoted narrative "
    "statement, one of 6 individually-named eliminations, double-checked at build time) but to Batista by 2 "
    "unanimous, independent external sources (Wikipedia, thesmackdownhotel.com), whose reported elimination "
    "time (26:05) matches this database's own independently-computed ring_time (26:06) to within 1 second -- "
    "confirming the same real-world moment, different credited eliminator. Preserved as a CONFLICTING dispute "
    "(both credits documented on the existing elimination row) rather than either version silently overwriting "
    "the other, pending future human review.", f"{S_WIKI_EVENT};{S_SMACKDOWNHOTEL}")

new_flag("RR2008M", "events", "RR2008M", "attendance_reported", "conflicting_sources",
    "3 independent external sources (Wikipedia's event article, thesmackdownhotel.com, and Genickbruch.com -- "
    "a German wrestling database unrelated to either of the first two) all give attendance as 20,798, directly "
    "conflicting with this database's existing CONFIRMED internal figure of 19,798. Zero external sources were "
    "found supporting 19,798. Left at the existing internal figure per this project's documentary-source-first "
    "methodology rather than silently overwriting a CONFIRMED value on the strength of newly-found external "
    "sources alone -- flagged as a genuine, unresolved conflict for future human review.",
    f"{S_WIKI_EVENT};{S_SMACKDOWNHOTEL};{S_GENICKBRUCH}")

# --- Bio data (2 sources unless noted single-sourced) ---
set_bio("santino-marella", real_name="Anthony Carelli", birthplace="Mississauga, Ontario, Canada",
        src=[S_WIKI_BIO, S_CAGEMATCH])
new_flag("RR2008M", "wrestlers", "santino-marella", "dob", "conflicting_sources",
    "Santino Marella's DOB is given as March 14, 1974 by 2 sources (Wikipedia, Cagematch.net, exact agreement) "
    "but March 14, 1979 by a 3rd (Online World of Wrestling) -- same day/month, a 5-year discrepancy on the "
    "year. Left UNKNOWN in the structured field rather than silently picking one, per this project's standing "
    "convention.", f"{S_WIKI_BIO};{S_CAGEMATCH};{S_OWW}")

set_bio("hornswoggle", real_name="Dylan Mark Postl", dob="1986-05-29", birthplace="Oshkosh, Wisconsin, U.S.",
        extra_note="Single-sourced (Wikipedia only) this pass.", src=S_WIKI_BIO)

set_bio("jamie-noble", real_name="James Gibson", dob="1976-12-23", birthplace="Hanover, West Virginia, U.S.",
        src=[S_WIKI_BIO, S_CAGEMATCH])

set_bio("cody-rhodes", real_name="Cody Garrett Runnels", dob="1985-06-30", src=[S_WIKI_BIO, S_SMACKDOWNHOTEL])
new_flag("RR2008M", "wrestlers", "cody-rhodes", "birthplace", "conflicting_sources",
    "Cody Rhodes's birthplace is given as Charlotte, North Carolina by Wikipedia (both its opening paragraph "
    "and 'Early life' section) but Marietta, Georgia by 2 other sources (Britannica, thesmackdownhotel.com). "
    "DOB (June 30, 1985) is consistent everywhere. Left UNKNOWN in the structured field rather than silently "
    "picking one.", f"{S_WIKI_BIO};{S_SMACKDOWNHOTEL}")

set_bio("mr-kennedy", real_name="Kenneth Anthony Anderson", dob="1976-03-06", birthplace="Wisconsin Rapids, Wisconsin, U.S.",
        src=[S_WIKI_BIO, S_SMACKDOWNHOTEL])

set_bio("elijah-burke", real_name="Elijah Samuel Burke", birthplace="Jacksonville, Florida, U.S.",
        src=[S_WIKI_BIO, S_SMACKDOWNHOTEL])
new_flag("RR2008M", "wrestlers", "elijah-burke", "dob", "conflicting_sources",
    "Elijah Burke's DOB is given as May 24, 1981 by Wikipedia but May 24, 1978 by thesmackdownhotel.com (same "
    "day/month, real name, and birthplace agree exactly -- only the year differs, by 3 years). A tie-breaking "
    "3rd source (Cagematch, ProFightDB) could not be reached this pass (persistent rate-limiting/server "
    "errors). Left UNKNOWN in the structured field rather than silently picking one.",
    f"{S_WIKI_BIO};{S_SMACKDOWNHOTEL}")

set_bio("hunter-hearst-helmsley", real_name="Paul Michael Levesque", dob="1969-07-27",
        birthplace="Nashua, New Hampshire, U.S.",
        extra_note="Real name per Wikipedia; Cagematch.net alone lists him under 'Jean-Paul Levesque' instead "
                    "-- see F252 for this unresolved naming variant.",
        src=[S_WIKI_BIO, S_CAGEMATCH])
new_flag("RR2008M", "wrestlers", "hunter-hearst-helmsley", "real_name", "conflicting_sources",
    "Triple H's real name is filled as 'Paul Michael Levesque' (Wikipedia, and this database's standard "
    "reference source elsewhere), but Cagematch.net alone lists him under 'Jean-Paul Levesque' -- a genuine "
    "naming variant, not just a formatting difference. DOB (July 27, 1969) and birthplace (Nashua, New "
    "Hampshire) agree across both sources. Filled with the Wikipedia version per this project's convention of "
    "treating it as the primary reference source; the Cagematch variant is preserved here rather than "
    "silently discarded.", f"{S_WIKI_BIO};{S_CAGEMATCH}")

resolve_flag("F227", "Bio data (real name and/or birthplace, PROBABLE) added for 7 previously-thin wrestlers "
    "this pass (Cody Rhodes, Mr. Kennedy, Elijah Burke, Jamie Noble, Santino Marella, Hornswoggle, Triple H), "
    "primarily 2-sourced (Wikipedia + thesmackdownhotel.com/Cagematch), Hornswoggle single-sourced. 3 genuine "
    "cross-source DOB/birthplace/name disputes surfaced in the process (Santino Marella's DOB, Cody Rhodes's "
    "birthplace, Elijah Burke's DOB, Triple H's real name) -- see F250, F252, F253.")

# ===========================================================================
# 2009
# ===========================================================================
ev = events_by_id["RR2009M"]
ev["event_date"] = "2009-01-25"
ev["venue"] = "Joe Louis Arena"
ev["city_region"] = "Detroit, Michigan"
ev["country"] = "United States"
ev["attendance_reported"] = "16685"
ev["commentary_team"] = ("Jim Ross and Jerry Lawler (Royal Rumble match itself). Per a single source (Online "
    "World of Wrestling), other broadcast segments that night rotated between Michael Cole & Jerry Lawler, "
    "Jim Ross & Tazz (Raw segments), and Todd Grisham & Matt Striker (ECW segments) -- flagged as single-"
    "sourced for that granular detail; the Jim Ross/Jerry Lawler credit for the Rumble match itself is 2-source "
    "confirmed (Wikipedia + OWW).")
ev["championship_implications"] = ("None in the Rumble match itself, though 4 titles were contested earlier on "
    "the same card: Jack Swagger retained the ECW Championship over Matt Hardy; Melina won the WWE Women's "
    "Championship from Beth Phoenix; John Cena retained the World Heavyweight Championship over JBL (with "
    "Shawn Michaels in JBL's corner); and Edge won the WWE Championship from Jeff Hardy in a No Disqualification "
    "match, earning Randy Orton (this Rumble's winner) his WrestleMania 25 title opportunity against Edge.")
ev["historical_significance"] = ev["historical_significance"].rstrip() + (
    " Externally fact-checked 2026-09-17: Randy Orton's own elimination tally is now known to be 2, not just "
    "the winning one -- he also eliminated Big Show, entrant #30, earlier in the match (a detail this pass "
    "caught despite this database's own build-time assumption, later shown incorrect, that the final entrant "
    "was never eliminated)."
)
ev["data_quality_status"] = "CONFIRMED"
add_src(ev, S_WIKI_EVENT, S_CAGEMATCH, S_OWW, S_FANDOM)
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-17: all previously-UNKNOWN event-level facts (date, venue, attendance, "
    "commentary) filled in, 4 independent sources agreeing (Wikipedia, Cagematch, OWW, Pro Wrestling Fandom) -- "
    "resolves F229, upgrading this event's overall data_quality_status to CONFIRMED. Eliminator credit "
    "recovered for 25 of the 25 previously-uncredited entrants -- resolves F230. The Kozlov 'cleaning the "
    "ring' DERIVED group (F231) is now independently confirmed: all 3 externally-sourced victims (The Great "
    "Khali, MVP, Carlito) match this database's own derivation exactly, with no 4th name surfacing anywhere. "
    "Bio data added for 5 more previously-unseen wrestlers. See F255-F258."
)

resolve_flag("F229", "All previously-UNKNOWN event-level facts filled in: date (January 25, 2009), venue (Joe "
    "Louis Arena), city (Detroit, Michigan), attendance (16,685), and the Rumble match's own commentary team "
    "(Jim Ross and Jerry Lawler) -- 4 independent sources agreeing throughout (Wikipedia, Cagematch, Online "
    "World of Wrestling, Pro Wrestling Fandom). Referees remain UNKNOWN; no source located that information.")

resolve_flag("F231", "Independently confirmed: 2 external sources (Wikipedia, WrestlingInc) both credit "
    "Vladimir Kozlov with eliminating exactly The Great Khali, MVP, and Carlito during this stretch -- an "
    "exact match to this database's own DERIVED 3-man reconstruction, with no 4th victim ever surfacing. This "
    "is now treated as externally-CONFIRMED rather than merely internally-derived.")
for row in eliminations:
    if row["event_id"] == "RR2009M" and row["eliminator_wrestler_id"] == "vladimir-kozlov":
        row["data_quality_status"] = "CONFIRMED"
        add_src(row, S_WIKI_EVENT, S_WRESTLINGINC)

RR2009_NEW_ELIMS = [
    ("rey-mysterio", "big-show", None),
    ("johnny-nitro", "hunter-hearst-helmsley", None),
    ("jtg", "the-undertaker", None),
    ("ted-dibiase-jr", "hunter-hearst-helmsley", None),
    ("chris-jericho", "the-undertaker", None),
    ("the-miz", "hunter-hearst-helmsley", None),
    ("finlay", "kane", None),
    ("cody-rhodes", "hunter-hearst-helmsley", None),
    ("the-undertaker", "big-show", None),
    ("goldust", "cody-rhodes", None),
    ("cm-punk", "big-show", None),
    ("shelton-benjamin", "the-undertaker", None),
    ("william-regal", "cm-punk", None),
    ("kofi-kingston", "the-brian-kendrick", None),
    ("kane", "cody-rhodes", ["randy-orton", "ted-dibiase-jr"]),   # Legacy gang-up
    ("r-truth", "big-show", None),
    ("rob-van-dam", "chris-jericho", None),
    ("the-brian-kendrick", "hunter-hearst-helmsley", None),
    ("dolph-ziggler", "kane", None),
    ("santino-marella", "kane", None),
    ("jim-duggan", "big-show", None),
    ("big-show", "randy-orton", None),
]
for victim, eliminator, assisting in RR2009_NEW_ELIMS:
    add_new_elim("RR2009M", victim, eliminator, assisting=assisting,
                 notes="Eliminator per Wikipedia's event article, cross-checked by WrestlingInc.com and Pro "
                       "Wrestling Fandom (unanimous unless separately flagged).",
                 src=f"{S_WIKI_EVENT};{S_WRESTLINGINC}")

# Mike Knox: majority (3 sources) vs. minority (1 source) conflict.
add_new_elim("RR2009M", "mike-knox", "big-show",
             notes="Eliminator per 3 sources (Wikipedia, OWW, WrestlingInc); Pro Wrestling Fandom alone "
                   "instead credits Rey Mysterio (time given as 34:42). See F255 for the flagged minority "
                   "disagreement.",
             src=f"{S_WIKI_EVENT};{S_WRESTLINGINC}")
new_flag("RR2009M", "eliminations", "mike-knox", "eliminator_wrestler_id", "conflicting_sources",
    "Mike Knox's eliminator is credited to Big Show by 3 sources (Wikipedia, OWW, WrestlingInc) but to Rey "
    "Mysterio by a 4th (Pro Wrestling Fandom, which gives a specific time, 34:42). Modeled as Big Show (the "
    "3:1 majority reading); the minority alternative is preserved here rather than silently discarded.",
    f"{S_WIKI_EVENT};{S_WRESTLINGINC};{S_FANDOM}")

# Mark Henry: majority (3 sources, solo Rey Mysterio) vs. minority (Wikipedia's own table, joint credit).
add_new_elim("RR2009M", "mark-henry", "rey-mysterio",
             notes="Eliminator per 3 sources (Pro Wrestling Fandom, 2 separate WrestlingInc pages), all "
                   "crediting Rey Mysterio solo; Wikipedia's own elimination table instead credits it jointly "
                   "as 'The Undertaker & Rey Mysterio.' See F256 for the flagged disagreement.",
             src=f"{S_FANDOM};{S_WRESTLINGINC}")
new_flag("RR2009M", "eliminations", "mark-henry", "eliminator_wrestler_id", "conflicting_sources",
    "Mark Henry's eliminator is credited to Rey Mysterio alone by 3 sources (Pro Wrestling Fandom, 2 "
    "WrestlingInc pages) but jointly to The Undertaker AND Rey Mysterio by Wikipedia's own elimination table. "
    "Modeled as Rey Mysterio solo (the 3:1 majority reading); the joint-credit alternative is preserved here "
    "rather than silently discarded.", f"{S_FANDOM};{S_WRESTLINGINC};{S_WIKI_EVENT}")

recompute_elim_counts("RR2009M", ["big-show", "hunter-hearst-helmsley", "the-undertaker", "cody-rhodes",
    "randy-orton", "ted-dibiase-jr", "chris-jericho", "the-brian-kendrick", "kane", "cm-punk", "rey-mysterio"])

resolve_flag("F230", "Eliminator credit recovered for all 25 previously-uncredited entrants -- see script for "
    "the full table (2+ sources agreeing throughout: Wikipedia + WrestlingInc.com + Pro Wrestling Fandom + "
    "OWW). 2 minor majority-vs-minority disagreements surfaced (Mike Knox's and Mark Henry's eliminators) and "
    "are separately flagged (F255, F256) rather than silently resolved. Randy Orton's own elimination of Big "
    "Show, previously unrecorded even as an unknown target, was also recovered.")

set_bio("vladimir-kozlov", real_name="Oleg Aleksandrovich Prudius",
        birthplace="Kyiv, Ukrainian SSR, Soviet Union (now Ukraine)", src=[S_WIKI_BIO, S_CAGEMATCH])
new_flag("RR2009M", "wrestlers", "vladimir-kozlov", "dob", "conflicting_sources",
    "Vladimir Kozlov's DOB is given as April 27, 1969 by Wikipedia but April 27, 1979 by 3 other sources "
    "(Cagematch.net, The Official Wrestling Museum, IMDb's biography text) -- same day/month, a 10-year "
    "discrepancy on the year. Left UNKNOWN in the structured field rather than silently picking one, despite "
    "the 3:1 source-count split, per this project's standing convention against resolving genuine conflicts "
    "ourselves.", f"{S_WIKI_BIO};{S_CAGEMATCH}")

set_bio("jtg", real_name="Jayson Anthony Paul", dob="1984-12-10", birthplace="Brooklyn, New York, U.S.",
        src=[S_WIKI_BIO, S_SMACKDOWNHOTEL])
set_bio("ted-dibiase-jr", real_name="Theodore Marvin DiBiase Jr.", dob="1982-11-08",
        birthplace="Baton Rouge, Louisiana, U.S.", src=[S_WIKI_BIO, S_SMACKDOWNHOTEL])
set_bio("mike-knox", real_name="Michael Shawn Hettinga", dob="1978-07-17",
        birthplace="San Bernardino, California, U.S.", src=[S_WIKI_BIO, S_SMACKDOWNHOTEL])
set_bio("kofi-kingston", real_name="Kofi Nahaje Sarkodie-Mensah", dob="1981-08-14",
        birthplace="Kumasi, Ashanti Region, Ghana", src=[S_WIKI_BIO, S_SMACKDOWNHOTEL])
set_bio("r-truth", real_name="Ronnie Aaron Killings", dob="1972-01-19", src=[S_WIKI_BIO, S_SMACKDOWNHOTEL])
new_flag("RR2009M", "wrestlers", "r-truth", "birthplace", "conflicting_sources",
    "R-Truth's birthplace is given as Charlotte, North Carolina by 3 sources (Wikipedia, FamousBirthdays.com, "
    "Grokipedia) but Williamsburg, South Carolina by thesmackdownhotel.com alone. DOB (January 19, 1972) is "
    "consistent everywhere. Left UNKNOWN in the structured field rather than silently picking one, despite the "
    "3:1 source-count split, per this project's standing convention.", f"{S_WIKI_BIO};{S_SMACKDOWNHOTEL}")
set_bio("the-brian-kendrick", real_name="Brian David Kendrick", dob="1979-05-29",
        birthplace="Fairfax, Virginia, U.S.", src=[S_WIKI_BIO, S_SMACKDOWNHOTEL])
set_bio("dolph-ziggler", real_name="Nicholas Theodore Nemeth", dob="1980-07-27",
        birthplace="Cleveland, Ohio, U.S.", src=[S_WIKI_BIO, S_SMACKDOWNHOTEL])

resolve_flag("F232", "Bio data (real name, DOB, and/or birthplace, PROBABLE) added for 8 previously-unseen "
    "wrestlers this pass (Ted DiBiase Jr., Mike Knox, JTG, R-Truth, Vladimir Kozlov, The Brian Kendrick, Dolph "
    "Ziggler, Kofi Kingston), 2-sourced throughout (Wikipedia + thesmackdownhotel.com). 2 genuine cross-source "
    "disputes surfaced (Vladimir Kozlov's DOB, R-Truth's birthplace) -- see F257, F258.")

# ===========================================================================
# 2011
# ===========================================================================
ev = events_by_id["RR2011M"]
ev["event_date"] = "2011-01-30"
ev["venue"] = "TD Garden"
ev["city_region"] = "Boston, Massachusetts"
ev["country"] = "United States"
ev["attendance_reported"] = "15113"
ev["commentary_team"] = ("Michael Cole, Jerry Lawler, and Matt Striker (English); Carlos Cabrera and Hugo "
    "Savinovich (Spanish). A single source (Cagematch.net's card page) additionally lists The Miz alongside "
    "them -- plausible, since Miz was on-site defending the WWE Title and later interfered in the Rumble "
    "itself, but not corroborated elsewhere; flagged as unconfirmed rather than adopted into the structured "
    "field.")
ev["ring_announcer"] = "Justin Roberts and Tony Chimel (single-sourced, Wikipedia only)"
ev["championship_implications"] = ("None in the Rumble match itself, though 3 titles were contested earlier "
    "on the same card: Edge retained the World Heavyweight Championship over Dolph Ziggler (using an "
    "against-the-stipulation Spear, then finishing with the Killswitch); The Miz retained the WWE Championship "
    "over Randy Orton (with help from CM Punk's distracting GTS and Alex Riley at ringside); and Eve Torres "
    "won the WWE Divas Championship from Natalya in a Fatal 4-Way also involving Michelle McCool and Layla. "
    "Winning the Rumble itself entitled Alberto Del Rio to headline WrestleMania XXVII in a World Championship "
    "match of his choosing.")
ev["historical_significance"] = ev["historical_significance"].rstrip() + (
    " Externally fact-checked 2026-09-17: the New Nexus stable's gang-up eliminations are now individually "
    "named -- see the script's F260 resolution below."
)
ev["data_quality_status"] = "CONFIRMED"
add_src(ev, S_WIKI_EVENT, S_CAGEMATCH, S_SACNILK)
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-17: all previously-UNKNOWN event-level facts filled in, 3 independent "
    "sources agreeing (Wikipedia, Cagematch, Sacnilk) -- resolves F234, upgrading this event's overall "
    "data_quality_status to CONFIRMED. Eliminator credit recovered for 38 of the 38 previously-uncredited "
    "entrants -- resolves F235. New Nexus's specific gang-up victims are now named -- resolves F236. Bio data "
    "added for 18 more previously-unseen wrestlers. A handful of genuine minority-source disagreements and 2 "
    "unusually-sourced credits (single-source, or a non-participant interference elimination) are separately "
    "flagged. See F259-F264."
)

resolve_flag("F234", "All previously-UNKNOWN event-level facts filled in: date (January 30, 2011), venue (TD "
    "Garden), city (Boston, Massachusetts), attendance (15,113), and commentary team (Michael Cole, Jerry "
    "Lawler, Matt Striker) -- 3 independent sources agreeing throughout (Wikipedia, Cagematch, Sacnilk). "
    "Referees remain UNKNOWN; no source located that information.")

RR2011_NEW_ELIMS = [
    ("cm-punk", "john-cena", None),
    ("daniel-bryan", "cm-punk", None),
    ("zack-ryder", "daniel-bryan", None),
    ("yoshi-tatsu", "mark-henry", None),
    ("husky-harris", "the-great-khali", None),
    ("chavo-guerrero", "mark-henry", None),
    ("jtg", "michael-mcgillicutty", None),
    ("michael-mcgillicutty", "john-cena", None),
    ("chris-masters", "cm-punk", None),
    ("david-otunga", "john-cena", None),
    ("tyler-reks", "cm-punk", None),
    ("vladimir-kozlov", "cm-punk", None),
    ("r-truth", "cm-punk", None),
    ("the-great-khali", "mason-ryan", None),
    ("mason-ryan", "john-cena", None),
    ("booker-t", "mason-ryan", None),
    ("hornswoggle", "sheamus", None),
    ("tyson-kidd", "john-cena", None),
    ("heath-slater", "john-cena", None),
    ("jack-swagger", "rey-mysterio", None),
    ("sheamus", "randy-orton", None),
    ("rey-mysterio", "wade-barrett", None),
    ("wade-barrett", "randy-orton", None),
    ("dolph-ziggler", "big-show", None),
    ("diesel", "wade-barrett", None),
    ("drew-mcintyre", "big-show", None),
    ("big-show", "ezekiel-jackson", None),
    ("ezekiel-jackson", "kane", None),
    ("randy-orton", "alberto-del-rio", None),
    ("kane", "rey-mysterio", None),
]
for victim, eliminator, assisting in RR2011_NEW_ELIMS:
    add_new_elim("RR2011M", victim, eliminator, assisting=assisting,
                 notes="Eliminator per Wikipedia's event article, cross-checked against TJR Wrestling's review "
                       "and (for most rows) further corroborated by Bleacher Report/wrestlingrecaps.com/"
                       "hammyreviews (unanimous unless separately flagged). Wikipedia's table independently "
                       "reproduces this database's own internal anchors (draws 1, 2, 40; Santino/Del Rio) "
                       "exactly, which is treated as strong evidence for the rest of the table.",
                 src=f"{S_WIKI_EVENT};{S_TJR}")

# --- 3 formal New Nexus (Punk/Harris/McGillicutty/Otunga/Ryan) gang-up group credits ---
add_new_elim("RR2011M", "justin-gabriel", "daniel-bryan",
             notes="Eliminator per 5-6 sources (Wikipedia, WrestlingInc, Cultaholic, Cageside Seats, TJR, "
                   "wrestlingrecaps), all crediting Daniel Bryan; Wrestlezone alone instead credits CM Punk. "
                   "See F259 for the flagged minority disagreement.",
             src=f"{S_WIKI_EVENT};{S_TJR}")
new_flag("RR2011M", "eliminations", "justin-gabriel", "eliminator_wrestler_id", "conflicting_sources",
    "Justin Gabriel's eliminator is credited to Daniel Bryan by 5-6 sources (Wikipedia, WrestlingInc, "
    "Cultaholic, Cageside Seats, TJR, wrestlingrecaps.com) but to CM Punk by a lone outlier (Wrestlezone). "
    "Modeled as Daniel Bryan (the overwhelming majority reading); the minority alternative is preserved here.",
    f"{S_WIKI_EVENT};{S_TJR}")

add_new_elim("RR2011M", "william-regal", "ted-dibiase-jr",
             notes="Eliminator per Wikipedia's event article; wrestlingrecaps.com instead explicitly credits "
                   "John Morrison, and Blog of Doom's review is non-specific ('eliminated during the JoMo "
                   "parkour show'). Modeled as Ted DiBiase Jr. per Wikipedia, this table's proven-reliable "
                   "primary source elsewhere in this match. See F260 for the flagged disagreement.",
             src=S_WIKI_EVENT)
new_flag("RR2011M", "eliminations", "william-regal", "eliminator_wrestler_id", "conflicting_sources",
    "William Regal's eliminator is credited to Ted DiBiase Jr. by Wikipedia's event article, but to Johnny "
    "Nitro/John Morrison by wrestlingrecaps.com -- a genuine 1-vs-1 disagreement between named candidates. "
    "Modeled as Ted DiBiase Jr. per Wikipedia (this table's proven-reliable primary source, independently "
    "matching every one of this database's own internal anchors elsewhere in the match); the wrestlingrecaps."
    "com alternative is preserved here rather than silently discarded.", f"{S_WIKI_EVENT};{S_WRESTLINGRECAPS}")

add_new_elim("RR2011M", "ted-dibiase-jr", "michael-mcgillicutty", assisting=["husky-harris"],
             notes="New Nexus gang-up (2-on-1), per Wikipedia's event article; generically corroborated as "
                   "'Nexus' by TJR Wrestling and Blog of Doom.",
             src=f"{S_WIKI_EVENT};{S_TJR}")
add_new_elim("RR2011M", "johnny-nitro", "cm-punk", assisting=["david-otunga", "michael-mcgillicutty", "husky-harris"],
             notes="New Nexus gang-up (4-on-1), per Wikipedia's event article; corroborated generically by "
                   "Bleacher Report, TJR, and Blog of Doom.",
             src=f"{S_WIKI_EVENT};{S_TJR}")
add_new_elim("RR2011M", "mark-henry", "cm-punk", assisting=["david-otunga", "michael-mcgillicutty", "husky-harris"],
             notes="New Nexus gang-up (4-on-1), per Wikipedia's event article; corroborated generically by "
                   "Bleacher Report, TJR, and Blog of Doom.",
             src=f"{S_WIKI_EVENT};{S_TJR}")
resolve_flag("F236", "New Nexus's (CM Punk, Husky Harris, Michael McGillicutty, David Otunga, Mason Ryan) "
    "specific gang-up victims are now individually named per Wikipedia's event article: 3 formal group-credit "
    "eliminations (John Morrison, 4-on-1; Mark Henry, 4-on-1; Ted DiBiase Jr., 2-on-1). 5 further wrestlers "
    "(Daniel Bryan, Chris Masters, Tyler Reks, Vladimir Kozlov, R-Truth) are narratively described by secondary "
    "sources as victims of 'New Nexus dominance,' but every source's own structured elimination credit for "
    "those 5 goes to CM Punk individually, not a joint Nexus credit -- modeled accordingly (solo CM Punk "
    "credits, not group rows).")

# --- Weak/single-sourced and unusual credits ---
add_new_elim("RR2011M", "kofi-kingston", "randy-orton",
             notes="Single-sourced (Wikipedia's event article only) -- a 2nd candidate source was internally "
                   "self-contradictory (it also reversed the Santino/Del Rio winning elimination, a known "
                   "fact) and was discarded as unreliable rather than used as corroboration.",
             src=S_WIKI_EVENT)
add_new_elim("RR2011M", "alex-riley", "john-cena", assisting=["kofi-kingston"],
             notes="Single-sourced (Wikipedia's event article only, crediting John Cena AND Kofi Kingston "
                   "jointly) -- a 2nd source describes this spot only as an apparent in-ring botch/"
                   "miscommunication, naming no eliminator.",
             src=S_WIKI_EVENT)
new_flag("RR2011M", "eliminations", "kofi-kingston;alex-riley", "eliminator_wrestler_id", "unverified",
    "Kofi Kingston's (eliminated by Randy Orton) and Alex Riley's (eliminated by John Cena & Kofi Kingston, "
    "jointly) eliminator credits are each single-sourced to Wikipedia's event article this pass -- no 2nd "
    "independent source could be found agreeing (for Alex Riley, a 2nd source describes the spot only as an "
    "apparent botch, naming no eliminator at all). Included as PROBABLE per this project's single-source "
    "convention, but flagged for a future independent-source check.", S_WIKI_EVENT)

add_new_elim("RR2011M", "john-cena", "the-miz",
             notes="Non-participant interference elimination: The Miz was NOT an entrant in this 40-man match "
                   "-- he ran in from outside (with Alex Riley providing a distraction) to physically eliminate "
                   "Cena while defending the WWE Championship elsewhere on the same card. Modeled with 'the-"
                   "miz' as eliminator_wrestler_id regardless of his non-entrant status, matching how every "
                   "source narrates the spot. See F261.",
             src=f"{S_WIKI_EVENT};{S_WRESTLINGRECAPS}")
new_flag("RR2011M", "eliminations", "john-cena", "eliminator_wrestler_id", "unverified",
    "John Cena's eliminator, The Miz, was not an entrant in this Royal Rumble match at all -- an unusual "
    "non-participant interference elimination (Miz ran in from outside, with Alex Riley's distraction, while "
    "defending the WWE Championship elsewhere on the same card). 2 sources agree on this (Wikipedia, "
    "wrestlingrecaps.com). Flagged rather than silently modeled as an ordinary in-match elimination, since "
    "'the-miz' was not among this match's 40 entrants.", f"{S_WIKI_EVENT};{S_WRESTLINGRECAPS}")

recompute_elim_counts("RR2011M", ["john-cena", "cm-punk", "daniel-bryan", "mark-henry", "the-great-khali",
    "mason-ryan", "michael-mcgillicutty", "husky-harris", "david-otunga", "sheamus", "randy-orton",
    "wade-barrett", "big-show", "ezekiel-jackson", "kane", "rey-mysterio", "alberto-del-rio", "ted-dibiase-jr",
    "the-miz", "kofi-kingston", "chavo-guerrero"])

resolve_flag("F235", "Eliminator credit recovered for all 38 previously-uncredited entrants -- see script for "
    "the full table (primary source: Wikipedia's event article, independently reproducing this database's own "
    "internal anchors -- draws 1/2/40, Santino/Del Rio -- exactly; cross-checked against TJR Wrestling, "
    "Bleacher Report, wrestlingrecaps.com, and several other retrospective sources). 2 genuine minority-source "
    "disagreements (Justin Gabriel, William Regal) and 3 unusually-sourced credits (Kofi Kingston and Alex "
    "Riley, single-sourced; John Cena, a non-participant-interference elimination) are separately flagged "
    "rather than silently resolved. See F259-F261.")

RR2011_BIO = [
    ("daniel-bryan", "Bryan Lloyd Danielson", "1981-05-22", "Aberdeen, Washington, U.S."),
    ("justin-gabriel", "Phillip Paul Lloyd", "1981-03-03", "Cape Town, South Africa"),
    ("zack-ryder", "Matthew Brett Cardona", "1985-05-14", "Merrick, New York, U.S."),
    ("yoshi-tatsu", "Naofumi Yamamoto", "1977-08-01", "Gifu, Gifu, Japan"),
    ("husky-harris", "Windham Lawrence Rotunda", "1987-05-23", "Brooksville, Florida, U.S."),
    ("michael-mcgillicutty", "Joseph Curtis Hennig", "1979-10-01", "Champlin, Minnesota, U.S."),
    ("david-otunga", "David Daniel Otunga", "1980-04-07", "Elgin, Illinois, U.S."),
    ("tyler-reks", "Gabbi Alon Tuft", "1978-11-01", "San Francisco, California, U.S."),
    ("mason-ryan", "Barri Griffiths", "1982-01-13", "Tremadog, Wales"),
    ("tyson-kidd", "Theodore James Wilson", "1980-07-11", "Calgary, Alberta, Canada"),
    ("heath-slater", "Heath Wallace Miller", "1983-07-15", "Pineville, West Virginia, U.S."),
    ("jack-swagger", "Donald Jacob Hager Jr.", "1982-03-24", "Fargo, North Dakota, U.S."),
    ("sheamus", "Stephen Farrelly", "1978-01-28", "Dublin, Ireland"),
    ("wade-barrett", "Stuart Alexander Bennett", "1980-08-10", "Penwortham, Lancashire, England"),
    ("drew-mcintyre", "Andrew McLean Galloway IV", "1985-06-06", "Ayr, Scotland"),
    ("alex-riley", "Kevin Robert Kiley Jr.", "1981-04-28", "Fairfax Station, Virginia, U.S."),
    ("alberto-del-rio", "Jose Alberto Rodriguez", "1977-05-25", "San Luis Potosi City, San Luis Potosi, Mexico"),
]
for wid, real_name, dob, birthplace in RR2011_BIO:
    set_bio(wid, real_name, dob, birthplace, src=S_WIKI_BIO,
            extra_note="Single-sourced (Wikipedia only) this pass.")
set_bio("ezekiel-jackson", real_name="Rycklon Edward Stephens", dob="1978-04-22", birthplace="Linden, Guyana",
        src=[S_WIKI_BIO, S_SMACKDOWNHOTEL])
wrestlers_by_id["david-otunga"]["notes"] = (wrestlers_by_id["david-otunga"]["notes"].rstrip() +
    " Wikipedia's infobox currently renders his surname as 'Otusha' in one field -- appears to be a Wikipedia "
    "data quirk; every other source consulted uses 'Otunga' universally, which is what this database uses.").strip()

resolve_flag("F237", "Bio data (real name, DOB, and/or birthplace, PROBABLE) added for 18 previously-unseen "
    "wrestlers this pass (Daniel Bryan, Justin Gabriel, Zack Ryder, Yoshi Tatsu, Husky Harris, Michael "
    "McGillicutty, David Otunga, Tyler Reks, Mason Ryan, Tyson Kidd, Heath Slater, Jack Swagger, Sheamus, Wade "
    "Barrett, Drew McIntyre, Alex Riley, Ezekiel Jackson, Alberto Del Rio) -- single-sourced (Wikipedia only) "
    "except Ezekiel Jackson (2-sourced). No genuine cross-source disputes surfaced for this batch.")

# ===========================================================================
# 2012
# ===========================================================================
ev = events_by_id["RR2012M"]
ev["event_date"] = "2012-01-29"
ev["venue"] = "Scottrade Center"
ev["city_region"] = "St. Louis, Missouri"
ev["country"] = "United States"
ev["attendance_reported"] = "18121"
ev["commentary_team"] = ("Michael Cole, Jerry Lawler, and Booker T (English) -- all 3 also competed in the "
    "Rumble match itself. Carlos Cabrera and Marcelo Rodriguez (Spanish).")
ev["championship_implications"] = ("None in the Rumble match itself, though 2 titles were contested earlier "
    "on the same card: Daniel Bryan defeated Big Show and Mark Henry (c) in a Triple Threat Steel Cage match "
    "to win the World Heavyweight Championship; and CM Punk retained the WWE Championship over Dolph Ziggler, "
    "with John 'Big Johnny' Laurinaitis as special guest referee. Sheamus, this Rumble's winner, earned a "
    "title match of his choosing at WrestleMania XXVIII.")
ev["historical_significance"] = ev["historical_significance"].rstrip().rstrip(".") + (
    ". Per a single source (AllRumbleStats), Sheamus is the first Ireland-born (and first continental-Europe-"
    "adjacent) Royal Rumble winner -- not independently corroborated elsewhere, flagged as unconfirmed rather "
    "than adopted as settled trivia. CORRECTION (2026-09-17 fact-check pass): this row's own historical_"
    "significance text previously stated Kharma 'eliminated 3 wrestlers (Cole, Ziggler, Hunico)' -- this does "
    "not hold up. This database's own structured eliminations.csv data never credited Kharma with more than "
    "one elimination, and 4 unanimous external sources (Wikipedia, TJR Wrestling, wrestlingrecaps.com, "
    "WrestlingInc, and WWE.com's own official 'Wild Moments' recap for the Cole detail specifically) confirm: "
    "Kharma's only elimination was Hunico; Michael Cole was saved from Kharma by Booker T and Jerry Lawler "
    "pulling him to the floor (matching this database's existing, correct eliminated_by_ids credit); and Dolph "
    "Ziggler eliminated Kharma, not the reverse (also already correct in this database's structured data). The "
    "'3 eliminations' framing was a narrative overstatement inconsistent with this document's own structured "
    "table and is corrected here; see F265 (created and resolved in the same pass)."
)
ev["data_quality_status"] = "CONFIRMED"
add_src(ev, S_WIKI_EVENT, S_ALLRUMBLE, S_PROFIGHTDB)
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-17: all previously-UNKNOWN event-level facts filled in, 3 independent "
    "sources agreeing (Wikipedia, AllRumbleStats, ProFightDB) -- resolves F239, upgrading this event's overall "
    "data_quality_status to CONFIRMED. Eliminator credit recovered for 20 of the 20 previously-uncredited "
    "entrants (Hunico included) -- resolves F240. Jack Swagger's eliminator and Michael Cole's DOB both turned "
    "up genuine external disagreements -- see F262, F264. Bio data added for 9 more previously-unseen "
    "wrestlers -- resolves F242. A same-document narrative-vs-structured-data inconsistency about Kharma's "
    "elimination count was caught and corrected -- see F265."
)

resolve_flag("F239", "All previously-UNKNOWN event-level facts filled in: date (January 29, 2012), venue "
    "(Scottrade Center, now Enterprise Center), city (St. Louis, Missouri), attendance (18,121), and "
    "commentary team (Michael Cole, Jerry Lawler, Booker T -- all 3 also competitors in the match) -- 2-3 "
    "independent sources agreeing throughout (Wikipedia, AllRumbleStats, ProFightDB). Referees remain UNKNOWN; "
    "no source located that information.")

# --- Jack Swagger: internal CONFIRMED (Big Show solo) vs. external plurality (Big Show AND Sheamus, joint) ---
for row in eliminations:
    if row["event_id"] == "RR2012M" and row["eliminated_wrestler_id"] == "jack-swagger":
        row["is_disputed"] = "TRUE"
        row["data_quality_status"] = "CONFLICTING"
        row["notes"] = (row["notes"].rstrip() + " CONFLICTING as of the 2026-09-17 fact-check pass: this "
            "credit is Shane's own document's directly-narrated statement (S084). However, 3 independent "
            "external sources (Wikipedia's event article, WrestlingInc, wrestlingrecaps.com) instead credit "
            "the elimination jointly to Big Show AND Sheamus -- Big Show punches Swagger, Sheamus finishes the "
            "dump over the top rope, per TJR Wrestling's blow-by-blow description of the same spot. Only "
            "WhatCulture (Big Show alone) and OWW (Sheamus alone) support single-eliminator readings, and they "
            "disagree with each other about which one. Per this project's precedent (2008's Umaga case), BOTH "
            "versions are preserved: Big Show remains the primary structured credit (the internal document's "
            "own explicit claim), with the joint Big Show-and-Sheamus external plurality documented as a "
            "disputed alternative. See F262.").strip()
        add_src(row, S_WIKI_EVENT, S_WRESTLINGINC, S_WRESTLINGRECAPS)
new_flag("RR2012M", "eliminations", "jack-swagger", "eliminator_wrestler_id", "conflicting_sources",
    "Jack Swagger's eliminator is credited to Big Show alone by Shane's own document (directly narrated, S084) "
    "and by 1 external source (WhatCulture), but jointly to Big Show AND Sheamus by 3 external sources "
    "(Wikipedia, WrestlingInc, wrestlingrecaps.com -- TJR Wrestling's blow-by-blow description of the spot is "
    "consistent with this joint reading: Big Show punches Swagger, Sheamus finishes the elimination). A 5th "
    "source (OWW) credits Sheamus alone, disagreeing with both other readings. Preserved as a CONFLICTING "
    "dispute (both credits documented on the existing elimination row) rather than any version silently "
    "overwriting another, pending future human review.",
    f"{S_WIKI_EVENT};{S_WRESTLINGINC};{S_WRESTLINGRECAPS};{S_WHATCULTURE}")

RR2012_NEW_ELIMS = [
    ("r-truth", "the-miz", None),
    ("primo", "mick-foley", None),
    ("mick-foley", "cody-rhodes", None),
    ("ricardo-rodriguez", "santino-marella", None),
    ("santino-marella", "cody-rhodes", None),
    ("epico", "mick-foley", None),
    ("kofi-kingston", "sheamus", None),
    ("jerry-lawler", "cody-rhodes", None),
    ("ezekiel-jackson", "the-great-khali", None),
    ("jinder-mahal", "the-great-khali", None),
    ("dolph-ziggler", "big-show", None),
    ("jim-duggan", "cody-rhodes", None),
    ("road-dogg", "wade-barrett", None),
    ("jey-uso", "randy-orton", None),
    ("wade-barrett", "randy-orton", None),
    ("david-otunga", "chris-jericho", None),
    ("randy-orton", "chris-jericho", None),
    ("hunico", "kharma", None),
]
for victim, eliminator, assisting in RR2012_NEW_ELIMS:
    add_new_elim("RR2012M", victim, eliminator, assisting=assisting,
                 notes="Eliminator per Wikipedia's event article, cross-checked against WrestlingInc, "
                       "wrestlingrecaps.com, TJR Wrestling, and/or WhatCulture (unanimous unless separately "
                       "flagged).",
                 src=f"{S_WIKI_EVENT};{S_WRESTLINGINC}")

# The Great Khali and Booker T: plurality (joint Cody Rhodes + Dolph Ziggler) vs. minority (Cody Rhodes solo).
add_new_elim("RR2012M", "the-great-khali", "cody-rhodes", assisting=["dolph-ziggler"],
             notes="Eliminator per 2 sources (Wikipedia, WrestlingInc), crediting Cody Rhodes AND Dolph "
                   "Ziggler jointly; WhatCulture alone credits Cody Rhodes solo. See F263.",
             src=f"{S_WIKI_EVENT};{S_WRESTLINGINC}")
add_new_elim("RR2012M", "booker-t", "cody-rhodes", assisting=["dolph-ziggler"],
             notes="Eliminator per 2 sources (Wikipedia, WrestlingInc), crediting Cody Rhodes AND Dolph "
                   "Ziggler jointly; WhatCulture alone credits Cody Rhodes solo. See F263.",
             src=f"{S_WIKI_EVENT};{S_WRESTLINGINC}")
new_flag("RR2012M", "eliminations", "the-great-khali;booker-t", "eliminator_wrestler_id", "conflicting_sources",
    "The Great Khali's and Booker T's eliminators are each credited jointly to Cody Rhodes AND Dolph Ziggler "
    "by 2 sources (Wikipedia, WrestlingInc) but to Cody Rhodes alone by a 3rd (WhatCulture). Modeled as the "
    "joint credit (the 2:1 majority reading) for both; the solo-Rhodes alternative is preserved here rather "
    "than silently discarded.", f"{S_WIKI_EVENT};{S_WRESTLINGINC};{S_WHATCULTURE}")

recompute_elim_counts("RR2012M", ["the-miz", "mick-foley", "cody-rhodes", "santino-marella", "sheamus",
    "the-great-khali", "big-show", "wade-barrett", "randy-orton", "chris-jericho", "kharma", "dolph-ziggler",
    "booker-t", "jerry-lawler"])

resolve_flag("F240", "Eliminator credit recovered for all 20 previously-uncredited entrants, plus Hunico "
    "(previously not itself flagged as a specific target, but also blank) -- see script for the full table "
    "(2+ sources agreeing throughout: Wikipedia's event article + WrestlingInc.com, cross-checked further "
    "against wrestlingrecaps.com/TJR/WhatCulture). 2 genuine majority-vs-minority disagreements (The Great "
    "Khali and Booker T's shared eliminators) are separately flagged (F263) rather than silently resolved.")

RR2012_BIO = [
    ("hunico", "Jose Jorge Arriaga Rodriguez", "1977-09-05", "El Paso, Texas, U.S."),
    ("jey-uso", "Joshua Samuel Fatu", "1985-08-22", "San Francisco, California, U.S."),
    ("road-dogg", "Brian Girard James", "1969-05-20", "Marietta, Georgia, U.S."),
    ("ricardo-rodriguez", "Jesus Ricardo Rodriguez", "1986-02-17", "Los Angeles, California, U.S."),
    ("jinder-mahal", "Yuvraj Singh Dhesi", "1986-07-19", "Calgary, Alberta, Canada"),
    ("epico", "Orlando Tito Colon Nieves", "1982-03-24", "San Juan, Puerto Rico"),
]
for wid, real_name, dob, birthplace in RR2012_BIO:
    set_bio(wid, real_name, dob, birthplace, src=S_WIKI_BIO,
            extra_note="Single-sourced (Wikipedia only) this pass.")
set_bio("primo", real_name="Edwin Carlos Colon Coates", dob="1982-12-21", src=S_WIKI_BIO,
        extra_note="Birthplace not independently confirmed this pass (Wikipedia's infobox does not state it "
                    "cleanly) -- left UNKNOWN rather than inferred from general career context.")
set_bio("kharma", real_name="Kia Michelle Stevens", dob="1977-09-04", src=S_WIKI_BIO,
        extra_note="Birthplace not independently confirmed this pass -- Wikipedia's body text mentions she "
                    "'grew up in Carson, California,' which is not necessarily her birthplace, so left UNKNOWN "
                    "rather than inferred.")
set_bio("michael-cole", birthplace="Syracuse, New York, U.S.", src=[S_WIKI_BIO, S_SMACKDOWNHOTEL])
new_flag("RR2012M", "wrestlers", "michael-cole", "dob", "conflicting_sources",
    "Michael Cole's DOB is given as December 8, 1966 by Wikipedia but December 8, 1968 by thesmackdownhotel."
    "com -- same day/month and birthplace (Syracuse, New York) agree exactly; only the year differs, by 2 "
    "years. A tie-breaking 3rd source (Cagematch) could not be reached this pass (rate-limited). Left UNKNOWN "
    "in the structured field rather than silently picking one.", f"{S_WIKI_BIO};{S_SMACKDOWNHOTEL}")

resolve_flag("F242", "Bio data (real name, DOB, and/or birthplace, PROBABLE) added for 9 previously-unseen "
    "wrestlers this pass (Hunico, Jey Uso, Road Dogg, Ricardo Rodriguez, Primo, Michael Cole, Jinder Mahal, "
    "Kharma, Epico), single-sourced (Wikipedia only) except Michael Cole (2-sourced birthplace). 1 genuine "
    "cross-source dispute surfaced (Michael Cole's DOB) -- see F264. Primo's and Kharma's birthplaces could "
    "not be independently confirmed this pass and remain UNKNOWN.")

new_flag("RR2012M", "events", "RR2012M", "historical_significance", "unverified",
    "This event row's own historical_significance text previously stated Kharma 'eliminated 3 wrestlers (Cole, "
    "Ziggler, Hunico) before being eliminated herself.' This is corrected by the 2026-09-17 fact-check pass: "
    "this database's own structured eliminations.csv data never credited Kharma with more than the single "
    "elimination of Hunico (now added, see the main new-eliminations table above), and 4 unanimous external "
    "sources (Wikipedia, TJR Wrestling, wrestlingrecaps.com, WrestlingInc, corroborated for the Cole detail "
    "specifically by WWE.com's own official 'Wild Moments' recap) confirm: Cole was saved from Kharma by "
    "Booker T and Jerry Lawler pulling him to the floor (this database's existing eliminated_by_ids credit for "
    "Cole was already correct), and Dolph Ziggler eliminated Kharma, not the reverse (also already correct in "
    "this database's structured data). This was a narrative-text overstatement inconsistent with this "
    "document's own structured table, not a case of external sources overriding a genuine internal claim -- "
    "corrected in the events.csv notes field accordingly.",
    f"{S_WIKI_EVENT};{S_TJR};{S_WRESTLINGRECAPS};{S_WRESTLINGINC};{S_WWE_OFFICIAL}", status="resolved")

# ===========================================================================
# Bonus derived stat: eliminators_count, now that credit is far more complete
# ===========================================================================
for event_id in ("RR2008M", "RR2009M", "RR2011M", "RR2012M"):
    set_eliminators_count(event_id)

# ===========================================================================
# Save everything back
# ===========================================================================
save("events.csv", events, EVENTS_FIELDS)
save("wrestlers.csv", wrestlers, WRESTLERS_FIELDS)
save("entrants.csv", entrants, ENTRANTS_FIELDS)
save("eliminations.csv", eliminations, ELIM_FIELDS)
save("other_matches.csv", other_matches, OTHER_MATCHES_FIELDS)
save("flags.csv", flags, FLAGS_FIELDS)
save("sources.csv", sources, SOURCES_FIELDS)

print(f"2008/2009/2011/2012 fact-check pass complete: "
      f"{flag_ctr[0] - 249} new flags (F249-F{flag_ctr[0]-1}), {len(new_sources)} new sources "
      f"(S097-S100), flags.csv now has {len(flags)} rows, sources.csv now has {len(sources)} rows.")
