# Deep Research Handoff — Fill the Gaps, Efficiently

Shane's instruction for this pass: search broadly, find whatever you can as
you go rather than working one narrow task at a time, and be as efficient as
possible. This document tells you what's outstanding, how to work through it
without wasting passes, and the rules that keep the database trustworthy
while you do it. Read it in full before starting.

This is a **full handoff**: you're writing research findings back (or
writing directly to the database files, if that's the arrangement in place
when you read this) to the same standard as everything already built here.
Nothing about rigor is relaxed because the work is being done externally.

---

## 0. The prime directive: never invent data

If you can't find a reliable source for a field, leave it blank and, if it
matters, log it in `flags.csv` (`issue_type = "unverified"` or
`"needs_human_judgement"`). Never guess a plausible date, hometown,
elimination order, or title reign. A blank cell is honest; a guessed one
corrupts the database permanently and silently. This overrides every
convenience below, including "be efficient."

Read `DEFINITIONS.md` and `scripts/schema.py` before writing anything if you
haven't already — they're the fixed vocabulary and field lists for every
table. The status vocabulary (`CONFIRMED` / `DERIVED` / `PROBABLE` /
`UNCERTAIN` / `CONFLICTING` / `UNKNOWN` / `N/A`) and the source-tier list are
unchanged from every prior handoff; see `BUILD_INSTRUCTIONS.md` §1 for the
full recap if you need it.

**Current max IDs — recompute before you use the next one, don't count up by
hand across a long session:**

```python
import csv
def maxnum(path, col, prefix):
    with open(path, newline="", encoding="utf-8") as f:
        nums = [int(r[col][len(prefix):]) for r in csv.DictReader(f) if r.get(col) and r[col].startswith(prefix)]
    return max(nums) if nums else 0
print("next source id: S" + str(maxnum("sources.csv", "source_id", "S") + 1))
print("next flag id: F" + str(maxnum("flags.csv", "flag_id", "F") + 1))
print("next moment id: NM" + str(maxnum("notable_moments.csv", "moment_id", "NM") + 1))
```
As of this handoff (2026-09-28): next available are **S1842**, **F563**, **NM140**.

---

## 1. The efficiency principle — how Shane wants this pass to run

Every bucket below (biographies, ring-occupancy timing, ratings, title
histories) has historically been researched as its own separate sweep, one
wrestler or one event at a time. That's slow and re-visits the same pages
repeatedly — a single Wikipedia wrestler article often has the answer to
three or four of the buckets below at once (nationality, HOF year, deceased
status, and sometimes a title reign, all on one page).

**Work source-by-source, not bucket-by-bucket.** When you open a wrestler's
Wikipedia page, Cagematch profile, or a promotion's title-history page,
extract *everything relevant on that page* in one pass — bio fields, title
reigns, HOF status, death date, whatever's there — rather than closing the
page and coming back to it later for a different bucket. Batch your own work
by *source*, not by *field*. This is purely about your own research
sequencing; it changes nothing about the sourcing/status/flag rules below.

Practical shape this takes:
- When you're already on a wrestler's profile page for a bio gap (§2), pull
  their title history at the same time if the page has one — even though
  that data lands in a different table (§4).
- When researching a promotion's title history (§4) and you land on a
  champion's own bio page to confirm a reign date, grab their missing bio
  fields (§2) while you're there instead of queuing them for later.
- Group your fetches by *site* where practical (e.g. do every Cagematch
  lookup you need in one stretch, then every Wikipedia one) rather than
  round-tripping the same site repeatedly across buckets.

---

## 2. Bucket A — Wrestler biography backlog

**335 of 530 wrestlers (63%) have no `nationality` filled in.** This is the
single highest-value field to chase right now — it directly unlocks the new
per-event nationality/billed-country breakdown Shane's asked for on the
dashboard (a fast build once the data exists, see the companion stat-side
work). Prioritize nationality over the other bio fields below if you have to
choose, but grab whatever else is on the same page regardless (§1).

Other known gaps, lower volume but still open:
- **Residual physical-profile blanks** (F559): Paul Roma, Timothy Well,
  Kevin Thorn, Zelina Vega (height/hometown), Roxanne Perez, Kelani Jordan
  (billed weight). No reliable source found in prior passes — worth one more
  targeted look each, otherwise leave as-is.
- **Deceased-status and WWE Hall of Fame audits.** Both have been found
  repeatedly through *incidental* discovery across the fact-check sweep (18+
  HOF completions, a new death found almost every batch) rather than a
  dedicated database-wide pass. It's genuinely unclear whether either is now
  complete. If you're already open on a wrestler's page for another reason,
  check both fields while you're there rather than assuming they're settled.
- **Doink / Doink-1995 (wrestler_ids `doink` and `doink-1995`)** — just
  resolved (2026-09-28): both rows now correctly show real_name "Ray
  Licameli" / alias "Ray Apollo" per IMDb, thesmackdownhotel.com, and
  prowrestling.fandom.com. No action needed here, just don't re-open it.

**Sourcing bar:** 2 independent sources for CONFIRMED, same as every prior
pass. Wikipedia + one of Cagematch/thesmackdownhotel.com/ProFightDB is the
usual pairing.

---

## 3. Bucket B — Ring-occupancy timing gaps (7 events)

`ring_occupancy_stats.csv` has **no row at all** (not just an incomplete
one) for: **RR1989M, RR2024M, RR2024W, RR2025M, RR2025W, RR2026M, RR2026W**.

For the 6 recent years, the underlying entrant data isn't the problem — each
entrant's own `ring_time` (their individual survival duration) is already
populated. What's missing is **entry-interval / "buzzer gap" timing**: the
elapsed time between each entrant's arrival, which is what lets a shared
match clock (and therefore a ring-occupancy-over-time curve) be
reconstructed at all. This is the same gap flagged as F361 when 2017 was
first built externally, and it's recurred for every year since that doesn't
have a Cageside-style fan-timed entrance graphic.

What to look for specifically: entrance-timing graphics or tables (the kind
Cageside Seats and similar recap sites sometimes publish, showing each
entrant's clock-in time to the second), or any source that gives a running
match clock alongside the entrant order. If you find one for any of these 7
events, that's enough to populate `entrances.csv`'s timing fields and let
`build_derived.py` compute the occupancy curve — don't try to hand-derive it
yourself from partial data.

RR1989M is a special case: it previously had derived clock values that
turned out to have silently overwritten CONFIRMED data (F561/F562, now
reverted) — if you find a genuine source for its timing, flag it clearly as
new rather than assuming it matches whatever was there before.

If no such source exists for a given event after a real search, leave it —
this is exactly the kind of gap where UNKNOWN is the honest answer, not a
research failure.

---

## 4. Bucket C — Royal Rumble event ratings

Not tracked anywhere in this database yet. Shane wants this added as a new
reference table: `event_ratings.csv`.

**Proposed schema** (add to `scripts/schema.py` if you're writing directly,
otherwise just follow this shape in whatever you hand back):

```
EVENT_RATINGS_FIELDS = [
    "rating_id", "event_id", "source_name", "rating_scale", "rating_value",
    "rating_type", "review_url", "rating_status", "source_ids", "notes",
]
```
- `rating_scale`: describe it plainly (e.g. `"out of 5 stars"`,
  `"out of 10"`, `"letter grade"`) — don't normalize different scales into
  one number, preserve each source's own scale.
- `rating_type`: `"critic_review"` | `"fan_aggregate"` | `"match_rating"` —
  a whole-show review reads differently from a Dave Meltzer-style star
  rating for the Rumble match specifically; keep them distinct rather than
  collapsing to one row per event.
- Multiple rows per event are expected and correct (one per source/rater) —
  this is a raw-observations table, not a single blended score. Don't
  average sources together into one "final" rating; that's exactly the kind
  of derived-value invention the project avoids. If Shane wants an aggregate
  later, that's a `build_derived.py` computation off this raw table, not
  something to hand-calculate now.
- Good source types to look for: Dave Meltzer/Wrestling Observer star
  ratings (widely cited, often summarized on secondary sites — cite the
  original Observer issue where you can, a secondary site's report of it
  otherwise, flagged accordingly), Cagematch's user-rating aggregate for the
  match, contemporary press reviews.
- `rating_status` follows the usual vocabulary — most of these will land as
  PROBABLE (single source) since ratings by nature come from one named
  critic/outlet at a time; that's expected, not a problem to fix.

---

## 5. Bucket D — Title histories / `championships.csv` (the big one)

Shane's ask: pull title histories from the major companies so the database
can map which entrants were reigning, former, or future champions at each
Royal Rumble — not just WWE's own titles (already partly captured via each
entrant's `current_champion_title` field), but a proper standalone
title-history table that works across companies and independent of Rumble
appearances.

**This is large. Scope it in this order, don't try to do everything at
once:**

1. **WWE titles first** (WWF/WWE/WWE-branded titles across the full
   1988–2026 span this database covers: WWE/WWF Championship, Intercontinental,
   World Heavyweight (2002–2013 brand-split era and 2016–2021), Tag Team
   (both eras), Women's/Divas, Cruiserweight, etc.) — this is what almost
   every entrant's own career touches, and it's what most directly answers
   "who was a reigning/former/future champion in this specific Rumble
   field," which is the actual question Shane wants answered.
2. **Then WCW and ECW** (1988–2001, since both closed in 2001) — relevant
   for any entrant who had a notable run there, especially anyone flagged
   in this database's own notes as a crossover/invasion-era entrant.
3. **Then AEW, NJPW, and Impact/TNA** for anyone in the database's more
   recent (2018+) fields who's held a title at one of those.
4. **Stop there** unless a specific entrant's notes point somewhere else
   (a territory-era NWA title, for instance) — don't go looking for every
   regional title a wrestler ever held. The goal is "meaningfully connects
   to their Rumble appearance," not exhaustive title-history completism.

**Proposed schema:**

```
CHAMPIONSHIPS_FIELDS = [
    "reign_id", "title_name", "promotion", "wrestler_id", "reign_number",
    "reign_start_date", "reign_end_date", "reign_length_days",
    "reign_length_status", "won_from_wrestler_id", "lost_to_wrestler_id",
    "won_location", "notes", "source_ids", "data_quality_status",
]
```
- `wrestler_id`: reuse this database's own existing IDs wherever the champion
  is already a wrestler in this database (check first, same discipline as
  §3 of `BUILD_INSTRUCTIONS.md`). For a champion who's never appeared in a
  Royal Rumble and therefore has no existing ID, it's fine to leave this
  table's row unlinked (blank `wrestler_id`, name in `notes`) rather than
  inventing a new wrestler_id purely for a title-history row — the point of
  this table is to enrich entrants already in the database, not to import
  every champion of every title.
- `reign_length_days`: DERIVED from start/end dates, only compute it when
  both dates are CONFIRMED or PROBABLE — leave UNKNOWN rather than
  estimating from a fuzzy range.
- Good sources: Wikipedia's own "List of WWE Champions"-style pages (these
  are generally well-maintained and cite their own sources), Cagematch's
  title-history pages (title search → title page → full reign list),
  ProFightDB. Cross-check reign dates the same way entrant/elimination
  tables have always been cross-checked in this project — **don't trust a
  single AI-summarized fetch of a long ordered table**; this database has
  been burned by exactly that failure mode before (scrambled 1988/1992
  elimination tables). Demand a literal, row-by-row transcription, or fetch
  the same table from two sources and diff them.
- Once a reasonable slice of this table exists, it unlocks (for a later
  pass, not this one): "days into title reign at time of entry," "future
  world champions in the field" computed properly instead of via the
  existing single-flag heuristic, and a dedicated champion-history browser
  page on the dashboard (already on the outstanding-features list).

---

## 6. Before you write anything to the live database

Same discipline as every prior handoff:
1. Test in an isolated copy first (`cp -r data /tmp/rr_test_data` or
   equivalent) — build/patch scripts against that copy.
2. Run `python3 scripts/validate_integrity.py <test-data-dir>` and confirm
   `ALL CHECKS PASSED` before touching the live `data/` directory.
3. Apply the same change to live, then re-run
   `validate_integrity.py ../data` against live and confirm it still passes.
4. Report back (or leave in `flags.csv`/a changelog) what was added, what
   was checked and came back empty, and what's still genuinely unknown —
   same as every batch write-up already in `IDEAS.md`.

If you're handing research back rather than writing directly: package it the
same way prior batches have — a plain list of field/value/source-url per
finding is enough, Claude will apply it through the same tested pipeline.

---

## 7. What NOT to do

- Don't invent a rating, a title reign, or a nationality because it "seems
  likely." Leave it blank.
- Don't average/blend multiple sources into one number for the ratings
  table — preserve each source's own rating as its own row.
- Don't create a new `wrestler_id` for a champion who's never been in a
  Royal Rumble. Link by name in `notes` instead.
- Don't try to complete every regional title history in wrestling. Stop at
  the scope in §5.
- Don't trust a single AI-summarized fetch of a long ordered table (title
  histories, elimination tables) without a second, independent check.
