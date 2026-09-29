# Order-in-Match Gap Worklist

Generated 2026-09-23, against the live database immediately after the Version 27 dashboard publish (RR1994M co-winner fix). Running `python3 scripts/validate_integrity.py data` right now reports exactly these **10 errors**, all of the same kind — an event's `eliminations.csv` `order_in_match` sequence doesn't run cleanly from 1 to the expected count. This is the full, explicit list of what's needed to close every one of them from Wikipedia.

There are two genuinely different kinds of gap here, and they need different amounts of work.

## Two gap types

**Type A — "no entry order recorded at all" (6 events: 1994, 1998, 2000, 2002, 2004, 2006).** For these, `entrants.csv` has no `elim_number` for almost every non-winner entrant. The database has the entrant list and (mostly) entry numbers, but the actual elimination sequence was never sourced. This is the bigger job — you're establishing the order from scratch for the whole match.

**Type B — "just missing eliminator credit for a handful of entrants" (4 events: 2007, 2013, 2015, 2016).** For these, `entrants.csv` already has a **CONFIRMED** `elim_number` and elimination time for every entrant — the order is fully known. The gap is narrower: a specific entrant is missing their **eliminator** (who put them out), so there's no matching row in `eliminations.csv` for that elimination at all. This is a much smaller job — one Wikipedia lookup per named wrestler, not a whole match.

## What to fill in, and where

Two files, and for Type A/B alike you're touching both:

**`data/entrants.csv`** (one row per wrestler per event — this is what the dashboard and every derived stat actually reads):
- `elim_number` — integer, their position in the elimination order (1 = first out). Leave blank + `elim_number_status=N/A` only for a genuine no-show who never entered (see note below); otherwise a real number.
- `elim_number_status` — `CONFIRMED` if 2 independent sources agree, `PROBABLE` if only 1 source or it's a reasoned inference (e.g. derived from buzzer-gap timing), `UNCERTAIN`/`CONFLICTING` if sources disagree (and add a flags.csv row — see below).
- `eliminated_by_ids` — the eliminator's `wrestler_id` (semicolon-separated if more than one, e.g. a tag-team elimination).
- `eliminated_by_ids_status` — same CONFIRMED/PROBABLE/etc. convention.
- `elimination_clock_time` (mm:ss) and `elimination_clock_seconds` — only needed for Type A; Type B already has these filled in.
- `source_ids` — semicolon-separated source IDs (see Sourcing below).
- `notes` — free text, especially for anything odd (simultaneous eliminations, storyline complications, disputed calls).
- `data_quality_status` — the row's overall status.

**`data/eliminations.csv`** (one row per elimination event — this is the timeline table the dashboard renders):
- `event_id`, `order_in_match` (the number you just assigned), `eliminated_wrestler_id`, `eliminator_wrestler_id` (blank if genuinely unrecorded/unknown), `assisting_wrestler_ids` (if a group elimination, everyone else involved besides the primary eliminator), `entry_number_of_eliminated`, `entry_number_of_eliminator`, `elimination_clock_time`, `elimination_clock_seconds`.
- `elimination_type` — controlled vocabulary already in use: `over_the_top_rope` (the normal case — use this unless something unusual happened), `self_elimination`, `voluntary_dive`, `voluntary_exit`.
- `elimination_method` — free text describing what actually happened (a sentence or two is fine and is exactly the existing style — see any populated row for the tone).
- `is_solo` / `is_shared` (TRUE/FALSE — was it one eliminator or several), `is_accidental`, `is_self_elimination`, `is_storyline_related`, `was_already_incapacitated`, `is_disputed` — TRUE/FALSE flags, leave FALSE unless the source specifically says so.
- `simultaneous_group_id` — only needed if 2+ wrestlers went out at the exact same moment (give them the same group ID); leave blank otherwise.
- `data_quality_status`, `source_ids`, `notes` — same conventions as above.

**No-shows**: if you find a wrestler was advertised/drew a number but never actually entered the ring (this database already has a few of these, e.g. Bastion Booger 1994, Skull 1998, Spike Dudley and Test 2004), the convention is: leave `elim_number` blank and set `elim_number_status=N/A` specifically (not blank, not UNKNOWN — the validator only recognizes the literal `N/A`), and don't create an `eliminations.csv` row for them at all.

**Sourcing**: Wikipedia's own Royal Rumble match entrant tables (with Entrance #, Eliminated by, Elimination move, Time columns) are exactly the kind of structured source this database is built from. If the Wikipedia article for that year isn't already in `data/sources.csv`, add a new row (next available `source_id`, e.g. continue from S446) — the format is `source_id,source_name,source_type,url,reliability_tier,tier_label,accessed_date,notes`; copy the style of the existing `S0xx: Wikipedia: Royal Rumble (YYYY)` rows (reliability_tier 10, tier_label "Wikipedia/reference"). A single Wikipedia table only gets you to PROBABLE, not CONFIRMED, per this database's 2-independent-source rule — CONFIRMED needs a second source (e.g. Cagematch, an allrumblestats.com/PWDB style stats site, or a Cageside Seats-style retrospective) to agree, the same standard every other event in the database uses. PROBABLE is a perfectly fine status to leave these at if a second source isn't easy to find — do not invent a second source or guess to force CONFIRMED.

**If two sources disagree** on an eliminator or order, do NOT pick one arbitrarily — that's exactly the "never invent data" rule this whole database is built around. Instead: record the one you consider more likely with an appropriate PROBABLE/UNCERTAIN status, and add a row to `data/flags.csv` (columns: `flag_id` — next available, e.g. continue from the existing sequence; `event_id`; `table`; `record_id`; `field`; `issue_type=conflicting_sources`; `description`; `source_ids_involved`; `status=open`; `date_logged`) documenting the disagreement, exactly like the many existing `conflicting_sources` flags on these same events already do.

**After you're done with an event**, run `python3 scripts/validate_integrity.py data` — it should drop that event out of the error list. I'll handle rebuilding `scripts/build_derived.py` / `scripts/build_dashboard_data.py` and republishing the dashboard once you've worked through however many you want to tackle; you don't need to run those yourself.

---

## Type A events — full order needed (6)

### RR1994M — winner: Bret Hart (co-winner Lex Luger, already handled separately)
28 of 29 non-winner entrants need `elim_number` established (all currently `UNKNOWN`), in entry-number order:
scott-steiner(#1), samu(#2), rick-steiner(#3), kwang(#4), owen-hart(#5), bart-gunn(#6), diesel(#7), bob-backlund(#8), billy-gunn(#9), virgil(#10), randy-savage(#11), jeff-jarrett(#12), demolition-crush(#13), doink(#14), bam-bam-bigelow(#15), mabel(#16), sparky-plugg(#17), shawn-michaels(#18), mo(#19), greg-valentine(#20), tatanka(#21), great-kabuki(#22), genichiro-tenryu(#24), rick-martel(#26), fatu(#28), marty-jannetty(#29), adam-bomb(#30) — plus bastion-booger(#25), who per F091 withdrew before the match due to illness and never entered (currently has blank `elim_number_status` rather than the standard `N/A` — worth correcting to `N/A` while you're in there, or leave it, your call).

Relevant open flags: **F059** (Shane's source doc has no timing chapter for this year at all — this is a genuine source-material gap, not a processing miss), **F061/F063** (participant-list completeness), **F092** (Mabel's elimination credited only to an unnamed "group" per Wikipedia — worth checking if a fuller source names them), **F094/F095/F096** (Bret/Luger finish and the Doink performer, not order-related), **F521** (the flag documenting this exact co-winner modeling handoff, now resolved by Version 27).

### RR1998M — winner: Steve Austin
29 of 30 non-winner entrants need `elim_number` (all `UNKNOWN` except skull, who is the 1 documented no-show — already correctly `N/A`, no action needed):
cactus-jack(#1), terry-funk(#2), tom-brandi(#3), rocky-maivia(#4), mosh(#5), phineas-godwinn(#6), eight-ball(#7), bradshaw(#8), owen-hart(#9), steve-blackman(#10), d-lo-brown(#11), kurrgan(#12), marc-mero(#13), ken-shamrock(#14), thrasher(#15), mankind(#16), goldust(#17), jeff-jarrett(#18), the-honky-tonk-man(#19), ahmed-johnson(#20), mark-henry(#21), kama(#23), henry-godwinn(#25), savio-vega(#26), faarooq(#27), dude-love(#28), chainz(#29), vader(#30).

Relevant open flags: **F111** (Mick Foley wrestled this match 3 times under 3 gimmicks — Cactus Jack #1, Mankind #16, Dude Love #28 — all 3 already correctly separate entrant rows, just noting it so you don't merge them), **F113** (Triple H injured, didn't take his own #19 slot — Honky Tonk Man went instead, already reflected in the entrant list above), **F142** (Harris twins birth-year conflict, not order-related), **F144/F145/F146/F147** (specific elimination-credit leads worth checking first — Owen Hart's elimination per S050 is jointly Triple H AND Chyna; Kurrgan's is a 6-way group per S050; Phineas Godwinn's elimination allegedly kicked the referee; The Rock's elimination time has a source discrepancy), **F500** (confirms only 2 outside-interference entrants, not 3 — already reflected above).

### RR2000M — winner: Rocky Maivia (The Rock)
29 of 30 non-winner entrants need `elim_number` (all `UNKNOWN`):
d-lo-brown(#1), brian-christopher(#2), mosh(#3), christian(#4), rikishi(#5), scott-taylor(#6), steve-blackman(#7), mabel(#8), big-boss-man(#9), test(#10), british-bulldog(#11), gangrel(#12), edge(#13), bob-backlund(#14), chris-jericho(#15), crash-holly(#16), chyna(#17), faarooq(#18), jesse-james(#19), al-snow(#20), val-venis(#21), prince-albert(#22), hardcore-holly(#23), billy-gunn(#25), big-show(#26), bradshaw(#27), kane(#28), the-godfather(#29), 1-2-3-kid(#30).

Relevant open flags: **F128** (bio gaps, not order), **F153/F154/F155** (birthplace/DOB conflicts for Crash Holly/Scott Taylor/Rikishi, not order-related — skip these, they're not about the elimination sequence).

### RR2002M — winner: Triple H
29 of 30 non-winner entrants need `elim_number` (all `UNKNOWN`):
rikishi(#1), goldust(#2), big-boss-man(#3), bradshaw(#4), lance-storm(#5), al-snow(#6), billy-gunn(#7), the-undertaker(#8), matt-hardy(#9), jeff-hardy(#10), maven(#11), scott-taylor(#12), christian(#13), diamond-dallas-page(#14), chuck-palumbo(#15), the-godfather(#16), prince-albert(#17), perry-saturn(#18), steve-austin(#19), val-venis(#20), test(#21), the-hurricane(#23), faarooq(#24), mr-perfect(#25), kurt-angle(#26), big-show(#27), kane(#28), rob-van-dam(#29), booker-t(#30).

Relevant open flags: **F159** (attendance conflict, not order), **F163** (no reliable source found yet for who eliminated Maven right after his famous Undertaker elimination — worth a fresh look), **F165** (Austin/Undertaker tied for most eliminations per one source — cross-check while you're filling in the order).

### RR2004M — winner: Chris Benoit
28 of 31 entrants need `elim_number` (all `UNKNOWN`; spike-dudley and test are the 2 documented no-shows, already correctly `N/A` — no action needed for them):
randy-orton(#2), mark-henry(#3), yoshihiro-tajiri(#4), bradshaw(#5), rhyno(#6), matt-hardy(#7), scott-steiner(#8), matt-morgan(#9), the-hurricane(#10), booker-t(#11), kane(#12), rikishi(#14), renee-dupree(#15), prince-albert(#16), shelton-benjamin(#17), ernest-miller(#18), kurt-angle(#19), rico(#20), mick-foley(#21), christian(#22), nunzio(#23), big-show(#24), chris-jericho(#25), charlie-haas(#26), billy-gunn(#27), john-cena(#28), rob-van-dam(#29), bill-goldberg(#30).

Relevant open flags: **F175** (Test's no-show and Foley's slot-21 replacement — already correctly reflected in the no-show handling above), **F176** (Foley's "Cactus Jack clothesline spot" eliminated both Foley and Randy Orton together — this is a real simultaneous elimination, use `simultaneous_group_id`), **F206** (Yoshihiro Tajiri's eliminator is Rhyno alone per one source but Mark Henry+Rhyno jointly per another — genuine conflict, needs a flags.csv entry either way), **F207** (Charlie Haas's eliminator similarly disputed between Goldberg alone vs. jointly).

### RR2006M — winner: Rey Mysterio
29 of 30 entrants need `elim_number` (all `UNKNOWN`):
hunter-hearst-helmsley(#1), simon-dean(#3), psicosis(#4), ric-flair(#5), big-show(#6), jonathan-coachman(#7), bobby-lashley(#8), kane(#9), sylvan-grenier(#10), carlito(#11), chris-benoit(#12), booker-t(#13), joey-mercury(#14), tatanka(#15), johnny-nitro(#16), trevor-murdoch(#17), eugene(#18), road-warrior-animal(#19), rob-van-dam(#20), orlando-jordan(#21), chavo-guerrero(#22), matt-hardy(#23), super-crazy(#24), shawn-michaels(#25), chris-masters(#26), mabel(#27), shelton-benjamin(#28), goldust(#29), randy-orton(#30).

Relevant open flags: **F192** (Shane McMahon, a non-entrant, allegedly eliminated Shawn Michaels per one source — a real oddity worth preserving in notes if it holds up), **F213** (several survival times disputed between 2 stats-blog sources), **F214** (Tatanka's elimination via MNM tag-team interference rather than a single eliminator), **F215/F216/F217** (Viscera/RVD/Super Crazy eliminator conflicts — 3-way source disagreement on Super Crazy specifically), **F218** (raw attendance/duration figures internally inconsistent), **F321** (Rey Mysterio's longest-single-appearance record sits within a small external range, not order-related).

---

## Type B events — just the missing eliminator credit (4)

These already have full, CONFIRMED order and timing in `entrants.csv`. You only need to look up **who eliminated this one named wrestler** and add the matching `eliminations.csv` row (plus fill `eliminated_by_ids`/`eliminated_by_ids_status` on their `entrants.csv` row).

### RR2007M — order #10 — Booker T (entry #12, eliminated 25:12)
Winner: The Undertaker. Wikipedia's entrant table for this match will have Booker T's "Eliminated by" cell. Relevant open flag: **F220** — this is already a known 1-source-vs-1-source split (Wikipedia says Kane alone; prowrestling.fandom.com says something different) — check both and if they still disagree, use PROBABLE + a flags.csv row rather than picking one.

### RR2013M — order #6 — Brodus Clay (entry #13, eliminated 21:57)
Winner: John Cena. Relevant open flag: **F336** — already flagged as unresolved after checking WrestlingInc.com, Sportskeeda, and wwebrady.fandom.com without success. Worth one more direct Wikipedia check since this worklist is specifically asking you to look; if it's still not findable, this one may need to stay UNKNOWN with the flag left open rather than forced closed.

### RR2015M — 11 gaps — order #2 r-truth(#2), #4 curtis-axel(#6), #5 luke-harper(#4), #7 hunico(#8), #8 zack-ryder(#9), #12 daniel-bryan(#10), #15 goldust(#16), #17 damien-sandow(#21), #23 cesaro(#28), #25 bray-wyatt(#5), #26 dean-ambrose(#25)
Winner: Roman Reigns. This is the biggest Type B job — 11 separate eliminator lookups. Relevant open flags: **F286** (Kane and Big Show were eliminated simultaneously by Roman Reigns — already correctly modeled, not one of the 11 gaps above), **F309** (corroborates the simultaneous-elimination read), **F310** (Bray Wyatt's elimination-COUNT total is 6 per one source — separate from his own elimination-by, don't conflate).

### RR2016M — 4 gaps — order #12 kevin-owens(#18), #15 mark-henry(#22), #25 bray-wyatt(#27), #28 roman-reigns(#1)
Winner: Triple H. Relevant open flags: **F312** (Curtis Axel's eliminator is disputed between AJ Styles per 2 sources and Roman Reigns per a 3rd — not one of the 4 gaps, but check it while you're in this event), **F313** (Alberto Del Rio's eliminator similarly disputed), **F316** (whether Triple H physically entered before Sheamus despite being the later official entrant — trivia, not order-affecting).
