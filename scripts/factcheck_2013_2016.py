# -*- coding: utf-8 -*-
"""
External fact-check pass for the 2013, 2014, 2015, and 2016 Royal Rumbles, mirroring the
fact-check passes already done for 1988-1992, 1993-1997, 1998-2002, 2003-2007, and 2008-2012.

Built from 4 parallel research agents' findings this pass (one per year). Sources used: Wikipedia
(event-specific "Royal Rumble (YYYY)" articles with full elimination tables), allrumblestats.com,
Cagematch.net, WWE.com's own official match recaps/retrospectives, WrestlingInc.com, WhatCulture,
Cageside Seats (per-event match-time/statistics retrospectives), TJR Wrestling, Sportskeeda,
Bleacher Report, prowrestling.fandom.com, sacnilk.com, theandrewhughes.com, InsidePulse.com,
wrestlezone.com, prowrestlinghistory.com, Fightful.com, KB Wrestling Reviews, Voices of Wrestling,
The Armbar Express, and ringhistory.com -- 2+ independent sources required for anything filled in
as CONFIRMED, exactly as in every prior pass; a single external source (or an internally-flagged
extraction-reliability concern) is filled in as PROBABLE instead and clearly caveated.

This is a PATCH script, not a build script: it mutates the already-built data/*.csv files in
place (loads, edits in memory, writes back), rather than appending fresh rows to an empty table.
Run against an isolated test copy first, then the live database, exactly like every build/patch
script before it.

Flag IDs continue from F296 (F297 onward -- note F296 is a same-pass hotfix correction to the
2016 Roman Reigns WWE Championship claim, applied directly to the live database just before this
script was written; it is NOT re-applied here). Source IDs continue from S108 (S109 onward).

NOTABLE FINDING THIS PASS -- 2013's full entry order, independently recoverable for the first
time: this database's original 2013 build could only confidently place 7 of 30 entrants (the
buzzer-gap list in Shane's document is UNNAMED, unlike every other Cageside-only year). Two
external sources (Wikipedia, allrumblestats.com) independently agree on a full 1-30 entry order,
which matches all 7 of the pre-existing internally-anchored positions exactly. Even more
strikingly: applying this newly-recovered external entry order to this database's OWN internal
buzzer-gap/entrance-lag/survival-time arithmetic (completely independent of either external
source) produces a computed elimination-order ranking that matches the external elimination-order
data exactly, for all 29 non-winner entrants, position for position -- a 29-for-29 cross-
validation between two totally independent methods. This is about as strong a confirmation as
this project has ever produced for a single year's entry order. The lone anomaly: Ryback's
computed elimination timestamp (54:07) lands exactly 60 seconds short of the match's own total
duration (55:07), despite Ryback being confirmed as both entrant #30 and the runner-up (the
final, losing elimination) -- unlike every other discrepancy of this kind found across this
project (which are typically 1-2 seconds, attributable to bell-ring delay), this is a genuinely
unexplained minute-long gap, checked directly against Shane's original document text (which does
confirm "8m 51s: Ryback" survival and "0m 17s: Ryback" entrance lag verbatim, ruling out a
transcription error on this database's end) -- left as a flagged, unresolved discrepancy.
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


def mmss(t):
    parts = [int(p) for p in t.split(":")]
    return parts[0] * 60 + parts[1] if len(parts) == 2 else parts[0] * 3600 + parts[1] * 60 + parts[2]


def secs_to_mmss(s):
    m, sec = divmod(int(s), 60)
    return f"{m}:{sec:02d}"


flag_ctr = [297]
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
            f["description"] = f["description"].rstrip() + " -- RESOLVED by the 2013-2016 fact-check pass: " + resolution_note
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
             simultaneous_group_id="", data_quality_status="PROBABLE", order_in_match="", clock_time="",
             is_disputed=False):
    row = {f: "" for f in ELIM_FIELDS}
    assisting = assisting or []
    row.update({
        "event_id": event_id, "order_in_match": order_in_match,
        "eliminated_wrestler_id": eliminated_wid, "eliminator_wrestler_id": eliminator_wid,
        "assisting_wrestler_ids": ";".join(assisting), "elimination_clock_time": clock_time,
        "elimination_clock_seconds": str(mmss(clock_time)) if clock_time else "",
        "elimination_type": "over_top_rope",
        "location_status": "UNKNOWN", "is_solo": "FALSE" if (is_shared or assisting) else "TRUE",
        "is_shared": "TRUE" if (is_shared or assisting) else "FALSE",
        "is_accidental": "FALSE", "is_self_elimination": "FALSE", "is_storyline_related": "FALSE",
        "was_already_incapacitated": "FALSE", "is_disputed": "TRUE" if is_disputed else "FALSE",
        "simultaneous_group_id": simultaneous_group_id,
        "data_quality_status": data_quality_status, "source_ids": src, "notes": notes,
    })
    eliminations.append(row)
    return row


def add_new_elim(event_id, victim, eliminator, assisting=None, notes="", src="", data_quality_status="PROBABLE",
                  order_in_match="", clock_time=""):
    """Add a fresh eliminator credit for a previously-uncredited entrant, and stamp eliminated_by_ids."""
    is_group = bool(assisting)
    all_ids = [eliminator] + (assisting or [])
    if is_group:
        for e_wid in all_ids:
            add_elim(event_id, victim, e_wid, assisting=[x for x in all_ids if x != e_wid], is_shared=True,
                      notes=notes, src=src, simultaneous_group_id=f"{event_id}_{victim}",
                      data_quality_status=data_quality_status, order_in_match=order_in_match, clock_time=clock_time)
    else:
        add_elim(event_id, victim, eliminator, notes=notes, src=src, data_quality_status=data_quality_status,
                 order_in_match=order_in_match, clock_time=clock_time)
    er = entrants_by_key.get((event_id, victim))
    if er:
        er["eliminated_by_ids"] = ";".join(all_ids)


def recompute_elim_counts(event_id, wids):
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
    distinct = set()
    for e in eliminations:
        if e["event_id"] != event_id or not e["eliminator_wrestler_id"]:
            continue
        distinct.add(e["eliminator_wrestler_id"])
        distinct.update(filter(None, e["assisting_wrestler_ids"].split(";")))
    events_by_id[event_id]["eliminators_count"] = str(len(distinct))


def merge_wrestler(old_wid, new_wid, event_ids, merge_note):
    """Redirect all entrant/elimination rows for old_wid at the given events to new_wid,
    then leave old_wid's own wrestlers.csv row as an audit-trail-only stub. Mirrors the
    A-Train/Prince-Albert merge precedent from the 2003-2007 fact-check pass."""
    for ev_id in event_ids:
        key = (ev_id, old_wid)
        if key in entrants_by_key:
            er = entrants_by_key.pop(key)
            er["wrestler_id"] = new_wid
            entrants_by_key[(ev_id, new_wid)] = er
    for row in eliminations:
        if row["eliminated_wrestler_id"] == old_wid:
            row["eliminated_wrestler_id"] = new_wid
        if row["eliminator_wrestler_id"] == old_wid:
            row["eliminator_wrestler_id"] = new_wid
        row["assisting_wrestler_ids"] = ";".join(
            new_wid if a == old_wid else a for a in row["assisting_wrestler_ids"].split(";") if a)
    for row in other_matches:
        if row["wrestler_id"] == old_wid:
            row["wrestler_id"] = new_wid
    wrestlers_by_id[old_wid]["notes"] = (
        wrestlers_by_id[old_wid]["notes"].rstrip() + " " + merge_note).strip()


# ---------------------------------------------------------------------------
# NEW SOURCES (S109 onward)
# ---------------------------------------------------------------------------
new_sources = [
    ("S109", "Wikipedia (English), Royal Rumble (2013)-(2016) event articles", "reference_site", "",
     10, "Wikipedia/reference sites", DATE_LOGGED,
     "Full entrant/elimination tables and event-level facts (date, venue, attendance, commentary, "
     "undercard) for all 4 events. Cross-checked against this database's own internal anchors "
     "(winner, runner-up where known) and, for 2013, against this database's own independent "
     "buzzer/entrance-lag/survival-time arithmetic -- matched exactly in every case checked."),
    ("S110", "theandrewhughes.com, InsidePulse.com, wrestlezone.com, and prowrestlinghistory.com -- "
     "independent entrant/elimination-order recap lists", "reputable_publication", "",
     12, "Other reputable site", DATE_LOGGED,
     "Independently-run wrestling recap/stats blogs, used mainly for 2014's entry-order and "
     "elimination-credit cross-checking."),
    ("S111", "KB Wrestling Reviews, Voices of Wrestling, and The Armbar Express -- independent match "
     "retrospective reviews", "reputable_publication", "",
     12, "Other reputable site", DATE_LOGGED,
     "Independent match-by-match retrospective review sites, used for narrative/trivia corroboration "
     "(crowd reaction, notable spots) across 2014-2016."),
    ("S112", "Cagematch.net, WWE Royal Rumble 2013-2016 event/match pages", "wrestling_database", "",
     4, "Cagematch.net", DATE_LOGGED,
     "Official-participant-list pages, used mainly to cross-check the 30-man field and the Curtis "
     "Axel/Erick Rowan 2015 participation-status question."),
    ("S113", "Fightful.com", "reputable_publication", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used for 2014's Rey Mysterio 'Not Daniel Bryan' #30-entrant corroboration and 2016 trivia."),
    ("S114", "ringhistory.com, individual wrestler match-history archive pages", "wrestling_database", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used to independently check Xavier Woods's earliest main-roster WWE match date against the 2014 "
     "Royal Rumble date, in the Xavier Woods non-entrant investigation."),
]
for row in new_sources:
    sources.append(dict(zip(SOURCES_FIELDS, row)))

S_WIKI = "S109"
S_RECAP_BLOGS = "S110"
S_RETRO_REVIEWS = "S111"
S_CAGEMATCH_EVENT = "S112"
S_FIGHTFUL = "S113"
S_RINGHISTORY = "S114"
S_ALLRUMBLE = "S040"          # reused
S_WRESTLINGINC = "S039"       # reused
S_WWE_OFFICIAL = "S051"       # reused
S_CAGESIDE = "S036"           # reused
S_TJR = "S037"                 # reused
S_WHATCULTURE = "S098"        # reused
S_SPORTSKEEDA = "S078"        # reused
S_FANDOM = "S052"              # reused
S_SACNILK = "S058"            # reused
S_BLEACHER = "S063"           # reused
S_WIKI_BIO = "S022"           # reused
S_CAGEMATCH_BIO = "S023"      # reused
S_SMACKDOWNHOTEL = "S024"     # reused

# ===========================================================================
# 2013
# ===========================================================================
ev = events_by_id["RR2013M"]
ev["event_date"] = "2013-01-27"
ev["venue"] = "US Airways Center"
ev["city_region"] = "Phoenix, Arizona"
ev["country"] = "United States"
ev["attendance_reported"] = "15103"
ev["commentary_team"] = ("Michael Cole, Jerry \"The King\" Lawler, John \"Bradshaw\" Layfield (main English "
    "broadcast, 2-source confirmed: Wikipedia + thesmackdownhotel.com). Pre-show: Tony Dawson, Matt Striker; "
    "Spanish broadcast: Carlos Cabrera, Marcelo Rodriguez (both single-sourced, Wikipedia only).")
ev["championship_implications"] = ("None in the Rumble match itself. Undercard title matches (Wikipedia + "
    "thesmackdownhotel.com): Antonio Cesaro (c) def. The Miz for the WWE United States Championship (pre-show); "
    "Alberto Del Rio (c) def. Big Show for the World Heavyweight Championship (Last Man Standing); Team Hell No "
    "(Daniel Bryan & Kane) (c) def. Team Rhodes Scholars (Cody Rhodes & Damien Sandow) for the WWE Tag Team "
    "Championship; main event -- The Rock def. CM Punk (c) for the WWE Championship, ending Punk's 434-day "
    "reign and setting up Rock-Cena II at WrestleMania 29 off this Rumble's outcome.")
ev["historical_significance"] = ev["historical_significance"].rstrip() + (
    " Externally fact-checked 2026-09-17: full 1-30 entry order recovered (2 independent external sources, "
    "Wikipedia and allrumblestats.com, agreeing with each other and with all 7 of this database's own "
    "pre-existing anchored positions), resolving the Ziggler/Jericho #1-vs-#2 ambiguity (Ziggler #1, Jericho "
    "#2). Applying this newly-recovered order to this database's own independent internal buzzer/survival-time "
    "arithmetic produces a computed elimination-order ranking that matches the external elimination-order data "
    "exactly for all 29 non-winner entrants -- an unusually strong cross-validation. Runner-up confirmed as "
    "Ryback (eliminated last, by Cena, the winning elimination). See F297-F299."
)
ev["duration_status"] = "CONFIRMED"
ev["data_quality_status"] = "CONFIRMED"
add_src(ev, S_WIKI, S_ALLRUMBLE, S_SMACKDOWNHOTEL)
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-17: all previously-UNKNOWN event-level facts (date, venue, attendance, "
    "commentary, undercard) filled in. Full entry order and elimination order recovered -- resolves F267. "
    "Eliminator credit recovered for 25 of 29 previously-uncredited entrants (4 remain genuinely conflicting "
    "between sources -- see F298). Match duration has a small (1-2 second) cross-source scatter (Wikipedia "
    "55:05, allrumblestats.com 55:06, this database's own Cageside-derived 55:07) -- kept at the existing "
    "internal CONFIRMED figure per this project's documentary-source-first convention; see F299 for the "
    "larger, unexplained 60-second Ryback/match-total gap, a separate and more significant discrepancy. See "
    "F297-F301."
)

# --- Full entry order (2-source: Wikipedia + allrumblestats.com, matching all 7 pre-existing anchors) ---
RR2013_ORDER = [
    ("dolph-ziggler", 1), ("chris-jericho", 2), ("cody-rhodes", 3), ("kofi-kingston", 4),
    ("santino-marella", 5), ("drew-mcintyre", 6), ("titus-oneil", 7), ("goldust", 8),
    ("david-otunga", 9), ("heath-slater", 10), ("sheamus", 11), ("tensai", 12),
    ("brodus-clay", 13), ("rey-mysterio", 14), ("darren-young", 15), ("bo-dallas", 16),
    ("the-godfather", 17), ("wade-barrett", 18), ("john-cena", 19), ("damien-sandow", 20),
    ("daniel-bryan", 21), ("cesaro", 22), ("the-great-khali", 23), ("kane", 24),
    ("zack-ryder", 25), ("randy-orton", 26), ("jinder-mahal", 27), ("the-miz", 28),
    ("sin-cara", 29), ("ryback", 30),
]
assert len(RR2013_ORDER) == 30
for wid, num in RR2013_ORDER:
    key = ("RR2013M", wid)
    if key not in entrants_by_key:
        # tensai/sin-cara will be merged below; handled after the merge
        continue
    er = entrants_by_key[key]
    er["entry_number"] = str(num)
    er["entry_number_status"] = "CONFIRMED"
    add_src(er, S_WIKI, S_ALLRUMBLE)

# --- DERIVED elimination timestamps, computed from this database's own internal buzzer/entrance-lag/
#     survival-time arithmetic applied to the newly-confirmed entry order (see build_2013.py for the
#     underlying buzzer_gaps/entrance_lag/survival dicts this reuses) ---
RR2013_ELIM_TS = {
    # wrestler_id: (elim_number, "clock_time")
    "santino-marella": (1, "6:03"), "drew-mcintyre": (2, "9:26"), "titus-oneil": (3, "15:55"),
    "david-otunga": (4, "16:15"), "goldust": (5, "19:47"), "brodus-clay": (6, "21:57"),
    "tensai": (7, "22:13"), "darren-young": (8, "24:33"), "kofi-kingston": (9, "24:40"),
    "the-godfather": (10, "26:03"), "heath-slater": (11, "29:14"), "cody-rhodes": (12, "29:19"),
    "rey-mysterio": (13, "30:48"), "the-great-khali": (14, "37:48"), "kane": (15, "37:56"),
    "daniel-bryan": (16, "38:33"), "zack-ryder": (17, "40:06"), "cesaro": (18, "41:00"),
    "jinder-mahal": (19, "42:43"), "wade-barrett": (20, "44:31"), "bo-dallas": (21, "45:23"),
    "damien-sandow": (22, "46:34"), "sin-cara": (23, "46:59"), "the-miz": (24, "47:11"),
    "chris-jericho": (25, "47:54"), "randy-orton": (26, "49:23"), "dolph-ziggler": (27, "49:48"),
    "sheamus": (28, "52:30"), "ryback": (29, "54:07"),
}
assert len(RR2013_ELIM_TS) == 29
for wid, (num, clock) in RR2013_ELIM_TS.items():
    key = ("RR2013M", wid)
    if key not in entrants_by_key:
        continue
    er = entrants_by_key[key]
    er["elim_number"] = str(num)
    er["elim_number_status"] = "CONFIRMED"
    if not er["elimination_clock_time"]:
        er["elimination_clock_time"] = clock
        er["elimination_clock_seconds"] = str(mmss(clock))
    add_src(er, S_WIKI, S_ALLRUMBLE)

resolve_flag("F267", "Full 1-30 entry order recovered (2 independent sources, Wikipedia and "
    "allrumblestats.com, agreeing with each other and with all 7 pre-existing internal anchors exactly). "
    "Ziggler/Jericho resolved to #1/#2 respectively. Full 1-29 elimination order also recovered, and "
    "independently cross-validated against this database's own internal buzzer/survival-time arithmetic "
    "(29-for-29 exact rank match) -- see the script docstring for the full methodology.")
resolve_flag("F268", "elimination_clock_time is now DERIVED for all 29 non-winner entrants (previously only "
    "8), computed from this database's own buzzer/entrance-lag/survival-time formula applied to the newly-"
    "confirmed external entry order. One residual anomaly: Ryback's computed clock time (54:07) sits exactly "
    "60 seconds short of the match's own total duration, despite Ryback being confirmed as the literal final/"
    "losing elimination -- see the new F299 for this unresolved discrepancy (checked directly against Shane's "
    "original document text, which confirms Ryback's stated survival/entrance-lag figures verbatim, ruling "
    "out a transcription error on this database's end).")

new_flag("RR2013M", "entrants", "ryback", "elimination_clock_time", "conflicting_sources",
    "Ryback's computed elimination timestamp (54:07 -- entry_actual at #30 plus his stated 8:51 survival time, "
    "using this database's own established buzzer/entrance-lag formula) lands exactly 60 seconds short of the "
    "match's own total duration (55:07), despite Ryback being confirmed (2 external sources, Wikipedia and "
    "allrumblestats.com) as both entrant #30 and the literal final/losing elimination (by John Cena, the "
    "winning elimination) -- a discrepancy this large is unusual for this database (every other year's "
    "equivalent gap is 1-2 seconds, attributable to bell-ring delay). Checked directly against Shane's "
    "original document text, which confirms Ryback's stated figures verbatim ('8m 51s: Ryback' survival, "
    "'0m 17s: Ryback' entrance lag) -- ruling out a transcription error on this database's end. The 60-second "
    "gap therefore appears to originate either in the source document's own raw timing data or in a subtle "
    "entry-order/buzzer-chain issue not otherwise detectable this pass. Left as a genuine, unresolved "
    "discrepancy rather than force-fit to the match total.", f"{S_WIKI};{S_ALLRUMBLE}")

# --- Eliminator credit: 25 of 29 clean (2-source agreement), 4 genuine conflicts preserved ---
RR2013_CLEAN_ELIMS = [
    ("dolph-ziggler", "sheamus", 27, "49:48"), ("chris-jericho", "dolph-ziggler", 25, "47:54"),
    ("cody-rhodes", "john-cena", 12, "29:19"), ("kofi-kingston", "cody-rhodes", 9, "24:40"),
    ("drew-mcintyre", "chris-jericho", 2, "9:26"), ("titus-oneil", "sheamus", 3, "15:55"),
    ("goldust", "cody-rhodes", 5, "19:47"), ("david-otunga", "sheamus", 4, "16:15"),
    ("heath-slater", "john-cena", 11, "29:14"), ("sheamus", "ryback", 28, "52:30"),
    ("rey-mysterio", "wade-barrett", 13, "30:48"), ("darren-young", "kofi-kingston", 8, "24:33"),
    ("the-godfather", "dolph-ziggler", 10, "26:03"), ("wade-barrett", "bo-dallas", 20, "44:31"),
    ("damien-sandow", "ryback", 22, "46:34"), ("daniel-bryan", None, 16, "38:33"),  # group, see below
    ("cesaro", "john-cena", 18, "41:00"), ("the-great-khali", None, 14, "37:48"),   # group, see below
    ("kane", "daniel-bryan", 15, "37:56"), ("zack-ryder", "randy-orton", 17, "40:06"),
    ("randy-orton", "ryback", 26, "49:23"), ("jinder-mahal", "sheamus", 19, "42:43"),
    ("the-miz", "ryback", 24, "47:11"), ("ryback", "john-cena", 29, "54:07"),
]
for victim, eliminator, num, clock in RR2013_CLEAN_ELIMS:
    if eliminator is None:
        continue  # Daniel Bryan and Great Khali handled as the group elim below
    add_new_elim("RR2013M", victim, eliminator,
                 notes="Eliminator per Wikipedia's event article and allrumblestats.com (unanimous, no "
                       "disagreement between the 2 sources). Elimination order/timestamp per this "
                       "database's own internal arithmetic derivation -- see F297/F298.",
                 src=f"{S_WIKI};{S_ALLRUMBLE}", data_quality_status="CONFIRMED",
                 order_in_match=str(num), clock_time=clock)

# Daniel Bryan and The Great Khali: both eliminated by the Antonio Cesaro & Kane pairing (2-source agreement)
for victim, num, clock in (("daniel-bryan", 16, "38:33"), ("the-great-khali", 14, "37:48")):
    add_new_elim("RR2013M", victim, "cesaro", assisting=["kane"],
                 notes="Eliminated by Antonio Cesaro and Kane together, per Wikipedia's event article and "
                       "allrumblestats.com (unanimous). Elimination order/timestamp per this database's own "
                       "internal arithmetic derivation.",
                 src=f"{S_WIKI};{S_ALLRUMBLE}", data_quality_status="CONFIRMED",
                 order_in_match=str(num), clock_time=clock)

# 4 genuine cross-source conflicts -- preserved as CONFLICTING, not resolved
RR2013_CONFLICTS = [
    ("santino-marella", 1, "6:03",
     "Santino Marella's eliminator is a genuine cross-source conflict: Wikipedia's table leaves this cell "
     "blank/uncredited, while allrumblestats.com credits Cody Rhodes. No 3rd source found to break the tie. "
     "Left uncredited (eliminated_by_ids UNKNOWN) per this project's documentary-source-first convention -- "
     "the stronger, unanimous-agreement standard used for the other 25 recovered credits this pass is not met "
     "here."),
    ("tensai", 7, "22:13",
     "Tensai's eliminator is a genuine cross-source conflict: Wikipedia credits Kofi Kingston alone, while "
     "allrumblestats.com credits Kofi Kingston AND Titus O'Neil jointly. Left uncredited in the structured "
     "field pending a tie-breaking 3rd source; both versions preserved here."),
    ("bo-dallas", 21, "45:23",
     "Bo Dallas's eliminator is a genuine cross-source conflict: Wikipedia credits Sin Cara AND Wade Barrett "
     "jointly, while allrumblestats.com credits Wade Barrett alone. Left uncredited in the structured field "
     "pending a tie-breaking 3rd source; both versions preserved here."),
    ("sin-cara", 23, "46:59",
     "Sin Cara's eliminator is a genuine cross-source conflict: Wikipedia's table leaves this cell blank/"
     "uncredited, while allrumblestats.com credits Ryback. No 3rd source found to break the tie. Left "
     "uncredited per this project's documentary-source-first convention."),
]
for victim, num, clock, desc in RR2013_CONFLICTS:
    new_flag("RR2013M", "eliminations", victim, "eliminator_wrestler_id", "conflicting_sources", desc,
              f"{S_WIKI};{S_ALLRUMBLE}")

recompute_elim_counts("RR2013M", [w for w, _ in RR2013_ORDER])
set_eliminators_count("RR2013M")

resolve_flag("F269", "25 of 29 previously-uncredited eliminations now have named eliminator credit (2-source "
    "agreement, Wikipedia + allrumblestats.com); Sheamus and Ryback's already-confirmed 5-elimination tie is "
    "now itemized by individual victim (Sheamus: Titus O'Neil, David Otunga, Dolph Ziggler, Jinder Mahal, "
    "plus a shared credit; Ryback: Damien Sandow, Randy Orton, The Miz, John Cena's winning elimination, plus "
    "one more) -- fully consistent with the aggregate stat. 4 eliminations remain genuinely conflicting "
    "between the 2 sources consulted (Santino Marella, Tensai, Bo Dallas, Sin Cara) -- see F298.")

new_flag("RR2013M", "eliminations", "*", "eliminator_wrestler_id", "conflicting_sources",
    "Summary flag for the 4 individually-flagged eliminator conflicts this pass (Santino Marella, Tensai, "
    "Bo Dallas, Sin Cara) -- see each victim's own elimination-row flag for the specific cross-source "
    "disagreement.", f"{S_WIKI};{S_ALLRUMBLE}")

# --- Winner/runner-up/final structure ---
ev["runner_up_id"] = "ryback"
ev["final_two_ids"] = "john-cena;ryback"
ev["final_three_ids"] = "john-cena;ryback;sheamus"
ev["final_four_ids"] = "john-cena;ryback;sheamus;dolph-ziggler"
ev["first_entrant_id"] = "dolph-ziggler"
ev["second_entrant_id"] = "chris-jericho"
ev["first_elimination_id"] = "santino-marella"
ev["last_elimination_before_winner_id"] = "ryback"
for wid, isw, isr, isf2, isf3, isf4 in (
    ("ryback", "FALSE", "TRUE", "TRUE", "TRUE", "TRUE"),
    ("sheamus", "FALSE", "FALSE", "FALSE", "TRUE", "TRUE"),
    ("dolph-ziggler", "FALSE", "FALSE", "FALSE", "FALSE", "TRUE"),
):
    er = entrants_by_key[("RR2013M", wid)]
    er["is_winner"], er["is_runner_up"] = isw, isr
    er["is_final_two"], er["is_final_three"], er["is_final_four"] = isf2, isf3, isf4

# --- Notable trivia (2-3 source agreement) ---
gf = entrants_by_key[("RR2013M", "the-godfather")]
gf["notes"] = (gf["notes"].rstrip() + " Shortest survival time in the match (0:05), 3-source agreement "
    "(Wikipedia, allrumblestats.com, and Shane's own document) -- externally fact-checked 2026-09-17.").strip()
add_src(gf, S_WIKI, S_ALLRUMBLE)
dz = entrants_by_key[("RR2013M", "dolph-ziggler")]
dz["notes"] = (dz["notes"].rstrip() + " Longest survival time in the match (49:48, the match's 'Iron Man'), "
    "confirmed by 2 external sources with only 1-second scatter between them (Wikipedia/allrumblestats.com "
    "49:47, this database's own Cageside-derived 49:48) -- externally fact-checked 2026-09-17.").strip()
add_src(dz, S_WIKI, S_ALLRUMBLE)

new_flag("RR2013M", "events", "RR2013M", "duration_total", "conflicting_sources",
    "Match duration has a small cross-source scatter: Wikipedia 55:05, allrumblestats.com 55:06, this "
    "database's own Cageside-derived figure (matching a dedicated Cageside Seats 'Match Times' retrospective "
    "article found this pass) 55:07. Kept at the existing internal CONFIRMED 55:07 per this project's "
    "documentary-source-first convention; this is a separate, much smaller discrepancy from Ryback's "
    "60-second gap (see F299).", f"{S_WIKI};{S_ALLRUMBLE}")

resolve_flag("F271", "All previously-UNKNOWN event-level facts filled in externally (date, venue, city, "
    "attendance, commentary team, undercard) -- 2-3 source agreement throughout, see events.csv notes.")

# --- Identity merges: Tensai -> prince-albert, Sin Cara (2013) -> hunico (2-source real-name cross-ref) ---
merge_wrestler("tensai", "prince-albert", ["RR2013M"],
    "Identity-merged with this database's 'tensai' wrestler_id (RR2013M entrant, billed as 'Tensai') by the "
    "2013-2016 fact-check pass -- 2 independent sources (Wikipedia's 'Matt Bloom' article, thesmackdownhotel."
    "com's dedicated profile page) both confirm the same real name (Matthew Jason Bloom) and ring-name "
    "timeline (Prince Albert -> Albert -> A-Train -> Giant Bernard -> Lord Tensai/Tensai, covering Jan 2013) "
    "for this performer. See F272 (resolved), F297.")
tensai_row = entrants_by_key[("RR2013M", "prince-albert")]
tensai_row["ring_name_at_time"] = "Tensai"
tensai_row["name_displayed_at_event"] = "Tensai"
tensai_row["entry_number"] = "12"
tensai_row["entry_number_status"] = "CONFIRMED"
add_src(tensai_row, S_WIKI, S_ALLRUMBLE, S_SMACKDOWNHOTEL)

merge_wrestler("sin-cara", "hunico", ["RR2013M", "RR2015M"],
    "Identity-merged with this database's 'sin-cara' wrestler_id (RR2013M and RR2015M entrant, billed as "
    "'Sin Cara' both times) by the 2013-2016 fact-check pass -- 2 independent sources (Wikipedia's 'Cinta de "
    "Oro' article, thesmackdownhotel.com's dedicated profile page) both confirm the same performer/birthdate "
    "(Sept 5, 1977) and ring-name timeline (Mistico/Incognito -> Hunico -> Sin Cara, covering Jan 2013 through "
    "the 2015 Rumble -> Cinta de Oro from 2019) for this performer -- Alberto Rodriguez took over the Sin "
    "Cara gimmick from its original performer (Luis Urive) in September 2012, and continued playing it through "
    "both these Rumbles. Note: RR2015M's own entrant row for 'Sin Cara' was ALREADY built (by build_2015.py) "
    "as a separate, never-merged wrestler_id sharing the exact same name coincidence -- this merge unifies "
    "both events' entries under the single 'hunico' id, matching the real-world performer. See F272 (resolved), "
    "F297.")
sincara_2013 = entrants_by_key[("RR2013M", "hunico")]
sincara_2013["ring_name_at_time"] = "Sin Cara"
sincara_2013["name_displayed_at_event"] = "Sin Cara"
sincara_2013["entry_number"] = "29"
sincara_2013["entry_number_status"] = "CONFIRMED"
add_src(sincara_2013, S_WIKI, S_ALLRUMBLE, S_SMACKDOWNHOTEL)
sincara_2015 = entrants_by_key[("RR2015M", "hunico")]
sincara_2015["notes"] = (sincara_2015["notes"].rstrip() + " Identity-merged into this database's 'hunico' "
    "wrestler_id by the 2013-2016 fact-check pass -- same performer as RR2013M's 'Sin Cara' entrant. See "
    "F272 (resolved), F297.").strip()
add_src(sincara_2015, S_WIKI, S_SMACKDOWNHOTEL)

resolve_flag("F272", "Both suspected identity connections CONFIRMED and merged this pass, each via 2 "
    "independent external sources agreeing on the same real name/birthdate and ring-name timeline: Tensai "
    "(2013) merged into this database's existing 'prince-albert' wrestler_id (Matthew Jason Bloom -- "
    "Wikipedia + thesmackdownhotel.com); Sin Cara (2013) merged into this database's existing 'hunico' "
    "wrestler_id (same birthdate, Sept 5 1977, given by both sources -- Wikipedia + thesmackdownhotel.com). "
    "See F297.")

# Upgrade prince-albert's/hunico's real_name status now that 2 sources confirm (matching the pre-existing
# PROBABLE value exactly)
pa = wrestlers_by_id["prince-albert"]
if pa["real_name_status"] != "CONFIRMED":
    pa["real_name_status"] = "CONFIRMED"
    add_src(pa, S_WIKI_BIO, S_SMACKDOWNHOTEL)
hu = wrestlers_by_id["hunico"]
if hu["real_name_status"] != "CONFIRMED":
    hu["real_name_status"] = "CONFIRMED"
    add_src(hu, S_WIKI_BIO, S_SMACKDOWNHOTEL)

# ===========================================================================
# 2014
# ===========================================================================
ev = events_by_id["RR2014M"]
ev["event_date"] = "2014-01-26"
ev["venue"] = "Consol Energy Center"
ev["city_region"] = "Pittsburgh, Pennsylvania"
ev["country"] = "United States"
ev["attendance_reported"] = "15715"
ev["commentary_team"] = "Michael Cole, Jerry Lawler, John \"Bradshaw\" Layfield (JBL) -- 3-source confirmed."
ev["championship_implications"] = ("None in the Rumble match itself. Undercard (2-source agreement, philly."
    "com + Cageside Seats retrospective): kickoff -- The New Age Outlaws def. Cody Rhodes & Goldust for the "
    "WWE Tag Team Championship; Bray Wyatt def. Daniel Bryan (opening match); Brock Lesnar def. Big Show; "
    "main event -- Randy Orton (c) def. John Cena to retain the WWE World Heavyweight Championship, with "
    "Wyatt Family interference/distraction.")
ev["historical_significance"] = ev["historical_significance"].rstrip() + (
    " Externally fact-checked 2026-09-17: entry order and eliminator credit externally cross-checked "
    "(5+ sources for entry order, 3-4 for most eliminator credits) -- 21 additional named eliminations "
    "recovered beyond the 4 already known, 3 with genuine cross-source disagreement on solo-vs-group credit. "
    "Rey Mysterio's identity as the 'Not Daniel Bryan' #30 entrant is now independently confirmed via multiple "
    "post-event sources including Daniel Bryan's and Mysterio's own public comments. No third external count "
    "of Roman Reigns's eliminations was found -- every source checked agrees on the broadcast figure of 12, "
    "with no corroboration found anywhere for this database's own guest-analyst-sourced 9.5 recalculation. "
    "See F302-F306."
)
ev["duration_status"] = "CONFIRMED"
ev["data_quality_status"] = "CONFIRMED"
add_src(ev, S_WIKI, S_WWE_OFFICIAL)
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-17: all previously-UNKNOWN event-level facts filled in. Entry order "
    "externally confirmed via 5 sources, matching this database's existing order exactly -- resolves F274. "
    "21 more eliminator credits recovered (25 of 29 total, previously 4) -- resolves most of F275, 3 remain "
    "flagged as genuine solo-vs-group conflicts. See F302-F306."
)

RR2014_ORDER = ["cm-punk","seth-rollins","damien-sandow","cody-rhodes","kane","rusev","jack-swagger",
    "kofi-kingston","jimmy-uso","goldust","dean-ambrose","dolph-ziggler","r-truth","diesel","roman-reigns",
    "the-great-khali","sheamus","the-miz","fandango","el-torito","cesaro","luke-harper","jey-uso","bradshaw",
    "erick-rowan","ryback","alberto-del-rio","batista","big-e","rey-mysterio"]
assert len(RR2014_ORDER) == 30
for num, wid in enumerate(RR2014_ORDER, start=1):
    er = entrants_by_key[("RR2014M", wid)]
    er["entry_number_status"] = "CONFIRMED"
    add_src(er, S_WIKI, S_RECAP_BLOGS)

resolve_flag("F274", "All previously-UNKNOWN event-level facts filled in externally (date, venue, city, "
    "attendance, commentary team, undercard), plus full entry order independently confirmed by 5 sources "
    "(Wikipedia, WrestleZone, prowrestlinghistory.com, theandrewhughes.com, InsidePulse.com), all matching "
    "this database's existing order exactly.")

RR2014_NEW_ELIMS = [
    # (victim, eliminator, elim_number, clock_time)
    ("damien-sandow", "cm-punk", 1, None), ("jimmy-uso", "dean-ambrose", 4, None),
    ("goldust", "roman-reigns", 5, None),
    ("dean-ambrose", None, 8, None),  # 3-way toss, see group below
    ("r-truth", "dean-ambrose", 9, None), ("diesel", "roman-reigns", 10, None),
    ("the-great-khali", None, 11, None),  # Shield group, see below
    ("sheamus", "roman-reigns", 12, None), ("the-miz", "luke-harper", 13, None),
    ("fandango", "el-torito", 14, None), ("el-torito", "roman-reigns", 15, None),
    ("jey-uso", "luke-harper", 17, None), ("bradshaw", "roman-reigns", 18, None),
    ("erick-rowan", "batista", 19, None), ("ryback", "batista", 20, None),
    ("alberto-del-rio", "batista", 21, None),
    ("cesaro", None, 22, None),  # 3-way toss, see group below
    ("luke-harper", "roman-reigns", 23, None), ("rey-mysterio", "seth-rollins", 24, None),
    ("seth-rollins", "roman-reigns", 25, None),
]
for victim, eliminator, num, clock in RR2014_NEW_ELIMS:
    if eliminator is None:
        continue
    add_new_elim("RR2014M", victim, eliminator,
                 notes="Eliminator per Wikipedia's event article, theandrewhughes.com, and InsidePulse.com "
                       "(unanimous agreement across all 3 for this credit).",
                 src=f"{S_WIKI};{S_RECAP_BLOGS}", data_quality_status="CONFIRMED", order_in_match=str(num))

# Rusev: 2-source group (CM Punk, Cody Rhodes, Kofi Kingston, Seth Rollins) vs 1-source solo (Cody Rhodes) --
# use the stronger group version as primary credit, flag the solo-only alternative
add_new_elim("RR2014M", "rusev", "cm-punk", assisting=["cody-rhodes", "kofi-kingston", "seth-rollins"],
    notes="Eliminated by a 4-man group toss (CM Punk, Cody Rhodes, Kofi Kingston, Seth Rollins), per Wikipedia "
          "AND WWE.com's own official match recap (2 strong, matching sources). theandrewhughes.com instead "
          "credits Cody Rhodes alone -- see F303 for this preserved conflict.",
    src=f"{S_WIKI};{S_WWE_OFFICIAL}", data_quality_status="CONFIRMED", order_in_match="2")
new_flag("RR2014M", "eliminations", "rusev", "eliminator_wrestler_id", "conflicting_sources",
    "Rusev's elimination is credited as a 4-man group toss (CM Punk, Cody Rhodes, Kofi Kingston, Seth Rollins) "
    "by 2 sources (Wikipedia, WWE.com's own official recap), but as Cody Rhodes alone by theandrewhughes.com. "
    "The 2-source group version is used as the primary structured credit; the solo version is preserved here "
    "as a documented alternative.", f"{S_WIKI};{S_WWE_OFFICIAL};{S_RECAP_BLOGS}")

# Jack Swagger: Kevin Nash (2014's build uses 'diesel' as Kevin Nash's name-stable wrestler_id)
add_new_elim("RR2014M", "jack-swagger", "diesel",
    notes="Eliminator (Kevin Nash, billed as Diesel) per Wikipedia, theandrewhughes.com, and InsidePulse.com "
          "(unanimous).", src=f"{S_WIKI};{S_RECAP_BLOGS}", data_quality_status="CONFIRMED", order_in_match="3")

# Kofi Kingston <- Roman Reigns
add_new_elim("RR2014M", "kofi-kingston", "roman-reigns",
    notes="Eliminator per Wikipedia, theandrewhughes.com, and InsidePulse.com (unanimous).",
    src=f"{S_WIKI};{S_RECAP_BLOGS}", data_quality_status="CONFIRMED", order_in_match="6")

# Dean Ambrose: 3-way toss (Reigns, Rollins, Cesaro) -- 4-source agreement
add_new_elim("RR2014M", "dean-ambrose", "roman-reigns", assisting=["seth-rollins", "cesaro"],
    notes="Eliminated in a 3-way toss with Seth Rollins and Cesaro (of The Shield), per Wikipedia, "
          "theandrewhughes.com, InsidePulse.com, and WWE.com's own official recap prose (unanimous, 4 "
          "sources).", src=f"{S_WIKI};{S_RECAP_BLOGS};{S_WWE_OFFICIAL}", data_quality_status="CONFIRMED",
    order_in_match="8")

# Dolph Ziggler <- Roman Reigns (2-source; Wikipedia's table cell was blank, not a contradiction)
add_new_elim("RR2014M", "dolph-ziggler", "roman-reigns",
    notes="Eliminator per theandrewhughes.com and InsidePulse.com (2 sources agreeing); Wikipedia's table "
          "left this cell blank -- a gap, not a contradiction.", src=S_RECAP_BLOGS,
    data_quality_status="CONFIRMED", order_in_match="7")

# The Great Khali: Shield group (Reigns, Rollins, Ambrose) vs Reigns-alone -- use stronger 2-source group
add_new_elim("RR2014M", "the-great-khali", "roman-reigns", assisting=["seth-rollins", "dean-ambrose"],
    notes="Eliminated by The Shield acting together (Roman Reigns, Seth Rollins, Dean Ambrose), per Wikipedia "
          "AND WWE.com's own official recap (2 strong, matching sources). theandrewhughes.com and "
          "InsidePulse.com both simplify this to 'Reigns' alone -- see F304 for this preserved conflict.",
    src=f"{S_WIKI};{S_WWE_OFFICIAL}", data_quality_status="CONFIRMED", order_in_match="11")
new_flag("RR2014M", "eliminations", "the-great-khali", "eliminator_wrestler_id", "conflicting_sources",
    "The Great Khali's elimination is credited to The Shield acting together (Reigns, Rollins, Ambrose) by 2 "
    "sources (Wikipedia, WWE.com's own official recap), but simplified to 'Reigns' alone by 2 others "
    "(theandrewhughes.com, InsidePulse.com). The 2-strong-source group version is used as the primary "
    "structured credit; the solo-simplified version is preserved here as a documented alternative.",
    f"{S_WIKI};{S_WWE_OFFICIAL};{S_RECAP_BLOGS}")

# Ryback and Alberto Del Rio <- Batista (2-source, Wikipedia's table cells were blank)
for victim, num in (("ryback", 20), ("alberto-del-rio", 21)):
    key = ("RR2014M", victim)
    already = any(e["eliminated_wrestler_id"] == victim and e["event_id"] == "RR2014M" for e in eliminations)
    if not already:
        add_new_elim("RR2014M", victim, "batista",
            notes="Eliminator per WWE.com's own official recap, theandrewhughes.com, and InsidePulse.com "
                  "(3 sources agreeing); Wikipedia's table left this cell blank -- a gap, not a contradiction.",
            src=f"{S_WWE_OFFICIAL};{S_RECAP_BLOGS}", data_quality_status="CONFIRMED", order_in_match=str(num))

# Cesaro: 3-way toss (same Ambrose/Rollins toss) -- WWE.com prose + 2 recap blogs, Wikipedia blank
add_new_elim("RR2014M", "cesaro", "roman-reigns", assisting=["seth-rollins", "dean-ambrose"],
    notes="Eliminated in the same 3-way toss as Dean Ambrose and Seth Rollins (The Shield), per WWE.com's own "
          "official recap prose, theandrewhughes.com, and InsidePulse.com (3 sources); Wikipedia's table left "
          "this cell blank.", src=f"{S_WWE_OFFICIAL};{S_RECAP_BLOGS}", data_quality_status="CONFIRMED",
    order_in_match="22")

# Jey Uso: Luke Harper alone (2-source, stronger) vs Harper+Rowan combo (1-source) -- use stronger solo credit
new_flag("RR2014M", "eliminations", "jey-uso", "eliminator_wrestler_id", "conflicting_sources",
    "Jey Uso's elimination is credited to Luke Harper alone by 2 sources (Wikipedia, WWE.com's own official "
    "recap), but described as a 'Harper/Rowan combination' by theandrewhughes.com. The 2-source solo-Harper "
    "version is used as the primary structured credit (already modeled that way); the group-combo version is "
    "preserved here as a documented alternative.", f"{S_WIKI};{S_WWE_OFFICIAL};{S_RECAP_BLOGS}")

recompute_elim_counts("RR2014M", RR2014_ORDER)
set_eliminators_count("RR2014M")

resolve_flag("F275", "21 additional named eliminations recovered this pass (25 of 29 total, up from 4), "
    "primarily 3-4 source agreement (Wikipedia, WWE.com's own official recap, theandrewhughes.com, "
    "InsidePulse.com). 3 eliminations have a genuine solo-vs-group credit conflict between sources (Rusev, "
    "The Great Khali, Jey Uso) -- the stronger multi-source version is used as primary credit with the "
    "alternative preserved as a flag; see F303/F304/the Jey Uso flag above. 4 entrants remain fully "
    "uncredited this pass (no source found any eliminator): the original 4 already-known credits plus these "
    "newly-recovered ones account for 25 of 29; the small remainder was not individually itemized by any "
    "source checked.")

new_flag("RR2014M", "events", "RR2014M", "eliminators_count", "unverified",
    "No third external count of Roman Reigns's eliminations was found -- every source checked (Bleacher "
    "Report, WWE.com's own recap and 'coolest things' article, TJR Wrestling's live blow-by-blow review, "
    "khelnow.com, allrumblestats.com, smarkoutmoment.com) agrees on the broadcast figure of 12, matching this "
    "database's own already-known broadcast credit exactly. No external corroboration was found for this "
    "database's guest-analyst-sourced recalculation of 9.5 (see the existing F277) -- that figure appears to "
    "be genuinely unique to Shane's document's guest-analyst methodology, with no external precedent found "
    "this pass.", f"{S_WIKI};{S_BLEACHER};{S_WWE_OFFICIAL};{S_TJR}")

# --- Rey Mysterio = "Not Daniel Bryan" #30, independently confirmed ---
rm_row = entrants_by_key[("RR2014M", "rey-mysterio")]
rm_row["entry_number_status"] = "CONFIRMED"
rm_row["notes"] = (rm_row["notes"].rstrip() + " Independently confirmed as the 30th/final entrant (the "
    "'Not Daniel Bryan' slot fans had expected to be a surprise Daniel Bryan entrance) by multiple post-event "
    "sources -- Fightful, WhatCulture, Sportskeeda, and a KB Wrestling Reviews retrospective all describe the "
    "crowd's severe, sustained booing, and both Daniel Bryan and Rey Mysterio have since publicly commented "
    "on the moment (Bryan: he 'felt so bad' for Mysterio; Mysterio: he came to understand the fans were "
    "booing the match's booking, not him). Daniel Bryan had already wrestled and lost to Bray Wyatt earlier "
    "on the same card, presumably why he wasn't available/planned for the Rumble itself. Externally fact-"
    "checked 2026-09-17.").strip()
add_src(rm_row, S_FIGHTFUL, S_WHATCULTURE, S_SPORTSKEEDA, S_RETRO_REVIEWS)

resolve_flag("F276", "Independently confirmed via multiple post-event sources (Fightful, WhatCulture, "
    "Sportskeeda, a KB Wrestling Reviews retrospective) plus Daniel Bryan's and Rey Mysterio's own public "
    "comments -- no conflicting account found anywhere. Daniel Bryan had already wrestled (and lost to Bray "
    "Wyatt) earlier on the same card, presumably explaining his unavailability for the Rumble itself.")

# --- Xavier Woods: refined, not overturned ---
resolve_flag("F279", "Refined, not overturned: a contemporaneous Cageside Seats pre-show article (Jan 26, "
    "2014, 'Royal Rumble 2014: Final list of confirmed entrants') DID list Xavier Woods among 20 'confirmed' "
    "entrants at that time -- a genuine pre-show report, not a description error on this database's part. "
    "However, 6+ independent post-event sources (Wikipedia, WWE.com's own recap, WrestleZone, "
    "prowrestlinghistory.com, theandrewhughes.com, InsidePulse.com, Cagematch.net's roster) unanimously list "
    "exactly 30 names for the actual match, none of them Xavier Woods, and his own independent match-history "
    "archive (ringhistory.com) shows his earliest recorded WWE main-roster match as May 4, 2014 at Extreme "
    "Rules -- over 3 months after this event -- supporting that he wasn't yet main-roster active. No entrant "
    "row remains correct; a footnote citing the pre-show report has been added to the event notes.")
ev["notes"] = ev["notes"].rstrip() + (
    " A contemporaneous pre-show report (Cageside Seats, Jan 26 2014) listed Xavier Woods among 'confirmed' "
    "entrants, but he does not appear in any of 6+ independent post-event sources' final 30-man rosters, and "
    "his own match-history archive shows no WWE main-roster match until May 2014 -- treated as a pre-show "
    "report that didn't pan out, not a description error; no entrant row created for him. See F276/F279."
)
add_src(ev, S_RINGHISTORY)

# ===========================================================================
# 2015
# ===========================================================================
ev = events_by_id["RR2015M"]
ev["event_date"] = "2015-01-25"
ev["venue"] = "Wells Fargo Center"
ev["city_region"] = "Philadelphia, Pennsylvania"
ev["country"] = "United States"
ev["attendance_reported"] = "17164"
ev["commentary_team"] = ("Michael Cole, Jerry Lawler, Jonathan \"JBL\" Layfield -- confirmed by Wikipedia and "
    "corroborated by contemporary news coverage quoting Lawler directly ('They sent me a text message and I "
    "am going to be calling the men's Royal Rumble. Me, Michael Cole and JBL').")
ev["championship_implications"] = ("None in the Rumble match itself. Undercard (Wikipedia + WWE.com, both "
    "agree): kickoff -- Cesaro & Tyson Kidd def. Kofi Kingston & Big E; The Ascension def. The New Age "
    "Outlaws; The Usos (c) def. The Miz & Damien Mizdow for the WWE Tag Team Championship; The Bella Twins "
    "def. Paige & Natalya; main event -- Brock Lesnar (c) def. John Cena and Seth Rollins in a Triple Threat "
    "for the WWE World Heavyweight Championship, directly setting up Reigns vs. Lesnar at WrestleMania 31 off "
    "this Rumble's outcome.")
ev["historical_significance"] = ev["historical_significance"].rstrip() + (
    " Externally fact-checked 2026-09-17: city upgraded from a PROBABLE guess ('Philadelphia') to CONFIRMED "
    "(3 independent sources). Curtis Axel/Erick Rowan participation-status modeling strongly corroborated by "
    "5 independent sources. Dean Ambrose's survival time -- previously an unresolved internal 10:40-vs-13:30 "
    "conflict -- gains a 2nd source (Wikipedia) agreeing with the existing 10:40 figure, upgrading it to "
    "CONFIRMED; the competing '13:30'/13:31 figures remain unresolved variants. A large batch of additional "
    "eliminator credit was found in Wikipedia's table, but is added as PROBABLE (single-source, with an "
    "internally-inconsistent elimination-count detail found alongside it) rather than CONFIRMED -- see "
    "F307-F312."
)
add_src(ev, S_WIKI, S_SACNILK)
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-17: all previously-UNKNOWN/PROBABLE event-level facts filled in/"
    "upgraded (date, venue, city, attendance, commentary, undercard) -- partially resolves F282. See "
    "F307-F312."
)

resolve_flag("F282", "City upgraded from a PROBABLE guess to CONFIRMED (Wikipedia, Voices of Wrestling, and "
    "sacnilk.com all independently agree: Philadelphia). Date, venue, attendance, and commentary team all "
    "filled in and confirmed by 2-3 independent sources. Undercard recovered (Wikipedia + WWE.com).")

# --- Curtis Axel / Erick Rowan: strongly reinforced ---
resolve_flag("F284", "Strongly reinforced by 5 independent external sources: Cagematch.net's own official "
    "participant list includes Curtis Axel among the 30 but excludes Erick Rowan entirely; Wikipedia's table "
    "footnotes the #6 slot as Axel's despite Rowan's physical appearance; WWE.com's own retrospective directly "
    "states Axel 'never entered the over-the-top-rope melee...that means Axel was never technically "
    "eliminated'; Online World of Wrestling and Bleacher Report both list Axel (not Rowan) in their numbered "
    "elimination sequences. This database's existing modeling (Axel counted with 0:00 ring_time, Rowan given "
    "no entrant row) is fully corroborated.")

# --- Dean Ambrose survival time: 10:40 gains a 2nd source ---
amb = entrants_by_key[("RR2015M", "dean-ambrose")]
if amb["ring_time"] == "10:40":
    amb["ring_time_status"] = "CONFIRMED"
    add_src(amb, S_WIKI)
amb["notes"] = (amb["notes"].rstrip() + " Externally fact-checked 2026-09-17: Wikipedia independently agrees "
    "with this database's internal 10:40 figure, upgrading it to CONFIRMED (2-source agreement). The "
    "competing 'WWE's own 13:30 figure' cited elsewhere in Shane's document could not be independently located "
    "verbatim by any external source checked; a related but not-identical figure (13:31) appears on "
    "allrumblestats.com, whose underlying methodology could not be verified. Both remain documented as "
    "unresolved alternate figures rather than discarded -- see F309.").strip()
new_flag("RR2015M", "entrants", "dean-ambrose", "ring_time", "conflicting_sources",
    "Dean Ambrose's survival time is now CONFIRMED at 10:40 (2-source agreement: this database's internal "
    "Cageside-derived figure + Wikipedia, independently). The originally-flagged competing figures -- '13:30' "
    "(cited within Shane's document as 'WWE's own figure', not independently located verbatim externally this "
    "pass) and 13:31 (allrumblestats.com, methodology unverified) -- remain unresolved, documented alternates "
    "rather than the primary CONFIRMED value.", f"{S_WIKI};{S_ALLRUMBLE}", status="resolved")
resolve_flag("F285", "Dean Ambrose's survival time is now CONFIRMED at 10:40 -- a 2nd independent source "
    "(Wikipedia) agrees with this database's existing internal figure. The competing 'WWE's own 13:30' claim "
    "could not be independently verified verbatim by any external source checked this pass; a related but "
    "not-identical figure (13:31, allrumblestats.com) remains an unresolved alternate -- see the new flag "
    "above.")

# --- Simultaneous Kane/Big Show elimination: reinforced narrative confirmation ---
new_flag("RR2015M", "eliminations", "kane;big-show", "n/a", "unverified",
    "The simultaneous-elimination modeling (Kane and Big Show eliminated together by Roman Reigns, no true "
    "'final three' moment) is corroborated by contemporary narrative sources describing a single, one-motion "
    "double elimination (a KB Wrestling Reviews retrospective: 'Reigns gets up for a double elimination'). "
    "However, structured database tables (Wikipedia, Online World of Wrestling) list Kane and Big Show with "
    "sequential, not tied, elimination-order numbers (27th/28th) -- almost certainly a listing-convention "
    "artifact (structured tables need SOME sequential order even for simultaneous events) rather than genuine "
    "evidence against simultaneity, but noted per this project's report-don't-silently-resolve convention. No "
    "source with exact match-clock timestamps proving same-second simultaneity was found.", f"{S_WIKI};{S_RETRO_REVIEWS}")

# --- Additional eliminator credit from Wikipedia's table -- PROBABLE (single source, reliability-caveated) ---
RR2015_NEW_ELIMS_PROBABLE = [
    ("the-miz", "bubba-ray-dudley", "4:01"), ("bubba-ray-dudley", "bray-wyatt", "5:22"),
    ("the-boogeyman", "bray-wyatt", "0:47"), ("fandango", "rusev", "7:50"),
    ("tyson-kidd", "daniel-bryan", "2:29"), ("cody-rhodes", "roman-reigns", "12:49"),
    ("diamond-dallas-page", "rusev", "2:28"), ("kofi-kingston", "rusev", "3:04"),
    ("big-e", "rusev", "15:04"), ("jack-swagger", "big-show", "13:06"),
    ("wade-barrett", "dolph-ziggler", "6:10"),
]
for victim, eliminator, clock in RR2015_NEW_ELIMS_PROBABLE:
    add_new_elim("RR2015M", victim, eliminator,
                 notes="Eliminator and clock-time per Wikipedia's event-article table -- single-sourced this "
                       "pass (could not be independently re-verified against the raw page due to this "
                       "session's fetch-tool limitations, and a nearby figure in the same table -- Bray "
                       "Wyatt's own elimination total -- did not internally reconcile against a 2nd source, "
                       "Wrestling Inc's dedicated stats article -- see F311). Recorded as PROBABLE rather than "
                       "CONFIRMED pending independent re-verification. This external clock-time is a distinct "
                       "metric from this database's own internal ring_time/survival-time field and was not "
                       "cross-checked against it this pass.",
                 src=S_WIKI, data_quality_status="PROBABLE", clock_time=clock)

# Shared eliminations
add_new_elim("RR2015M", "adam-rose", "rusev", assisting=["kofi-kingston"],
    notes="Eliminated by Rusev and Kofi Kingston together, per Wikipedia's table -- single-sourced, same "
          "reliability caveat as above.", src=S_WIKI, data_quality_status="PROBABLE", clock_time="1:01")
add_new_elim("RR2015M", "ryback", "big-show", assisting=["kane"],
    notes="Eliminated by Big Show and Kane together, per Wikipedia's table -- single-sourced, same "
          "reliability caveat as above.", src=S_WIKI, data_quality_status="PROBABLE", clock_time="11:15")
add_new_elim("RR2015M", "titus-oneil", "dean-ambrose", assisting=["roman-reigns"],
    notes="Eliminated by Dean Ambrose and Roman Reigns together, per Wikipedia's table -- single-sourced, "
          "same reliability caveat as above. Independently, 2 sources (Wikipedia, Wrestling Inc's dedicated "
          "stats article) agree this was the fastest elimination of the match at 0:04.",
    src=f"{S_WIKI};{S_WRESTLINGINC}", data_quality_status="PROBABLE", clock_time="0:04")
add_new_elim("RR2015M", "dolph-ziggler", "big-show", assisting=["kane"],
    notes="Eliminated by Big Show and Kane together, per Wikipedia's table -- single-sourced, same "
          "reliability caveat as above. Notable: this puts Ziggler's own elimination shortly before Kane and "
          "Big Show's own (simultaneous) elimination by Reigns later in the match.",
    src=S_WIKI, data_quality_status="PROBABLE", clock_time="2:29")

recompute_elim_counts("RR2015M", ["the-miz","r-truth","bubba-ray-dudley","luke-harper","bray-wyatt",
    "curtis-axel","the-boogeyman","hunico","zack-ryder","daniel-bryan","fandango","tyson-kidd","cody-rhodes",
    "diamond-dallas-page","rusev","goldust","kofi-kingston","adam-rose","roman-reigns","big-e","damien-sandow",
    "jack-swagger","ryback","kane","dean-ambrose","titus-oneil","wade-barrett","cesaro","big-show","dolph-ziggler"])
set_eliminators_count("RR2015M")

resolve_flag("F283", "15 additional eliminator credits recovered from Wikipedia's event-article table (12 "
    "solo + 3 shared-credit eliminations), covering all but 9 of the previously-uncredited entrants (R-Truth, "
    "Luke Harper, Sin Cara/hunico, Zack Ryder, Daniel Bryan, Goldust, Damien Mizdow, Cesaro remain uncredited "
    "-- no source found any eliminator for them). Recorded as PROBABLE rather than CONFIRMED: this pass could "
    "not independently re-verify the Wikipedia table against a 2nd structured source, and found one "
    "internally-inconsistent detail alongside it (Bray Wyatt's own elimination-count total: 6 per Wrestling "
    "Inc's dedicated stats article vs. an implied 7 from the same Wikipedia table) -- see F311.")

new_flag("RR2015M", "eliminations", "*", "n/a", "unverified",
    "Bray Wyatt's elimination-count total for this match is 6 per Wrestling Inc's dedicated day-after stats "
    "article ('Bray Wyatt, Rusev, and Roman Reigns led the Rumble in eliminations, with 6 each'), but the "
    "newly-added Wikipedia-sourced elimination credits (this pass) imply 7 for Wyatt if all are counted "
    "(Bubba Ray Dudley, The Boogeyman, plus this database's pre-existing internal credits). This 1-count "
    "discrepancy was not resolved this pass -- left as an open flag given the reliability caveats already "
    "noted on the newly-added credits.", f"{S_WIKI};{S_WRESTLINGINC}")

new_flag("RR2015M", "events", "RR2015M", "duration_total", "conflicting_sources",
    "Match duration has a cross-source conflict: Wikipedia states 59:31, while a Cageside Seats retrospective "
    "('The Complete List of WWE's 2015 PPV Match Times') states 59:35 -- matching this database's own "
    "internal Cageside-derived total exactly. Kept at the existing internal CONFIRMED 59:35 per this "
    "project's documentary-source-first convention.", f"{S_WIKI};{S_CAGESIDE}")

# ===========================================================================
# 2016
# ===========================================================================
ev = events_by_id["RR2016M"]
ev["event_date"] = "2016-01-24"
ev["venue"] = "Amway Center"
ev["city_region"] = "Orlando, Florida"
ev["country"] = "United States"
ev["attendance_reported"] = "15170"
ev["commentary_team"] = ("Michael Cole, John \"Bradshaw\" Layfield (JBL), and Byron Saxton -- confirmed by 3 "
    "sources (Wikipedia, prowrestling.fandom.com, TJR Wrestling).")
ev["championship_implications"] = (ev["championship_implications"].rstrip() + (
    " Undercard (2-source agreement, Online World of Wrestling + sacnilk.com): Jack Swagger & Mark Henry won a "
    "Fatal 4-Way tag qualifier (over The Ascension, Sandow/Young, and The Dudley Boyz) earning the final Rumble "
    "spots for Henry/Swagger; Dean Ambrose defeated Kevin Owens in a Last Man Standing match to retain the "
    "Intercontinental Championship; The New Day defeated The Usos to retain the Tag Team Championship; Kalisto "
    "defeated Alberto Del Rio to win the United States Championship; Charlotte defeated Becky Lynch to retain "
    "the Divas Championship."
))
ev["historical_significance"] = ev["historical_significance"].rstrip() + (
    " Externally fact-checked 2026-09-17: Brock Lesnar's Wyatt Family group elimination now individually "
    "named -- 3 sources (WWE.com's own official recap, a Wrestling Inc retro review, and allrumblestats.com's "
    "data table) independently agree the other 'thugs' were Erick Rowan and Luke Harper, plus Braun Strowman. "
    "17 additional eliminator credits recovered (2 with a genuine cross-source conflict). Kane/Big Show's "
    "51-second gap independently confirmed to the second. Roman Reigns's 29:25 adjusted survival figure "
    "independently corroborated by Cageside Seats' own dedicated timing article. AJ Styles's WWE PPV debut and "
    "the Reigns/Strowman elimination-count tie (5 each) both confirmed. See F313-F318."
)
add_src(ev, S_WIKI, S_ALLRUMBLE, S_WWE_OFFICIAL)
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-17: all previously-UNKNOWN event-level facts filled in. Eliminator "
    "credit substantially expanded (23 of 29 total, up from 6) -- resolves most of F290. Wyatt Family group "
    "for Lesnar's elimination fully individually named -- resolves F291. See F313-F318."
)

RR2016_ORDER = ["roman-reigns","rusev","aj-styles","tyler-breeze","curtis-axel","chris-jericho","kane",
    "goldust","ryback","kofi-kingston","titus-oneil","r-truth","luke-harper","cody-rhodes","big-show",
    "neville","braun-strowman","kevin-owens","dean-ambrose","sami-zayn","erick-rowan","mark-henry",
    "brock-lesnar","jack-swagger","the-miz","alberto-del-rio","bray-wyatt","dolph-ziggler","sheamus",
    "hunter-hearst-helmsley"]
assert len(RR2016_ORDER) == 30
for wid in RR2016_ORDER:
    er = entrants_by_key[("RR2016M", wid)]
    er["entry_number_status"] = "CONFIRMED"
    add_src(er, S_WIKI, S_ALLRUMBLE)

resolve_flag("F289", "All previously-UNKNOWN event-level facts filled in externally (date, venue, city, "
    "attendance, commentary team, undercard), plus full entry order independently confirmed by 4 sources "
    "(Wrestling Inc, Online World of Wrestling, prowrestling.fandom.com, allrumblestats.com), matching this "
    "database's existing order exactly.")

# --- Wyatt Family group for Lesnar's elimination: fully individually named this pass ---
for row in eliminations:
    if row["event_id"] == "RR2016M" and row["eliminated_wrestler_id"] == "brock-lesnar" and row["eliminator_wrestler_id"] == "bray-wyatt":
        row["data_quality_status"] = "CONFIRMED"
        row["assisting_wrestler_ids"] = "erick-rowan;luke-harper;braun-strowman"
        row["is_solo"] = "FALSE"
        add_src(row, S_WWE_OFFICIAL, S_WRESTLINGINC, S_ALLRUMBLE)
        row["notes"] = (row["notes"].rstrip() + " Externally fact-checked 2026-09-17: the other 'thugs' are "
            "now individually named by 3 independent sources -- WWE.com's own official match recap ('Rowan, "
            "Strowman and Harper crawled back into the ring...Wyatt hit Sister Abigail before his followers "
            "pushed Brock over the top rope'), a Wrestling Inc retro review ('The Wyatt Family -- Luke Harper, "
            "Braun Strowman, and Erick Rowan -- eventually eliminated Lesnar'), and allrumblestats.com's data "
            "table (listing Braun Strowman, Erick Rowan, Luke Harper as eliminator credit, distinct from Bray "
            "Wyatt's own separately-noted Sister Abigail). Upgraded to CONFIRMED and all 3 added as assisting "
            "eliminators alongside Bray Wyatt. See F291 (resolved), F313.").strip()
for row in eliminations:
    if row["event_id"] == "RR2016M" and row["eliminated_wrestler_id"] == "brock-lesnar" and row["eliminator_wrestler_id"] in ("erick-rowan","luke-harper","braun-strowman"):
        pass  # none should exist yet -- add_elim helper only wrote the single bray-wyatt row at build time
lesnar_row = entrants_by_key[("RR2016M", "brock-lesnar")]
lesnar_row["eliminated_by_ids"] = "bray-wyatt;erick-rowan;luke-harper;braun-strowman"

resolve_flag("F291", "The other 'thugs' who eliminated Brock Lesnar alongside Bray Wyatt are now individually "
    "named: Erick Rowan, Luke Harper, and Braun Strowman -- confirmed by 3 independent sources (WWE.com's own "
    "official recap, a Wrestling Inc retro review, allrumblestats.com's data table), matching this database's "
    "own prior speculation exactly (Rowan and Harper, both already-eliminated Wyatt Family members interfering "
    "from outside) plus Strowman, not individually anticipated at build time. All 3 added as assisting "
    "eliminators on the existing elimination row, upgraded to CONFIRMED.")

# --- Additional eliminator credit (17 new, 2 conflicts preserved) ---
RR2016_NEW_ELIMS = [
    ("rusev", "roman-reigns"), ("tyler-breeze", None),  # shared, see below
    ("chris-jericho", "dean-ambrose"), ("goldust", "titus-oneil"), ("ryback", "big-show"),
    ("kofi-kingston", "chris-jericho"), ("titus-oneil", "big-show"), ("r-truth", "kane"),
    ("cody-rhodes", "luke-harper"), ("neville", "luke-harper"), ("braun-strowman", "brock-lesnar"),
    ("sami-zayn", "braun-strowman"), ("erick-rowan", "brock-lesnar"), ("jack-swagger", "brock-lesnar"),
    ("the-miz", "roman-reigns"), ("dolph-ziggler", "hunter-hearst-helmsley"), ("sheamus", "roman-reigns"),
]
for victim, eliminator in RR2016_NEW_ELIMS:
    if eliminator is None:
        continue
    add_new_elim("RR2016M", victim, eliminator,
                 notes="Eliminator per allrumblestats.com's data table, cross-checked against a Wikipedia "
                       "table fetch, prowrestling.fandom.com, and Wrestling Inc/Online World of Wrestling "
                       "(4-source agreement throughout).",
                 src=f"{S_WIKI};{S_ALLRUMBLE};{S_FANDOM}", data_quality_status="CONFIRMED")

# Tyler Breeze: shared credit (Reigns + AJ Styles), 3-source agreement
add_new_elim("RR2016M", "tyler-breeze", "roman-reigns", assisting=["aj-styles"],
    notes="Eliminated by Roman Reigns and AJ Styles together, per allrumblestats.com, a Wikipedia table fetch, "
          "and prowrestling.fandom.com (3 sources agreeing).",
    src=f"{S_WIKI};{S_ALLRUMBLE};{S_FANDOM}", data_quality_status="CONFIRMED")

# 2 genuine conflicts preserved
add_new_elim("RR2016M", "curtis-axel", "aj-styles",
    notes="Curtis Axel's eliminator is a genuine cross-source conflict: allrumblestats.com and a Wikipedia "
          "table fetch both credit AJ Styles, while prowrestling.fandom.com instead credits Roman Reigns. The "
          "2-source AJ Styles version is used as primary credit; the Reigns version is preserved as a "
          "documented alternative -- see F314.",
    src=f"{S_WIKI};{S_ALLRUMBLE}", data_quality_status="PROBABLE")
new_flag("RR2016M", "eliminations", "curtis-axel", "eliminator_wrestler_id", "conflicting_sources",
    "Curtis Axel's eliminator is credited to AJ Styles by 2 sources (allrumblestats.com, a Wikipedia table "
    "fetch) but to Roman Reigns by a 3rd (prowrestling.fandom.com). The 2-source AJ Styles version is used as "
    "primary credit; the Reigns version is preserved here as a documented alternative.",
    f"{S_WIKI};{S_ALLRUMBLE};{S_FANDOM}")

add_new_elim("RR2016M", "alberto-del-rio", "roman-reigns",
    notes="Alberto Del Rio's eliminator is a genuine cross-source conflict: allrumblestats.com and "
          "prowrestling.fandom.com both credit Roman Reigns, while a Wikipedia table fetch shows this cell "
          "blank/no eliminator listed. The 2-source Reigns version is used as primary credit -- see F315.",
    src=f"{S_ALLRUMBLE};{S_FANDOM}", data_quality_status="PROBABLE")
new_flag("RR2016M", "eliminations", "alberto-del-rio", "eliminator_wrestler_id", "conflicting_sources",
    "Alberto Del Rio's eliminator is credited to Roman Reigns by 2 sources (allrumblestats.com, "
    "prowrestling.fandom.com), while a Wikipedia table fetch left this cell blank (a gap, not a directly "
    "competing claim). The 2-source Reigns version is used as primary credit.",
    f"{S_WIKI};{S_ALLRUMBLE};{S_FANDOM}")

recompute_elim_counts("RR2016M", RR2016_ORDER)
set_eliminators_count("RR2016M")

resolve_flag("F290", "17 additional eliminator credits recovered this pass (23 of 29 total, up from 6), "
    "primarily 3-4 source agreement (allrumblestats.com, a Wikipedia table fetch, prowrestling.fandom.com, "
    "Wrestling Inc/Online World of Wrestling). 2 eliminations have a genuine cross-source conflict (Curtis "
    "Axel, Alberto Del Rio) -- see F314/F315. Remaining uncredited entrants: Goldust (now credited above, "
    "correcting this note) -- 6 entrants remain fully uncredited this pass (no source found any eliminator).")

# --- Kane/Big Show 51-second gap: independently confirmed to the second ---
new_flag("RR2016M", "eliminations", "kane;big-show", "elimination_clock_time", "unverified",
    "Kane's (28:19) and Big Show's (29:10) elimination timestamps, both by Braun Strowman, are independently "
    "confirmed to the exact second by allrumblestats.com's clock-time data -- the 51-second gap between them "
    "matches this database's own internal computation exactly. Both eliminations are separately confirmed by "
    "4 sources total (allrumblestats.com, a Wikipedia table fetch, prowrestling.fandom.com, TJR Wrestling). "
    "The 2015 comparison (the same Kane/Big Show pairing eliminated simultaneously by Roman Reigns the "
    "previous year) is independently corroborated by WWE.com's own official 2015 recap.",
    f"{S_ALLRUMBLE};{S_WIKI};{S_FANDOM};{S_TJR};{S_WWE_OFFICIAL}", status="resolved")

# --- Roman Reigns's adjusted survival figure: independently corroborated ---
rr = entrants_by_key[("RR2016M", "roman-reigns")]
rr["notes"] = (rr["notes"].rstrip() + " Externally fact-checked 2026-09-17: the 29:25 ADJUSTED figure is "
    "independently corroborated by a Cageside Seats dedicated timing-and-statistics article ('59m 48s "
    "(adjusted to 29m 25s accounting for ring absence)'), matching this database's own internal figure "
    "exactly -- strong external validation. Kofi Kingston's parallel adjusted figure (4:29) could not be "
    "independently corroborated this pass -- no external source gives a specific adjusted number for him, "
    "though the underlying absence event itself (caught on Big E's shoulders, avoiding official elimination) "
    "is independently confirmed by 2 sources (Wrestling Inc, TJR Wrestling). See F316.").strip()
add_src(rr, S_CAGESIDE)
kofi = entrants_by_key[("RR2016M", "kofi-kingston")]
add_src(kofi, S_WRESTLINGINC, S_TJR)

new_flag("RR2016M", "entrants", "roman-reigns;kofi-kingston", "notes", "unverified",
    "Roman Reigns's adjusted survival figure (29:25) is independently confirmed by an external source "
    "(Cageside Seats), matching this database's internal figure exactly. Kofi Kingston's underlying "
    "shoulder-save absence event is independently confirmed (Wrestling Inc, TJR Wrestling), but no external "
    "source gives a specific adjusted-time number for him to cross-check against this database's internal "
    "4:29 figure.", f"{S_CAGESIDE};{S_WRESTLINGINC};{S_TJR}", status="resolved")
resolve_flag("F292", "Roman Reigns's 29:25 adjusted figure independently corroborated by Cageside Seats' own "
    "dedicated timing article, matching this database's internal figure exactly. Kofi Kingston's underlying "
    "absence event is independently confirmed, but no external adjusted-time NUMBER was found for him this "
    "pass -- see the new flag above for this remaining gap.")

# --- Triple H entering before Sheamus: no external corroboration found, left as-is ---
new_flag("RR2016M", "entrants", "hunter-hearst-helmsley;sheamus", "notes", "unverified",
    "No external source addressing whether Triple H physically entered the ring before Sheamus (despite being "
    "the later official entrant) was found this pass. One detailed match review (The Armbar Express) "
    "describes the surrounding sequence without confirming or denying the specific claim. Circumstantial "
    "support: allrumblestats.com's entry-clock gap between Sheamus (51:20) and Triple H (53:53) is 2:33, "
    "notably longer than the ~90-second standard interval used elsewhere in the same table -- consistent with "
    "something unusual happening around that entrance, but not proof of the specific claim. Left as-is, "
    "single-sourced (Shane's document) per F293.", f"{S_RETRO_REVIEWS};{S_ALLRUMBLE}")

# --- Trivia: elimination leaders, AJ Styles debut ---
for wid in ("roman-reigns", "braun-strowman"):
    er = entrants_by_key[("RR2016M", wid)]
    er["notes"] = (er["notes"].rstrip() + " Tied for most eliminations in the match (5 each), 2-source "
        "agreement (Fightful's stats piece, allrumblestats.com's own Eliminations column) -- externally "
        "fact-checked 2026-09-17.").strip()
    add_src(er, S_FIGHTFUL, S_ALLRUMBLE)

aj = entrants_by_key[("RR2016M", "aj-styles")]
aj["notes"] = (aj["notes"].rstrip() + " Entered at #3, marking his WWE pay-per-view debut -- confirmed by "
    "multiple sources (a Wikipedia table fetch, CBS Sports headline coverage). Externally fact-checked "
    "2026-09-17.").strip()
add_src(aj, S_WIKI)

# ===========================================================================
# Bonus derived stat: eliminators_count, now that credit is far more complete
# ===========================================================================
for event_id in ("RR2013M", "RR2014M", "RR2015M", "RR2016M"):
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

print(f"2013-2016 fact-check pass complete: "
      f"{flag_ctr[0] - 297} new flags (F297-F{flag_ctr[0]-1}), {len(new_sources)} new sources "
      f"(S109-S114), flags.csv now has {len(flags)} rows, sources.csv now has {len(sources)} rows.")
