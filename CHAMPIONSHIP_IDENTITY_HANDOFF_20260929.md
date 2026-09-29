# Championship history and performer-identity reconciliation

## Outcome

This pass rebuilt the championship layer around performer identity rather than a single WWE gimmick. Historical reign rows retain their original champion names, while the dashboard now aggregates title summaries across sourced same-performer wrestler IDs.

- Promotions: 16 -> 19
- Championships: 234 -> 256
- Reign rows: 7,589 -> 9,298
- Reign rows linked to Royal Rumble wrestler IDs: 2,411 -> 2,698
- Distinct Royal Rumble wrestler IDs with a linked reign: 360 at the original audit baseline -> 415
- Distinct performer groups after conservative real-name/DOB grouping: 464
- Performer groups with no linked reign in the 19-promotion scope: 58
- Validator: 0 errors before; 0 errors after

The residual 58 are preserved in `research/championship_identity_audit_20260929/rumble_performers_without_linked_reigns.csv`. This is not a claim that all 58 never held any title anywhere: the queue includes genuine non-champions/celebrities and people whose only documented championships are in regional or independent promotions outside the present 19-promotion layer.

## Important corrections

- Replaced unsafe substring identity matching with exact full-name and exact team-member matching. This prevents false links such as Austin Aries -> Steve Austin, Taylor Wilde -> Red Rooster, Taya Valkyrie -> Lyra Valkyria, Johnny Valentine -> Emma, Davey Boy Smith Jr. -> British Bulldog, and Tama Tonga -> Tama.
- Split the WWF Light Heavyweight lineage into the UWA/MPW/NJPW-recognized history and the WWF-recognized 1997-2001 history. The earlier build had silently omitted the WWF table, including Gillberg.
- Kept short/reused identities scoped to the relevant title. Examples: TNA's Jade -> Mia Yim; WCW's Gerald/Patrick -> the Harris brothers; OVW's Nova -> Simon Dean. Mexican Super Nova is deliberately not linked to Simon Dean.
- Dashboard title summaries now propagate across sourced same-performer sibling IDs, while reign rows preserve the name used when the title was held.

## New promotion rows

- `wwc` - World Wrestling Council
- `ovw` - Ohio Valley Wrestling
- `fcw` - Florida Championship Wrestling

## New championship rows

- WWE: World Tag Team Championship (1971-2010); WWF Women's Tag Team Championship; NXT Women's North American; NXT Women's Tag Team; NXT Heritage Cup; WWF-recognized Light Heavyweight Championship (1997-2001).
- CMLL: World Heavyweight, World Middleweight, World Welterweight, World Tag Team, and World Trios.
- WWC: Universal Heavyweight, Puerto Rico, World Tag Team, and Caribbean Heavyweight.
- OVW: Heavyweight, Tag Team, Women's, and Television.
- FCW: Florida Heavyweight, Florida Tag Team, and Divas.

The existing `wwf-light-heavyweight` row was renamed to make its UWA/MPW/NJPW recognition scope explicit and linked to the new WWF-recognized successor row.

## Wrestler rows changed

Thirty-six existing rows received sourced aliases and, where needed, canonical real names so the same performer can be recognized across gimmicks and promotions:

`adam-bomb`, `adam-rose`, `aldo-montoya`, `bastion-booger`, `big-cass`, `bill-demott`, `brodus-clay`, `chris-masters`, `eight-ball`, `eli-blu`, `elijah-burke`, `fake-razor-ramon`, `flash-funk`, `golga`, `hakushi`, `headhunter-1`, `headhunter-2`, `headshrinker-sione`, `irwin-r-schyster`, `jacob-blu`, `kama`, `kenny-dykstra`, `kharma`, `kwang`, `max-moon`, `papa-shango`, `saba-simba`, `savio-vega`, `sid-justice`, `simon-dean`, `skinner`, `skull`, `the-berzerker`, `the-godfather`, `tom-prichard`, `tugboat`.

Examples include X-Pac/Syxx/Syxx-Pac, Adam Bomb/Wrath/Bryan Clark, Aldo Montoya/Justin Credible, Kharma/Awesome Kong, Brodus Clay/Tyrus, Big Cass/Big Bill, Flash Funk/2 Cold Scorpio, Golga/Earthquake, Saba Simba/Tony Atlas, Max Moon/Paul Diamond/Kato, and the Harris brothers' Blu/DOA/Creative Control names.

## New sources

Added `S2127` through `S2150`. They comprise 22 structured championship-history pages plus the Bryan Clark, Steve Keirn, and Paul Diamond identity pages. Full URLs and source notes are in `data/sources.csv`; every new reign remains `PROBABLE` because it currently has one structured observation source.

## Scripts

- `scripts/build_championship_history_20260928.py`: adds the new lineages/promotions, safe identity matching, scoped aliases, selective `--refresh-missing`, and support for multiple recognition tables on one source page.
- `scripts/build_dashboard_data.py`: aggregates championship summaries across sourced same-performer IDs using unique reign IDs.
- `scripts/audit_championship_identities_20260929.py`: produces deterministic duplicate, ambiguity, unlinked-name, nonentrant-link, wrestler-gap, and performer-gap queues.
- `scripts/apply_wrestler_identity_enrichment_20260929.py`: idempotently applies the 36 sourced identity updates.
- `scripts/apply_championship_identity_sources_20260929.py`: idempotently registers new identity sources.
- `scripts/research_wrestler_aliases_20260929.py`: preserves the attempted broad Wikipedia snapshot research. The endpoint rate-limited the sweep, so its partial output is research evidence only and is not used as source data.

## Generated files

Rebuilt `data/promotions.csv`, `data/championships.csv`, `data/championship_reigns.csv`, `data/sources.csv`, `data/wrestlers.csv`, the derived layer, and `dashboard/data.json`. The dated structured-source snapshot was extended in `research/championship_history_snapshot_20260928.json`.

No flag row was changed or added: the pass found identity/linkage design issues and missing lineage coverage, all resolved through sourced rows and scripts rather than unresolved factual conflicts.

## Verification

- `scripts/build_championship_history_20260928.py`: clean.
- `scripts/build_derived.py`: clean; 491 career rows, 70 entry-number rows, 90 current records, 1,485 rivalry rows, 48 event-dynamic rows.
- `scripts/build_dashboard_data.py`: clean; 39 men's events / 404 wrestlers and 9 women's events / 87 wrestlers.
- `scripts/validate_integrity.py data`: `ALL CHECKS PASSED (the whole database).`
- Idempotency: identity-source apply, wrestler-identity apply, championship build, derived build, and dashboard build reran with byte-identical outputs for the championship CSVs, wrestler/source registries, source snapshot, and dashboard data.

## Recommended next step

Merge and independently verify this phase before broadening the promotion universe further. The next championship phase should be entrant-driven: work through the 58-row performer queue and add a promotion only where a documented entrant reign justifies it (likely Stampede, USWA/CWA, SMW, FMW, or selected independents), instead of indiscriminately importing every title ever created.
