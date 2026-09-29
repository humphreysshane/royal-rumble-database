# Championship and Return Records Report — 2026-09-25

## Scope

This phase converts already researched entrant-level championship and return fields into tracked records and dashboard facts. It performs no new biographical research and changes no raw data, sources, or flags.

## New records

| ID | Division | Record | Result |
|---|---|---|---|
| R064 | Men's | Rumble with most reigning champions in the field | RR2006M — 6 |
| R065 | Men's | Longest title reign entering a Rumble | Pete Dunne, RR2019M — 617 days as NXT UK Champion |
| R066 | Men's | Most Rumble appearances as reigning champion | Shinsuke Nakamura — 4 (tied with The Miz) |
| R067 | Men's | Rumble with most returning wrestlers | RR2015M — 4 (tied with RR2021M) |
| R068 | Men's | Most Rumble appearances classified as a return | Edge — 2 (tied with Goldust, Rey Mysterio, The Honky Tonk Man and The Hurricane) |
| R069 | Women's | Rumble with most reigning champions in the field | RR2025W — 6 (tied with RR2026W) |
| R070 | Women's | Longest title reign entering a Rumble | Bianca Belair, RR2025W — 154 days as WWE Women's Tag Team Champion |
| R071 | Women's | Most Rumble appearances as reigning champion | Chelsea Green — 2 (tied with Giulia and Kairi Sane) |
| R072 | Women's | Rumble with most returning wrestlers | RR2018W — 11 |
| R073 | Women's | Most Rumble appearances classified as a return | Molly Holly — 3 |

Championship records count a title only when `current_champion_title` is populated at match start. A title lost earlier on the same card is therefore excluded. Return records use the existing `is_returning_wrestler` classification and do not infer an absence duration.

## File-by-file changes

- `scripts/build_derived.py`: added deterministic generation of the ten championship/return records after the established R001–R063 sequence.
- `data/derived/records.csv`: added R064–R073.
- `data/derived/records_history.csv`: appended one history entry for each new record.
- `data/derived/.records_baseline.csv`: refreshed to the current 73-record baseline.
- `scripts/build_dashboard_data.py`: exposes the documented return count for every event as `returningCount`.
- `dashboard/data.json`: rebuilt from the complete current data and derived layers.
- `dashboard/page.html`: shows “Returning wrestlers” in each event summary.

No rows changed in `data/entrants.csv`, `data/sources.csv`, `data/flags.csv`, or any other raw-data CSV. No source or flag was added or updated. Existing residual research flag F559 remains unchanged; no missing height, weight, or billed-from value was guessed.

## Verification

- Baseline validator: 0 errors (`ALL CHECKS PASSED`).
- Final validator: 0 errors (`ALL CHECKS PASSED`).
- Independent group counts reproduced the championship and return event/entrant leaders, including all ties.
- A second derived build produced 0 new history entries; history remained at 190 rows and byte-stable.
- Two consecutive dashboard builds produced identical SHA-256 output.
- Derived output now contains 73 current records across 48 events; the dashboard contains 37 Men's and 36 Women's records.

## Recommended next phase

Continue the same reuse-first approach by auditing which already researched entrant fields can support further defensible records or filters. Keep unresolved physical-profile gaps behind their existing research flags unless a genuinely new source resolves them.
