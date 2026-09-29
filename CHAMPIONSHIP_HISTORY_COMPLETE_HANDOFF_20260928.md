# Complete cross-promotion championship-history handoff — 2026-09-28

## Outcome

Built one consolidated career-spanning championship-history layer rather than
separate partial handoffs. It covers every dated structured reign history
located across 16 major promotions and their directly inherited or sanctioned
lineages.

- 16 promotions
- 234 championship lineages
- 8,568 dated lineage records
- 7,589 wrestler/team reigns
- 742 vacancies
- 237 unifications, retirements, deactivations and other lineage events
- 2,411 reign rows linked to existing Royal Rumble wrestler IDs
- 376 distinct Royal Rumble wrestlers linked to at least one reign

This layer is deliberately separate from
`entrants.csv:current_champion_title`, which remains a point-in-time fact about
the beginning of one particular Royal Rumble match.

## Promotions covered

WWE/WWF/NXT, WCW, ECW, AEW, TNA/Impact, ROH, NJPW, NWA, AWA, All Japan Pro
Wrestling, Pro Wrestling Noah, World Wonder Ring Stardom, AAA, CMLL, Major
League Wrestling and Lucha Underground.

The title set includes world, secondary, television, regional, developmental,
weight-class, openweight, specialty, tag-team and trios championships. It also
preserves predecessor/adopted lineages where a covered promotion's history
directly includes them. NWA affiliate territory belts that were independent
local championships are not silently treated as championships of the modern
central NWA promotion.

## Data model

- `data/promotions.csv` — promotion identity, operating dates, former names
  and external links.
- `data/championships.csv` — title identity, promotion, level, division,
  active/retired state, lineage relationships and official/reference URLs.
- `data/championship_reigns.csv` — individual reigns plus vacancies and
  lineage events.

`champion_name` always preserves the historical source display. The optional
`champion_wrestler_ids` field links one or more members to this project's
existing wrestler registry. A blank link does not mean the champion is
unknown; it normally means that wrestler never entered a Royal Rumble or that
the source exposed only a team name rather than its members.

## Source and refresh design

Added 233 structured championship-history source registrations, `S1894`
through `S2126`. Each imported observation is `PROBABLE` because it currently
has one structured history source. Official history links are retained where
available for future independent confirmation; no row was upgraded merely
because the import was automated.

The external sources contained live current-reign counters, and one page
returned different cached day totals on two consecutive requests. To prevent
that instability from contaminating normal builds:

- `research/championship_history_snapshot_20260928.json` is the committed,
  dated parsed-source snapshot.
- `python3 scripts/build_championship_history_20260928.py` rebuilds all three
  CSV tables deterministically and offline from that snapshot.
- `python3 scripts/build_championship_history_20260928.py --refresh` is the
  explicit network operation that revisits all 234 configured lineages and
  replaces the snapshot. Its diff must be reviewed before publication.

No dashboard page or database build depends on Wikipedia being online at
runtime.

## Dashboard feed

`scripts/build_dashboard_data.py` emits a top-level `championshipHistory`
object with:

- all promotion metadata and external links;
- all 234 championships and 8,568 dated records;
- current/vacant/retired state;
- source-preserved reign details;
- a per-wrestler summary of reign count, championship IDs and promotion IDs.

The supplied baseline did not contain `dashboard/page.html`, so the data
contract is complete and ready for the published front-end, but no substitute
HTML file was invented in this handoff.

## File-by-file changes

- `data/promotions.csv` — new, 16 rows.
- `data/championships.csv` — new, 234 rows.
- `data/championship_reigns.csv` — new, 8,568 rows.
- `data/sources.csv` — 233 new championship-history source rows.
- `research/championship_history_snapshot_20260928.json` — new reproducible
  parsed-source snapshot.
- `scripts/build_championship_history_20260928.py` — new snapshot/refresh
  builder and wrestler/team identity linker.
- `scripts/schema.py` — registers the new tables and exact field order.
- `scripts/validate_integrity.py` — validates unique IDs, record types and all
  promotion/championship/wrestler/source references.
- `scripts/build_dashboard_data.py` — adds the complete championship browser
  feed and wrestler summary.
- `dashboard/data.json` — rebuilt from the merged database.
- `README.md`, `DEFINITIONS.md`, `BUILD_INSTRUCTIONS.md` — document the data
  model, separation from event-time fields and reproducible refresh workflow.

No existing raw Rumble fact, flag or source row was overwritten.

## Verification

- Complete validator before changes: 0 errors.
- Complete validator after changes: 0 errors.
- Every championship has at least one dated lineage row.
- All adjacent lineage dates reconcile: each row's `lost_date` equals the
  following record's `won_date`.
- Retired championships have no current reign.
- Active titles either have exactly one current reign or end in an explicit
  vacancy/lineage event.
- All 8,568 records appear in `dashboard/data.json`.
- Two consecutive offline snapshot builds plus dashboard rebuilds were
  byte-identical: idempotency passed.
