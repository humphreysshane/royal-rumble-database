# -*- coding: utf-8 -*-
"""
External fact-check pass for the 1998-2002 Royal Rumbles, mirroring the fact-check
pass already done for 1988-1992 and 1993-1997. Built from 5 parallel research agents'
findings (Wikipedia event articles + wrestler biography articles, thesmackdownhotel.com
Pro Wrestlers Database, Online World of Wrestling, prowrestling.fandom.com,
allrumblestats.com, WWE.com's own official retrospective, Cageside Seats, TJR Wrestling,
Cultaholic, sacnilk.com, wrestlingrecaps.com, KB's Wrestling Reviews, Wrestling DVD
Network, WrestleCrap, Philadelphia Inquirer, Miami New Times, slamwrestling.net,
Enuffa.com, historyofwrestlingblog.wordpress.com, Bleacher Report, and TheSportster.com).

This is a PATCH script, not a build script: it mutates the already-built data/*.csv
files in place (loads, edits in memory, writes back), rather than appending fresh rows
to an empty table. Run against an isolated test copy first, then the live database,
exactly like every build/patch script before it.

Flag IDs continue from F140 (F141 onward). Source IDs continue from S049 (S050 onward).
Wrestler IDs for brand-new people continue the existing convention (slugified ring name).

Cagematch.net was rate-limited (HTTP 429) on essentially every attempt across all 5
research agents, consistent with every prior fact-check pass -- it remains largely
unavailable as a corroborating source and is not relied upon here.
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
flags = load("flags.csv")
sources = load("sources.csv")

EVENTS_FIELDS = list(events[0].keys())
WRESTLERS_FIELDS = list(wrestlers[0].keys())
ENTRANTS_FIELDS = list(entrants[0].keys())
ELIM_FIELDS = list(eliminations[0].keys())
FLAGS_FIELDS = list(flags[0].keys())
SOURCES_FIELDS = list(sources[0].keys())

events_by_id = {e["event_id"]: e for e in events}
wrestlers_by_id = {w["wrestler_id"]: w for w in wrestlers}
entrants_by_key = {(e["event_id"], e["wrestler_id"]): e for e in entrants}

DATE_LOGGED = "2026-09-16"

flag_ctr = [141]
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
            f["description"] = f["description"].rstrip() + " -- RESOLVED by the 1998-2002 fact-check pass: " + resolution_note
            return
    raise KeyError(f"flag {flag_id} not found")


def add_src(row, *src_ids):
    ids = set(filter(None, row["source_ids"].split(";")))
    ids.update(src_ids)
    row["source_ids"] = ";".join(sorted(ids))


# ---------------------------------------------------------------------------
# NEW SOURCES (S050 onward)
# ---------------------------------------------------------------------------
new_sources = [
    ("S050", "Wikipedia (English), Royal Rumble (1998)-(2002) event articles", "reference_site", "",
     10, "Wikipedia/reference sites", DATE_LOGGED,
     "Event-level facts and full entrant/elimination tables for all 5 events. Long ordered tables "
     "required repeated, narrowed re-fetches in several cases to resolve row-alignment/rowspan-cell "
     "issues in the underlying web-fetch tooling -- see individual flags below for where this mattered "
     "and how it was cross-checked against independent secondary databases before being trusted."),
    ("S051", "WWE.com, official Royal Rumble history / retrospective pages", "reputable_publication", "",
     12, "Other reputable site", DATE_LOGGED,
     "wwe.com/shows/royalrumble/history pages -- used chiefly to corroborate Triple H's 2002 entry "
     "number (#22) and Faarooq's (#24)."),
    ("S052", "prowrestling.fandom.com", "wrestling_database", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used for 1999 eliminator-credit cross-checking against thesmackdownhotel.com/PWDB."),
    ("S053", "KB's Wrestling Reviews (kbwrestlingreviews.com)", "reputable_publication", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used for 1998 Skull no-show and Vader-as-final-entrant corroboration."),
    ("S054", "Wrestling DVD Network, 'Throwback Thursday' retrospectives", "reputable_publication", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used for 1998 attendance/buyrate/trivia corroboration."),
    ("S055", "WrestleCrap.com inductions", "reputable_publication", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used for 1999 Mabel/Undertaker abduction-angle detail."),
    ("S056", "Philadelphia Inquirer, 'The Squared Circle' wrestling retrospective blog", "reputable_publication", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used for 1999 Chyna-history-making and Jim Ross-absence trivia."),
    ("S057", "Miami New Times", "reputable_publication", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used for 1999 Gangrel background detail."),
    ("S058", "sacnilk.com results pages", "wrestling_database", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used for 2000 venue/attendance/entry-order cross-checking."),
    ("S059", "wrestlingrecaps.com (Scott Keith-style blow-by-blow recaps)", "reputable_publication", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used for 2000 and 2002 entry-order and narrative corroboration."),
    ("S060", "slamwrestling.net legend profiles", "reputable_publication", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used for Crash Holly birthplace corroboration."),
    ("S061", "Enuffa.com, 'History of WWE Royal Rumble' retrospective series", "reputable_publication", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used for 2002 buy-rate, Triple H return-entrance, and Austin-longevity trivia."),
    ("S062", "historyofwrestlingblog.wordpress.com", "reputable_publication", "",
     13, "Fan blog / lower-tier retrospective", DATE_LOGGED,
     "Used for 2002 Rob Van Dam elimination-sequence detail."),
    ("S063", "Bleacher Report, 'WWE Classic of the Week' retrospectives", "reputable_publication", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used for 2002 Austin/Undertaker elimination-count trivia."),
    ("S064", "TheSportster.com", "reputable_publication", "",
     12, "Other reputable site", DATE_LOGGED,
     "Used for Mr. Perfect's 2002 WWE release date corroboration."),
]
for row in new_sources:
    sources.append(dict(zip(SOURCES_FIELDS, row)))

S_WIKI_EVENT = "S050"
S_WWE_HISTORY = "S051"
S_FANDOM = "S052"
S_KB = "S053"
S_DVDNET = "S054"
S_WRESTLECRAP = "S055"
S_INQUIRER = "S056"
S_MIAMINEWTIMES = "S057"
S_SACNILK = "S058"
S_WRESTLINGRECAPS = "S059"
S_SLAMWRESTLING = "S060"
S_ENUFFA = "S061"
S_HOWBLOG = "S062"
S_BLEACHER = "S063"
S_SPORTSTER = "S064"
S_WIKI_BIO = "S022"   # reused
S_PWDB = "S024"       # reused (thesmackdownhotel.com)
S_OWW = "S025"        # reused (OWW profile pages)
S_CAGESIDE = "S036"   # reused
S_TJR = "S037"        # reused
S_CULTAHOLIC = "S038" # reused
S_ALLRUMBLE = "S040"  # reused
S_OWW2 = "S042"       # reused (OWW event results pages)


def set_bio(wid, real_name=None, dob=None, birthplace=None, status="PROBABLE", extra_note=None, src=S_WIKI_BIO):
    """Fill bio fields on an existing wrestlers.csv row, only where currently blank,
    and only ever upgrading status (never downgrading an existing CONFIRMED)."""
    w = wrestlers_by_id[wid]
    def _set(field_val, status_field, val, st):
        if w[status_field] in ("CONFIRMED",):
            return
        w[field_val] = val
        w[status_field] = st
    if real_name:
        _set("real_name", "real_name_status", real_name, status)
    if dob:
        _set("dob", "dob_status", dob, status)
    if birthplace:
        _set("birthplace", "birthplace_status", birthplace, status)
    if extra_note:
        w["notes"] = (w["notes"].rstrip() + " " + extra_note).strip()
    add_src(w, src)


def add_wrestler(wid, ring_name, real_name="", real_name_status="UNKNOWN", dob="", dob_status="UNKNOWN",
                  deceased_date="", birthplace="", birthplace_status="UNKNOWN", aliases="", notes="", src=""):
    row = {f: "" for f in WRESTLERS_FIELDS}
    row.update({
        "wrestler_id": wid, "ring_name": ring_name, "real_name": real_name,
        "real_name_status": real_name_status, "gender": "M", "dob": dob, "dob_status": dob_status,
        "deceased_date": deceased_date, "birthplace": birthplace, "birthplace_status": birthplace_status,
        "nationality": "", "debut_year_company": "", "hall_of_fame_year": "",
        "aliases_ring_names": aliases, "wrestling_style": "", "notes": notes, "source_ids": src,
    })
    wrestlers.append(row)
    wrestlers_by_id[wid] = row
    return row


def add_entrant(event_id, wid, entry_number, ring_time, eliminated_by="", notes="", src="", entry_status="CONFIRMED"):
    row = {f: "" for f in ENTRANTS_FIELDS}
    m, s = (ring_time.split(":") if ring_time else ("0", "0"))
    row.update({
        "event_id": event_id, "wrestler_id": wid, "match_id": event_id,
        "entry_number": str(entry_number), "entry_number_status": entry_status,
        "ring_name_at_time": wrestlers_by_id[wid]["ring_name"], "name_displayed_at_event": wrestlers_by_id[wid]["ring_name"],
        "ring_time": ring_time, "ring_time_seconds": str(int(m) * 60 + int(s)),
        "ring_time_status": "CONFIRMED" if ring_time == "00:00" else "PROBABLE",
        "eliminated_by_ids": eliminated_by,
        "wrestlers_eliminated_count": "0", "solo_eliminations_count": "0", "assisted_eliminations_count": "0",
        "self_eliminated": "FALSE", "is_winner": "FALSE", "is_runner_up": "FALSE", "is_final_two": "FALSE",
        "is_final_three": "FALSE", "is_final_four": "FALSE", "surprise_entrant": "FALSE",
        "legend_returning": "FALSE", "celebrity_entrant": "FALSE", "non_full_time_wrestler": "FALSE",
        "wrestled_earlier_on_card": "FALSE", "was_hof_member_at_time": "FALSE",
        "data_quality_status": "PROBABLE", "source_ids": src, "notes": notes,
    })
    entrants.append(row)
    entrants_by_key[(event_id, wid)] = row
    return row


def add_elim(event_id, eliminated_wid, eliminator_wid, assisting=None, is_shared=False, notes="", src=""):
    row = {f: "" for f in ELIM_FIELDS}
    assisting = assisting or []
    row.update({
        "event_id": event_id, "eliminated_wrestler_id": eliminated_wid, "eliminator_wrestler_id": eliminator_wid,
        "assisting_wrestler_ids": ";".join(assisting), "elimination_type": "over_the_top_rope",
        "location_status": "UNKNOWN", "is_solo": "FALSE" if (is_shared or assisting) else "TRUE",
        "is_shared": "TRUE" if (is_shared or assisting) else "FALSE",
        "is_accidental": "FALSE", "is_self_elimination": "FALSE", "is_storyline_related": "FALSE",
        "was_already_incapacitated": "FALSE", "is_disputed": "FALSE",
        "data_quality_status": "PROBABLE", "source_ids": src, "notes": notes,
    })
    eliminations.append(row)
    return row


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


# ===========================================================================
# 1998
# ===========================================================================
ev = events_by_id["RR1998M"]
ev["attendance_reported"] = "18542"
ev["ring_announcer"] = "Howard Finkel"
ev["referees"] = "Mike Chioda, Jack Doan, Jim Korderas, Earl Hebner, Tim White (per S050, single-sourced)"
ev["historical_significance"] = ev["historical_significance"].rstrip() + (
    " Steve Austin recorded 7 eliminations, the most of the match (Marc Mero, Thrasher, Kama Mustafa, 8-Ball, "
    "Savio Vega, Chainz, and The Rock) -- per S054. This was the 3rd time a wrestler won the Rumble in "
    "consecutive years (after Hogan 1990-91 and Michaels 1995-96) -- per S050/S054. S054 also claims this "
    "Rumble featured 17 first-time participants, the most since 1989 (single-sourced, not independently "
    "cross-checked)."
)
add_src(ev, S_WIKI_EVENT, S_KB, S_DVDNET)
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-16: attendance CONFIRMED at 18,542 (matches S043 exactly, corroborated "
    "by S050/S054). The full 1-30 entry order, ring times, and eliminator credit were recovered from Wikipedia "
    "(S050), independently matched by thesmackdownhotel.com/PWDB -- resolving F112. The 'Brian Lee' entrant "
    "was found to be a build-time duplication error (Brian Lee Harris is Chainz's real name, not a separate "
    "entrant); corrected to reflect the true #29 (Chainz) and #30 (Vader, previously entirely missing from "
    "this event). Skull (Don Harris) was added as an advertised-but-no-show entrant at #22. Dude Love's "
    "eliminator was corrected from Steve Austin to Faarooq. See F141-F151."
)

# --- Brian Lee / Chainz / Skull correction -------------------------------------------------
# "Brian Lee" (wrestler_id "brian-lee") was a build-time duplication error: Brian Lee Harris is
# the REAL NAME of the wrestler who competed as "Chainz" at this event (both Wikipedia and
# thesmackdownhotel.com/PWDB list only "Chainz" at #29 -- no separate "Brian Lee" entrant exists
# in either source). The wrestler_id is RETAINED for audit-trail purposes but its RR1998M
# entrant/elimination rows are removed; #30 was actually Vader (not in the DB at all until now).
wrestlers_by_id["brian-lee"]["notes"] = (
    "BUILD ERROR, corrected by the 1998-2002 fact-check pass: this wrestler_id was created from a misreading "
    "of S043's narrative mention of 'Brian Lee of DOA.' External research (S050, corroborated by S024) "
    "confirms Brian Lee Harris is the REAL NAME of the performer who competed as 'Chainz' (wrestler_id "
    "'chainz') at this event -- there was no separate 'Brian Lee' entrant. This wrestler_id's RR1998M "
    "entrant/elimination rows have been removed; Brian Lee Harris's bio data is now recorded on 'chainz'. "
    "Retained here only for audit-trail purposes -- do not use for any entrant/elimination record. See F115 "
    "(resolved)."
)
entrants[:] = [e for e in entrants if not (e["event_id"] == "RR1998M" and e["wrestler_id"] == "brian-lee")]
eliminations[:] = [e for e in eliminations if not (e["event_id"] == "RR1998M" and e["eliminated_wrestler_id"] == "brian-lee")]
entrants_by_key.pop(("RR1998M", "brian-lee"), None)

set_bio("chainz", real_name="Brian Lee Harris", dob="1966-11-26", birthplace="St. Petersburg, Florida, U.S.",
        status="PROBABLE", src=S_PWDB,
        extra_note="Real name/DOB/birthplace corroborated by 2 independent sources (Wikipedia + thesmackdownhotel.com, "
                    "identical on all 3 fields). Ring name 'Chainz'; real name Brian Lee Harris was previously "
                    "mistaken for a separate entrant -- see F115 (resolved).")
wrestlers_by_id["chainz"]["aliases_ring_names"] = (wrestlers_by_id["chainz"]["aliases_ring_names"] + "; Brian Lee").strip("; ")
add_src(wrestlers_by_id["chainz"], S_WIKI_BIO)

set_bio("eight-ball", real_name="Ronald Harris", birthplace="Apopka, Florida, U.S.", status="PROBABLE", src=S_PWDB,
        extra_note="DOB is a genuine 1-year conflict between sources (Wikipedia's 'Harris Brothers' article gives "
                    "1961-10-23, thesmackdownhotel.com gives 1960-10-23; day/month agree) -- left UNKNOWN in the "
                    "structured dob field rather than guessing; see F142.")
add_src(wrestlers_by_id["eight-ball"], S_WIKI_BIO)

add_wrestler("skull", "Skull", real_name="Donald Harris", real_name_status="PROBABLE",
             birthplace="Apopka, Florida, U.S.", birthplace_status="PROBABLE",
             aliases="Don Harris; Jacob Blu; Patrick",
             notes="Twin brother of Eight-Ball (Ron Harris). Advertised for entry #22 at this event but never "
                   "physically entered the match -- per S050, 'attacked by Los Boricuas prior to the Royal "
                   "Rumble match when they mistook him for Stone Cold Steve Austin,' independently corroborated "
                   "by S053. Same DOB-year conflict as his twin -- see F142.",
             src=f"{S_WIKI_BIO};{S_PWDB}")

# --- Full 1-30 entry order, ring time, eliminator (Wikipedia + thesmackdownhotel.com agree) ---
# (entry_number, wrestler_id, [eliminator_ids] or None=winner or "NOSHOW", ring_time)
RR1998_ORDER = [
    (1, "cactus-jack", ["terry-funk"], "9:21"),
    (2, "terry-funk", ["mankind"], "25:19"),
    (3, "tom-brandi", ["cactus-jack", "terry-funk"], "0:12"),
    (4, "rocky-maivia", ["steve-austin"], "51:32"),
    (5, "mosh", ["kurrgan"], "13:09"),
    (6, "phineas-godwinn", ["mark-henry"], "28:48"),
    (7, "eight-ball", ["steve-austin"], "30:43"),
    (8, "bradshaw", ["dude-love"], "35:45"),
    (9, "owen-hart", ["hunter-hearst-helmsley", "chyna"], "2:00"),
    (10, "steve-blackman", ["kurrgan"], "5:58"),
    (11, "d-lo-brown", ["faarooq"], "32:21"),
    (12, "kurrgan", ["eight-ball", "bradshaw", "ken-shamrock", "terry-funk", "phineas-godwinn", "rocky-maivia"], "3:38"),
    (13, "marc-mero", ["steve-austin"], "19:38"),
    (14, "ken-shamrock", ["rocky-maivia"], "9:15"),
    (15, "thrasher", ["steve-austin"], "28:08"),
    (16, "mankind", ["goldust"], "2:07"),
    (17, "goldust", ["chainz"], "26:01"),
    (18, "jeff-jarrett", ["owen-hart"], "1:05"),
    (19, "the-honky-tonk-man", ["vader"], "19:55"),
    (20, "ahmed-johnson", ["d-lo-brown", "mark-henry"], "3:18"),
    (21, "mark-henry", ["faarooq"], "19:07"),
    (22, "skull", "NOSHOW", "0:00"),
    (23, "kama", ["steve-austin"], "13:58"),
    (24, "steve-austin", None, "15:58"),  # WINNER
    (25, "henry-godwinn", ["dude-love"], "11:32"),
    (26, "savio-vega", ["steve-austin"], "9:29"),
    (27, "faarooq", ["rocky-maivia"], "10:03"),
    (28, "dude-love", ["faarooq"], "7:53"),
    (29, "chainz", ["steve-austin"], "4:56"),
    (30, "vader", ["goldust"], "2:15"),
]
GROUP_ROWS_1998 = {3, 9, 12, 20}
ALREADY_HAD_ELIM = {
    ("cactus-jack", "terry-funk"), ("terry-funk", "mankind"), ("rocky-maivia", "steve-austin"),
    ("mankind", "goldust"), ("marc-mero", "steve-austin"), ("thrasher", "steve-austin"),
    ("savio-vega", "steve-austin"),
}

for entry_num, wid, elims, ring_time in RR1998_ORDER:
    if wid == "skull":
        add_entrant("RR1998M", "skull", entry_num, "0:00",
                     notes="Advertised for this slot but never entered -- attacked by Los Boricuas prior to the "
                           "match, mistaken for Steve Austin. See F141 (resolved).",
                     src=f"{S_WIKI_EVENT};{S_KB}")
        continue
    if wid == "vader" and ("RR1998M", "vader") not in entrants_by_key:
        add_entrant("RR1998M", "vader", entry_num, ring_time,
                     notes="Previously entirely missing from this event -- the true #30 entrant (the database "
                           "had erroneously modeled this slot as 'Brian Lee'). See F141 (resolved).",
                     src=f"{S_WIKI_EVENT};{S_PWDB};{S_KB}")
    er = entrants_by_key[("RR1998M", wid)]
    er["entry_number"] = str(entry_num)
    er["entry_number_status"] = "CONFIRMED"
    m, s = ring_time.split(":")
    er["ring_time"] = ring_time
    er["ring_time_seconds"] = str(int(m) * 60 + int(s))
    er["ring_time_status"] = "PROBABLE"
    er["data_quality_status"] = "PROBABLE"
    add_src(er, S_WIKI_EVENT, S_PWDB)
    if elims is None:
        er["is_winner"] = "TRUE"
        continue
    is_group = entry_num in GROUP_ROWS_1998
    er["eliminated_by_ids"] = ";".join(elims)
    if wid == "dude-love":
        # correct the existing row's eliminator instead of adding a duplicate
        for row in eliminations:
            if row["event_id"] == "RR1998M" and row["eliminated_wrestler_id"] == "dude-love":
                row["eliminator_wrestler_id"] = "faarooq"
                row["notes"] = (row["notes"].rstrip() + " CORRECTED 2026-09-16: was credited to Steve Austin in "
                                "the build phase; S050/S024 both independently credit Faarooq. See F143 (resolved).").strip()
                row["data_quality_status"] = "PROBABLE"
                add_src(row, S_WIKI_EVENT, S_PWDB)
        continue
    if wid == "owen-hart":
        # add Chyna as a second, joint assisting eliminator alongside the already-recorded Triple H
        for row in eliminations:
            if row["event_id"] == "RR1998M" and row["eliminated_wrestler_id"] == "owen-hart":
                row["assisting_wrestler_ids"] = "chyna"
                row["is_shared"] = "TRUE"
                row["notes"] = (row["notes"].rstrip() + " S050 credits this jointly to Triple H and Chyna -- "
                                "neither was an official entrant in this match; both are credited as ringside "
                                "interference, consistent with F113's existing framing for Triple H. See F144.").strip()
                add_src(row, S_WIKI_EVENT)
        continue
    if (wid, elims[0]) in ALREADY_HAD_ELIM and len(elims) == 1:
        continue  # unchanged, already correct
    sim_group = f"1998_{wid}" if is_group else ""
    for e_wid in elims:
        add_elim("RR1998M", wid, e_wid, assisting=[x for x in elims if x != e_wid] if is_group else None,
                  is_shared=is_group,
                  notes=f"Entry order/eliminator recovered from S050, independently matched by S024. "
                        f"{'Group elimination -- ' + ', '.join(elims) + '.' if is_group else ''}".strip(),
                  src=f"{S_WIKI_EVENT};{S_PWDB}")

recompute_elim_counts("RR1998M", [wid for _, wid, _, _ in RR1998_ORDER if wid != "skull"])

new_flag("RR1998M", "wrestlers", "brian-lee;chainz;skull;vader", "wrestler_id;entry_number", "unverified",
    "F115's puzzle resolved: 'Brian Lee' was a build-time duplication error -- Brian Lee Harris is Chainz's "
    "real name (2 independent sources: Wikipedia + thesmackdownhotel.com/PWDB), not a separate entrant. The "
    "true #30 entrant was Vader (previously missing from this event entirely), confirmed by the same 2 "
    "sources plus S053. Skull (Don Harris, 8-Ball's twin) was added as the true advertised-but-no-show at "
    "#22, per S050 (corroborated by S053): attacked by Los Boricuas before the match, mistaking him for "
    "Steve Austin.", f"{S_WIKI_EVENT};{S_PWDB};{S_KB}", status="resolved")

new_flag("RR1998M", "wrestlers", "eight-ball;skull", "dob", "conflicting_sources",
    "The Harris twins' (Eight-Ball/Ron and Skull/Don) birth year is a genuine 1-source-vs-1-source conflict: "
    "Wikipedia's 'Harris Brothers' article gives 1961-10-23 for both; thesmackdownhotel.com/PWDB gives "
    "1960-10-23 for both. Month/day agree exactly. Left UNKNOWN in the structured dob field rather than "
    "silently picking one.", f"{S_WIKI_BIO};{S_PWDB}")

new_flag("RR1998M", "eliminations", "dude-love", "eliminator_wrestler_id", "unverified",
    "The build phase (from S043's narrative) credited Dude Love's elimination to Steve Austin. External "
    "research found 2 independent sources (Wikipedia + thesmackdownhotel.com/PWDB) both instead credit "
    "Faarooq, at 7:53. Corrected in favor of the 2-source external agreement.", f"{S_WIKI_EVENT};{S_PWDB}",
    status="resolved")

new_flag("RR1998M", "eliminations", "owen-hart", "assisting_wrestler_ids", "unverified",
    "S050 credits Owen Hart's elimination jointly to Triple H AND Chyna -- Chyna added as a second assisting "
    "eliminator alongside the already-recorded Triple H. Neither Triple H nor Chyna was an official entrant "
    "in this match; both are credited via ringside interference, consistent with F113's existing framing "
    "(Triple H, injured, did not take his own entry but showed up on crutches to eliminate Owen Hart).",
    S_WIKI_EVENT)

new_flag("RR1998M", "eliminations", "kurrgan", "eliminator_wrestler_id", "unverified",
    "Kurrgan's elimination (entry #12, 3:38) is credited to an unusually large 6-way group per S050: 8-Ball, "
    "Bradshaw, Ken Shamrock, Chainsaw Charlie (Terry Funk), Phineas I. Godwinn, and The Rock. Modeled as a "
    "single shared/group elimination per DEFINITIONS.md's convention.", S_WIKI_EVENT)

new_flag("RR1998M", "events", "RR1998M", "notes", "unverified",
    "S054 (Wrestling DVD Network retrospective) claims referee Jack Doan was inadvertently kicked by Phineas "
    "I. Godwinn during an elimination and suffered a concussion -- this was surfaced only via an AI-summarized "
    "fetch and could not be independently re-verified against the literal Wikipedia article text in this "
    "pass. Treated as PLAUSIBLE, not added as confirmed fact.", S_DVDNET)

new_flag("RR1998M", "entrants", "rocky-maivia", "ring_time", "unverified",
    "The Rock's elimination time (his run from entry #4 to being eliminated by Austin) is given as 51:32 by "
    "Wikipedia's own entrant table but 51:27 by S054 (Wrestling DVD Network) -- a minor 5-second discrepancy "
    "between two sources describing the same 'Iron Man of the match' figure. Wikipedia's 51:32 is used "
    "(matches the entrant table used for the rest of this event's timing), difference noted rather than "
    "silently resolved.", f"{S_WIKI_EVENT};{S_DVDNET}")

for wid, real_name, dob, birthplace in [
    ("steve-blackman", None, "1963-09-28", "Annville, Pennsylvania, U.S."),
    ("bradshaw", "John Charles Layfield", "1966-11-29", "Sweetwater, Texas, U.S."),
    ("tom-brandi", "Thomas Brandi", "1966-07-09", "Philadelphia, Pennsylvania, U.S."),
    ("d-lo-brown", "Accie Julius Connor", "1973-10-22", "Burlington, New Jersey, U.S."),
    ("mark-henry", "Mark Jerrold Henry", "1971-06-12", "Silsbee, Texas, U.S."),
    ("kurrgan", "Robert Maillet", "1969-10-26", "Georgetown, Ontario, Canada"),
    ("mosh", "Chaz Warrington", "1971-05-28", "Cherry Hill, New Jersey, U.S."),
    ("ken-shamrock", "Kenneth Wayne Kilpatrick", "1964-02-11", "Warner Robins, Georgia, U.S."),
    ("thrasher", "Glenn Ruth", "1969-06-13", "Camden, New Jersey, U.S."),
    ("phineas-godwinn", "Dennis Knight", "1968-12-26", "Clearwater, Florida, U.S."),
    ("ahmed-johnson", "Anthony Norris", "1963-06-06", "Kokomo, Indiana, U.S."),
]:
    set_bio(wid, real_name, dob, birthplace, status="PROBABLE", src=S_WIKI_BIO)
# Faarooq's real name (Ron Simmons) was already CONFIRMED from an earlier year -- just add DOB/birthplace.
set_bio("faarooq", dob="1958-05-15", birthplace="Perry, Georgia, U.S.", status="PROBABLE", src=S_WIKI_BIO)

new_flag("RR1998M", "wrestlers", "*", "real_name;dob;birthplace", "unverified",
    "Bio data added for 12 previously-unseen wrestlers this pass (Steve Blackman, Bradshaw, Tom Brandi, D-Lo "
    "Brown, Mark Henry, Kurrgan, Mosh, Ken Shamrock, Thrasher, Phineas Godwinn/Mideon, Ahmed Johnson, plus "
    "DOB/birthplace for the already-named Faarooq), single-sourced to Wikipedia in this pass (PROBABLE, not "
    "CONFIRMED -- a second-source cross-check via thesmackdownhotel.com was not completed for these due to "
    "time/scope).", S_WIKI_BIO, status="resolved")

resolve_flag("F112", "The full 1-30 entry order, ring times, and eliminator credit were recovered from "
    "Wikipedia's Royal Rumble (1998) structured table, independently matched exactly by thesmackdownhotel.com/"
    "PWDB's own entrant table -- transforming this event from 6 of 30 known entry numbers to all 30.")
resolve_flag("F114", "S050 and S024 both independently confirm Steve Austin eliminated BOTH DOA members over "
    "the course of the match -- 8-Ball (entry #7) at 30:43, and Chainz (entry #29) later at 4:56 -- not just "
    "one of them as the internal S043 narrative implied.")
# ===========================================================================
# 1999
# ===========================================================================
ev = events_by_id["RR1999M"]
ev["attendance_reported"] = "14816"
ev["referees"] = "Mike Chioda, Earl Hebner, Jim Korderas, Theodore Long, Tim White (per S050, single-sourced)"
ev["historical_significance"] = ev["historical_significance"].rstrip() + (
    " Chyna (entry #30) became the first woman to compete in a men's Royal Rumble match, and the first woman "
    "to record an official Royal Rumble elimination (Mark Henry) -- per S050/S056; she remained the only "
    "woman entrant until 2010. Kane (entry #18) is the only wrestler in Royal Rumble history credited with "
    "eliminating HIMSELF (walked out of the ring unprompted, chasing storyline 'orderlies' during his "
    "contemporaneous psychological-instability angle) -- per S050/S037."
)
add_src(ev, S_WIKI_EVENT, S_INQUIRER, S_TJR)
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-16: attendance CONFIRMED at 14,816 (matches S045 exactly). Eliminator "
    "credit was recovered for 22 of the 29 eliminations that previously had none (Wikipedia + thesmackdownhotel."
    "com/PWDB + prowrestling.fandom.com, 2-3 sources agreeing throughout). Jeff Jarrett's eliminator was "
    "corrected from Steve Austin to Triple H (3-source agreement). X-Pac was merged into the existing "
    "'1-2-3-kid' wrestler_id (2 independent sources explicitly confirm same performer, Sean Waltman). Mabel's "
    "elimination was re-modeled as a 3-way group elimination (Mideon/Phineas Godwinn, Bradshaw, Faarooq) "
    "rather than a sole Undertaker credit -- Undertaker was the storyline mastermind of the 'Ministry' "
    "abduction angle, not the physical/credited eliminator. See F152-F160."
)

# --- X-Pac / 1-2-3 Kid identity merge (2 independent sources: Wikipedia + thesmackdownhotel.com/PWDB) ---
for ev_id in ("RR1999M", "RR2000M"):
    key = (ev_id, "x-pac")
    if key in entrants_by_key:
        er = entrants_by_key.pop(key)
        er["wrestler_id"] = "1-2-3-kid"
        entrants_by_key[(ev_id, "1-2-3-kid")] = er
for row in eliminations:
    if row["eliminated_wrestler_id"] == "x-pac":
        row["eliminated_wrestler_id"] = "1-2-3-kid"
    if row["eliminator_wrestler_id"] == "x-pac":
        row["eliminator_wrestler_id"] = "1-2-3-kid"
    row["assisting_wrestler_ids"] = ";".join(
        "1-2-3-kid" if a == "x-pac" else a for a in row["assisting_wrestler_ids"].split(";") if a)

kid = wrestlers_by_id["1-2-3-kid"]
kid["aliases_ring_names"] = "; ".join(filter(None, [kid["aliases_ring_names"], "X-Pac", "Syxx", "Syxx-Pac", "6-Pac"]))
kid["notes"] = (kid["notes"].rstrip() + " Identity-merged with this database's former 'x-pac' wrestler_id "
                "(RR1999M/RR2000M entrant) by the 1998-2002 fact-check pass -- 2 independent sources (Wikipedia's "
                "'Sean Waltman' infobox and thesmackdownhotel.com/PWDB's career-timeline profile) both explicitly "
                "list '1-2-3 Kid' and 'X-Pac' as ring names of the same performer, Sean Michael Waltman. See F118 "
                "(resolved).").strip()
add_src(kid, S_WIKI_BIO, S_PWDB)
wrestlers_by_id["x-pac"]["notes"] = (
    "MERGED into 'the '1-2-3-kid' wrestler_id by the 1998-2002 fact-check pass -- 2 independent sources "
    "(Wikipedia + thesmackdownhotel.com/PWDB) confirm X-Pac and 1-2-3 Kid are the same performer, Sean Waltman. "
    "This wrestler_id's RR1999M/RR2000M entrant/elimination rows have been redirected to '1-2-3-kid'. Retained "
    "here only for audit-trail purposes -- do not use for any entrant/elimination record. See F118 (resolved)."
)
resolve_flag("F118", "2 independent sources (Wikipedia's 'Sean Waltman' infobox, listing both '1-2-3 Kid' and "
    "'X-Pac' as ring names of the same performer; thesmackdownhotel.com/PWDB's career-timeline profile, "
    "explicitly sequencing '1-2-3 Kid' May 1993-Sep 1996 then 'X-Pac' from Apr 1998) confirm the identity. "
    "Merged into wrestler_id '1-2-3-kid' per the project's 2-source rule.")

# --- Jeff Jarrett eliminator correction (Austin -> Triple H, 3-source agreement) ---
for row in eliminations:
    if row["event_id"] == "RR1999M" and row["eliminated_wrestler_id"] == "jeff-jarrett":
        row["eliminator_wrestler_id"] = "hunter-hearst-helmsley"
        row["notes"] = (row["notes"].rstrip() + " CORRECTED 2026-09-16: was credited to Steve Austin; 3 "
                        "independent sources (Wikipedia, thesmackdownhotel.com/PWDB, prowrestling.fandom.com) "
                        "unanimously credit Triple H, with a matching elimination time (~3:38-3:39). See F153 "
                        "(resolved).").strip()
        add_src(row, S_WIKI_EVENT, S_PWDB, S_FANDOM)
resolve_flag("F119", "22 of the 25 previously-uncredited eliminations recovered from 2-3 independently-agreeing "
    "sources (Wikipedia, thesmackdownhotel.com/PWDB, prowrestling.fandom.com). Jeff Jarrett's eliminator "
    "additionally corrected from Steve Austin to Triple H (see dedicated note). Only Kane's self-elimination "
    "and the already-known 7 remain without a conventional single named opposing eliminator.")

# --- New eliminator credits (2-3 source agreement: Wikipedia + thesmackdownhotel.com/PWDB + prowrestling.fandom.com) ---
RR1999_NEW_ELIMS = [
    ("golga", ["steve-austin"]),
    ("droz", ["mabel"]),
    ("edge", ["mabel"]),
    ("gillberg", ["edge"]),
    ("steve-blackman", ["mabel"]),
    ("dan-severn", ["mabel"]),
    ("tiger-ali-singh", ["mabel"]),
    ("blue-meanie", ["mabel"]),
    ("jesse-james", ["kane"]),
    ("gangrel", ["jesse-james"]),
    ("kurrgan", ["kane"]),
    ("al-snow", ["jesse-james"]),
    ("goldust", ["kane"]),
    ("the-godfather", ["kane"]),
    ("ken-shamrock", ["steve-austin"]),
    ("billy-gunn", ["steve-austin"]),
    ("test", ["steve-austin"]),
    ("val-venis", ["hunter-hearst-helmsley"]),
    ("1-2-3-kid", ["big-boss-man"]),  # X-Pac, already merged into 1-2-3-kid above
    ("d-lo-brown", ["big-boss-man"]),
    ("chyna", ["steve-austin"]),
]
for eliminated_wid, elims in RR1999_NEW_ELIMS:
    add_elim("RR1999M", eliminated_wid, elims[0],
             notes="Eliminator recovered from S050, cross-checked by S024/S052.",
             src=f"{S_WIKI_EVENT};{S_PWDB};{S_FANDOM}")
    entrants_by_key[("RR1999M", eliminated_wid)]["eliminated_by_ids"] = elims[0]

# --- Kane's self-elimination (walked out of the ring during a storyline "orderlies" chase) ---
add_elim("RR1999M", "kane", "kane",
         notes="Self-elimination -- per S050/S037, Kane 'threw the coat over the rope and then walked out of "
               "the ring' unprompted, chasing storyline 'orderlies/handlers' during his contemporaneous "
               "psychological-instability angle. Not a conventional in-ring finish; modeled as eliminator=self "
               "per the same convention already used for Drew Carey's 2001 self-elimination.",
         src=f"{S_WIKI_EVENT};{S_TJR}")
entrants_by_key[("RR1999M", "kane")]["eliminated_by_ids"] = "kane"
entrants_by_key[("RR1999M", "kane")]["self_eliminated"] = "TRUE"

# --- Mabel's elimination re-modeled as a 3-way group (Mideon/Phineas Godwinn, Bradshaw, Faarooq) ---
# Undertaker was the storyline mastermind of the "Ministry" abduction angle but is NOT the physical/credited
# eliminator per 3 independent sources (Wikipedia, TJR Wrestling, WrestleCrap all name the trio as the
# literal eliminators of record).
for row in eliminations:
    if row["event_id"] == "RR1999M" and row["eliminated_wrestler_id"] == "mabel":
        row["eliminator_wrestler_id"] = "phineas-godwinn"
        row["assisting_wrestler_ids"] = "bradshaw;faarooq"
        row["is_shared"] = "TRUE"
        row["is_solo"] = "FALSE"
        row["is_storyline_related"] = "TRUE"
        row["simultaneous_group_id"] = "1999_mabel"
        row["notes"] = ("CORRECTED 2026-09-16: was credited solely to The Undertaker. 3 independent sources "
                         "(S050, S037, S055) agree the physical/credited eliminators of record were Mideon "
                         "(this DB's 'phineas-godwinn' wrestler_id, a later ring name of the same performer, "
                         "Dennis Knight), Bradshaw, and Faarooq -- acting on The Undertaker's orders as part "
                         "of his 'Ministry of Darkness' abduction storyline. Undertaker appeared at ringside "
                         "and was the storyline architect but is not the credited in-ring eliminator. None of "
                         "the three were official entrants in this match -- credited via ringside interference, "
                         "consistent with F113/F144's precedent. See F154 (resolved).").strip()
        add_src(row, S_WIKI_EVENT, S_TJR, S_WRESTLECRAP)
for e_wid in ("bradshaw", "faarooq"):
    add_elim("RR1999M", "mabel", e_wid, assisting=[x for x in ("phineas-godwinn", "bradshaw", "faarooq") if x != e_wid],
              is_shared=True,
              notes="Ministry of Darkness abduction angle -- see the Mideon/phineas-godwinn row for full detail.",
              src=f"{S_WIKI_EVENT};{S_TJR};{S_WRESTLECRAP}")
entrants_by_key[("RR1999M", "mabel")]["eliminated_by_ids"] = "phineas-godwinn;bradshaw;faarooq"
wrestlers_by_id["phineas-godwinn"]["aliases_ring_names"] = (
    wrestlers_by_id["phineas-godwinn"]["aliases_ring_names"] + "; Mideon").strip("; ")
wrestlers_by_id["phineas-godwinn"]["notes"] = (wrestlers_by_id["phineas-godwinn"]["notes"].rstrip() +
    " By January 1999 this performer (Dennis Knight) had moved on to the 'Mideon' gimmick as a member of The "
    "Undertaker's Ministry of Darkness -- credited under 'phineas-godwinn' here only because that is this "
    "database's existing wrestler_id for him (reused per the project's identity-consistency rule); he was not "
    "an official RR1999M entrant, only a ringside interferer. See F154.").strip()

new_flag("RR1999M", "eliminations", "mabel", "eliminator_wrestler_id", "needs_human_judgement",
    "Mabel's elimination (the 'lights out' Ministry abduction spot) was originally credited solely to The "
    "Undertaker per the internal S044 buzzer document. 3 independent external sources (Wikipedia, TJR "
    "Wrestling, WrestleCrap) instead name Mideon (Dennis Knight, this database's 'phineas-godwinn' wrestler_id), "
    "Bradshaw, and Faarooq as the physical/credited eliminators, with Undertaker as the off-screen storyline "
    "architect who does not himself perform the in-ring elimination. Re-modeled as a 3-way group elimination.",
    f"{S_WIKI_EVENT};{S_TJR};{S_WRESTLECRAP}", status="resolved")

recompute_elim_counts("RR1999M", [e["wrestler_id"] for e in entrants if e["event_id"] == "RR1999M"])

for wid, real_name, dob, birthplace in [
    ("golga", None, None, None),  # real name (John Tenta) already CONFIRMED from an earlier year; nothing new to add
    ("droz", "Darren Alexander Drozdov", "1969-04-07", "Mays Landing, Hamilton Township, New Jersey, U.S."),
    ("edge", "Adam Joseph Copeland", "1973-10-30", "Orangeville, Ontario, Canada"),
    ("gillberg", "Duane Gill", "1959-07-10", "Glen Burnie, Maryland, U.S."),
    ("dan-severn", "Daniel DeWayne Severn", "1958-06-08", "Coldwater, Michigan, U.S."),
    ("tiger-ali-singh", "Gurjit Singh Hans", "1971-03-09", "Toronto, Ontario, Canada"),
    ("blue-meanie", "Brian Heffron", "1973-05-18", "Philadelphia, Pennsylvania, U.S."),
    ("gangrel", "David William Heath", "1969-02-16", None),
    ("al-snow", "Allen Ray Sarven", "1963-07-18", "Lima, Ohio, U.S."),
    ("the-godfather", "Charles Wright", "1961-05-16", "Las Vegas, Nevada, U.S."),
    ("kane", "Glenn Thomas Jacobs", "1967-04-26", "Torrejon de Ardoz, Spain"),
    ("test", "Andrew James Robert Patrick Martin", "1975-03-17", "Whitby, Ontario, Canada"),
    ("big-boss-man", None, None, "Marietta, Georgia, U.S."),  # real name already CONFIRMED; birthplace refinement only
    ("val-venis", "Sean Allen Morley", "1971-03-06", "Oakville, Ontario, Canada"),
    ("chyna", "Joan Marie Laurer", "1969-12-27", "Rochester, New York, U.S."),
]:
    if real_name or dob or birthplace:
        set_bio(wid, real_name, dob, birthplace, status="PROBABLE", src=S_WIKI_BIO)
wrestlers_by_id["test"]["deceased_date"] = wrestlers_by_id["test"]["deceased_date"] or "2009-03-13"
wrestlers_by_id["chyna"]["deceased_date"] = wrestlers_by_id["chyna"]["deceased_date"] or ""

new_flag("RR1999M", "wrestlers", "gangrel", "birthplace", "unverified",
    "Gangrel's exact birth city/state could not be confirmed this pass -- Wikipedia gives his DOB but not a "
    "birthplace, and S057 (Miami New Times) only establishes he was RAISED in Deerfield Beach, Florida "
    "('a rundown neighborhood... attended Deerfield Beach High'), which is a hometown/upbringing detail, not "
    "a stated birthplace. Left UNKNOWN rather than treating 'raised in' as 'born in.'", f"{S_WIKI_BIO};{S_MIAMINEWTIMES}")

new_flag("RR1999M", "wrestlers", "*", "real_name;dob;birthplace", "unverified",
    "Bio data added for 13 previously-unseen wrestlers this pass (Droz, Edge, Gillberg, Dan Severn, Tiger Ali "
    "Singh, Blue Meanie, Gangrel, Al Snow, The Godfather, Kane, Test, Val Venis, Chyna), single/double-sourced "
    "to Wikipedia (PROBABLE). Golga's real name (John Tenta) and Big Boss Man's real name were already "
    "CONFIRMED from earlier years -- only birthplace/DOB refinements were added for them.", S_WIKI_BIO,
    status="resolved")

resolve_flag("F120", "No new camera-cut timing data was found externally this pass -- the 4 documented "
    "uncertainties (Droz, Tiger Ali Singh, Mabel, Ken Shamrock) remain as originally derived from S044's own "
    "stated methodology; nothing to correct.")
resolve_flag("F121", "External sources (Wikipedia, TJR Wrestling, WrestleCrap) corroborate the 'abduction, not "
    "a conventional elimination' framing and add the physical-eliminator detail -- see the dedicated Mabel "
    "elimination re-model above.")
resolve_flag("F122", "Bio data added for the remaining previously-unseen wrestlers this pass; see the bio flag "
    "above for the full list and sourcing.")
# ===========================================================================
# 2000
# ===========================================================================
ev = events_by_id["RR2000M"]
ev["attendance_reported"] = "19231"
ev["ring_announcer"] = "Howard Finkel"
ev["referees"] = "Jack Doan, Earl Hebner, Jim Korderas, Theodore Long, Chad Patton, Mike Sparks, Tim White (per S050, single-sourced)"
ev["historical_significance"] = ev["historical_significance"].rstrip() + (
    " This was the WWF's 100th pay-per-view event and the 13th annual Royal Rumble -- per S050. Tazz made his "
    "surprise in-ring WWF debut in the show opener, defeating an undefeated Kurt Angle by submission (Tazzmission) "
    "-- per S050/S059. Kaientai's Taka Michinoku was legitimately injured (thrown over the top rope, hospitalized) "
    "during one of two unauthorized/angle-driven interference attempts on the Rumble match itself -- per S050/S037."
)
add_src(ev, S_WIKI_EVENT, S_SACNILK, S_WRESTLINGRECAPS, S_TJR)
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-16: venue/attendance (Madison Square Garden, NYC; 19,231) CONFIRMED "
    "(matches S046 exactly -- 6 independent sources checked, none support any alternate venue). Kane's entry "
    "number corrected from #27 to #28 (Bradshaw takes #27) -- 4 independent sources agree unanimously. The "
    "full 1-30 entry order, ring times, and eliminator credit were recovered (Wikipedia, cross-checked against "
    "sacnilk.com/thesmackdownhotel.com/wrestlingrecaps.com/TJRwrestling.net, with the recovered data matching "
    "all 9 previously-known eliminations exactly). Rikishi's 7 eliminated victims and his own 6 named "
    "eliminators were both recovered (previously 'unnamed group of ~8'). Viscera was merged into the existing "
    "'mabel' wrestler_id (2 independent sources). A previously-flagged possible hallucination ('X-Pac "
    "re-entered the match') was investigated again by the research agent and could NOT be independently "
    "confirmed by a non-AI-mediated source -- NOT added to the database. See F161-F168."
)

# --- Kane / Bradshaw entry-number swap (4-source agreement) ---
kane_er = entrants_by_key[("RR2000M", "kane")]
brad_er = entrants_by_key[("RR2000M", "bradshaw")]
assert kane_er["entry_number"] == "27", kane_er["entry_number"]
kane_er["entry_number"] = "28"
brad_er["entry_number"] = "27"
for r in (kane_er, brad_er):
    r["entry_number_status"] = "CONFIRMED"
    add_src(r, S_WIKI_EVENT, S_PWDB, S_TJR, S_WRESTLINGRECAPS)

new_flag("RR2000M", "entrants", "kane;bradshaw", "entry_number", "conflicting_sources",
    "The build phase had Kane at #27 with Bradshaw's entry number unknown. 4 independent external sources "
    "(Wikipedia, thesmackdownhotel.com/PWDB, TJRwrestling.net, wrestlingrecaps.com) unanimously agree the "
    "correct assignment is Kane #28, Bradshaw #27. Corrected in favor of the 4-source external agreement.",
    f"{S_WIKI_EVENT};{S_PWDB};{S_TJR};{S_WRESTLINGRECAPS}", status="resolved")

# --- Viscera / Mabel identity merge (2 independent sources) ---
key = ("RR2000M", "viscera")
if key in entrants_by_key:
    er = entrants_by_key.pop(key)
    er["wrestler_id"] = "mabel"
    entrants_by_key[("RR2000M", "mabel")] = er
mabel_w = wrestlers_by_id["mabel"]
mabel_w["aliases_ring_names"] = "; ".join(filter(None, [mabel_w["aliases_ring_names"], "Viscera", "Big Daddy V"]))
mabel_w["notes"] = (mabel_w["notes"].rstrip() + " Identity-merged with this database's former 'viscera' "
    "wrestler_id (RR2000M entrant) by the 1998-2002 fact-check pass -- 2 independent sources (Wikipedia's "
    "'Viscera (wrestler)' article and thesmackdownhotel.com/PWDB's career-timeline profile) both explicitly "
    "list 'Mabel' and 'Viscera' as ring names of the same performer, Nelson Lee Frazier Jr. Died 2014-02-18 "
    "(heart attack), per Wikipedia. See F127 (resolved).").strip()
mabel_w["deceased_date"] = mabel_w["deceased_date"] or "2014-02-18"
add_src(mabel_w, S_WIKI_BIO, S_PWDB)
wrestlers_by_id["viscera"]["notes"] = (
    "MERGED into the 'mabel' wrestler_id by the 1998-2002 fact-check pass -- 2 independent sources (Wikipedia "
    "+ thesmackdownhotel.com/PWDB) confirm Viscera and Mabel are the same performer, Nelson Lee Frazier Jr. "
    "This wrestler_id's RR2000M entrant row has been redirected to 'mabel'. Retained here only for "
    "audit-trail purposes -- do not use for any entrant/elimination record. See F127 (resolved)."
)
resolve_flag("F127", "2 independent sources (Wikipedia's 'Viscera (wrestler)' article, listing 'Mabel, "
    "Viscera, and Big Daddy V' as ring names of the same performer; thesmackdownhotel.com/PWDB's "
    "career-timeline profile, sequencing 'Mabel' Jun 1993-Jan 1999 directly into the Viscera era) confirm "
    "the identity. Merged into wrestler_id 'mabel' per the project's 2-source rule.")

# --- Full 1-30 entry order, ring time, eliminator (5-source cross-check; matches all 9 pre-known eliminations) ---
RR2000_ORDER = [
    (1, "d-lo-brown", ["rikishi"], "6:08"),
    (2, "brian-christopher", ["rikishi"], "7:42"),
    (3, "mosh", ["rikishi"], "2:08"),
    (4, "christian", ["rikishi"], "3:37"),
    (5, "rikishi", ["big-boss-man", "bob-backlund", "edge", "gangrel", "test", "british-bulldog"], "16:23"),
    (6, "scott-taylor", ["rikishi"], "1:02"),
    (7, "steve-blackman", ["rikishi"], "0:44"),
    (8, "mabel", ["rikishi"], "1:25"),  # Viscera
    (9, "big-boss-man", ["rocky-maivia"], "22:47"),
    (10, "test", ["big-show"], "26:17"),
    (11, "british-bulldog", ["jesse-james"], "15:22"),
    (12, "gangrel", ["big-show"], "23:19"),
    (13, "edge", ["al-snow", "val-venis"], "14:48"),
    (14, "bob-backlund", ["chris-jericho"], "2:00"),
    (15, "chris-jericho", ["chyna"], "3:47"),
    (16, "crash-holly", ["rocky-maivia"], "14:54"),
    (17, "chyna", ["big-boss-man"], "0:38"),
    (18, "faarooq", ["big-boss-man"], "0:18"),
    (19, "jesse-james", ["billy-gunn"], "19:02"),
    (20, "al-snow", ["rocky-maivia"], "17:17"),
    (21, "val-venis", ["kane"], "11:47"),
    (22, "prince-albert", ["kane"], "11:23"),
    (23, "hardcore-holly", ["al-snow"], "11:48"),
    (24, "rocky-maivia", None, ""),  # WINNER
    (25, "billy-gunn", ["kane"], "9:38"),
    (26, "big-show", ["rocky-maivia"], "11:12"),
    (27, "bradshaw", ["jesse-james", "billy-gunn"], "0:25"),
    (28, "kane", ["1-2-3-kid"], "6:11"),
    (29, "the-godfather", ["big-show"], "1:32"),
    (30, "1-2-3-kid", ["big-show"], "3:32"),  # X-Pac, already merged above
]
GROUP_ROWS_2000 = {5, 13, 27}
ALREADY_HAD_2000 = {
    ("test", "big-show"), ("big-boss-man", "rocky-maivia"), ("gangrel", "big-show"),
    ("crash-holly", "rocky-maivia"), ("val-venis", "kane"), ("prince-albert", "kane"),
    ("big-show", "rocky-maivia"), ("kane", "1-2-3-kid"), ("1-2-3-kid", "big-show"),
}

for entry_num, wid, elims, ring_time in RR2000_ORDER:
    er = entrants_by_key[("RR2000M", wid)]
    er["entry_number"] = str(entry_num)
    er["entry_number_status"] = "CONFIRMED"
    if ring_time:
        m, s = ring_time.split(":")
        er["ring_time"] = ring_time
        er["ring_time_seconds"] = str(int(m) * 60 + int(s))
        er["ring_time_status"] = "PROBABLE"
    er["data_quality_status"] = "PROBABLE"
    add_src(er, S_WIKI_EVENT, S_SACNILK, S_PWDB)
    if elims is None:
        er["is_winner"] = "TRUE"
        continue
    is_group = entry_num in GROUP_ROWS_2000
    er["eliminated_by_ids"] = ";".join(elims)
    if len(elims) == 1 and (wid, elims[0]) in ALREADY_HAD_2000:
        continue  # unchanged, already correct
    sim_group = f"2000_{wid}" if is_group else ""
    for e_wid in elims:
        add_elim("RR2000M", wid, e_wid, assisting=[x for x in elims if x != e_wid] if is_group else None,
                  is_shared=is_group,
                  notes=f"Entry order/eliminator recovered from S050, cross-checked by S058/S024/S059/S037. "
                        f"{'Group elimination -- ' + ', '.join(elims) + '.' if is_group else ''}".strip(),
                  src=f"{S_WIKI_EVENT};{S_SACNILK};{S_PWDB};{S_WRESTLINGRECAPS};{S_TJR}")

recompute_elim_counts("RR2000M", [e["wrestler_id"] for e in entrants if e["event_id"] == "RR2000M"])

resolve_flag("F124", "The full 1-30 entry order, ring times, and eliminator credit were recovered and "
    "cross-checked against 5 independent sources (Wikipedia, sacnilk.com, thesmackdownhotel.com/PWDB, "
    "wrestlingrecaps.com, TJRwrestling.net), all 9 of the database's previously-known eliminations matching "
    "exactly -- giving high confidence in the rest of the recovered table.")
resolve_flag("F125", "Rikishi's 7 eliminated victims (D-Lo Brown, Grandmaster Sexay/Brian Christopher, Mosh, "
    "Christian, Scotty 2 Hotty/Scott Taylor, Steve Blackman, Viscera/Mabel) and his own 6 named eliminators "
    "(Big Boss Man, Bob Backlund, Edge, Gangrel, Test, British Bulldog -- a named group of exactly 6, not an "
    "'unnamed ~8' as previously modeled) were both recovered from 3 independent sources agreeing on the same "
    "6 names.")
resolve_flag("F126", "External sources confirm the existing missed-call modeling is accurate -- no change "
    "needed. One additional, single-sourced (Wikipedia only, not independently corroborated) detail was found "
    "-- a claimed 2016 Rock/Big Show backstage segment where Rock admitted Big Show should have won -- but "
    "this is NOT added to the database as it could not be verified by a second source.")

new_flag("RR2000M", "wrestlers", "crash-holly", "birthplace", "conflicting_sources",
    "Crash Holly's birthplace remains a genuine conflict: Wikipedia (checked twice, consistently) says San "
    "Francisco, California; 2 independent non-Wikipedia sources (thesmackdownhotel.com/PWDB and "
    "slamwrestling.net) both instead say Anaheim, California. Per the project's tie-breaking rule (more "
    "independently-agreeing sources wins), Anaheim, California is used here (PROBABLE, not CONFIRMED, since "
    "Wikipedia disagrees) -- the San Francisco figure is preserved in this flag rather than silently discarded.",
    f"{S_WIKI_BIO};{S_PWDB};{S_SLAMWRESTLING}")
set_bio("crash-holly", birthplace="Anaheim, California, U.S.", status="PROBABLE", src=S_PWDB)
add_src(wrestlers_by_id["crash-holly"], S_SLAMWRESTLING)
wrestlers_by_id["crash-holly"]["deceased_date"] = wrestlers_by_id["crash-holly"]["deceased_date"] or "2003-11-06"

new_flag("RR2000M", "wrestlers", "scott-taylor", "dob", "conflicting_sources",
    "Scott Taylor's (Scotty 2 Hotty's 2000-era ring name) date of birth is a genuine conflict: Wikipedia gives "
    "July 2, 1973 (citing weak sources -- a MySpace page and an 'Intelius search' -- by its own citations); "
    "thesmackdownhotel.com/PWDB gives July 2, 1970. Both agree on month/day and birthplace (Westbrook, Maine). "
    "No third source broke the tie -- left UNKNOWN in the structured dob field rather than guessing.",
    f"{S_WIKI_BIO};{S_PWDB}")
set_bio("scott-taylor", real_name="Scott Ronald Garland", birthplace="Westbrook, Maine, U.S.", status="PROBABLE", src=S_PWDB)

for wid, real_name, dob, birthplace in [
    ("brian-christopher", "Brian Christopher Lawler", "1972-01-10", "Memphis, Tennessee, U.S."),
    ("christian", "William Jason Reso", "1973-11-30", "Kitchener, Ontario, Canada"),
    ("rikishi", "Solofa Fatu Jr.", "1965-10-11", "San Francisco, California, U.S."),
    ("chris-jericho", "Christopher Keith Irvine", "1970-11-09", "Manhasset, New York, U.S."),
    ("prince-albert", "Matthew Jason Bloom", "1972-11-14", "Peabody, Massachusetts, U.S."),
    ("hardcore-holly", None, None, "Glendale, California, U.S."),  # real name already CONFIRMED
    ("big-show", "Paul Donald Wight II", "1972-02-08", "Aiken, South Carolina, U.S."),
]:
    if real_name or dob or birthplace:
        set_bio(wid, real_name, dob, birthplace, status="PROBABLE", src=S_WIKI_BIO)

new_flag("RR2000M", "wrestlers", "rikishi", "dob", "unverified",
    "Rikishi's day-of-month is a minor 1-source-vs-1-source conflict: Wikipedia says October 11, 1965; "
    "thesmackdownhotel.com/PWDB says October 1, 1965 (both agree on month/year and birthplace, San Francisco). "
    "Wikipedia's figure is used per this pass's default, difference noted rather than silently discarded.",
    f"{S_WIKI_BIO};{S_PWDB}")

new_flag("RR2000M", "wrestlers", "*", "real_name;dob;birthplace", "unverified",
    "Bio data added for 8 previously-unseen wrestlers this pass (Brian Christopher, Christian, Rikishi, Chris "
    "Jericho, Prince Albert, Big Show, plus refinements for Hardcore Holly/Crash Holly/Scott Taylor), "
    "single/double-sourced to Wikipedia (PROBABLE).", S_WIKI_BIO, status="resolved")
# ===========================================================================
# 2001
# ===========================================================================
ev = events_by_id["RR2001M"]
ev["attendance_reported"] = "17137"
ev["referees"] = "Mike Chioda, Tim White, Jim Korderas, Jack Doan, Earl Hebner, Chad Patton (per S050, single-sourced)"
ev["historical_significance"] = ev["historical_significance"].rstrip() + (
    " Kane's 11 eliminations broke the single-match record of 10, jointly held by Hulk Hogan (1989) and Steve "
    "Austin himself (1997) -- per S050; this new record stood for 13 years until Roman Reigns eliminated 12 "
    "in 2014, per S040. Austin's win was his 3rd, making him the first three-time Royal Rumble winner -- per "
    "S050/S040. Drew Carey's celebrity-entrant appearance (entry #5) came about via an on-screen storyline "
    "where Vince McMahon pulled a promised Sunday Night Heat pre-show winner's slot and gave it to Carey "
    "instead, hoping he would be pummeled -- Carey safely self-eliminated by climbing over the top rope; this "
    "appearance led to his 2010s induction into the WWE Hall of Fame's celebrity wing -- per S050."
)
add_src(ev, S_WIKI_EVENT, S_ALLRUMBLE)
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-16: attendance CONFIRMED at 17,137. Austin's drawn number CONFIRMED at "
    "#27 by 4 independent external sources (Wikipedia, Online World of Wrestling, Cageside Seats, "
    "allrumblestats.com) -- the internal S048 Dan Wahlers narrative's '#26' is a confirmed transcription "
    "error, not a genuine alternate account. Austin's unusual delayed/out-of-order physical entry (coinciding "
    "with Rikishi's #30 entrance) is independently corroborated by all 4 of the same external sources. Kane's "
    "remaining 6 (of 11) eliminations were recovered and added: Raven, Brian Christopher, Tazz, Prince Albert, "
    "Crash Holly, and Scotty 2 Hotty (jointly with The Undertaker). Scotty 2 Hotty was merged into the "
    "existing 'scott-taylor' wrestler_id (2 independent sources). Note: 9 entrants (Faarooq, The Godfather, "
    "Bradshaw, Hardcore Holly, K-Kwik, Val Venis, William Regal, Test, Haku) still have no eliminator credit "
    "-- this specific research pass did not turn up sourced data for them; left open rather than guessed. See "
    "F169-F173."
)

# --- Austin drawn-number confirmation (#27, already correct -- upgrade to CONFIRMED) ---
austin_er = entrants_by_key[("RR2001M", "steve-austin")]
austin_er["entry_number_status"] = "CONFIRMED"
add_src(austin_er, S_WIKI_EVENT, S_OWW, S_CAGESIDE, S_ALLRUMBLE)
austin_er["notes"] = (austin_er["notes"].rstrip() + " Drawn number #27 CONFIRMED by 4 independent external "
    "sources (Wikipedia, OWOW, Cageside Seats, allrumblestats.com); the internal S048 Dan Wahlers narrative's "
    "'#26' is a confirmed transcription error. See F130 (resolved).").strip()
resolve_flag("F130", "4 independent external sources (Wikipedia, Online World of Wrestling, Cageside Seats, "
    "allrumblestats.com) unanimously confirm Austin's drawn number as #27 -- none support #26. The internal "
    "S048 narrative's '#26' is a confirmed transcription error, not a genuine alternate account. The delayed/"
    "out-of-order physical entry (Austin's actual ring entry coinciding with Rikishi's #30 entrance, after "
    "being attacked in the aisle by Triple H) is independently corroborated by all 4 sources, including the "
    "specific detail that Austin's path into the match was via attacking Rikishi in the aisle.")

# --- Kane's remaining 6 (of 11) eliminations ---
RR2001_KANE_NEW = ["raven", "brian-christopher", "tazz", "prince-albert", "crash-holly"]
for wid in RR2001_KANE_NEW:
    add_elim("RR2001M", wid, "kane",
             notes="One of Kane's then-record 11 eliminations; recovered from 3 independent sources (Wikipedia, "
                   "Online World of Wrestling, allrumblestats.com).",
             src=f"{S_WIKI_EVENT};{S_OWW};{S_ALLRUMBLE}")
    entrants_by_key[("RR2001M", wid)]["eliminated_by_ids"] = "kane"

# --- Scotty 2 Hotty / Scott Taylor identity merge (2 independent sources) ---
for ev_id in ("RR2001M", "RR2002M"):
    key = (ev_id, "scotty-2-hotty")
    if key in entrants_by_key:
        er = entrants_by_key.pop(key)
        er["wrestler_id"] = "scott-taylor"
        entrants_by_key[(ev_id, "scott-taylor")] = er
for row in eliminations:
    if row["eliminated_wrestler_id"] == "scotty-2-hotty":
        row["eliminated_wrestler_id"] = "scott-taylor"
    if row["eliminator_wrestler_id"] == "scotty-2-hotty":
        row["eliminator_wrestler_id"] = "scott-taylor"
    row["assisting_wrestler_ids"] = ";".join(
        "scott-taylor" if a == "scotty-2-hotty" else a for a in row["assisting_wrestler_ids"].split(";") if a)

taylor_w = wrestlers_by_id["scott-taylor"]
taylor_w["aliases_ring_names"] = "; ".join(filter(None, [taylor_w["aliases_ring_names"], "Scotty 2 Hotty", "Too Hot"]))
taylor_w["notes"] = (taylor_w["notes"].rstrip() + " Identity-merged with this database's former 'scotty-2-hotty' "
    "wrestler_id (RR2001M/RR2002M entrant) by the 1998-2002 fact-check pass -- 2 independent sources (Wikipedia's "
    "'Scotty 2 Hotty' infobox, listing 'Scott Taylor' and 'Scotty 2 Hotty' as sequential ring names of the same "
    "performer, Scott Ronald Garland; thesmackdownhotel.com/PWDB's career-timeline profile, sequencing 'Scott "
    "Taylor' Nov 1989-Feb 1999 directly into 'Scotty 2 Hotty' from Mar 1999) confirm the identity. See F132 "
    "(resolved).").strip()
add_src(taylor_w, S_WIKI_BIO, S_PWDB)
wrestlers_by_id["scotty-2-hotty"]["notes"] = (
    "MERGED into the 'scott-taylor' wrestler_id by the 1998-2002 fact-check pass -- 2 independent sources "
    "(Wikipedia + thesmackdownhotel.com/PWDB) confirm Scotty 2 Hotty and Scott Taylor are the same performer, "
    "Scott Ronald Garland. This wrestler_id's RR2001M/RR2002M entrant/elimination rows have been redirected to "
    "'scott-taylor'. Retained here only for audit-trail purposes -- do not use for any entrant/elimination "
    "record. See F132 (resolved)."
)
resolve_flag("F132", "2 independent sources (Wikipedia's 'Scotty 2 Hotty' infobox and article text, and "
    "thesmackdownhotel.com/PWDB's career-timeline profile) both explicitly treat 'Scott Taylor' and 'Scotty 2 "
    "Hotty' as sequential ring names of one performer, Scott Ronald Garland. Merged into wrestler_id "
    "'scott-taylor' per the project's 2-source rule. His DOB remains a genuine, unresolved 1973-vs-1970 "
    "conflict between the same 2 sources -- see the dedicated flag filed against this wrestler_id in the 2000 "
    "section.")

# --- Scotty 2 Hotty / Scott Taylor's own 2001 elimination: Kane AND The Undertaker jointly ---
add_elim("RR2001M", "scott-taylor", "kane", assisting=["the-undertaker"], is_shared=True,
         notes="Scott Taylor's (as 'Scotty 2 Hotty') own 2001 elimination -- credited jointly to Kane (his "
               "11th and final elimination of the match) and The Undertaker. Recovered from 3 independent "
               "sources (Wikipedia, Online World of Wrestling, allrumblestats.com).",
         src=f"{S_WIKI_EVENT};{S_OWW};{S_ALLRUMBLE}")
add_elim("RR2001M", "scott-taylor", "the-undertaker", assisting=["kane"], is_shared=True,
         notes="See the Kane row above for full detail.", src=f"{S_WIKI_EVENT};{S_OWW};{S_ALLRUMBLE}")
entrants_by_key[("RR2001M", "scott-taylor")]["eliminated_by_ids"] = "kane;the-undertaker"

recompute_elim_counts("RR2001M", [e["wrestler_id"] for e in entrants if e["event_id"] == "RR2001M"])

resolve_flag("F131", "Kane's remaining 6 (of 11) eliminations recovered from 3 independent sources agreeing "
    "exactly: Raven, Brian Christopher (Grand Master Sexay), Tazz, Prince Albert, Crash Holly, and Scotty 2 "
    "Hotty/Scott Taylor (jointly with The Undertaker) -- bringing the individually-named total to 11, matching "
    "the CONFIRMED aggregate exactly and leaving no room for an alternate list (cross-checked against every "
    "other wrestler's individual elimination count in the match).")

new_flag("RR2001M", "wrestlers", "drew-carey", "real_name", "unverified",
    "Drew Carey's real middle name is 'Allison' per Wikipedia's infobox ('Born Drew Allison Carey'), not "
    "'Allen' as might be assumed.", S_WIKI_BIO)

for wid, real_name, dob, birthplace in [
    ("jeff-hardy", "Jeffrey Nero Hardy", "1977-08-31", "Cameron, North Carolina, U.S."),
    ("bull-buchanan", "Barry Buchanan", "1968-01-15", "Bowdon, Georgia, U.S."),
    ("matt-hardy", "Matthew Moore Hardy", "1974-09-23", "Cameron, North Carolina, U.S."),
    ("drew-carey", "Drew Allison Carey", "1958-05-23", "Cleveland, Ohio, U.S."),
    ("raven", "Scott Levy", "1964-09-08", "Philadelphia, Pennsylvania, U.S."),
    ("perry-saturn", "Perry Arthur Satullo", "1966-10-25", "Cleveland, Ohio, U.S."),
    ("william-regal", "Darren Kenneth Matthews", "1968-05-10", "Codsall, Staffordshire, England"),
    ("tazz", "Peter Senerchia", "1967-10-11", "Brooklyn, New York, U.S."),
    ("k-kwik", "Ronnie Aaron Killings", "1972-01-19", "Charlotte, North Carolina, U.S."),
]:
    set_bio(wid, real_name, dob, birthplace, status="PROBABLE", src=S_WIKI_BIO,
            extra_note="Later known as 'R-Truth.'" if wid == "k-kwik" else None)

new_flag("RR2001M", "wrestlers", "*", "real_name;dob;birthplace", "unverified",
    "Bio data added for 9 previously-unseen wrestlers this pass (Jeff Hardy, Bull Buchanan, Matt Hardy, Drew "
    "Carey, Raven, Perry Saturn, William Regal, Tazz, K-Kwik), single-sourced to Wikipedia (PROBABLE).",
    S_WIKI_BIO, status="resolved")
# ===========================================================================
# 2002
# ===========================================================================
ev = events_by_id["RR2002M"]
ev["referees"] = "Mike Chioda, Jack Doan, Brian Hebner, Earl Hebner, Jim Korderas, Theodore Long, Nick Patrick, Charles Robinson, Tim White (per S050, single-sourced)"
ev["historical_significance"] = ev["historical_significance"].rstrip() + (
    " At 69:22, this remains, per S061/S036, the longest 30-man Royal Rumble match up to that point, "
    "surpassing 1993's previous record. Per S061, the event drew 670,000 PPV buys, the most-bought Royal "
    "Rumble in WWE history at the time (surpassing 1999's 650,000). Steve Austin set a then-record of 36 "
    "cumulative career Royal Rumble eliminations at this event, a record that stood for 8 years until Shawn "
    "Michaels broke it in 2010 -- per S050. This was Austin's 5th Final Four appearance and his last Royal "
    "Rumble match. Per S063, Austin and The Undertaker tied for most eliminations in this match at 7 apiece."
)
add_src(ev, S_WIKI_EVENT, S_ENUFFA, S_BLEACHER)

# --- Attendance conflict: internal S049 (12,915) vs 2 independent external sources (16,106) ---
ev["attendance_reported"] = "16106"
add_src(ev, S_WIKI_EVENT, S_PWDB)
new_flag("RR2002M", "events", "RR2002M", "attendance_reported", "conflicting_sources",
    "The internal S049 (Dan Wahlers chapter) gives attendance as 12,915. Two independent external sources "
    "(Wikipedia and thesmackdownhotel.com/PWDB) both instead give 16,106. Per the project's tie-breaking rule "
    "(2+ independently-agreeing external sources over a single internal source, as used for the 1995 Bob "
    "Backlund/Steven Dunn entry-number swap), 16,106 is used here; the internal 12,915 figure is preserved in "
    "this flag rather than silently discarded.", f"{S_WIKI_EVENT};{S_PWDB}")

# --- Triple H entry-number correction (5-source agreement: 24 -> 22), Faarooq's slot newly established ---
hhh_er = entrants_by_key[("RR2002M", "hunter-hearst-helmsley")]
assert hhh_er["entry_number"] == "24", hhh_er["entry_number"]
hhh_er["entry_number"] = "22"
hhh_er["entry_number_status"] = "CONFIRMED"
hhh_er["ring_time"], hhh_er["ring_time_seconds"] = "23:14", str(23 * 60 + 14)
hhh_er["ring_time_status"] = "PROBABLE"
add_src(hhh_er, S_WIKI_EVENT, S_WWE_HISTORY, S_ALLRUMBLE, S_TJR, S_PWDB)
hhh_er["notes"] = (hhh_er["notes"].rstrip() + " Entry number CORRECTED from 24 to 22, 2026-09-16 -- 5 "
    "independent sources (Wikipedia, WWE.com's own official history page, allrumblestats.com, TJRwrestling.net, "
    "thesmackdownhotel.com/PWDB) unanimously agree. One outlier (a Cageside Seats stats article giving #20) "
    "was checked and discounted as a probable extraction error -- see F174 (resolved).").strip()

faarooq_er = entrants_by_key[("RR2002M", "faarooq")]
faarooq_er["entry_number"] = "24"
faarooq_er["entry_number_status"] = "CONFIRMED"
faarooq_er["ring_time"], faarooq_er["ring_time_seconds"] = "0:36", "36"
faarooq_er["ring_time_status"] = "PROBABLE"
faarooq_er["eliminated_by_ids"] = "hunter-hearst-helmsley"
add_src(faarooq_er, S_WIKI_EVENT, S_WWE_HISTORY, S_ALLRUMBLE, S_TJR, S_PWDB)
add_elim("RR2002M", "faarooq", "hunter-hearst-helmsley",
         notes="Faarooq's entry number (#24) was previously entirely unknown -- newly established by 5 "
               "independent sources, all also crediting Triple H with this elimination at 0:36.",
         src=f"{S_WIKI_EVENT};{S_WWE_HISTORY};{S_ALLRUMBLE};{S_TJR};{S_PWDB}")

new_flag("RR2002M", "entrants", "hunter-hearst-helmsley;faarooq", "entry_number", "conflicting_sources",
    "The build phase (from S049's narrative) had Triple H at entry #24 with Faarooq's entry number entirely "
    "unknown. 5 independent external sources (Wikipedia, WWE.com's official history page, allrumblestats.com, "
    "TJRwrestling.net, thesmackdownhotel.com/PWDB) unanimously agree Triple H was actually #22 and Faarooq was "
    "#24 (eliminated by Triple H at 0:36). One outlier source (a Cageside Seats stats article giving Triple H "
    "as the '20th competitor') was checked and discounted as a probable data-extraction error, since the same "
    "fetch correctly reproduced the well-known 69:22 total match time. Corrected in favor of the 5-source "
    "agreement.", f"{S_WIKI_EVENT};{S_WWE_HISTORY};{S_ALLRUMBLE};{S_TJR};{S_PWDB}", status="resolved")
resolve_flag("F135", "The full 1-30 entry order and ring times were recovered from Wikipedia, cross-checked "
    "against WWE.com's official ordered entrant list (which independently reproduced the identical 1-30 "
    "sequence). Triple H's entry number was additionally corrected from 24 to 22 -- see the dedicated flag.")

# --- Remaining entry order / ring times / eliminator credit (Wikipedia + WWE.com + allrumblestats.com) ---
RR2002_REMAINING = [
    (1, "rikishi", "13:39"), (2, "goldust", "12:38"), (3, "big-boss-man", "3:05"),
    (4, "bradshaw", "7:17"), (5, "lance-storm", "4:46"), (6, "al-snow", "5:12"),
    (7, "billy-gunn", "3:37"), (8, "the-undertaker", "7:40"), (9, "matt-hardy", "4:16"),
    (10, "jeff-hardy", "1:30"), (12, "scott-taylor", "2:36"), (13, "christian", "12:14"),
    (14, "diamond-dallas-page", "5:15"), (15, "chuck-palumbo", "9:04"),
    (16, "the-godfather", "1:48"), (17, "prince-albert", "0:48"), (18, "perry-saturn", "2:57"),
    (19, "steve-austin", "26:46"), (20, "val-venis", "2:58"), (21, "test", "1:42"),
    (23, "the-hurricane", "0:39"), (25, "mr-perfect", "15:18"), (26, "kurt-angle", "16:09"),
    (27, "big-show", "2:45"), (28, "kane", "1:02"), (29, "rob-van-dam", "2:12"), (30, "booker-t", "0:33"),
]
for entry_num, wid, ring_time in RR2002_REMAINING:
    er = entrants_by_key[("RR2002M", wid)]
    if not er["entry_number"]:
        er["entry_number"] = str(entry_num)
        er["entry_number_status"] = "CONFIRMED"
    m, s = ring_time.split(":")
    er["ring_time"] = ring_time
    er["ring_time_seconds"] = str(int(m) * 60 + int(s))
    er["ring_time_status"] = "PROBABLE"
    add_src(er, S_WIKI_EVENT, S_ALLRUMBLE)

# entrants newly assigned an entry number this pass (previously entirely UNKNOWN)
for wid in ("big-boss-man", "bradshaw", "lance-storm", "scott-taylor", "diamond-dallas-page"):
    entrants_by_key[("RR2002M", wid)]["data_quality_status"] = "PROBABLE"

new_flag("RR2002M", "entrants", "big-boss-man;bradshaw;lance-storm;scott-taylor;diamond-dallas-page", "entry_number",
    "unverified",
    "Entry numbers (and ring times) newly established for 5 previously-unknown entrants this pass: Big Boss "
    "Man (#3), Bradshaw (#4), Lance Storm (#5), Scotty 2 Hotty/Scott Taylor (#12), Diamond Dallas Page (#14) "
    "-- from Wikipedia's structured table, cross-checked against WWE.com's official ordered list and "
    "allrumblestats.com.", f"{S_WIKI_EVENT};{S_WWE_HISTORY};{S_ALLRUMBLE}", status="resolved")

# --- New eliminations: Big Boss Man, Bradshaw, Lance Storm, Scotty 2 Hotty/Scott Taylor, DDP ---
for eliminated_wid, eliminator_wid in [
    ("big-boss-man", "rikishi"), ("bradshaw", "billy-gunn"), ("lance-storm", "al-snow"),
    ("scott-taylor", "diamond-dallas-page"), ("diamond-dallas-page", "christian"),
]:
    add_elim("RR2002M", eliminated_wid, eliminator_wid,
             notes="Entry order/eliminator recovered from S050, cross-checked by S051/S040.",
             src=f"{S_WIKI_EVENT};{S_WWE_HISTORY};{S_ALLRUMBLE}")
    entrants_by_key[("RR2002M", eliminated_wid)]["eliminated_by_ids"] = eliminator_wid

# --- Godfather and Prince Albert: joint elimination by Chuck Palumbo and Christian ---
for wid in ("the-godfather", "prince-albert"):
    for e_wid in ("chuck-palumbo", "christian"):
        add_elim("RR2002M", wid, e_wid, assisting=[x for x in ("chuck-palumbo", "christian") if x != e_wid],
                  is_shared=True,
                  notes="Jointly eliminated by Chuck Palumbo and Christian -- per S050, a detail not previously "
                        "in the database, suggesting a mini-alliance/spot between the two mid-match.",
                  src=f"{S_WIKI_EVENT};{S_ALLRUMBLE}")
    entrants_by_key[("RR2002M", wid)]["eliminated_by_ids"] = "chuck-palumbo;christian"

# --- Steve Austin's elimination: Mr. Perfect added as a joint eliminator alongside Kurt Angle ---
for row in eliminations:
    if row["event_id"] == "RR2002M" and row["eliminated_wrestler_id"] == "steve-austin":
        row["assisting_wrestler_ids"] = "mr-perfect"
        row["is_shared"] = "TRUE"
        row["is_solo"] = "FALSE"
        row["notes"] = (row["notes"].rstrip() + " CORRECTED 2026-09-16: was credited solely to Kurt Angle. "
                        "Wikipedia's entrant table instead credits this elimination jointly to Kurt Angle AND "
                        "Mr. Perfect. See F175 (resolved).").strip()
        add_src(row, S_WIKI_EVENT)
entrants_by_key[("RR2002M", "steve-austin")]["eliminated_by_ids"] = "kurt-angle;mr-perfect"
new_flag("RR2002M", "eliminations", "steve-austin", "assisting_wrestler_ids", "unverified",
    "Steve Austin's elimination (the Final Four stretch, 26:46) was originally credited solely to Kurt Angle. "
    "Wikipedia's structured entrant table instead credits this jointly to Kurt Angle and Mr. Perfect. Mr. "
    "Perfect added as a joint/assisting eliminator.", S_WIKI_EVENT, status="resolved")

# --- Kane's elimination: previously no eliminator credited; Kurt Angle added ---
add_elim("RR2002M", "kane", "kurt-angle",
         notes="Previously had no eliminator credited. Recovered from Wikipedia + allrumblestats.com.",
         src=f"{S_WIKI_EVENT};{S_ALLRUMBLE}")
entrants_by_key[("RR2002M", "kane")]["eliminated_by_ids"] = "kurt-angle"

recompute_elim_counts("RR2002M", [e["wrestler_id"] for e in entrants if e["event_id"] == "RR2002M"])

new_flag("RR2002M", "entrants", "maven", "eliminated_by_ids", "unverified",
    "No reliable source could be found for who eliminated Maven after his famous elimination of The "
    "Undertaker. One web-fetch extraction pass returned 'eliminated by The Undertaker' for Maven's row -- "
    "this is logically impossible (Undertaker had already been eliminated by Maven and cannot re-enter) and "
    "is almost certainly a table-misalignment artifact (the same pass also mis-shifted several neighboring "
    "rows' entry numbers). Multiple recap sources describe Undertaker brutally beating down Maven after the "
    "elimination but none specify who formally eliminates him from the match or when. Left UNKNOWN rather "
    "than guessed.", S_WIKI_EVENT)

resolve_flag("F136", "No external source contradicts this modeling; not independently re-verified further "
    "this pass (out of scope for the specific questions asked).")
resolve_flag("F137", "Every source checked this pass (Wikipedia, allrumblestats.com, TJR Wrestling, "
    "wrestlingrecaps.com, historyofwrestlingblog.wordpress.com) confirms the joint Austin/Triple H framing -- "
    "no source anywhere attributes this elimination to a single man. The existing modeling is correct and "
    "well-corroborated; no change needed.")
resolve_flag("F138", "Every source that discusses the sequence in any detail (Wikipedia, "
    "historyofwrestlingblog.wordpress.com, TJR Wrestling) explicitly confirms Triple H's Pedigree "
    "incapacitated RVD first, with Booker T performing the actual elimination moments later. The existing "
    "modeling is accurate and well-corroborated; no change needed.")

# --- Mr. Perfect post-Rumble career correction ---
mp = wrestlers_by_id["mr-perfect"]
mp["notes"] = (mp["notes"].rstrip() + " CORRECTED 2026-09-16: this event's internal narrative previously "
    "implied the 2002 Royal Rumble was essentially the last notable thing before Mr. Perfect's death -- this "
    "is WRONG. Per Wikipedia (Curt Hennig) and S064 (TheSportster.com): his Final-Four Rumble showing earned "
    "him a new full-time WWE contract and an assignment to the Raw brand in the 2002 draft. On the flight home "
    "from the Insurrextion (2002) PPV (May 4, 2002 UK), he was involved in the 'Plane Ride From Hell' incident "
    "(a shaving-cream prank on Brock Lesnar that escalated into a scuffle); he was released within days "
    "(May 7 per S064, May 8 per Wikipedia -- both attested, not resolved to one date). He then wrestled for "
    "TNA through his final match on January 8, 2003 (defeating David Flair), before his death on February 10, "
    "2003 in Brandon, Florida (acute drug overdose -- mixed toxicity from steroids and painkillers). See F176 "
    "(resolved).").strip()
add_src(mp, S_WIKI_BIO, S_SPORTSTER)
new_flag("RR2002M", "wrestlers", "mr-perfect", "notes", "unverified",
    "The database's internal narrative previously implied this 2002 Royal Rumble appearance was essentially "
    "the last notable thing before Curt Hennig's ('Mr. Perfect's') death. This was WRONG -- corrected with a "
    "full timeline (new WWE contract, Raw brand draft, Plane Ride From Hell incident, release, TNA run through "
    "Jan 2003, death Feb 10 2003). See the wrestler's notes field for full detail.", f"{S_WIKI_BIO};{S_SPORTSTER}",
    status="resolved")

for wid, real_name, dob, birthplace in [
    ("booker-t", "Booker T. Huffman Jr.", "1965-03-01", "Plain Dealing, Louisiana, U.S."),
    ("chuck-palumbo", "Charles Ronald Palumbo", "1971-06-15", "West Warwick, Rhode Island, U.S."),
    ("diamond-dallas-page", "Page Joseph Falkinburg Jr.", "1956-04-05", "Point Pleasant, New Jersey, U.S."),
    ("kurt-angle", "Kurt Steven Angle", "1968-12-09", "Mt. Lebanon, Pennsylvania, U.S."),
    ("lance-storm", "Lance Timothy Evers", "1969-04-03", "Sarnia, Ontario, Canada"),
    ("maven", "Maven Klate Huffman", "1976-11-26", "Nashville, Tennessee, U.S."),
    ("rob-van-dam", "Robert Szatkowski", "1970-12-18", "Battle Creek, Michigan, U.S."),
    ("the-hurricane", "Gregory Shane Helms", "1974-07-12", "Smithfield, North Carolina, U.S."),
]:
    set_bio(wid, real_name, dob, birthplace, status="PROBABLE", src=S_WIKI_BIO)
wrestlers_by_id["booker-t"]["notes"] = (wrestlers_by_id["booker-t"]["notes"].rstrip() +
    " Wikipedia notes his birthplace 'is often misidentified as Houston, Texas.'").strip()

resolve_flag("F139", "Bio data added for all 8 previously-unseen wrestlers this pass (Booker T, Chuck Palumbo, "
    "Diamond Dallas Page, Kurt Angle, Lance Storm, Maven, Rob Van Dam, The Hurricane), single-sourced to "
    "Wikipedia (PROBABLE).")

new_flag("RR2002M", "wrestlers", "the-undertaker", "wrestlers_eliminated_count", "unverified",
    "S063 (Bleacher Report) claims Austin and The Undertaker 'both tossed seven men over the top rope' "
    "(tied for most eliminations). Austin's reproduced total from this database's recovered elimination data "
    "is exactly 7, but The Undertaker's is only 6 (Rikishi, Goldust, Al Snow, Billy Gunn, Matt Hardy, Jeff "
    "Hardy) -- no source consulted this pass names a 7th Undertaker elimination. Left at 6 (the sourced, "
    "named figure) rather than adjusting to match the single-sourced '7' trivia claim.", S_BLEACHER)

save("events.csv", events, EVENTS_FIELDS)
save("wrestlers.csv", wrestlers, WRESTLERS_FIELDS)
save("entrants.csv", entrants, ENTRANTS_FIELDS)
save("eliminations.csv", eliminations, ELIM_FIELDS)
save("flags.csv", flags, FLAGS_FIELDS)
save("sources.csv", sources, SOURCES_FIELDS)

print(f"Done. Next flag id: F{flag_ctr[0]:03d}. Total flags: {len(flags)}. Total sources: {len(sources)}. "
      f"Total wrestlers: {len(wrestlers)}. Total entrants: {len(entrants)}. Total eliminations: {len(eliminations)}.")
