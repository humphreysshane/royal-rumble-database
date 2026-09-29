# Collection of Stats: source material and claim catalog

This document archives the "Royal Rumble Collection of Stats" section of Shane's original
`Main_Rumble_Stats_New.docx`, plus the adjoining "2016 Rumble Stats" Paddy Power prediction
blog, and records what this database's cross-check pass (2026-09-17, `scripts/
factcheck_collection_of_stats.py`) found for each checkable claim. It exists so that the
reasoning behind every flag/record change from that pass can be traced back to its source
without re-opening the original Word document.

The document's later "WCW World War 3" headings (1995, 1996, 1997, 1998) were also checked
during this pass and contain **no body content at all** -- four empty Heading-1 paragraphs
with nothing underneath. There is nothing there to build, catalog, or cross-check, and WCW's
World War 3 is a different promotion's own battle-royal-style event, not a WWE Royal Rumble,
so it sits outside this database's stated scope in any case. Noted here for completeness.

## Sources quoted in this section

| Source | This database's ID | Notes |
|---|---|---|
| Sky Sports, "WWE Royal Rumble: Stats on most wins, eliminations and more" | S115 | Short records list |
| WrestlingInc, "WWE Royal Rumble Interesting Facts And Stats" | S103 (already existed) | Long trivia bullet list |
| Cult of Whatever, "WWE Royal Rumble Match Statistics" | S116 | 1988-2012 retrospective + records |
| PodSwoggle, "Wrestling's Most Important Facts: Royal Rumble Edition!" | S117 | Informal unique-facts list |
| SE Scoops, "Looking At A Ton Of Royal Rumble Statistics & Records" | S102 (already existed) | Records list + winner/entry-number table |
| Paddy Power blog (Josh Powell), "Rumble Prediction 2016" | S108 (already existed) | Height/weight/age/experience trend-band prediction, archival only (see below) |

## Claims checked and outcome

Status legend: **CONFIRMED** = matches this database's own computed value exactly.
**UPDATED** = this database's own data changed as a direct result of checking this claim.
**CONFLICT (preserved)** = a genuine disagreement exists and is flagged, not resolved.
**MORE CURRENT** = this database's value is correct and simply more up to date than the
trivia source (which predates later Rumbles this database has since added).
**ARCHIVAL ONLY** = not converted into a tracked stat; reasoning given.

- Most eliminations in a single Rumble ever (Roman Reigns, 12, 2014, breaking Kane's 11 from
  2001) -- **CONFIRMED**, matches R009 exactly.
- Number 27 has produced the most Royal Rumble winners (4: Big John Studd, Yokozuna, Bret
  Hart, Steve Austin) -- **CONFIRMED** against `entry_number_stats.csv`.
- Number 1 and Number 2 have each produced 2 winners -- **CONFIRMED**.
- Number 30 has produced 2 winners (Undertaker 2007, Cena 2008), per SE Scoops (written
  "before 2011") -- **MORE CURRENT**: this database now correctly shows 3 (Triple H's 2016
  win from #30 postdates every source in this section).
- The Godfather's 5-gimmick chain (Papa Shango 1993 -> Kama 1996 -> Kama Mustafa 1998 ->
  Goodfather/Godfather 1999-2002 -> The Godfather 2013), 20 years apart -- **CONFIRMED**
  against `entrants.csv`'s `ring_name_at_time` field for all 5 gimmick names.
- Viscera needed 8 wrestlers to eliminate him in 2007 (his own record, breaking his 7-man
  1994-as-Mabel toss) -- **CONFIRMED** exactly (8 named contributors) and promoted into a new
  tracked record, R016.
- The Great Khali's 7 consecutive eliminations in 2007 -- **CONFIRMED** via `order_in_match`
  sequencing (positions 18-24, all solo, no interruption) and promoted into a new tracked
  record, R017 (tied with Hulk Hogan's 1989 7-streak, which no source in this section
  mentions).
- Diesel's (1994) and Rikishi's (2000) matching 7-consecutive-elimination claims --
  **CONFLICT (preserved)**: both years' `eliminations.csv` rows carry zero `order_in_match`
  data, so true consecutiveness can't be computed; what little positional information exists
  for 1994 suggests Diesel's 7 were in fact interrupted. Both wrestlers' raw 7-elimination
  TOTALS for that match are independently confirmed; only the "consecutive" framing is in
  question.
- Chyna eliminated Mark Henry (1999) and Chris Jericho (2000); Beth Phoenix eliminated The
  Great Khali (2010); Kharma eliminated Hunico (2012) -- **CONFIRMED** against
  `eliminations.csv` (though the redundant `wrestlers_eliminated_ids` convenience field on
  their own entrant rows was stale/blank until this pass's systemic resync -- see below).
- Bob Backlund's ~61-minute run in 1993 ("over an hour") -- **CONFIRMED** (61:16).
- Entry #4 producing the fewest total eliminations (PodSwoggle's "10", from a smaller sample
  as of ~2012) -- **directionally consistent**, not independently re-verified figure-for-
  figure given the sample-size difference between then and now (29 years of data today).
- Rey Mysterio's longest single-match survival time -- **CONFLICT (preserved)**: Sky
  Sports/SE Scoops say 62:12, Cult of Whatever says 62:16 (in the same article), this
  database's own figure (from Shane's original document) is 62:14. All three external figures
  disagree with each other AND with this database; the documentary-source-first convention is
  applied and this database's 62:14 is kept as the primary value.
- "Shortest time in the Rumble" -- Santino Marella, eliminated by Kane in 2009, cited as 1.9s
  (Sky Sports) or 1.7s (SE Scoops) -- **UPDATED**: this database's own pre-existing record
  (R008) incorrectly credited Randy Savage's 1991 no-show (he drew a number but never entered
  the match) with "00:00", conflating a no-show with a genuine appearance. Corrected to
  Santino Marella's real recorded ring time of 0:02, which is what this record type is
  actually meant to capture.
- Career elimination totals (Kane 43, Shawn Michaels 39, Steve Austin 36, Undertaker 35, per
  Sky Sports/WrestlingInc/Cult of Whatever/PodSwoggle/SE Scoops) -- **CONFLICT (preserved)**:
  this database's own totals (Kane 40 -- corrected down from 41 by this same pass, see below
  -- Michaels 29, Austin 28, Undertaker 22) are well below every external figure. Not a
  solo-vs-shared-credit difference (verified). This document's own WrestlingInc excerpt
  admits "WWE's official website lists several different numbers for both competitors" --
  i.e. even WWE's own promotional totals for this exact comparison are inconsistent. Left
  open rather than adjusted to match an unreproducible aggregate claim.
- Eliminators needed to remove Earthquake (1990) and Muhammad Hassan (2005) -- WrestlingInc/
  Cult of Whatever both say 6 for each -- **CONFLICT (preserved)**: this database records 5
  contributors for Earthquake and 8 for Hassan. The Hassan case connects to this project's
  already-known "2005 Muhammad Hassan contradiction" open item.
- Self-eliminations (Cult of Whatever/WrestlingInc's list of 9: Andre 1989, [Savage 1992 --
  see below], Ahmed Johnson 1997, Mil Mascaras 1997, Faarooq 1997, Drew Carey 2001, Kane 1999,
  Mick Foley 2004, MVP 2010) -- **UPDATED** in two ways: (1) Kane's 1999 self-elimination was
  already in this database's data but its `is_self_elimination` flag was bugged to FALSE --
  fixed. (2) Ahmed Johnson and Faarooq had no `eliminations.csv` row at all for 1997 --
  added, CONFIRMED by 2 independent sources. Randy Savage's 1992 case is correctly NOT
  modeled as a self-elimination in this database -- even Cult of Whatever's own account says
  he only "technically" did it but continued in the match until eliminated later by Flair/Sid
  Justice, i.e. not a genuine self-elimination by this database's own definition. This
  database's resulting list also includes Big Bossman (1992) and Hornswoggle (2008), which
  this trivia section's list of 9 omits -- not treated as an error on either side.
- Mabel's 1994 group elimination -- WrestlingInc/Cult of Whatever both cite a 7-man group,
  matching this database's own (previously unconfirmed) claim that it was a group elimination
  -- **partial corroboration**: F092 stays open (specific names still unknown) but now carries
  independent confirmation of the group's size.
- Height/weight/age/experience trend bands predicting a 2016 "model winner" (Paddy Power) --
  **ARCHIVAL ONLY**. Not converted into a new records.csv category: the bin boundaries are the
  original author's own editorial choices from a point-in-time prediction piece (the predicted
  winner, Sheamus, did not win -- Triple H did), not a standard this database can reproduce
  without making the same arbitrary judgment calls itself.

## Systemic data-integrity issue surfaced by this pass

While cross-checking the rivalry/most-eliminated-type claims above against `career_stats.csv`,
this pass found that `entrants.csv`'s own `wrestlers_eliminated_ids` field (a denormalized
convenience copy of `eliminations.csv`'s data) had never been kept in sync for a large number
of rows across many years -- 264 of 872 entrant rows were stale or blank. This was fixed by
recomputing it directly from `eliminations.csv` for every row. Verifying that recomputation
against the existing `wrestlers_eliminated_count` numeric field also surfaced 10 rows where
that count itself was stale (most from a fact-check pass adding new `eliminations.csv` credits
without re-running the per-wrestler recount afterward; 2 -- Andre the Giant 1989 and Drew
Carey 2001 -- from a self-elimination being miscounted as "eliminating 1 person: themselves").
All 10 were corrected; see flag F317 for the full list and reasoning. See the main README for
the headline effect (Kane's tracked career-elimination total moves from 41 to 40).
