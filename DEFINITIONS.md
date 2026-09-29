# Definitions

These are fixed for the whole project (per Shane's spec, section 35). Every
build script applies these consistently rather than re-deciding them per event.

**Time in match / ring time** — from the moment a wrestler legally enters the
ring (both feet over the top rope and onto the mat) until they are eliminated,
or until the match ends if they win. This is what `entrants.csv:ring_time`
stores. It is NOT the same as time-on-broadcast, which can differ slightly
from published "ring time" stats when a source's clock starts at a different
point (see `ring_time_status` — most historical Rumbles only have one
published ring-time source, so these are PROBABLE, not CONFIRMED, until
cross-checked or footage-timed).

**Entrance time** — from the entrance-start cue (typically: their entry
number is shown/announced or their music hits) to the moment their body
first enters the ring. `entrances.csv` now records Cageside Seats' human,
frame-by-frame review: `countdown_ts` is the cumulative match timestamp of
the relevant buzzer; `enters_ring_ts` and `entrance_duration_seconds` are
populated only where the article enumerates that entrant's buzzer-to-ring
duration. The first two entrants remain absent because their entrances took
place before the match clock began. A legitimate no-buzzer/no-show case is
left blank rather than assigned a synthetic zero.

**Elimination** — a wrestler is officially eliminated when both feet touch
the floor outside the ring after going over the top rope (the Rumble's
standard rule since 1988; noted in `events.csv:special_rules` if a given
year varied — e.g. count-outs/pinfalls have never applied in the Rumble
match itself).

**Credited elimination** — the wrestler the broadcast/commentary and
official record attribute the elimination to. This is what
`eliminations.csv:eliminator_wrestler_id` stores.

**Assisted elimination** — more than one wrestler materially contributed to
putting the eliminated wrestler over the rope. `eliminations.csv` logs one
row per contributing wrestler and links them with a shared
`simultaneous_group_id`; it does NOT automatically mean both get a "credited
elimination" in traditional stat-keeping — where the original broadcast/
records single out one specific eliminator, that's who is_solo/credited.
Where sources plainly credit both (e.g. "eliminated by X and Y"), both are
logged and `is_shared` = TRUE.

**Rumble debut** — first appearance in a Royal Rumble MATCH specifically
(distinct from company debut).

**Company debut** — a wrestler's first appearance for the promotion running
the show (WWF/WWE), which may predate their first Rumble appearance by
years.

**"Confirmed champion at event" vs. "eventual career champion"** — kept
strictly separate. `entrants.csv:current_champion_title` only reflects a
title actually held ON THE EVENT DATE. Career-long facts (e.g. "went on to
win the world title 3 years later") belong in `career_stats.csv` /
`wrestlers.csv` notes, never conflated with in-the-moment status.

## Status vocabulary (used throughout)

| Status | Meaning |
|---|---|
| CONFIRMED | Directly stated by a cited, reliable source |
| DERIVED | Calculated from other CONFIRMED/DERIVED fields (formula documented) |
| PROBABLE | Stated by exactly one source, not yet cross-checked against a second |
| UNCERTAIN | Single weak/informal source, or minor unresolved discrepancy |
| CONFLICTING | Two+ reliable sources disagree — both preserved, see flags.csv |
| UNKNOWN | No reliable source found — field left blank on purpose |
| N/A | Field doesn't apply to this record |

## Source reliability tiers (Shane's hierarchy, section 4)

1. WWE / official sources
2. Official event footage
3. WWE Network / Peacock footage
4. Cagematch
5. ProFightDB / Internet Wrestling Database
6. WrestlingData
7. Wrestling Observer / reputable wrestling publications
8. Historical newspapers and magazines
9. Contemporary wrestling publications
10. Wikipedia and similar reference sites
11. Shane's original research document (Entrant_Stats.xlsx / Main Rumble Stats.docx)
12. Other reputable statistical/historical wrestling sites

A fact independently stated by 2+ sources that AGREE with each other is
CONFIRMED, regardless of exact tier (e.g. Wikipedia's structured match
table and Shane's original research agreeing to the second on 20 entry/
elimination times, independently compiled, is strong evidence — stronger
than either alone). A fact from a single source — including Shane's
original document on its own — is PROBABLE, not CONFIRMED, until a second
source is found. Sources that disagree are CONFLICTING, both preserved,
logged in flags.csv. Tier numbers are used to decide which source wins a
disagreement (lower tier number = trusted more), not to gate whether
something counts as "confirmed."
