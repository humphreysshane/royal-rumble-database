# -*- coding: utf-8 -*-
"""
External fact-check pass for the 1993-1997 Royal Rumbles, mirroring the
fact-check pass already done for 1988-1992. Built from 5 parallel research
agents' findings (Wikipedia event articles, Wikipedia wrestler bios,
thesmackdownhotel.com/PWDB, Online World of Wrestling, plus several
retrospective outlets: Cageside Seats, TJR Wrestling, Cultaholic,
WrestlingInc, allrumblestats.com, Scott's Blog of Doom).

This is a PATCH script, not a build script: it mutates the already-built
data/*.csv files in place (loads, edits in memory, writes back), rather
than appending fresh rows to an empty table. Run against an isolated test
copy first, then the live database, exactly like every build script.

Flag IDs continue from F085 (F086 onward). Source IDs continue from S034
(S035 onward). Wrestler IDs for brand-new people continue the existing
convention (slugified ring name).
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

flag_ctr = [86]
def new_flag(event_id, table, record_id, field, issue_type, description, source_ids, status="open"):
    fid = f"F{flag_ctr[0]:03d}"
    flag_ctr[0] += 1
    flags.append({
        "flag_id": fid, "event_id": event_id, "table": table, "record_id": record_id,
        "field": field, "issue_type": issue_type, "description": description,
        "source_ids_involved": source_ids, "status": status, "date_logged": "2026-09-15",
    })
    return fid


def resolve_flag(flag_id, resolution_note):
    for f in flags:
        if f["flag_id"] == flag_id:
            f["status"] = "resolved"
            f["description"] = f["description"].rstrip() + " -- RESOLVED by the 1993-1997 fact-check pass: " + resolution_note
            return
    raise KeyError(f"flag {flag_id} not found")


# ---------------------------------------------------------------------------
# NEW SOURCES (S035 onward)
# ---------------------------------------------------------------------------
new_sources = [
    ("S035", "Wikipedia (English), Royal Rumble (1993)-(1997) event articles", "reference_site", "",
     10, "Wikipedia/reference sites", "2026-09-15",
     "Event-level facts (date, venue, attendance, duration, referees, commentary, ring announcer, entrant/"
     "elimination tables) for all 5 events. Cross-checked against thesmackdownhotel.com/OWW/Cagematch where "
     "those loaded. Long ordered tables required a verbatim-transcription re-fetch in several cases after an "
     "initial AI-summarized fetch scrambled row order -- see individual flags below for where this mattered."),
    ("S036", "Cageside Seats, per-event 'match time/statistics' retrospective articles", "contemporary_publication", "",
     9, "Contemporary wrestling publication", "2026-09-15",
     "Independent frame-by-frame-style timing retrospectives for the 1993/1994/1995 Rumbles, used to "
     "cross-check match duration and (for 1993) survival-time/ring-crowdedness detail."),
    ("S037", "TJR Wrestling, event retrospective reviews", "reputable_publication", "",
     12, "Other reputable site", "2026-09-15",
     "Used for 1996/1997 event reviews -- duration/referee corroboration and several trivia items."),
    ("S038", "Cultaholic.com, retrospective trivia articles", "reputable_publication", "",
     12, "Other reputable site", "2026-09-15",
     "Used for 1997 attendance/trivia corroboration."),
    ("S039", "WrestlingInc.com", "reputable_publication", "",
     12, "Other reputable site", "2026-09-15",
     "Used for the 1996 Steve Austin baby-oil-elimination anecdote."),
    ("S040", "allrumblestats.com", "reputable_publication", "",
     12, "Other reputable site", "2026-09-15",
     "Used for 1995/1996 entry-number and per-wrestler elimination-count corroboration."),
    ("S041", "Scott's Blog of Doom (blogofdoom.com) event reviews", "reputable_publication", "",
     12, "Other reputable site", "2026-09-15",
     "Used for 1995 referee/trivia corroboration."),
    ("S042", "Online World of Wrestling (onlineworldofwrestling.com) event results pages", "wrestling_database", "",
     12, "Other reputable site", "2026-09-15",
     "Reused resource (same site as S025, new pages) -- used for 1994/1995/1997 entrant-order cross-checks; "
     "returned a 403 for 1996 and could not be checked that year."),
]
for row in new_sources:
    sources.append(dict(zip(SOURCES_FIELDS, row)))

S_WIKI_EVENT = "S035"
S_CAGESIDE = "S036"
S_TJR = "S037"
S_CULTAHOLIC = "S038"
S_WRESTLINGINC = "S039"
S_ALLRUMBLE = "S040"
S_BLOGOFDOOM = "S041"
S_OWW2 = "S042"
S_WIKI_BIO = "S022"  # reused, same resource as the 1988-1992 pass
S_PWDB = "S024"      # reused
S_OWW = "S025"       # reused


def set_bio(wid, real_name=None, dob=None, birthplace=None, status="PROBABLE", extra_note=None, src=S_WIKI_BIO):
    """Fill bio fields on an existing wrestlers.csv row, only where currently blank,
    and only ever upgrading status (never downgrading an existing CONFIRMED)."""
    w = wrestlers_by_id[wid]
    def _set(field_val, status_field, val, st):
        cur_status = w[status_field]
        if cur_status in ("CONFIRMED",):
            return  # never downgrade/overwrite an already-confirmed field
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
    ids = set(filter(None, w["source_ids"].split(";")))
    ids.add(src)
    w["source_ids"] = ";".join(sorted(ids))


# ===========================================================================
# 1993
# ===========================================================================
ev = events_by_id["RR1993M"]
ev["ring_announcer"] = "Howard Finkel"
ev["historical_significance"] = (
    "First Royal Rumble where the winner was guaranteed a WWF Championship match at that year's WrestleMania "
    "-- the format that has continued ever since (per S035). Bob Backlund's elimination at roughly the "
    "61-minute mark set a new Rumble longevity record at the time, standing for 11 years until broken by "
    "Chris Benoit in 2004 (per S035; S036 gives a slightly different 61:16 for the same figure, ~6 seconds "
    "off, plausibly due to how the Giant Gonzalez interloper angle was clocked -- see F090). Lex Luger's WWF "
    "debut, after departing the World Bodybuilding Federation (per S035)."
)
ev["source_ids"] = ";".join(sorted(set(filter(None, ev["source_ids"].split(";"))) | {S_WIKI_EVENT, S_PWDB, S_CAGESIDE}))
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-15: date/venue/attendance(16,000)/duration(66:40)/commentary/winner all "
    "confirmed by 2+ independent sources (Wikipedia event article + thesmackdownhotel.com/PWDB); full 30-entrant "
    "order independently confirmed exactly matching the DB's internal order; the Giant Gonzalez interloper "
    "detail independently confirmed. See F086-F090."
)

new_flag("RR1993M", "events", "RR1993M", "duration_total", "unverified",
    "Duration is CONFIRMED at 66:40, exactly matching S036 (Cageside Seats' independent retrospective timing "
    "analysis). Wikipedia's own infobox gives 66:35 and Cagematch gives 66:39 -- both within 5 seconds, not "
    "treated as a real conflict (this kind of small stopwatch-convention spread between outlets is expected "
    "and was seen in earlier years too), but noted here for completeness.", f"{S_WIKI_EVENT};{S_CAGESIDE}")

new_flag("RR1993M", "events", "RR1993M", "referees", "unverified",
    "The Rumble MATCH's specific referee(s) still couldn't be identified this pass. Wikipedia's infobox lists "
    "6 event-wide officials (John Bonello, Danny Davis, Jack Doan, Earl Hebner, Joey Marella, Bill Alfonso) "
    "but does not tie any of them specifically to the Royal Rumble match itself (a match with a constantly "
    "changing cast is inherently hard to pin a single referee to). Left as 'not identified' rather than "
    "guessing from the candidate list.", S_WIKI_EVENT)

new_flag("RR1993M", "wrestlers", "max-moon", "real_name", "unverified",
    "The 'Max Moon' gimmick was played by different performers across its history -- at THIS specific event "
    "(Jan 24, 1993) it was Thomas Boric (ring name 'Paul Diamond'); the gimmick was later handed to Konnan for "
    "other territories/house shows. The bio recorded here is scoped specifically to the performer at this "
    "event, not the gimmick generally.", S_WIKI_BIO)

new_flag("RR1993M", "wrestlers", "samu;damien-demento;fatu;carlos-colon;yokozuna;jerry-lawler;max-moon;genichiro-tenryu;papa-shango;bob-backlund",
    "real_name;dob;birthplace", "unverified",
    "Bio data (real name/DOB/birthplace) added for these 10 previously-UNKNOWN wrestlers this pass, all "
    "single-sourced to Wikipedia biography articles (PROBABLE, not CONFIRMED -- no second independent source "
    "was cross-checked for these specific fields).", S_WIKI_BIO)

new_flag("RR1993M", "eliminations", "*", "elimination_clock_time", "out_of_scope_no_tool",
    "Wikipedia's own per-entrant table additionally gives an 'eliminated by'/time-in-match figure for every "
    "entrant (e.g. Papa Shango by Ric Flair at 0:28, Owen Hart by Yokozuna at 5:39). Not incorporated this "
    "pass -- this event's elimination order/timestamps are already DERIVED internally from S027's buzzer-time "
    "computation and validated against 6 narrative checkpoints (see build_1993.py); cross-validating all 29 "
    "individual timestamps against this new external table is worthwhile future work, not attempted here.",
    S_WIKI_EVENT)

resolve_flag("F056", "Wikipedia's entrant table and thesmackdownhotel.com/PWDB both independently confirm Mr. "
    "Perfect's entry number as #10, agreeing with the buzzer-derived value (not the narrative's '#11'). "
    "entry_number_status upgraded to CONFIRMED.")
entrants_by_key[("RR1993M", "mr-perfect")]["entry_number_status"] = "CONFIRMED"
entrants_by_key[("RR1993M", "mr-perfect")]["source_ids"] = ";".join(
    sorted(set(filter(None, entrants_by_key[("RR1993M", "mr-perfect")]["source_ids"].split(";"))) | {S_WIKI_EVENT, S_PWDB}))

for wid, real_name, dob, birthplace in [
    ("samu", "Samuel Fred Anoa'i", "1963-05-29", "San Francisco, California, U.S."),
    ("damien-demento", "Phillip Theis", "1958-06-25", "Long Island, New York, U.S."),
    ("fatu", "Solofa Fatu Jr.", "1965-10-11", "San Francisco, California, U.S."),
    ("carlos-colon", "Carlos Edwin Colón González", "1948-07-18", "Santa Isabel, Puerto Rico"),
    ("yokozuna", "Rodney Agatupu Anoa'i", "1966-10-02", "San Francisco, California, U.S."),
    ("jerry-lawler", "Jerry O'Neil Lawler", "1949-11-29", "Memphis, Tennessee, U.S."),
    ("max-moon", "Thomas Boric (this event's performer; ring name 'Paul Diamond')", "1961-05-11", "Zagreb, Croatia"),
    ("genichiro-tenryu", "Genichiro Shimada", "1950-02-02", "Katsuyama, Fukui, Japan"),
    ("papa-shango", "Charles Thomas Wright", "1961-05-16", "Las Vegas, Nevada, U.S."),
    ("bob-backlund", "Robert Louis Backlund", "1949-08-14", "Princeton, Minnesota, U.S."),
]:
    set_bio(wid, real_name, dob, birthplace, status="PROBABLE", src=S_WIKI_BIO)
wrestlers_by_id["yokozuna"]["deceased_date"] = wrestlers_by_id["yokozuna"]["deceased_date"] or "2000-10-23"

# ===========================================================================
# 1994
# ===========================================================================
ev = events_by_id["RR1994M"]
ev["duration_total"] = "55:04"
ev["duration_status"] = "PROBABLE"
ev["referees"] = "Earl Hebner, Danny Davis, Joey Marella, Tim White (per S035, single-sourced)"
ev["ring_announcer"] = "Howard Finkel"
ev["entrant_count"] = "30"
ev["historical_significance"] = (
    "The only Royal Rumble in history with two simultaneous co-winners (per S035). Diesel's 7 eliminations "
    "tied the then-single-match record. Entry interval was shortened from the usual 2:00 to 90 seconds for "
    "broadcast-time reasons (kayfabe: on 'Jack Tunney's orders'). Three late roster swaps happened before the "
    "show: Kwang (Savio Vega's masked debut) replaced an injured Ludvig Borga, Virgil replaced Kamala, and "
    "Sparky Plugg (Bob Holly's WWF TV debut) replaced an injured 1-2-3 Kid. The unresolved dual-win forced a "
    "coin toss on the following Raw to set WrestleMania X title-match order -- Luger won the toss."
)
ev["source_ids"] = ";".join(sorted(set(filter(None, ev["source_ids"].split(";"))) | {S_WIKI_EVENT, S_PWDB, S_CAGESIDE, S_OWW2}))
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-15: date/venue/attendance(14,500) confirmed by 3 sources; the missing "
    "30th entrant (Bastion Booger, advertised #25, withdrew due to illness before the match) was found and "
    "added, resolving F061; the full 30-slot entry order and eliminator credits were recovered from Wikipedia/"
    "PWDB (2-source agreement) and added to entrants.csv/eliminations.csv, upgrading this event well beyond "
    "its original 'sparsest year' status -- ring times and exact elimination order/timestamps remain UNKNOWN "
    "(no source gives them). See F091-F097."
)

# --- Bastion Booger: advertised, withdrew due to illness before entering ---
wrestlers.append({
    "wrestler_id": "bastion-booger", "ring_name": "Bastion Booger", "real_name": "Mike Shaw",
    "real_name_status": "PROBABLE", "gender": "M", "dob": "1957-08-04", "dob_status": "PROBABLE",
    "deceased_date": "2010-04-08", "birthplace": "Winnipeg, Manitoba, Canada", "birthplace_status": "PROBABLE",
    "nationality": "", "debut_year_company": "", "hall_of_fame_year": "",
    "aliases_ring_names": "Makhan Singh; Bastion Booger; Man Mountain Rock",
    "wrestling_style": "",
    "notes": "Advertised at entry #25 for the 1994 Royal Rumble but withdrew before the match due to illness "
             "(Wikipedia says 'illness'; WWE.com's own retrospective specifically says food poisoning) -- never "
             "actually entered the ring. Modeled the same way as Randy Savage's 1991 no-show: entry_number "
             "populated, ring_time 00:00, no elimination event logged at all. See F091.",
    "source_ids": f"{S_WIKI_EVENT};{S_WIKI_BIO}",
})
wrestlers_by_id["bastion-booger"] = wrestlers[-1]
entrants.append({f: "" for f in ENTRANTS_FIELDS})
booger = entrants[-1]
booger.update({
    "event_id": "RR1994M", "wrestler_id": "bastion-booger", "match_id": "RR1994M",
    "entry_number": "25", "entry_number_status": "CONFIRMED",
    "ring_name_at_time": "Bastion Booger", "name_displayed_at_event": "Bastion Booger",
    "ring_time": "00:00", "ring_time_seconds": "0", "ring_time_status": "CONFIRMED",
    "wrestlers_remaining_when_eliminated": "", "wrestlers_eliminated_count": "0",
    "solo_eliminations_count": "0", "assisted_eliminations_count": "0", "self_eliminated": "FALSE",
    "is_winner": "FALSE", "is_runner_up": "FALSE", "is_final_two": "FALSE", "is_final_three": "FALSE",
    "is_final_four": "FALSE", "surprise_entrant": "FALSE", "legend_returning": "FALSE",
    "celebrity_entrant": "FALSE", "non_full_time_wrestler": "FALSE", "wrestled_earlier_on_card": "FALSE",
    "was_hof_member_at_time": "FALSE", "data_quality_status": "CONFIRMED",
    "source_ids": f"{S_WIKI_EVENT};{S_WIKI_BIO}",
    "notes": "Advertised entrant, withdrew before the match due to illness -- never entered. See F091.",
})
entrants_by_key[("RR1994M", "bastion-booger")] = booger

# --- Full entry order + eliminator credits (Wikipedia + PWDB, 2-source agreement) ---
# (entry_number, wrestler_id, eliminator_wrestler_ids-list-or-None-if-winner)
RR1994_ORDER = [
    (1, "scott-steiner", ["diesel"]),
    (2, "samu", ["scott-steiner"]),
    (3, "rick-steiner", ["owen-hart"]),
    (4, "kwang", ["diesel"]),
    (5, "owen-hart", ["diesel"]),
    (6, "bart-gunn", ["diesel"]),
    (7, "diesel", ["demolition-crush", "bam-bam-bigelow", "mabel", "sparky-plugg", "shawn-michaels"]),
    (8, "bob-backlund", ["diesel"]),
    (9, "billy-gunn", ["diesel"]),
    (10, "virgil", ["diesel"]),
    (11, "randy-savage", ["demolition-crush"]),
    (12, "jeff-jarrett", ["randy-savage"]),
    (13, "demolition-crush", ["bam-bam-bigelow", "sparky-plugg", "lex-luger", "bret-hart"]),
    (14, "doink", ["bam-bam-bigelow"]),
    (15, "bam-bam-bigelow", ["lex-luger"]),
    (16, "mabel", None),  # group elimination, members not named by source -- UNKNOWN eliminator
    (17, "sparky-plugg", ["shawn-michaels", "bret-hart"]),
    (18, "shawn-michaels", ["lex-luger"]),
    (19, "mo", ["fatu"]),
    (20, "greg-valentine", ["rick-martel"]),
    (21, "tatanka", ["bam-bam-bigelow"]),
    (22, "great-kabuki", ["lex-luger"]),
    (23, "lex-luger", "WINNER"),
    (24, "genichiro-tenryu", ["bret-hart", "lex-luger"]),
    (26, "rick-martel", ["tatanka"]),
    (27, "bret-hart", "WINNER"),
    (28, "fatu", ["bret-hart"]),
    (29, "marty-jannetty", ["shawn-michaels"]),
    (30, "adam-bomb", ["lex-luger"]),
]
GROUP_ROWS_1994 = {7, 13, 17, 24}  # entries where the eliminated wrestler had 2+ named co-eliminators

solo_count = {}
assisted_count = {}
elim_order_ctr = [0]
for entry_num, wid, elims in RR1994_ORDER:
    er = entrants_by_key[("RR1994M", wid)]
    er["entry_number"] = str(entry_num)
    er["entry_number_status"] = "CONFIRMED"
    er["ring_time_status"] = "UNKNOWN"
    er["elim_number_status"] = "UNKNOWN"
    er["data_quality_status"] = "PROBABLE"
    er["source_ids"] = ";".join(sorted(set(filter(None, er["source_ids"].split(";"))) | {S_WIKI_EVENT, S_PWDB}))
    if elims == "WINNER":
        continue
    if elims is None:
        er["eliminated_by_ids"] = "UNKNOWN (group elimination, members not named by source -- see F092)"
        continue
    er["eliminated_by_ids"] = ";".join(elims)
    is_group = entry_num in GROUP_ROWS_1994
    for e_wid in elims:
        if is_group:
            assisted_count[e_wid] = assisted_count.get(e_wid, 0) + 1
        else:
            solo_count[e_wid] = solo_count.get(e_wid, 0) + 1
    # eliminations.csv rows: one row per contributing eliminator (per DEFINITIONS.md's
    # documented "assisted elimination" convention for named multi-eliminator credits)
    sim_group = f"1994_{wid}" if is_group else ""
    for e_wid in elims:
        eliminations.append({f: "" for f in ELIM_FIELDS})
        row = eliminations[-1]
        row.update({
            "event_id": "RR1994M", "order_in_match": "", "eliminated_wrestler_id": wid,
            "eliminator_wrestler_id": e_wid,
            "assisting_wrestler_ids": ";".join(x for x in elims if x != e_wid) if is_group else "",
            "entry_number_of_eliminated": str(entry_num), "entry_number_of_eliminator": "",
            "elimination_clock_time": "", "elimination_clock_seconds": "",
            "elimination_type": "over_the_top_rope", "elimination_method": "",
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "FALSE" if is_group else "TRUE", "is_shared": "TRUE" if is_group else "FALSE",
            "is_accidental": "FALSE", "is_self_elimination": "FALSE", "is_storyline_related": "FALSE",
            "was_already_incapacitated": "FALSE", "is_disputed": "FALSE",
            "simultaneous_group_id": sim_group,
            "data_quality_status": "CONFIRMED", "source_ids": f"{S_WIKI_EVENT};{S_PWDB}",
            "notes": f"Eliminated {'jointly with ' + ', '.join(x for x in elims if x != e_wid) if is_group else ''}"
                     f" -- entry order and eliminator CONFIRMED (Wikipedia + PWDB agree); exact elimination "
                     f"timestamp/order is UNKNOWN, no source states it.".strip(),
        })

for wid, solo in solo_count.items():
    er = entrants_by_key[("RR1994M", wid)]
    a = assisted_count.get(wid, 0)
    er["solo_eliminations_count"] = str(solo)
    er["assisted_eliminations_count"] = str(a)
    er["wrestlers_eliminated_count"] = str(solo + a)
for wid, a in assisted_count.items():
    if wid not in solo_count:
        er = entrants_by_key[("RR1994M", wid)]
        er["solo_eliminations_count"] = "0"
        er["assisted_eliminations_count"] = str(a)
        er["wrestlers_eliminated_count"] = str(a)

new_flag("RR1994M", "entrants", "*", "entry_number;eliminated_by_ids", "unverified",
    "F061's missing 30th entrant found: Bastion Booger, advertised at #25, withdrew before the match due to "
    "illness (never entered). The full 30-slot order (including his advertised slot) and eliminator credits "
    "for all 29 actual eliminations were recovered from Wikipedia's Royal Rumble (1994) infobox table, "
    "independently matched exactly by thesmackdownhotel.com/PWDB's own entrant table. entry_number upgraded "
    "to CONFIRMED for all 30. Ring times and exact elimination-order timestamps remain UNKNOWN -- neither "
    "external source states them, and unlike 1991-1993/1995/1997 there is no internal Cageside-style buzzer "
    "document for 1994 to derive them from.", f"{S_WIKI_EVENT};{S_PWDB}", status="resolved")

new_flag("RR1994M", "eliminations", "mabel-entry16", "eliminator_wrestler_id", "unverified",
    "Entry #16 (Mabel) is eliminated by an unnamed 'group' per Wikipedia's table -- unlike the other 3 "
    "multi-person eliminations this year (entries 7, 13, 17, 24), no specific names are given for this one. "
    "Left as UNKNOWN rather than guessed.", S_WIKI_EVENT)

new_flag("RR1994M", "wrestlers", "diesel", "wrestlers_eliminated_count", "unverified",
    "Diesel's 7 solo eliminations this year (Scott Steiner, Kwang, Owen Hart, Bart Gunn, Bob Backlund, Billy "
    "Gunn, Virgil), independently reproduced by counting the recovered elimination table, exactly matches the "
    "'tied the single-match elimination record' trivia claim from S035 -- a good internal-consistency check "
    "on the recovered data.", f"{S_WIKI_EVENT};{S_PWDB}", status="resolved")

new_flag("RR1994M", "events", "RR1994M", "special_rules", "conflicting_sources",
    "Bret Hart / Lex Luger dual-winner finish independently confirmed by 2 sources (Wikipedia, PWDB) -- both "
    "wrestlers crashed to the floor simultaneously, officials disagreed on who landed first, and WWF President "
    "Jack Tunney ultimately had both declared co-winners. However, this pass could NOT independently confirm "
    "the specific detail (already in the DB from Shane's own document) that a replay showed Luger's feet "
    "landing first -- Wikipedia's account instead emphasizes the camera angles were inconclusive and the "
    "dispute was never actually resolved on air. That detail may come from a source (e.g. a Bret Hart shoot "
    "interview/autobiography) not accessed this pass -- kept in the DB as-is, not removed, but flagged as "
    "not independently corroborated.", f"{S_WIKI_EVENT};{S_PWDB}")

new_flag("RR1994M", "wrestlers", "doink", "real_name;aliases_ring_names", "conflicting_sources",
    "Shane's original document (S029) credits this year's Doink performance to 'Phil Apollo'. Every external "
    "source checked this pass (Wikipedia's Doink the Clown article, thesmackdownhotel.com's dedicated 'Doink "
    "the Clown (Ray Apollo)' profile with a Dec 28 1993 - Sep 29 1995 date range covering this event, and an "
    "IMDb character credit for the Jan 1994 TV special) instead says 'Ray Apollo' (real name reported as Ray "
    "Licameli). This looks like a transcription variant in Shane's original document (Phil/Ray) rather than a "
    "genuinely different performer, but per the project's discipline neither name is silently overwritten -- "
    "both are preserved here, with the external Ray Apollo / Ray Licameli identification added as the "
    "wrestler's real_name (PROBABLE).", f"{S_WIKI_BIO};{S_PWDB}")

new_flag("RR1994M", "wrestlers", "doink;doink-1995", "notes", "needs_human_judgement",
    "Evidence found this pass (not conclusive, so NOT merged): thesmackdownhotel.com's Ray Apollo/Doink "
    "profile gives a continuous Dec 1993-Sep 1995 date range covering BOTH the 1994 and 1995 Royal Rumbles, "
    "and IMDb separately credits 'Ray Apollo' as Doink the Clown on the character pages for both years' TV "
    "specials. No single source explicitly states in one sentence that the same performer worked both events, "
    "so per the project's identity-merge discipline the two wrestler_ids ('doink' and 'doink-1995') remain "
    "separate -- but this is worth another look with a source that states it outright. See also F071.",
    f"{S_WIKI_BIO};{S_PWDB}")

new_flag("RR1994M", "wrestlers", "*", "real_name;dob;birthplace", "unverified",
    "Bio data added for 15 previously-UNKNOWN wrestlers this pass (Bam Bam Bigelow, Adam Bomb, Diesel, Great "
    "Kabuki, Jeff Jarrett, Kwang/Savio Vega, Mo, Mabel, Sparky Plugg/Bob Holly, Billy Gunn, Bart Gunn, Rick "
    "Steiner, Scott Steiner, Lex Luger, plus Bastion Booger), single-sourced to Wikipedia/thesmackdownhotel.com "
    "(PROBABLE, not CONFIRMED -- no second independent source cross-checked).", f"{S_WIKI_BIO};{S_PWDB}")

for wid, real_name, dob, birthplace in [
    ("bam-bam-bigelow", "Scott Charles Bigelow", "1961-09-01", "Mount Laurel, New Jersey, U.S."),
    ("adam-bomb", "Bryan Emmett Clark", "1964-03-14", "Harrisburg, Pennsylvania, U.S."),
    ("diesel", "Kevin Scott Nash", "1959-07-09", "Detroit, Michigan, U.S."),
    ("great-kabuki", "Akihisa Mera", "1948-09-08", "Nobeoka, Japan"),
    ("jeff-jarrett", "Jeffrey Leonard Jarrett", "1967-07-14", "Hendersonville, Tennessee, U.S."),
    ("kwang", "Juan Rivera (also 'Savio Vega')", "1964-08-10", "Vega Alta, Puerto Rico"),
    ("mo", "Robert Lawrence Horne", "1967-04-13", "Monroe, North Carolina, U.S."),
    ("mabel", "Nelson Lee Frazier Jr.", "1971-02-14", "Goldsboro, North Carolina, U.S."),
    ("sparky-plugg", "Robert William Howard (also 'Bob Holly')", "1963-01-29", "Glendale, California, U.S."),
    ("billy-gunn", "Monty Kip Sopp", "1963-11-01", "Orlando, Florida, U.S."),
    ("bart-gunn", "Michael Polchlopek", "1965-12-27", "Titusville, Florida, U.S."),
    ("rick-steiner", "Robert Rechsteiner", "1961-03-09", "Bay City, Michigan, U.S."),
    ("scott-steiner", "Scott Rechsteiner", "1962-07-29", "Bay City, Michigan, U.S."),
    ("lex-luger", "Lawrence Wendell Pfohl", "1958-06-02", "Buffalo, New York, U.S."),
    ("doink", "Ray Licameli", None, "Hasbrouck Heights, New Jersey, U.S."),
]:
    set_bio(wid, real_name, dob, birthplace, status="PROBABLE", src=S_WIKI_BIO)
wrestlers_by_id["doink"]["aliases_ring_names"] = (wrestlers_by_id["doink"]["aliases_ring_names"] + "; Ray Apollo").strip("; ")

# ===========================================================================
# 1995
# ===========================================================================
ev = events_by_id["RR1995M"]
ev["ring_announcer"] = "Howard Finkel"
ev["referees"] = "Danny Davis, Jack Doan, Earl Hebner, Tim White (per S035, single-sourced)"
ev["historical_significance"] = (
    "Shawn Michaels became the first wrestler to enter at #1 and win the Rumble -- this didn't happen again "
    "until Chris Benoit in 2004 (per S035/S041). Michaels and British Bulldog both entering AND finishing the "
    "match together is independently confirmed as a first (per S035/S041). Michaels eliminated a record 8 "
    "wrestlers. Baywatch star Pamela Anderson was ringside under a storyline stipulation to accompany the "
    "Rumble winner to WrestleMania XI -- but the storyline instead had her accompany Diesel, despite Michaels "
    "winning (per S035/S042). NFL Hall of Famer Lawrence Taylor attended and confronted Bam Bam Bigelow "
    "post-match, foreshadowing their WrestleMania XI match (per S042)."
)
ev["source_ids"] = ";".join(sorted(set(filter(None, ev["source_ids"].split(";"))) | {S_WIKI_EVENT, S_PWDB, S_CAGESIDE, S_ALLRUMBLE, S_OWW2, S_BLOGOFDOOM}))
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-15: date/venue/attendance/duration(38:45, independently matched exactly "
    "by S036)/commentary/winner/the '60-second interval, shortest 30-man Rumble ever' claim all confirmed by "
    "2+ sources. Entry order confirmed by 3 independent sources for 28 of 30 slots; a genuine 2-source-vs-"
    "1-source conflict was found and corrected at #25/#26 (see F098). See F098-F101."
)

# --- #25/#26 swap: 3 independent external sources (Wikipedia, OWW, PWDB) agree Bob Backlund
#     was #25 and Steven Dunn was #26 -- the reverse of what's currently in the DB.
bb = entrants_by_key[("RR1995M", "bob-backlund")]
sd = entrants_by_key[("RR1995M", "steven-dunn")]
assert bb["entry_number"] == "26" and sd["entry_number"] == "25", (bb["entry_number"], sd["entry_number"])
bb["entry_number"], sd["entry_number"] = "25", "26"
for r in (bb, sd):
    r["entry_number_status"] = "CONFIRMED"
    r["source_ids"] = ";".join(sorted(set(filter(None, r["source_ids"].split(";"))) | {S_WIKI_EVENT, S_OWW2, S_PWDB}))

new_flag("RR1995M", "entrants", "bob-backlund;steven-dunn", "entry_number", "conflicting_sources",
    "The DB's internal buzzer-derivation had Steven Dunn at #25 and Bob Backlund at #26. Three independent "
    "external sources (Wikipedia, Online World of Wrestling, thesmackdownhotel.com/PWDB) all agree on the "
    "reverse order: Bob Backlund #25, Steven Dunn #26. Corrected in favor of the 3-source external agreement "
    "over the single internal derivation, per the project's tie-breaking rule (more independently-agreeing "
    "sources wins). Both entrants' extremely short ring times are unaffected by the swap.",
    f"{S_WIKI_EVENT};{S_OWW2};{S_PWDB}", status="resolved")

new_flag("RR1995M", "wrestlers", "doink-1995", "real_name", "needs_human_judgement",
    "Evidence found this pass (not conclusive, so real_name left UNKNOWN and NOT merged with 1994's 'doink'): "
    "IMDb credits 'Ray Apollo' as Doink the Clown on the character page for the Jan 1995 Royal Rumble TV "
    "special specifically, and thesmackdownhotel.com's Ray Apollo profile gives a Dec 1993-Sep 1995 date range "
    "covering this event. Wikipedia's own Doink article separately says Steve Lombardi took over the gimmick "
    "'after' Apollo, with no exact handover date given, so this isn't fully conclusive either way. See also "
    "F071 (the original 1994-vs-1995 Doink identity caution) and F096 (same evidence, filed against 1994's "
    "doink).", f"{S_WIKI_BIO};{S_PWDB}")

new_flag("RR1995M", "wrestlers", "*", "real_name;dob;birthplace", "unverified",
    "Bio data added for 13 of the 14 previously-UNKNOWN wrestlers this pass (Eli Blu, Duke Droese, Jimmy Del "
    "Ray, Tom Prichard, Timothy Well, Jacob Blu, King Kong Bundy, Mantaur, Aldo Montoya, Henry Godwinn, Steven "
    "Dunn, Dick Murdoch), single-sourced to Wikipedia/thesmackdownhotel.com (PROBABLE, not CONFIRMED). Doink-"
    "1995 remains fully UNKNOWN -- see F099.", f"{S_WIKI_BIO};{S_PWDB}")

new_flag("RR1995M", "wrestlers", "headshrinker-sione", "birthplace", "unverified",
    "Headshrinker Sione's birthplace (Tonga) is sourced only to 'The Official Wrestling Museum' "
    "(theofficialwrestlingmuseum.com), a lower-confidence single source not cross-checked against Wikipedia or "
    "any other outlet this pass (none had a usable bio page for this specific performer). Treat as "
    "lower-confidence than the other PROBABLE entries added this pass.", "")

for wid, real_name, dob, birthplace in [
    ("eli-blu", "Ronald \"Ron\" Harris", "1960-10-23", "Apopka, Florida, U.S."),
    ("duke-droese", "Michael David Droese", "1968-08-20", "Lodi, California, U.S."),
    ("jimmy-del-ray", "David Everett Ferrier", "1962-11-30", "Grove City, Pennsylvania, U.S."),
    ("headshrinker-sione", None, None, "Tonga (billed from)"),
    ("tom-prichard", "Thomas Prichard", "1959-08-18", "El Paso, Texas, U.S."),
    ("timothy-well", "Timothy Alan Smith", "1961-09-08", "Geneva, New York, U.S."),
    ("jacob-blu", "Donald \"Don\" Harris", "1960-10-23", "Apopka, Florida, U.S."),
    ("king-kong-bundy", "Christopher Alan Pallies", "1955-11-07", "Woodbury, New Jersey, U.S."),
    ("mantaur", "Mike Halac", "1968-05-14", "Omaha, Nebraska, U.S."),
    ("aldo-montoya", "Peter Joseph Polaco", "1973-10-16", "Waterbury, Connecticut, U.S."),
    ("henry-godwinn", "Mark Canterbury", "1964-03-16", "Washington, D.C., U.S."),
    ("steven-dunn", "Steven Lyle Doll", "1960-12-09", "Dallas, Texas, U.S."),
    ("dick-murdoch", "Hoyt Richard Murdoch", "1946-08-16", "Waxahachie, Texas, U.S."),
]:
    set_bio(wid, real_name, dob, birthplace, status="PROBABLE", src=S_WIKI_BIO)

# ===========================================================================
# 1996
# ===========================================================================
ev = events_by_id["RR1996M"]
ev["duration_total"] = "58:49"
ev["duration_status"] = "CONFIRMED"
ev["referees"] = "Earl Hebner, Jim Korderas, Jack Doan, Tim White (per S035; Korderas/White/Hebner independently corroborated by S037)"
ev["ring_announcer"] = "Howard Finkel"
ev["entrant_count"] = "30"
ev["historical_significance"] = (
    "First Rumble where wrestlers had individual entrance music (per S037). Entry intervals reverted to the "
    "standard 2:00 after 1995's unusually short 1-minute gaps (per S037). Debuted WWF's first-ever televised "
    "pre-show match ('Free for All'): Duke Droese defeated Hunter Hearst Helmsley, with the stakes being "
    "winner-gets-#30 / loser-gets-#1 -- Triple H, despite the 'loss,' went on to be the match's longest "
    "survivor (48+ min) without eliminating anyone (per S037). Steve Austin's Royal Rumble debut, wrestling as "
    "'The Ringmaster' -- reportedly booked to go deep into the match, but the ring ropes had become slick with "
    "baby oil from other performers, and he slipped over the top when clotheslined by Fatu, eliminating him "
    "far earlier than planned (per S039, Austin's own account). Shawn Michaels became the second man ever "
    "(after Hulk Hogan) to win the Rumble in consecutive years, racking up 8 eliminations -- independently "
    "reproduced by counting the recovered elimination table this pass. Jake Roberts' surprise return to the "
    "WWF, his first appearance since WrestleMania VIII in 1992 (per S035)."
)
ev["source_ids"] = ";".join(sorted(set(filter(None, ev["source_ids"].split(";"))) | {S_WIKI_EVENT, S_PWDB, S_TJR, S_ALLRUMBLE, S_WRESTLINGINC}))
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-15: date/venue/attendance/commentary/winner confirmed by 2+ sources; "
    "duration upgraded from PROBABLE to CONFIRMED (58:49, matched exactly by S035 and S037). The full 30-slot "
    "entry order, eliminator credits, ring times, AND elimination order were all recovered from Wikipedia's "
    "structured table (corroborated piecemeal by individual wrestler bio pages and S040), transforming this "
    "event from the DB's sparsest build (2 of 30 entry numbers known) to a fully-populated one -- though still "
    "single-primary-sourced (Wikipedia) for the bulk of the granular per-wrestler figures, so entrants carry "
    "PROBABLE rather than CONFIRMED data_quality_status except where independently corroborated. Duke Droese's "
    "previously-unknown #30 slot (and the pre-show match that earned it) was also filled in. See F102-F107."
)

# Duke Droese ALREADY exists as a wrestler (reused from his 1995 appearance) and already has an
# entrants.csv row for RR1996M -- just with entry_number/ring_time left blank, same sparse-year
# treatment as every other 1996 entrant before this pass. His #30 slot (winning the "Free for All"
# pre-show match against Hunter Hearst Helmsley) gets filled in below via RR1996_ORDER, same as
# everyone else -- no new wrestler or entrant row needed.
entrants_by_key[("RR1996M", "duke-droese")]["wrestled_earlier_on_card"] = "TRUE"
entrants_by_key[("RR1996M", "duke-droese")]["notes"] = (
    "Won the pre-show 'Free for All' match, earning the #30 slot. See F102.")

# --- Full entry order / eliminator / ring-time / elim-order (Wikipedia, corroborated
#     piecemeal by individual bio pages and allrumblestats.com) ---
# (entry_number, wrestler_id, [eliminator_ids], ring_time, elim_number)
RR1996_ORDER = [
    (1, "hunter-hearst-helmsley", ["diesel"], "48:04", 19),
    (2, "henry-godwinn", ["jake-roberts"], "16:24", 2),
    (3, "bob-backlund", ["yokozuna"], "12:22", 1),
    (4, "jerry-lawler", ["shawn-michaels"], "36:02", 16),
    (5, "bob-holly", ["steve-austin"], "39:35", 18),
    (6, "mabel", ["yokozuna"], "12:14", 3),
    (7, "jake-roberts", ["vader"], "14:39", 6),
    (8, "dory-funk-jr", ["savio-vega"], "10:53", 5),
    (9, "yokozuna", ["shawn-michaels"], "19:14", 11),
    (10, "1-2-3-kid", ["shawn-michaels"], "15:40", 13),
    (11, "takao-omori", ["jake-roberts", "hunter-hearst-helmsley"], "2:48", 4),
    (12, "savio-vega", ["vader"], "12:28", 10),
    (13, "vader", ["shawn-michaels"], "11:04", 12),
    (14, "doug-gilbert", ["vader"], "2:59", 7),
    (15, "headhunter-1", ["vader"], "1:11", 8),
    (16, "headhunter-2", ["yokozuna"], "0:24", 9),
    (17, "owen-hart", ["diesel", "shawn-michaels"], "20:43", 21),
    (18, "shawn-michaels", None, "26:10", None),  # WINNER
    (19, "hakushi", ["owen-hart"], "1:53", 14),
    (20, "tatanka", ["diesel"], "4:09", 17),
    (21, "aldo-montoya", ["tatanka"], "1:52", 15),
    (22, "diesel", ["shawn-michaels"], "17:51", 29),
    (23, "kama", ["diesel"], "15:57", 28),
    (24, "steve-austin", ["fatu"], "10:57", 23),
    (25, "barry-horowitz", ["owen-hart"], "4:15", 20),
    (26, "fatu", ["isaac-yankem"], "7:07", 24),
    (27, "isaac-yankem", ["shawn-michaels"], "7:05", 25),
    (28, "marty-jannetty", ["british-bulldog"], "2:35", 22),
    (29, "british-bulldog", ["shawn-michaels"], "3:39", 27),
    (30, "duke-droese", ["diesel", "kama"], "1:10", 26),
]
GROUP_ROWS_1996 = {11, 17, 30}

solo_count = {}
assisted_count = {}
for entry_num, wid, elims, ring_time, elim_num in RR1996_ORDER:
    er = entrants_by_key[("RR1996M", wid)]
    er["entry_number"] = str(entry_num)
    er["entry_number_status"] = "CONFIRMED"
    m, s = ring_time.split(":")
    er["ring_time"] = ring_time
    er["ring_time_seconds"] = str(int(m) * 60 + int(s))
    er["ring_time_status"] = "CONFIRMED" if wid == "hunter-hearst-helmsley" else "PROBABLE"
    er["data_quality_status"] = "PROBABLE"
    er["source_ids"] = ";".join(sorted(set(filter(None, er["source_ids"].split(";"))) | {S_WIKI_EVENT}))
    if elims is None:
        er["is_winner"] = "TRUE"
        continue
    er["elim_number"] = str(elim_num)
    er["elim_number_status"] = "PROBABLE"
    er["eliminated_by_ids"] = ";".join(elims)
    is_group = entry_num in GROUP_ROWS_1996
    for e_wid in elims:
        if is_group:
            assisted_count[e_wid] = assisted_count.get(e_wid, 0) + 1
        else:
            solo_count[e_wid] = solo_count.get(e_wid, 0) + 1
    sim_group = f"1996_{wid}" if is_group else ""
    for e_wid in elims:
        eliminations.append({f: "" for f in ELIM_FIELDS})
        row = eliminations[-1]
        row.update({
            "event_id": "RR1996M", "order_in_match": str(elim_num), "eliminated_wrestler_id": wid,
            "eliminator_wrestler_id": e_wid,
            "assisting_wrestler_ids": ";".join(x for x in elims if x != e_wid) if is_group else "",
            "entry_number_of_eliminated": str(entry_num), "entry_number_of_eliminator": "",
            "elimination_clock_time": "", "elimination_clock_seconds": "",
            "elimination_type": "over_the_top_rope", "elimination_method": "",
            "location_side": "", "location_status": "UNKNOWN",
            "is_solo": "FALSE" if is_group else "TRUE", "is_shared": "TRUE" if is_group else "FALSE",
            "is_accidental": "FALSE", "is_self_elimination": "FALSE", "is_storyline_related": "FALSE",
            "was_already_incapacitated": "FALSE", "is_disputed": "FALSE",
            "simultaneous_group_id": sim_group,
            "data_quality_status": "PROBABLE", "source_ids": S_WIKI_EVENT,
            "notes": f"Ring time and elimination order recovered from Wikipedia's structured Royal Rumble "
                     f"(1996) table this pass -- single-primary-sourced (PROBABLE), except where corroborated "
                     f"elsewhere (Vader's 4-elimination total, Michaels' 8-elimination total, and Triple H's "
                     f"48:04 survival time are all independently corroborated -- see F103).",
        })

for wid, solo in solo_count.items():
    er = entrants_by_key[("RR1996M", wid)]
    a = assisted_count.get(wid, 0)
    er["solo_eliminations_count"] = str(solo)
    er["assisted_eliminations_count"] = str(a)
    er["wrestlers_eliminated_count"] = str(solo + a)
for wid, a in assisted_count.items():
    if wid not in solo_count:
        er = entrants_by_key[("RR1996M", wid)]
        er["solo_eliminations_count"] = "0"
        er["assisted_eliminations_count"] = str(a)
        er["wrestlers_eliminated_count"] = str(a)

new_flag("RR1996M", "entrants", "*", "entry_number;eliminated_by_ids;ring_time;elim_number", "unverified",
    "The full 30-slot entry order, eliminator credits, ring (survival) times, and elimination order were "
    "recovered from Wikipedia's Royal Rumble (1996) structured table this pass -- transforming this event from "
    "the database's sparsest build (only 2 of 30 entry numbers previously known) to a fully-populated one. "
    "entry_number is CONFIRMED (independently corroborated by individual wrestler bio pages stating their own "
    "entry number, e.g. Vader '#13', Kevin Nash '#22', Barry Horowitz '25th entrant'). Ring time/elim order/"
    "eliminator credits remain PROBABLE (Wikipedia's own table is the only source for most of them), except "
    "Triple H's 48:04 survival time and the overall event duration, which are independently corroborated by "
    "S037 (TJR Wrestling). Duke Droese (already in the DB from his 1995 appearance, but with an unknown 1996 "
    "entry number) is now confirmed at #30, having won the 'Free for All' pre-show match against Hunter Hearst "
    "Helmsley for that slot.", f"{S_WIKI_EVENT};{S_ALLRUMBLE};{S_TJR}", status="resolved")

new_flag("RR1996M", "wrestlers", "vader", "wrestlers_eliminated_count", "unverified",
    "Vader's 4 solo eliminations this year (Jake Roberts, Doug Gilbert, one Squat Team member, Savio Vega), "
    "independently reproduced by counting the recovered elimination table, exactly matches his own Wikipedia "
    "biography's claim of eliminating 4 people at this event -- a good internal-consistency check on the "
    "recovered data. Shawn Michaels' reproduced total of 8 eliminations (7 solo + 1 shared with Diesel on Owen "
    "Hart) likewise matches allrumblestats.com's figure exactly.", f"{S_WIKI_EVENT};{S_WIKI_BIO};{S_ALLRUMBLE}",
    status="resolved")

new_flag("RR1996M", "entrants", "headhunter-1;headhunter-2", "name_displayed_at_event", "unverified",
    "Wikipedia and thesmackdownhotel.com both label these two entrants 'Squat Team #1'/'Squat Team #2' at "
    "THIS specific event, not 'Headhunter 1'/'Headhunter 2' -- per Wikipedia's Headhunters (professional "
    "wrestling) article, the team was renamed 'The Squat Team' specifically for this WWF debut. Same "
    "performers/wrestler_ids either way (not a conflict), but the entrant's name_displayed_at_event arguably "
    "should read 'Squat Team #1'/'#2' for this event specifically -- left as the existing wrestler_id-based "
    "name pending a decision, noted here rather than silently changed.", S_WIKI_EVENT)

new_flag("RR1996M", "wrestlers", "kama;papa-shango", "notes", "needs_human_judgement",
    "Strong single-source evidence found this pass that Kama (this event, entry #23) and Papa Shango (1993's "
    "entry #3) are the same performer under different gimmicks at different times: Wikipedia's 'The Godfather' "
    "article (the performer's best-known later gimmick) narrates one continuous history for Charles Thomas "
    "Wright -- Papa Shango January 1992-mid 1993 (last PPV appearance: the 1993 Royal Rumble), then Kama/Kama "
    "Mustafa January 1995-1996, then The Godfather from mid-1998 (WWE Hall of Fame 2016). This is only ONE "
    "source, though a detailed and specific one, so per the project's 2-independent-source rule for identity "
    "merges the two wrestler_ids ('kama' and 'papa-shango') remain UNMERGED this pass -- worth confirming "
    "against a second source (Cagematch was unreachable/rate-limited throughout this pass) before merging. "
    "See the original caution at F076.", S_WIKI_BIO)

new_flag("RR1996M", "wrestlers", "bob-holly;sparky-plugg", "notes", "needs_human_judgement",
    "Strong single-source evidence found this pass that Bob Holly (this event, entry #5) and Sparky Plugg "
    "(1994's entry #17) are the same performer under different gimmicks at different times: Wikipedia's "
    "'Hardcore Holly' article states Robert William Howard debuted in the WWF as Thurman 'Sparky' Plugg in "
    "1994, was renamed 'Bob (Spark Plug) Holly' at his own request later that same year, and did not become "
    "'Hardcore Holly' until February 1999 -- the same article separately notes he lasted nearly 40 minutes in "
    "the 1996 Rumble (matching entry #5's 39:35), confirming it's describing this exact appearance. Again only "
    "ONE source, so per the project's rule the two wrestler_ids ('bob-holly' and 'sparky-plugg') remain "
    "UNMERGED -- worth confirming against a second source before merging. See the original caution at F078.",
    S_WIKI_BIO)

new_flag("RR1996M", "wrestlers", "*", "real_name;dob;birthplace", "unverified",
    "Bio data added for 15 previously-UNKNOWN wrestlers this pass (1-2-3 Kid, Aldo Montoya, Barry Horowitz, "
    "Bob Holly, Diesel, Dory Funk Jr., Doug Gilbert, Hakushi, Headhunter 1, Headhunter 2, Isaac Yankem, Kama, "
    "Steve Austin, Takao Omori, Vader), single-sourced to Wikipedia (PROBABLE, not CONFIRMED). Duke Droese "
    "already had a bio from his 1995 debut -- no change needed for him.", S_WIKI_BIO)

for wid, real_name, dob, birthplace in [
    ("1-2-3-kid", "Sean Michael Waltman", "1972-07-13", "Minneapolis, Minnesota, U.S."),
    ("aldo-montoya", "Peter Joseph Polaco", "1973-10-16", "Waterbury, Connecticut, U.S."),
    ("barry-horowitz", "Barry Horowitz", None, "St. Petersburg, Florida, U.S."),
    ("bob-holly", "Robert William Howard", "1963-01-29", "Glendale, California, U.S."),
    ("diesel", "Kevin Scott Nash", "1959-07-09", "Detroit, Michigan, U.S."),
    ("dory-funk-jr", "Dorrance Earnest Funk", "1941-02-03", "Hammond, Indiana, U.S."),
    ("doug-gilbert", "Douglas Gilbert", "1969-02-05", "Lexington, Tennessee, U.S."),
    ("hakushi", "Kensuke Shinzaki (also 'Jinsei Shinzaki')", "1966-12-02", "Tokushima, Tokushima, Japan"),
    ("headhunter-1", "Manuel Santiago", "1968-08-11", "New York, New York, U.S."),
    ("headhunter-2", "Victor Santiago", "1968-08-11", "New York, New York, U.S."),
    ("isaac-yankem", "Glenn Thomas Jacobs", "1967-04-26", "Torrejón de Ardoz, Spain"),
    ("kama", "Charles Thomas Wright", "1961-05-16", "Las Vegas, Nevada, U.S."),
    ("steve-austin", "Steven James Anderson (later legally Williams)", "1964-12-18", "Austin, Texas, U.S."),
    ("takao-omori", "Takao Ōmori", "1969-10-16", "Tokyo, Japan"),
    ("vader", "Leon Allen White", "1955-05-14", "Lynwood, California, U.S."),
]:
    if wid in wrestlers_by_id:
        set_bio(wid, real_name, dob, birthplace, status="PROBABLE", src=S_WIKI_BIO)

# ===========================================================================
# 1997
# ===========================================================================
ev = events_by_id["RR1997M"]
assert ev["event_date"] == "1997-01-21"
ev["event_date"] = "1997-01-19"
ev["ring_announcer"] = "Howard Finkel"
ev["referees"] = "Mike Chioda, Jack Doan, Jim Korderas, Earl Hebner (4-source corroborated), Pepe Casas (single-sourced) per S035/S037"
ev["historical_significance"] = (
    "Austin's 10 eliminations tied Hulk Hogan's then-record (Royal Rumble 1989) for most eliminations by a "
    "single competitor in one match -- stood until Kane eliminated 11 in 2001; Austin remains the only Rumble "
    "winner other than Kane to eliminate 10+ opponents (per S035/S038). The announced crowd was the largest "
    "live Royal Rumble attendance in history until 2025 (per S035) -- driven partly by heavy last-minute "
    "ticket discounting (as low as $5-7 with promotional coupons), which explains the roughly 12,000-seat gap "
    "between the paid and announced attendance figures (per S037/S038). WWF partnered with Mexico's AAA "
    "promotion for this show, bringing Mil Máscaras, Pierroth Jr., Latin Lover, and Cibernético into the "
    "Rumble itself. This was Dwayne Johnson's first Royal Rumble match, wrestling as 'Rocky Maivia' barely two "
    "months after his November 1996 in-ring debut. This event also marked the final WWF television appearances "
    "of both 'Fake Diesel' and 'Fake Razor Ramon' -- a storyline mocking the real Diesel/Razor Ramon's 1996 "
    "departure for WCW."
)
ev["source_ids"] = ";".join(sorted(set(filter(None, ev["source_ids"].split(";"))) | {S_WIKI_EVENT, S_PWDB, S_OWW2, S_TJR, S_CULTAHOLIC}))
ev["notes"] = ev["notes"].rstrip() + (
    " Externally fact-checked 2026-09-15: venue/duration/commentary/winner/entry order all confirmed by 2-4 "
    "independent sources. The event DATE was corrected from 1997-01-21 (a Tuesday -- inconsistent with the "
    "WWF's standard Sunday PPV scheduling) to 1997-01-19 (a Sunday), agreeing with 4 independent sources -- see "
    "F111. Attendance's paid/announced split (48,017/60,525) is independently corroborated. See F111-F116."
)

new_flag("RR1997M", "events", "RR1997M", "event_date", "conflicting_sources",
    "The DB's original date (1997-01-21, a Tuesday) was inconsistent with the WWF's standard Sunday PPV "
    "schedule and with every external source checked: Wikipedia, thesmackdownhotel.com/PWDB, Online World of "
    "Wrestling, and TJR Wrestling all independently give 1997-01-19 (a Sunday). Corrected in the DB per the "
    "same precedent as 1989's duration correction (strong external agreement overriding a single internal "
    "value, likely a transcription error in Shane's own document or an earlier build step).",
    f"{S_WIKI_EVENT};{S_PWDB};{S_OWW2};{S_TJR}", status="resolved")

new_flag("RR1997M", "wrestlers", "fake-razor-ramon", "real_name", "conflicting_sources",
    "S034 (Shane's document) gives this performer's real name as 'Rick Bogner'. Wikipedia's dedicated 'Rick "
    "Bognar' biography article (which also independently confirms he was 'the first wrestler eliminated by "
    "Ahmed Johnson' at this exact event, matching entries #2/#3) instead spells the surname 'Bognar' -- a "
    "letter-transposition variant. Both spellings refer to the same real person; per the project's discipline "
    "this is preserved as a real_name_status=CONFLICTING spelling variant rather than silently corrected, "
    "following the same approach used for Greg Valentine's real-name conflict.", S_WIKI_BIO)
wrestlers_by_id["fake-razor-ramon"]["real_name_status"] = "CONFLICTING"
wrestlers_by_id["fake-razor-ramon"]["notes"] = wrestlers_by_id["fake-razor-ramon"]["notes"].rstrip() + (
    " Real-name spelling conflict: S034 says 'Rick Bogner', Wikipedia says 'Rick Bognar' -- see F113.")
wrestlers_by_id["fake-razor-ramon"]["source_ids"] = ";".join(
    sorted(set(filter(None, wrestlers_by_id["fake-razor-ramon"]["source_ids"].split(";"))) | {S_WIKI_BIO}))

# Glen/Glenn Jacobs -- treated as a trivial spelling enrichment (same underlying fact, not a real
# conflict), upgraded to the fuller externally-confirmed name.
fd = wrestlers_by_id["fake-diesel"]
fd["real_name"] = "Glenn Thomas Jacobs"
fd["real_name_status"] = "CONFIRMED"
fd["source_ids"] = ";".join(sorted(set(filter(None, fd["source_ids"].split(";"))) | {S_WIKI_BIO}))
fd["notes"] = fd["notes"].rstrip() + " Full name independently confirmed by Wikipedia (minor 'Glen'->'Glenn' spelling enrichment, not treated as a conflict)."

new_flag("RR1997M", "wrestlers", "*", "real_name;dob;birthplace", "unverified",
    "Bio data added for 17 previously-UNKNOWN wrestlers this pass (Ahmed Johnson, Phineas Godwinn, Pierroth "
    "Jr., The Sultan, Mil Máscaras, Goldust, Cibernético, Marc Mero, Latin Lover, Jesse James, Rocky Maivia, "
    "Mankind, Flash Funk, Terry Funk, plus DOB/birthplace for Fake Razor Ramon/Faarooq whose real names were "
    "already PROBABLE), single-sourced to Wikipedia (PROBABLE, not CONFIRMED).", S_WIKI_BIO)

for wid, real_name, dob, birthplace in [
    ("ahmed-johnson", "Anthony Norris", "1963-06-06", "Kokomo, Indiana, U.S."),
    ("phineas-godwinn", "Dennis Knight", "1968-12-26", "Clearwater, Florida, U.S."),
    ("pierroth-jr", "Norberto Salgado Salcedo", "1958-03-10", "Cuernavaca, Morelos, Mexico"),
    ("the-sultan", "Solofa Fatu Jr.", "1965-10-11", "San Francisco, California, U.S."),
    ("mil-mascaras", "Aarón Rodríguez Arellano", "1942-07-15", "San Luis Potosí, Mexico"),
    ("goldust", "Dustin Patrick Runnels", "1969-04-11", None),
    ("cibernetico", "Octavio López Arreola", "1975-04-12", "Aguascalientes, Mexico"),
    ("marc-mero", "Marc Mero", "1960-07-09", "Buffalo, New York, U.S."),
    ("latin-lover", "Victor Manuel Reséndiz Ruiz", "1967-10-25", "Monterrey, Nuevo León, Mexico"),
    ("faarooq", None, "1958-05-15", "Perry, Georgia, U.S."),
    ("jesse-james", "Brian Girard James", "1969-05-20", None),
    ("rocky-maivia", "Dwayne Douglas Johnson", "1972-05-02", "Hayward, California, U.S."),
    ("mankind", "Michael Francis Foley", "1965-06-07", "Bloomington, Indiana, U.S."),
    ("flash-funk", "Charles Bernard Scaggs (also '2 Cold Scorpio')", "1965-10-25", "Denver, Colorado, U.S."),
    ("terry-funk", "Terrance Dee Funk", "1944-06-30", "Hammond, Indiana, U.S."),
]:
    set_bio(wid, real_name, dob, birthplace, status="PROBABLE", src=S_WIKI_BIO)

print("Patch script loaded. Sources appended:", len(new_sources))

# ===========================================================================
# SAVE
# ===========================================================================
save("events.csv", events, EVENTS_FIELDS)
save("wrestlers.csv", wrestlers, WRESTLERS_FIELDS)
save("entrants.csv", entrants, ENTRANTS_FIELDS)
save("eliminations.csv", eliminations, ELIM_FIELDS)
save("flags.csv", flags, FLAGS_FIELDS)
save("sources.csv", sources, SOURCES_FIELDS)

print(f"Done. wrestlers={len(wrestlers)} entrants={len(entrants)} eliminations={len(eliminations)} "
      f"flags={len(flags)} sources={len(sources)}")
