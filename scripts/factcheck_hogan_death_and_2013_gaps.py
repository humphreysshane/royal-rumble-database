# -*- coding: utf-8 -*-
"""
Two small, unrelated corrections Shane spotted on a glancing quality check of the dashboard,
both fixed here together as quick, concrete wins ahead of the much larger event-by-event
fact-check sweep he's asked for next (see IDEAS.md / this pass's flag for that larger scope).

1) HULK HOGAN'S DEATH NOT RECORDED. Shane noticed R014 ("Rumble with most now-deceased
   entrants", RR1990M, 8) doesn't include Hulk Hogan, RR1990M's own winner, despite Hogan
   having died. wrestlers.csv's hulk-hogan row had a blank deceased_date -- this database was
   simply never updated after his death (WWE.com's official announcement + Wikipedia both
   confirm: Terry Bollea / Hulk Hogan died 2025-07-24, age 71). Corrected here; every event's
   now_deceased_count is a moving target recomputed fresh each build_derived.py run (see that
   script's own event_dynamic_stats.csv comment), so this alone updates however many other
   Rumbles Hogan entered too (1990-2006), not just 1990.

2) 2013 ROYAL RUMBLE UNRECORDED ELIMINATIONS. Shane specifically flagged 2 of RR2013M's 5
   originally-blank eliminated_by_ids: Santino Marella and Tensai. Checked all 5 individually
   against 4 independent sources (WrestlingInc.com's own order-of-eliminations article,
   Sportskeeda's entrant/elimination list, Wikipedia's event article, wwebrady.fandom.com's WWE
   Wiki elimination table, eWrestlingNews.com's series retrospective -- not all 5 needed for
   every row, but at least 2 independent sources agree for each one that WAS resolved):
     - santino-marella -> cody-rhodes (2 sources: WrestlingInc, Sportskeeda)
     - prince-albert (billed "Tensai" this event) -> kofi-kingston (4 sources: WrestlingInc,
       Sportskeeda, Wikipedia, wwebrady -- unanimous)
     - hunico (billed "Sin Cara" this event) -> ryback (2 sources: WrestlingInc, wwebrady --
       consistent with Ryback's well-documented 5-elimination run this match, independently
       corroborated by Shane's own document per S103)
     - bo-dallas -> wade-barrett, a genuinely unusual angle, not a data-entry gap masquerading
       as a normal elimination: Bo Dallas eliminated Wade Barrett (elim #20, already on record),
       then Barrett re-entered/interfered from ringside and eliminated Dallas right back (elim
       #21) -- 3 sources agree on this sequence (WrestlingInc, wwebrady, eWrestlingNews's
       narrative recap: "Wade gives Bo the Bullhammer Elbow" after his own elimination).
     - brodus-clay -> left UNRESOLVED. All sources checked describe a gang elimination
       ("multiple people" / "a number of wrestlers" / "everyone gangs up on Brodus Clay because
       he's the widest") but NONE names the individual contributor(s). Per this project's core
       rule, not inventing names here -- flagged as still-open/needs-further-research rather than
       silently left to look like a plain oversight.

Flag ID: F334 (continues from F333). Source IDs: S126 (new) + reused S039/S059/S078/S109/S121.
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
entrants = load("entrants.csv")
eliminations = load("eliminations.csv")
flags = load("flags.csv")
sources = load("sources.csv")

WRESTLERS_FIELDS = list(wrestlers[0].keys())
ENTRANTS_FIELDS = list(entrants[0].keys())
ELIM_FIELDS = list(eliminations[0].keys())
FLAGS_FIELDS = list(flags[0].keys())
SOURCES_FIELDS = list(sources[0].keys())

wrestlers_by_id = {w["wrestler_id"]: w for w in wrestlers}
entrants_by_key = {(e["event_id"], e["wrestler_id"]): e for e in entrants}

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


def new_flag(event_id, table, record_id, field, issue_type, description, source_ids, status="open"):
    fid = f"F{new_flag.ctr:03d}"
    new_flag.ctr += 1
    flags.append({
        "flag_id": fid, "event_id": event_id, "table": table, "record_id": record_id,
        "field": field, "issue_type": issue_type, "description": description,
        "source_ids_involved": source_ids, "status": status, "date_logged": DATE_LOGGED,
    })
    return fid


new_flag.ctr = 334

# ---------------------------------------------------------------------------
# New source (S126). WWE.com's own Hogan obituary is cited inline below via
# the official_wwe reliability tier; Wikipedia is reused as S022-family
# general reference (added fresh here since S022 is scoped to the original
# 1988-1992 bio pass) -- kept as one new source per site, per convention.
# ---------------------------------------------------------------------------
S_WWE_HOGAN = "S126"
S_WWE_WIKI_BIO = "S127"
S_WWEBRADY = "S128"

add_source(S_WWE_HOGAN, "WWE.com, 'Legendary WWE Hall of Famer Hulk Hogan passes away' "
           "(official announcement article)", "official_wwe", 1, "WWE / official sources",
           "Confirms Hulk Hogan (Terry Bollea) died 2025-07-24 at age 71. Triggered by Shane "
           "noticing R014 (most now-deceased entrants) didn't include Hogan despite his death.")
add_source(S_WWE_WIKI_BIO, "Wikipedia (English), Hulk Hogan biography article",
           "reference_site", 10, "Wikipedia/reference sites",
           "Second independent source confirming the 2025-07-24 death date, cross-checked "
           "against WWE.com's own announcement (S126).")
add_source(S_WWEBRADY, "wwebrady.fandom.com (WWE Wiki), Royal Rumble (2013) elimination table",
           "wrestling_database", 12, "Other reputable site",
           "Used alongside WrestlingInc.com/Sportskeeda/Wikipedia/eWrestlingNews to resolve "
           "2013 Royal Rumble elimination-credit gaps Shane flagged on a quality check.")

# Existing sources reused (already registered earlier in the project):
S_WRESTLINGINC = "S039"
S_WRESTLINGRECAPS = "S059"
S_SPORTSKEEDA = "S078"
S_WIKI_2013_16 = "S109"
S_EWN = "S121"

# ---------------------------------------------------------------------------
# 1) Hulk Hogan's death
# ---------------------------------------------------------------------------
hogan = wrestlers_by_id["hulk-hogan"]
assert not hogan["deceased_date"], "hulk-hogan already has a deceased_date -- check before rerunning"
hogan["deceased_date"] = "2025-07-24"
hogan["notes"] = (hogan["notes"].rstrip() + " Died 2025-07-24, age 71 (per WWE.com's own "
                  "announcement and Wikipedia) -- added after Shane noticed R014 (most "
                  "now-deceased entrants) didn't reflect it. See F334.")
add_src(hogan, S_WWE_HOGAN, S_WWE_WIKI_BIO)

new_flag(
    "", "wrestlers", "hulk-hogan", "deceased_date", "corrected",
    "Shane noticed RR1990M's R014 leaderboard card (most now-deceased entrants, 8) didn't "
    "include Hulk Hogan -- RR1990M's own winner -- despite Hogan having died. wrestlers.csv's "
    "hulk-hogan row simply had a blank deceased_date; this database was never updated after his "
    "death. Confirmed 2025-07-24 (age 71) via WWE.com's official announcement and Wikipedia. "
    "now_deceased_count is recomputed fresh from today's date on every build_derived.py run, so "
    "this single correction updates every Rumble Hogan entered (1990-2006), not just 1990.",
    f"{S_WWE_HOGAN};{S_WWE_WIKI_BIO}", status="resolved",
)

# ---------------------------------------------------------------------------
# 2) 2013 Royal Rumble elimination-credit gaps
# ---------------------------------------------------------------------------
NEW_2013_CREDITS = [
    # (victim, eliminator, source_ids)
    ("santino-marella", "cody-rhodes", (S_WRESTLINGINC, S_SPORTSKEEDA)),
    ("prince-albert", "kofi-kingston", (S_WRESTLINGINC, S_SPORTSKEEDA, S_WIKI_2013_16, S_WWEBRADY)),
    ("hunico", "ryback", (S_WRESTLINGINC, S_WWEBRADY)),
]

for victim, eliminator, srcs in NEW_2013_CREDITS:
    e_row = entrants_by_key[("RR2013M", victim)]
    assert not e_row["eliminated_by_ids"], f"{victim}: expected a blank eliminated_by_ids"
    e_row["eliminated_by_ids"] = eliminator
    add_src(e_row, *srcs)
    eliminations.append({
        "event_id": "RR2013M", "order_in_match": e_row["elim_number"],
        "eliminated_wrestler_id": victim, "eliminator_wrestler_id": eliminator,
        "assisting_wrestler_ids": "", "entry_number_of_eliminated": e_row["entry_number"],
        "entry_number_of_eliminator": "", "elimination_clock_time": e_row["elimination_clock_time"],
        "elimination_clock_seconds": e_row["elimination_clock_seconds"],
        "elimination_type": "over_top_rope", "elimination_method": "", "location_side": "",
        "location_status": "UNKNOWN", "is_solo": "TRUE", "is_shared": "FALSE",
        "is_accidental": "FALSE", "is_self_elimination": "FALSE", "is_storyline_related": "FALSE",
        "was_already_incapacitated": "FALSE", "is_disputed": "FALSE", "simultaneous_group_id": "",
        "data_quality_status": "CONFIRMED", "source_ids": ";".join(srcs),
        "notes": "Filled during Shane's 2026-09-18 quality-check pass -- previously an "
                 "unrecorded eliminator credit.",
    })

# Bo Dallas: a genuine post-elimination-interference spot, not a plain solo credit -- Wade
# Barrett was already eliminated (elim #20, already on record, eliminated by Bo Dallas himself)
# when he returned to ringside and eliminated Dallas right back. Recorded as storyline-related
# rather than a normal in-ring elimination.
bo_row = entrants_by_key[("RR2013M", "bo-dallas")]
assert not bo_row["eliminated_by_ids"], "bo-dallas: expected a blank eliminated_by_ids"
bo_row["eliminated_by_ids"] = "wade-barrett"
add_src(bo_row, S_WRESTLINGINC, S_WWEBRADY, S_EWN)
eliminations.append({
    "event_id": "RR2013M", "order_in_match": bo_row["elim_number"],
    "eliminated_wrestler_id": "bo-dallas", "eliminator_wrestler_id": "wade-barrett",
    "assisting_wrestler_ids": "", "entry_number_of_eliminated": bo_row["entry_number"],
    "entry_number_of_eliminator": "18", "elimination_clock_time": bo_row["elimination_clock_time"],
    "elimination_clock_seconds": bo_row["elimination_clock_seconds"],
    "elimination_type": "over_top_rope", "elimination_method": "Payback spot: Barrett, already "
    "eliminated by Dallas moments earlier (elim #20), returned to ringside and pulled/struck "
    "Dallas (a Bullhammer Elbow per eWrestlingNews's recap) to cause his elimination too.",
    "location_side": "", "location_status": "UNKNOWN", "is_solo": "TRUE", "is_shared": "FALSE",
    "is_accidental": "FALSE", "is_self_elimination": "FALSE", "is_storyline_related": "TRUE",
    "was_already_incapacitated": "FALSE", "is_disputed": "FALSE", "simultaneous_group_id": "",
    "data_quality_status": "CONFIRMED",
    "source_ids": f"{S_WRESTLINGINC};{S_WWEBRADY};{S_EWN}",
    "notes": "Filled during Shane's 2026-09-18 quality-check pass. Unusual case: the eliminator "
             "(Wade Barrett) had himself already been eliminated one spot earlier in the same "
             "match, by the same wrestler he then eliminated -- 3 independent sources agree on "
             "this sequence.",
})

new_flag(
    "RR2013M", "entrants", "santino-marella;prince-albert;hunico;bo-dallas", "eliminated_by_ids",
    "corrected",
    "Shane's quality-check pass specifically named Santino Marella (-> Cody Rhodes) and Tensai "
    "(-> Kofi Kingston, wrestler_id prince-albert) as unrecorded eliminations; checking the rest "
    "of RR2013M's originally-blank eliminated_by_ids turned up 2 more resolvable gaps: Sin Cara "
    "(wrestler_id hunico) -> Ryback, and Bo Dallas -> Wade Barrett (a post-elimination "
    "interference spot -- Barrett eliminated Dallas right back after Dallas had just eliminated "
    "him). All 4 confirmed via 2+ independent sources each. A 5th gap, Brodus Clay, was NOT "
    "resolved -- every source checked describes a gang elimination without naming individual "
    "contributors, and this project's rule is to flag rather than guess -- see F336.",
    f"{S_WRESTLINGINC};{S_SPORTSKEEDA};{S_WIKI_2013_16};{S_WWEBRADY};{S_EWN}", status="resolved",
)

new_flag(
    "RR2013M", "entrants", "brodus-clay", "eliminated_by_ids", "unverified",
    "Brodus Clay's eliminator(s) could not be resolved this pass. Every source checked "
    "(WrestlingInc.com, Sportskeeda, wwebrady.fandom.com, eWrestlingNews.com) independently "
    "describes this as a gang elimination ('multiple people' / 'a number of wrestlers' / "
    "'everyone gangs up on Brodus Clay ... because he's the widest') but none names the "
    "individual contributor(s). Left unrecorded rather than guessing; worth another pass with "
    "narrower/alternate sources (e.g. a play-by-play transcript) if this matters for a specific "
    "stat later.",
    f"{S_WRESTLINGINC};{S_SPORTSKEEDA};{S_WWEBRADY};{S_EWN}", status="open",
)

save("wrestlers.csv", wrestlers, WRESTLERS_FIELDS)
save("entrants.csv", entrants, ENTRANTS_FIELDS)
save("eliminations.csv", eliminations, ELIM_FIELDS)
save("flags.csv", flags, FLAGS_FIELDS)
save("sources.csv", sources, SOURCES_FIELDS)

print("Hulk Hogan deceased_date set to 2025-07-24.")
print("2013 Royal Rumble: filled 4 of 5 originally-blank eliminations (santino-marella, "
      "prince-albert/Tensai, hunico/Sin Cara, bo-dallas); brodus-clay left open (F336, no "
      "source names an individual eliminator).")
print(f"Logged {new_flag.ctr - 334} flags (F{334:03d}-F{new_flag.ctr - 1:03d}), 3 new sources (S126-S128).")
