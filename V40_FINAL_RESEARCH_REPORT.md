# V40 final research handoff

Baseline: live Version 39 supplied 2026-09-26, SHA-256
`3E31950299F4BE3240BE21CA09094B3A402F8B0BC29B879F1FEA38A0399A627D`.

This report supersedes the earlier checkpoint report. `V40_CHANGED_ROWS.csv` lists every
raw CSV row changed or added against V39, its changed fields, and the reason.

## Completed scope

- Populated `promotion_at_event` and its status for all 1,442 entrant rows using the
  1988-2026 event pages. All remain `PROBABLE` (one independent source).
- Completed `wrestled_masked` for all 1,442 appearances: 51 `TRUE`, 1,391 `FALSE`.
  The tagging is appearance-specific, including Kane's masked/unmasked periods,
  Hurricane/Gregory Helms, and Mighty Molly/Molly Holly.
- Added `deceased_date_status` and `hall_of_fame_year_status` to `wrestlers.csv`, then
  applied only exact-identity audit results. Ten deceased dates and 20 Hall of Fame
  years were added, all `PROBABLE`. Search collisions were discarded.
- Added 19 sourced real-life family units to `families.csv`. Persona IDs are retained
  where necessary so entrant rows can join without changing the existing identity model.
- Filled all four Roxanne Perez billed-weight gaps with 52 kg from two agreeing sources
  (`CONFIRMED`). Filled all seven Zelina Vega gaps with 48 kg (`PROBABLE`) and logged
  the published 106-vs-107 lb disagreement as F560. Kelani Jordan remains honestly
  blank because no reliable published billed weight was established.
- Expanded complete occupancy coverage from 12 events to 34 events (28 Men's, 6
  Women's). The final extra event is RR2015M: Curtis Axel's confirmed zero-time no-show
  is excluded without excluding match winners. RR2015M's derived peak is 10 entrants,
  47:05-48:16.
- Preserved stable record IDs and added Women's occupancy records R088-R090.

## Raw CSV changes

- `data/entrants.csv`: all 1,442 rows changed for promotion and masked tagging; 11 of
  those rows also received billed weights (4 Roxanne Perez, 7 Zelina Vega).
- `data/wrestlers.csv`: two status columns added; 29 wrestler/persona rows gained facts
  (10 deceased dates, 20 Hall of Fame years, with Sid Justice in both groups).
- `data/families.csv`: 19 rows added (FAM001-FAM019).
- `data/sources.csv`: 67 rows added (S1775-S1841): 39 event pages plus 28 exact-identity,
  weight, and family sources. No existing source row was changed.
- `data/flags.csv`: F560 added for Zelina Vega's 106/107 lb source conflict. Existing
  F559 remains open for the still-unresolved Kelani Jordan weight and other legacy gaps.
- `V40_CHANGED_ROWS.csv`: exhaustive raw-row manifest against Version 39 (1,558 rows).

## Code and captured inputs

- `scripts/build_derived.py`: sourced entrance-time occupancy fallback, stable record-ID
  allocation, and correct zero-time no-show handling.
- `scripts/research_consolidated_v40.py`: idempotent promotion/brand importer.
- `scripts/apply_v40_remaining_research.py`: idempotent exact-identity profile, weight,
  family, and masked-status application.
- `scripts/build_v40_change_manifest.py`: reproducible V39-to-V40 row manifest.
- `scripts/research_inputs/promotion_brand_rows_2003_2026.json`: captured event-table
  promotion research.
- `scripts/research_inputs/wrestler_audit.json`: retained raw discovery audit; only the
  explicit exact-identity allow-list in the application script is committed to data.

## Rebuilt outputs

The complete derived layer and `dashboard/data.json` were rebuilt. Changed derived
files are `.records_baseline.csv`, `event_dynamic_stats.csv`,
`event_field_physical_stats.csv`, `records_history.csv`, `records.csv`,
`ring_crowdedness.csv`, `ring_occupancy_stats.csv`, `ring_physical_peaks.csv`.

## Validation

- Version 39 baseline: 0 errors.
- Final V40 after raw edits, derived rebuild, and dashboard rebuild: 0 errors —
  `ALL CHECKS PASSED (the whole database)`.
- Final research application script: byte-stable on a second run (idempotence passed).
- Derived build: 48 events, 491 career rows, 70 entry-number rows, 90 current records,
  1,485 elimination pairings, and 48 dynamic event rows.

## Cain A. Knight timing closeout

The registered Cain A. Knight articles were audited at section level rather than merely
at source-row level. Earlier work had imported buzzer clocks but omitted many published
survival-time lists. The complete survival, entrance-delay, and buzzer sections were
harvested for RR1988M, RR1989M, RR1994M, RR2000M, RR2002M, RR2004M, RR2006M, and
RR2010M.

- Added 80 previously blank sourced ring times.
- Updated or added 214 entrance-timing rows.
- Derived 215 global elimination clocks from sourced physical entry plus survival time.
- Occupancy coverage increased from 34 to 42 of 48 events.
- Newly complete: RR1988M, RR1989M, RR1994M, RR2000M, RR2002M, RR2004M, RR2006M,
  and RR2010M.
- Added `research_cain_timing_closeout.py`, `apply_cain_timing_closeout.py`, and
  `scripts/research_inputs/cain_timing_closeout.json`.
- Final validation after the timing rebuild remains 0 errors.

## Honest residuals and recommendation

Six events still lack a complete replayable occupancy timeline because one or more
physical-entry timestamps are genuinely absent; they were not approximated. Their
waiting-interval articles supply every buzzer clock and companion articles supply every
survival time, but the prose supplies only selected entrance delays. Kelani Jordan's
billed weight also remains blank. These are documented gaps, not incomplete processing
of available evidence. The next efficient phase should be a targeted primary-video or
event-timing pass for only those six events, followed by the remaining open-flag queue;
there is no reason to repeat the completed database-wide V40 sweeps.
