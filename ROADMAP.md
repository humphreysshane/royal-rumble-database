# Roadmap — where the database goes from here (2026-09-23)

Written the moment the chronological build finished (1988–2026, 48 events, Men's
and Women's both current through RR2026). Per Shane's own 2026-09-21 sequencing
decision ("keep building new years first... this whole wishlist is a backlog to
pick up once that sequence catches up to today"), that day has arrived — this
file is the pickup point. See `IDEAS.md` for the full history of how each of
these items was identified; this file is the acted-on version, prioritized.

## 0. Where things stand right now

- 48 events live (1988–2026), Men's + Women's fully separated throughout the
  derived layer and dashboard (Version 19+ architecture).
- Dashboard: **Version 31** — RR2021–2026 merged, 7 new "Phase A" record
  categories (most career eliminations/appearances without ever winning, most
  eliminations in a single Rumble without winning it, longest gap between
  appearances, longest consecutive-year streak, most distinct wrestlers
  eliminated across a career and its inverse), a "Hall of Famers already
  inducted at the time" record, an honesty fix on the Physical/Age records
  (see below), an Entry Number Statistics page, a wrestler-profile Rivalries
  panel, the legacy data cleanup (see §1), the RR1994M co-winner schema fix
  (see §1), a new **Explore** page (see §6), peak ring-occupancy stats +
  Host Locations pages from the external AI's Phase A handoff merged with a
  bug fix to the occupancy calculation (see §7), the full `order_in_match`
  resolution + a broad Phase B biography backfill + RR1991M/RR1992M physical
  profiles from the external AI's Phase C1/C2 handoff (see §8), and — from
  the external AI's Phase C3–C14 cumulative handoff (see §9) — complete
  character alignment (1,442/1,442 entrant rows) and near-complete billed
  physical profiles (height/weight/hometown, ~99% of entrant rows, up from
  ~12%) database-wide — all shipped 2026-09-23/24.
- **0 validator errors, down from 51.** The legacy cleanup closed 39 of the
  original 51 (see §1), the RR1994M co-winner fix closed 1 more, and the
  external AI's Phase C1/C2 handoff (§8) closed the remaining 10
  `order_in_match` gaps with genuine sourced research, independently verified
  before merging — see §8 for the full verification writeup.
  `validate_integrity.py`'s own output confirms the count before/after every
  change this session, independently re-run by me rather than trusted from
  any report.
- Editable video-analysis workflow (§4) has a working first version:
  `Video_Analysis_Entry_Template.xlsx` (project root) +
  `scripts/ingest_video_template.py`, tested end to end.
- **Found 2026-09-23, fixed the same day**: the "Oldest/Youngest entrant
  ever" and all 4 "Heaviest/Lightest/Tallest/Shortest" records were computed
  correctly (no invented data) but from a tiny, non-representative sample —
  `age_at_event` is populated for only 76 of 1,443 entrant rows (5.3%),
  `billed_weight_kg_at_event`/`billed_height_m_at_event` for only 50 (3.5%),
  and **every single one of those rows comes from RR1988–RR1990** (Shane's
  own original source document had this level of detail only for the
  earliest years; nothing since has backfilled it). So "Oldest entrant ever:
  Bad News Brown" was really "oldest among the 76 entrants anyone's ever
  looked up an age for" — true as far as it went, but presented with no hint
  of that. Fixed by making `build_derived.py` attach a dynamic coverage note
  to each of these 6 records (sample size, % of the division, and which
  years are actually covered), rather than either hiding the gap or trying
  to force-fix it with invented ages/weights/heights. **This is the single
  most visible symptom of Phase B (§3) not having started yet** — it's the
  same `entrants.csv` sparse-field problem the 2026-09-21 audit already
  documented, just now visible on the live dashboard instead of buried in an
  audit note. Worth treating Physical/Age as the FIRST Phase B batch once
  that work starts, ahead of the other sparse fields, specifically because
  it's the one actively producing a misleading "record" today. If you spot
  another record that looks similarly thin, it's very likely the same root
  cause (a record computed honestly from whatever subset has been
  researched) — worth asking rather than assuming a computation bug, though
  I'd rather you flag it either way than let it sit.

## 1. Legacy data-quality cleanup (51 errors) — DONE 2026-09-23, 51 → 12

The external AI took this on (per §5's kickoff prompt) and delivered a fully
isolated, sourced proposal, which I independently re-verified from scratch
(re-ran the validator myself rather than trusting its report, CSV-diffed
every changed cell against live, spot-checked the riskiest changes against
wrestlers.csv/sources.csv, confirmed wrestlers.csv/tag_teams.csv/
other_matches.csv/near_eliminations.csv/moves.csv/entrances.csv and every
2021–2026 event were byte-for-byte untouched, rebuilt derived+dashboard from
the merged result, and smoke-tested) before merging it into live. Full
detail in `LEGACY_CLEANUP_LIVE_20260923_REPORT.md` (project root) and
`cleanup_review/error_ledger.csv` (all 51 original errors individually
classified). Shipped as dashboard **Version 26**.

What changed: 23 literal-"UNKNOWN"-in-an-ID-field placeholders blanked (with
new field-specific `*_status` companion columns so the "why it's blank"
information isn't lost — schema.py extended additively, nothing removed); 3
dangling wrestler-ID references fixed (`the-rock` → `rocky-maivia`,
`alicia-fox-not-tracked` → `alicia-fox`, both reusing existing canonical IDs,
no new identity invented); NM014's stale `category` fixed; both entry-number
anomalies resolved (RR1998M's extra Triple H row moved to
`show_appearances.csv` as outside interference — Owen Hart's elimination
credit is preserved, just no longer double-counting Triple H as a numbered
entrant; RR2004M's `entrant_count` field corrected to match its actual 31
rows); 10 events' `order_in_match` gaps resynchronized from already-sourced
entrant ranks; 18 previously-uncredited eliminations added across
2001/2005/2007/2009/2012/2014, each newly sourced (S434–S445) and tagged
PROBABLE (single source) or CONFIRMED (two independent sources) per
DEFINITIONS.md — none invented, none guessed past what a cited source
actually stated.

**10 errors remain, all `order_in_match` gaps needing new research, not
further mechanical cleanup** (RR1994M/1998M/2000M/2002M/2004M/2006M/2007M/
2013M/2015M/2016M) — existing flags (F059, F091, F092, F112, F124, F135,
F163, F174, F175, F189, F220, F283, F284, F290, F309, F336) already document
why; correctly left UNKNOWN rather than reconstructed from ring times. Full
explicit worklist in `ORDER_IN_MATCH_WORKLIST.md`, which Shane is working
through from Wikipedia himself.

**RR1994M's co-winner finish — RESOLVED 2026-09-23, shipped as Version 27.**
Was: `winner_id='bret-hart;lex-luger'`, "expected exactly 1 winner, got 2".
Shane endorsed the external AI's recommended design and it's now
implemented: a new `event_winners.csv` table `(event_id, wrestler_id,
data_quality_status, source_ids, notes)` holds the declared winner set for
any event whose `events.csv:finish_type == "co_winners"` (RR1994M is
currently the only one); `validate_integrity.py` now cross-checks that set
against `entrants.csv:is_winner=TRUE` for the event; `build_dashboard_data.py`
and `dashboard/page.html` both updated to display multiple winners correctly
(event cards, hero badge, search) rather than picking one arbitrarily. Both
Bret Hart and Lex Luger were already correctly credited a win in every
derived career stat before this fix (`build_derived.py` reads
`entrants.csv:is_winner`, not the old single-ID `events.csv:winner_id`) — this
fix was about the event-level record and the dashboard display catching up
to that, not about who actually won. F060 (the underlying whose-feet-hit-
first controversy) stays open on purpose — it documents a real dispute, not
a data-format problem.

## 2. Phase A — more zero-new-research dashboard/derived wins

9 of these shipped (7 in Version 28, see §0; "wrestlers in the ring at the
same time" and the host arena/city pages in Version 29, see §7 — the external
AI's submission, merged with a bug fix). Remaining, all computable from data
already in the database, no new research needed:

- **Rumbles with the most Hall of Famers in the field AT THE TIME (not just
  eventually)** — `event_dynamic_stats.csv` already has `hof_members_at_time_count`
  computed, just not surfaced as its own record category yet (currently only
  the "eventual" HOF count is a tracked record).

This is an "I write the code, test in isolation, deploy" task — good next
slice for me to keep working through, no external-AI involvement needed.

## 3. Phase B — the big one: per-appearance biography backfill

Needs new research across **every existing entrant row**, not just new years
going forward. Current fill rates (audited 2026-09-21, ~1,022 entrant rows at
the time — now ~1,444): `alignment`, `billed_height_m_at_event`,
`billed_weight_kg_at_event`, `billed_from_at_event` each under 5% filled;
`tag_team_name` ~4%; `current_champion_title` ~2%; `prior_rumble_appearances_count`
~8%; `gimmick_at_event`/`manager_at_event` near 0%.

**Underway** — the external AI has been working through this in parallel
(see §8, Version 30): championships, tag teams, factions, gimmicks and
managers now have real coverage across most of 1988–2026, and RR1991M/
RR1992M are fully backfilled for physical profiles (height/weight/billed
-from). Shane's standing decisions on how to run it (from 2026-09-21, still
in force): go **oldest to newest** (1988 forward), and `ethnicity_heritage`
is tracked as a new field **only where a wrestler has publicly self-described
it** in reliable sources — never inferred/assigned. Next up per the external
AI's own plan: RR1993M–RR1996M physical profiles, resolving the open
conflicts flagged in §8 (F522–F527), and auditing 1988–1990 for the same
kind of gaps just closed in 1991–1992.

**Recommended owner: the external AI, as the ongoing parallel track once §1 is
done.** This is exactly the kind of large, well-defined, batchable research
work the RR2021-2026 build proved out — same event-by-event pace, same
build-script-per-batch pattern, same isolated-test-then-report-back loop. I'd
suggest batches of 4-8 events at a time (1988-1992, 1993-1996, etc.,
matching the fact-check sweep's own batch sizing from earlier in this
project), each one a self-contained build script that adds the new fields to
existing entrant rows rather than touching anything else.

## 4. Editability for Shane's own video analysis

**Built this session, first working version:**

- `Video_Analysis_Entry_Template.xlsx` (project root) — one tab each for
  Entrances / Near Eliminations / Moves, matching `entrances.csv` /
  `near_eliminations.csv` / `moves.csv` exactly. Dropdown suggestions (not
  locked) for every TRUE/FALSE-ish and enum-ish field, an Event ID Reference
  tab and a searchable Wrestler ID Reference tab (531 names) so you're never
  hand-typing an id from memory, an example row on each tab, and a Read Me
  explaining the workflow.
- `scripts/ingest_video_template.py` — reads a filled-in copy back, cross-
  checks every event_id/wrestler_id against the live database (catches a typo
  before it becomes a bad row), appends the new rows to the 3 CSVs, and
  reports problems without silently dropping them. Tested end to end this
  session (valid row appended correctly, a deliberately-wrong wrestler_id was
  caught and flagged, `validate_integrity.py` stayed clean after).

**Why Excel and not a live web-editable dashboard**: a page published to
claude.ai runs entirely in your browser — it has no way to write back to this
project's actual CSV files, which live in Claude's own workspace. A true
"live" editor would mean either routing everything through Google Sheets +
an API sync, or a custom backend service — much bigger lift for a workflow
that's fundamentally "I watch footage, I log what I see, it gets folded in
later," not something that needs real-time collaboration. The Excel round
trip gets you dropdowns, validation, filtering and a familiar tool with
none of that infrastructure, and it slots into the exact same
test-in-isolation-then-merge pipeline every other contribution to this
database already goes through.

**Not yet decided / worth your steer:**
- The suggested vocabularies I picked for `move_category` (strike, slam,
  submission, aerial, weapon, throw_over_top, other) and `confidence`
  (HIGH/MEDIUM/LOW) aren't from any existing schema convention — I invented
  them as a reasonable starting point. Tell me if you want different buckets
  before you're 50 rows into using them, since the dropdown is just a
  suggestion (you can type over it) but changing the *intended* vocabulary
  later means revisiting whatever's already logged.
- These 3 tables aren't wired into `build_derived.py` or the dashboard at
  all yet — logging data into them doesn't produce any visible stat until
  Phase C builds something that reads them. Worth deciding whether that's
  worth doing once you've got a real batch of footage-logged data, or
  whether the tables are more useful as a raw reference layer that never
  needs its own UI.

## 5. Ready-to-paste kickoff prompt for the external AI (legacy cleanup, §1)

**COMPLETED 2026-09-23 — see §1 for the result.** Left below as a record of
what was sent, in case a similarly-scoped task needs a kickoff prompt later.

**Yes, use a fresh copy of the database for this** — a lot has changed since
whatever zip it last worked from: RR2021–2026 are merged into the live
database now (48 events total), `validate_integrity.py` has 3 rounds of
changes since (no-show handling, the notable_moments category check, and its
own documented-substitution logic), and the Physical/Age record coverage fix
above landed today. Hand it
`royal_rumble_database_through_RR2026_LIVE_20260923.zip` (in this
conversation) rather than letting it keep working from an older copy —
anything older is missing real changes to the shared tooling it'll be
running.

```
Next task on the Royal Rumble Database: a legacy data-quality cleanup pass,
NOT new years. This is a FRESH copy of the database (through RR2026, dated
2026-09-23) -- if you've worked from an older zip before, discard it and
work only from this one; several things changed since, including
validate_integrity.py itself. Re-familiarize yourself with DEFINITIONS.md
and BUILD_INSTRUCTIONS.md first if it's been a while.

Run `python3 scripts/validate_integrity.py data` against the full live
database (no event_id args, so it checks everything) — you should get
exactly 51 errors. Fix all of them EXCEPT the RR1994M two-winner issue
(events.csv winner_id='bret-hart;lex-luger') — flag that one back to me
with your recommendation instead of fixing it, since it's WWE's own
real co-winner finish and might need a schema/validator change rather
than a data fix.

The other 50 fall into 3 groups:
1. Literal "UNKNOWN" text living inside an ID field (events.csv
   winner_id/runner_up_id/first_entrant_id/etc. for several 1994-2006
   events; entrants.csv eliminated_by_ids for RR1994M). Fix: blank the
   field itself, and make sure there's a *_status=UNKNOWN plus a flags.csv
   row explaining why it's unknown (check flags.csv first -- some of these
   may already have an explanatory flag that just never got the field
   itself cleaned up to match).
2. order_in_match gaps across ~15 events, 1994-2016 (the validator's own
   error message tells you exactly which orders are missing per event).
   Before touching any of these, check flags.csv for that event first --
   several years are documented as having no timing-analysis source at
   all (e.g. F112 for 1998), which means a real, permanent gap, not a bug
   to force-fill. Only actually fix the ones where the gap looks like a
   genuine oversight rather than an already-documented sourcing limit --
   flag the rest back to me with which flag already explains them.
3. RR1998M/RR2004M entry-number anomalies (duplicate/missing entry
   numbers) and notable_moments.csv NM014's category='upset' (just needs
   to become one of this database's actual category values -- see
   VALID_NM_CATEGORY in scripts/validate_integrity.py).

Test everything in an isolated copy first, exactly like every prior batch:
copy scripts+data elsewhere, make your fixes, re-run
validate_integrity.py against the copy (should drop from 51 to however
many are genuinely left after group 2's carve-outs), THEN stop and send
the results back rather than touching live data yourself -- same handoff
pattern as the RR2024-2026 batch. Tell me plainly which of the 51 you
fixed, which you left as genuine pre-existing sourcing gaps (with the
flag_id that already documents each one), and what you recommend for the
RR1994M two-winner case.
```

## Suggested order

1. Hand §1's cleanup to the external AI now (prompt above) — mechanical,
   fully scoped, doesn't block anything else.
2. I keep working through §2 (Phase A dashboard wins) in parallel — no
   research dependency, I can just build these.
3. Once §1 comes back clean, external AI starts §3 (Phase B biography
   backfill), 1988 forward, in batches — the long-running track from here on.
4. §4 (video analysis) is ready whenever you want to start logging footage —
   no dependency on anything else above.

## 6. Explore page — shipped 2026-09-23 (Version 28)

Shane's ask: be able to type a number, a keyword, or a wrestler's name and
immediately pull every relevant stat/record/moment already in the database —
concretely, the "video on the number 23" / "video on a steel chair" / "video
on Shawn Michaels" use cases. Built while the external AI works through §1/§2/
§3 in parallel, deliberately scoped to touch **only** `scripts/build_dashboard_data.py`
and `dashboard/page.html` — zero changes to any file under `data/`, so there's
no collision risk with whatever the external AI hands back.

**What it does**, all computed or copied from data already in the database
(no new research, nothing invented):
- A per-(division, entry number) highlight card — appearances, win rate,
  every winner from that number, the longest survival and most eliminations
  made from that number and who holds them. Typing a bare number (1–40)
  surfaces this directly.
- Every `records.csv` row and every `notable_moments.csv` row (139 of them,
  previously only visible buried on their own event's page — now searchable
  from anywhere), plus a handful of auto-generated trivia facts about
  genuinely rare field sizes (1988's 20-man field, 2011's 40-man field, the
  two 31-man fields).
- Full-text search over `eliminations.csv`'s own sourced `elimination_method`
  narrative text — e.g. searching "chair" surfaces every elimination whose
  already-sourced description happens to mention one. This is real existing
  sourced text shown as-is, not a curated "weapon" tag (no such field
  exists), so nothing is being asserted that isn't already in the database.
- Wrestler name/alias/birthplace/nationality search, linking straight to
  their profile.

**Two known, honestly-surfaced gaps** (the page says so directly rather than
returning misleading empty results):
- Hometown search is only as good as `billed_from_at_event`'s current ~3.5%
  fill rate. This **improves automatically, with no dashboard changes
  needed**, as the external AI's Phase B backfill (§3) lands — genuine
  synergy between the two parallel tracks.
- There's no "masked wrestler" gimmick tag anywhere in the database (search
  still works reasonably well for this today only by accident, e.g. Alexa
  Bliss's "La Luchadora" alias already being in `wrestlers.csv`). A real
  masked/gimmick-type tag would need new, deliberate tagging work — not
  something to guess at. Worth scoping as its own small addendum if Shane
  wants it.

**Bigger idea flagged, not started**: Shane also wants non-official Royal
Rumbles (house-show/dark-match/international versions) added, with their own
stats and cross-tagged onto wrestler bios. This is a much bigger initiative
than a dashboard feature — it's new event *research and sourcing* at roughly
the scale of Phase B, plus a schema decision (a separate table? a flag on
`events.csv`? how "official" is defined and sourced). Deliberately not
started without a scoping conversation first, consistent with this project's
"never invent data" discipline — an "unofficial Rumble" catalog invented or
loosely sourced would undermine the exact rigor the rest of the database is
built on.

## 7. Phase A merge (peak ring occupancy + Host Locations) — shipped 2026-09-23 (Version 29)

The external AI submitted its first Phase A handoff (`ring_occupancy_stats.csv`
+ record `R045` "Most wrestlers simultaneously in the ring", plus Men's/Women's
Host Locations venue/city pages) as a zip + `PHASE_A_REPORT.md`. Independently
verified before merging to live, per this project's standing rule — never
trust an external contributor's report at face value:

- Confirmed byte-for-byte that every raw `data/*.csv` source file was
  genuinely untouched, matching the report's claim.
- Reproduced their entire derived-data output from live source data using
  their own submitted `schema.py`/`build_derived.py` (not their supplied
  output files), confirming the computation is deterministic and does what
  the report says.
- **Found and fixed a real bug** in the ring-occupancy peak-concurrency
  calculation: a match winner's `elim_number_status` is legitimately `"N/A"`
  (the field doesn't apply — they were never eliminated), the same literal
  value used to mark a genuine no-show. The submitted code's entrant filter
  (`elim_number_status != "N/A"`) didn't distinguish the two, so it silently
  dropped the winner from every single event's occupancy count (verified:
  winner absent from all 12 submitted `wrestler_ids_at_peak` lists) — this
  codebase's own established convention for this exact ambiguity (already
  used in `validate_integrity.py`'s no-show detection) guards with
  `is_winner != "TRUE"`, which the new code omitted. Fixed by adding that
  guard. **Record R045's value changed from the submitted 14 to the correct
  15** (RR2009M, window 39:33–39:37); 5 of the 12 computed events changed in
  total (RR1999M 9→10, RR2009M 14→15, RR2012M 8→9, RR2013M 11→12, RR2014M
  10→11 — RR2012M and RR2014M's windows also moved). The other 7 events were
  coincidentally unaffected.
- Manually three-way-merged `scripts/build_dashboard_data.py` and
  `dashboard/page.html`: the external AI's diff was generated against the
  pre-Explore snapshot, so it would have silently deleted the entire Explore
  page (§6, Version 28) if copied over directly. Both features now coexist
  — verified with 34 Playwright checks covering Host Locations (Men's +
  Women's venue/city pages, 34/24 Men's and 9/8 Women's groups, matching the
  report's counts), the corrected peak-occupancy display on event pages, and
  full regression of the pre-existing pages (co-winner display, Explore
  search, wrestler profiles, records).
- `validate_integrity.py`: confirmed still exactly 10 errors (the
  `order_in_match` gaps), no regression.
- Every pre-existing `record_id`/`history_id` preserved; `R045`/`H0154` are
  the only new rows, now holding the corrected value.

## 8. Order-in-match resolution + Phase B backfill + RR1991M/RR1992M physical profiles — shipped 2026-09-23 (Version 30)

The external AI sent a "Phase C2" report describing only 24 RR1991M/RR1992M
physical-profile rows, but the zip Shane forwarded was — as its own text said
— a **cumulative** handoff: it also carried an entire unreported prior phase
(evidently "Phase C1") that resolved every one of the 10 `order_in_match`
gaps from `ORDER_IN_MATCH_WORKLIST.md`, plus a broad Phase B biography
backfill (championships, tag teams, factions, gimmicks, managers, ages)
spanning nearly every event from 1988 to 2026. The actual diff against
Version 29 was thousands of field changes across `entrants.csv`,
`eliminations.csv`, `sources.csv`, `flags.csv` and `wrestlers.csv` — not the
24 rows the report described. Given the scale, and that this is exactly the
kind of gap this project's whole discipline exists to catch, I verified this
as its own pass before merging anything:

- **Full pipeline reproducibility**: rebuilt every derived table
  (`career_stats.csv`, `records.csv`, `records_history.csv`,
  `ring_occupancy_stats.csv`, etc.) and `dashboard/data.json` from the
  submission's raw `data/` using its own (byte-identical-to-live)
  `build_derived.py`/`build_dashboard_data.py` — every output matched the
  submitted files byte-for-byte, confirming the whole thing is deterministic
  and non-fabricated at the pipeline level.
- **The `order_in_match` fill matches the worklist precisely**: cross-checked
  the new `eliminations.csv` rows against `ORDER_IN_MATCH_WORKLIST.md`'s own
  Type A (RR1994M, RR1998M, RR2000M, RR2002M, RR2004M, RR2006M — full order
  built from scratch) / Type B (RR2007M, RR2013M, RR2015M, RR2016M — just
  missing eliminator credits) split, and the row counts matched exactly.
- **Genuine conflict-handling, not fabrication**: RR2015M's Curtis Axel is
  modeled as a CONFLICTING storyline exit (flag F522) rather than an invented
  elimination, because Wikipedia and Pro Wrestling History both say he never
  actually entered after an Erick Rowan backstage attack — independently
  confirmed via WWE's own site
  ([wwe.com](https://www.wwe.com/videos/curtis-axel-is-attacked-by-erick-rowan-never-being-eliminated-from-the-royal-rumble-match)).
  Two more conflicts (Tugboat's height, Sgt. Slaughter's weight — current vs.
  archived Wikipedia) and two wrestler-master-data conflicts (Paul Roma's
  DOB, Virgil's DOB/birthplace) were flagged and left unresolved rather than
  picked, per the project's own rules.
- **`validate_integrity.py` was itself patched** — a genuine, necessary fix:
  the RR1994M co-winner formula (`n - 1 - no_shows`, from my own Version 27
  work) never accounted for a *second* winner, so it would have wrongly
  flagged RR1994M as short one elimination once its order was actually
  filled in. The external AI's fix (`n - len(winners) - no_shows`) is
  correct — confirmed by running the OLD validator against the new data and
  watching it mis-fire exactly as predicted, then confirming the new formula
  gives the right answer. Adopted into live's `validate_integrity.py`.
- **The `ethnicity_heritage`/`ethnicity_heritage_status` fields added to
  `wrestlers.csv`** are not a surprise — they're my own standing decision
  from `ROADMAP.md` §3 / the original kickoff prompt ("only where a wrestler
  has publicly self-described it"). Confirmed zero rows actually have a
  value populated, matching the report's claim.
- **Small legacy cleanup folded in**: RR1994M's two co-winners had
  `elim_number_status=UNKNOWN` (a leftover from my Version 27 co-winner fix,
  predating this submission) instead of the correct `N/A` (doesn't apply —
  they won). Fixed both rows while merging.
- `validate_integrity.py`: **0 errors, `ALL CHECKS PASSED` — down from 10.**
  Confirmed with both the submission's own validator and, separately, a
  from-scratch rebuild on live.
- Smoke-tested (13 Playwright checks): the 10 previously-gapped events now
  render full elimination tables, the new R002 record (Skinner, 98kg)
  displays correctly, and every pre-existing page (Explore, Host Locations,
  corrected peak occupancy, wrestler profiles) still works.

**One open item, not yet resolved**: the report significantly undersold the
scope of what was actually in the handoff. The work itself checked out clean
on every test available to me, but going forward it's worth asking the
external AI to report cumulative scope accurately (or asking it directly
what changed since a given baseline) rather than assuming a report's stated
scope matches the zip's actual contents.

## 9. Character alignment complete + database-wide physical profiles — shipped 2026-09-24 (Version 31)

Handoff labeled "Phase C14," starting from "Phase C13" — I never saw reports
for C3 through C13, so this section verifies the full cumulative diff against
Version 30 (the last state I'd independently checked), not just the
alignment work the report describes.

**What the report described**: `alignment`/`alignment_status` populated for
all 270 Women's entrant rows (RR2018W–RR2026W), each PROBABLE on one
qualifying source (78 TheSmackDownHotel dated Face/Heel-turn profiles,
9 Wikipedia event articles for residual context), combined with an
already-complete Men's pass to reach **1,442/1,442 entrant rows** with an
alignment value — zero blanks, for the first time.

**What the report did NOT mention, found during the diff**: `billed_height_m_at_event`,
`billed_weight_kg_at_event`, `billed_from_at_event` and `physical_status`
also jumped from ~168/1,442 (~12%) to ~1,427–1,437/1,442 (~99%) somewhere in
the unreported C3–C13 phases. This is effectively the entire Phase B
physical-profile backfill (§3) completing, silently, inside a "cumulative"
package whose own report never mentions it. Verified anyway, same rigor as
every prior phase:

- **Shared code untouched**: `schema.py`, `build_derived.py`,
  `build_dashboard_data.py`, `validate_integrity.py`, `dashboard/page.html`
  all byte-identical to Version 30 — this phase touched only
  `entrants.csv`, `sources.csv`, `flags.csv`.
- **Full pipeline reproducibility**: every derived table and
  `dashboard/data.json`, rebuilt from the submission's raw data with its own
  scripts, byte-identical to what was submitted.
- **`PHASE_C14_CHANGED_ROWS.csv` cross-checked**: its 270 listed
  (event, wrestler) pairs are the *exact* set of Women's rows whose
  `alignment` field actually changed — no more, no less.
- **31 new flags, all `conflicting_sources`**: cross-source billed-value
  disagreements (height/weight/hometown across multiple Wikipedia revisions)
  logged rather than silently picked. Consistent with the project's
  never-resolve-by-guessing rule.
- **Two independent fact-checks against outside sources**: Curtis Axel's
  RR2015M non-entry (carried over from §8, re-confirmed) and Becky Lynch's
  Heel alignment at RR2026M — confirmed she turned heel on Raw in April 2025
  ([Cageside Seats](https://www.cagesideseats.com/wwe/2025/4/21/24413591/becky-lynch-turns-heel-raw-after-mania-lyra-valkyria-liv-morgan-raquel-rodriguez)),
  consistent with Heel at a January 2026 event.
- **New records, sanity-checked**: El Torito (45 kg) and Hornswoggle (1.35 m)
  are now the Men's lightest/shortest entrants — both real, very small
  wrestlers, exactly who you'd expect to hold these once weight/height data
  existed for them. Women's physical records exist for the first time (Nia
  Jax heaviest/tallest, Kacy Catanzaro lightest/shortest) — also exactly
  who you'd expect.
- **File hash verified**: the SHA-256 Shane relayed matched the uploaded zip
  exactly.
- `validate_integrity.py`: **0 errors, unchanged.** Smoke-tested (9 Playwright
  checks): new Women's records display, El Torito's profile loads, and every
  pre-existing page still works.

**On Shane's "I feel we're wasting resources" message**: raised directly
with the external AI mid-handoff, which self-diagnosed the problem (alignment
run as its own isolated pass instead of pulling manager/tag-team/faction/
championship data from the same source visits) and proposed stopping further
chronological passes in favor of a database-wide gap-classification audit
first. That diagnosis matches what I found in the diff — alignment used 1,119
new sources on its own, largely separate from the physical-profile pass that
apparently happened in a different phase — and the proposed fix (classify
every blank as likely-missing / likely-N/A-needs-verifying /
derivable-from-elsewhere / genuinely-unknown, reuse the 1,683 already-
registered sources before searching for new ones, and pull several related
fields per source visit) is sound. I'd endorse running that audit before any
more chronological research passes.

**Correction, 2026-09-24**: the paragraph below originally framed this as
the external AI under-reporting scope. Shane clarified that isn't right —
the external AI did produce a report for every phase, C3 through C13
included; Shane simply hadn't forwarded each intermediate one to me for
merging, and hadn't been reporting back to the external AI after each of my
merges either. So the ~1,260-row physical-profile change wasn't hidden from
its own report — it just arrived in a report I never saw, because C14 was
the first cumulative zip forwarded to me since Version 30. The actual
process gap is upstream of the AI: every zip needs to come to me for
independent verification before the external AI is told to continue, the
same way C1/C2 and this one did, rather than several phases accumulating
unseen. That's now the standing expectation — see §10.

The observation that still stands regardless: a given report only describes
its own phase's *intent*, not the full diff against the last state I
actually checked. When phases are forwarded one at a time as they should be,
that's rarely a problem. But asking for a literal file-and-field-count diff
summary against the last known-good baseline, alongside the phase's own
report, costs the external AI little and makes independent verification
faster and more reliable regardless of forwarding cadence — kept as a
standing ask in §10.

## 10. Process fix, outstanding gaps, and new stat categories — 2026-09-24

### 10.1 Process fix: every handoff gets forwarded, not batched

Going forward, each zip from the external AI comes to me for independent
verification and merge before Shane tells it to continue — no batching of
several phases before a merge. This is what already happened for the
Phase A, C1/C2, and C14 handoffs; it just needs to happen every time, not
only when Shane remembers to forward one. Nothing for the external AI to
change here — this is on the human relay step.

### 10.2 "Col. Mustafa is the oldest competitor" — investigated, not a bug

Checked `data/derived/records.csv` (R005) and the live dashboard's rendered
`notes` field directly. This is accurately labeled, not a data error:

> "Based on the 139 of 1172 Men's entrants (11.9%) with age at event
> currently researched (years covered so far: 1988-1992) — NOT a claim
> about the other 1033 entrants, whose age at event simply hasn't been
> looked up yet."

That caveat is real and does render on the card under the record. Checked
`entrants.csv` directly: `age_at_event` is populated for exactly 140 of
1,442 rows (140/1,172 Men's), covering only RR1988M–RR1992M. Every other
event — including all of 1993–2026, where several much-older legends have
entered over the years — has never had this field researched, so the
"record" can only reflect what's been checked so far. This is the
honesty-fix mechanism working as designed (§0/§1): it's labeled as
incomplete rather than presented as definitive. But Shane's complaint is
still fair — a card headlined "Oldest entrant ever" reads as a finished
claim unless the small print underneath gets read, and right now the small
print is doing a lot of work. **`age_at_event` is added to the priority list
for the gap-classification audit (§9)** as a field that needs coverage
across all 48 events, not just 1988–1992, given how visibly it affects a
headline record.

### 10.3 New stat categories Shane wants surfaced

Researched what these actually are (Cageside Seats' Cain A. Knight stat
series, and the WhatCulture trivia-facts format) before proposing anything,
per this project's research-before-schema rule.

**Ring Crowdedness** — Cageside's version is a full breakdown of what % of
match time had exactly N wrestlers in the ring simultaneously (e.g. "7
wrestlers: 15m 14s, 25.9%"), not just the peak. Good news: `build_derived.py`
already builds a full second-by-second occupancy timeline internally to
find the peak (see the `ring_occupancy_stats.csv` section) — extending it to
record time-at-each-count instead of only the max is a derived-computation
change, **not new sourcing**. It only benefits the 12 events that currently
pass the "complete timeline" gate (`ring_occupancy_stats.csv` today), and
will extend automatically to more events as `elim_number`/`ring_time`
research fills in for the rest. Proposing this as a small, low-risk
dashboard/derived-layer change I can make directly, same rigor as the
Phase A occupancy work — not external-AI research.

**Entrance Times** (buzzer → wrestler's feet hit the ring) and **Follow the
Buzzers** (interval between consecutive buzzers vs. WWE's stated 90-second/
2-minute target) — both map directly onto the existing but currently-empty
`entrances.csv` table (`music_start_ts`, `enters_ring_ts`,
`entrance_duration_seconds`), designed for exactly this back when the
video-analysis workflow (§4, `Video_Analysis_Entry_Template.xlsx` +
`ingest_video_template.py`) was built. Two ways to populate it, not
mutually exclusive:
  - Shane's own video-timed entries via the existing template workflow
    (most rigorous — human-verified, `confidence`/`human_verified` fields
    already exist for this).
  - Citing Cageside Seats' own already-published per-event timing articles
    (their "Match Time and Statistics" and "waiting intervals" series) as a
    source, where one exists for that year — this is genuinely faster but
    coverage is uneven: Cageside has published these for some years (I
    found explicit examples for 1988, 1992, 1996, 2000, 2001, 2003, 2006,
    2014, 2016, 2018, 2023–2026, non-exhaustively) and not others. Where
    only Cageside covers a year, that's a single-source PROBABLE per this
    project's own rules, not CONFIRMED — flagged as such, not silently
    upgraded.

**Per-event trivia facts** (WhatCulture-style, e.g. "60% of RR1993's
entrants were gone by year's end") — these fit the existing
`notable_moments.csv` table (already has `category`/`title`/`description`/
`source_ids` per event) rather than needing a new table; would add a new
category value (`historical_trivia` or similar) to the existing controlled
vocabulary. One important finding: checked the actual WhatCulture article
Shane linked, and it **cites no sources at all** for its claims — not even
a general one. So WhatCulture facts can be used as a lead for what to look
for, but each one needs independent verification against a primary source
(Wikipedia, contemporary reporting, PWHistory, etc.) before it goes in the
database as CONFIRMED/PROBABLE — never copied in as-is on WhatCulture's
say-so alone. This is exactly the kind of thing the gap-classification
audit's "reuse existing sources / classify before researching" discipline
should apply to as well, so it's being folded into the same audit rather
than run as a separate ad hoc pass.

## 11. Gap-classification audit reviewed and approved — 2026-09-24

The external AI's audit (`royal_rumble_gap_classification_audit_20260924.zip`)
was independently reviewed rather than approved on trust:

- **No data touched, confirmed**: the package contains only
  `AUDIT_REPORT.md`, `gap_classification.csv`, `gap_summary.csv`,
  `remaining_queries.csv`, and the audit script itself — no `data/`,
  `scripts/`, or `dashboard/` files, matching its own claim.
- **Full reproducibility**: ran `audit_gap_classification.py` directly
  against live `data/` myself. All three CSV outputs came back byte-for-byte
  identical to the submitted files (`AUDIT_REPORT.md` differed only in line
  endings — CRLF vs LF, a platform artifact, not a content difference).
- **Hand-verified the headline numbers**: independently recomputed the
  `age_at_event` breakdown from `entrants.csv`/`wrestlers.csv` directly.
  1,302 blank rows confirmed; of those, 967 already carry an explicit
  `age_status` of UNKNOWN/CONFLICTING/UNCERTAIN from earlier phases (a
  real, previously-flagged gap, not new), 318 have a wrestler DOB on file
  and are trivially derivable with no new sourcing, and only 17 wrestlers
  have no DOB at all. The report's "984 requiring research" is
  967 + 17 — both genuinely need work, just for different reasons (resolve
  a known conflict/UNKNOWN vs. find a DOB from scratch). Worth knowing when
  reading "984" as a single number.
- **Spot-checked the ethnicity_heritage (530) and entrance-timing
  (1,232 reusable / 210 new-research) figures** directly against
  `wrestlers.csv` and `sources.csv` — both correct, including that the
  1,232/210 split is genuinely gated on whether a Cageside-tagged source is
  already registered for that event (41 of 48 events currently have one).
- **Classification logic reviewed line-by-line**: correctly treats
  `N/A` companion-status fields as verified-not-research, `UNKNOWN`/
  `CONFLICTING`/`UNCERTAIN` as already-intentional (not silently
  reclassified), and keeps the ethnicity/heritage high bar (self-description
  only) intact. No blank is treated as evidence of absence anywhere in the
  script.

**Approved as submitted, no adjustments needed.** Green light to proceed:
fill the 318 free `age_at_event` derivations first (zero new research),
then work the P0/P1 queue in `remaining_queries.csv`, one event's source
bundle at a time as the audit itself recommends.

## 12. Age-derivation phase merged — shipped 2026-09-24 (Version 32)

The external AI's first fill-phase handoff (`royal_rumble_age_derivation_phase_20260924.zip`,
the 318 free `age_at_event` derivations from the audit) was independently
verified and published. Full diff against live confirmed the claimed scope
exactly — only `entrants.csv` (raw) plus the derived tables/dashboard that
depend on age; no `sources.csv`/`flags.csv` change, correctly, since no new
source was needed. Reproduced the whole thing from scratch: ran the
submission's own `derive_age_at_event_20260924.py` directly against live
data myself (it refuses to run unless the candidate cohort is exactly 318
rows, guarding against baseline drift), got byte-identical `entrants.csv`,
then rebuilt every derived table and `dashboard/data.json` with the
unmodified `build_derived.py`/`build_dashboard_data.py` — all outputs
byte-identical to the submission. Validator: 0 errors, confirmed
independently. SHA-256 matched. `page.html` untouched (no new UI needed).

**New records worth noting** — four record changes came out of this, all
independently checked against outside sources:
- Men's oldest entrant ever flips from Col. Mustafa (49y10m, RR1992M) to
  **Booker T (57y10m, RR2023M)** — exactly the kind of change flagged as
  likely in §10.2, now confirmed. Verified via [Sportskeeda](https://sportskeeda.com/wwe/news-booker-t-says-57-year-old-wwe-legend-royal-rumble-match)
  and [Wrestling Inc](https://www.wrestlinginc.com/1503643/booker-t-explains-wwe-royal-rumble-2023-appearance-made-feel-25/) coverage of his 2023 surprise return.
- Men's youngest entrant ever: **iShowSpeed (20y0m, RR2025M)**, a celebrity
  entrant — confirmed via [Wrestling Inc](https://www.wrestlinginc.com/1777872/ishowspeed-enters-wwe-royal-rumble-match-scores-elimination-getting-destroyed/).
- Women's oldest/youngest entrant ever set for the first time (no prior
  age data existed for Women's at all): **Ivory (60y2m, RR2022W)** and
  **Roxanne Perez (21y2m, RR2023W)** — Ivory's age-60 return independently
  confirmed via [Wrestling World](https://www.wrestling-world.com/news/news/wwe/35743/huge-updates-on-ivorys-return-plans-at-60/).

Green light sent to proceed with the P0/P1 queue in `remaining_queries.csv`
next (the 984 remaining age gaps, then residual close-out fields).

## 13. Known-DOB age phase merged, with one row held back — shipped 2026-09-24 (Version 33)

The external AI's next handoff (843 more `age_at_event` rows, derived from
wrestler DOBs that were already on file but whose entrant-level status had
been left at a stale `UNKNOWN` from an earlier phase) was independently
verified. Full diff confirmed the claimed scope exactly; reran the
submission's own `derive_remaining_known_dob_ages_20260924.py` directly
against live, got a byte-identical `entrants.csv`, and cross-checked its
843-row manifest against the submitted `KNOWN_DOB_AGE_CHANGED_ROWS.csv`
with zero mismatches.

**One row held back from this merge**: cross-referencing the 843 changed
wrestler_ids against `flags.csv` (not something the submission's own
exclusion logic checks — it only looks at the wrestler's `dob_status`
field, not at whether an open flag disputes that specific DOB) turned up
`F527`: an open, unresolved flag on Virgil's date of birth, explicitly
noting "a family obituary and a direct published interview with Virgil's
siblings" support 1951-04-07 against the database's inherited 1962-06-13 —
an 11-year discrepancy — and explicitly says "Shane should approve the
master-data migration" before it's used anywhere. `dob_status` for Virgil
is only `PROBABLE`, not `CONFLICTING`, so the derivation script's filter
didn't catch it. Rather than compute and label Virgil's age at RR1993M/
RR1994M as `DERIVED` (implying a solid calculation) from a value already
flagged as probably wrong and awaiting a decision, both rows were reverted
to blank/`UNKNOWN` before merging — matching their pre-phase state. Two
other flagged DOB conflicts turned up in the same cross-check (Rikishi:
10-day day-of-month difference, negligible, already resolved by keeping
Wikipedia's figure per F155; Prince Albert: 1972 vs. 1973 birth year,
already deliberately kept at the existing value per F201) — both are
minor and already-considered, so those rows were left in the merge as
submitted.

**Decision needed from Shane**: whether to approve migrating Virgil's
master DOB to 1951-04-07 (Wilkinsburg, PA) per F527's evidence. Note this
predates this session — Virgil already has an RR1992M `age_at_event` row
computed from the disputed 1962-06-13 value, added in an earlier phase,
still live. Whatever Shane decides, `flags.csv` F527 is the record of
the evidence either way.

Validator: 0 errors (independently confirmed, both before and after the
Virgil revert). Second rebuild byte-for-byte stable. New record: **Men's
oldest entrant ever flips again, to Jimmy Snuka (64y8m, RR2008M)** —
independently checked against outside coverage of his 2008 surprise
return. 9 Playwright smoke checks passed. SHA-256 of the published
`data.json` verified post-publish.

## 14. Standing handoff protocol — 2026-09-24

Shane asked for a more efficient round-trip: fewer back-and-forth handoffs
between him, the external AI, and this session. Documenting a standing
protocol here so future rounds can reference it instead of needing fresh
custom instructions each time.

**Batch by priority tier, not by data-slice.** The age_at_event P0 work
took three round-trips (audit → 318 zero-research rows → 843
previously-mislabeled rows) that could reasonably have been one or two:
the 318 and 843 splits were both "derivable without new research," just
discovered in two passes. Going forward, the external AI should exhaust
everything achievable without new research for a priority tier in a single
pass before packaging a handoff, rather than sending a partial slice as
soon as one sub-case is found.

**A handoff is worth sending when**: a full priority tier (or a natural
sub-tier, like "everything derivable without new research" vs. "everything
requiring it") is complete, or the external AI hits something needing a
judgment call it can't resolve itself (a Shane-level decision like F527,
a genuinely ambiguous sourcing conflict, a scope question). Not every
individual field or discovery needs its own round-trip.

**What doesn't need a round-trip**: routine continuation once a phase is
approved. The external AI can keep working through the rest of a tier
using the same standing rules (sourcing/status conventions in
`DEFINITIONS.md`, the CONFIRMED/PROBABLE bar, never-invent-data,
N/A-for-verified-absence) without re-asking permission for each field.

**What still always needs independent verification before the next AI
instruction**: any handoff that changes `data/` — this doesn't change
under the new protocol. The savings are in fewer, larger, better-scoped
handoffs, not skipped verification.

## 15. Appearance-history phase merged, plus a report-accuracy problem worth naming clearly — shipped 2026-09-24 (Version 34)

The technical work in this handoff is excellent and fully verified: three
scripts (`derive_rumble_appearance_history_20260924.py`,
`research_missing_dob_ages_20260924.py`,
`close_residual_physical_profiles_20260924.py`), all baseline-guarded and
idempotent, all reproduced byte-for-byte against live when run in sequence
myself — `entrants.csv`, `wrestlers.csv`, `sources.csv`, `flags.csv`, every
derived table and `dashboard/data.json` all matched the submission exactly.
0 validator errors, confirmed independently. The DOB-research script
explicitly checks `flags.csv` for open disputes before touching a wrestler
(and hardcodes `virgil`/`haku` into its blocked list — direct evidence it
picked up the correction from §13). New sources are specific, named,
real Wikipedia/WWE.com URLs, spot-checked for two (AJ Styles, Roman
Reigns) against outside sources. The residual physical-profile gaps that
couldn't be closed (Paul Roma, Timothy Well, Kevin Thorn, Zelina Vega,
Roxanne Perez, Kelani Jordan) were left open in a new flag (F559) rather
than guessed. No new age/physical record this round (0 new
`records_history` rows) — just the honesty-note coverage percentages
climbing as expected.

**The problem**: `PHASE_KNOWN_DOB_AGE_REPORT.md`'s successor,
`APPEARANCE_HISTORY_REPORT_20260924.md`, states explicitly: *"No changes
were made to `sources.csv`, `flags.csv`, `wrestlers.csv`, `events.csv`, or
any unrelated raw-data table in this phase."* This is false — the same zip
also contained 38 new wrestler DOBs, 121 new `age_at_event` derivations, 14
new sources, a new flag, and 23 physical-profile cells, none of which the
report mentions or the stated file list covers. This is a different, more
serious kind of problem than §9/§13's under-reporting: those were omissions
in a report describing only its own phase's stated intent; this is an
explicit, specific, checkable claim that turned out to be wrong. It also
directly contradicts what the external AI told Shane in the same
conversation — that the appearance-history package "needs independent
verification before I make further database changes" — when the zip
already contained those further changes.

The work itself was good and got merged. But going forward, a report's file
list needs to be generated mechanically from an actual diff against the
last verified baseline (e.g. `git diff --stat` or equivalent), not written
from memory of what the AI intended to change — intent and actual diff can
drift, as demonstrated here twice now in two different ways. Flagged to the
external AI directly, with a request to change how reports are produced,
not just what they cover.

9 Playwright smoke checks passed. SHA-256 of the published `data.json`
verified post-publish.

**Correction, 2026-09-24**: the "false claim" framing above was wrong, and
for the same underlying reason as §9. Shane subsequently forwarded the two
reports I'd never seen: `royal_rumble_p0_age_research_closeout_20260924.zip`
(the P0 age-research phase — 38 new DOBs, 121 new `age_at_event` rows, 14
new sources, matching this section's numbers exactly) and
`royal_rumble_database_physical_profile_closeout_20260924.zip` (the
physical-profile phase — 23 cells across 13 rows, flag F559, also matching
exactly). Both were separately, individually reported by the external AI at
the time, and both reports are accurate about their own phase. The
appearance-history report's statement that no changes were made to
`sources.csv`/`flags.csv`/`wrestlers.csv`/`events.csv` **in that phase** was
true — those changes belonged to the other two phases, which happen to sit
in the same zip only because each handoff is a cumulative full-state
snapshot. I only had the one (appearance-history) report in hand, so I read
its file-list claim as a claim about the whole zip's contents rather than
about its own phase, and called that a false statement when it wasn't one.
The actual gap was the same as §9's: Shane forwarding only the last of
several sequential zips, rather than each report individually. No process
defect on the external AI's side is demonstrated here after all — the
mechanical-diff suggestion above is still good practice and worth keeping,
but not because a report was caught being wrong.

## 16. Ring Crowdedness — shipped 2026-09-24 (Version 35)

Built directly, not by the external AI — this is exactly the case
identified in §10.3 as a small, low-risk derived-layer change requiring no
new sourcing, done while waiting on the external AI's next handoff.

**What it is**: Cageside Seats' "Ring Crowdedness" stat (e.g. "7 wrestlers:
15m 14s, 25.9%") — the full breakdown of how much of a match's time was
spent with each possible number of wrestlers simultaneously in the ring,
not just the peak. New derived table `data/derived/ring_crowdedness.csv`
(schema added to `scripts/schema.py`), computed as a direct extension of
the existing peak-occupancy reconstruction in `scripts/build_derived.py`
(the same reconstructed per-second timeline, same gating logic, same
half-open interval convention as `ring_occupancy_stats.csv` — literally the
same loop, just also accumulating time-at-each-count instead of only
tracking the max). Wired into `build_dashboard_data.py` (new `crowdedness`
array per event) and rendered on the event page as a new "Ring
crowdedness" panel directly under "Peak ring occupancy," reusing the
existing `barRow()` component already used elsewhere on the dashboard.

**No new sourcing, no raw data touched**: only `scripts/schema.py`,
`scripts/build_derived.py`, `scripts/build_dashboard_data.py`, and
`dashboard/page.html` changed. `entrants.csv`, `wrestlers.csv`,
`sources.csv`, `flags.csv`, `events.csv` are all untouched — this is purely
a derived-layer/presentation change over data that was already verified.

**Verification**:
- Built and tested first in an isolated `/tmp` copy, then the identical
  code changes applied to the live tree and rebuilt there — `data/derived/
  ring_crowdedness.csv` and `dashboard/data.json` were byte-identical
  between the isolated run and the live rebuild.
- Internal consistency checks across all 12 qualifying events (the same 12
  that already have `ring_occupancy_stats.csv` rows — this can never cover
  more events than that, by construction): each event's max crowdedness
  count matches its existing peak count exactly; each event's
  `seconds_at_count` values sum exactly to its own `total_match_seconds`;
  percentages sum to ~100% (rounding only) for every event.
- `validate_integrity.py`: 0 errors, unchanged.
- 12 Playwright smoke checks: new panel renders correctly (singular "1
  wrestler" vs. plural "13 wrestlers", correct bar ordering, correct
  percentages/times), events without qualifying data (e.g. RR2026M) render
  fine with no broken/empty panel, and every pre-existing page (Goldberg's
  profile, Men's Records, Explore, Trish Stratus's profile) still works.
  Screenshot-checked the rendered panel visually.
- Staged, published as **Version 35**, SHA-256 verified post-publish for
  both `page.html` and `data.json`.

**Not yet done** (still queued, per §10.3): Entrance Times / Follow the
Buzzers (needs `entrances.csv` populated — either Shane's video-timed
entries or citing Cageside's own published per-event timing articles where
they exist, PROBABLE/single-source where only Cageside covers a year) and
verified per-event trivia facts (WhatCulture as a lead only, each fact
independently verified against a primary source before entering
`notable_moments.csv`). Both still require actual research/sourcing, so
they stay with the external AI's queue rather than being built directly.

## 17. Championship profile closeout — verified and merged 2026-09-24 (no new Version — dashboard unaffected)

Full independent verification, same rigor as every prior phase. Clean
result — nothing held back, nothing corrected.

**What it does**: completes all eight championship-profile fields
(`current_champion_title`, `championship_level`, `championship_partner`,
`reign_number`, `title_won_date`, `days_into_reign_at_event`,
`title_defended_same_card`, `title_lost_same_card`) across all 1,442
entrant rows — 133 rows keep their researched champion data (just a few
gaps filled: 29 blank reign numbers, 3 RR1989M timing values, blank
booleans), and the other 1,309 non-champion rows move from blank/UNKNOWN to
an explicit, verified `N/A`. 11 new sources (`S1700`–`S1710`), all real,
checkable WWE.com/Wrestling-Titles.com URLs.

**Baseline-timing note, not a defect**: this handoff was built against the
Version 34 snapshot, before Ring Crowdedness (§16) landed as Version 35.
Its copy of `schema.py`/`build_derived.py`/`build_dashboard_data.py`
therefore lacked my Ring Crowdedness code — diffed those three files
against current live and confirmed the *only* differences are exactly my
own Version 35 additions, nothing else. Handled correctly: applied their
`entrants.csv`/`sources.csv` changes on top of the current live tree (which
already has Ring Crowdedness) and rebuilt with the current scripts, rather
than trusting their stale derived/dashboard output directly.

**Verification**:
- Baseline guard hashes in their script (`EXPECTED_ENTRANTS_SHA256`,
  `EXPECTED_SOURCES_SHA256`) matched live `entrants.csv`/`sources.csv`
  exactly.
- Reproduced independently: ran their own `close_championship_profiles_
  20260924.py` against a fresh isolated copy of live — output `entrants.csv`,
  `sources.csv`, and the row-manifest were byte-identical to what they
  submitted. Second run: correctly idempotent (baseline-guard short-circuit).
- Cross-checked the entire submission's `entrants.csv` diff field-by-field
  against `CHAMPIONSHIP_PROFILE_CHANGED_ROWS.csv`: zero field-list
  mismatches, zero value mismatches, across all 1,442 changed rows. Also
  confirmed zero non-championship-field cells changed anywhere (their "no
  other field touched" claim checked directly, not assumed).
- Rebuilt derived layer + dashboard with the *current* (Version
  35-inclusive) scripts: all derived tables and `dashboard/data.json` came
  out byte-identical to live Version 35 — championship fields aren't
  currently read anywhere in `build_dashboard_data.py`, so this phase has
  zero dashboard-visible effect (see note below).
- `flags.csv` cross-check (my own standing practice, not the submission's):
  found one relevant *open* flag, F479 (Solo Sikoa / RR2026M, a genuine
  unresolved dispute over how to count a title transfer) — pre-existing,
  unchanged by this phase, and its own stated interpretation ("leave Solo's
  title blank, count Jey as champion") is exactly what the submitted data
  does. Also confirmed two *resolved* title-related flags (F296 Roman
  Reigns/RR2016M, F404 Kairi Sane's WWE Women's Tag Team Championship)
  were left untouched — their existing champion data carried through with
  only the blank `championship_partner` filled to `N/A`.
- `validate_integrity.py`: 0 errors.
- Outside-source spot checks (5 claims, all confirmed): WrestleMania IV
  date and Randy Savage's/Demolition's title wins (1988-03-27); The Usos'
  Raw Tag Team Championship win (2025-12-29); Becky Lynch's Women's
  Intercontinental Championship win (2026-01-05); Jacy Jayne's NXT Women's
  Championship regain at NXT Gold Rush (2025-11-18).
- SHA-256 of the uploaded zip verified against Shane's stated hash before
  opening it.

**No republish needed**: `dashboard/page.html` and `dashboard/data.json`
are byte-identical to the currently-published Version 35 (hashes checked
directly) — this phase only touches `entrants.csv`/`sources.csv`, and
nothing on the dashboard currently reads the championship fields. The
*database* is more complete after this merge; the *published site* is
unchanged pixel-for-pixel. Worth a scope decision from Shane at some point:
should champion status show on wrestler/event pages now that the data
exists for it? Not urgent — noting it here rather than deciding it myself.

## 18. Company debut & return closeout — verified and merged 2026-09-24 (no new Version — dashboard unaffected)

Another clean handoff. This time the external AI's own report explicitly
flagged the Ring Crowdedness baseline lag itself and said the verifier
should rebuild with current live scripts — exactly right, and exactly what
I did (same handling as §17).

**What it does**: completes four entrant fields (`is_company_debut`,
`company_debut_date`, `is_returning_wrestler`, `absence_length`) across all
1,442 entrant rows. 3 genuine WWF/WWE company debuts (Vader RR1996M, AJ
Styles RR2016M, Royce Keys/Powerhouse Hobbs RR2026M), 68 documented
returns, 46 of those honestly left `absence_length=UNKNOWN` where a source
confirms the return but not a duration, everything else explicit
`FALSE`/`N/A`. Also corrected legacy false positives (RR1989M/RR1990M rows
that had been marked as returns purely from Rumble-to-Rumble chronology,
plus a few wrongly-flagged active-roster cases). 21 new sources
(`S1711`–`S1731`), all real WWE.com/Wikipedia URLs.

**Verification** (same protocol as §17):
- Baseline guard hashes matched live exactly (anchored to the
  championship-closeout-merged state from §17, correctly picking up where
  that phase left off).
- The 3 shared scripts (`schema.py`/`build_derived.py`/
  `build_dashboard_data.py`) differed from the submission only by exactly
  my Version 35 Ring Crowdedness code — confirmed, not assumed.
- Reproduced independently: ran their `research_debuts_returns_20260924.py`
  against a fresh isolated copy of live — `entrants.csv`, `sources.csv`,
  and the manifest all came out byte-identical to their submission.
- Cross-checked all 1,442 manifest rows' before/after values against the
  actual entrants.csv diff directly (their manifest uses before_/after_
  column pairs rather than a changed-fields list — checked accordingly):
  zero mismatches. Zero non-target-field cells changed anywhere.
- 21 new sources: all present, none removed, none modified, matching
  exactly.
- `flags.csv` cross-check: one flag touches a wrestler in this phase's
  scope (F455, LA Knight, `debut_year_company`, open) — confirmed it's
  about his pre-WWE indie-circuit debut year (`wrestlers` table), unrelated
  to the entrant-level fields this phase touches. No real conflict.
- `validate_integrity.py`: 0 errors.
- Outside-source spot checks: AJ Styles' 2016 Royal Rumble debut
  (confirmed); the 2026 Royal Rumble returns of LA Knight, Brie Bella and
  Tiffany Stratton (confirmed). Vader's claimed 1996 Royal Rumble debut
  initially looked questionable (a first search suggested pre-Rumble WWF
  vignettes might count as an earlier appearance) — dug further and
  confirmed those were same-run hype packaging, not a standalone earlier
  appearance; Wikipedia states the Rumble match itself was his first WWF
  appearance. Also specifically ran down "Royce Keys" vs. "Powerhouse
  Hobbs" (the wrestler_id doesn't match the ring name recorded at the
  event, which stood out): confirmed Royce Keys **is** Powerhouse Hobbs,
  an AEW departure who signed with WWE under a new ring name and debuted
  as the RR2026M mystery entrant — the wrestler_id choice and the
  company-debut classification are both correct.
- Rebuilt derived layer + dashboard with current (Version 35-inclusive)
  scripts: all derived tables and `dashboard/data.json` byte-identical to
  live. Same as §17, nothing in `build_dashboard_data.py` currently reads
  these fields, so no dashboard change and no republish needed — confirmed
  by direct hash comparison against the published Version 35.
- SHA-256 of the uploaded zip verified against Shane's stated hash before
  opening it.

No issues found, nothing held back, nothing corrected.

## 19. Ethnicity/heritage + Cageside entrance timing — verified and merged 2026-09-25 (Version 36)

Two phases arrived in one turn: Shane pasted the ethnicity/heritage chat
update as text only (no zip attached), then separately uploaded the
entrance-timing zip. Same cumulative-snapshot pattern as before — the
entrance-timing zip's `wrestlers.csv` and `scripts/research_ethnicity_
heritage_20260924.py` already contained the full, already-reported
ethnicity phase, so both were verified from the one zip without needing to
ask Shane to re-send anything.

**Ethnicity/heritage**: `wrestlers.csv` gets a new `ethnicity_heritage`/
`ethnicity_heritage_status` pair, populated *only* from direct first-person
self-identification (interviews, WWE.com first-person pieces) — never
inferred from nationality, name, appearance, or family. 21 of 530
wrestlers qualify (6 CONFIRMED on two agreeing direct sources, 15 PROBABLE
on one), the other 509 explicitly `UNKNOWN`. 21 new sources (S1732–S1752).

**Entrance timing**: `entrances.csv` (previously empty by design, pending
a video tool) is now populated from Cageside Seats' own published
frame-by-frame timing articles — one per event/division, all 48. 1,343
entrant rows get a buzzer timestamp; 1,122 of those also get an exact
buzzer-to-ring duration. 221 honestly stay duration-blank where the
article didn't enumerate one — no estimate inserted. 22 new sources
(S1753–S1774), plus 19 existing Cageside source rows that had been logged
with blank URLs (several explicitly noted "NOT live-fetched this pass" in
their own descriptions) now got their live URL recovered and re-accessed.
`DEFINITIONS.md` updated to match — no longer describes `entrances.csv` as
intentionally empty.

**Verification**:
- Baseline guard hashes (ethnicity script) matched live exactly.
- Reproduced the ethnicity phase independently: ran their script against a
  fresh copy of live, `wrestlers.csv` output byte-identical to submission.
- Reproduced the entrance-timing phase's `entrances.csv` independently:
  ran `apply_cageside_entrance_timing.py` against a fresh copy of live,
  output byte-identical.
- **Genuine gap found, worth naming plainly**: unlike every prior phase,
  the 22 new sources + 19 recovered-URL edits to `sources.csv` for
  entrance timing have no reproducible script behind them anywhere in the
  zip — I checked every script for a `sources.csv` write and found none
  tied to this phase. This is the first phase this project where I
  couldn't mechanically reproduce a raw-data change; I verified it by
  direct content inspection instead: diffed `sources.csv` line-by-line,
  confirmed the *exact* 22 additions and *exact* 19 modifications the
  report claims (nothing more, nothing fewer), confirmed the 19 modified
  rows changed only `url`/`accessed_date`/`notes` (never `source_name`/
  `reliability_tier`/anything else), and confirmed all 22 new URLs plus 2
  of the 19 recovered URLs are real, live, on-topic Cageside Seats
  articles via independent web search. Content checks out completely, but
  I've asked the external AI to make this step scriptable/reproducible
  going forward, the same as every other phase.
- `flags.csv`: unchanged (confirmed directly), consistent with the claim
  that no flags needed touching. The pre-existing combined `entrances;
  moves` "no video tool" flags correctly stay open — they cover moves.csv
  and near_eliminations.csv too, which are still genuinely unaddressed;
  their continued existence doesn't misrepresent the (now-populated)
  buzzer timing.
- `validate_integrity.py`: 0 errors.
- Outside-source spot checks: 3 of the new/recovered Cageside URLs
  (1990, 2021 Women's, 2026 Men's) independently confirmed as real,
  on-topic, plausibly-dated articles.
- Rebuilt derived layer + dashboard with current scripts: neither
  `entrances.csv` nor `ethnicity_heritage` is read anywhere in
  `build_derived.py`/`build_dashboard_data.py` (confirmed directly, not
  assumed) — so this phase's content has zero dashboard effect. The
  dashboard *did* rebuild with 4 cell differences from the last published
  version, but all four are the "Rumble with most now-deceased entrants"
  record's self-documented daily-recompute date stamp ("as of 2026-09-24"
  → "as of 2026-09-25") rolling over with the calendar day — unrelated to
  this phase, expected/documented behavior, not a bug.
- Republished as **Version 36** since `data.json` genuinely changed (that
  date stamp). 5 Playwright smoke checks passed. SHA-256 verified
  post-publish.
- SHA-256 of the uploaded zip verified against Shane's stated hash before
  opening it.

No data-quality issues found. One process note sent to the external AI
about the unscripted `sources.csv` edit, same spirit as the mechanical-diff
ask from §15/§18 — nothing held back or reverted.

## 20. Entrance-derived stats + full profile surfacing + championship/return records — verified and merged 2026-09-25 (Version 37)

The external AI sent the current Version 36 full package (per its own
request, after correctly flagging that the entrance-timing zip's shared
scripts were pre-Version-35 and would have dropped Ring Crowdedness — see
the previous handoff), then delivered three further phases in quick
succession, bundled cumulatively into one zip
(`royal_rumble_database_CHAMPIONSHIP_RETURN_RECORDS_HANDOFF_20260925...zip`):
entrance-derived statistics, full profile surfacing (championship/debut/
return/ethnicity fields finally wired into the dashboard), and ten new
championship/return records (R064–R073). All three verified and merged
together since the zip's own diff showed them as one consistent, cumulative
change set.

**What changed, mechanically:**
- New `data/derived/entrance_event_stats.csv` (48 rows) — event-level
  entrance-timing summaries (median/average/shortest/longest duration,
  latest physical ring entry, advertised-vs-actual interval variance),
  computed from the `entrances.csv` data merged in the previous phase.
- 10 new records (R064–R073): most reigning champions in a field, longest
  title reign entering a Rumble, most appearances as reigning champion,
  most returning wrestlers in an event, most appearances classified as a
  return — each split Men's/Women's.
- `scripts/schema.py`, `build_derived.py`, `build_dashboard_data.py`:
  extended (purely additive — championship, debut/return, physical/
  character profile, ethnicity, and entrance-timing fields that were
  already sitting in `entrants.csv`/`wrestlers.csv`/`entrances.csv` since
  earlier phases, but were invisible on the dashboard until now, are all
  wired in).
- `dashboard/page.html`: new "Entrance timing" event panel, "Champions in
  field"/"Returning wrestlers" event facts, per-entrant championship/
  physical/character badges on the elimination table, a "Championship
  status at entry" and "Debuts and returns" panel on wrestler profiles, a
  full "Rumble-by-Rumble profile history" table (age/height/weight/billed
  from/alignment/gimmick/manager/team per appearance), and ethnicity in
  Explore search.
- No raw entrant/wrestler/source/flag CSV touched at all — confirmed by
  diff. This phase is pure derivation and dashboard surfacing of data that
  was already fully merged in earlier phases.

**Verification steps:**
- SHA-256 of the uploaded zip verified against the stated hash before
  opening.
- Diffed every file in the submission against live — confirmed the actual
  scope exactly matches the list above, nothing else touched.
- Reproduced independently: copied the submission's own `schema.py`/
  `build_derived.py`/`build_dashboard_data.py` onto a fresh, untouched copy
  of live raw data, ran the pipeline myself — `records.csv`,
  `records_history.csv`, `.records_baseline.csv`, `entrance_event_stats.csv`,
  and `dashboard/data.json` all came out byte-identical to the submission.
- Independently re-derived a sample of the new records directly from
  `entrants.csv` with my own separate script (not reusing their
  `build_derived.py` logic) — R064 (RR2006M, 6 champions), R069 (RR2025W/
  RR2026W tied at 6), R072 (RR2018W, 11 returns), R073 (Molly Holly, 3
  return appearances) all confirmed exactly.
- Read every line of the `build_derived.py`/`build_dashboard_data.py` diffs
  (230 and 117 added lines respectively) — deterministic, no invented
  values, ties preserved rather than hidden behind a single `max()`.
- `flags.csv`: confirmed unchanged directly.
- `validate_integrity.py`: 0 errors.
- Playwright smoke test (6 checks: home load, RR2006M champions-in-field/
  returning-wrestlers facts, RR1988M entrance-timing panel, wrestler
  profile load, profile-history table, Explore ethnicity search) — all
  passed.
- Republished as **Version 37**. Read the full live artifact (both
  `page.html` and `data.json`) before publishing, per standing protocol.
  SHA-256 verified post-publish on both files.

No data-quality issues found, nothing held back. This closes out the
"surface completed profile fields" work item that's been sitting since
§17/§18/§19 — championship, debut/return, and ethnicity/heritage data
researched over the past two days is now all actually visible on the
published dashboard, not just sitting in CSVs.

## 21. Ring Physical Peaks + Field Physical Records — verified and merged 2026-09-25 (Version 38)

Two more phases, bundled cumulatively into one zip
(`royal_rumble_database_FIELD_PHYSICAL_RECORDS_HANDOFF_20260925_205610.zip`):
Ring Physical Peaks (R074–R075, the highest combined billed weight/height
simultaneously in the ring, gated on the same complete-occupancy-timeline
reconstruction as Ring Crowdedness) and Field Physical Records (R076–R083,
eight complete-field combined/average billed height and weight records,
Men's and Women's, gated on 100% appearance-specific coverage of the
actual field). Reports for both were attached
(`RING_PHYSICAL_PEAKS_REPORT_20260925.md`, `FIELD_PHYSICAL_RECORDS_REPORT_20260925.md`).

This was forwarded alongside Shane asking the external AI "How many more
separate runs do we need?! I don't even know what we're doing now" — its
reply (relayed by Shane) was that the original personal-profile research
objective is complete, recent batches have been optional dashboard
extras, and it recommended one final verification/merge (this one) and
then a pause for a consolidated remaining-work audit rather than more
incremental batches. Treating this explicitly as that pause point — see
the note at the end of this section.

**What changed, mechanically:**
- `scripts/schema.py`: registered `ring_physical_peaks.csv` and
  `event_field_physical_stats.csv` — purely additive.
- `scripts/build_derived.py`: +159 lines — event field-physical
  aggregation (combined/average height & weight, gated on 100% actual-field
  coverage), ring physical-peak calculation (reusing the exact
  interval-reconstruction logic from `ring_occupancy_stats.csv`, gated on a
  complete timeline AND 100% profile coverage), and R074–R083.
- `scripts/build_dashboard_data.py`: +30 lines — exposes `fieldPhysical`
  and `physicalPeaks` on event summaries.
- `data/derived/ring_physical_peaks.csv`, `event_field_physical_stats.csv`:
  new.
- `data/derived/records.csv`, `records_history.csv`, `.records_baseline.csv`:
  updated (baseline 73 → 75 → 83; history 190 → 200 rows).
- `dashboard/page.html`: +29 lines — "Maximum combined size in the ring"
  event panel, and combined/average field weight & height facts.
- `dashboard/data.json`: rebuilt.
- No raw `data/` file touched; `flags.csv` unchanged.

**Record-count arithmetic (checked, resolves cleanly):** the Ring Physical
Peaks report says its own baseline was "refreshed to the 75-record
baseline" — that's the count *after* adding R074–R075 (73 + 2 = 75), not
before. The Field Physical Records report then refreshes to 83 (75 + 8 =
83). No inconsistency once read correctly; flagged here only because it
looked like one at first pass.

**Verification steps:**
- SHA-256 of the uploaded zip verified against the stated hash
  (`fa8f2b7b24515392bd364106e06cb6356b5fe9597ff4863f3e3daf2155513e77`)
  before opening.
- Diffed every file in the submission against live — confirmed the actual
  scope exactly matches the list above, nothing else touched. Every raw
  `data/*.csv` file and every other untouched derived table confirmed
  byte-identical.
- Reproduced independently: copied the submission's own `schema.py`/
  `build_derived.py`/`build_dashboard_data.py` onto a fresh, untouched copy
  of live raw data, ran the pipeline myself — `records.csv`,
  `records_history.csv`, `.records_baseline.csv`, `ring_physical_peaks.csv`,
  `event_field_physical_stats.csv`, and `dashboard/data.json` all came out
  byte-identical to the submission.
- Independently re-derived every one of the 8 Field Physical Records
  (R076–R083) directly from `entrants.csv`/`events.csv` with my own
  separate script (not reusing their `build_derived.py` logic) — all 8
  values and the Men's (39/39) and Women's (2/9) coverage counts matched
  exactly.
- Independently reconstructed RR2009M's occupancy timeline from raw data
  with my own separate script (not reusing their interval logic) to
  cross-check R074/R075 — reproduced 1,792.0 kg and 28.89 m at the
  46:18–47:02 window with the same 15 wrestlers, exactly.
- Read every line of both script diffs by hand — deterministic, no
  invented values, no-show exclusion and winner-retention handled the same
  way as the rest of the codebase.
- `flags.csv`: confirmed unchanged directly.
- `validate_integrity.py`: 0 errors, run against the independent rebuild.
- Playwright smoke test (16 checks across RR2011M, RR2009M, RR2021W, and
  both divisions' Records pages) — all passed except two false failures in
  my own test regex (see cosmetic note below); re-checked directly and the
  underlying values are correct.
- Republished as **Version 38**. Read the full live artifact (both
  `page.html` and `data.json`) before publishing, per standing protocol —
  confirmed no drift since Version 37. SHA-256 verified post-publish on
  `data.json`.

**Minor cosmetic finding (not blocking, not fixed here):** the event-page
combined/average weight and height facts use JS `.toFixed()`, which
doesn't add thousand separators (e.g. "4590.0 kg"), while the Records page
uses Python's `{:,.1f}` formatter, which does ("4,590.0 kg" for the same
RR2011M value). Purely a display inconsistency between two panels showing
the same underlying number — worth a one-line fix next time either file is
touched, not worth a standalone phase.

No data-quality issues found, nothing held back.

**On the "how many more runs" question:** per the external AI's own
recommendation and Shane's evident fatigue with incremental batches, this
merge is being treated as the natural pause point. Next step is a plain
conversation with Shane about whether he wants a consolidated
remaining-work audit built (by me, by the external AI, or jointly) before
any further phases are queued — not launching straight into more work.

## 22. Decision-batch data corrections + no-research stats — merged 2026-09-26 (Version 39)

Following `ROYAL_RUMBLE_REMAINING_WORK_AUDIT_20260926.md`, Shane made a set
of explicit decisions and asked for everything not requiring new research
to be built directly, without a handoff round. All of it was done and
verified in an isolated copy (`/tmp/phase1_test`) before being merged to
live, re-derived against live, re-validated, and smoke-tested exactly as
Version 38 was — see that phase's write-up above for the full protocol;
not repeated verbatim here.

**Data corrections (Shane's explicit decisions):**
- **F527 — Virgil's DOB/birthplace migrated.** `1962-06-13`/Nashville →
  `1951-04-07`/Wilkinsburg, Pennsylvania, both upgraded to CONFIRMED. Cascaded
  into recomputing `age_at_event` on all 3 of Virgil's entrant rows
  (RR1992M/93M/94M) using the same `exact_age()` algorithm the rest of the
  database uses, filling in two ages that had been UNKNOWN.
- **F105 — Kama/Papa Shango.** Investigated the dashboard's same-performer
  linking mechanism first (`build_dashboard_data.py`'s union-find over
  `real_name`/`dob`): these two were already sharing an identical
  `real_name` ("Charles Thomas Wright") and `dob`, so they were already
  auto-linked live as of Version 38 — no data change needed, flag resolved
  as already-correct.
- **F106 — Bob Holly/Sparky Plugg.** Genuinely blocked from auto-linking:
  `sparky-plugg`'s `real_name` carried a parenthetical ("Robert William
  Howard (also 'Bob Holly')") that broke the exact-match linking logic.
  Stripped to "Robert William Howard" — the two now correctly show as the
  same performer on the dashboard.
- **RR1996M duplicate elimination rows merged.** The two near-duplicate
  pairs flagged in the audit (Diesel eliminating Kama; Shawn Michaels
  eliminating Diesel — each previously two rows, one from S035 with
  order/clock, one from S032 with narrative method) merged into one row
  each: order/clock kept from the S035 row, method text from the S032 row,
  `source_ids` combined, both upgraded to CONFIRMED (genuine two-source
  agreement). `eliminations.csv` 1579→1577 rows. Independently confirmed
  this fixed a real inflated rivalry count (`diesel→kama` was showing 2,
  correctly 1; `shawn-michaels→diesel` was showing 3, correctly 2 — the
  second pairing turned out to be affected too, since one of the duplicate
  pairs was a Shawn Michaels/Diesel elimination) with no effect on any
  other pairing.
- **F071/F096/F099 (Doink vs. Doink-1995) left open** — Shane said he
  didn't understand what these referred to, not that he'd decided
  something; nothing merged, explained to him separately instead of
  guessing at a resolution.
- Non-official Royal Rumbles: confirmed staying paused, no action.
- Masked-wrestler tagging: confirmed as wanted, but this is new tagging
  work, not a data correction — queued for the external AI's next batch
  (Section 23 below), not done here.

**New stats/fixes requiring zero new research, all computed purely from
data already in the database:**
- **Comma-separator formatting bug fixed.** The event-page combined/average
  weight and height facts (and the Ring Physical Peaks panel) were using
  raw JS `.toFixed()`, which doesn't add thousand separators, while the
  Records page used Python's `{:,.1f}`. Added a shared `fmtDec()` helper to
  `dashboard/page.html` and switched every affected call site to it — both
  panels now show "4,590.0 kg" consistently.
- **`wrestled_earlier_on_card` surfaced as an entrant badge**, mirroring
  how `celebrity_entrant` already showed as a "Celebrity" badge (that field
  turned out to already be surfaced — the audit's claim it wasn't was
  slightly off; only `wrestled_earlier_on_card` was genuinely missing).
- **"Most Hall of Famers already inducted at the time" record** — turned
  out to already exist live (R014/R039, added in an earlier phase), so
  nothing to build here either; the audit was wrong on this point too.
- **`entry_number_bands.csv`** (new derived table + schema entry) — the
  same `entry_number_stats.csv` data re-bucketed into #1, #2, First 5 (1-5),
  Last 5, and Middle, per Shane's "win rate by #1 vs #2, first-5 vs middle
  vs last-5" request. "Last 5" is computed relative to each division's own
  observed max entry number (40 for Men's, since RR2011M was a 40-man
  field; 30 for Women's), not hardcoded. Surfaced as a new "By value slice"
  panel on the Entry Number Statistics page, above the existing per-number
  breakdown.
- **"Longest iron-man streak" record** (new, per division) — most
  consecutive editions of a division in which one wrestler had the single
  longest ring time in the match. Chris Benoit (Men's, RR2004M-RR2005M, 2)
  and Bianca Belair (Women's, RR2020W-RR2022W, 3). "Consecutive" is defined
  against this database's own edition sequence, not calendar years —
  events with zero ring-time coverage are excluded from the sequence
  entirely (documented per-division in the record's own notes) rather than
  silently breaking or extending a streak.
- **"Best bounce-back" record** (new, per division) — earliest elimination
  one edition immediately followed by an outright win the very next
  edition (restricted to true back-to-back editions present in the
  database, and to a win rather than a looser "deep run" threshold, so the
  record has one unambiguous answer). Hulk Hogan (Men's — eliminated #21 of
  30 at RR1989M, won RR1990M) and Bayley (Women's — eliminated #13 of 30 at
  RR2023W, won RR2024W).
- Both new record types added strictly after every previously-assigned
  `record_id`, per the established convention — R001-R083 unchanged,
  R084-R087 are the four new records (2 per division).

**Deliberately not done in this batch:** the bigger dashboard/UI builds
flagged in the audit as optional polish — an interactive birthplace world
map, expandable record cards (top-10 instead of just the current holder),
and a dedicated champion-history browser page. None of these are broken or
blocking anything; they were set aside so this pass could move on to
packaging the external AI's next batch and starting the Rumble Logger tool
build, per Shane's explicit ordering. Worth picking up in a future pass if
Shane wants them.

**Verification, same protocol as every phase before this:** every edit
made and tested first in an isolated copy (`/tmp/phase1_test`); keyed diff
(by primary-key tuple, not `sort`-based, which produces misleading noise
from row reordering) confirmed only the intended rows changed in
`wrestlers.csv`, `entrants.csv`, `flags.csv`, and `eliminations.csv`, with
zero unexpected additions or removals; `build_derived.py` and
`build_dashboard_data.py` re-run against the isolated copy and separately
against live after merging, with `dashboard/data.json` coming back
byte-identical (SHA-256 match) between the two runs; re-running
`build_derived.py` a second time against the now-updated live data
produced 0 new `records_history.csv` entries, confirming idempotency;
`validate_integrity.py` — 0 errors, both before and after; Playwright
smoke test against both the isolated copy and the live tree (Entry Number
Statistics bands panel, RR2011M/RR2009M comma-formatted weight facts,
RR1996M page post-merge, Virgil's and Sparky Plugg's wrestler pages,
Records pages for both new record types) — all passed, no console errors.
Live artifact re-read (SHA-256 `a0d39461...`, matching the recorded
Version 38 hash) immediately before publishing, confirming no drift; SHA-256
verified post-publish on `data.json`.

Published as **Version 39**. Nothing held back.

## 23. Rumble Event Logger V1 — delivered 2026-09-26 (separate tool, no dashboard change)

Following the approved Docs plan ("Royal Rumble Event Logger —
Architecture & Development Plan," Section H revision), built and
delivered a working V1 of the standalone Logger: `royal_rumble_logger.zip`,
alongside this database rather than inside it. Full detail is in that
package's own `README.md`; summarized here for the database's own
history since the Logger reads from and writes back to this data.

Stdlib-only Python (`http.server` + `sqlite3`, no dependencies) serving a
single-file vanilla-JS frontend. `import_adapter.py` builds a local
SQLite working store from this database's own CSVs, using the three-state
`imported_*`/`reviewed_*` field model from the approved plan; `server.py`
runs the Home → Review (pre-populated, Save & Next, keyboard shortcuts
1-4 for Confirm/Correct/Uncertain/Conflict) → Overview flow;
`export_sync.py` turns reviewed rows into a **proposed**
`eliminations.csv` plus a change summary — it never touches this live
database directly, so any Logger output still goes through the same
isolated-copy-test-then-merge protocol as every other change here.

One real bug caught and fixed before delivery, worth recording: the
first cut of the Logger's natural key was `(event_id,
eliminated_wrestler_id)` alone, which silently collapsed every "group
elimination" (a victim eliminated by several wrestlers recorded as
separate rows, same `order_in_match` -- e.g. RR2023W's Nia Jax, 11 rows)
down to a single reviewable row, keeping only the last eliminator
processed. Caught during this tool's own Playwright smoke testing
(1577 live rows only produced 1384 imported rows -- the exact gap
matched the known count of multi-eliminator rows from ROADMAP §21's
"125 legitimate group eliminations" note). Fixed by keying on the full
`(event_id, eliminated_wrestler_id, imported_eliminator_wrestler_id)`
triple instead, anchored to the *imported* eliminator specifically so
correcting who the eliminator was during review is an edit to a row,
never a change to its identity. Re-verified after the fix: 1577 rows in,
1577 rows out, RR2023W's Dana Brooke (3 real eliminators) round-trips as
3 distinct reviewable rows.

Not in V1, deliberately: no embedded video player (video reference is a
plain text note for now), no Arena Configuration UI or spatial Heatmap
(later phases in the approved plan -- the `reviewed_location_zone_id`/
`_x`/`_y` columns exist in the schema already so that phase won't need a
migration, but there's no UI for them yet), no multi-user support.

**Superseded 2026-09-26: rebuilt as a live, hosted Claude Artifact.**
Shane's feedback on the local-server delivery was direct: it required him
to run a Python server himself rather than being live and accessible. V1's
static reference data (events/entrants/imported elimination facts, 1577
reviewable rows -- same group-elimination-safe id scheme as above, carried
over verbatim and re-verified: zero duplicate-id warnings against the live
`eliminations.csv`) was republished as a static `data.json` alongside a new
`page.html`, with review state (status, corrected fields, per-event video
reference) moved to the artifact's `db` runtime capability instead of a
local SQLite file -- lazy per-row documents, nothing pre-seeded, so
opening the artifact's link from any device gives the full working tool
immediately. Visual design reuses the main dashboard's Oswald/Inter type
pair and warm cream/amber token system rather than inventing a new one.
Live at `https://claude.ai/artifact/2XbASAVb7uuXQPyj8xBrp2`.

Shane's follow-up feedback: the location field (originally a six-option
text dropdown -- Left/Right/Hard camera/Far side/Corner/Unknown) wasn't
what he wanted; placing the elimination location was "the key interface
item" and needed to be a direct spatial action, not a list. Replaced with
a click-to-place top-down ring diagram: the reviewer clicks where the
elimination happened and the zone (Hard camera, Far side, Left, Right, or
each of the four corners individually -- Near-left/Near-right/Far-left/
Far-right, eight zones total, a real precision gain over the old single
"Corner" bucket) is derived automatically from the click's angle off ring
center, alongside the exact normalized x/y coordinate. Writes into the
already-reserved `reviewed_location_zone_id`/`_x`/`_y` schema fields plus a
derived legacy `location_side` value for continued compatibility. No
architecture-plan document was available in this session to check the
ring geometry against, so this was built from Shane's description and
flagged to him as such, open to correction.

Still open: an equivalent to `export_sync.py` for this architecture --
reading the artifact's `db` (via `ArtifactData`) and turning reviewed rows
into a proposed `eliminations.csv`, so Shane's review work can eventually
be merged into the live database through the standard protocol. Not yet
built; will be picked up once there's a meaningful batch of reviews to
pull.

## 24. V40 research handoff (promotion/masked tagging, physical profiles,
Hall of Fame/deceased status, families, Cain A. Knight timing closeout) —
verified and merged 2026-09-26 (Version 40)

External AI handoff, verified against an isolated copy and merged following
the same protocol as every phase before this. Baseline SHA-256 verified
against the actual V39 zip on disk before anything else: exact match,
confirming the handoff genuinely started from what was sent.

**Completed scope, spot-checked line by line against the delivered
manifest and report, not taken on trust:**
- `promotion_at_event`/`_status` populated for all 1,442 entrant rows
  (PROBABLE, one source each) -- exact count confirmed by direct diff.
- `wrestled_masked` completed for all 1,442 appearances: 51 TRUE / 1,391
  FALSE, exact match.
- `deceased_date_status`/`hall_of_fame_year_status` added to
  `wrestlers.csv`; 10 new deceased dates, 20 new Hall of Fame years, Sid
  Justice correctly appearing in both -- exact match.
- `families.csv`: 19 rows added (FAM001-FAM019) -- exact match.
- Billed weights: 4 Roxanne Perez gaps filled at 52 kg (two agreeing
  sources, upgraded to CONFIRMED, `physical_status` correctly promoted
  alongside); 7 Zelina Vega gaps filled at 48 kg (PROBABLE), with the
  106-vs-107 lb source disagreement correctly preserved as new flag F560
  rather than silently picked -- this is the methodology working exactly
  as intended, and is why the next finding below stood out by contrast.
- `sources.csv`: 67 rows added (S1775-S1841) -- exact match. F559
  correctly left open, untouched.
- Occupancy coverage expanded from 12 to 42 of 48 events (28+6 in the
  main pass, +8 more from the Cain Knight closeout below) -- row count
  confirmed by direct rebuild.
- `build_derived.py`/`build_dashboard_data.py` rebuilds are fully
  reproducible from the raw CSVs (byte-identical to the shipped derived
  layer and `dashboard/data.json` on a from-scratch rebuild) and
  idempotent (0 new `records_history.csv` entries on a second run) --
  48 events, 491 career rows, 70 entry-number rows, 90 current records,
  1,485 elimination pairings, 48 dynamic event rows, all matching the
  report exactly.

**Two genuine issues found during verification, not present in the
delivered report, and handled before merging rather than passed through:**

1. **Silent overwrite of previously-CONFIRMED data (RR1988M/RR1989M).**
   The Cain A. Knight timing closeout derives `elimination_clock_time` as
   physical-entry-time plus sourced survival-time for eight events. For
   six of them this only fills genuinely blank cells (safe, additive --
   170 rows). For RR1988M and RR1989M specifically, `apply_cain_timing_
   closeout.py` special-cased those two events to overwrite the field
   unconditionally, even where a value already existed. Diffed against
   live: 42 rows (after excluding one pure formatting fix with no value
   change) had their `elimination_clock_time` replaced outright --
   deltas up to nearly an hour, not rounding noise -- while
   `data_quality_status` stayed CONFIRMED and the new source was merely
   appended to `source_ids`, with no flag logged. That is a disagreement
   resolved by overwrite, not preserved -- exactly what this database's
   methodology exists to prevent, and inconsistent with how the same
   handoff correctly handled the Zelina Vega weight conflict (F560,
   above). Retained the existing multi-source CONFIRMED value for all 42
   rows; logged the derived candidate, its method, and three representative
   examples as new flags F561 (RR1988M, 17 rows) and F562 (RR1989M, 25
   rows), open, pending a targeted review of which timeline is actually
   correct. One side effect, and the honest one: reverting RR1989M's
   clock values means its occupancy timeline can no longer be completed
   from this handoff alone, so it drops back out of the occupancy table
   (41 of 48 events, not 42) until F562 is resolved. RR1988M's occupancy
   row is unaffected -- it already had a complete, independent timeline
   before this handoff touched it, so the override wasn't even necessary
   there.
   Separately noted, not fixed here: `eliminations.csv` carries its own
   independent `elimination_clock_time` column, used by the Rumble Event
   Logger's imported snapshot, and this handoff never touched it -- only
   `entrants.csv`'s copy. The two tables are now out of sync for the ~170
   legitimately-filled rows (`entrants.csv` has the new value,
   `eliminations.csv` still blank/old). No propagation script exists for
   this pair; needs a small sync utility, not built on this pass since it
   wasn't part of what was delivered and reviewed.

2. **`build_derived.py` occupancy-coverage bug (code, not data).** The
   ring-occupancy builder computes `coverage_percentage` once from its
   first-attempt interval set, then may replace that interval set with a
   different one from its sourced-physical-entry fallback -- but never
   recomputed the percentage against the set actually used. Result: 15
   events showed a spurious `0.0%` and 3 showed a stale `96.7%` despite
   having fully complete timelines (`timed_entrant_count ==
   eligible_entrant_count`), which would have surfaced as a misleadingly
   "incomplete" coverage badge on the live dashboard. This is new code
   contributed by this same handoff (the sourced-entrance fallback path),
   not a pre-existing bug. Fixed by recomputing `coverage_percentage`
   after the fallback reassignment, in the isolated copy, before merging;
   re-verified idempotent and byte-identical on a second rebuild. All 41
   occupancy rows now correctly read 100.0%.

**Verification protocol, same as every phase before this:** isolated
copy under `/home/claude/v40_verify` (never the live tree directly);
keyed diff (by primary-key tuple) against live for every changed table,
not `sort`-based; `validate_integrity.py` -- 0 errors before, during, and
after both corrections; full rebuild-from-scratch reproducibility check
on `derived/` and `dashboard/data.json`; idempotence re-confirmed with a
second consecutive rebuild; live tree only touched after the isolated
copy was fully clean, then re-derived and re-validated identically on
live before publishing (0 errors, byte-identical outputs to the isolated
copy); live dashboard artifact's current published source read in full
before republishing (required by the publish tool itself); SHA-256 of the
published `data.json` verified post-publish against the local file that
was sent.

Published as **Version 40**. Held back, both flagged rather than
silently merged or silently dropped: the RR1988M/RR1989M elimination-clock
conflict (F561/F562) and the entrants.csv/eliminations.csv clock-field
sync gap noted above.

## 25. Rumble Logger rebuilt around the two development briefs and the
    heatmap mockups — 2026-09-26 (Logger artifact Version 3, no database
    change)

Shane supplied two Development Brief documents (an original and a
"Revised Development Brief — Research Import, Verification & Spatial
Logging") plus a reference image showing a target "Data Capture
Interface" (live capture screen) alongside a "Final Heatmap View" (the
eventual end-user dashboard). Both had gone unread while the Logger
built in §23 was reviewed on its own; this phase read them in full and
rebuilt the Logger's capture screen to match, on the same db-backed
architecture (no new database/dashboard change).

**What changed, mapped to the revised brief's numbered requirements:**

- Per-event arena configuration (§13/§28): Hard Camera Side and
  Entrance Position selectors, persisted to `events/<id>` alongside the
  existing `videoReference` field (fixed a latent bug in the process --
  the old video-reference save called `.set()` with only that one
  field, which would have silently clobbered any other event-overlay
  field written after it; now goes through a single `saveEventOverlay()`
  merge helper).
- Spatial model rebuilt to keep raw coordinates unrotated while
  deriving a camera-relative zone from them (§13, and the original
  brief's §27/§36 "do not rotate or overwrite raw coordinates" rule):
  a click is stored as physical, un-rotated normalized x/y plus an
  8-point physical compass zone (N/NE/E/.../NW, N = top of the fixed
  diagram); the camera-relative label (hard-camera/near-right/.../
  near-left) is derived at display time from that physical zone plus
  the event's configured hard-camera side, never stored as the primary
  value. `locationZoneId` (camera-relative only, implicitly hard-camera
  = bottom always) is replaced by `locationCompass` (physical, un-rotated);
  the legacy single-word `locationSide` column is still populated the
  same way as before, now correctly derived through the camera-relative
  step instead of assumed.
- Elimination record now shows and allows editing of Eliminated Wrestler
  as well as Eliminated By / Assist / Method (§8/§18) -- previously the
  eliminated wrestler was a fixed heading, not a reviewable field.
- "Save & Resume" is the single primary action (§9), with the
  confirmed/corrected status now auto-detected by diffing the edited
  fields against the imported snapshot (§16/§27: unedited = confirmed,
  anything changed = corrected) rather than requiring an explicit
  choice every row; Uncertain/Conflict remain as explicit secondary
  buttons for the cases that need a human call.
- Keyboard shortcuts (§10): Enter = Save & Next, Ctrl+Enter = save
  without advancing, Left/Right = prev/next elimination, E/K/A/M focus
  the corresponding field.
- Numbered/faded prior-elimination markers on the main ring (§11/§12)
  and a live "Ring Overview" mini-map panel plotting every location
  recorded so far in the event.
- Live "Active Wrestlers" roster and "Event Timeline" panels, computed
  from entrants minus everyone eliminated at or before the row being
  reviewed -- an approximation (entrants are treated as present for the
  whole match rather than from their sourced entrance time, since not
  every event has entrance-timing data), noted here rather than
  presented as more precise than it is.
- A lightweight Match Clock (play/pause/reset, ±5s/±10s nudges, seeded
  from the imported elimination-clock time when one exists) as a
  reviewing aid, with a one-click "use this time" into the elimination-
  clock field -- deliberately simple rather than full video-transport
  integration, per the brief's own "initially they may simply
  adjust/display the target time" scope note.
- Event-type tabs (Elimination/Entrance/Weapon/Other Event) shown per
  the mockup, with only Elimination enabled -- matches the brief's
  explicit instruction not to let additional event types delay the core
  elimination-verification workflow (§35).

**Not yet built** (flagged rather than silently skipped): the
Entrance/Weapon/Other-Event tabs are visual only, no back-end yet;
free rotation of the entrance/camera markers (only the four cardinal
positions snap); a jump-to-elimination numbered navigator distinct from
Prev/Next; marker display modes (Current Only/Previous/All/Heatmap
Preview) -- today the ring always shows current + all-so-far; Ctrl+Z
undo; a "Review Complete" end-of-rumble summary screen with its own
heatmap; CSV/JSON/master-compatible export (still the deferred
`export_sync.py`-equivalent from §23, now more clearly scoped since the
schema this phase settled on -- `locationCompass` + derived
camera-relative zone -- is what it will need to read).

**Testing performed:** the full page script was extracted and syntax
checked, then run headlessly (Node + jsdom) against the live `data.json`
with a stubbed `db` capability -- boot, event-to-event navigation,
placing a ring click, saving with no field edited (verified status
comes back "confirmed", not "corrected" -- this caught and fixed a real
bug where the auto-status diff was comparing the eliminated-wrestler
name against the wrong source object and always registered a false
change), saving with an edited field (verified "corrected"), the
Enter-key shortcut, hard-camera-side reconfiguration persisting without
clobbering other event fields, and prior-elimination markers/timeline/
roster counts across two consecutive eliminations of the same event.
`ArtifactData` confirms the `reviews` collection is still empty --
Shane has not logged any real eliminations yet, so this was a
zero-risk schema change with nothing to migrate.

Published as **Version 3** of the Rumble Logger artifact (contract
0.2.60, `db` capability unchanged).

## 26. Entrance to 8-point compass + Weapon tab activated — 2026-09-26
    (Logger artifact Version 4)

Two follow-up requests. First: the Entrance Position selector was
cardinal-only (N/E/S/W); Shane asked for all 8 compass points, since a
ramp can genuinely sit at a corner rather than dead-center on a side.
Extended the selector and the ring diagram's marker placement to all 8
(`edgePoint()`/`labelOffsetY()` generalized); Hard Camera Side stays
cardinal-only, per the original brief's stated minimum and since Shane
only asked about the entrance.

Second: the Weapon tab, previously a disabled stub, is now functional
-- a controlled weapon list (Chair/Table/Ladder/Kendo Stick/Trash
Can/Ring Bell/Steps/Microphone/Championship Belt/Other, with a custom
name field when "Other" is picked), Used By / Target(s) / Introduced By
(all pre-filled from the entrant list via datalist), first-vs-subsequent
use, an optional outcome and notes, and the same click-to-place ring
location as eliminations. Saves to a new `weaponEvents` collection
(one doc per event, own id scheme -- these aren't imported research
rows, so there's no existing-record model to merge into). The form
clears and stays on the Weapon tab after each save, so multiple weapon
events can be logged back-to-back while watching without leaving the
screen or losing the running match clock -- switching tabs only
rebuilds the ring/form/bottom-row area, not the control bar the clock
lives in, and the weapon-events database subscription only forces a
full page rebuild on its first (initial-load) fire, not on every
subsequent write, for the same reason.

The Ring Overview mini-map and the main ring's faded "earlier this
event" markers now show both eliminations (circles) and weapon events
(squares) together, so the spatial picture stays complete regardless of
which tab is open. The Weapon tab has its own log list (all of this
event's weapon events, independent of elimination order, since weapons
aren't sequenced against eliminations the way review rows are).

**Not yet built:** editing or deleting a saved weapon event (append-only
for now); the Entrance/Other Event tabs remain stubs, per the brief's
own instruction not to let additional event types delay the elimination
workflow; keyboard shortcuts are scoped to the Elimination tab only
(the brief's shortcut list is written entirely in terms of the
elimination fields).

Tested the same way as Version 3: full headless run (Node + jsdom)
against live `data.json` with a stubbed `db` -- verified the entrance
selector offers exactly the 8 compass values and the hard-camera
selector still offers only 4, verified switching to Weapon does not
throw and shows the correct form, placed a location and saved a weapon
event (confirmed the doc landed in `weaponEvents` with the right
fields, including a real derived `locationCompass`), confirmed the form
resets and the tab stays on Weapon after saving, and confirmed
switching back to Elimination still works cleanly afterward. Zero
console errors throughout. `reviews` collection still empty at time of
publish, so again nothing to migrate.

Published as **Version 4** of the Rumble Logger artifact.

## 27. Joint eliminations now review as one step, not one per co-eliminator
    — 2026-09-26 (Logger artifact Version 5)

Bug report from Shane, verbatim: reviewing 1988, he logged the second
elimination's location and saved, but because it was a joint
elimination, he then had to log the same location again and "the
eliminated by changed to the previous assister."

Root cause, confirmed against `data.json` directly: the master
database stores a joint/shared elimination as one raw row **per
credited co-eliminator** (each row lists the other(s) as its "assist").
That's the correct shape for the master database, but the Logger's
review queue was iterating raw rows one at a time, so the same
physical elimination came up twice in a row -- once per co-eliminator
-- with "Eliminated By" flipping to whichever name was on that
particular row. Across the whole dataset this affects 125 of 1384
physical eliminations (97 pairs, 13 threes, 6 fours, 4 sixes, 2 fives,
2 eights, 1 row of 11); RR1988M elimination #2 (Bret Hart / Jim
Neidhart both credited for Tito Santana) is exactly this pattern.

Fix: introduced a "review group" -- every raw row sharing (event,
eliminated wrestler) -- as the unit the review screen now operates on,
since a wrestler is eliminated exactly once per match, making that pair
a safe, stable grouping key. `STATE.reviewGroupsByEvent` /
`reviewGroupsById` are built once at boot from the existing sorted raw
rows; `mergedGroup(id)` merges every member row the same way
`mergedReview()` already did, then adds a `memberIds` list and an
`eliminatorSummary` ("Bret Hart & Jim Neidhart") for display. The whole
app -- home queue, event overview, global overview, the review/capture
screen, Prev/Next, the timeline panel, the active-roster and ring
overview calculations, and the Weapon tab's "earlier this event"
markers -- now reads groups instead of raw rows, so "Elimination X of
N" reflects physical eliminations, not raw database rows.

On the review screen itself, a single-member group (the overwhelming
majority) looks exactly as before: one "Eliminated By" field plus the
original optional "Assist" field, unchanged, including the 9 known
cases where a solo credited eliminator has a genuinely separate assist
list (e.g. RR1994M Mabel, eliminated by Demolition Crush with six
listed assists) -- that pattern is preserved exactly. A multi-member
(joint) group instead shows one "Eliminated By" field per credited
co-eliminator, each pre-filled and editable independently, with a
"Joint elimination -- N credited eliminators" label above them; the
Assist field is dropped for these groups since it's now redundant --
saving auto-derives each member's assist list as the other members'
resolved eliminator ids, so they can never drift out of sync with each
other again. One location click, one set of shared fields (order,
clock, method, solo/shared, notes), Save & Resume now writes all of the
underlying per-eliminator docs in parallel with identical shared
fields and each member's own eliminator/assist/import-snapshot, and
advances to the *next physical elimination* -- not back through the
same one under a different name.

Tested with a full headless run (Node + jsdom) against live
`data.json` with a stubbed `db`: confirmed RR1988M's Tito Santana group
has exactly 2 members and both eliminator fields pre-fill correctly
with no Assist field shown; simulated a location click and a save,
then confirmed both underlying `reviews/RR1988M__tito-santana__bret-hart`
and `reviews/RR1988M__tito-santana__jim-neidhart` docs were written
with the same location/order/clock and correct cross-referenced assist
ids, status auto-detected as "confirmed", and navigation landed on the
*next* group, not the same one again; confirmed RR1994M's Mabel
elimination is still a single-member group with its original six-name
assist list intact and editable; confirmed RR1988M's event overview
now lists 19 eliminations (down from 23 raw rows, matching the
physical count) and the global overview aggregates from groups the
same way. Zero console errors throughout. `reviews` collection still
empty at time of publish, so nothing to migrate on this fix either.

Published as **Version 5** of the Rumble Logger artifact.

## 28. Ray Apollo/Doink-1995 identity, deep-research handoff brief, nationality breakdown, and the World Map — 2026-09-28 (Version 41)

Four pieces of work from one request, in order: a specific identity fact
from Shane, a handoff document for the external AI's next research pass,
and two new stat/dashboard features ("the stat side of things ...
Nationality/billed country per event. And various Dashboard features
like the world map").

**Ray Apollo as Doink the Clown, RR1995M.** Shane stated this directly.
Rather than writing it on his word alone, checked it against two further
independent sources beyond what he gave: a web search and
`prowrestling.fandom.com` (S052, already a registered source), which
both describe Ray Apollo as the character's permanent replacement after
Matt Borne originated the gimmick — clearing this project's own
2-independent-source CONFIRMED-adjacent bar for the specific fact
being added. Applied to `wrestlers.csv`'s `doink-1995` row (real_name
"Ray Licameli", status PROBABLE — the underlying performer identity
claim, not the Rumble appearance itself, is what's short of CONFIRMED)
and resolved three related flags (F071, F096, F099) in `flags.csv` with
the new source cited. `validate_integrity.py` clean before and after.

**Deep-research handoff.** Wrote and delivered
`DEEP_RESEARCH_INSTRUCTIONS_20260928.md` for the external AI: biography
gaps (335/530 wrestlers missing nationality, flagged top priority), the
7 specific events still missing ring-occupancy timing data, a proposed
schema for event ratings, and a scoped, explicitly-bounded plan for a
new `championships.csv` (WWE first, then WCW/ECW, then AEW/NJPW/
Impact-TNA, stop there unless a wrestler's existing notes point
elsewhere) — bounded deliberately since "theres just a lot of different
companies/titles out there" was Shane's own flag that this could sprawl
if left open-ended.

**Nationality / billed-country breakdown per event.** New derived table
`event_nationality_breakdown.csv` (added to `schema.py`'s
`DERIVED_TABLES`, computed in `build_derived.py` using the same
no-show-exclusion "actual entrant" convention as
`event_field_physical_stats.csv`): one row per distinct nationality
string per event, with `percentage_of_known` (share of entrants who
*have* a recorded nationality) kept separate from `coverage_percentage`
(share of the actual field that's known at all) so a sparse-coverage
event — most of the 2020s so far, typically ~10% — never gets
represented as if 100% of the field were accounted for. Compound
strings ("Mexican-American") are kept as their own bucket, not split.
Wired through `build_dashboard_data.py` into a `nationalityBreakdown` /
`nationalityCoveragePct` pair on each event object, and displayed as a
new "Billed nationality" panel on the event detail page (reusing the
existing `barRow` bar-list component), which hides itself entirely for
the events with zero recorded nationalities rather than showing an
empty or misleading panel.

**World Map.** New cross-division page (`#/map`, alongside Home and
Explore — nationality is a wrestler-level fact, not scoped to one
division, and a wrestler who's competed in both is counted once). New
global aggregation in `build_dashboard_data.py`: every `wrestlers.csv`
nationality string mapped to a country via an explicit
`NATIONALITY_TO_COUNTRY` table (compound entries plotted at whichever
country is named *first* in the string — a fixed mechanical rule, not a
per-wrestler judgment call) with approximate country-centroid
coordinates, projected through a plain equirectangular formula shared
between the Python build step and the page's JS. Any nationality string
with no table entry is *not* silently dropped — it's counted in the
coverage total but excluded from the map and surfaced verbatim in the
page's "Not yet plotted" panel and a build-time console warning, so a
newly-researched nationality can't quietly go unplotted. Currently: 22
countries, 195 of 530 wrestlers (36.8%). The map background itself is a
hand-built, deliberately simplified continent outline (not sourced from
any geographic dataset or external fetch — screenshotted and checked
for recognizability before shipping) that exists only to give the
markers spatial context; markers are sized by count (sqrt scale, area-
proportional), themed via the existing `--accent` token rather than a
new palette (a single-hue magnitude encoding, not a categorical one, so
the `dataviz` skill's palette validator doesn't apply here), with a
hover/focus tooltip per marker and a same-data table underneath for
accessibility and non-hover access. Clicking a marker jumps to that
country's first (alphabetical) wrestler's profile, resolving whichever
division actually holds that wrestler_id rather than assuming Men's.

Fixed a latent nav bug surfaced by adding this third global route: the
sidebar's "Home" link was computed as active on *any* division-less
page (`!route.division`), not just Home itself, so Explore had silently
been highlighting both itself and Home this whole time; the World Map
page would have done the same. Now each of Home / Explore / World Map
is exclusively active on its own route.

**Process note, in the interest of the same discipline this database
holds its data to.** Building `event_nationality_breakdown.csv`
required running `build_derived.py`, and that script's `DATA_DIR` is
hardcoded relative to its own file location — unlike
`build_dashboard_data.py`, it does not accept a directory argument, so
there is currently no way to point it at an isolated copy without
either monkey-patching it or copying the whole `scripts/` +`data/` tree
elsewhere. An isolated-copy test run of it was attempted first as
usual, but the actual `import build_derived` invocation ran against and
wrote to the **live** `data/derived/` directory before this was
noticed. Diffed the live tree against the pre-run backup afterward:
harmless (`event_dynamic_stats.csv`'s `as_of_date` moved to today, as
every full rebuild does; `records_history.csv` — the one genuinely
non-regenerable, append-only table — gained 0 new rows), and
`validate_integrity.py` was clean before and after. No data was lost or
corrupted, but the isolated-copy-first step didn't actually hold for
this one script, and should have been caught before running it rather
than after. `build_dashboard_data.py`'s run this session *was* properly
tested against an isolated copy first, per its own `sys.argv[1]`
support. Flagging here rather than quietly moving past it: a small
follow-up to make `build_derived.py` accept a `DATA_DIR` argument the
same way would close this gap properly.

Tested with a headless Playwright run against the live rebuilt
`dashboard/data.json` before publishing: confirmed the nationality
panel's figures match the derived CSV exactly for both a full-coverage
event (RR1988M: American 15/75%, Canadian 3/15%, Croatian-American
1/5%, Mexican-American 1/5%, 100% coverage) and a sparse one (RR2018M:
Irish/Japanese/Mexican at 1 each, 33.3% of known, 10% coverage overall);
confirmed the panel is absent (not empty) on a zero-nationality event
(RR2000M); confirmed the World Map's KPIs, marker count, and table row
count all agree (22 countries, 195/530, 36.8%); confirmed a marker's
hover tooltip and click-to-navigate both resolve correctly; confirmed
the nav-highlighting fix across Home/Explore/Map. Zero console errors
throughout (excluding pre-existing, unrelated proxy/font noise present
before this session's changes). `validate_integrity.py` clean.

Live dashboard artifact's current published source read in full before
republishing (required by the publish tool itself, and would have
surfaced any drift from what this session's edits were built on top
of — none found). Published as **Version 41**. Outstanding from this
phase: making `build_derived.py` accept an isolated `DATA_DIR` argument
(the process-discipline gap noted above); the Outstanding Items doc
still needs updating to reflect the nationality breakdown and World Map
as done.

## 29. World Map v2 — visual redesign and click-through full rosters — 2026-09-28 (Version 42)

Direct follow-up to Shane's feedback on v1: "The visual for the world
map could be a lot better (more visual). Locations should be clickable
to show all the wrestlers from locations." Two changes, both to the
same page.

**Full roster on click, not just a jump to one wrestler.** v1's marker
click navigated straight to the alphabetically-first wrestler in that
country — informative for nobody trying to see the whole list. Removed
the 12-wrestler cap `build_dashboard_data.py` previously put on each
country's `wrestlers` array (`wrestlerCountShown` field, and the `+N
more` truncation it drove, are both gone — the backend now always
serializes the full roster, e.g. all 127 for the United States, not a
preview sample) and added a per-wrestler `nationality` field so a
country with several compound-string nationalities (e.g. both
"American" and "Mexican-American" plotting to United States) can group
its roster by the actual recorded string rather than flattening it.
The existing "By country" table's rows are now expandable: clicking a
row — or clicking the matching marker on the map, which opens *and*
smooth-scrolls to its row — reveals every wrestler for that country as
linked names, grouped by nationality sub-label when more than one
string maps there. Only one row (map- or table-triggered) is open at a
time; the previously open one closes automatically. Added
`anyDivWlink(id, name)`, a cross-division counterpart to the existing
`wlink()` helper, since a country's roster mixes wrestlers from both
divisions and each needs resolving to whichever division actually
holds that `wrestler_id` before it can link anywhere.

**Visual redesign.** Applied the `dataviz` skill's guidance for a
single-series magnitude map: markers now encode count by size only (no
new hue — this is one accent color, not a categorical set), with a
widened radius range (5–27px, up from 4–20) so the count spread reads
more clearly, a glossy "sheen" highlight on each marker for depth, a
`.selected` state distinct from `:hover` so the active country stays
visually marked while its roster is open, a light graticule grid for
map-like context, direct labels on the top markers only (collision-
avoided at a 70px minimum spacing, so the crowded Western Europe
cluster doesn't get plastered with overlapping text), and a size
legend. The hover tooltip gained a "Click for the full roster ↓" hint
line so the new interaction is discoverable without trial and error.

Tested in this order: a Node `new Function()` syntax check on the
edited inline `<script>` block (clean, one 92k-character block); a
fresh `build_dashboard_data.py` run against an isolated copy of `data/`
confirming the uncapped roster (United States: 127 wrestlers returned,
`wrestlerCountShown` key gone) and `validate_integrity.py` clean on the
live data tree; then a headless Playwright pass against the **live**
`dashboard/` files specifically (not just the isolated copy) covering:
the map renders with zero page errors and zero non-network console
errors; clicking the United States marker opens and scrolls to its
table row and renders all 127 linked names; clicking a linked name
(Alexa Bliss) resolves cross-division correctly and navigates to
`/womens/wrestlers/alexa-bliss`, landing on a page that actually
contains her profile; clicking a table row directly (Canada) opens
that row's roster independently, without selecting any map marker;
switching from one open marker to another closes the first row and
opens only the second, with exactly one `.selected` marker at a time;
and the hover tooltip shows the new roster-preview + "Click for the
full roster ↓" copy. Live `dashboard/data.json` regenerated from live
`data/` (backed up before, diffed after: only the World Map's roster
arrays changed, all other totals identical) and `validate_integrity.py`
re-confirmed clean on the live tree post-regen.

Live dashboard artifact's current published source (Version 41) read
in full before republishing, per the publish tool's own requirement.
Published as **Version 42**.

Not addressed this phase, and flagged rather than started: Shane also
floated "we could even expand to cities" as a third, more tentative
idea. Investigated feasibility only — birthplace data actually has
better coverage than nationality (470/530 wrestlers vs. 195/530), but
those 470 rows span 369 distinct city strings, which would need
substantial hand-geocoding before a city-level map would mean
anything. This is a scope/investment decision for Shane, not yet put
to him.

## 30. Migrating the database to GitHub — 2026-09-28

Shane's request: get the database "accessible away from Claude" in a way
he can edit himself or hand to another AI, rather than everything living
only inside Claude sessions and being manually re-packaged/zipped each
time. Confirmed with him directly (rather than assuming) on two forks:
where it should live (GitHub, over Google Sheets/Drive or a plain cloud
folder — GitHub was the clear fit given the project is already CSVs +
Python scripts, which is exactly what git is built for) and what "another
AI access" actually means (both: stop manually re-packaging a zip for
the external ChatGPT research workflow, *and* make the finished database
generally explorable). Also confirmed: public repo (nothing sensitive in
WWE match stats, and public means any AI can read files directly from a
URL with zero auth), and Shane already has a GitHub account.

Checked what tooling was actually available before doing anything: no
GitHub MCP connector in the registry, no `gh` CLI or stored credentials
in the cloud sandbox, and the linked device (a Windows laptop) has no
`device_bash` tool available this session — so nothing here could
authenticate or push to Shane's GitHub account as him. The correct move
was to prepare a complete, ready-to-push package and hand it to him,
not to guess at a workaround or ask him to paste a credential into chat.

**What was built:**
- Split the old 2,600-line root `README.md` (really a year-by-year
  research journal) out to `docs/BUILD_LOG.md`, and wrote a new, short
  `README.md` proper to a repo's front door: what the project is,
  current status, the file structure, how to edit the data and rebuild
  derived tables/dashboard locally, and a dedicated "For an AI working on
  this repo" section pointing at `DEFINITIONS.md` and
  `BUILD_INSTRUCTIONS.md` (the existing full-handoff-build spec) as the
  required reading before touching anything.
- Added `dashboard/index.html` and a root `index.html`, both tiny
  redirects (not copies, so nothing can drift out of sync) — GitHub
  Pages has no directory-listing fallback, so without these the Pages
  root and the dashboard folder would each 404.
- Added a `.gitignore` (Python `__pycache__`, OS cruft).
- Left the existing loose top-level report/checkpoint files
  (`*_REPORT*.md`, `V40_*`, `*_CHANGED_ROWS.csv`, etc.) where they were
  rather than reorganizing them into a subfolder — several are referenced
  by one-off scripts under `scripts/` by their current relative path, and
  reorganizing them wasn't necessary for this task's actual goal.
- `git init`, configured `user.name`/`user.email`, one clean initial
  commit (148 files), default branch renamed to `main`.

Delivered as a zip (`royal_rumble_database.zip`, 4.9MB) containing the
full working tree **including the initialized `.git` folder** — so
unzipping it on Shane's machine already yields a real git repository
with one commit on `main`, not a plain folder he'd need to `git init`
himself. He still has to create the empty repo on github.com (a step
nothing here can do on his behalf) and either push it or drag-and-drop
upload it through GitHub's web UI — both paths given to him, since his
git/CLI comfort level isn't known.

**Left for Shane to complete, and not yet confirmed done:**
- Create the GitHub repo and get this initial commit onto it.
- Enable GitHub Pages (root source) so `dashboard/` is reachable at a
  public URL — README currently says `<pages-url>/dashboard/` as a
  placeholder until that URL exists.
- Decide on a license, if any (left unset deliberately — a legal choice,
  not this project's to make unilaterally; README explains how to add
  one via GitHub's UI if he wants one).
- Once live, this makes the recurring "package a zip and hand it to
  ChatGPT" step in the external-research workflow (see §26/§28's
  handoff process) obsolete — an AI can just be pointed at the repo URL
  or raw file URLs directly. Whether/how to actually change that
  workflow is Shane's call, not changed here.
