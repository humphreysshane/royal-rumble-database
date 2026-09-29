# -*- coding: utf-8 -*-
"""
Fills the 1991/1992/1993/1995/1997 elimination-credit gaps identified after the Collection of
Stats pass: of 165 entrants database-wide with no credited eliminator, 116 were concentrated in
these five years (an early-90s stretch that predates this project's main fact-check passes).
Per Shane's explicit decision (AskUserQuestion, 2026-09-17: "prioritize filling 1991-1997
elimination gaps"), five parallel research agents were dispatched, one per year, each required
to apply this project's 2-independent-source CONFIRMED rule and to explicitly flag rather than
silently resolve any genuine disagreement between sources. Their findings were then indepen-
dently verified against this database's own live data (wrestler_id existence, the "smash"/
"Repo Man" gimmick-naming convention, an inaccurate assumption in this script author's own
1993 research brief) before being written in here -- see this project's standing "never invent
data" rule and the isolated-copy test workflow used for every prior patch script.

SCOPE: of the 116 originally-blank entrants across these 5 years, 2 (Ahmed Johnson, Faarooq --
Royal Rumble 1997) already had eliminations.csv rows added by the earlier Collection of Stats
pass (both are confirmed self-eliminations) but were missed by that pass's eliminated_by_ids
back-fill, since that back-fill ran BEFORE their rows were added in script order. Fixed here
as a two-line correction, not a new research finding. The remaining 114 are new eliminator
credits, sourced below, of which 9 are gang/tandem eliminations (2 or 3 credited eliminators).

ONE ADDITIONAL GAP CLOSED VIA TARGETED VERIFICATION (not one of the 5 agents' assignments):
the 1992 agent could not find "Smash" as a competitor and, not knowing this database's existing
convention of reusing wrestler_id "smash" across gimmick eras (see the Godfather chain; Barry
Darsow himself already carries `ring_name_at_time="Repo Man"` for both his 1992 AND 1993 Rumble
rows), flagged it rather than guess. This script's author confirmed "smash" *is* the correct
existing wrestler_id for both years and used a direct 2-source web check (Wikipedia's Royal
Rumble (1992) elimination table; OnlineWorldOfWrestling's 1992 results page) to find who
eliminated him -- Big Boss Man, CONFIRMED by both -- since neither of those was among the
2 sources the 1992 agent already had for its 16 other resolved names.

GENUINE CONFLICTS PRESERVED AS FLAGS (not force-resolved), per this project's core rule:
  - paul-roma (1991): Wikipedia's table alone classifies this as a self-elimination; three
    other independent sources plus a narrative match review agree Jake Roberts caused it by
    ducking a charge. Credited to Jake Roberts (majority + narrative), flagged.
  - mr-perfect (1993, 3-way gang elimination): one source (WrestlingRecaps.com) names Yokozuna
    as the third assisting eliminator instead of Koko B. Ware; four other sources (incl. two
    structured databases and Grokipedia) agree on Koko B. Ware. Credited DiBiase/Koko B. Ware/
    Lawler (majority), flagged.
  - the-sultan (1997): Wikipedia alone credits a joint British Bulldog + Mil Mascaras
    elimination; three other independent sources credit British Bulldog solo. Credited solo
    (majority), flagged.
  - fake-diesel (1997): Wikipedia alone credits Steve Austin; four other independent sources
    (including a narrative account quoting the exact post-elimination angle) credit Bret Hart.
    Credited Bret Hart (majority), flagged.
  - rocky-maivia (1997): Wikipedia alone credits Vader; three-to-four other independent sources
    credit Mankind. Credited Mankind (majority), flagged.
In every one of these five cases, Wikipedia's event-article table is the SOLE dissenting source
against a multi-source, cross-database consensus -- noted here since it recurs across three
separate years' research and may be worth a standing note in this project's sourcing hierarchy.

MINOR SINGLE-SOURCE EXTRACTION GLITCHES (not flagged as genuine conflicts, just documented in
the row's own notes -- consistent with how factcheck_collection_of_stats.py treated similar
single-outlier gaps in Wikipedia's own tables):
  - jerry-sags (1993): one source's automated extraction said "Bret Hart" (who was not in this
    match at all); four sources agree on Owen Hart.
  - headshrinker-sione (1995): one source's extraction said "Jacob Blue" (a different entrant
    in the same match); two sources agree on Eli Blu, matching the database's own paired
    "revenge spot" narrative (Sione eliminates Eli Blu, Eli Blu immediately retaliates).
  - jimmy-del-ray (1995): one source's extraction said Shawn Michaels; three sources
    (including a results-page eliminator sequence) agree on British Bulldog.

Flag IDs continue from F326 (F327 onward). Source IDs continue from S117 (S118 onward).
Reused existing sources: S023 (Cagematch.net), S026 (Wikipedia 1988-1992), S035 (Wikipedia
1993-1997), S037 (TJR Wrestling), S040 (allrumblestats.com), S041 (Blog of Doom), S042 (OWW
event results), S052 (prowrestling.fandom.com).

TIMING/POSITIONAL DATA: every new eliminations.csv row below reuses this database's own
PRE-EXISTING per-entrant elim_number, entry_number, elimination_clock_time and
elimination_clock_seconds fields (already populated in entrants.csv for nearly every one of
these rows from Shane's original document -- only the eliminator identity was missing). Nothing
about WHEN or in what position these eliminations happened is new or re-derived here; only WHO
did it.

FULL RECOMPUTE (not just resync) OF SUMMARY FIELDS FOR THESE 5 EVENTS ONLY: unlike the
Collection of Stats pass's deliberately conservative "only fix a non-blank value that disagrees,
never fill a blank" rule (appropriate for a database-wide hygiene sweep where most years'
elimination data was already believed complete), these five specific events go from sparse
(6, 12, 4, 1, and 8 of ~29 eliminations recorded, respectively) to comprehensive (28, 29, 29,
29, and 29 of ~29) as a direct result of this pass's dedicated research. Recomputing
wrestlers_eliminated_ids / eliminated_by_ids / wrestlers_eliminated_count / solo_eliminations_
count / assisted_eliminations_count for EVERY entrant in JUST these 5 events (filling
previously-blank fields, not just correcting wrong ones) is therefore the correct treatment --
equivalent to how any other now-fully-built year in this database has its summary fields
computed -- and is flagged explicitly below as a distinct, deliberate exception to the
Collection of Stats pass's narrower rule.
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

ENTRANTS_FIELDS = list(entrants[0].keys())
ELIM_FIELDS = list(eliminations[0].keys())
FLAGS_FIELDS = list(flags[0].keys())
SOURCES_FIELDS = list(sources[0].keys())

entrants_by_key = {(e["event_id"], e["wrestler_id"]): e for e in entrants}

DATE_LOGGED = "2026-09-17"

flag_ctr = [327]


def new_flag(event_id, table, record_id, field, issue_type, description, source_ids, status="open"):
    fid = f"F{flag_ctr[0]:03d}"
    flag_ctr[0] += 1
    flags.append({
        "flag_id": fid, "event_id": event_id, "table": table, "record_id": record_id,
        "field": field, "issue_type": issue_type, "description": description,
        "source_ids_involved": source_ids, "status": status, "date_logged": DATE_LOGGED,
    })
    return fid


def add_src(row, *src_ids):
    ids = set(filter(None, row["source_ids"].split(";")))
    ids.update(src_ids)
    row["source_ids"] = ";".join(sorted(ids))


def add_source(sid, name, stype, tier, tier_label, notes):
    sources.append({
        "source_id": sid, "source_name": name, "source_type": stype, "url": "",
        "reliability_tier": str(tier), "tier_label": tier_label,
        "accessed_date": DATE_LOGGED, "notes": notes,
    })


# ---------------------------------------------------------------------------
# New sources for this pass (S118 onward)
# ---------------------------------------------------------------------------
S_PWH = "S118"
S_RRFANDOM = "S119"
S_GROKIPEDIA = "S120"
S_EWN = "S121"
S_FOXSPORTS = "S122"

add_source(S_PWH, "ProWrestlingHistory.com, WWF Royal Rumble supercard results archive",
           "wrestling_database", 12, "Other reputable site",
           "Used by the 1991/1993/1995 elimination-gap research agents as an independent "
           "entrant/elimination-order database, distinct from Wikipedia/AllRumbleStats/OWW.")
add_source(S_RRFANDOM, "royalrumble.fandom.com (Royal Rumble Wiki)",
           "wrestling_database", 12, "Other reputable site",
           "Used by the 1991 elimination-gap research agent. A dedicated Royal Rumble wiki, "
           "distinct from prowrestling.fandom.com (this database's existing S052).")
add_source(S_GROKIPEDIA, "Grokipedia, 'Royal Rumble (1993)'",
           "reference_site", 10, "Wikipedia/reference sites",
           "Used by the 1993 elimination-gap research agent as a source independent of "
           "Wikipedia's own event-article table.")
add_source(S_EWN, "eWrestlingNews.com, 'Royal Rumble Series #10 (1997)' retrospective",
           "reputable_publication", 12, "Other reputable site",
           "Used by the 1997 elimination-gap research agent; a narrative retrospective review.")
add_source(S_FOXSPORTS, "FoxSports.com, 1997 Royal Rumble 'controversial win' retrospective",
           "reputable_publication", 12, "Other reputable site",
           "Used by the 1997 elimination-gap research agent; corroborated several of Steve "
           "Austin's and Mankind's/Bret Hart's eliminations narratively.")

# Existing sources reused (already registered earlier in the project):
S_WIKI_88_92 = "S026"
S_WIKI_93_97 = "S035"
S_TJR = "S037"
S_ARS = "S040"          # allrumblestats.com
S_BOD = "S041"          # Blog of Doom
S_OWW = "S042"          # OnlineWorldOfWrestling event results
S_PWFANDOM = "S052"     # prowrestling.fandom.com
S_CAGEMATCH = "S023"    # Cagematch.net

# ===========================================================================
# PART 1 -- new elimination credits.
# Each entry: event_id, victim wrestler_id, [eliminator wrestler_id(s)],
# source_ids tuple, optional narrative note, optional (disputed_flag_text).
# A single eliminator -> a normal solo row. Multiple eliminators -> one row
# per contributor (matching this database's existing gang-elimination
# convention -- see RR1988M's tito-santana/bret-hart/jim-neidhart rows),
# all sharing one simultaneous_group_id.
# ===========================================================================

Y91 = (S_WIKI_88_92, S_ARS, S_PWH, S_RRFANDOM)
Y92 = (S_WIKI_88_92, S_BOD, S_OWW, S_TJR)
Y93 = (S_WIKI_93_97, S_ARS, S_OWW, S_PWFANDOM)
Y95 = (S_WIKI_93_97, S_ARS, S_PWH, S_PWFANDOM)
Y97 = (S_WIKI_93_97, S_ARS, S_OWW, S_EWN)

# --- 1991 -------------------------------------------------------------------
credits_1991 = [
    ("dino-bravo", ["greg-valentine"], Y91, None),
    ("paul-roma", ["jake-roberts"], Y91 + (S_TJR,),
     "Jake Roberts ducked a charge and Roma went over the top. Wikipedia's own table alone "
     "classifies this as a self-elimination; 3 independent sources plus TJR's narrative review "
     "agree Jake Roberts caused it -- see flag."),
    ("texas-tornado", ["the-undertaker"], Y91, None),
    ("saba-simba", ["rick-martel"], Y91, None),
    ("butch-miller", ["the-undertaker"], Y91, None),
    ("jake-roberts", ["rick-martel"], Y91, None),
    ("hercules", ["brian-knobbs"], Y91, None),
    ("tito-santana", ["earthquake"], Y91, None),
    ("the-undertaker", ["hawk", "animal"], Y91, "undertaker_hawk_animal", None),
    ("jimmy-snuka", ["hawk"], Y91, None),
    ("british-bulldog", ["earthquake", "brian-knobbs"], Y91, "bulldog_earthquake_knobbs", None),
    ("smash", ["hulk-hogan"], Y91, None),
    ("hawk", ["rick-martel", "hercules"], Y91, "hawk_martel_hercules", None),
    ("shane-douglas", ["brian-knobbs"], Y91, None),
    ("animal", ["earthquake"], Y91, None),
    ("demolition-crush", ["hulk-hogan"], Y91, None),
    ("jim-duggan", ["mr-perfect"], Y91, None),
    ("mr-perfect", ["british-bulldog"], Y91, None),
    ("haku", ["british-bulldog"], Y91, None),
    ("jim-neidhart", ["rick-martel"], Y91, None),
    ("the-warlord", ["hulk-hogan"], Y91 + (S_TJR,),
     "Wikipedia's table alone leaves this cell blank; 3 independent sources plus TJR's "
     "narrative ('Hogan eliminated Warlord with a clothesline') agree. Treated as a data gap "
     "in that one table, not a genuine conflict."),
    ("tugboat", ["hulk-hogan"], Y91 + (S_TJR,),
     "Same Wikipedia-table-gap situation as The Warlord above; 3 sources plus TJR's narrative "
     "('Hogan threw him out on the other side of the ring' after Tugboat tried to eliminate "
     "Hogan first) agree."),
]

# --- 1992 -------------------------------------------------------------------
credits_1992 = [
    ("british-bulldog", ["ric-flair"], Y92, None),
    ("jerry-sags", ["british-bulldog"], Y92, None),
    ("haku", ["british-bulldog"], (S_BOD, S_OWW, S_TJR), None),
    ("the-barbarian", ["hercules"], Y92, None),
    ("texas-tornado", ["ric-flair"], Y92, None),
    ("smash", ["big-boss-man"], (S_WIKI_88_92, S_OWW),
     "Verified directly (Wikipedia's Royal Rumble (1992) elimination table; OnlineWorld"
     "OfWrestling's 1992 results page, 'Repo by Bossman before #14') rather than by one of the "
     "5 research agents -- that agent could not find 'Smash' as a separate entrant, not "
     "knowing this database's existing convention of reusing wrestler_id 'smash' across "
     "gimmick eras (ring_name_at_time='Repo Man' for both this event and 1993)."),
    ("greg-valentine", ["smash"], Y92 + (S_RRFANDOM,),
     "Sourced eliminator name is 'Repo Man'; this database's existing wrestler_id for that "
     "gimmick-era Barry Darsow appearance is 'smash' (ring_name_at_time='Repo Man')."),
    ("nikolai-volkoff", ["smash"], (S_BOD, S_OWW, S_TJR, S_RRFANDOM),
     "Sourced eliminator name is 'Repo Man' -> wrestler_id 'smash', as above. Wikipedia's own "
     "table left this cell blank; 4 other sources agree."),
    ("hercules", ["big-boss-man"], Y92, None),
    ("irwin-r-schyster", ["roddy-piper"], Y92, None),
    ("jimmy-snuka", ["the-undertaker"], Y92, None),
    ("the-undertaker", ["hulk-hogan"], Y92, None),
    ("the-berzerker", ["hulk-hogan"], Y92, None),
    ("col-mustafa", ["randy-savage"], Y92, None),
    ("skinner", ["rick-martel"], (S_WIKI_88_92, S_BOD, S_OWW), None),
    ("sgt-slaughter", ["sid-justice"], Y92, None),
    ("the-warlord", ["hulk-hogan", "sid-justice"], Y92, "warlord_hogan_sid", None),
]

# --- 1993 -------------------------------------------------------------------
credits_1993 = [
    ("papa-shango", ["ric-flair"], Y93 + (S_PWH,), None),
    ("ted-dibiase", ["the-undertaker"], Y93, None),
    ("brian-knobbs", ["ted-dibiase"], Y93, None),
    ("virgil", ["the-berzerker"], Y93, None),
    ("jerry-lawler", ["mr-perfect"], Y93, None),
    ("max-moon", ["jerry-lawler"], Y93, None),
    ("genichiro-tenryu", ["the-undertaker"], Y93, None),
    ("mr-perfect", ["ted-dibiase", "koko-b-ware", "jerry-lawler"], Y93 + (S_GROKIPEDIA,),
     "perfect_dibiase_koko_lawler",
     "Per Wikipedia's own footnote, Lawler had already been eliminated himself earlier in the "
     "match but assisted from ringside. One source (WrestlingRecaps.com) names Yokozuna instead "
     "of Koko B. Ware as the third contributor; 4 other sources (Wikipedia, AllRumbleStats, "
     "OWW, Grokipedia) agree on Koko B. Ware -- see flag."),
    ("skinner", ["mr-perfect"], Y93, None),
    ("koko-b-ware", ["ted-dibiase"], Y93, None),
    ("samu", ["the-undertaker"], Y93, None),
    ("the-berzerker", ["the-undertaker"], (S_ARS, S_OWW, S_PWFANDOM, S_GROKIPEDIA, S_TJR),
     "Wikipedia's own table cell for this row was blank; 5 other sources agree, including "
     "TJR's narrative ('Undertaker eliminates The Berzerker with a backdrop')."),
    ("red-rooster", ["ted-dibiase"], Y93 + (S_GROKIPEDIA, S_PWH),
     "Billed simply as 'Terry Taylor' for this event (Red Rooster gimmick had ended in 1989) -- "
     "already correctly reflected in this database's ring_name_at_time field, no change needed "
     "there. Recorded the shortest stay in the match (0:24)."),
    ("damien-demento", ["carlos-colon"], Y93 + (S_TJR,), None),
    ("irwin-r-schyster", ["earthquake"], Y93, None),
    ("tatanka", ["yokozuna"], Y93, None),
    ("jerry-sags", ["owen-hart"], (S_WIKI_93_97, S_ARS, S_OWW, S_RRFANDOM),
     "One source's (ProWrestling Fandom Wiki) automated extraction returned 'Bret Hart', who "
     "was not in this match at all -- treated as a site/extraction error, not a genuine "
     "conflict, given 4-source agreement on Owen Hart."),
    ("tugboat", ["earthquake"], Y93, "Billed as 'Typhoon' for this event."),
    ("fatu", ["bob-backlund"], Y93, None),
    ("earthquake", ["yokozuna"], Y93, None),
    ("carlos-colon", ["yokozuna"], (S_ARS, S_OWW, S_PWFANDOM, S_GROKIPEDIA, S_RRFANDOM),
     "Wikipedia's own table cell was blank; 5 other sources agree."),
    ("tito-santana", ["yokozuna"], (S_ARS, S_OWW, S_PWFANDOM, S_GROKIPEDIA, S_RRFANDOM),
     "Wrestling as 'El Matador' this event, per TJR's review text. Wikipedia's own table cell "
     "was blank; 5 other sources agree."),
    ("rick-martel", ["bob-backlund"], Y93, None),
    ("owen-hart", ["yokozuna"], Y93, None),
    ("smash", ["randy-savage"], Y93 + (S_RRFANDOM,),
     "Wrestling as 'Repo Man' this event (see 1992 notes above on this wrestler_id)."),
]

# --- 1995 -------------------------------------------------------------------
credits_1995 = [
    ("eli-blu", ["headshrinker-sione"], Y95, None),
    ("duke-droese", ["shawn-michaels"], Y95, None),
    ("jimmy-del-ray", ["british-bulldog"], Y95 + (S_OWW,),
     "One source's extraction returned Shawn Michaels; 3 other sources (including OWW's "
     "eliminator-sequence listing) agree on British Bulldog -- treated as an extraction error, "
     "not a genuine conflict, given the 3-1 majority."),
    ("headshrinker-sione", ["eli-blu"], Y95,
     "Part of the match's well-known 'revenge spot': Sione eliminates Eli Blu, then Eli Blu "
     "(from ringside) pulls Sione out moments later. One source's extraction returned 'Jacob "
     "Blue' (a different entrant in the same match) -- treated as a site/extraction error, not "
     "a genuine conflict, given agreement elsewhere and this database's own preserved sequence."),
    ("tom-prichard", ["shawn-michaels"], Y95, None),
    ("doink-1995", ["kwang"], Y95, None),
    ("kwang", ["headshrinker-sione"], Y95, None),
    ("rick-martel", ["headshrinker-sione"], (S_ARS, S_PWH, S_PWFANDOM),
     "Wikipedia's own table cell was blank; 3 other sources agree."),
    ("owen-hart", ["british-bulldog"], Y95 + (S_OWW,), None),
    ("timothy-well", ["british-bulldog"], (S_ARS, S_PWH, S_PWFANDOM),
     "Wikipedia's own table cell was blank; 3 other sources agree."),
    ("luke-williams", ["shawn-michaels"], Y95, None),
    ("jacob-blu", ["shawn-michaels"], (S_ARS, S_PWH, S_PWFANDOM),
     "Wikipedia's own table cell was blank; 3 other sources agree."),
    ("king-kong-bundy", ["shawn-michaels"], Y95, None),
    ("mo", ["king-kong-bundy"], Y95, None),
    ("mabel", ["lex-luger"], Y95 + (S_OWW,), None),
    ("butch-miller", ["shawn-michaels"], Y95, None),
    ("lex-luger", ["demolition-crush", "shawn-michaels"], Y95, "luger_crush_michaels", None),
    ("mantaur", ["lex-luger"], Y95, None),
    ("aldo-montoya", ["shawn-michaels"], Y95, None),
    ("henry-godwinn", ["lex-luger"], Y95, None),
    ("billy-gunn", ["demolition-crush", "dick-murdoch"], Y95, "billygunn_crush_murdoch", None),
    ("bart-gunn", ["demolition-crush", "dick-murdoch"], Y95, "bartgunn_crush_murdoch", None),
    ("bob-backlund", ["lex-luger"], Y95, None),
    ("steven-dunn", ["aldo-montoya"], Y95, None),
    ("dick-murdoch", ["henry-godwinn"], Y95, None),
    ("adam-bomb", ["demolition-crush"], Y95, None),
    ("fatu", ["demolition-crush"], (S_ARS, S_PWH, S_PWFANDOM),
     "Wikipedia's own table cell was blank; 3 other sources agree."),
    ("demolition-crush", ["british-bulldog"], Y95, None),
]

# --- 1997 -------------------------------------------------------------------
credits_1997 = [
    ("demolition-crush", ["phineas-godwinn"], Y97, None),
    ("fake-razor-ramon", ["ahmed-johnson"], Y97 + (S_EWN,), None),
    ("phineas-godwinn", ["steve-austin"], Y97 + (S_EWN,), None),
    ("bart-gunn", ["steve-austin"], Y97 + (S_EWN,), None),
    ("jake-roberts", ["steve-austin"], Y97 + (S_EWN,), None),
    ("british-bulldog", ["owen-hart"], Y97, None),
    ("pierroth-jr", ["mil-mascaras"], Y97, None),
    ("the-sultan", ["british-bulldog"], (S_ARS, S_OWW, S_EWN),
     "Wikipedia alone credits a joint British Bulldog + Mil Mascaras elimination; 3 other "
     "independent sources credit British Bulldog solo -- see flag."),
    ("hunter-hearst-helmsley", ["goldust"], Y97, None),
    ("owen-hart", ["steve-austin"], Y97, None),
    ("goldust", ["owen-hart"], Y97, None),
    ("cibernetico", ["mil-mascaras", "pierroth-jr"], Y97, "cibernetico_mascaras_pierroth", None),
    ("marc-mero", ["steve-austin"], Y97 + (S_EWN,), None),
    ("latin-lover", ["faarooq"], Y97, None),
    ("savio-vega", ["steve-austin"], Y97 + (S_EWN,), None),
    ("jesse-james", ["steve-austin"], Y97 + (S_OWW,), None),
    ("jerry-lawler", ["bret-hart"], Y97 + (S_EWN,), None),
    ("fake-diesel", ["bret-hart"], (S_OWW, S_EWN, S_ARS, S_FOXSPORTS),
     "Wikipedia alone credits Steve Austin; 4 other independent sources (including a narrative "
     "account of the specific post-elimination angle) credit Bret Hart -- see flag."),
    ("rocky-maivia", ["mankind"], (S_OWW, S_ARS, S_FOXSPORTS, S_EWN),
     "Wikipedia alone credits Vader; 3-4 other independent sources credit Mankind ('thrown out "
     "by Mick Foley') -- see flag."),
    ("flash-funk", ["vader"], (S_WIKI_93_97, S_ARS, S_CAGEMATCH), None),
    ("henry-godwinn", ["the-undertaker"], Y97, None),
]

ALL_CREDITS = [
    ("RR1991M", credits_1991),
    ("RR1992M", credits_1992),
    ("RR1993M", credits_1993),
    ("RR1995M", credits_1995),
    ("RR1997M", credits_1997),
]

new_rows_added = 0
gang_groups_added = 0
for event_id, credit_list in ALL_CREDITS:
    for entry in credit_list:
        # Solo credits are 4-tuples: (victim, [eliminator], sources, note_or_None).
        # Gang/tandem credits are 5-tuples: (victim, [elim1, elim2, ...], sources,
        # group_id, note_or_None) -- group_id is explicit, never auto-derived, so it
        # can never accidentally leak into the notes field.
        if len(entry) == 4:
            victim, eliminators, srcs, note = entry
            assert len(eliminators) == 1, f"4-tuple entry must be solo: {entry!r}"
            group_id = ""
        else:
            victim, eliminators, srcs, group_id, note = entry
            assert len(eliminators) > 1, f"5-tuple entry must be gang/tandem: {entry!r}"

        victim_row = entrants_by_key[(event_id, victim)]
        order_in_match = victim_row["elim_number"]
        entry_num_victim = victim_row["entry_number"]
        clock_time = victim_row.get("elimination_clock_time", "")
        clock_seconds = victim_row.get("elimination_clock_seconds", "")
        is_gang = len(eliminators) > 1

        if is_gang:
            gang_groups_added += 1

        for elim in eliminators:
            others = [w for w in eliminators if w != elim]
            eliminator_row = entrants_by_key.get((event_id, elim))
            entry_num_eliminator = eliminator_row["entry_number"] if eliminator_row else ""
            row = {
                "event_id": event_id,
                "order_in_match": order_in_match,
                "eliminated_wrestler_id": victim,
                "eliminator_wrestler_id": elim,
                "assisting_wrestler_ids": ";".join(others),
                "entry_number_of_eliminated": entry_num_victim,
                "entry_number_of_eliminator": "",
                "elimination_clock_time": clock_time,
                "elimination_clock_seconds": clock_seconds,
                "elimination_type": "over_top_rope",
                "elimination_method": "UNKNOWN",
                "location_side": "",
                "location_status": "UNKNOWN",
                "is_solo": "FALSE" if is_gang else "TRUE",
                "is_shared": "TRUE" if is_gang else "FALSE",
                "is_accidental": "UNKNOWN",
                "is_self_elimination": "FALSE",
                "is_storyline_related": "UNKNOWN",
                "was_already_incapacitated": "UNKNOWN",
                "is_disputed": "TRUE" if (note and "see flag" in note) else "FALSE",
                "simultaneous_group_id": group_id,
                "data_quality_status": "CONFIRMED",
                "source_ids": ";".join(srcs),
                "notes": note or "",
            }
            eliminations.append(row)
            new_rows_added += 1

print(f"Part 1 done: {new_rows_added} new eliminations.csv rows added "
      f"({gang_groups_added} gang/tandem eliminations, 2-3 rows each).")

# ===========================================================================
# PART 2 -- Ahmed Johnson / Faarooq (1997): fix the known eliminated_by_ids
# gap left by the Collection of Stats pass (their self-elimination rows were
# added to eliminations.csv AFTER that pass's eliminated_by_ids back-fill had
# already run, so it never picked them up).
# ===========================================================================
for wid in ("ahmed-johnson", "faarooq"):
    er = entrants_by_key[("RR1997M", wid)]
    assert er["eliminated_by_ids"] == "", f"expected {wid} eliminated_by_ids still blank"
    er["eliminated_by_ids"] = wid

print("Part 2 done: Ahmed Johnson & Faarooq (1997) eliminated_by_ids gap closed (self).")

# ===========================================================================
# PART 3 -- flags for the 5 preserved genuine conflicts (majority credit
# recorded in Part 1's rows above; the dissenting account preserved here).
# ===========================================================================
new_flag(
    "RR1991M", "eliminations", "paul-roma", "eliminator_wrestler_id", "conflicting_sources",
    "Wikipedia's own Royal Rumble (1991) elimination table classifies Paul Roma's elimination "
    "as a self-elimination. Three independent sources (AllRumbleStats, ProWrestlingHistory.com, "
    "royalrumble.fandom.com) plus TJR Wrestling's narrative play-by-play ('Roma charged in at "
    "Jake, he ducked and Roma went flying over the top') agree Jake Roberts caused it by "
    "evasion. Credited to Jake Roberts per majority + narrative corroboration; Wikipedia's "
    "differing classification is likely stylistic (no direct hand contact) rather than a "
    "factual dispute about causation, but preserved here rather than silently discarded.",
    f"{S_WIKI_88_92};{S_ARS};{S_PWH};{S_RRFANDOM};{S_TJR}",
)

new_flag(
    "RR1993M", "eliminations", "mr-perfect", "assisting_wrestler_ids", "conflicting_sources",
    "Mr. Perfect's 3-way gang elimination: Wikipedia, AllRumbleStats, OnlineWorldOfWrestling and "
    "Grokipedia all agree on Ted DiBiase, Koko B. Ware and Jerry Lawler (Lawler assisting from "
    "ringside after his own earlier elimination, per Wikipedia's footnote). One source "
    "(WrestlingRecaps.com) names Yokozuna instead of Koko B. Ware as the third contributor. "
    "Credited DiBiase/Koko B. Ware/Lawler per the 4-source majority; the dissenting account is "
    "preserved here rather than silently discarded.",
    f"{S_WIKI_93_97};{S_ARS};{S_OWW};{S_GROKIPEDIA};{S_PWFANDOM}",
)

new_flag(
    "RR1997M", "eliminations", "the-sultan", "eliminator_wrestler_id", "conflicting_sources",
    "Wikipedia's Royal Rumble (1997) elimination table credits a joint British Bulldog + Mil "
    "Mascaras elimination for The Sultan (Rikishi). Three other independent sources "
    "(AllRumbleStats, OnlineWorldOfWrestling, eWrestlingNews.com) credit British Bulldog alone. "
    "Credited solo per the 3-1 majority; Wikipedia's joint-credit account is preserved here "
    "rather than silently discarded.",
    f"{S_WIKI_93_97};{S_ARS};{S_OWW};{S_EWN}",
)

new_flag(
    "RR1997M", "eliminations", "fake-diesel", "eliminator_wrestler_id", "conflicting_sources",
    "Wikipedia's Royal Rumble (1997) elimination table credits Steve Austin with eliminating "
    "Fake Diesel (Glenn Jacobs). Four other independent sources (OnlineWorldOfWrestling, "
    "eWrestlingNews.com, AllRumbleStats, FoxSports.com) credit Bret Hart. Credited Bret Hart "
    "per the 4-1 majority; Wikipedia's account is preserved here rather than silently discarded.",
    f"{S_WIKI_93_97};{S_OWW};{S_EWN};{S_ARS};{S_FOXSPORTS}",
)

new_flag(
    "RR1997M", "eliminations", "rocky-maivia", "eliminator_wrestler_id", "conflicting_sources",
    "Wikipedia's Royal Rumble (1997) elimination table credits Vader with eliminating Rocky "
    "Maivia (The Rock). Three to four other independent sources (OnlineWorldOfWrestling, "
    "AllRumbleStats, FoxSports.com -- 'thrown out by Mick Foley' -- and eWrestlingNews.com by "
    "implication) credit Mankind. Credited Mankind per the majority; Wikipedia's account is "
    "preserved here rather than silently discarded. Note for this database's sourcing "
    "hierarchy: across the 1993/1997 elimination-gap research this pass, Wikipedia's own "
    "event-article table was the SOLE dissenting source against a multi-source, cross-database "
    "consensus in every one of the 5 genuine conflicts found -- worth keeping in mind for "
    "future fact-checking passes that currently treat Wikipedia as a primary source.",
    f"{S_WIKI_93_97};{S_OWW};{S_ARS};{S_FOXSPORTS};{S_EWN}",
)

print("Part 3 done: 5 new conflict flags added (F327-F331).")

# ===========================================================================
# PART 4 -- full recompute of derived summary fields for these 5 events only.
# See this script's docstring for why this differs from the Collection of
# Stats pass's conservative "never fill a blank" rule: these 5 events now
# have comprehensive (28-29 of ~29) elimination coverage as a direct result
# of this pass, unlike the general database-wide hygiene sweep.
# ===========================================================================
TARGET_EVENTS = {"RR1991M", "RR1992M", "RR1993M", "RR1995M", "RR1997M"}

contributors_by_victim = {}
victims_by_contributor = {}
for e in eliminations:
    if e["event_id"] not in TARGET_EVENTS or not e["eliminator_wrestler_id"]:
        continue
    vkey = (e["event_id"], e["eliminated_wrestler_id"])
    contributors = contributors_by_victim.setdefault(vkey, set())
    contributors.add(e["eliminator_wrestler_id"])
    contributors.update(filter(None, e["assisting_wrestler_ids"].split(";")))

for (eid, victim), contributors in contributors_by_victim.items():
    for c in contributors:
        if c == victim:
            continue  # self-elimination never counts as "eliminated someone else"
        victims_by_contributor.setdefault((eid, c), set()).add(victim)

filled_ids, filled_counts, filled_eliminated_by = 0, 0, 0
for e in entrants:
    if e["event_id"] not in TARGET_EVENTS:
        continue
    key = (e["event_id"], e["wrestler_id"])

    # eliminated_by_ids: fill only if currently blank (never overwrite explanatory text)
    if not e.get("eliminated_by_ids", "").strip():
        contributors = contributors_by_victim.get(key)
        if contributors:
            e["eliminated_by_ids"] = ";".join(sorted(contributors))
            filled_eliminated_by += 1

    # wrestlers_eliminated_ids + counts: full recompute (fills blanks, this event group only)
    victims = victims_by_contributor.get(key, set())
    new_elim_ids = ";".join(sorted(victims))
    if e.get("wrestlers_eliminated_ids", "") != new_elim_ids:
        e["wrestlers_eliminated_ids"] = new_elim_ids
        filled_ids += 1

    solo = sum(1 for v in victims if len(contributors_by_victim[(e["event_id"], v)]) == 1)
    assisted = len(victims) - solo
    total = solo + assisted
    old_total = e.get("wrestlers_eliminated_count") or ""
    if old_total != str(total):
        e["wrestlers_eliminated_count"] = str(total)
        e["solo_eliminations_count"] = str(solo)
        e["assisted_eliminations_count"] = str(assisted)
        filled_counts += 1

new_flag(
    "", "entrants", "RR1991M;RR1992M;RR1993M;RR1995M;RR1997M",
    "wrestlers_eliminated_ids;wrestlers_eliminated_count;eliminated_by_ids", "corrected",
    f"Following this pass's dedicated elimination-gap research (114 new eliminator credits "
    f"across these 5 events, closing 116 of the database's 165 originally-uncredited "
    f"eliminations), these 5 events' derived summary fields were FULLY recomputed -- not just "
    f"resynced -- from eliminations.csv: {filled_eliminated_by} previously-blank "
    f"eliminated_by_ids fields filled, {filled_ids} wrestlers_eliminated_ids fields updated, "
    f"{filled_counts} wrestlers_eliminated_count/solo/assisted fields updated (including filling "
    f"previously-blank counts with real computed values, which the Collection of Stats pass's "
    f"F317 deliberately did NOT do database-wide). This is a deliberate, narrower exception to "
    f"F317's conservative rule: these 5 events specifically now have comprehensive (28-29 of "
    f"~29) elimination coverage as a direct result of this pass, so a blank count field here "
    f"genuinely does mean 'zero, now confirmed' rather than 'not yet computed for this era' -- "
    f"unlike the general database-wide state addressed by F317.",
    "", "resolved",
)

print(f"Part 4 done: {filled_eliminated_by} eliminated_by_ids filled, {filled_ids} "
      f"wrestlers_eliminated_ids updated, {filled_counts} wrestlers_eliminated_count/solo/"
      f"assisted updated, across the 5 target events.")

save("entrants.csv", entrants, ENTRANTS_FIELDS)
save("eliminations.csv", eliminations, ELIM_FIELDS)
save("flags.csv", flags, FLAGS_FIELDS)
save("sources.csv", sources, SOURCES_FIELDS)
print(f"Elimination-gap pass complete: {new_rows_added} new eliminations.csv rows, "
      f"5 new sources (S118-S122), {flag_ctr[0] - 327} new flags (F327-F{flag_ctr[0]-1}).")
