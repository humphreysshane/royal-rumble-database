# -*- coding: utf-8 -*-
"""
Fixes a data-integrity bug in wrestlers.csv's `hall_of_fame_year` field, discovered when Shane
fact-checked the dashboard's "Rumble with most eventual Hall of Famers" record (R013, 17
members, RR1995M) and immediately flagged 3 names he was confident were NOT WWE Hall of Famers:
Eli Blu, Jimmy Del Ray, and Tom Prichard.

ROOT CAUSE: a full scan of wrestlers.csv found the `hall_of_fame_year` column (position 13 of
17) holding a non-year string -- a tag-team/stable name, or in 2 cases a wrestler's better-known
ring name -- for 31 wrestler_ids, all originally created by the 1991-1997 event-build scripts
(build_1991.py through build_1997.py). Comparing the row tuples against wrestlers.csv's column
order shows this was never intentional HOF data: for every one of these 31 rows, the
`aliases_ring_names` field (the very next column) is blank, and the same "half of The X
Brothers (w/ ...)" text already appears correctly in the row's own `notes` field. The
`hall_of_fame_year` slot was mistakenly used as an ad hoc scratch note for "how this wrestler is
otherwise known" during those early build passes -- nothing about it was ever verified against
actual WWE Hall of Fame induction records. build_derived.py's R013 logic (`if
wrestlers[wid].get("hall_of_fame_year")`) then naively treated ANY non-blank value here as proof
of induction, silently counting all 31 as Hall of Famers regardless of what the text said.

RESEARCH THIS PASS: each of the 31 affected wrestler_ids was checked individually against WWE's
official Hall of Fame induction announcements (WWE.com) and Wikipedia's year-by-year "WWE Hall
of Fame (YYYY)" class articles -- 2 independent sources agreeing, meeting this database's
CONFIRMED bar. Result: 9 of the 31 ARE genuine inductees (the scratch text just happened to
name a team/gimmick they were later inducted under, or alongside); the other 22, including all
3 Shane specifically named, are NOT WWE Hall of Fame inductees at all -- confirmed further for
several by notinhalloffame.com, a fan site specifically tracking wrestlers NOT (yet) inducted.

GENUINE INDUCTEES (hall_of_fame_year corrected to the real induction year):
  - hawk, animal          -> 2011, as The Road Warriors/Legion of Doom (w/ manager Paul Ellering)
  - rick-steiner, scott-steiner -> 2022, as The Steiner Brothers
  - hunter-hearst-helmsley      -> 2025, individual (Triple H)
  - jesse-james                 -> 2019, as part of D-Generation X (billed "Road Dogg")
  - billy-gunn                  -> 2019, as part of D-Generation X -- NOT as one of The Smoking
                                    Gunns (that team itself has never been inducted; bart-gunn,
                                    who was never in DX, is correctly blanked below)
  - texas-tornado                -> 2009, as part of the Von Erich family induction (Kerry Von
                                    Erich, posthumous)
  - british-bulldog               -> 2020, individual (Davey Boy Smith)

NOT INDUCTEES (hall_of_fame_year blanked -- no data lost; the team/gimmick context these cells
held is already preserved verbatim in each row's own `notes` field):
  - the-genius (Lanny Poffo): presented his brother Randy Savage's 2015 induction, never
    inducted himself.
  - demolition-crush: Demolition's 2026 WWE Hall of Fame induction names Ax and Smash only
    (WWE's own announcement); Crush, a later-era third member, is explicitly not part of it.
  - the-great-tanaka, kato (The Orient Express): no induction found.
  - jerry-sags (The Nasty Boys): no induction found; fan campaigns for a future induction exist
    but none has happened.
  - irwin-r-schyster (IRS / Mike Rotunda): no induction found.
  - the-berzerker (John Nord): no induction found (notinhalloffame.com lists him as a
    fan-suggested, not-yet-inducted candidate).
  - beau-beverly, blake-beverly (The Beverly Brothers): no induction found.
  - giant-gonzalez: no induction found.
  - doink, doink-1995 (Doink The Clown -- separate wrestler_ids for 2 different performers under
    the gimmick): no induction found for either (notinhalloffame.com lists Matt Borne as a
    not-yet-inducted candidate).
  - mo, mabel (Men on a Mission): no induction found; a 2025 interview with Oscar/Mo discusses
    a possible future induction as speculation, not an event that has happened.
  - bart-gunn (The Smoking Gunns): unlike his ex-partner Billy Gunn (inducted via DX, above),
    Bart Gunn has never been inducted.
  - eli-blu, jacob-blu (The Blu Brothers): no induction found -- confirms Shane's specific call.
  - jimmy-del-ray, tom-prichard (The Heavenly Bodies): no induction found (notinhalloffame.com
    has a dedicated "not in Hall of Fame" entry for Tom Prichard) -- confirms Shane's specific
    call.
  - headshrinker-sione: no induction found. (Distinct from Samu/Fatu's father-and-uncle duo The
    Wild Samoans, Afa and Sika, who WERE inducted in 2007 -- Samu himself presented that
    induction but was not inducted alongside them.)
  - timothy-well, steven-dunn (Well Dunn): no induction found.

R013 ("Rumble with most eventual Hall of Famers") is recomputed by re-running build_derived.py
after this patch -- not hand-edited here -- since it depends on other events' fields too and
must stay in sync with the same logic used database-wide.

Flag ID: F333 (continues from F332). Source IDs: S123-S125 (continue from S122).
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


wrestlers = load("wrestlers.csv")
flags = load("flags.csv")
sources = load("sources.csv")

WRESTLERS_FIELDS = list(wrestlers[0].keys())
FLAGS_FIELDS = list(flags[0].keys())
SOURCES_FIELDS = list(sources[0].keys())

wrestlers_by_id = {w["wrestler_id"]: w for w in wrestlers}

DATE_LOGGED = "2026-09-18"


def add_source(sid, name, stype, tier, tier_label, notes):
    sources.append({
        "source_id": sid, "source_name": name, "source_type": stype, "url": "",
        "reliability_tier": str(tier), "tier_label": tier_label,
        "accessed_date": DATE_LOGGED, "notes": notes,
    })


def add_src(row, *src_ids):
    ids = set(filter(None, row["source_ids"].split(";")))
    ids.update(src_ids)
    row["source_ids"] = ";".join(sorted(ids))


# ---------------------------------------------------------------------------
# New sources for this pass (S123 onward)
# ---------------------------------------------------------------------------
S_WWE_OFFICIAL = "S123"
S_WIKI_HOF_CLASSES = "S124"
S_NOT_IN_HOF = "S125"

add_source(S_WWE_OFFICIAL, "WWE.com, official Hall of Fame induction announcement articles "
           "(classes of 2009, 2011, 2019, 2020, 2022, 2025, 2026)",
           "official_wwe", 1, "WWE / official sources",
           "Fact-check pass triggered by Shane's Eli Blu/Jimmy Del Ray/Tom Prichard challenge. "
           "Used to confirm the genuine WWE Hall of Fame inductees among the 31 wrestler_ids "
           "flagged with a corrupted hall_of_fame_year field. Treated as ONE independent source "
           "regardless of how many individual class-announcement articles were consulted, per "
           "this project's existing convention (see S022).")
add_source(S_WIKI_HOF_CLASSES, "Wikipedia (English), 'WWE Hall of Fame (YYYY)' year-by-year "
           "class articles (2009, 2011, 2019, 2020, 2022, 2025, 2026) plus individual wrestler "
           "biography articles",
           "reference_site", 10, "Wikipedia/reference sites",
           "Fact-check pass triggered by Shane's Eli Blu/Jimmy Del Ray/Tom Prichard challenge. "
           "Used as the second independent source confirming (or, for the 22 non-inductees, "
           "failing to confirm) WWE Hall of Fame induction for each of the 31 flagged "
           "wrestler_ids.")
add_source(S_NOT_IN_HOF, "notinhalloffame.com (fan-run 'not yet in the Hall of Fame' tracking "
           "site) and Wrestling Inc./Cultaholic/Fightful news coverage discussing wrestlers NOT "
           "yet inducted",
           "wrestling_database", 12, "Other reputable site",
           "Corroborating negative evidence for several of the 22 confirmed-not-inducted "
           "wrestler_ids (has dedicated entries for Tom Prichard and Matt Borne/Doink "
           "specifically; news coverage of ongoing fan campaigns for the Nasty Boys, Men on a "
           "Mission, and John Nord/The Berzerker confirms none has happened yet).")

# ---------------------------------------------------------------------------
# Corrections
# ---------------------------------------------------------------------------

# wrestler_id -> real induction year (2 independent sources: S123 + S124)
CORRECTED_YEAR = {
    "hawk": "2011",
    "animal": "2011",
    "rick-steiner": "2022",
    "scott-steiner": "2022",
    "hunter-hearst-helmsley": "2025",
    "jesse-james": "2019",
    "billy-gunn": "2019",
    "texas-tornado": "2009",
    "british-bulldog": "2020",
}

# wrestler_id -> nothing found (blanked; not induced). Listed explicitly (rather than just "the
# remaining 22 of the 31") so this script fails loudly (KeyError below) if the full set of 31
# ever drifts from what this pass actually checked.
CONFIRMED_NOT_INDUCTED = [
    "the-genius", "demolition-crush", "the-great-tanaka", "kato", "jerry-sags",
    "irwin-r-schyster", "the-berzerker", "beau-beverly", "blake-beverly", "giant-gonzalez",
    "doink", "doink-1995", "mo", "mabel", "bart-gunn", "eli-blu", "jacob-blu", "jimmy-del-ray",
    "tom-prichard", "headshrinker-sione", "timothy-well", "steven-dunn",
]

assert len(CORRECTED_YEAR) + len(CONFIRMED_NOT_INDUCTED) == 31, \
    "Expected exactly 31 affected wrestler_ids (the full scan result) to be accounted for."

CORRECTION_NOTE = (
    " [HOF field corrected {date}: this field previously held stray text (\"{old}\"), a "
    "leftover scratch note from this row's original creation, not real Hall of Fame data -- "
    "see F333."
)

fixed_to_year = []
fixed_to_blank = []

for wid, year in CORRECTED_YEAR.items():
    row = wrestlers_by_id[wid]
    old = row["hall_of_fame_year"]
    assert old and not (old.isdigit() and len(old) == 4), \
        f"{wid}: expected a corrupted (non-year) hall_of_fame_year, found {old!r}"
    row["hall_of_fame_year"] = year
    row["notes"] = row["notes"].rstrip() + CORRECTION_NOTE.format(date=DATE_LOGGED, old=old) + \
        f" Confirmed genuine WWE Hall of Fame induction, {year}.]"
    add_src(row, S_WWE_OFFICIAL, S_WIKI_HOF_CLASSES)
    fixed_to_year.append((wid, old, year))

for wid in CONFIRMED_NOT_INDUCTED:
    row = wrestlers_by_id[wid]
    old = row["hall_of_fame_year"]
    assert old and not (old.isdigit() and len(old) == 4), \
        f"{wid}: expected a corrupted (non-year) hall_of_fame_year, found {old!r}"
    row["hall_of_fame_year"] = ""
    row["notes"] = row["notes"].rstrip() + CORRECTION_NOTE.format(date=DATE_LOGGED, old=old) + \
        " No WWE Hall of Fame induction found for this wrestler; field blanked.]"
    add_src(row, S_WIKI_HOF_CLASSES)
    fixed_to_blank.append((wid, old))

# ---------------------------------------------------------------------------
# One flag documenting the whole cleanup (mirrors F332's precedent of a single flag covering a
# multi-record bulk correction, rather than 31 near-identical individual flags).
# ---------------------------------------------------------------------------
all_ids = sorted(CORRECTED_YEAR) + sorted(CONFIRMED_NOT_INDUCTED)
flags.append({
    "flag_id": "F333",
    "event_id": "",
    "table": "wrestlers",
    "record_id": ";".join(all_ids),
    "field": "hall_of_fame_year",
    "issue_type": "corrected",
    "description": (
        "Triggered by Shane's fact-check (2026-09-18): he correctly identified that Eli Blu, "
        "Jimmy Del Ray and Tom Prichard, shown in the dashboard's R013 'Rumble with most "
        "eventual Hall of Famers' record, are not WWE Hall of Famers. A full scan of "
        "wrestlers.csv found this was systemic, not isolated: the hall_of_fame_year field held "
        "a stray tag-team/gimmick-name string (a leftover scratch note from row creation in "
        "build_1991.py-build_1997.py, never actually verified as HOF data) for 31 "
        "wrestler_ids, which build_derived.py's naive truthy check on this field silently "
        "miscounted as inductions. Researched each of the 31 individually against WWE.com's "
        "official induction announcements and Wikipedia's year-by-year HOF class articles: 9 "
        "are genuine inductees and had their field corrected to the real induction year (hawk/"
        "animal 2011, rick-steiner/scott-steiner 2022, hunter-hearst-helmsley 2025, jesse-james/"
        "billy-gunn 2019 via D-Generation X, texas-tornado 2009 via the Von Erich family, "
        "british-bulldog 2020); the other 22, including all 3 Shane named, are confirmed not "
        "inducted and had the field blanked (no data lost -- the team/gimmick text these cells "
        "held is already preserved in each row's own notes field). R013 recomputed accordingly "
        "by build_derived.py after this patch; see scripts/factcheck_hall_of_fame_field.py's "
        "docstring for the full per-wrestler breakdown."
    ),
    "source_ids_involved": f"{S_WWE_OFFICIAL};{S_WIKI_HOF_CLASSES};{S_NOT_IN_HOF}",
    "status": "resolved",
    "date_logged": DATE_LOGGED,
})

save("wrestlers.csv", wrestlers, WRESTLERS_FIELDS)
save("flags.csv", flags, FLAGS_FIELDS)
save("sources.csv", sources, SOURCES_FIELDS)

print(f"Corrected {len(fixed_to_year)} hall_of_fame_year values to real induction years:")
for wid, old, year in fixed_to_year:
    print(f"  {wid}: {old!r} -> {year}")
print(f"\nBlanked {len(fixed_to_blank)} erroneous hall_of_fame_year values (not inducted):")
for wid, old in fixed_to_blank:
    print(f"  {wid}: {old!r} -> ''")
print(f"\nLogged 1 flag (F333), 3 new sources (S123-S125).")
