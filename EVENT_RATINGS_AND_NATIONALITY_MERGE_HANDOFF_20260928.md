# Nationality verification and event-ratings handoff — 2026-09-28

## Outcome

- Verified and retained the completed nationality sweep: 530 of 530 wrestler profiles now have a populated `nationality` value; zero remain blank.
- Added a new source-preserved event-ratings table covering every Royal Rumble match in the database: 96 observations across 48 event IDs, exactly two observations per event.
- Rebuilt the dashboard data and ran the complete integrity validator. Result: **0 errors before and 0 errors after**.

## Nationality sweep verification and merge

The nationality working copy was compared with the Version 40 baseline before the ratings work began.

- 335 wrestler rows changed.
- All 335 changes populated a previously blank `nationality` field.
- No wrestler rows were added or removed (530 before and after).
- Final nationality coverage is 530/530, with no blanks.
- `source_ids` changed on 258 of those profiles as sources were attached or reused.
- The same source-led profile pass also retained 14 incidental same-page corrections: six `deceased_date_status` updates, six `hall_of_fame_year_status` updates, one `hall_of_fame_year`, and one `deceased_date`. These are documented in `BROAD_RESEARCH_HANDOFF_20260928.md` and the nationality research manifest.

The detailed per-profile evidence is in `research/nationality_sweep_20260928.csv`; the dedicated merge narrative is in `NATIONALITY_SWEEP_HANDOFF_20260928.md`.

## Event ratings added

Created `data/event_ratings.csv` with the requested schema:

`rating_id,event_id,source_name,rating_scale,rating_value,rating_type,review_url,rating_status,source_ids,notes`

For each of all 48 event IDs, the table contains:

1. Cagematch's live fan aggregate, retained on its original 0–10 scale with the valid-vote count and access date in `notes`.
2. The Wrestling Observer Newsletter match rating displayed by Cagematch, retained in its original five-star notation, including `DUD` where displayed.

No scores were normalized, averaged together, or converted into a project-authored overall rating. All 96 rows are `PROBABLE`, because each observation is currently supported by one named database page. Cagematch fan aggregates are time-sensitive and may change as new votes are submitted; this handoff freezes the value and vote count observed on 2026-09-28.

Royal Rumble 2005 was checked directly after an event-card cache showed 8.12; its cited match page displayed 8.13 from 247 valid votes, so 8.13 is the retained value. The same page displayed the WON rating as `DUD`, which is preserved without reinterpretation.

## Sources

- Added 47 direct Cagematch match-page source rows, `S1847` through `S1893`.
- Reused existing source `S002` for RR1988M because its URL already exactly matched the direct Cagematch match page.
- Five earlier sources from the nationality/profile sweep are also present in this consolidated handoff (`S1842`–`S1846`).

## File-by-file changes

- `data/wrestlers.csv` — verified nationality merge and the documented incidental profile findings.
- `data/sources.csv` — nationality/profile sources plus 47 direct Cagematch match-page sources.
- `data/event_ratings.csv` — new; 96 sourced rating observations.
- `scripts/schema.py` — registers the new table and its fields.
- `scripts/validate_integrity.py` — validates IDs, events, rating types, statuses, values, and source references.
- `scripts/build_dashboard_data.py` — carries each event's ratings into `dashboard/data.json`.
- `scripts/build_event_ratings_20260928.py` — reproducible, idempotent builder for this ratings collection.
- `dashboard/data.json` — rebuilt; all 48 events contain their two rating observations.
- `README.md` — documents `event_ratings.csv` in the database file list.
- `research/nationality_sweep_20260928.csv` — evidence manifest for the nationality sweep.

No existing flag was closed or altered and no new flag was required: ratings are retained as attributed subjective observations rather than treated as conflicting factual claims.

## Reproducibility and validation

- Ratings builder: 96 rows for 48 events; rerun added zero sources.
- Idempotency: `event_ratings.csv`, `sources.csv`, and `dashboard/data.json` were byte-stable on the no-change rerun before the final verified RR2005 value refresh.
- Dashboard rebuild: 39 Men's events and 9 Women's events; all 48 carry ratings.
- Final validator: `ALL CHECKS PASSED (the whole database).`
- Validator error count: **0 before / 0 after**.
