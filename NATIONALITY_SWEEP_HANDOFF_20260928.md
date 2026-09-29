# Complete nationality sweep — 2026-09-28

## Outcome

Nationality coverage is now **530 of 530 wrestlers (100%)**. The pass filled the 326 blanks remaining after the initial nine-row profile cohort; measured against the supplied baseline, the combined work filled all 335 original blanks.

No nationality was assigned from appearance, name, or birthplace alone. Evidence came from wrestler biography/profile descriptions, principally Wikipedia and TheSmackDownHotel. The research manifest preserves the exact matched URLs, source observations, agreement state, and exception notes.

## Research method

1. Loaded all 2,347 wrestler-profile URLs from TheSmackDownHotel's published sitemap.
2. Matched database identities using wrestler IDs, ring names, real names, and combined-name profile slugs.
3. Queried or opened Wikipedia biography pages for independent nationality descriptors.
4. Captured all nationality badges on multi-national TheSmackDownHotel profiles rather than silently keeping only the first.
5. Manually reviewed 54 alias, gimmick, short-name, and nationality-versus-heritage exceptions.
6. Corrected the two automated-matching hazards found during audit:
   - `hakushi` had initially matched Haku's profile through a short substring; corrected to Jinsei Shinzaki/Hakushi and `Japanese`.
   - `cesaro` produced a misleading Wikipedia parser result; manually checked and recorded as `Swiss`.
7. Kept ancestry and billed nationality separate from nationality where the source presentation mixed them. For example, Jinder Mahal and Tiger Ali Singh remain `Canadian`; ethnicity/heritage belongs in the separate field.

## Files changed

- `data/wrestlers.csv`: all 326 remaining nationality blanks populated and source IDs extended where required.
- `data/derived/*.csv`: regenerated from the completed master data.
- `dashboard/data.json`: regenerated.
- `scripts/research_nationality_sweep_20260928.py`: initial full profile-site/Wikipedia research manifest builder.
- `scripts/enrich_nationality_manifest_wikipedia_20260928.py`: rate-limited Wikipedia API research helper.
- `scripts/enrich_nationality_manifest_wikipedia_direct_20260928.py`: direct-page fallback.
- `scripts/enrich_nationality_manifest_sdh_aliases_20260928.py`: combined-name profile resolver.
- `scripts/audit_nationality_dual_badges_20260928.py`: multi-nationality badge audit and Hakushi URL correction.
- `scripts/apply_nationality_sweep_20260928.py`: guarded application script; refuses a drifted baseline.
- `scripts/reapply_audited_nationality_sweep_20260928.py`: applies the semantic-review corrections.
- `research/nationality_sweep_20260928.csv`: row-level research manifest with matched URLs and review outcomes.

The earlier source-led profile cohort in this same package also contains the associated HOF/death completions documented in `BROAD_RESEARCH_HANDOFF_20260928.md`.

## Sources

The sweep reuses the project's registered source collections:

- S022 — Wikipedia wrestler biographies.
- S024 — TheSmackDownHotel Pro Wrestlers Database.

Exact per-wrestler URLs are retained in `research/nationality_sweep_20260928.csv`; sources already registered individually were reused rather than duplicated. S1842–S1846 are the five URL-specific profile sources added during the preceding nine-row cohort.

## Confidence and unresolved issues

- Two independent matching sources were treated as confirmed research evidence.
- A single explicit biography/profile statement was retained as probable research evidence rather than upgraded by assumption.
- Multi-national descriptions were preserved when the profile explicitly listed both and the semantic review supported that interpretation.
- The master schema has no `nationality_status` column. Therefore the row-level evidence state is retained in the research manifest rather than adding an unapproved schema column.
- **Remaining blank nationalities: 0.**
- **Remaining unresolved nationality conflicts: 0.**

## Flags

No new open flag was required. The apparent Cesaro conflict was a parser error, not a genuine source disagreement, and the Hakushi/Haku issue was a URL-matching error corrected before handoff.

## Validation

- Baseline before this work: `ALL CHECKS PASSED` (0 errors).
- Immediately after applying all 326 rows: `ALL CHECKS PASSED` (0 errors).
- After the multi-nationality and alias semantic audit: `ALL CHECKS PASSED` (0 errors).
- After rebuilding all derived tables and dashboard data: `ALL CHECKS PASSED` (0 errors).
