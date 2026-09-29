# Entrance-derived statistics and dashboard handoff

Baseline: `royal_rumble_database_LIVE_V36_20260925.zip`  
Baseline SHA-256: `c3c027ef62beeed582159d8c541682b6ff96533e3bd42557a1ecbcd08caf11ef`  
Date: 2026-09-25

## Scope completed

Built and surfaced the entrance-stat layer requested in `CONTINUE_20260925b.md`, entirely from the existing Version 36 `entrances.csv` and `events.csv` values:

- longest and shortest buzzer-to-ring entrance, separately for Men's and Women's divisions;
- latest valid physical ring entry, separately by division;
- largest valid variance from the advertised entry interval, separately by division;
- event-level median and average entrance duration, coverage, extremes, latest physical entry and interval behavior;
- longest and shortest event median as tracked all-time records, separately by division;
- dashboard event panels and records cards for all of the above.

No raw factual data was changed. No source, flag, entrant, wrestler, event, elimination or entrance row was added or edited.

## Method and guardrails

- Entrance-duration statistics use only nonblank `entrance_duration_seconds` values already in `entrances.csv`.
- Interval comparisons require two consecutive entry numbers with countdown timestamps and a numeric advertised interval.
- Buzzer gaps over five minutes are excluded as source-video clock discontinuities, not interpreted as real entry delays.
- An absolute `enters_ring_ts` is eligible for the latest-entry statistic only when it does not exceed that event's recorded match duration.
- This excludes four RR2008M late-match absolute timestamps that use a discontinuous source-video clock. Their raw rows remain untouched, and their explicit entrance durations remain eligible.
- All outputs are tagged `DERIVED`; no factual status was upgraded.

## File-by-file changes

- `scripts/schema.py`
  - Registered the new `data/derived/entrance_event_stats.csv` schema.
- `scripts/build_derived.py`
  - Loads the existing entrance table.
  - Rebuilds 48 event-level entrance summary rows.
  - Adds 12 division-separated entrance records while preserving existing R001-R051 IDs.
  - Appends the corresponding first-history entries and remains idempotent on repeat builds.
- `scripts/build_dashboard_data.py`
  - Loads the event summaries and raw entrance durations.
  - Adds event entrance summaries and per-entrant entrance timing values to dashboard JSON.
- `dashboard/page.html`
  - Adds median entrance to the event hero.
  - Adds an Entrance Timing panel with coverage, median, average, range, latest physical entry, interval behavior and a longest-to-shortest duration chart.
- `dashboard/data.json`
  - Fully rebuilt from the updated scripts and derived tables.
- `data/derived/entrance_event_stats.csv`
  - New complete 48-row table: 39 Men's events and 9 Women's events.
  - Duration coverage: 954 Men's rows across 34 events; 168 Women's rows across 6 events.
- `data/derived/records.csv`
  - Added R052-R063, listed below.
- `data/derived/records_history.csv`
  - Added H0169-H0180 as the initial history entries for R052-R063.
- `data/derived/.records_baseline.csv`
  - Regenerated to the new 63-record baseline.

All other files are byte-identical to Version 36, apart from the rebuilt dashboard payload listed above.

## New records.csv rows

| ID | Division | Record | Holder/event | Value |
|---|---|---|---|---|
| R052 | Men's | Longest entrance | Hornswoggle, RR2008M | 25:45 |
| R053 | Men's | Shortest entrance | Rick Rude, RR1990M | 0:00 |
| R054 | Men's | Latest physical ring entry | Kane, RR2011M | 61:52 |
| R055 | Men's | Biggest advertised-interval variance | Dolph Ziggler, RR2016M | 91 sec late |
| R056 | Men's | Rumble with longest median entrance | RR2023M | 0:39 |
| R057 | Men's | Rumble with shortest median entrance | RR1991M | 0:07 |
| R058 | Women's | Longest entrance | Billie Kay, RR2021W | 7:25 |
| R059 | Women's | Shortest entrance | Brie Bella, RR2018W | 0:11 |
| R060 | Women's | Latest physical ring entry | Becky Lynch, RR2019W | 58:02 |
| R061 | Women's | Biggest advertised-interval variance | Natalya, RR2021W | 117 sec late |
| R062 | Women's | Rumble with longest median entrance | RR2023W | 0:33.5 |
| R063 | Women's | Rumble with shortest median entrance | RR2018W | 0:21.5 |

`records_history.csv` received one matching initial row per record: H0169-H0180. These are generated rows, not separately researched facts.

## Sources and flags

- New sources: none.
- Changed sources: none.
- New flags: none.
- Changed flags: none.

## Validation and reproducibility

- Baseline validator: `ALL CHECKS PASSED (the whole database).`
- Final validator: `ALL CHECKS PASSED (the whole database).`
- Validator errors before: 0.
- Validator errors after: 0.
- First derived build: 12 new history rows, 180 total.
- Immediate second derived build: 0 new history rows, 180 total (idempotence confirmed).
- Assertions passed: 48 event summaries, 12 entrance records, 180 history rows, 63 dashboard records.
- Browser smoke tests passed for RR2008M's entrance panel, Men's entrance records and RR2023W's half-second median; no local page errors.

## Recommended next step

This closes the requested entrance-derived-stat layer. The best next phase is a dedicated dashboard surfacing pass for already-built but still largely invisible profile data: championship-at-entry history, company/Rumble debut and return context, and the strictly self-described ethnicity/heritage values. That can be done without revisiting the Cageside entrance pages or altering the source data completed here.
