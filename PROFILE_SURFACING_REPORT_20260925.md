# Championship, debut/return and ethnicity dashboard surfacing

Date: 2026-09-25  
Baseline: cumulative entrance-statistics handoff built from live Version 36

## Scope completed

Surfaced three already-researched groups that previously existed in the CSV data but were largely invisible on the dashboard:

- championship status when each Rumble match began, including reign number, reign age, tag partner and same-card defence/loss context;
- Royal Rumble debut, WWE debut and documented return context for every appearance;
- publicly self-described ethnicity/heritage values and their existing status labels.

No new research was performed. No factual value or status was created, changed or upgraded.

## Coverage surfaced

- 1,442 entrant appearances with appearance number and Rumble-debut classification;
- 471 Rumble debuts;
- 3 WWE debuts occurring at a Royal Rumble, with their recorded dates;
- 68 returning-wrestler appearances;
  - 22 have a descriptive absence length;
  - 46 remain honestly labelled as having no established absence length;
- 133 reigning-champion appearances;
- 2 titleholders who lost their championship earlier on the card and therefore correctly are not presented as current champions when the Rumble began;
- 21 wrestler profiles with ethnicity/heritage values, shown only where the existing database already records a self-described value.

## File-by-file changes

- `scripts/build_dashboard_data.py`
  - Adds entrant-level appearance number, debut, return, absence and championship objects to dashboard JSON.
  - Preserves the distinction between a current champion and somebody who lost a title earlier on the card.
  - Adds ethnicity/heritage and WWE debut year to wrestler bios.
  - Adds ethnicity/heritage to the Explore search index.
  - Adds each event's existing champions-in-field count.
- `dashboard/page.html`
  - Adds Rumble debut, WWE debut, Return, Champion and Lost title earlier badges to event rosters.
  - Adds champions-in-field to event summaries.
  - Adds ethnicity/heritage and WWE debut year to profile facts.
  - Expands Rumble history with appearance number and a context column.
  - Adds dedicated Championship status at entry and Debuts and returns panels.
  - Makes ethnicity/heritage searchable and visible in Explore results.
- `dashboard/data.json`
  - Rebuilt deterministically from the unchanged CSV database.

## Data, sources and flags

- Raw `data/*.csv` changes: none.
- Derived CSV changes: none.
- New sources: none.
- Changed sources: none.
- New flags: none.
- Changed flags: none.
- Scripts other than `build_dashboard_data.py`: byte-identical to the preceding handoff.

## Validation

- Baseline validator errors: 0.
- Final validator errors: 0 (`ALL CHECKS PASSED (the whole database)`).
- Dashboard output was byte-identical across two consecutive rebuilds.
- Dashboard output SHA-256: `d203522b04a97a2121d5208d15b80078d3d9326a65dd2cb1873ca50fa4fa4a2d`.
- Population assertions passed for all 1,442 appearances and every count listed above.
- Browser smoke tests covered:
  - championship-at-entry and earlier-same-card title loss on Roman Reigns' profile;
  - Rey Mysterio's confirmed ethnicity/heritage and return history;
  - RR2017M event-roster title-loss context;
  - ethnicity/heritage retrieval through Explore search.

## Scope comparison

Compared with the immediately preceding entrance-statistics handoff, exactly three generated/source files changed before this report was added:

1. `scripts/build_dashboard_data.py`
2. `dashboard/page.html`
3. `dashboard/data.json`

Every data CSV, derived CSV, source registry, flag and unrelated script remained byte-identical.

## Recommended next step

The highest-value remaining dashboard-only improvement is to surface the per-appearance physical and character profile already researched in `entrants.csv`: billed height, billed weight, billed-from location, alignment, gimmick, manager, tag team and faction. These values belong in each wrestler's Rumble-by-Rumble history because they can change over time; presenting only a single career-level value would lose that event-specific history.
