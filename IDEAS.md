# Stat ideas — the "haven't thought of it yet" list

A running brainstorm, not a to-do list to clear in one go. Add to this as
ideas come up; move an idea into the schema/derived layer once it's worth
building. Grouped by what it takes to actually compute it.

## Buildable now, just need more events (2+ Rumbles) to be meaningful
- Bounce-back factor: eliminated early one year, deep run or win the very
  next year (needs `career_stats.csv` joined across consecutive years)
- Entry-number "value": win rate / avg survival / final-four rate by entry
  number, already tracked in `entry_number_stats.csv` — gets interesting
  once there's a real sample per number
- #1 vs #2 combined performance, first-5 vs middle vs last-5 entrants
  (slice of `entry_number_stats.csv`)
- Most consecutive Rumbles entered at the exact same entry number
- Longest iron-man streak: most consecutive Rumbles where a wrestler had
  the single longest ring time in the match
- "Grand slam" wrestlers: won it, also holds/held a single-Rumble
  elimination record, also has multiple final-four runs — a composite
  achievement list rather than one number
- Family dynasties: total combined Rumble eliminations/appearances/wins by
  surname or tracked family group (needs a `families.csv` linking
  wrestler_ids — not built yet, flagged below)
- Most different tag-team partners entered the Rumble with over a career
- Which former partners later eliminated each other

## Buildable now, need a small new table
- **Championship history** (`championships.csv` — title, holder(s), reign
  start/end dates): unlocks "future world champions in the field",
  "days into title reign at time of entry" properly instead of leaving it
  UNKNOWN, and "who won the world title the same night as their Rumble run"
- **Family relationships** (`families.csv` — wrestler_id, family_group,
  relationship): unlocks the "first family member to also enter" idea from
  your original Excel, plus dynasty-level aggregates
- **Rumble reward/stipulation history** (what winning actually granted —
  this changed over the years: no guaranteed title shot in 1988, a
  WrestleMania main event title shot became standard later): a small
  per-year reference table rather than free text in `events.csv`

## Needs video/footage review (schema already stubbed, unpopulated)
- Entrance length, crowd reaction proxies, near-eliminations, elimination
  side-of-ring — see `entrances.csv`, `near_eliminations.csv`,
  `eliminations.csv:location_side`
- Move-by-move logs (`moves.csv`)
- Commentary claims vs. actual database (section 29 of your spec) — would
  need transcripts; possible without full video if transcripts/closed
  captions are sourceable, worth a future look

## Field-composition stats worth adding to `event_dynamic_stats.csv`
Already built: HOF members (at-time vs. eventual), now-deceased count,
combined billed weight of the field, combined age of the final four.
Good next additions:
- Number of debuting/returning wrestlers per event (needs those flags
  reliably filled in per entrant — currently UNKNOWN for 1988, another
  research task)
- Number of "hidden"/uncredited entrants — surprise appearances that
  weren't on the poster
- Nationality/billed-country breakdown per event
- Number of women's-division wrestlers appearing in men's-division shows
  or vice versa (relevant once Women's Rumble data is loaded)

## Content-discovery angle (your spec section 39)
Once 3-4 more events are loaded, worth a pass generating a short list of
"interesting findings" per new event the way a stats site would: unusual
records, closest calls, biggest surprises relative to career pattern. This
is easy to automate once `career_stats.csv` has real multi-year history to
compare a new event against — not worth doing yet against 1 data point.

## Shane's 2026-09-18 "exhaustive stats" brief — new buckets to build out
Triggered after Shane spotted the Hogan/2013 gaps on a glancing check and asked for a full
event-by-event fact-check sweep PLUS an exhaustive "weird and wonderful" stats catalog,
capturing anything and everything — nothing off limits. Decided (his answers): fact-check and
new-stats capture happen together, event by event; work proceeds in batches with a check-in
after each; don't pre-review the stat-idea list with him first, just start capturing whatever is
findable from text/existing sources.

- **Weapons used in a Rumble match**: needs a new table (`weapons_incidents.csv` — event_id,
  wrestler_id who used it, target wrestler_id if any, weapon, whether it caused/assisted an
  elimination, description, data_quality_status, source_ids). Not yet built — no weapon use
  confirmed for 1988 yet, but this era leans "clean" (pre-Attitude Era chair-shot chaos), so this
  category will likely get much more interesting from the mid/late 90s onward. Once populated
  across enough events, unlocks "most weapons used in a single Rumble", "most frequently used
  weapon", "first weapon ever used in a Rumble", etc.
- **Brand/promotion affiliation** ("what brand did they appear from", "were they from a
  different company"): needs a new `entrants.csv` field (e.g. `promotion_at_event`). Not worth
  populating for 1988-2001 (pre-brand-split, everyone's just "WWF") — becomes meaningful from the
  2002 brand extension onward, and for any surprise/crossover entrants from outside companies
  (WCW/ECW invasion-era call-ups, indie/NXT debuts, etc.). Flagged here so it gets built when the
  sweep reaches the relevant years rather than sitting half-empty from year one.
- **A general "notable moments" table** for weird trivia that doesn't reduce to a single
  leaderboard number (botches, in-ring injuries, unusual entrances, TV-rating/attendance
  records, storyline-driven weirdness like Bo Dallas's payback elimination in 2013) — needs a
  new `notable_moments.csv` (event_id, wrestler_id(s) involved, category, description,
  source_ids, data_quality_status). Not yet built.

### What the 1988 pilot pass taught about HOW to do this safely
Spent real effort fact-checking just RR1988M as a worked example before committing to a pace for
all 29 events. Findings, for future passes:
- This database's earlier build/fact-check passes were already quite rigorous (2-source
  CONFIRMED bar, disputes preserved as flags rather than force-resolved — see F006/F007). Don't
  expect every event to have Hogan/2013-level gaps; 1988 turned up exactly ONE new finding
  (Ultimate Warrior's eliminator disputed between the structured record and Scott Keith's
  narrative recap — see F337) after real effort, not a pile of errors.
- **AI-summarized web-fetches of long ordered elimination tables are NOT reliable enough to
  re-derive an event's order from scratch** — this exact problem is already documented in S026's
  own source notes (scrambled/reordered 1988's and 1992's tables) and was reproduced again this
  pass (a fresh Wikipedia fetch and a wrestlingrecaps.com fetch each returned internally
  plausible but mutually contradictory "elimination order" sequences for 1988). The safe pattern
  going forward: treat this database's own existing elim_number/entry_number ordering as the
  baseline (it's usually independently well-sourced already), and use fresh fetches only to
  check specific ELIMINATOR-CREDIT pairs against it — flag genuine disagreements, don't trust a
  freshly-fetched table's row order over the database's own.
- **Check whether a "second source" is actually independent before trusting it as one.**
  wrestlingrecaps.com's 1988 recap turned out to be the same underlying Scott Keith review
  already registered as S010 (Kayfabe Memories' mirror of it) — worth 1 source, not 2, despite
  living at a different URL.
- Realistic pace: a genuinely rigorous pass (multi-source eliminator spot-checks + a trivia/
  weapons/notable-moments search) took meaningful research effort for ONE event. 29 events at
  this depth is a multi-session project, not a single sweep — batches should probably be sized
  by effort, not a fixed event count, and it's worth flagging to Shane if a "batch" ends up being
  smaller than expected because an event needed more digging than usual (or larger, if an event
  is quiet).

### 1989-1992 batch findings (2026-09-18)
- **The deceased_date field is likely incomplete database-wide, not just for Hogan.** Auditing
  only the ~30 entrants each of RR1989M-RR1992M turned up 12 more wrestlers who are confirmed
  deceased but had a blank deceased_date (Roddy Piper, Dusty Rhodes, Jimmy Snuka, Earthquake,
  Texas Tornado, British Bulldog, Hawk, Animal, Demolition Crush, Jim Neidhart, Bushwhacker
  Butch, Col. Mustafa/The Iron Sheik — see flags F339-F341). That's a high hit rate for a random
  4-event slice, which strongly suggests the same gap exists across the other 25 events. Worth a
  dedicated database-wide audit rather than only catching these incidentally as each event gets
  swept — flagged to Shane as F340 (open).
- **Stale flags are a recurring bug pattern, separate from data errors.** Found 3 cases this batch
  (F009, F048, and F031) where wrestlers.csv already held the correct, resolved value from an
  earlier pass, but flags.csv still listed the issue as "open" and the row's own notes text hadn't
  been updated either — in Col. Mustafa's case badly enough that a later pass (the HOF field
  cleanup) had no way to know his real identity was already on file. Worth keeping an eye out for
  more of these — a flag or notes field can go stale even when the underlying data got fixed.
- **Weird & wonderful trivia found for 1991/1992, not yet added to the database** (no
  notable_moments.csv exists yet — see the bucket above): Rick Martel's 52:30 was the first-ever
  50+ minute Rumble survival; Andre the Giant was advertised for RR1991M but withdrew ~3 weeks out
  over health; Brian Knobbs entered RR1991M as a late substitute for Honky Tonk Man (who'd quit
  the company weeks earlier), then missed RR1992M himself after being stabbed in a road-rage
  incident, with Bret Hart (kayfabe 104° fever) and Marty Jannetty (written out post-Superkick
  angle) also absent that year and replaced by Haku/Nikolai Volkoff; and WWE reportedly re-recorded
  RR1992M's commentary track after the fact to make Sid Justice's elimination of Hulk Hogan sound
  more like a cheap shot than the crowd's actual (more positive) live reaction. All single-sourced
  (cultaholic/whatculture) this pass — worth a second source before writing into the database
  proper, and worth Shane's steer on whether it's time to build notable_moments.csv now that
  there's real content for it.

### 1993-1996 batch findings (2026-09-18)
- Same deceased-status audit as the 1989-1992 batch, same hit rate: 6 more confirmed-deceased
  wrestlers found with a blank deceased_date (Bam Bam Bigelow, King Kong Bundy, Dick Murdoch, Owen
  Hart, Vader, Jimmy Del Ray) plus Yokozuna's missing 2012 Hall of Fame year — see flag F344. Further
  confirms the database-wide audit suggested in F340 is worth doing rather than deferring.
- Near-miss worth flagging as a lesson: almost mapped Matt Borne's 2013 death onto this database's
  "doink"/"doink-1995" wrestler_ids before checking — those ids are actually a different performer
  (Ray Apollo/Ray Licameli) per this database's own existing F095/F096. Caught it by re-reading the
  existing flags before writing, not by instinct. Worth remembering: a famous name attached to a
  gimmick (Doink, Kane, Sin Cara, etc.) is not automatically the wrestler_id representing THIS
  database's specific performer for THIS specific year — always check aliases/notes/existing flags
  first, the same discipline that caught the big-bossman/big-boss-man bug in the previous batch.
- notable_moments.csv now has 7 rows total (RR1991M x3, RR1992M x2, RR1993M x1, RR1996M x1) — still
  nothing for 1988-1990 or 1994-1995 at this research depth. Not a gap to force-fill; just means
  those events were quieter (or need a different kind of source) at the level searched so far.

### 1997-2000 batch findings (2026-09-18/19)
- Before assuming RR1998M's near-total blank elim_number field was a bug (it looked alarming in a
  first data dump — almost the entire field missing that one derived value), checked its existing
  flags.csv entries first rather than diving into research. F112 already explains it: like 1994/1996,
  1998 has no Cageside-style timing-analysis source, so elim_number (which requires that specific kind
  of source to derive, per F080's methodology) is correctly left blank for the whole event — not a gap
  to chase. The two rows that looked like unrecorded gaps (Hunter Hearst Helmsley, Skull) were likewise
  both already-documented, correct special cases (F113, F141), not bugs. Worth remembering: check
  flags.csv before assuming a data hole is new, the same discipline as the stale-flag lesson from
  batch 1, just pointed the other direction (an apparent gap that's actually already explained, not an
  already-fixed flag that looks open).
- Deceased-status audit continues to be the highest hit-rate finding every single batch: 4 more
  confirmed-deceased wrestlers with a blank deceased_date this batch (Chyna, Terry Funk, Brian
  Christopher/Grandmaster Sexay, Darren "Droz" Drozdov) — see F346. Now 4 batches in a row with a
  non-trivial hit count; F340's suggestion of a dedicated database-wide audit (still open, still
  unanswered by Shane) looks more justified with each pass.
- A genuine near-miss caught by searching instead of assuming: Droz is widely remembered as "the guy
  paralyzed in a real 1999 in-ring accident" and, going in, it would have been easy to assume he was
  still alive on that basis. He actually died in 2023 (WWE.com's own tribute article, corroborated
  independently) — checked via search rather than relying on that general knowledge, which turned out
  to be outdated. A mirror-image lesson to the Matt Borne/Doink near-miss from batch 2: that one was
  "don't assume a death applies to someone who's actually alive/different," this one is "don't assume
  someone's still alive because of what's commonly remembered about them."
- Also completed 2 bio gaps using this database's OWN already-sourced sibling data rather than new
  assumptions: golga's dob/deceased_date/birthplace (already independently identified elsewhere in
  this database as the same real person as the "earthquake" id, John Tenta) and big-boss-man's
  real_name/dob/deceased_date (the database's own F338 already states in its own text that this id is
  "Ray Traylor's 1999-era Corporation Big Boss Man," the same real person as the separately-tracked
  "big-bossman" id). Also found and added Ray Traylor's 2016 WWE Hall of Fame induction to BOTH ids.
  Not a wrestler_id merge — the two Big Boss Man eras stay as separate rows per this database's
  gimmick-era convention — just completing real-person facts each row was independently missing,
  using sourcing the database already trusted elsewhere.
- Also checked and explicitly ruled OUT a false alarm: a search for "Jerry Lawler death" surfaced an
  unrelated same-name obituary ("Jerome Charles Lawler, 1938-2026"). Checked directly against
  Wikipedia rather than trusting the search snippet — the real Jerry Lawler (wrestler/commentator, b.
  1949) is a different person and confirmed alive. Worth remembering as the inverse of the Droz
  lesson: a scary-looking search result for a common name needs the same skepticism as an assumption.
- notable_moments.csv now has 11 rows total, adding RR1997M x2 (surfacing this database's own already-
  documented F081 Bret Hart/Austin missed-call finish, and F082 Mil Mascaras' self-elimination dive —
  no new research needed, same "surface existing content" pattern as batch 2's Giant Gonzalez row),
  RR1999M x1 (Vince McMahon's win and title-shot forfeiture, newly researched), and RR2000M x1 (The
  Rock/Big Show botched-finish controversy, newly researched). 1988-1990 and 1994-1995 remain the only
  gaps in notable_moments.csv coverage so far.

### Wrestler-profile dedup & gimmick cross-linking (2026-09-19)
- Shane's request: sweep for accidental duplicate wrestler entries (his example: Big Boss Man showing
  as two separate records), and make same-performer gimmick relationships easy to find (his examples:
  Glenn Jacobs/Kane was previously Isaac Yankem DDS; John Tenta appeared as both Earthquake and Golga).
- Ran a full data-quality sweep first, since "is this a bug" had to be answered before building
  anything: no exact or normalized ring-name collisions beyond the already-known Big Boss Man split, no
  duplicate wrestler_id rows in wrestlers.csv (371 rows, 371 unique ids), no within-group year overlaps
  among any same-performer group (i.e. nobody's "two eras" actually double-count a single real
  appearance). Conclusion: there is no accidental-duplication bug. What Shane is seeing is this
  database's own deliberate convention — each gimmick era gets its own wrestler_id, matching WWE's own
  official-record treatment (Mick Foley's 3-gimmicks-in-one-night, F111, is the clearest reason merging
  outright isn't safe) — just not yet cross-linked anywhere in the dashboard, so it *reads* like
  duplication even though the underlying data is correct.
- Built automatic same-performer matching into `build_dashboard_data.py` rather than hand-maintaining a
  list: (1) exact match on normalized real_name (generational suffixes like Jr./Sr. deliberately kept,
  so Ted DiBiase and Ted DiBiase Jr. — father and son, different DOBs — are never conflated), with any
  DOB conflict across the group killing the match; (2) a second, stricter fuzzy pass for names that
  aren't identical strings but are obviously the same person in fuller/shorter form (e.g. golga's "John
  Tenta" vs earthquake's "John Anthony Tenta Jr.") — this path requires BOTH DOBs present and exactly
  equal (not just non-conflicting), plus matching first and last name tokens, plus one name's token set
  being a subset of the other's. Union-find merges the two passes so a 3-way group where only some pairs
  match exactly still ends up fully linked.
- Result: 10 same-performer groups, cross-linked with a new "Same performer, other gimmicks" panel on
  each wrestler's profile page (with combined career totals across all their gimmick eras) and a small
  "also N gimmicks" badge (hover for the names) next to their name on the Wrestlers index and the
  all-time stat sheet:
  - Glenn Thomas Jacobs: isaac-yankem, fake-diesel, kane (Shane's own example)
  - John Tenta: earthquake, golga (Shane's own example — this pair needed the fuzzy-match pass; the
    exact-match pass alone would have missed it)
  - Ray Washington Traylor Jr.: big-bossman, big-boss-man (Shane's own example)
  - Charles Thomas Wright: papa-shango, kama, the-godfather — a THIRD case the fuzzy-match pass caught
    that wasn't on anyone's list going in (the-godfather's real_name field is the shorter "Charles
    Wright," which the exact-string pass alone would have missed, same shape as the Tenta case)
  - Michael Francis Foley: mankind, cactus-jack, dude-love, mick-foley
  - Solofa Fatu Jr.: fatu, the-sultan, rikishi
  - Brian Girard James: jesse-james, road-dogg
  - Ronnie Aaron Killings: k-kwik, r-truth
  - Joseph Michael Laurinaitis: animal, road-warrior-animal
  - Dustin Patrick Runnels: dustin-rhodes (0 Rumble appearances under that name), goldust
- Deliberately did NOT link doink / doink-1995, even though they're a well-known real-world case
  (Matt Borne's original Doink vs. later performers under the same gimmick). This database's own
  flags F095/F096 already treat it as a PROBABLE, not CONFIRMED, same-performer question — doink-1995
  has a blank real_name field precisely because sourcing hasn't cleared this database's own bar yet.
  The new matching logic correctly stays silent on it rather than asserting more confidence than the
  database itself has. This might be worth a specific look from Shane at some point (is there a source
  to confirm it either way?) but it's a sourcing question, not something to force through the profile
  feature.
- Deployed as dashboard Version 12 (data.json rebuilt from the live database; page.html gets the new
  panel + badges; validated with a Playwright headless smoke test across the Wrestlers index, all 10
  profile pages worth of same-performer groups, and the all-time stat sheet — no console errors, badge
  counts match the expected group-membership sum exactly (24), and a sibling with no profile page of
  its own, like dustin-rhodes, renders as plain non-clickable text rather than a broken link).

### 2001-2004 batch findings (2026-09-19)
Next batch in the established fact-check + new-stats sweep (1988 pilot → 1989-92 → 1993-96 →
1997-2000 → this one). Different starting point than earlier batches, though: RR2001M-RR2004M
already carried substantial flags (F130-F181, F201-F208) from this database's original build —
these 4 events were never a "cold start" the way 1988-2000 were. Many of those existing open flags
are genuine CONFLICTING_SOURCES disagreements (attendance figures, a couple of birthplace and
eliminator-credit disputes) that this pass deliberately left alone — per this project's core rule,
real disagreements between sources stay preserved as flags, not force-resolved by picking a side,
so "lots of open flags" here isn't itself a problem to fix.
- Deceased-status audit (still the highest hit-rate finding, 4 batches running now): jamal — Edward
  "Eddie" Fatu, who wrestled under that name at RR2003M before later becoming Umaga (this database's
  notes already record that identity merge from an earlier pass, F198) — confirmed deceased
  2009-12-04 (heart attack from acute toxicity of multiple substances), Wikipedia cross-checked
  against CNN's contemporary report. Also spot-checked 9 lower-profile names (Bull Buchanan, Haku,
  Perry Saturn, Steve Blackman, Spike Dudley, Hardcore Holly, Rene Dupree, Ernest "The Cat" Miller,
  Scott Steiner) — no deaths found, left unchanged.
- New audit type, not specifically targeted before: **WWE Hall of Fame induction year**. Found blank
  on several RR2001-2004 entrants who've since been inducted — Ron Simmons/Faarooq (2012), Booker T
  (2013), Mick Foley (2013), Eddie Guerrero (2006, posthumous), Kane (2021), Kurt Angle (2017),
  Diamond Dallas Page (2017), The Undertaker (2022, a rare solo induction), Rey Mysterio (2023).
  Reused this database's own existing reusable HOF-bucket sources (S123/S124) rather than
  registering new ones. Checked and confirmed NOT yet inducted: Edge. **Worth flagging to Shane**:
  this was found incidentally, not from a dedicated sweep — hall_of_fame_year is very plausibly
  incomplete across the WHOLE database (all 29 events), the same way deceased_date turned out to be.
  Given the deceased-status audit's track record, a dedicated database-wide Hall of Fame pass
  (alongside F340's still-open deceased-status one) seems like it would have a similarly good hit
  rate — flagging both here for Shane to weigh in on rather than assuming that's wanted.
- 7 new notable_moments.csv rows (NM012-NM018), all surfaced from this database's own already-
  CONFIRMED events.csv historical_significance text or resolved flags rather than freshly researched
  — same "surface existing content" pattern as batches 2-3: Drew Carey's celebrity cameo and Steve
  Austin's delayed/out-of-order entry (RR2001M); Maven's famous upset elimination of The Undertaker
  and Mr. Perfect's surprise swan-song return (RR2002M); Batista's chair-shot interference after his
  own elimination (RR2003M); Mick Foley's "Cactus Jack" reveal replacing the storyline-attacked Test,
  and the Foley/Orton simultaneous double-clothesline elimination (RR2004M).
- Deployed as dashboard Version 13 (rebuilt dashboard/data.json off the live database; page.html
  itself unchanged this batch; validated with a Playwright headless smoke test across all 4 event
  pages and all 10 touched wrestler profiles — no console errors, moment counts and HOF/deceased
  badges all rendering as expected).

### 2005-2008 batch findings (2026-09-20)
Next batch in the sweep (1988 pilot → 1989-92 → 1993-96 → 1997-2000 → 2001-04 → this one).
RR2005M-RR2008M already carried substantial flags (F182-F228, F249-F254, F321, F324) from the
original build, same situation as the last batch — several remain open as genuine, deliberately-
preserved CONFLICTING_SOURCES disagreements rather than bugs.
- Deceased-status audit: **no new deaths found this batch** — a real "checked and clear" result, not
  a skipped step. Individually spot-checked the lower-profile/higher-perceived-risk names (The Great
  Khali, The Sandman, Orlando Jordan, Muhammad Hassan, Trevor Murdoch, Kenzo Suzuki, Psicosis, Gene
  Snitsky, Luther Reigns, Mark Jindrak, Kevin Thorn, Simon Dean/Gotch, Sylvain Grenier, Daniel Puder)
  against Wikipedia and the mainstream-obituary bucket. Worth noting for calibration: after 5 batches
  covering 1988-2008 (roughly 250+ unique entrants), this is the first batch with zero hits — the
  earlier batches' hit rate wasn't a fluke, but it also isn't a guarantee every batch finds something.
- WWE Hall of Fame bio-completion (continuing batch 4's new audit type): Ric Flair (2008), The Great
  Khali (2021), Mark Henry (2018), Rob Van Dam (2021) — all previously blank, all confirmed via this
  database's existing HOF-bucket sources. That's 13 HOF completions across 2 batches now purely from
  incidental discovery while doing something else — reinforces the case (see 2001-2004's write-up)
  for a dedicated database-wide Hall of Fame pass.
- 7 new notable_moments.csv rows (NM019-NM025), again mostly surfaced from already-CONFIRMED content
  rather than freshly researched: Vince McMahon's real torn-quad injury and Kurt Angle's post-
  elimination attack on Shawn Michaels (RR2005M); Kane's then-record 8th consecutive appearance —
  deliberately logged as PROBABLE, not CONFIRMED, since it rests on one uncross-checked source, a good
  example of the site's quality-pill system doing its job on a genuinely interesting but thin claim
  (RR2006M); the widely-praised Undertaker/Michaels final segment and the first-all-3-brands milestone
  (RR2007M); John Cena's surprise-return win and Hornswoggle's ~26-minutes-under-the-ring oddity
  (RR2008M).
- Deployed as dashboard Version 14 (rebuilt dashboard/data.json off the live database; page.html
  unchanged this batch; validated with a Playwright headless smoke test across all 4 event pages and
  all 4 touched wrestler profiles, including confirming the PROBABLE quality pill renders correctly on
  the Kane moment — no console errors).

---

### 2009-2012 batch findings (2026-09-20)
Next batch in the sweep (1988 pilot → 1989-92 → 1993-96 → 1997-2000 → 2001-04 → 2005-08 → this one).
RR2009M-RR2012M already carried substantial flags (F229-F266) from the original build and earlier
passes, same situation as every prior batch — several remain open as genuine, deliberately-preserved
CONFLICTING_SOURCES disagreements rather than bugs. Winner/entrant-count/elimination-count/duration
for all 4 events were spot-checked and are already correctly CONFIRMED — no fix needed. Worth flagging
for awareness (not something this pass can close): RR2011M is the special 40-man anniversary Rumble
(historically accurate, not a data error), and RR2010M carries pre-existing flags (F244/F245) noting
Shane's own reference document has zero content for that year and no per-wrestler timing-graphic
source exists for it — a genuinely sparser-sourced year than its neighbors.
- Deceased-status audit: this batch's headline finding. Checked all 71 unique RR2009M-RR2012M
  entrants against Wikipedia and the mainstream-obituary bucket — unlike every prior batch, *none*
  already had deceased_date set going in. Individually spot-checked the lower-profile/higher-
  perceived-risk names (Jim Duggan, Jerry Lawler, Kevin Nash/Diesel, Kharma, Tyson Kidd, Curtis Axel,
  Mason Ryan, Vladimir Kozlov, Chris Masters, Ezekiel Jackson, Tyler Reks, Epico/Primo, Finlay,
  William Regal, Road Dogg, Mike Knox, JTG, The Brian Kendrick, Shelton Benjamin, Chavo Guerrero,
  Carlito, Johnny Nitro) and found exactly one new death: **husky-harris (Windham Rotunda), who later
  became Bray Wyatt, died 2023-08-24** of a heart attack in his sleep related to an undisclosed heart
  condition (sleep apnea exacerbating a pre-existing issue he'd been managing since February 2023 —
  he'd been hospitalized for a heart issue one week prior and advised to wear a defibrillator vest but
  wasn't wearing it). Independently corroborated by CBS News, CBS Sports, TVLine and Cageside Seats in
  addition to Wikipedia. Note on Jerry Lawler: he had a well-publicized 2025 stroke and is in recovery
  — confirmed alive, explicitly *not* treated as a deceased-status hit, so the two kinds of finding
  don't get conflated.
- Same-performer sibling bio-completion: this database already tracks husky-harris (his 2011 Rumble
  identity) and a separate bray-wyatt id (his later Rumble appearance) as two rows, per the project's
  gimmick-era-split convention — husky-harris's own notes already said "Later became Bray Wyatt."
  Following the exact precedent set by batch 3's golga/earthquake fix, filled in bray-wyatt's
  real_name, dob and deceased_date from husky-harris's own row — not a wrestler_id merge, just
  completing the real-person facts on both sibling rows. Recorded at PROBABLE throughout, matching
  husky-harris's own single-sourced confidence level rather than upgrading it just because the sibling
  link is solid.
- WWE Hall of Fame bio-completion (continuing batches 4-5's audit type): Edge (2012), Beth Phoenix
  (2017), and Kevin Nash (2015, individually inducted under his own name — recorded on this database's
  'diesel' wrestler_id row, per the same gimmick-era convention). Checked and found not yet inducted:
  William Regal, Road Dogg (group-only DX induction doesn't count), MVP, Goldust, Matt Hardy. That's
  16 HOF completions across 3 batches now purely from incidental discovery — still reinforces the case
  for a dedicated database-wide Hall of Fame pass.
- 8 new notable_moments.csv rows (NM026-NM033), again mostly surfaced from already-CONFIRMED content:
  Santino Marella's record-breaking 0:02 survival time (RR2009M); Edge's shortest-ever winning ring
  time and Beth Phoenix becoming only the second woman ever to compete in a standard 30-man Rumble
  (RR2010M); the first-ever 40-man Royal Rumble (RR2011M); the full WWE commentary team entering as
  competitors, Kofi Kingston's handstand escape, The Miz's non-entrant interference elimination of
  John Cena (surfaced from F262), and Big Show's unusual eliminations landed before his own official
  entry — deliberately logged PROBABLE, single-sourced (surfaced from F241) (all RR2012M).
- Deployed as dashboard Version 15 (rebuilt dashboard/data.json off the live database; page.html
  unchanged this batch; validated with a Playwright headless smoke test across all 4 event pages and
  the 5 touched wrestler profiles — husky-harris and bray-wyatt both correctly show the deceased
  badge, Edge/Beth Phoenix/diesel all correctly show the HOF badge — no console errors beyond an
  expected offline-sandbox resource-load failure unrelated to the app).

This closes out 2009-2012. One batch remains to complete the full 1988-2016 sweep: 2013-2016.

---

### 2013-2016 batch findings (2026-09-20) — the FINAL batch of the sweep
This closes out the full fact-check sweep: 1988 pilot → 1989-92 → 1993-96 → 1997-2000 → 2001-04 →
2005-08 → 2009-12 → this one. RR2013M-RR2016M already carried substantial flags (F267-F316, F326,
F335, F336) from the original build and earlier external fact-check passes — this range's own
historical_significance text already documents several external cross-checks it went through
(F296-F318), and several remaining open flags are genuine, deliberately-preserved CONFLICTING_SOURCES
disagreements rather than bugs. Winner/entrant-count/elimination-count/duration for all 4 events were
spot-checked and are already correctly CONFIRMED — no fix needed.
- Deceased-status audit: checked all 65 unique RR2013M-RR2016M entrants against Wikipedia and the
  mainstream-obituary bucket. Individually spot-checked the lower-profile/higher-perceived-risk names
  (The Godfather, Bradshaw/JBL, Bubba Ray Dudley, Adam Rose, Prince Albert, The Boogeyman, El Torito,
  Hunico, Damien Sandow, Darren Young, Erick Rowan, Heath Slater, Zack Ryder, Fandango, Tyler Breeze,
  Bo Dallas, Jack Swagger, David Otunga) and found exactly one new death: **Luke Harper (Jon Huber,
  also wrestled in AEW as Brodie Lee), died 2020-12-26** of complications from a rare, non-COVID
  progressive lung disease tied to an underlying autoimmune/blood disorder — independently corroborated
  by WWE's own tribute coverage and mainstream sports press in addition to Wikipedia.
- WWE Hall of Fame bio-completion (continuing batches 4-6's audit type): The Godfather (2016) and
  Bradshaw/JBL (2020), both individual inductions, confirmed via the existing HOF-bucket sources.
  Checked and correctly left blank: Bubba Ray Dudley — the Dudley Boyz were inducted as a tag team in
  2018, a group-only induction that doesn't satisfy this field's individual-induction convention, same
  treatment as Road Dogg/DX in the 2009-2012 batch. That's 18 HOF completions total across 4 batches
  now, purely from incidental discovery — the case for a dedicated database-wide Hall of Fame pass (see
  earlier write-ups) stands even stronger now that the full sweep is done.
- 10 new notable_moments.csv rows (NM034-NM043) — more than a typical batch, because this stretch is
  unusually rich in already-CONFIRMED trivia: John Cena's rare #9-21-draw 2nd win and The Godfather's
  5-gimmick farewell (RR2013M); Roman Reigns's record-breaking 12 eliminations and the fan backlash
  when Batista won instead — with the database's own uncorroborated 9.5 partial-credit recalculation
  noted honestly rather than upgraded — plus the "Not Daniel Bryan" Rey Mysterio surprise and Xavier
  Woods's never-realized entrant spot (RR2014M); the Daniel Bryan/Philadelphia boo-fest and Curtis
  Axel's Erick-Rowan substitution (RR2015M); the then-longest-ever 61:43 running time, Roman Reigns's
  in-match WWE Championship defense (only the 2nd time a title was decided by the Rumble match itself,
  after Ric Flair in 1992), and the individually-named Wyatt Family group elimination of Brock Lesnar
  (RR2016M).
- Deployed as dashboard Version 16 (rebuilt dashboard/data.json off the live database; page.html
  unchanged this batch; validated with a Playwright headless smoke test across all 4 event pages, the
  4 touched wrestler profiles — Luke Harper's deceased badge and The Godfather's/Bradshaw's HOF badges
  all render correctly — and the overview page, confirming the full 29-event dataset still loads clean
  end to end. No console errors beyond an expected offline-sandbox resource-load failure unrelated to
  the app).

**This completes the full 1988-2016 fact-check sweep.** Across all 7 batches (plus the original 1988
pilot pass and the dedup/gimmick-cross-linking feature built mid-sweep): every one of this database's
29 events has now had its winner/entrant/elimination/duration figures spot-checked, every unique
entrant has gone through at least one deceased-status pass, 18 WWE Hall of Fame bio-completions were
made incidentally, several same-performer sibling bio-completions were made without merging any
wrestler_id (golga/earthquake, big-boss-man/big-bossman, husky-harris/bray-wyatt), and 43
notable_moments.csv rows now exist covering the database's best "doesn't reduce to a single stat"
trivia. Strong candidates for a next project phase, in roughly the order they've come up across this
sweep's write-ups: (1) a dedicated database-wide WWE Hall of Fame pass, rather than picking up
completions incidentally; (2) extending the sweep forward past 2016, since WWE has run many more
Royal Rumbles since (including the Women's Royal Rumble, launched 2018) that aren't in this database
at all yet; (3) the video-analysis-dependent tables (entrances.csv, moves.csv, near_eliminations.csv)
stubbed in the schema but never built, pending a computer-vision tool; (4) a second full audit pass
now that the whole sweep's methodology has been battle-tested once already.

---

### Process change: HOF checks now happen at build time, not as a separate sweep (2026-09-20)
Shane's instruction: going forward, a new wrestler's WWE Hall of Fame status gets checked as part of
adding them to the database (i.e. when the event they're first added in is built), not picked up later
as its own incidental audit pass the way it was for the whole 1988-2016 sweep. Implemented starting with
the 2017 build (see below) — every wrestler new to the database gets a live HOF check alongside their
other bio research, and the result goes straight into their `wrestlers.csv` row in the same build script
rather than waiting for a future pass to stumble onto it. This doesn't retroactively change how the
1988-2016 roster was built (that's what the fact-check sweep was for), just how every wrestler added from
here forward is handled.

### 2017 Royal Rumble build (2026-09-20) — first event beyond Shane's source document
This is the first genuinely NEW event built in this database, not a fact-check pass over existing
content. Shane's own source document (Entrant_Stats.xlsx / Main_Rumble_Stats_New.docx) has nothing past
"2016 Royal Rumble Stats" — its final section is general cross-year trivia, then the document moves on to
WCW World War 3 content. Every event from 2017 onward therefore has to be built from fresh external
research rather than transcribed from Shane's own document, using the same cross-validation standard
already proven in this database's "external fact-check" passes on 2013-2016.
- Researched via Wikipedia, WWE.com's own official stats page, dailyddt.com, and WrestlingInc.com,
  cross-validated against each other rather than trusted individually — worth flagging that an initial
  pass at this genuinely produced two disagreeing-looking tables, which turned out to be a table-parsing
  artifact (a small model's fetch conflating "entrant order" and "elimination order" columns) rather than
  real source disagreement; a follow-up research pass caught and resolved it. Real source disagreement was
  found in exactly one place: Sheamus and Cesaro's relative elimination order (13th vs 14th, both
  eliminated by Chris Jericho seconds apart) — logged as CONFLICTING (F360) rather than picked arbitrarily.
- Built: full 30-entrant field, entry order and eliminator credit CONFIRMED for all but that one disputed
  pair, event facts (date, venue, attendance, winner's reward), 11 new wrestler bios (with HOF/deceased
  status checked as part of the build, per the process change above — Goldberg's 2018 individual HOF
  induction was caught immediately), and 7 notable_moments rows (Randy Orton's 2nd win, Tye Dillinger's
  "Perfect 10" entrance, Roman Reigns wrestling twice in one night, James Ellsworth's 15-second run, Braun
  Strowman's match-high 7 eliminations, the Goldberg/Lesnar elimination previewing their WM33 feud, and
  this being the last men's-only Rumble before the Women's Royal Rumble launched in 2018).
- One real methodology gap versus the pre-2013 years: no source recovered this pass gives entry-interval
  ("buzzer gap") data, so global match-clock timestamps (`elimination_clock_time`) couldn't be
  reconstructed with confidence and are left UNKNOWN throughout (F361) — each entrant's own survival
  duration (`ring_time`) IS populated and CONFIRMED, since that came directly from sources rather than
  being derived. This will very likely recur for every future externally-researched year unless a source
  with per-entrant entrance timestamps turns up.
- Dashboard: also fixed 3 places where the page's own HTML hardcoded "1988–2016" / "29 Events" — now
  computed from the data (`DB.meta.minYear`/`maxYear`) so this doesn't need a manual edit every time a new
  year is added. Deployed as dashboard Version 17 (data.json rebuilt, page.html changed this time,
  Playwright-smoke-tested — confirmed the year range now reads 1988–2017 and 30 event cards render, no
  console errors beyond the usual offline-sandbox resource-load noise).

Next up, per Shane's chosen pace (one event or two at a time, building forward through both Men's and
Women's Royal Rumble): 2018, which is the first year with a Women's Royal Rumble match to build alongside
the Men's.

### 2018 Men's and Women's Royal Rumble build (2026-09-20) — first year with both matches, kept as separate records
Built per Shane's explicit instruction: "Yes let's do that but remember to keep them separate" — RR2018M
and RR2018W are two fully independent event_id rows, built by two separate scripts
(`build_2018_men.py` / `build_2018_women.py`), never merged into one record even though they share a date,
venue and several sourcing threads. This is also the first pass where the earlier conversation was
compacted mid-task; the prior research findings weren't recoverable from the saved transcript in enough
detail to build from safely, so both events were re-researched from scratch via fresh web research rather
than risk building off a lossy paraphrase — consistent with this database's "never invent data" rule.

**RR2018M (Men's):** 30 entrants, researched via Wikipedia, WWE.com's official stats page, WrestlingInc.com,
and Cageside Seats' independent fan re-timing (used specifically to stress-test official timing figures).
Entry order and eliminator credit CONFIRMED for all 30 via 3 independent sources, cross-checked with an
internal arithmetic self-consistency check. One genuine, well-evidenced conflict: Sheamus's elimination
time is 0:20 per WWE.com (tier 1) but four independent fan-timed sources (Wikipedia's own footnote,
Cageside Seats, WhatCulture, KhelNow.com) converge on roughly 2-3 seconds instead — recorded at the
tier-1 figure per this database's source-hierarchy convention, but flagged CONFLICTING rather than
silently trusted (F367). 6 new wrestler bios added (Finn Bálor, Elias, Andrade, Shinsuke Nakamura, Aiden
English, Adam Cole), cross-checked against 2 independent sources (Wikipedia + Cagematch.net) where they
agreed — upgrading several fields to CONFIRMED rather than this database's usual single-source PROBABLE —
with 2 minor named bio conflicts preserved rather than guessed at (Elias's middle name, Adam Cole's
birthplace; F368). None of the 6 are WWE Hall of Famers as of this build. Also caught: Cesaro and Sheamus
(as The Bar) won the Raw Tag Team Championship earlier the same card, entering the Rumble as reigning
champions — recorded via `current_champion_title`/`title_won_date`, the same fields used for Roman Reigns's
title-loss in the RR2017M build.

**RR2018W (Women's):** the first-ever Women's Royal Rumble match — 30 entrants, researched via Wikipedia,
WWE.com's dedicated official stats page for the women's match, Cagematch.net, plus event-specific sourcing
(the Alicia Fox injury article, the Stephanie McMahon commentary announcement, and 2 contemporary
(next-day) outlets — Sports Illustrated and FanSided — covering the Ronda Rousey/Asuka finish
controversy). Entry order and eliminator credit CONFIRMED for all 30, including both group eliminations
(Vickie Guerrero, 4-way; Nia Jax, 6-way) with `simultaneous_group_id` used to link the rows. A specific,
deliberate re-verification (literally walking the 29-row elimination table rather than trusting either
source's own summary) confirmed Nia Jax's true total is 4 solo eliminations, not the "5" some secondary
sources claim — she was the victim, not a contributor, of the 6-way group elimination; Michelle McCool's
true total is 5 (4 solo + 1 shared), correctly distinguished from "5 solo." 29 new wrestler bios added —
essentially the entire field, since no Women's Rumble had been built before — including independently
web-fetching real name/DOB/birthplace for 3 Hall of Famers (Lita, Jacqueline, Trish Stratus) whose HOF
status was already known but whose bio data hadn't actually been sourced yet, rather than filling it from
general knowledge. Of the 9 returning legends/alumnae in the field, only 4 (Lita, Jacqueline, Beth
Phoenix, Trish Stratus) were already Hall of Famers as of the event date (Jan 28, 2018) — Michelle McCool,
Torrie Wilson and Molly Holly have since been inducted (2025, 2019, 2021), and the Bella Twins were
inducted in 2020, all well after this event; Kelly Kelly and Vickie Guerrero have never been inducted in
their own right (Vickie's late husband Eddie Guerrero's 2006 induction is his own, not hers — explicitly
not recorded on her row). One genuine conflict: the commentary team is CONFLICTING between two WWE.com
articles (one naming Stephanie McMahon alongside Cole/Graves, one not) — resolved to the better-evidenced
version in the structured field but logged, not silently picked (F373). Also recorded: the "second women's
match to main event a WWE PPV, first to main event a Big Four show" historical framing (direct Wikipedia
quote), the absence of both reigning champions (Alexa Bliss, Charlotte Flair) as entrants, and the
contemporary (within-24-hours) criticism that Ronda Rousey's surprise post-match appearance overshadowed
Asuka's win — while explicitly excluding an unverified "Beth Phoenix on commentary as a surprise entrant"
claim and the unrelated 2025 Royal Rumble "AJ Lee snub" story, which a first research pass had correctly
flagged as not belonging to this event.

- Both events tested in an isolated `/tmp` copy (full spot-check: entrant/elimination counts, elim_number
  coverage 1-29, eliminator credit tallies, HOF-at-time flags, wrestlers.csv HOF years) before touching
  live data, then deployed, `build_derived.py` and `build_dashboard_data.py` rerun, and Playwright-smoke-
  tested against the live data.json/page.html pairing (both new event pages render their full entrant
  lists and elimination tables correctly, hash-routed at `/events/RR2018M` and `/events/RR2018W`; the
  Events list correctly shows two separate "2018" cards, one per winner, confirming the events were kept
  separate as instructed; new wrestler profile pages render HOF badges correctly) before republishing.
- Deployed as dashboard Version 18 (32 events total, span now 1988-2018, 417 wrestlers).
- Continuing HOF-at-build-time process from RR2017M: all 35 new wrestlers across both events had HOF and
  deceased status checked live as part of this build (F369, F376).

Next up, per Shane's chosen pace: 2019, or a pause here to check in with Shane first, matching the
precedent set after RR2017M.

### Men's/Women's division split — architecture change (2026-09-20)

Shane's instruction: "I think I want all of the woman's stats and info completely separate to the man's."
Clarified via a scoping question before touching anything, since this could have meant several different
things and the wrong interpretation would have meant expensive rework:

- **Scope** — Shane chose "Everything": the Records & Leaderboards page, the Wrestlers index/profiles, the
  dashboard's navigation itself, and the underlying database files all needed to split Men's from Women's,
  not just the display layer.
- **Shared performers** (e.g. Beth Phoenix, who wrestled a Men's Rumble in 2010 and the Women's Rumble in
  2018) — Shane chose "One wrestler_id, stats split by side": she keeps a single wrestler_id/profile
  identity (the database's existing identity model is unaffected), but her career stats, leaderboard
  appearances and Rumble history are computed and displayed completely separately for her Men's-Rumble
  history vs. her Women's-Rumble history — never summed into one blended line.

**What changed, end to end:**

- `schema.py` — `DERIVED_TABLES` now carries a `division` field/key on `career_stats.csv` (compound key
  `wrestler_id` + `division`), `entry_number_stats.csv` (compound key `division` + `entry_number`),
  `records.csv`, `records_history.csv`, `elimination_rivalries.csv` (compound key including `division`),
  and `event_dynamic_stats.csv` (an explicit column, on top of the event_id's own M/W suffix).
- `build_derived.py` — every computation (career_stats, entry_number_stats, elimination_rivalries, and
  every category in the big records.csv block — Physical, Age, Time, Eliminations, Frequency, Field
  composition, Rivalries, plus the two "Collection of Stats" additions: most-wrestlers-to-eliminate-one-
  entrant and most-consecutive-solo-eliminations) is now computed independently per division, division
  derived from `events.csv:match_type` ("Men's"/"Women's"), never blended. `records_history.csv`'s
  append-only baseline diff key changed from `(category, record_name)` to `(division, category,
  record_name)` so a Men's and a Women's record in the same category never overwrite each other's history.
- `build_dashboard_data.py` — `data.json`'s top-level shape changed from one blended `events`/`records`/
  `wrestlers` set to a `divisions` array, one entry per division, each carrying its own fully independent
  `events`, `records` and `wrestlers` lists. A shared wrestler_id appearing in both divisions (Beth
  Phoenix) gets one entry in each division's `wrestlers` array with two independent stat lines, cross-
  linked via a new `otherDivision` field; the existing gimmick-era `samePerformer` cross-link (different
  wrestler_ids, same real person) is now scoped per division too, since a sibling id only makes sense as a
  link within a division where they themselves have a stat line.
- `dashboard/page.html` — routing restructured from the old flat `#/events`, `#/records`, `#/wrestlers`
  scheme into a two-track scheme: `#/home` (a simple combined landing page — division picker + raw
  database-size counts, deliberately not a blended stat hub), and `#/<mens|womens>/<events|records|
  wrestlers>[/<id>]` per division. Nav is built dynamically from the divisions actually present in the
  data rather than hardcoded, so a future third division (if one is ever added) needs no HTML changes. A
  wrestler profile page shows an "Also competed in" panel linking to the same wrestler_id's stat line in
  the other division when one exists, and the Wrestlers index/stat-sheet badges a name with "also Men's"/
  "also Women's" for quick discovery. A stale/legacy hash (e.g. `#/events` from before this change) falls
  back cleanly to Home rather than erroring.
- Tested in an isolated `/tmp` copy end to end (derived tables, dashboard JSON, and the two-track page.html
  all together, via a Playwright smoke test covering Home, both divisions' Events/Records/Wrestlers pages,
  Beth Phoenix's cross-division link click, the index badge, and the stale-hash fallback) before touching
  live data, then deployed and re-verified identically against live data.
- Deployed as dashboard **Version 19**. Practical effect on the current data: since the Women's Royal
  Rumble has only ever been held once (2018) versus 31 Men's Rumbles, the Women's records/leaderboards are
  currently thin (e.g. no Physical/Age records yet — the RR2018W build didn't capture billed weight/
  height/age for that field, a pre-existing data gap worth a future fact-check pass, not something this
  architecture change introduced or could paper over) — but the structure is now fully in place and will
  fill out correctly as more Women's Rumbles are built.

---

### RR2019M / RR2019W build (2026-09-21)

Built both 2019 Royal Rumble matches (Men's and Women's, Jan 27 2019, Chase Field, Phoenix — a joint card),
continuing the year-by-year build sequence and the division-split architecture shipped as Version 19.

**Research methodology note.** A first attempt at extracting the Men's entrant table via a generic WebFetch
prompt to Wikipedia produced a table that silently disagreed with two other independent extractions on the
Draw-number-to-wrestler mapping (while agreeing on each wrestler's own facts). This was NOT trusted and
re-done properly: two dedicated research agents were dispatched (one per match) with explicit instructions
to (1) demand a literal, verbatim, non-reordered, row-by-row transcription from Wikipedia, (2) independently
cross-check against 3-4 more sources, matching by wrestler NAME rather than row position, and (3) run an
arithmetic self-consistency check (elimination order 1-29 used exactly once, no gaps/dupes; total credited-
elimination tally reconciling against known shared-credit spots). Both matches passed this check cleanly.
The Women's agent additionally caught and discarded its own first, internally-inconsistent extraction
attempt (duplicate Draw numbers) before re-pulling cleanly — exactly the failure mode being guarded against.

**What the two builds cover:**
- **RR2019M** — winner Seth Rollins (entered #10, 43:00 survival), runner-up Braun Strowman, final four
  {Rollins, Strowman, Ziggler, Andrade}. 7 new wrestlers (Curt Hawkins, Samoa Joe, Johnny Gargano, No Way
  Jose, Aleister Black, Pete Dunne, Mustafa Ali), 23 reused. Notable: **Nia Jax**, already in the database
  from RR2018W, is a genuine entrant in this MEN'S match too — a real storyline moment (she attacked
  advertised entrant R-Truth and took his slot), legitimately injuring him in the process per a source
  citing Jerry Lawler's own podcast account. She also competes in RR2019W the same night, making her the
  first wrestler to exercise this database's division-split architecture across a same-night double
  appearance rather than across different years (the original Beth Phoenix precedent). Two elimination-
  time figures (Jeff Hardy, and separately Dean Ambrose/Rey Mysterio) and Braun Strowman's total credited-
  elimination count (6 by literal box-score vs. 5 per Fightful.com's own published stats) came back
  genuinely CONFLICTING between sources — logged as flags rather than silently picked. Attendance is
  CONFLICTING (48,193 WWE-announced vs. ~40,000 actual/~32,000 paid per Dave Meltzer) — a card-wide dispute
  also logged against RR2019W. Research also caught and corrected an initial WRONG assumption that several
  wrestlers (The Miz, Shane McMahon, AJ Styles, Kevin Owens, Finn Balor, Big Show, Bobby Roode, Chad Gable,
  Mojo Rawley) were probable entrants — none of them actually competed in this match, they wrestled
  elsewhere on the same card; this was fixed before anything was written to entrants.csv.
- **RR2019W** — winner Becky Lynch (unusually, entering AFTER the official #30 entrant had already gone in,
  having inherited injured Lana's #28 slot — see below), runner-up Charlotte Flair (first appearance in this
  database), final four {Lynch, Flair, Nia Jax, Bayley}. 14 new wrestlers (Lacey Evans, Billie Kay, Peyton
  Royce, Nikki Cross, Xia Li, Charlotte Flair, Maria Kanellis, Candice LeRae, Alicia Fox, Kacy Catanzaro,
  Zelina Vega, Io Shirai, Rhea Ripley, Alexa Bliss), 16 reused. Notable: Becky Lynch lost her own SmackDown
  Women's Championship match to Asuka earlier the SAME card, then still won the Rumble hours later — a
  remarkable same-night arc, confirmed via a direct Wikipedia footnote about the Lana/Becky Lynch entry
  mechanics (Lana "came out" as the #28 entrant but a storyline injury kept her from competing; Becky Lynch
  was allowed to take the slot, but only after #30 Carmella had already entered). This database records her
  OFFICIAL entry_number as 28 (matching the numbered-slot-replacement precedent from Sami Zayn/Tye Dillinger
  and Kairi Sane/Alicia Fox in prior years) while setting `final_entrant_id` to Carmella (the true #30) to
  keep that field's meaning consistent, and preserving Lynch's true chronological-last status in her entrant
  notes and a flag instead. One eliminator credit (Billie Kay/Peyton Royce, by Lacey Evans) is CONFLICTING
  against a single outlier source (mykhel.com, which also drops a shared-credit co-eliminator elsewhere) —
  resolved via source-count majority, logged rather than silently picked. Match duration and commentary
  team are also imperfectly resolved between sources — logged as flags. Attendance carries the same
  card-wide CONFLICTING figure as RR2019M.
- Both new-wrestler cohorts (21 total) had WWE Hall of Fame and deceased status checked live as part of this
  build, per Shane's standing process — none of the 21 are HOF-inducted or deceased as of today (2026-09-21).
- Tested in an isolated `/tmp` copy (both build scripts, then `build_derived.py` and
  `build_dashboard_data.py`, plus Python referential-integrity checks — no duplicate IDs, entry numbers
  1-30 with no gaps, exactly one winner per event, all cross-references resolving) before touching live
  data, then deployed identically and re-verified against live data. Playwright-smoke-tested the live
  two-track dashboard, including Nia Jax's cross-division "Also competed in" panel rendering correctly on
  both her Men's and Women's profile pages (2026-09-21's build now exercises the same-year, same-wrestler
  cross-division case for the first time, not just Beth Phoenix's cross-year case).
- Deployed as dashboard **Version 20**.

---

### The big wishlist (2026-09-21) — Shane's full stats/features brief, triaged

Shane sent a large, wide-ranging list of stats and features he wants the database/dashboard to grow into.
Before touching anything, it's worth recording the full list and an honest scope assessment, since several
of these items are wildly different in cost -- some are one `build_derived.py` addition away, others mean
re-researching every entrant of every year already built.

**Reality check on current data completeness** (audited across all 1,022 entrant rows / 34 events so far):
`alignment`, `billed_height_m_at_event`, `billed_weight_kg_at_event`, `billed_from_at_event` are each only
4.9% filled; `tag_team_name` 3.7%; `current_champion_title` 1.6%; `prior_rumble_appearances_count` 7.8%;
`previous_rumble_year`/`result` under 5%; `gimmick_at_event` 0.4%; `manager_at_event` 0%. These fields exist
in the schema already (they were always part of `ENTRANTS_FIELDS`) but were only ever populated when a
specific year's research happened to surface them -- they were never a dedicated research pass. Filling
them properly for all ~960 entrant-appearances across 32 years is a genuinely large research project, not a
quick pass.

**Phase A -- zero-new-research, derivable from data already in the database.** These just need new
`build_derived.py` logic (and dashboard surfacing) against `entrants.csv`/`eliminations.csv`/`wrestlers.csv`
as they stand today:
- Average entry number / average survival time per career (entry-number leaderboards already exist as
  `entry_number_stats.csv` -- just not fully surfaced on the dashboard yet)
- Most common opponents eliminated by a wrestler ("rivalries") -- **already computed**, `elimination_
  rivalries.csv` (1,029 rows) exists but isn't linked from wrestler profile pages yet
- Longest gap between Rumble appearances; consecutive-year-appearance streaks; consecutive-years-
  eliminated-by-the-same-wrestler streaks
- Most eliminations without ever winning
- Most Hall of Famers in a single Rumble's field (HOF year is already tracked per wrestler)
- Host arena/city stats (venue/city already on every `events.csv` row)
- Entry-number statistics page (data exists, needs its own dashboard page + expandable drill-downs)
- "Wrestlers in the ring at the same time" -- derivable by replaying each match's entry/elimination
  timeline against existing `entry_number`/`ring_time`/elimination-order data
- Rumbles with the most champions in the field -- blocked on Phase B's `current_champion_title` backfill
  being populated first, can't do this properly yet

**Phase B -- per-appearance biography backfill (the big one).** Needs new research across every existing
entrant row, not just new years going forward: heel/face alignment at the time; billed height/weight/
hometown at the event (feeds a world-map/demographics page); tag team partner + whether the partner was
also in the same Rumble; current champion status entering the match, and titles held before/after; debut
vs. return status; whether they wrestled (and won) another match earlier on the same card; prior Rumble
appearance count and best result, and years-since-last-appearance; non-wrestler/celebrity entrant flags;
masked wrestlers; attire (trunks vs. trousers); entrance time; elimination method (superkick, clothesline,
thrown, etc.) and camera-side/ring position; betrayals, distractions, non-participant interference.
Ethnicity/nationality is on this list too -- flagged separately below, needs a decision before any work
starts on it.

**Phase C -- new dashboard features**, once Phase A/B data exists to power them: an interactive world map
pinning wrestler birthplaces; every record card expandable to a full top-10/full list, not just the single
leader; a highest-combined-billed-weight/height-in-the-ring-at-once stat with fun real-world comparisons
(Shane's own example: "equivalent to the height of Big Ben"); a champion-history browser/filter; host-arena/
city stat pages; highest-rated Royal Rumble events (this one needs genuinely NEW external data -- review/
rating scores aren't tracked anywhere in this database today).

**Phase D -- naming convention change**, small and mechanical, can be folded into any of the above: display
"Alias" instead of "gimmick" in the UI, and prefer the wrestler's commonly-known ring name over their birth
name where the two differ and the ring name is how they're actually known (Kane, not Glenn Jacobs; Road
Dogg, not Brian James) -- this affects `wrestlers.csv:ring_name` usage/labeling conventions and the
`gimmickBadge()`/`samePerformer` UI copy, not the underlying data model.

**Flagged for a decision before starting: race/ethnicity.** Nationality (already a schema field, e.g.
"Japanese," "Mexican," "Canadian") is straightforward and well-documented. A blunt "race" field is a
different, more sensitive kind of category to build into a permanent structured database -- worth
confirming with Shane exactly what he wants tracked (self-described ethnicity/heritage as reported in
reliable sources, vs. a coarser race classification) before any research or schema work begins on it.

**Shane's decisions on sequencing (2026-09-21):**
- **Keep building new years first.** The chronological year-by-year build (RR2020 onward) continues; this
  whole wishlist is a backlog to pick up once that sequence catches up to today, not something to context-
  switch onto mid-sequence.
- **When Phase B (the biography backfill) starts, go oldest to newest** -- 1988 forward, matching the
  order the database was originally built in, rather than newest-to-oldest (better sourcing) or one-field-
  at-a-time-across-all-years.
- **Race/ethnicity scope resolved:** track nationality (already in schema) PLUS ethnicity/heritage only
  where a wrestler has publicly self-described it in reliable sources (e.g. "Samoan-American," "African-
  American," "Mexican-American") -- never an assigned/inferred race label. This will need a new
  `wrestlers.csv` field (e.g. `ethnicity_heritage` alongside the existing `nationality`) when Phase B
  starts, sourced the same CONFIRMED/PROBABLE way as every other bio fact, left blank rather than guessed
  when a wrestler hasn't spoken about it publicly.

---

## RR2020M / RR2020W build (2026-09-21)

Continued the chronological year-by-year build per Shane's "keep building new years" instruction. Built
Royal Rumble 2020 (Jan 26, 2020, Minute Maid Park, Houston, Texas), both matches as fully separate
event_id records (RR2020M / RR2020W), following the exact same research/build/test/deploy pipeline used
for RR2019M/RR2019W.

**Research note:** the RR2020 research (originally done via two parallel agent calls) had to be re-run
fresh after a context-compaction event lost the detailed entrant/elimination tables from the first pass —
only the high-level summary survived, which wasn't enough to build from without risking invented data. Two
fresh research agents were run, this time using the by-then-established rigorous methodology (verbatim
row-by-row transcription demanded, cross-checked by name across 4-5 sources, arithmetic self-consistency
check). The Men's agent's first Wikipedia extraction was internally inconsistent and was discarded/re-pulled
correctly per protocol; the Women's agent's first attempt was clean on the first try.

**RR2020M:** Won by Drew McIntyre (entry #16, survived 34:11), eliminating Roman Reigns. Brock Lesnar
(entry #1) tied the all-time single-Rumble elimination record with 13 credited eliminations before being
eliminated himself — his exact credit on 2 of those 13 (Keith Lee, Braun Strowman) is CONFLICTING across
three different source versions, resolved using the official/majority version. Edge made a surprise in-ring
return after his 2011 forced retirement. Seth Rollins's "Monday Night Messiah" storyline (backed by Authors
of Pain interference, not co-credited since they weren't entrants) picked off a brief Owens/Black/Joe
alliance. King Corbin (post-"King of the Ring 2019" moniker) was correctly reused as the existing
`baron-corbin` wrestler_id rather than split into a new one — his profile now correctly shows all 4 career
Rumble appearances (2017/2018/2019/2020) aggregated, verified directly against career_stats.csv and the
live dashboard.

**RR2020W:** Won by Charlotte Flair (entry #17, survived 27:19), eliminating Shayna Baszler (runner-up).
Shayna Baszler and Bianca Belair tied for the all-time Women's Royal Rumble elimination record with 8 apiece,
breaking Nia Jax's prior record of 7. Kairi Sane entered as the field's one reigning champion (WWE Women's
Tag Team Championship, Kabuki Warriors) — correcting an initial working assumption that Alexa Bliss/Nikki
Cross held those titles at this point (they didn't win them until WrestleMania 36). Toni Storm and Shayna
Baszler both entered as recently-*former* champions of their own titles, not reigning ones. Santino Marella
returned in his comedic "Santina" drag persona for a self-elimination spot (a new `is_self_elimination`
usage pattern, reusing his existing wrestler_id).

**"New to database" vs. "new to WWE" correction, applied proactively this time:** 7 of the 16 combined new
wrestlers this build (Robert Roode, John Morrison, Ricochet, Karl Anderson, Luke Gallows on the men's side;
Bianca Belair, Shayna Baszler on the women's side) are established WWE/NXT performers that the research
agents initially assumed needed no fresh bio — but none of the 7 had actually appeared as an entrant in any
Royal Rumble 1988-2019 already built in this database, making each a genuinely new wrestler_id here. This
was caught by directly checking each agent's "no fresh bio needed" name against live `wrestlers.csv` before
writing the build scripts (the exact verification step flagged as still-needed after the RR2019 build), and
full bios were researched directly for all 7 rather than left blank.

**Testing/deployment:** copied `scripts`+`data` to an isolated `/tmp` directory, ran both build scripts,
`build_derived.py`, and `build_dashboard_data.py`; caught and fixed one bug during isolated testing (a flag-ID
numbering collision — F403 was reused across both scripts — fixed via a bulk regex renumber before deploying
live); ran a Python referential-integrity validation pass (duplicate-ID checks, entry-number completeness,
single-winner check, wrestler_id cross-reference checks) — clean except for pre-existing issues from earlier
years unrelated to this build. Repeated identically against live `data/`. Playwright headless smoke test
confirmed both event pages render correctly (winner, date, venue, attendance, runner-up all correct) and
directly verified the King Corbin/Baron Corbin wrestler_id merge renders his full 4-appearance history
correctly on the live dashboard. Deployed as dashboard **Version 21**.

---
Have more ideas as they occur to you — the intent is this file grows
alongside the database, not that it's "finished" now.
