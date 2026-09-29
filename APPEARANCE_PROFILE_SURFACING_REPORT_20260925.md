# Appearance-profile dashboard surfacing

Date: 2026-09-25  
Baseline: cumulative championship/debut/return/ethnicity surfacing handoff

## Scope completed

Surfaced the remaining researched per-appearance profile fields in one combined pass:

- age at the event;
- billed height;
- billed weight;
- billed-from location;
- face/heel/tweener alignment;
- gimmick at the event;
- manager;
- tag team;
- faction/stable.

These values are deliberately displayed by Rumble appearance rather than flattened into one career-level fact, because billing, alignment, gimmick and affiliations can change over time.

## Existing coverage now visible

| Field | Populated appearances |
|---|---:|
| Age at event | 1,420 |
| Billed height | 1,442 |
| Billed weight | 1,430 |
| Billed from | 1,439 |
| Alignment | 1,442 |
| Gimmick | 208 |
| Manager | 116 |
| Tag team | 375 |
| Faction/stable | 222 |

Blank gimmick, manager, team and faction values remain blank in the underlying database and appear as a dash in the dashboard. They are not presented as verified absences.

## File-by-file changes

- `scripts/build_dashboard_data.py`
  - Adds structured physical and character profiles to all 1,442 event entrants and wrestler-history appearances.
  - Preserves `age_status`, `physical_status` and `alignment_status` for dashboard quality labels.
  - Adds billed-from, alignment, gimmick, manager, team and faction terms to Explore search without changing the source rows.
- `dashboard/page.html`
  - Shows compact physical and character lines beneath each entrant on event pages.
  - Adds a Rumble-by-Rumble profile-history table to every wrestler page.
  - Displays source-quality pills for age, physical facts and alignment.
  - Searches historical billed-from locations, gimmicks, managers, teams and factions through Explore.
  - Adds the missing UTF-8 charset declaration so existing punctuation and symbols render correctly under ordinary web servers.
- `dashboard/data.json`
  - Rebuilt deterministically from the unchanged database.

## Data, sources and flags

- Raw CSV changes: none.
- Derived CSV changes: none.
- New or changed sources: none.
- New or changed flags: none.
- All unrelated scripts and files remained byte-identical to the preceding handoff.

## Validation

- Validator errors before: 0.
- Validator errors after: 0 (`ALL CHECKS PASSED (the whole database)`).
- Dashboard output was byte-identical across two consecutive rebuilds.
- Dashboard data SHA-256: `3c444788157077edc913ff87b388ec3c68bd1c3c18c27f9267aa42f0aa62a6b4`.
- Automated population checks matched every field count in `entrants.csv`.
- Browser checks covered:
  - Kofi Kingston's multi-year New Day affiliation and full physical history;
  - RR1999M billed-from values including Vancouver and Parts Unknown;
  - Randy Orton retrieval through the `Legend Killer` gimmick search;
  - Blue Meanie retrieval through the `Pepperland` billed-from search;
  - correct UTF-8 rendering.

## Scope comparison

Before adding this report, exactly three files differed from the preceding cumulative handoff:

1. `scripts/build_dashboard_data.py`
2. `dashboard/page.html`
3. `dashboard/data.json`

## Recommended next step

The current researched profile data is now visible rather than trapped in CSVs. The next useful task should be an honest remaining-gap audit against the current live schema: identify fields that are still genuinely unresearched, distinguish them from intentional `N/A` values, rank them by dashboard impact, and produce one consolidated queue before any new website visits begin.
