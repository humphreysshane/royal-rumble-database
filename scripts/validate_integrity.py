#!/usr/bin/env python3
"""
Referential-integrity validator for the Royal Rumble database.

Run this against BOTH an isolated test copy (after running your new build
script(s)) AND, only if that passes clean, the live data/ directory.

    python3 validate_integrity.py <path-to-data-dir> [event_id ...]

If you pass one or more event_ids (e.g. RR2021M RR2021W), the per-event
checks (entry numbers 1-30, exactly one winner, elimination order 1-29)
run only against those events -- use this right after building a new year.
With no event_ids, it checks every event in events.csv.

The whole-database checks (duplicate IDs, dangling cross-references, bad
status values) always run against everything, since a new build can
introduce an ID collision with data that already existed.

Exits with a non-zero status if any errors are found -- treat that as a
hard stop, not a warning. This script does NOT modify any files.
"""
import csv
import os
import sys
import re

VALID_STATUS = {
    "CONFIRMED", "DERIVED", "PROBABLE", "UNCERTAIN", "CONFLICTING",
    "UNKNOWN", "N/A", "",
}

# notable_moments.csv:category vocabulary, per schema.py's comment above
# NOTABLE_MOMENTS_FIELDS. A closed-ish list -- extend both here and in
# schema.py together if a genuinely new kind of finding turns up, rather
# than letting free-text categories like "notable" (not a real category,
# just restates that the row exists) slip in uncaught.
VALID_NM_CATEGORY = {
    "record", "milestone_first", "notable_absence_or_substitution",
    "behind_the_scenes", "storyline_moment", "controversy", "botch",
    "injury_or_incident", "weapon_used", "other", "",
}

# events.csv:finish_type -- "" means an ordinary single-winner match (the
# overwhelming majority). "co_winners" is the one documented exception
# (RR1994M) and requires matching rows in event_winners.csv -- see the
# per-event winner check below and schema.py's EVENT_WINNERS_FIELDS comment.
VALID_FINISH_TYPES = {"", "co_winners"}


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_dupes(rows, key, label, errors):
    seen = {}
    for r in rows:
        v = r.get(key, "")
        if not v:
            continue
        seen[v] = seen.get(v, 0) + 1
    dupes = {k: v for k, v in seen.items() if v > 1}
    if dupes:
        errors.append(f"{label}: duplicate {key} values: {dupes}")


def split_ids(raw):
    """Split a possibly-semicolon-joined ID field (used by flags.csv's
    event_id when one flag spans several events, and by every *_ids column
    in this schema) into a clean list, ignoring blanks."""
    if not raw:
        return []
    return [p.strip() for p in raw.split(";") if p.strip()]


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_integrity.py <data-dir> [event_id ...]")
        sys.exit(2)
    data_dir = sys.argv[1]
    target_events = set(sys.argv[2:]) if len(sys.argv) > 2 else None

    wrestlers = read_csv(os.path.join(data_dir, "wrestlers.csv"))
    sources = read_csv(os.path.join(data_dir, "sources.csv"))
    flags = read_csv(os.path.join(data_dir, "flags.csv"))
    nm = read_csv(os.path.join(data_dir, "notable_moments.csv"))
    events = read_csv(os.path.join(data_dir, "events.csv"))
    entrants = read_csv(os.path.join(data_dir, "entrants.csv"))
    elims = read_csv(os.path.join(data_dir, "eliminations.csv"))
    event_winners = read_csv(os.path.join(data_dir, "event_winners.csv"))

    errors = []

    # ---- whole-database: duplicate primary IDs ----
    check_dupes(wrestlers, "wrestler_id", "wrestlers.csv", errors)
    check_dupes(sources, "source_id", "sources.csv", errors)
    check_dupes(flags, "flag_id", "flags.csv", errors)
    check_dupes(nm, "moment_id", "notable_moments.csv", errors)
    check_dupes(events, "event_id", "events.csv", errors)

    wrestler_ids = set(r["wrestler_id"] for r in wrestlers if r.get("wrestler_id"))
    event_ids_all = set(r["event_id"] for r in events if r.get("event_id"))

    # ---- whole-database: dangling cross-references ----
    for r in entrants:
        if r.get("wrestler_id") and r["wrestler_id"] not in wrestler_ids:
            errors.append(f"entrants.csv: wrestler_id {r['wrestler_id']!r} "
                           f"(event {r.get('event_id')}) not found in wrestlers.csv")
        for fld in ("eliminated_by_ids", "wrestlers_eliminated_ids"):
            for wid in split_ids(r.get(fld, "")):
                if wid not in wrestler_ids:
                    errors.append(f"entrants.csv: {fld} contains {wid!r} "
                                   f"(event {r.get('event_id')}) not found in wrestlers.csv")

    for x in elims:
        for fld in ("eliminator_wrestler_id", "eliminated_wrestler_id"):
            wid = x.get(fld, "")
            if wid and wid not in wrestler_ids:
                errors.append(f"eliminations.csv: {fld} {wid!r} (event {x.get('event_id')}) "
                               f"not found in wrestlers.csv")
        for wid in split_ids(x.get("assisting_wrestler_ids", "")):
            if wid not in wrestler_ids:
                errors.append(f"eliminations.csv: assisting_wrestler_ids contains {wid!r} "
                               f"(event {x.get('event_id')}) not found in wrestlers.csv")

    check_dupes(
        [{"key": r.get("event_id", "") + "|" + r.get("wrestler_id", "")} for r in event_winners],
        "key", "event_winners.csv", errors,
    )
    for r in event_winners:
        eid, wid = r.get("event_id", ""), r.get("wrestler_id", "")
        if eid and eid not in event_ids_all:
            errors.append(f"event_winners.csv: references unknown event_id {eid!r}")
        if wid and wid not in wrestler_ids:
            errors.append(f"event_winners.csv: references unknown wrestler_id {wid!r} "
                           f"(event {eid})")

    for r in nm:
        eid = r.get("event_id", "")
        if eid and eid not in event_ids_all:
            errors.append(f"notable_moments.csv: {r.get('moment_id')} references "
                           f"unknown event_id {eid!r}")
        for wid in split_ids(r.get("wrestler_ids_involved", "")):
            if wid not in wrestler_ids:
                errors.append(f"notable_moments.csv: {r.get('moment_id')} references "
                               f"unknown wrestler_id {wid!r}")

    for fl in flags:
        for eid in split_ids(fl.get("event_id", "")):
            if eid not in event_ids_all:
                errors.append(f"flags.csv: {fl.get('flag_id')} references "
                               f"unknown event_id {eid!r}")

    ev = {e["event_id"]: e for e in events if e.get("event_id")}
    event_winners_by_event = {}
    for r in event_winners:
        event_winners_by_event.setdefault(r.get("event_id", ""), set()).add(r.get("wrestler_id", ""))
    for eid, e in ev.items():
        for fld in ("winner_id", "runner_up_id", "first_entrant_id", "second_entrant_id",
                    "final_entrant_id", "first_elimination_id",
                    "last_elimination_before_winner_id"):
            v = e.get(fld, "")
            if v and v not in wrestler_ids:
                errors.append(f"events.csv: {eid} field {fld}={v!r} not found in wrestlers.csv")
        for fld in ("final_two_ids", "final_three_ids", "final_four_ids"):
            for wid in split_ids(e.get(fld, "")):
                if wid not in wrestler_ids:
                    errors.append(f"events.csv: {eid} field {fld} contains {wid!r} "
                                   f"not found in wrestlers.csv")

    # ---- whole-database: status vocabulary ----
    for r in entrants:
        for fld in ("entry_number_status", "elim_number_status", "ring_time_status",
                    "data_quality_status", "age_status", "physical_status",
                    "alignment_status"):
            v = r.get(fld, "")
            if v and v not in VALID_STATUS:
                errors.append(f"entrants.csv: bad {fld}={v!r} for "
                               f"{r.get('wrestler_id')} in {r.get('event_id')}")
    for e in events:
        for fld in ("duration_status", "data_quality_status"):
            v = e.get(fld, "")
            if v and v not in VALID_STATUS:
                errors.append(f"events.csv: bad {fld}={v!r} for {e.get('event_id')}")
        ft = e.get("finish_type", "")
        if ft and ft not in VALID_FINISH_TYPES:
            errors.append(f"events.csv: bad finish_type={ft!r} for {e.get('event_id')}")

    # ---- whole-database: notable_moments.csv category vocabulary ----
    for r in nm:
        v = r.get("category", "")
        if v and v not in VALID_NM_CATEGORY:
            errors.append(f"notable_moments.csv: {r.get('moment_id')} has invalid "
                           f"category={v!r} (event {r.get('event_id')})")

    # ---- per-event checks (only for target_events, or all if none given) ----
    check_events = target_events if target_events else event_ids_all
    for eid in sorted(check_events):
        ev_entrants = [e for e in entrants if e["event_id"] == eid]
        if not ev_entrants:
            errors.append(f"{eid}: no entrants.csv rows found at all")
            continue
        nums = sorted(int(e["entry_number"]) for e in ev_entrants if e.get("entry_number"))
        n = len(ev_entrants)
        # Explicit substituted_by marker plus a sourced, resolved precedent flag
        # permits one non-competing scheduled entrant to share a replacement's slot.
        # Ordinary duplicates and historical unmarked rows remain errors.
        substitutions = []
        for row in ev_entrants:
            marker = re.search(r'\[substituted_by=([a-z0-9-]+)\]', row.get('notes', ''))
            if not marker:
                continue
            replacement = [e for e in ev_entrants if e.get('wrestler_id') == marker.group(1)]
            documented = any(f.get('event_id') == eid and f.get('field') == 'documented_substitution'
                             and f.get('record_id') == row.get('wrestler_id') + ';' + marker.group(1)
                             and f.get('status') == 'resolved' and f.get('source_ids_involved') for f in flags)
            valid = (len(replacement) == 1 and replacement[0].get('entry_number') == row.get('entry_number')
                     and replacement[0].get('elim_number_status') != 'N/A'
                     and row.get('elim_number_status') == 'N/A' and row.get('is_winner') != 'TRUE'
                     and not any(row.get(k) for k in ('elim_number','ring_time','ring_time_seconds','eliminated_by_ids'))
                     and documented)
            if valid:
                substitutions.append(row)
            else:
                errors.append(f"{eid}: invalid documented substitution for {row.get('wrestler_id')}")
        for row in substitutions:
            nums.remove(int(row['entry_number']))
        expected = list(range(1, n - len(substitutions) + 1))
        if nums != expected:
            errors.append(f"{eid}: entry numbers not exactly 1-{n}: got {nums}")
        winners = [e for e in ev_entrants if e.get("is_winner") == "TRUE"]
        actual_winner_ids = set(w["wrestler_id"] for w in winners)
        finish_type = ev.get(eid, {}).get("finish_type", "")
        declared_winner_ids = event_winners_by_event.get(eid, set())
        if finish_type == "co_winners":
            if len(winners) < 2:
                errors.append(f"{eid}: finish_type=co_winners but only "
                               f"{len(winners)} entrant(s) marked is_winner=TRUE")
            if not declared_winner_ids:
                errors.append(f"{eid}: finish_type=co_winners but no rows "
                               f"in event_winners.csv")
            elif declared_winner_ids != actual_winner_ids:
                errors.append(f"{eid}: event_winners.csv winner set "
                               f"{sorted(declared_winner_ids)} doesn't match "
                               f"entrants.csv is_winner=TRUE set {sorted(actual_winner_ids)}")
        else:
            if len(winners) != 1:
                errors.append(f"{eid}: expected exactly 1 winner, got {len(winners)}")
            if declared_winner_ids:
                errors.append(f"{eid}: has event_winners.csv row(s) but "
                               f"finish_type is not 'co_winners'")

        # A "no-show" entrant occupies an entry slot (entry_number) but never
        # actually entered the match, so there is no elimination event for
        # them at all -- this is a real, sourced situation (e.g. Randy Savage
        # RR1991M, Scotty 2 Hotty RR2005M, Rey Mysterio RR2023M), not a data
        # gap. The established convention for this is: elim_number left
        # blank with elim_number_status == "N/A" specifically (N/A means "this
        # field doesn't apply", distinct from "UNKNOWN" which means "a real
        # gap, still expected to exist"). Detect these and shrink the
        # expected elimination count accordingly, instead of assuming every
        # non-winner entrant has exactly one elimination row.
        no_shows = [e for e in ev_entrants if e.get("is_winner") != "TRUE"
                    and e.get("elim_number_status") == "N/A"]
        no_show_ids = set(e["wrestler_id"] for e in no_shows)

        ev_elims = [x for x in elims if x["event_id"] == eid]
        unique_orders = sorted(set(int(x["order_in_match"]) for x in ev_elims
                                    if x.get("order_in_match")))
        # Ordinary matches have one winner; the 1994 match has two documented
        # co-winners.  Every winner is, by definition, not eliminated.
        expected_elim_count = n - len(winners) - len(no_shows)
        expected_orders = list(range(1, expected_elim_count + 1))
        if unique_orders != expected_orders:
            errors.append(f"{eid}: elimination order_in_match not exactly "
                           f"1-{expected_elim_count} (n={n} entrants, "
                           f"{len(no_shows)} documented no-show(s)): got {unique_orders}")

        # A documented no-show must not also have an eliminations.csv row --
        # that would directly contradict "never entered the match".
        for wid in no_show_ids:
            stray = [x for x in ev_elims if x.get("eliminated_wrestler_id") == wid]
            if stray:
                errors.append(f"{eid}: {wid} has elim_number_status=N/A (documented "
                               f"no-show) but also has {len(stray)} eliminations.csv "
                               f"row(s) for them -- contradiction, pick one")

    if errors:
        print(f"ERRORS FOUND ({len(errors)}):")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    else:
        scope = f"events {sorted(check_events)}" if target_events else "the whole database"
        print(f"ALL CHECKS PASSED ({scope}).")
        sys.exit(0)


if __name__ == "__main__":
    main()
