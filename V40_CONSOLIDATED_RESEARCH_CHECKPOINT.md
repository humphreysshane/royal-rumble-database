# V40 consolidated research checkpoint

Baseline: live Version 39 package supplied 2026-09-26. Its SHA-256 was verified as
`3E31950299F4BE3240BE21CA09094B3A402F8B0BC29B879F1FEA38A0399A627D` before work began.

## Completed in this checkpoint

### Occupancy-timeline coverage

- Extended `scripts/build_derived.py` with a conservative second timeline method:
  `entrances.csv:enters_ring_ts` plus confirmed `entrants.csv:ring_time_seconds`.
- Entry numbers 1 and 2 begin at 00:00 under the match convention.
- Rows are rejected if an entrant is incomplete or a calculated timestamp exceeds the
  event duration.
- Preserved all existing record IDs by matching the stable record identity
  `(division, category, record_name)` and appending genuinely new records after the
  previous highest ID.
- Coverage increased from 12 Men's / 0 Women's events to 27 Men's / 6 Women's events
  (33 total). The 21 newly eligible events are RR1990M, RR1991M, RR1992M, RR1993M,
  RR1995M, RR1996M, RR1997M, RR1998M, RR2017M, RR2018M, RR2018W, RR2019M, RR2019W,
  RR2020M, RR2020W, RR2021M, RR2021W, RR2022M, RR2022W, RR2023M, and RR2023W.
- Added three Women's occupancy records without renumbering any Version 39 record:
  R088–R090.

### Brand/promotion affiliation

- Populated `promotion_at_event` and `promotion_at_event_status` on all 1,442 entrant
  rows.
- Distribution: WWF 440; Raw 387; SmackDown 310; WWE 150; Unaffiliated 75; NXT 49;
  ECW 22; NXT UK 3; TNA 3; AAA 2; 205 Live 1.
- Every value is `PROBABLE`, because this tranche has one independent event-page source.
  No row was incorrectly promoted to `CONFIRMED`.
- Pre-brand-split rows use WWF; the unified-brand RR2012–RR2016 rows use WWE; other
  years use the event table's specific brand/promotion.
- The importer resolves names against the actual Men's and Women's event rosters,
  rather than trusting table order. This corrects years whose source page lists the
  Women's table first.
- Malformed 2010 rowspan cells were rejected and replaced only through explicit,
  event-scoped brand overrides.

### Schema correction

- Added the missing `deceased_date_status` and `hall_of_fame_year_status` companion
  columns to `wrestlers.csv`. They remain blank pending the full evidence audit; no
  confidence values were inferred from unrelated row-level citations.

### Sources

- Added S1775–S1813: one Wikipedia/reference event source for each Royal Rumble year,
  1988–2026, reliability tier 10, accessed 2026-09-25.
- No existing source row was modified.

## Files changed

- `data/entrants.csv` — 1,442 promotion values/statuses and supporting source IDs.
- `data/wrestlers.csv` — two additive status columns only; no wrestler fact changed.
- `data/sources.csv` — 39 event-page sources.
- `scripts/build_derived.py` — occupancy fallback and stable record-ID allocation.
- `scripts/research_consolidated_v40.py` — idempotent research application script.
- `scripts/research_inputs/promotion_brand_rows_2003_2026.json` — captured event-table
  research input.
- `data/derived/ring_occupancy_stats.csv`, `ring_crowdedness.csv`,
  `ring_physical_peaks.csv`, `records.csv`, `records_history.csv`, and
  `.records_baseline.csv` — regenerated derived outputs.
- `dashboard/data.json` — regenerated dashboard payload.

No flag was added or changed in this checkpoint. Source-table anomalies were resolved
mechanically against event rosters or left unused; no factual conflict was silently
decided.

## Validation

- Baseline: 0 errors.
- After raw-data edits and full rebuild: 0 errors (`ALL CHECKS PASSED`).
- Derived layer and dashboard were rebuilt from scratch after the changes.

## Still outstanding from the consolidated brief

This checkpoint is not represented as completion of the full seven-item brief. The
database-wide deceased/Hall of Fame evidence audit, family table, per-appearance masked
tagging, remaining 15 occupancy events, and 12 Women's weight gaps still require
source-level resolution. A bulk discovery sweep was deliberately not applied after it
produced identity collisions (for example, a search for Virgil resolving to Dusty
Rhodes). Those candidates were discarded rather than allowed into the database.

For the Women's weight gaps, the initial sweep found conflicting published figures for
Zelina Vega and no reliable billed weight for Roxanne Perez or Kelani Jordan. Those
fields remain blank rather than being filled from weak or conflicting material.
