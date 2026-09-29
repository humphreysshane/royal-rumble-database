# BUILD INSTRUCTIONS — Full Handoff Kit

You've been given the live Royal Rumble statistics database and asked to
build the remaining years directly into it: **2021, 2022, 2023, 2024, 2025,
2026 — Men's and Women's — 12 events total.** This document is everything
you need to do that to the same standard as everything already in the
database. Read it in full before writing anything.

This is a **full handoff**: you (AI or human) are writing directly to the
database files yourself, not just handing research back. That means you are
responsible for the same rigor and the same testing discipline that built
everything already here. Nothing about the standard is relaxed because
you're doing the writing instead of Shane's regular assistant.

---

## 0. The prime directive: never invent data

If you cannot find a reliable source for a field, **leave it blank** (empty
string) and, if it matters, log it in `flags.csv` with `issue_type =
"unverified"` or `"needs_human_judgement"`. Do not guess a plausible date,
a plausible hometown, a plausible elimination order. A blank cell is honest;
a guessed cell corrupts the database permanently and silently. This rule
overrides every convenience below.

---

## 1. Read these two files first

- **`DEFINITIONS.md`** — the fixed vocabulary and rules for the whole
  project: what "ring time" means, what counts as a "credited elimination,"
  the status vocabulary, the source reliability tiers. Everything below
  assumes you've read it.
- **`scripts/schema.py`** — the authoritative field list for every table
  (as Python constants: `WRESTLERS_FIELDS`, `EVENTS_FIELDS`,
  `ENTRANTS_FIELDS`, `ELIMINATIONS_FIELDS`, `SOURCES_FIELDS`,
  `FLAGS_FIELDS`, `NOTABLE_MOMENTS_FIELDS`, etc., plus a `TABLES` dict
  mapping every CSV filename to its field list). Every row you write must
  have exactly these fields, in this order.

### Status vocabulary — the only valid values for any `*_status` column

`CONFIRMED`, `DERIVED`, `PROBABLE`, `UNCERTAIN`, `CONFLICTING`, `UNKNOWN`,
`N/A`, or empty string. **Nothing else** — not `"UNVERIFIED"`, not
`"VERIFIED"`, not `"PENDING"`. (`"unverified"` lowercase IS valid, but only
as a `flags.csv:issue_type` value — a completely different vocabulary. This
exact confusion caused a real bug during the 2020 build; `validate_integrity.py`
below will catch it if you slip, but check yourself first.)

- **CONFIRMED**: 2+ independent reliable sources agree.
- **DERIVED**: calculated from other CONFIRMED/DERIVED fields (e.g.
  `days_into_reign_at_event` from a title-win date + event date).
- **PROBABLE**: exactly one source states it, not yet cross-checked.
- **UNCERTAIN**: single weak/informal source, or a minor unresolved wrinkle.
- **CONFLICTING**: 2+ reliable sources disagree — log both values in
  `flags.csv`, pick the higher-tier source for the stored field value, and
  say in the flag which sources said what.
- **UNKNOWN**: no source found — leave the field blank.
- **N/A**: field doesn't apply to this record at all.

### Source reliability tiers (1 = most trusted)

1. WWE/official sources · 2. Official event footage · 3. WWE Network/Peacock
footage · 4. Cagematch · 5. ProFightDB/IWD · 6. WrestlingData · 7. Wrestling
Observer/reputable wrestling pubs · 8. Historical newspapers/magazines ·
9. Contemporary wrestling publications · 10. Wikipedia and similar ·
11. Shane's original research doc · 12. Other reputable stat/history sites.

Tiers break ties on disagreement. They do **not** gate CONFIRMED status by
themselves — two tier-10 sources that independently agree is still
CONFIRMED; one tier-1 source alone is still only PROBABLE.

---

## 2. ID conventions — READ THIS SECTION CAREFULLY, this is where collisions happen

Every ID type below is **sequential and global across the whole database**.
If you and anyone else (or you across two separate build scripts) both use
`F420`, the database is broken and `validate_integrity.py` will refuse to
pass. **Compute the next available ID fresh, immediately before you use it
— don't hardcode a number you calculated earlier in a long session.**

To (re)compute the current maximum IDs, run this from the `data/` directory
you're working against:

```python
import csv
def maxnum(path, col, prefix):
    with open(path, newline="", encoding="utf-8") as f:
        nums = [int(r[col][len(prefix):]) for r in csv.DictReader(f) if r.get(col)]
    return max(nums) if nums else 0

print("max source id: S" + str(maxnum("sources.csv", "source_id", "S")))
print("max flag id: F" + str(maxnum("flags.csv", "flag_id", "F")))
print("max moment id: NM" + str(maxnum("notable_moments.csv", "moment_id", "NM")))
```

**As of this handoff (post-RR2020 build, 2026-09-21): next available IDs are
`S212`, `F414`, `NM88`.** These will already be out of date once your first
script runs — recompute before each subsequent script, don't just keep
counting up from these numbers by hand.

- **`wrestler_id`**: a slug of the wrestler's most-known ring name (e.g.
  `roman-reigns`). **Reused across every event they appear in — do NOT
  create a new one for a wrestler already in the database.** See §3 below,
  this is the single most important thing to get right.
- **`event_id`**: `RR<year><M|W>` — e.g. `RR2021M`, `RR2021W`. (`G` is
  reserved for Greatest-Royal-Rumble-style specials; not relevant to any of
  the 12 remaining years.)
- **`source_id`**: `S###`, sequential, never reused.
- **`flag_id`**: `F###`, sequential, never reused.
- **`moment_id`**: `NM##`, sequential, never reused.

---

## 3. Before creating ANY new wrestler_id: check if they're already in the database

This is the single most common mistake made so far in this project (it has
happened twice: RR2019 and RR2020 builds). A research pass will often assume
a famous/established wrestler "needs no fresh bio" because they're
well-known **in WWE generally** — but that's a different question from
whether they've appeared in a Royal Rumble **already built in this specific
database**. Don't trust that assumption. Check directly:

```python
import csv
candidates = ["Wrestler Name One", "Wrestler Name Two"]  # names to check
with open("data/wrestlers.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
for name in candidates:
    matches = [r["wrestler_id"] for r in rows
               if r["ring_name"].strip().lower() == name.lower()
               or name.lower() in (r.get("aliases_ring_names") or "").lower()]
    print(name, "->", matches or "NOT FOUND (genuinely new)")
```

Run this for **every entrant** in your match before writing bios, not just
ones you personally don't recognize. Only write a `new_wrestlers` row (a new
`wrestler_id`) for names that come back `NOT FOUND`.

### Minor moniker change vs. full character reinvention

If a wrestler already in the database returns under a **new ring name that's
still fundamentally the same persona** (e.g. Baron Corbin briefly becoming
"King Corbin" after winning King of the Ring 2019 — same in-ring character,
same finisher, same surname) — **reuse the existing `wrestler_id`** and just
set that entrant row's `ring_name_at_time` to the new moniker. Do not create
`king-corbin` as a separate wrestler_id.

If it's a **full character reinvention** (different gimmick, different
name, effectively a different performer identity — e.g. Diesel/Kevin Nash,
Husky Harris/Bray Wyatt) — that precedent in this database DOES split into a
separate `wrestler_id`. Use judgment; when genuinely unsure, log a flag
(`issue_type = "needs_human_judgement"`) explaining the ambiguity rather than
silently picking one.

---

## 4. The build script template — copy the structure, don't start from scratch

Use **`scripts/build_2020_men.py`** and **`scripts/build_2020_women.py`** as
your literal structural templates — copy one, rename it (e.g.
`build_2021_men.py`), and replace the content. Both are complete, current,
correctly-passing examples of every pattern below. Their structure, in
order:

1. **Module docstring**: methodology notes, any wrestler_id-reuse decisions
   and why, any "new to database" corrections, and a summary of any
   cross-validation disputes you resolved and how.
2. **`EVENT_ID`** constant (e.g. `"RR2021M"`).
3. **`sources` list**: tuples matching `SOURCES_FIELDS` order, one per
   source you actually used, with real URLs and accessed dates, sequential
   `source_id`s starting from your freshly-computed next-available number.
4. **`all_names`**: the full ordered entrant list (30 names, in entry
   order).
5. **`ENTRY_NUMBERS`** dict: name -> entry number (1-30).
6. **`survival`** dict: name -> survival time string (e.g. `"26:24"`).
7. **`ELIM_ORDER`** list + derived `elim_number` dict: elimination order
   1 through 29 (30 entrants, 1 winner, so exactly 29 eliminations —
   `validate_integrity.py` checks this arithmetic for you).
8. **`FINAL_TWO`/`FINAL_THREE`/`FINAL_FOUR`** sets.
9. **`ELIMINATORS`** dict: name -> `(eliminator_list, is_shared_bool, notes)`.
   For a genuinely shared/simultaneous elimination credited to two people,
   set `is_shared=True` and list both. For a self-elimination (see the
   Santina Marella precedent in `build_2020_women.py`), set the eliminator
   list to `[name]` itself — the entrant-construction loop handles the
   special-casing for you if you follow the same pattern.
10. **`DISPUTED_ELIM_CREDIT`** set: names where sources disagree on who gets
    credit — cross-reference with a `flags.csv` row explaining each version.
11. **`CHAMPS_AT_ENTRY`** set + **`CHAMP_INFO`** dict: any entrant who was a
    reigning champion of an actual title ON THE EVENT DATE (not before, not
    after — see `DEFINITIONS.md`'s "confirmed champion at event" rule),
    with `days_into_reign` computed from the actual title-win date.
12. **`SURPRISE_ENTRANTS`**, **`LEGENDS`**/**`NON_FULL_TIME`** sets as
    applicable.
13. **`new_wrestlers`** list: full 17-field tuples (matching
    `WRESTLERS_FIELDS`) for every genuinely-new wrestler_id, per §3 above.
    **Leave any field you can't source blank — do not guess a debut year or
    birthplace.**
14. **`reused`** dict: name-as-billed -> existing `wrestler_id`, for every
    entrant who's already in the database (this will be most of them, for
    recent years).
15. **Entrant/elimination row-construction loop**: builds one `entrants.csv`
    row and one `eliminations.csv` row per entrant, following the exact
    field order from `schema.py`. Copy this loop essentially verbatim from
    the template — the logic for `is_winner`, `is_final_two/three/four`,
    `elimination_type`, `is_self_elimination`, etc. is already correct
    there; just verify it against your own data instead of rewriting it.
16. **`flags`** list: one row per genuine data issue (disputes, corrections,
    single-source claims worth flagging, HOF/new-wrestler documentation).
    Use freshly-computed sequential `flag_id`s — see §2 above, this is
    exactly where the 2020 build's real bug happened (men's and women's
    scripts both started at the same flag number). **If you're writing both
    the Men's and Women's script for the same year, compute the Men's
    script's flag IDs, note the actual final count you used, and start the
    Women's script's flags at that max + 1 — don't just assume a round
    number.**
17. **`nm_rows`** list: notable moments (records, firsts, storyline beats,
    controversies), sequential `moment_id`s.
18. **`event_row`** dict: matches `EVENTS_FIELDS` exactly, including
    `attendance_official`/`attendance_reported` (only fill `_reported` if
    there's an actual documented dispute), `duration_status`,
    `winner_id`/`runner_up_id`, etc.
19. A final block that writes/appends all of this to the CSVs, and a print
    statement summarizing counts (X entrants, Y eliminations, Z new
    wrestlers, W flags, V notable moments) — useful for a final sanity
    check against what you intended to write.

---

## 5. The mandatory test-before-"live" protocol — do not skip or reorder this

This is non-negotiable. This exact protocol caught a real ID-collision bug
during the 2020 build before it ever touched live data — that's not a
hypothetical risk, it's what actually happened last time.

1. **Copy** `scripts/` and `data/` into an isolated working directory (NOT
   the paths you were handed as "the database" — a scratch copy).
2. Run your new build script(s) against that isolated copy.
3. Run `scripts/build_derived.py` against the isolated copy (rebuilds the
   running record/total tables).
4. Run `scripts/build_dashboard_data.py` against the isolated copy if you
   want to sanity-check the dashboard JSON too (optional for a handoff, but
   useful).
5. Run **`scripts/validate_integrity.py <isolated-data-dir> RR2021M RR2021W`**
   (substitute your actual event_ids) — this is a new, purpose-built tool
   (see §6) that checks for exactly the class of bug that's bitten this
   project before: duplicate IDs anywhere, dangling cross-references,
   invalid status values, wrong entry-number/elimination-order counts,
   more-or-less-than-one winner.
6. **Only if that passes clean**, repeat steps 2-5 identically against
   whatever you're treating as "live" — i.e. the actual database you're
   going to hand back. Do not apply an unvalidated script directly to
   what's meant to be the final result.
7. If you're building all 6 remaining years, it's fine to do them one year
   at a time through this loop (isolated test -> validate -> apply to your
   working "live" copy -> next year), as long as **each subsequent script
   recomputes its next-available IDs fresh** (§2) rather than assuming
   numbers calculated earlier in the session. Do not attempt to run all 12
   scripts against a fixed set of pre-allocated ID ranges decided in
   advance — allocate IDs at the point each script is actually finalized.

---

## 6. `scripts/validate_integrity.py` — run this, don't skip it

A new, standalone, reusable checker (not present before this handoff) that
generalizes every referential-integrity check this project has needed so
far:

```
python3 validate_integrity.py <path-to-data-dir> [event_id ...]
```

- With no `event_id` arguments: checks the *whole* database (duplicate IDs,
  dangling cross-references, invalid status values) plus per-event checks
  (entry numbers 1-N, exactly one winner, elimination order 1-(N-1)) for
  every event in `events.csv`.
- With one or more `event_id` arguments (e.g. `RR2021M RR2021W`): the
  whole-database checks still run against everything (a new build can
  collide with data that already existed), but the per-event checks are
  scoped to just the events you name — use this right after building a new
  year so you're not re-reading unrelated output every time.
- Exits non-zero if it finds anything. Treat any non-zero exit as a hard
  stop — fix the underlying data, don't patch around the checker.
- It does not modify any files — safe to run as many times as you like.

Note: it will likely report a small number of **pre-existing, unrelated**
issues from much older parts of the database (a few flags with
semicolon-joined multi-event IDs, one known old placeholder wrestler_id).
These are already known and are not yours to fix — just confirm that
whatever it reports is not newly caused by your own script (i.e., doesn't
mention your new event_ids or wrestler_ids).

---

## 7. What to send back when you're done

For each of the 12 events (or however many you complete — partial handoffs
are fine, don't hold everything until all 6 years are done if that's not
practical):

1. The finished build script(s) themselves (e.g. `build_2021_men.py`,
   `build_2021_women.py`).
2. Confirmation that `validate_integrity.py` passed clean against your
   working "live" copy after applying them, including the exact command
   and output.
3. Either the full updated `data/` directory, or just the specific rows
   your script(s) added (the build script itself is usually enough, since
   it's deterministic — but send the data too if you made any manual edits
   outside the script, e.g. an `Edit`-style fix after the fact).
4. A short note on anything you weren't sure about, anything you left
   blank, and any flags you logged — don't smooth this over, the whole
   point of the flags.csv system is to preserve disagreement rather than
   silently resolve it.

**Important**: because IDs are sequential and global, if you're producing
multiple years, do them as one continuous effort in one working copy of the
database (recomputing next-available IDs between each script, per §2)
rather than starting several years in parallel from the same starting
snapshot — otherwise you'll get exactly the kind of collision this protocol
exists to prevent, except now between two entire years' worth of work
instead of one flag. Whatever you send back will be re-validated in full
before anything is merged back into the canonical copy of the database.

---

## 8. Quick-reference: next event_ids to build, oldest first

`RR2021M`, `RR2021W`, `RR2022M`, `RR2022W`, `RR2023M`, `RR2023W`,
`RR2024M`, `RR2024W`, `RR2025M`, `RR2025W`, `RR2026M`, `RR2026W`.

(2026's Rumble already happened, in January 2026 — it's real, completed
event data to research, not a future/hypothetical one.)

Good luck — and remember, a blank cell beats a guessed one every time.
