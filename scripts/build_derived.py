# -*- coding: utf-8 -*-
"""
Recomputes every DERIVED table from the base tables. Re-run this after
adding any new event. Two kinds of output:

  OVERWRITTEN each run (pure snapshot of current state, safe to regenerate):
    career_stats.csv, entry_number_stats.csv, records.csv, event_dynamic_stats.csv,
    elimination_rivalries.csv, ring_occupancy_stats.csv

  APPENDED to, never overwritten (this IS the point -- a running ledger that
  grows as more Rumbles are added, per Shane's "I need the overall record
  holder running total being tracked after each royal rumble" request):
    records_history.csv -- every time a record category's leader or value
    changes between one run and the next, a new row is logged here. Nothing
    in this file is ever deleted or rewritten; it's the history of the
    record book itself, not just its current state.

Every value here is DERIVED per DEFINITIONS.md. A record that depends on an
UNKNOWN/CONFLICTING base field (e.g. Boris Zhukov's weight, his DOB) simply
excludes that entrant from the relevant leaderboard rather than guessing --
see the exclusion notes printed at the end of this script's output.

DIVISION SPLIT (2026-09-20): per Shane's instruction "I think I want all of
the woman's stats and info completely separate to the man's", every one of
these derived tables is computed independently per division (Men's Royal
Rumble vs Women's Royal Rumble), never blended. Division is read straight
off events.csv:match_type for the event a row belongs to. wrestlers.csv
itself stays a single shared identity table -- a performer who has wrestled
in both divisions (e.g. Beth Phoenix, in the Men's 2010 Rumble and the
Women's 2018 Rumble) keeps ONE wrestler_id, but gets two fully independent
rows/leaderboard appearances below, one per division, never a blended
combined line. See IDEAS.md for the full write-up of this change.
"""
import csv
import os
import re
import sys
import datetime
import statistics
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(__file__))
from schema import DERIVED_TABLES

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DERIVED_DIR = os.path.join(DATA_DIR, "derived")
os.makedirs(DERIVED_DIR, exist_ok=True)
TODAY = datetime.date.today().isoformat()


def load(name, folder=DATA_DIR):
    path = os.path.join(folder, name)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(name, fieldnames, rows, folder=DERIVED_DIR):
    with open(os.path.join(folder, name), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_age_years(s):
    """'30 Years, 6 Months' -> 30.5. Returns None if unparseable/blank."""
    if not s:
        return None
    m = re.search(r"(\d+)\s*Years?", s)
    if not m:
        return None
    years = int(m.group(1))
    mo = re.search(r"(\d+)\s*Months?", s)
    months = int(mo.group(1)) if mo else 0
    return round(years + months / 12, 2)


def seconds_to_mmss(seconds):
    if seconds is None:
        return ""
    return f"{seconds // 60}:{seconds % 60:02d}"


entrants = load("entrants.csv")
events = {e["event_id"]: e for e in load("events.csv")}
wrestlers = {w["wrestler_id"]: w for w in load("wrestlers.csv")}
eliminations = load("eliminations.csv")
entrances = load("entrances.csv")

if not entrants:
    print("No entrant data yet -- run a build_<year>.py script first.")
    sys.exit(0)


def division_of(event_id):
    return events[event_id]["match_type"]


DIVISIONS = sorted(set(division_of(eid) for eid in events))

# ---------------------------------------------------------------------------
# career_stats.csv  (this table itself IS Shane's "running total per
# wrestler" -- every time a new event is added and this script re-run, every
# wrestler's row reflects their full cumulative history to date, e.g. Bret
# Hart's total_eliminations_made grows the next time he appears and
# eliminates someone). Grouped by (wrestler_id, division) so a performer who
# has appeared in both divisions (e.g. Beth Phoenix) gets two fully separate
# rows rather than one blended row.
# ---------------------------------------------------------------------------
by_wrestler_div = defaultdict(list)
for e in entrants:
    by_wrestler_div[(e["wrestler_id"], division_of(e["event_id"]))].append(e)

career_rows = []
for (wid, division), apps in sorted(by_wrestler_div.items()):
    years = sorted(int(events[a["event_id"]]["event_date"][:4]) for a in apps)
    wins = sum(1 for a in apps if a["is_winner"] == "TRUE")
    ru = sum(1 for a in apps if a["is_runner_up"] == "TRUE")
    f4 = sum(1 for a in apps if a["is_final_four"] == "TRUE")
    f3 = sum(1 for a in apps if a["is_final_three"] == "TRUE")
    f2 = sum(1 for a in apps if a["is_final_two"] == "TRUE")
    total_elims = sum(int(a["wrestlers_eliminated_count"] or 0) for a in apps)
    max_elims = max((int(a["wrestlers_eliminated_count"] or 0) for a in apps), default=0)
    ring_times = [int(a["ring_time_seconds"]) for a in apps if a["ring_time_seconds"]]
    entry_nums = [int(a["entry_number"]) for a in apps if a["entry_number"]]
    eliminators = Counter()
    eliminated_others = Counter()
    for a in apps:
        for e_id in (a["eliminated_by_ids"] or "").split(";"):
            if e_id:
                eliminators[e_id] += 1
        for v_id in (a["wrestlers_eliminated_ids"] or "").split(";"):
            if v_id:
                eliminated_others[v_id] += 1

    # consecutive-year streak (longest run of back-to-back years appeared,
    # within this division only)
    streak = longest = 1 if years else 0
    for i in range(1, len(years)):
        streak = streak + 1 if years[i] == years[i - 1] + 1 else 1
        longest = max(longest, streak)

    career_rows.append({
        "wrestler_id": wid,
        "division": division,
        "total_appearances": len(apps),
        "first_rumble_year": min(years) if years else "",
        "last_rumble_year": max(years) if years else "",
        "wins": wins, "runner_up_finishes": ru,
        "final_four_count": f4, "final_three_count": f3, "final_two_count": f2,
        "total_eliminations_made": total_elims,
        "avg_eliminations_per_appearance": round(total_elims / len(apps), 2) if apps else "",
        "max_eliminations_single_rumble": max_elims,
        "total_ring_time_seconds": sum(ring_times) if ring_times else "",
        "avg_ring_time_seconds": round(sum(ring_times) / len(ring_times), 1) if ring_times else "",
        "longest_single_appearance_seconds": max(ring_times) if ring_times else "",
        "shortest_single_appearance_seconds": min(ring_times) if ring_times else "",
        "avg_entry_number": round(sum(entry_nums) / len(entry_nums), 2) if entry_nums else "",
        "highest_entry_number": max(entry_nums) if entry_nums else "",
        "lowest_entry_number": min(entry_nums) if entry_nums else "",
        "times_entered_number_1": sum(1 for n in entry_nums if n == 1),
        "times_entered_number_2": sum(1 for n in entry_nums if n == 2),
        "times_entered_final_number": sum(
            1 for a in apps if a["entry_number"] and a["wrestler_id"] == events[a["event_id"]].get("final_entrant_id")
        ),
        "elimination_percentage": round(100 * sum(1 for a in apps if a["elim_number"]) / len(apps), 1) if apps else "",
        "win_percentage": round(100 * wins / len(apps), 1) if apps else "",
        "final_four_percentage": round(100 * f4 / len(apps), 1) if apps else "",
        "longest_consecutive_streak": longest,
        "longest_gap_years": (max(years) - min(years) - (len(set(years)) - 1)) if len(years) > 1 else 0,
        "distinct_eliminators_count": len(eliminators),
        "most_frequent_eliminator_id": eliminators.most_common(1)[0][0] if eliminators else "",
        "distinct_wrestlers_eliminated_count": len(eliminated_others),
        "most_frequently_eliminated_id": eliminated_others.most_common(1)[0][0] if eliminated_others else "",
        "most_frequent_tag_partner_id": "",  # needs cross-year tag_teams.csv join; TODO once more events exist
        "best_finish": "Winner" if wins else ("Runner-up" if ru else ("Final Four" if f4 else "")),
    })

write("career_stats.csv", DERIVED_TABLES["career_stats.csv"], career_rows)

# ---------------------------------------------------------------------------
# entry_number_stats.csv -- grouped by (division, entry_number)
# ---------------------------------------------------------------------------
by_entry_div = defaultdict(list)
for e in entrants:
    if e["entry_number"]:
        by_entry_div[(division_of(e["event_id"]), int(e["entry_number"]))].append(e)

entry_rows = []
for (division, n), apps in sorted(by_entry_div.items()):
    wins = sum(1 for a in apps if a["is_winner"] == "TRUE")
    ru = sum(1 for a in apps if a["is_runner_up"] == "TRUE")
    f4 = sum(1 for a in apps if a["is_final_four"] == "TRUE")
    times = sorted(int(a["ring_time_seconds"]) for a in apps if a["ring_time_seconds"])
    elims = [int(a["wrestlers_eliminated_count"] or 0) for a in apps]
    entry_rows.append({
        "division": division, "entry_number": n, "events_sample_size": len(apps),
        "wins": wins, "win_rate": round(100 * wins / len(apps), 1) if apps else "",
        "avg_survival_seconds": round(sum(times) / len(times), 1) if times else "",
        "median_survival_seconds": times[len(times) // 2] if times else "",
        "avg_eliminations": round(sum(elims) / len(elims), 2) if elims else "",
        "final_four_rate": round(100 * f4 / len(apps), 1) if apps else "",
        "runner_up_count": ru,
    })

write("entry_number_stats.csv", DERIVED_TABLES["entry_number_stats.csv"], entry_rows)

# ---------------------------------------------------------------------------
# entry_number_bands.csv -- coarser "value slice" view of the same
# entry_number_stats.csv data (per Shane's "win rate by #1 vs #2, first-5 vs
# middle vs last-5" request, 2026-09-26). Zero new research: this is purely
# a re-bucketing of by_entry_div (built above for entry_number_stats.csv).
# "Last-5" is defined relative to each division's own observed maximum entry
# number (not hardcoded to 30), since Men's and Women's fields -- and any
# future non-standard-size Rumble -- aren't guaranteed to be the same size.
# ---------------------------------------------------------------------------
band_rows = []
for division in DIVISIONS:
    div_max_entry = max((n for (d, n) in by_entry_div if d == division), default=None)
    if div_max_entry is None or div_max_entry < 10:
        continue  # too few distinct entry numbers observed for bands to mean anything
    bands = [
        ("#1", (1, 1)),
        ("#2", (2, 2)),
        ("First 5 (1-5)", (1, 5)),
        ("Last 5", (div_max_entry - 4, div_max_entry)),
        ("Middle", (6, div_max_entry - 5)),
    ]
    for band_label, (lo, hi) in bands:
        if lo > hi:
            continue  # e.g. "Middle" collapses to nothing on a very small field
        apps = []
        for (d, n), a_list in by_entry_div.items():
            if d == division and lo <= n <= hi:
                apps.extend(a_list)
        if not apps:
            continue
        wins = sum(1 for a in apps if a["is_winner"] == "TRUE")
        ru = sum(1 for a in apps if a["is_runner_up"] == "TRUE")
        f4 = sum(1 for a in apps if a["is_final_four"] == "TRUE")
        times = [int(a["ring_time_seconds"]) for a in apps if a["ring_time_seconds"]]
        elims = [int(a["wrestlers_eliminated_count"] or 0) for a in apps]
        band_rows.append({
            "division": division, "band": band_label, "band_range": f"{lo}-{hi}" if lo != hi else str(lo),
            "events_sample_size": len(apps),
            "wins": wins, "win_rate": round(100 * wins / len(apps), 1),
            "avg_survival_seconds": round(sum(times) / len(times), 1) if times else "",
            "avg_eliminations": round(sum(elims) / len(elims), 2) if elims else "",
            "final_four_rate": round(100 * f4 / len(apps), 1),
            "runner_up_count": ru,
            "notes": f"This division's observed entry-number range tops out at #{div_max_entry}; "
                     f"'Last 5' = #{div_max_entry-4}-#{div_max_entry}, 'Middle' = everything else.",
        })

write("entry_number_bands.csv", DERIVED_TABLES["entry_number_bands.csv"], band_rows)

# ---------------------------------------------------------------------------
# elimination_rivalries.csv -- pairwise, across ALL processed events WITHIN
# each division (a Men's-Rumble eliminator/eliminated pairing never merges
# with a Women's-Rumble one, even where the two wrestler_ids happen to match
# -- e.g. Beth Phoenix's Men's-Rumble eliminations vs her Women's-Rumble
# ones are two entirely separate pairing histories).
# ---------------------------------------------------------------------------
pair_counts = Counter()
pair_first = {}
pair_last = {}
for r in eliminations:
    if not all((r["eliminator_wrestler_id"], r["eliminated_wrestler_id"])):
        continue
    division = division_of(r["event_id"])
    key = (division, r["eliminator_wrestler_id"], r["eliminated_wrestler_id"])
    pair_counts[key] += 1
    ev_date = events[r["event_id"]]["event_date"]
    if key not in pair_first or ev_date < pair_first[key][1]:
        pair_first[key] = (r["event_id"], ev_date)
    if key not in pair_last or ev_date > pair_last[key][1]:
        pair_last[key] = (r["event_id"], ev_date)

rivalry_rows = [
    {
        "division": k[0], "eliminator_wrestler_id": k[1], "eliminated_wrestler_id": k[2],
        "times_eliminated": v,
        "first_event_id": pair_first[k][0], "most_recent_event_id": pair_last[k][0],
    }
    for k, v in sorted(pair_counts.items(), key=lambda kv: -kv[1])
]
write("elimination_rivalries.csv", DERIVED_TABLES["elimination_rivalries.csv"], rivalry_rows)

# ---------------------------------------------------------------------------
# event_dynamic_stats.csv -- stats that change as TIME passes even though
# the event itself is in the past (deaths, HOF inductions since). Computed
# fresh against TODAY every run, never hand-edited. Already one row per
# event, so the division split here is just an added column for filtering.
# ---------------------------------------------------------------------------
dyn_rows = []
for eid, ev in sorted(events.items()):
    field = [e for e in entrants if e["event_id"] == eid]
    hof_at_time = sum(1 for e in field if e.get("was_hof_member_at_time") == "TRUE")
    hof_eventually = sum(1 for e in field if wrestlers.get(e["wrestler_id"], {}).get("hall_of_fame_year"))
    now_deceased = sum(1 for e in field if wrestlers.get(e["wrestler_id"], {}).get("deceased_date"))
    weights = [float(e["billed_weight_kg_at_event"]) for e in field if e["billed_weight_kg_at_event"]]
    ff_ids = (ev.get("final_four_ids") or "").split(";")
    ff_ages = [parse_age_years(e["age_at_event"]) for e in field if e["wrestler_id"] in ff_ids and e.get("age_status") != "UNKNOWN"]
    ff_ages = [a for a in ff_ages if a is not None]
    dyn_rows.append({
        "event_id": eid, "division": ev["match_type"], "as_of_date": TODAY,
        "hof_members_at_time_count": hof_at_time,
        "hof_members_eventually_count": hof_eventually,
        "now_deceased_count": now_deceased,
        "future_world_champions_count": "",
        "combined_billed_weight_kg": round(sum(weights), 1) if weights else "",
        "combined_age_final_four_years": round(sum(ff_ages), 1) if ff_ages else "",
        "notes": "now_deceased_count and hof_members_eventually_count are moving targets -- recomputed vs today's date each run, not fixed at event time. Future world champions count is blank because no world-title-history table exists; see IDEAS.md.",
    })
write("event_dynamic_stats.csv", DERIVED_TABLES["event_dynamic_stats.csv"], dyn_rows)

# ---------------------------------------------------------------------------
# event_field_physical_stats.csv -- combined and average billed physical
# profile for each actual field. A metric is populated only when every
# actual entrant has that appearance-specific value. No-show rows are
# excluded with the same winner-safe convention as ring occupancy.
# ---------------------------------------------------------------------------
field_physical_rows = []
for eid, ev in sorted(events.items(), key=lambda kv: kv[1].get("event_date") or kv[0]):
    field = [e for e in entrants if e["event_id"] == eid]
    actual = [e for e in field
              if e.get("is_winner") == "TRUE"
              or (e.get("elim_number_status") != "N/A" and e.get("ring_time_seconds") != "0")]
    weights = []
    heights = []
    for e in actual:
        try:
            weight = float((e.get("billed_weight_kg_at_event") or "").strip())
            if weight > 0:
                weights.append(weight)
        except (TypeError, ValueError):
            pass
        try:
            height = float((e.get("billed_height_m_at_event") or "").strip())
            if height > 0:
                heights.append(height)
        except (TypeError, ValueError):
            pass

    actual_count = len(actual)
    weight_complete = bool(actual_count) and len(weights) == actual_count
    height_complete = bool(actual_count) and len(heights) == actual_count
    field_physical_rows.append({
        "event_id": eid,
        "division": ev["match_type"],
        "actual_entrant_count": actual_count,
        "billed_weight_count": len(weights),
        "weight_coverage_percentage": round(100 * len(weights) / actual_count, 1) if actual_count else 0,
        "combined_billed_weight_kg": round(sum(weights), 1) if weight_complete else "",
        "average_billed_weight_kg": round(sum(weights) / actual_count, 1) if weight_complete else "",
        "billed_height_count": len(heights),
        "height_coverage_percentage": round(100 * len(heights) / actual_count, 1) if actual_count else 0,
        "combined_billed_height_m": round(sum(heights), 2) if height_complete else "",
        "average_billed_height_m": round(sum(heights) / actual_count, 3) if height_complete else "",
        "data_quality_status": "DERIVED",
        "notes": ("Actual entrants only; genuine no-shows are excluded and winners retained. Combined and average "
                  "values are blank unless every actual entrant has the relevant appearance-specific field."),
    })
write("event_field_physical_stats.csv", DERIVED_TABLES["event_field_physical_stats.csv"], field_physical_rows)

# ---------------------------------------------------------------------------
# event_nationality_breakdown.csv -- one row per (event, nationality) actually
# represented in that event's field. Compound values remain intact and the
# known-nationality percentage is kept separate from whole-field coverage.
# ---------------------------------------------------------------------------
nationality_rows = []
for eid, ev in sorted(events.items(), key=lambda kv: kv[1].get("event_date") or kv[0]):
    field = [e for e in entrants if e["event_id"] == eid]
    actual = [e for e in field
              if e.get("is_winner") == "TRUE"
              or (e.get("elim_number_status") != "N/A" and e.get("ring_time_seconds") != "0")]
    actual_count = len(actual)
    known = []
    for e in actual:
        w = wrestlers.get(e["wrestler_id"])
        nat = (w.get("nationality") or "").strip() if w else ""
        if nat:
            known.append(nat)
    counts = Counter(known)
    known_count = len(known)
    coverage_pct = round(100 * known_count / actual_count, 1) if actual_count else 0
    if not counts:
        nationality_rows.append({
            "event_id": eid, "division": ev["match_type"], "nationality": "",
            "entrant_count": 0, "percentage_of_known": "",
            "known_nationality_count": 0, "actual_entrant_count": actual_count,
            "coverage_percentage": coverage_pct, "data_quality_status": "DERIVED",
            "notes": "No entrant in this field has a recorded nationality yet.",
        })
        continue
    for nat, cnt in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        nationality_rows.append({
            "event_id": eid, "division": ev["match_type"], "nationality": nat,
            "entrant_count": cnt,
            "percentage_of_known": round(100 * cnt / known_count, 1),
            "known_nationality_count": known_count, "actual_entrant_count": actual_count,
            "coverage_percentage": coverage_pct, "data_quality_status": "DERIVED",
            "notes": ("Percentage is of entrants with a known nationality, not of the full field "
                      "-- see coverage_percentage.") if coverage_pct < 100 else "",
        })
write("event_nationality_breakdown.csv", DERIVED_TABLES["event_nationality_breakdown.csv"], nationality_rows)

# ---------------------------------------------------------------------------
# ring_occupancy_stats.csv -- peak number of legal entrants simultaneously
# active in the ring, reconstructed only where the existing timing data is
# complete enough to do so without assumptions. Each entrant interval is
# [entry, exit): exits are processed before entries at the same recorded
# second, avoiding a false overlap where the one-second source resolution
# cannot establish that two wrestlers were legally active together.
#
# Entry time is derived from elimination_clock_seconds - ring_time_seconds.
# The winner's exit is the match end, represented by the final recorded
# elimination clock; the winner's entry time is derived from that endpoint.
# No entry interval is assumed, and incomplete events remain absent rather
# than receiving a plausible-looking estimate.
#
# NOTE (fixed 2026-09-23 during independent verification of the Phase A
# submission): a match winner's elim_number_status is legitimately "N/A"
# (they were never eliminated, so the field doesn't apply) -- the SAME
# literal value used to mark a genuine no-show (drew a number, never
# entered). The originally submitted filter here excluded ALL "N/A" rows,
# which silently dropped the winner from every event's occupancy count
# (verified: winner absent from all 12 submitted wrestler_ids_at_peak
# lists). This codebase's established convention for this exact ambiguity
# (already used in validate_integrity.py's no-show detection) is to guard
# with is_winner != "TRUE"; applied below.
# ---------------------------------------------------------------------------
occupancy_rows = []
crowdedness_rows = []
physical_peak_rows = []
entrance_by_event_wrestler = {(r["event_id"], r["wrestler_id"]): r for r in entrances}


def timeline_seconds(value):
    parts = (value or "").strip().split(":")
    if not parts or any(not p.isdigit() for p in parts):
        return None
    numbers = [int(p) for p in parts]
    if len(numbers) == 2:
        return numbers[0] * 60 + numbers[1]
    if len(numbers) == 3:
        return numbers[0] * 3600 + numbers[1] * 60 + numbers[2]
    return None


for eid, ev in sorted(events.items(), key=lambda kv: kv[1].get("event_date") or kv[0]):
    field = [e for e in entrants if e["event_id"] == eid]
    actual = [e for e in field
              if e.get("is_winner") == "TRUE"
              or (e.get("elim_number_status") != "N/A" and e.get("ring_time_seconds") != "0")]
    loser_ends = [int(e["elimination_clock_seconds"]) for e in actual
                  if e.get("elimination_clock_seconds")]
    match_end = max(loser_ends) if loser_ends else None
    intervals = []
    derived_starts = []
    for e in actual:
        if e.get("ring_time_seconds") in (None, ""):
            continue
        ring_seconds = int(e["ring_time_seconds"])
        if e.get("elimination_clock_seconds"):
            end = int(e["elimination_clock_seconds"])
        elif e.get("is_winner") == "TRUE" and match_end is not None:
            end = match_end
        else:
            continue
        start = end - ring_seconds
        if start < 0 or end <= start:
            continue
        intervals.append((start, end, e["wrestler_id"]))
        derived_starts.append(start)

    eligible_count = len(actual)
    coverage = round(100 * len(intervals) / eligible_count, 1) if eligible_count else 0
    # Several early legacy rows store the entrant's survival duration in
    # elimination_clock_seconds as well as ring_time_seconds. Those values
    # are valid durations, but not a global match clock: subtracting them
    # makes every entrant appear to enter at 0:00. Require a genuinely
    # distributed set of reconstructed entry times before treating an event
    # as a replayable timeline.
    has_global_clock = (
        len([s for s in derived_starts if s > 0]) >= max(1, eligible_count // 2)
        and len(set(derived_starts)) >= max(2, eligible_count // 2)
    )
    timeline_method = "elimination_clock_minus_ring_time"
    if eligible_count and (len(intervals) != eligible_count or not has_global_clock):
        # Fallback: entrances.csv already contains sourced physical ring-entry
        # timestamps for many events. Ring time is measured from physical entry
        # to exit, so entry + ring time gives the same legal-activity interval
        # directly. The first two entrants start at match time 0 by definition.
        # Reject incomplete rows and source-video timestamps beyond the event's
        # recorded duration rather than forcing a timeline through a cut.
        entrance_intervals = []
        match_duration = timeline_seconds(ev.get("duration_total"))
        for e in actual:
            if e.get("ring_time_seconds") in (None, ""):
                continue
            entry_number = int(e["entry_number"]) if (e.get("entry_number") or "").isdigit() else None
            if entry_number in (1, 2):
                start = 0
            else:
                timing = entrance_by_event_wrestler.get((eid, e["wrestler_id"]), {})
                start = timeline_seconds(timing.get("enters_ring_ts"))
            if start is None or (match_duration is not None and start > match_duration):
                continue
            end = start + int(e["ring_time_seconds"])
            if end <= start:
                continue
            entrance_intervals.append((start, end, e["wrestler_id"]))
        if len(entrance_intervals) == eligible_count:
            intervals = entrance_intervals
            derived_starts = [start for start, _, _ in intervals]
            has_global_clock = True
            timeline_method = "sourced_physical_entry_plus_ring_time"

    if not eligible_count or len(intervals) != eligible_count or not has_global_clock:
        continue

    # The fallback above may replace the original interval set. Report coverage
    # for the intervals actually used, not the discarded first attempt.
    coverage = round(100 * len(intervals) / eligible_count, 1) if eligible_count else 0

    starts = defaultdict(list)
    ends = defaultdict(list)
    for start, end, wid in intervals:
        starts[start].append(wid)
        ends[end].append(wid)
    times = sorted(set(starts) | set(ends))
    active = set()
    peak = 0
    peak_start = peak_end = None
    peak_ids = []
    time_at_count = defaultdict(int)
    for idx, t in enumerate(times[:-1]):
        for wid in ends.get(t, []):
            active.discard(wid)
        for wid in starts.get(t, []):
            active.add(wid)
        next_t = times[idx + 1]
        if next_t <= t:
            continue
        time_at_count[len(active)] += next_t - t
        if len(active) > peak:
            peak = len(active)
            peak_start, peak_end = t, next_t
            peak_ids = sorted(active)

    if not peak:
        continue
    occupancy_rows.append({
        "event_id": eid,
        "division": ev["match_type"],
        "peak_in_ring_count": peak,
        "peak_start_seconds": peak_start,
        "peak_end_seconds": peak_end,
        "peak_start_time": seconds_to_mmss(peak_start),
        "peak_end_time": seconds_to_mmss(peak_end),
        "wrestler_ids_at_peak": ";".join(peak_ids),
        "timed_entrant_count": len(intervals),
        "eligible_entrant_count": eligible_count,
        "coverage_percentage": coverage,
        "data_quality_status": "DERIVED",
        "notes": ("Complete-timeline events only. Timeline method: " + timeline_method + ". "
                  "Uses sourced ring-time/clock fields, half-open intervals, and no assumed entry-gap timing."),
    })

    # Ring Crowdedness: full breakdown of match time spent at each
    # simultaneous in-ring count (not just the peak), matching Cageside
    # Seats' "Ring Crowdedness" stat format (e.g. "7 wrestlers: 15m 14s,
    # 25.9%"). Reuses the exact same reconstructed timeline as the peak
    # computation above -- same gating, same intervals, same half-open
    # convention -- so it only ever exists for events that already qualify
    # for ring_occupancy_stats.csv, and can never disagree with the peak
    # row for the same event. No new sourcing: purely a derived-layer
    # extension of data already being computed. Per-event percentage is of
    # this event's own total *measured* match time (the sum of all counted
    # segments), not a fixed match-length assumption.
    total_match_seconds = sum(time_at_count.values())
    for count in sorted(time_at_count):
        secs = time_at_count[count]
        crowdedness_rows.append({
            "event_id": eid,
            "division": ev["match_type"],
            "in_ring_count": count,
            "seconds_at_count": secs,
            "time_at_count": seconds_to_mmss(secs),
            "percentage_of_match_time": round(100 * secs / total_match_seconds, 1) if total_match_seconds else "",
            "total_match_seconds": total_match_seconds,
            "data_quality_status": "DERIVED",
            "notes": ("Complete-timeline events only -- same reconstructed timeline as "
                      "ring_occupancy_stats.csv for this event. Percentage is of this event's own "
                      "total measured match time, not a fixed assumed match length."),
        })

    # Combined physical peaks reuse the exact same complete occupancy
    # timeline. A metric is emitted only when every actual entrant in the
    # event has that appearance-specific physical field populated, so a
    # missing lightweight/short entrant cannot create a plausible-looking
    # but understated record.
    entrant_by_id = {e["wrestler_id"]: e for e in actual}
    for metric, field_name, unit, precision in (
        ("combined_billed_weight", "billed_weight_kg_at_event", "kg", 1),
        ("combined_billed_height", "billed_height_m_at_event", "m", 2),
    ):
        values = {}
        for wid in entrant_by_id:
            raw = (entrant_by_id[wid].get(field_name) or "").strip()
            try:
                value = float(raw)
            except (TypeError, ValueError):
                continue
            if value > 0:
                values[wid] = value
        profile_coverage = round(100 * len(values) / eligible_count, 1) if eligible_count else 0
        if len(values) != eligible_count:
            continue

        active = set()
        peak_value = 0.0
        metric_start = metric_end = None
        metric_ids = []
        for idx, t in enumerate(times[:-1]):
            for wid in ends.get(t, []):
                active.discard(wid)
            for wid in starts.get(t, []):
                active.add(wid)
            next_t = times[idx + 1]
            if next_t <= t:
                continue
            # Iterate in a fixed order (not raw set order, which is
            # PYTHONHASHSEED-dependent) so floating-point summation order --
            # and therefore which of several near-tied windows wins -- is
            # reproducible from run to run, not a coin flip per process.
            combined = sum(values[wid] for wid in sorted(active))
            if combined > peak_value:
                peak_value = combined
                metric_start, metric_end = t, next_t
                metric_ids = sorted(active)

        if peak_value:
            physical_peak_rows.append({
                "event_id": eid,
                "division": ev["match_type"],
                "metric": metric,
                "peak_value": round(peak_value, precision),
                "unit": unit,
                "peak_start_seconds": metric_start,
                "peak_end_seconds": metric_end,
                "peak_start_time": seconds_to_mmss(metric_start),
                "peak_end_time": seconds_to_mmss(metric_end),
                "wrestler_ids_at_peak": ";".join(metric_ids),
                "timed_entrant_count": len(intervals),
                "eligible_entrant_count": eligible_count,
                "profiled_entrant_count": len(values),
                "profile_coverage_percentage": profile_coverage,
                "data_quality_status": "DERIVED",
                "notes": ("Complete-timeline and complete appearance-specific physical-profile events only. "
                          "Uses the same half-open intervals as ring_occupancy_stats.csv; no missing physical "
                          "value is estimated."),
            })
write("ring_occupancy_stats.csv", DERIVED_TABLES["ring_occupancy_stats.csv"], occupancy_rows)
write("ring_crowdedness.csv", DERIVED_TABLES["ring_crowdedness.csv"], crowdedness_rows)
write("ring_physical_peaks.csv", DERIVED_TABLES["ring_physical_peaks.csv"], physical_peak_rows)

# ---------------------------------------------------------------------------
# entrance_event_stats.csv -- event-level summaries of the sourced entrance
# timing rows. Duration statistics use the explicit duration field, so they
# remain valid even when a source article's absolute video clock has a cut or
# discontinuity. Absolute "entered ring" timestamps are accepted only when
# they fall within the event's recorded match duration. Buzzer-gap comparisons
# require consecutive entry numbers and discard gaps over five minutes, which
# are source-video clock discontinuities rather than a real advertised-entry
# interval (the known examples are RR2008M's late-match source timestamps).
# ---------------------------------------------------------------------------
def clock_to_seconds(value):
    if not value:
        return None
    try:
        parts = [int(part) for part in value.split(":")]
    except ValueError:
        return None
    total = 0
    for part in parts:
        total = total * 60 + part
    return total


def duration_label(value):
    if value is None:
        return ""
    if float(value).is_integer():
        return seconds_to_mmss(int(value))
    minutes = int(value) // 60
    seconds = value - minutes * 60
    return f"{minutes}:{seconds:04.1f}"


entrances_by_event = defaultdict(list)
for row in entrances:
    entrances_by_event[row["event_id"]].append(row)

entrance_event_rows = []
for eid, ev in sorted(events.items(), key=lambda kv: kv[1].get("event_date") or kv[0]):
    rows = entrances_by_event.get(eid, [])
    if not rows:
        continue
    durations = [int(r["entrance_duration_seconds"]) for r in rows
                 if r.get("entrance_duration_seconds") not in (None, "")]
    match_seconds = clock_to_seconds(ev.get("duration_total"))
    valid_physical_entries = []
    excluded_absolute = 0
    for r in rows:
        entered = clock_to_seconds(r.get("enters_ring_ts"))
        if entered is None:
            continue
        if match_seconds is not None and entered <= match_seconds:
            valid_physical_entries.append((entered, r))
        else:
            excluded_absolute += 1

    advertised = int(ev["entry_interval_seconds"]) if (ev.get("entry_interval_seconds") or "").isdigit() else None
    numbered = {int(r["entry_number"]): r for r in rows
                if (r.get("entry_number") or "").isdigit() and r.get("countdown_ts")}
    intervals = []
    excluded_intervals = 0
    if advertised is not None:
        for entry_number, r in numbered.items():
            previous = numbered.get(entry_number - 1)
            if previous is None:
                continue
            current_seconds = clock_to_seconds(r.get("countdown_ts"))
            previous_seconds = clock_to_seconds(previous.get("countdown_ts"))
            gap = current_seconds - previous_seconds
            if 0 <= gap <= 300:
                intervals.append((gap, gap - advertised, r))
            else:
                excluded_intervals += 1

    latest = max(valid_physical_entries, key=lambda item: item[0]) if valid_physical_entries else None
    largest_variance = max(intervals, key=lambda item: abs(item[1])) if intervals else None
    notes = [
        "DERIVED from entrances.csv; no new factual claims or inferred timestamps.",
        f"Entrance duration coverage: {len(durations)} of {len(rows)} entrance rows.",
    ]
    if excluded_absolute:
        notes.append(f"Excluded {excluded_absolute} absolute enters-ring timestamp(s) beyond the recorded match duration.")
    if excluded_intervals:
        notes.append(f"Excluded {excluded_intervals} source-clock interval discontinuity value(s).")
    entrance_event_rows.append({
        "event_id": eid,
        "division": ev["match_type"],
        "entrance_rows_count": len(rows),
        "timed_entrance_count": len(durations),
        "median_entrance_duration_seconds": statistics.median(durations) if durations else "",
        "median_entrance_duration": duration_label(statistics.median(durations)) if durations else "",
        "average_entrance_duration_seconds": round(statistics.mean(durations), 1) if durations else "",
        "shortest_entrance_seconds": min(durations) if durations else "",
        "longest_entrance_seconds": max(durations) if durations else "",
        "latest_physical_entry_seconds": latest[0] if latest else "",
        "latest_physical_entry_time": seconds_to_mmss(latest[0]) if latest else "",
        "latest_physical_entry_wrestler_id": latest[1]["wrestler_id"] if latest else "",
        "advertised_interval_seconds": advertised if advertised is not None else "",
        "interval_sample_size": len(intervals),
        "median_actual_interval_seconds": statistics.median([x[0] for x in intervals]) if intervals else "",
        "largest_interval_variance_seconds": largest_variance[1] if largest_variance else "",
        "largest_interval_variance_wrestler_id": largest_variance[2]["wrestler_id"] if largest_variance else "",
        "largest_interval_actual_seconds": largest_variance[0] if largest_variance else "",
        "data_quality_status": "DERIVED",
        "notes": " ".join(notes),
    })

write("entrance_event_stats.csv", DERIVED_TABLES["entrance_event_stats.csv"], entrance_event_rows)

# ---------------------------------------------------------------------------
# records.csv -- ALL-TIME leaderboard, computed SEPARATELY for each
# division (Men's Royal Rumble records and Women's Royal Rumble records
# never share a leaderboard row -- "Most eliminations in a single Rumble
# ever" has an independent Men's holder and an independent Women's holder,
# two rows, not one row picking whichever number is numerically higher).
# Bio-based records (age/height/weight) only consider entrants whose
# relevant field is NOT UNKNOWN/CONFLICTING.
# ---------------------------------------------------------------------------
records = []
rid = 1
prior_record_rows = load("records.csv", DERIVED_DIR)


def add(division, category, name, holder, value, event_id, notes=""):
    global rid
    records.append({
        "record_id": f"R{rid:03d}", "division": division, "category": category, "record_name": name,
        "holder_wrestler_id": holder, "value": value, "event_id": event_id,
        "as_of_date": TODAY, "notes": notes,
    })
    rid += 1


def safe_max(items, key):
    valid = [i for i in items if i.get(key)]
    return max(valid, key=lambda i: float(i[key])) if valid else None


def safe_min(items, key):
    valid = [i for i in items if i.get(key)]
    return min(valid, key=lambda i: float(i[key])) if valid else None


# Entrants who were advertised/drew a number but never actually entered the ring at all
# (withdrew, attacked before their entrance, etc.) -- their 0:00 ring_time is not a real
# "shortest appearance", it's a no-show. Excluded from the "shortest appearance" record
# only (they remain fully documented via their own flags). Found/confirmed during the
# Collection of Stats cross-check pass (2026-09-17) -- see F008-record correction flag.
NEVER_ENTERED = {
    ("RR1991M", "randy-savage"),    # F023 -- drew #18, never entered
    ("RR1994M", "bastion-booger"),  # F091 -- withdrew before the match, ill
    ("RR1998M", "skull"),           # F141 -- attacked/mistaken for Austin, never entered
    ("RR2004M", "spike-dudley"),    # storyline-beaten-up backstage, never entered
    ("RR2004M", "test"),            # F175 -- storyline-attacked, never entered
    ("RR2005M", "scott-taylor"),    # F186 -- attacked during entrance, never made the ring
    ("RR2008M", "finlay"),          # F225 -- ran in ahead of his buzzer, DQ'd, never had an official entrance
    ("RR2015M", "curtis-axel"),     # buzzer sounded but never entered, substituted by Erick Rowan
}

# "Most wrestlers required to eliminate a single entrant" -- generic across
# the whole database, keyed by (event_id, victim) so it's naturally
# per-event and therefore trivially filterable per division below.
group_size_by_victim = defaultdict(set)
for e in eliminations:
    if not e["eliminator_wrestler_id"]:
        continue
    key = (e["event_id"], e["eliminated_wrestler_id"])
    group_size_by_victim[key].add(e["eliminator_wrestler_id"])
    group_size_by_victim[key].update(filter(None, e["assisting_wrestler_ids"].split(";")))

# "Most consecutive SOLO eliminations by one wrestler in a single Rumble" --
# also keyed per-event, filtered per division below. Requires order_in_match
# to be populated for a solid majority of an event's eliminations to be
# meaningful -- events under 50% coverage are excluded entirely.
logical_elims_by_event = defaultdict(list)
seen_victim_keys = set()
for e in eliminations:
    if not e["eliminator_wrestler_id"]:
        continue
    vkey = (e["event_id"], e["eliminated_wrestler_id"])
    if vkey in seen_victim_keys:
        continue
    seen_victim_keys.add(vkey)
    all_rows_for_victim = [r for r in eliminations if r["event_id"] == e["event_id"] and r["eliminated_wrestler_id"] == e["eliminated_wrestler_id"]]
    contributors = set()
    for r in all_rows_for_victim:
        contributors.add(r["eliminator_wrestler_id"])
        contributors.update(filter(None, r["assisting_wrestler_ids"].split(";")))
    orders = [int(r["order_in_match"]) for r in all_rows_for_victim if r["order_in_match"]]
    logical_elims_by_event[e["event_id"]].append({
        "order": min(orders) if orders else None,
        "is_solo": len(contributors) == 1,
        "eliminator": next(iter(contributors)) if len(contributors) == 1 else None,
    })

for division in DIVISIONS:
    div_event_ids = {eid for eid in events if division_of(eid) == division}
    div_entrants = [e for e in entrants if e["event_id"] in div_event_ids]
    div_eliminations = [e for e in eliminations if e["event_id"] in div_event_ids]
    div_career_rows = [r for r in career_rows if r["division"] == division]
    div_dyn_rows = [r for r in dyn_rows if r["division"] == division]
    div_rivalry_rows = [r for r in rivalry_rows if r["division"] == division]
    div_latest_event_id = max(div_event_ids, key=lambda eid: events[eid]["event_date"])

    weight_ok = [e for e in div_entrants if e["billed_weight_kg_at_event"] and e.get("physical_status") != "UNCERTAIN"]
    height_ok = [e for e in div_entrants if e["billed_height_m_at_event"] and e.get("physical_status") != "UNCERTAIN"]
    age_ok = [e for e in div_entrants if e["age_at_event"] and e.get("age_status") not in ("UNKNOWN", "")]
    time_ok = [e for e in div_entrants if e["ring_time_seconds"]]
    time_ok_real_appearance = [e for e in time_ok if (e["event_id"], e["wrestler_id"]) not in NEVER_ENTERED]

    # Coverage caveat (2026-09-23) -- billed_weight_kg_at_event,
    # billed_height_m_at_event and age_at_event are each populated for only
    # a small, non-random slice of entrants (mostly the earliest years
    # built from Shane's own source document, before the Phase B
    # per-appearance biography backfill happens -- see ROADMAP.md Phase B).
    # A "record" computed from an unresearched-elsewhere minority of
    # entrants is honest (DERIVED, not invented) but misleading if
    # presented as a flat "ever" without saying so -- this note makes the
    # actual sample size and year coverage visible on the record card
    # itself, and is computed fresh every run so it corrects itself as
    # Phase B fills more of these fields in.
    def coverage_note(pool, field_label):
        yrs = sorted(set(int(events[e["event_id"]]["event_date"][:4]) for e in pool))
        yr_txt = f"{yrs[0]}" if len(yrs) == 1 else (f"{yrs[0]}-{yrs[-1]}" if yrs == list(range(yrs[0], yrs[-1] + 1)) else ", ".join(str(y) for y in yrs))
        return (f"Based on the {len(pool)} of {len(div_entrants)} {division} entrants "
                f"({100*len(pool)/len(div_entrants):.1f}%) with {field_label} currently researched "
                f"(years covered so far: {yr_txt}) -- NOT a claim about the other "
                f"{len(div_entrants)-len(pool)} entrants, whose {field_label} simply hasn't been "
                f"looked up yet. Will update automatically as that research (ROADMAP.md Phase B) fills in.")

    if weight_ok:
        h = safe_max(weight_ok, "billed_weight_kg_at_event")
        l = safe_min(weight_ok, "billed_weight_kg_at_event")
        note = coverage_note(weight_ok, "billed weight")
        add(division, "Physical", "Heaviest entrant ever (billed)", h["wrestler_id"], h["billed_weight_kg_at_event"] + " kg", h["event_id"], note)
        add(division, "Physical", "Lightest entrant ever (billed)", l["wrestler_id"], l["billed_weight_kg_at_event"] + " kg", l["event_id"], note)
    if height_ok:
        t = safe_max(height_ok, "billed_height_m_at_event")
        s = safe_min(height_ok, "billed_height_m_at_event")
        note = coverage_note(height_ok, "billed height")
        add(division, "Physical", "Tallest entrant ever (billed)", t["wrestler_id"], t["billed_height_m_at_event"] + " m", t["event_id"], note)
        add(division, "Physical", "Shortest entrant ever (billed)", s["wrestler_id"], s["billed_height_m_at_event"] + " m", s["event_id"], note)
    if age_ok:
        age_pairs = [(e, parse_age_years(e["age_at_event"])) for e in age_ok]
        age_pairs = [p for p in age_pairs if p[1] is not None]
        if age_pairs:
            o = max(age_pairs, key=lambda p: p[1])
            y = min(age_pairs, key=lambda p: p[1])
            note = coverage_note([p[0] for p in age_pairs], "age at event")
            add(division, "Age", "Oldest entrant ever", o[0]["wrestler_id"], o[0]["age_at_event"], o[0]["event_id"], note)
            add(division, "Age", "Youngest entrant ever", y[0]["wrestler_id"], y[0]["age_at_event"], y[0]["event_id"], note)
    if time_ok:
        lg = safe_max(time_ok, "ring_time_seconds")
        add(division, "Time", "Longest single Rumble appearance ever", lg["wrestler_id"], lg["ring_time"], lg["event_id"])
    if time_ok_real_appearance:
        sh = safe_min(time_ok_real_appearance, "ring_time_seconds")
        add(division, "Time", "Shortest single Rumble appearance ever", sh["wrestler_id"], sh["ring_time"], sh["event_id"],
            "Excludes entrants who were advertised/counted as an entrant but never actually entered the "
            "ring at all (withdrew, attacked before their entrance, etc. -- see NEVER_ENTERED in this "
            "script). Randy Savage's 1991 no-show (00:00, F023) held this record incorrectly until the "
            "Collection of Stats cross-check pass (2026-09-17) caught the mismatch.")

    if div_entrants:
        most_elims_single = max(div_entrants, key=lambda e: int(e["wrestlers_eliminated_count"] or 0))
        add(division, "Eliminations", "Most eliminations in a single Rumble ever", most_elims_single["wrestler_id"], most_elims_single["wrestlers_eliminated_count"], most_elims_single["event_id"])

    if div_career_rows:
        most_career_elims = max(div_career_rows, key=lambda r: r["total_eliminations_made"])
        most_appearances = max(div_career_rows, key=lambda r: r["total_appearances"])
        most_wins = max(div_career_rows, key=lambda r: r["wins"])
        add(division, "Eliminations", "Most CAREER eliminations", most_career_elims["wrestler_id"], most_career_elims["total_eliminations_made"], div_latest_event_id)
        add(division, "Frequency", "Most career appearances", most_appearances["wrestler_id"], most_appearances["total_appearances"], div_latest_event_id)
        add(division, "Frequency", "Most Rumble wins", most_wins["wrestler_id"], most_wins["wins"], div_latest_event_id)

        # "Most runner-up finishes (career)" -- zero-new-research, derived
        # purely from career_stats.csv's existing runner_up_finishes column
        # (IDEAS.md Phase A wishlist, 2026-09-29: surface the repeat-runner-up
        # pattern -- e.g. Roman Reigns' four Men's runner-up finishes --
        # rather than leaving it buried in each wrestler's own profile page).
        most_ru = [r for r in div_career_rows if r["runner_up_finishes"] > 0]
        if most_ru:
            max_ru_count = max(r["runner_up_finishes"] for r in most_ru)
            tied_ru = sorted((r for r in most_ru if r["runner_up_finishes"] == max_ru_count),
                              key=lambda r: r["wrestler_id"])
            top_ru = tied_ru[0]
            ru_note = ""
            if len(tied_ru) > 1:
                others = ", ".join(r["wrestler_id"] for r in tied_ru[1:])
                ru_note = f"Tied with: {others} (all at {max_ru_count})."
            add(division, "Frequency", "Most runner-up finishes (career)", top_ru["wrestler_id"], max_ru_count, div_latest_event_id, ru_note)

    if div_dyn_rows:
        most_hof = max(div_dyn_rows, key=lambda r: r["hof_members_eventually_count"])
        most_hof_at_time = max(div_dyn_rows, key=lambda r: int(r.get("hof_members_at_time_count") or 0))
        most_deceased = max(div_dyn_rows, key=lambda r: r["now_deceased_count"])
        add(division, "Field composition", "Rumble with most eventual Hall of Famers", "", most_hof["hof_members_eventually_count"], most_hof["event_id"], "'eventual' = inducted at any point, not necessarily by the event date")
        if int(most_hof_at_time.get("hof_members_at_time_count") or 0) > 0:
            add(division, "Field composition", "Rumble with most Hall of Famers already inducted at the time", "", most_hof_at_time["hof_members_at_time_count"], most_hof_at_time["event_id"], "distinct from the 'eventual' record above -- this one only counts wrestlers who were ALREADY Hall of Famers on the night, not ones inducted later")
        add(division, "Field composition", "Rumble with most now-deceased entrants", "", most_deceased["now_deceased_count"], most_deceased["event_id"], f"as of {TODAY} -- recompute this periodically, it only grows")

    if div_rivalry_rows:
        top_rivalry = div_rivalry_rows[0]
        add(division, "Rivalries", "Most frequent eliminator/eliminated pairing", f"{top_rivalry['eliminator_wrestler_id']} -> {top_rivalry['eliminated_wrestler_id']}", top_rivalry["times_eliminated"], top_rivalry["most_recent_event_id"])

    # ---- "Most wrestlers required to eliminate a single entrant", this division only
    div_group_sizes = {k: g for k, g in group_size_by_victim.items() if k[0] in div_event_ids}
    if div_group_sizes:
        max_size = max(len(g) for g in div_group_sizes.values())
        tied = [(k, g) for k, g in div_group_sizes.items() if len(g) == max_size]
        (top_event, top_victim), top_group = tied[0]
        tie_note = ""
        if len(tied) > 1:
            others = ", ".join(f"{v} ({eid}, {len(g)})" for (eid, v), g in tied[1:])
            tie_note = f" TIED with: {others}."
        add(division, "Eliminations", "Most wrestlers required to eliminate a single entrant", top_victim, len(top_group), top_event,
            f"Contributors: {', '.join(sorted(top_group))}.{tie_note} A new stat type added during the "
            f"Collection of Stats cross-check pass (2026-09-17) -- cross-verify against Wrestling Inc/"
            f"Cult of Whatever's own headcount claims for this and other years before treating any single "
            f"value as final (2 mismatches already flagged for Earthquake 1990 and Muhammad Hassan 2005).")

    # ---- "Most consecutive solo eliminations in a single Rumble", this division only
    div_all_streaks = []
    for eid, rows in logical_elims_by_event.items():
        if eid not in div_event_ids:
            continue
        with_order = [r for r in rows if r["order"] is not None]
        if not rows or len(with_order) < 0.5 * len(rows):
            continue  # order_in_match too sparse this event to trust a "consecutive" answer
        with_order.sort(key=lambda r: r["order"])
        cur, streak, best_this_event = None, 0, 0
        for r in with_order:
            if r["is_solo"] and r["eliminator"] == cur:
                streak += 1
            elif r["is_solo"]:
                cur, streak = r["eliminator"], 1
            else:
                cur, streak = None, 0
            if streak > best_this_event:
                best_this_event = streak
        if best_this_event:
            cur, streak = None, 0
            for r in with_order:
                if r["is_solo"] and r["eliminator"] == cur:
                    streak += 1
                elif r["is_solo"]:
                    cur, streak = r["eliminator"], 1
                else:
                    cur, streak = None, 0
                if streak == best_this_event:
                    div_all_streaks.append((streak, eid, cur))
                    break

    if div_all_streaks:
        best_streak = max(s for s, _, _ in div_all_streaks)
        tied = [(eid, w) for s, eid, w in div_all_streaks if s == best_streak]
        best_event, best_wrestler = tied[0]
        tie_note = ""
        if len(tied) > 1:
            others = ", ".join(f"{w} ({eid})" for eid, w in tied[1:])
            tie_note = f" TIED with: {others}."
        add(division, "Eliminations", "Most consecutive solo eliminations in a single Rumble", best_wrestler, best_streak, best_event,
            f"{tie_note.strip()} A new stat type added during the Collection of Stats cross-check pass "
            f"(2026-09-17). Only computed from events where order_in_match is populated for at least "
            f"50% of recorded eliminations -- 1994 and 2000 (both at 0% coverage) are excluded on this "
            f"basis despite Rumble trivia claiming a tying 7-streak for Diesel (1994) and Rikishi (2000) "
            f"respectively; see the flagged cross-check note for details.")

    # ---- Phase A additions (2026-09-23) -- zero new research, purely derived
    # from data already in career_stats.csv / entrants.csv, per the "big
    # wishlist" triage in IDEAS.md. See IDEAS.md for the full Phase A list.

    # "Most eliminations without ever winning" (career) -- a wrestler who
    # racked up a real career elimination total but never got the Rumble win.
    never_won = [r for r in div_career_rows if int(r.get("wins") or 0) == 0]
    elims_no_win = [r for r in never_won if int(r.get("total_eliminations_made") or 0) > 0]
    if elims_no_win:
        top = max(elims_no_win, key=lambda r: int(r["total_eliminations_made"]))
        add(division, "Eliminations", "Most career eliminations without ever winning",
            top["wrestler_id"], top["total_eliminations_made"], div_latest_event_id)

    # "Most appearances without ever winning" -- pure durability/bad-luck stat.
    if never_won:
        top = max(never_won, key=lambda r: int(r.get("total_appearances") or 0))
        add(division, "Frequency", "Most career appearances without ever winning",
            top["wrestler_id"], top["total_appearances"], div_latest_event_id)

    # "Most eliminations in a single Rumble without winning that Rumble" --
    # distinct from the existing "Most eliminations in a single Rumble ever"
    # record above, which can be (and often is) held by that match's winner.
    non_winners = [e for e in div_entrants if e.get("is_winner") != "TRUE"
                   and int(e.get("wrestlers_eliminated_count") or 0) > 0]
    if non_winners:
        top = max(non_winners, key=lambda e: int(e["wrestlers_eliminated_count"]))
        add(division, "Eliminations", "Most eliminations in a single Rumble without winning it",
            top["wrestler_id"], top["wrestlers_eliminated_count"], top["event_id"])

    # "Longest gap between Rumble appearances" (career) -- e.g. a legend's
    # return years after their last run. Uses longest_gap_years, already
    # computed above in career_rows but never surfaced as a record before.
    gap_rows = [r for r in div_career_rows if int(r.get("longest_gap_years") or 0) > 0]
    if gap_rows:
        top = max(gap_rows, key=lambda r: int(r["longest_gap_years"]))
        add(division, "Durability", "Longest gap between Rumble appearances (career)",
            top["wrestler_id"], f"{top['longest_gap_years']} years", div_latest_event_id)

    # "Longest consecutive-year appearance streak" -- uses
    # longest_consecutive_streak, same situation (already computed, not yet
    # surfaced as a record).
    streak_rows = [r for r in div_career_rows if int(r.get("longest_consecutive_streak") or 0) > 0]
    if streak_rows:
        top = max(streak_rows, key=lambda r: int(r["longest_consecutive_streak"]))
        add(division, "Durability", "Longest consecutive-year appearance streak",
            top["wrestler_id"], f"{top['longest_consecutive_streak']} years", div_latest_event_id)

    # "Most distinct wrestlers eliminated across a career" (variety, not
    # volume -- a wrestler who eliminated the same rival 5 times scores lower
    # here than one who eliminated 5 different people once each).
    if div_career_rows:
        top = max(div_career_rows, key=lambda r: int(r.get("distinct_wrestlers_eliminated_count") or 0))
        if int(top.get("distinct_wrestlers_eliminated_count") or 0) > 0:
            add(division, "Rivalries", "Most distinct wrestlers eliminated across a career",
                top["wrestler_id"], top["distinct_wrestlers_eliminated_count"], div_latest_event_id)

        # Inverse: eliminated by the widest variety of different opponents
        # across a career (as opposed to being repeatedly ended by one rival).
        top2 = max(div_career_rows, key=lambda r: int(r.get("distinct_eliminators_count") or 0))
        if int(top2.get("distinct_eliminators_count") or 0) > 0:
            add(division, "Rivalries", "Eliminated by the most different opponents across a career",
                top2["wrestler_id"], top2["distinct_eliminators_count"], div_latest_event_id)

# Append this new record type only after every pre-existing record has been
# assigned its ID. This preserves all established record_id values.
for division in DIVISIONS:
    div_occupancy_rows = [r for r in occupancy_rows if r["division"] == division]
    if not div_occupancy_rows:
        continue
    peak_count = max(int(r["peak_in_ring_count"]) for r in div_occupancy_rows)
    tied_peaks = [r for r in div_occupancy_rows if int(r["peak_in_ring_count"]) == peak_count]
    top_peak = tied_peaks[0]
    tie_note = ""
    if len(tied_peaks) > 1:
        tie_note = " Tied with: " + ", ".join(r["event_id"] for r in tied_peaks[1:]) + "."
    add(
        division, "Match dynamics", "Most wrestlers simultaneously in the ring", "",
        peak_count, top_peak["event_id"],
        (f"Peak window {top_peak['peak_start_time']}-{top_peak['peak_end_time']}.{tie_note} Based on "
         f"{len(div_occupancy_rows)} complete-timeline {division} events only; incomplete events "
         "are excluded rather than estimated."),
    )

# Entrance timing records are appended after every established record type so
# Version 36's R001-R051 identifiers remain stable. Ties are preserved in the
# note rather than silently discarded by max()/min().
for division in DIVISIONS:
    div_entrance_rows = [r for r in entrances if division_of(r["event_id"]) == division]
    timed = [r for r in div_entrance_rows if r.get("entrance_duration_seconds") not in (None, "")]
    div_event_stats = [r for r in entrance_event_rows if r["division"] == division]

    def add_timed_record(record_name, target_value, value_label):
        tied = [r for r in timed if int(r["entrance_duration_seconds"]) == target_value]
        top = tied[0]
        tie_note = ""
        if len(tied) > 1:
            tie_note = " Tied with: " + ", ".join(f"{r['wrestler_id']} ({r['event_id']})" for r in tied[1:]) + "."
        add(division, "Entrance timing", record_name, top["wrestler_id"], value_label,
            top["event_id"],
            f"Based on {len(timed)} sourced entrance-duration rows in this division.{tie_note}")

    if timed:
        longest = max(int(r["entrance_duration_seconds"]) for r in timed)
        shortest = min(int(r["entrance_duration_seconds"]) for r in timed)
        add_timed_record("Longest entrance (buzzer to physical ring entry)", longest, seconds_to_mmss(longest))
        add_timed_record("Shortest entrance (buzzer to physical ring entry)", shortest, seconds_to_mmss(shortest))

    latest_rows = [r for r in div_event_stats if r.get("latest_physical_entry_seconds") not in (None, "")]
    if latest_rows:
        latest = max(latest_rows, key=lambda r: int(r["latest_physical_entry_seconds"]))
        add(division, "Entrance timing", "Latest physical ring entry in a Rumble",
            latest["latest_physical_entry_wrestler_id"], latest["latest_physical_entry_time"], latest["event_id"],
            "Absolute timestamps beyond an event's recorded match duration are excluded as source-video clock discontinuities.")

    variance_rows = [r for r in div_event_stats if r.get("largest_interval_variance_seconds") not in (None, "")]
    if variance_rows:
        variance = max(variance_rows, key=lambda r: abs(int(r["largest_interval_variance_seconds"])))
        signed = int(variance["largest_interval_variance_seconds"])
        direction = "late" if signed >= 0 else "early"
        add(division, "Entrance timing", "Biggest variance from advertised entry interval",
            variance["largest_interval_variance_wrestler_id"], f"{abs(signed)} sec {direction}", variance["event_id"],
            f"Actual buzzer gap {variance['largest_interval_actual_seconds']} sec versus advertised {variance['advertised_interval_seconds']} sec. Consecutive entry numbers only; source-clock discontinuities over five minutes are excluded.")

    median_rows = [r for r in div_event_stats if r.get("median_entrance_duration_seconds") not in (None, "")]
    if median_rows:
        for record_name, chooser in (
            ("Rumble with longest median entrance", max),
            ("Rumble with shortest median entrance", min),
        ):
            chosen = chooser(median_rows, key=lambda r: float(r["median_entrance_duration_seconds"]))
            chosen_value = float(chosen["median_entrance_duration_seconds"])
            tied = [r for r in median_rows if float(r["median_entrance_duration_seconds"]) == chosen_value]
            tie_note = ""
            if len(tied) > 1:
                tie_note = " Tied with: " + ", ".join(r["event_id"] for r in tied[1:]) + "."
            add(division, "Entrance timing", record_name, "", chosen["median_entrance_duration"], chosen["event_id"],
                f"Median of {chosen['timed_entrance_count']} sourced entrance durations for this event.{tie_note}")

# Championship-at-entry and return records, derived only from the fully
# classified entrant rows. Appended after R001-R063 so all established record
# identifiers remain stable.
for division in DIVISIONS:
    div_rows = [r for r in entrants if division_of(r["event_id"]) == division]
    champ_rows = [r for r in div_rows if (r.get("current_champion_title") or "").strip() not in ("", "N/A", "UNKNOWN")]
    return_rows = [r for r in div_rows if (r.get("is_returning_wrestler") or "").upper() == "TRUE"]

    def tie_note(rows, labeler):
        return "" if len(rows) <= 1 else " Tied with: " + ", ".join(labeler(r) for r in rows[1:]) + "."

    if champ_rows:
        champions_by_event = Counter(r["event_id"] for r in champ_rows)
        most_champions = max(champions_by_event.values())
        champ_events = sorted((eid for eid, count in champions_by_event.items() if count == most_champions),
                              key=lambda eid: events[eid]["event_date"])
        add(division, "Championship context", "Rumble with most reigning champions in the field", "",
            most_champions, champ_events[0],
            "Counts titles held when the Rumble match began; a title lost earlier on the card is not counted."
            + tie_note(champ_events, lambda eid: eid))

        reign_rows = [r for r in champ_rows if (r.get("days_into_reign_at_event") or "").isdigit()]
        if reign_rows:
            longest_days = max(int(r["days_into_reign_at_event"]) for r in reign_rows)
            longest = [r for r in reign_rows if int(r["days_into_reign_at_event"]) == longest_days]
            top = longest[0]
            add(division, "Championship context", "Longest title reign entering a Rumble", top["wrestler_id"],
                f"{longest_days} days", top["event_id"],
                f"Title: {top['current_champion_title']}."
                + tie_note(longest, lambda r: f"{r['wrestler_id']} ({r['event_id']})"))

        champion_apps = Counter(r["wrestler_id"] for r in champ_rows)
        most_champion_apps = max(champion_apps.values())
        champion_holders = sorted(wid for wid, count in champion_apps.items() if count == most_champion_apps)
        holder = champion_holders[0]
        holder_rows = [r for r in champ_rows if r["wrestler_id"] == holder]
        latest_event = max(holder_rows, key=lambda r: events[r["event_id"]]["event_date"])["event_id"]
        add(division, "Championship context", "Most Rumble appearances as reigning champion", holder,
            most_champion_apps, latest_event,
            "A reigning-champion appearance is counted only when current_champion_title is populated at match start."
            + tie_note(champion_holders, lambda wid: wid))

    if return_rows:
        returns_by_event = Counter(r["event_id"] for r in return_rows)
        most_returns = max(returns_by_event.values())
        return_events = sorted((eid for eid, count in returns_by_event.items() if count == most_returns),
                               key=lambda eid: events[eid]["event_date"])
        add(division, "Return context", "Rumble with most returning wrestlers", "", most_returns,
            return_events[0],
            "Uses the existing is_returning_wrestler classification; no absence length is inferred when it is unknown."
            + tie_note(return_events, lambda eid: eid))

        return_apps = Counter(r["wrestler_id"] for r in return_rows)
        most_return_apps = max(return_apps.values())
        return_holders = sorted(wid for wid, count in return_apps.items() if count == most_return_apps)
        holder = return_holders[0]
        holder_rows = [r for r in return_rows if r["wrestler_id"] == holder]
        latest_event = max(holder_rows, key=lambda r: events[r["event_id"]]["event_date"])["event_id"]
        add(division, "Return context", "Most Rumble appearances classified as a return", holder,
            most_return_apps, latest_event,
            "Counts separately documented return appearances, not ordinary year-to-year participation."
            + tie_note(return_holders, lambda wid: wid))

# Combined billed-physical records. These are intentionally restricted to
# rows emitted by ring_physical_peaks.csv: complete reconstructed timeline
# plus 100% field coverage for the relevant metric.
for division in DIVISIONS:
    for metric, record_name, formatter in (
        ("combined_billed_weight", "Highest combined billed weight simultaneously in the ring",
         lambda value: f"{value:,.1f} kg"),
        ("combined_billed_height", "Greatest combined billed height simultaneously in the ring",
         lambda value: f"{value:.2f} m"),
    ):
        candidates = [r for r in physical_peak_rows if r["division"] == division and r["metric"] == metric]
        if not candidates:
            continue
        peak = max(float(r["peak_value"]) for r in candidates)
        tied = sorted((r for r in candidates if float(r["peak_value"]) == peak),
                      key=lambda r: events[r["event_id"]]["event_date"])
        chosen = tied[0]
        tie_text = "" if len(tied) == 1 else " Tied with: " + ", ".join(r["event_id"] for r in tied[1:]) + "."
        add(division, "Match dynamics", record_name, "", formatter(peak), chosen["event_id"],
            f"Peak window: {chosen['peak_start_time']}-{chosen['peak_end_time']}. "
            "Complete-timeline events with 100% appearance-specific profile coverage only; no missing value is estimated."
            + tie_text)

# Full-field billed physical records. Unlike simultaneous-ring peaks, these
# need no timeline, but still require 100% appearance-specific coverage for
# the metric across all actual entrants in an event.
for division in DIVISIONS:
    metrics = (
        ("combined_billed_weight_kg", "Heaviest combined billed Rumble field", lambda v: f"{v:,.1f} kg"),
        ("average_billed_weight_kg", "Highest average billed weight in a Rumble field", lambda v: f"{v:,.1f} kg"),
        ("combined_billed_height_m", "Greatest combined billed height in a Rumble field", lambda v: f"{v:.2f} m"),
        ("average_billed_height_m", "Highest average billed height in a Rumble field", lambda v: f"{v:.3f} m"),
    )
    for field_name, record_name, formatter in metrics:
        candidates = [r for r in field_physical_rows
                      if r["division"] == division and r.get(field_name) not in (None, "")]
        if not candidates:
            continue
        peak = max(float(r[field_name]) for r in candidates)
        tied = sorted((r for r in candidates if float(r[field_name]) == peak),
                      key=lambda r: events[r["event_id"]]["event_date"])
        chosen = tied[0]
        tie_text = "" if len(tied) == 1 else " Tied with: " + ", ".join(r["event_id"] for r in tied[1:]) + "."
        add(division, "Field composition", record_name, "", formatter(peak), chosen["event_id"],
            f"Based on all {chosen['actual_entrant_count']} actual entrants; 100% appearance-specific field coverage required."
            + tie_text)

# ---------------------------------------------------------------------------
# Phase A(2) additions (2026-09-26) -- again zero new research, purely
# derived from entrants.csv fields already in the database. Per Shane's
# "smaller, well-defined stats" list (ROYAL_RUMBLE_REMAINING_WORK_AUDIT
# Section 3): iron-man streak and bounce-back factor. Appended last so every
# previously-assigned record_id stays stable.
# ---------------------------------------------------------------------------
entrants_by_event_all = defaultdict(list)
for e in entrants:
    entrants_by_event_all[e["event_id"]].append(e)

for division in DIVISIONS:
    div_event_ids_sorted = sorted(
        (eid for eid in events if division_of(eid) == division),
        key=lambda eid: events[eid]["event_date"],
    )

    # ---- "Longest iron-man streak": most consecutive editions of this
    # division in which a wrestler had the single longest ring time in the
    # match. "Consecutive" means back-to-back editions actually present in
    # this database with usable ring-time data -- NOT necessarily
    # back-to-back calendar years, since an event with zero ring_time
    # coverage can't determine an iron man at all and is simply skipped
    # (documented per-division below rather than silently treated as a
    # streak-breaker or a streak-continuer).
    iron_man_sequence = []  # [(event_id, wrestler_id)], only for events where one could be determined
    skipped_events = []
    for eid in div_event_ids_sorted:
        pool = [e for e in entrants_by_event_all[eid]
                if e["ring_time_seconds"] and (eid, e["wrestler_id"]) not in NEVER_ENTERED]
        if not pool:
            skipped_events.append(eid)
            continue
        top_time = max(int(e["ring_time_seconds"]) for e in pool)
        tied = sorted((e for e in pool if int(e["ring_time_seconds"]) == top_time), key=lambda e: e["wrestler_id"])
        iron_man_sequence.append((eid, tied[0]["wrestler_id"], len(tied) > 1))

    if iron_man_sequence:
        best_streak, best_start, best_end, best_wrestler = 0, None, None, None
        cur_wrestler, cur_streak, cur_start = None, 0, None
        for eid, wid, was_tied in iron_man_sequence:
            if wid == cur_wrestler:
                cur_streak += 1
            else:
                cur_wrestler, cur_streak, cur_start = wid, 1, eid
            if cur_streak > best_streak:
                best_streak, best_start, best_end, best_wrestler = cur_streak, cur_start, eid, cur_wrestler
        if best_streak >= 2:
            covered_span = f"{best_start} to {best_end}"
            skip_note = (f" {len(skipped_events)} {division} event(s) had no usable ring-time data and were "
                         f"excluded from the sequence entirely (not counted as breaking or extending any "
                         f"streak): {', '.join(skipped_events)}." if skipped_events else "")
            add(division, "Durability", "Longest iron-man streak (most consecutive editions with the longest ring time)",
                best_wrestler, f"{best_streak} consecutive editions", best_end,
                f"Streak runs {covered_span} in this database's own edition sequence for this division."
                + skip_note)

    # ---- "Bounce-back factor": eliminated early one year, won the very next
    # edition (of the true back-to-back editions present in this database).
    # Score = how early the elimination was, expressed as elim_number /
    # field size for that event (lower = eliminated earlier). Restricted to
    # actual winners the following year so the record has one unambiguous
    # top answer rather than a subjective "deep run" threshold.
    bounce_candidates = []
    for i in range(len(div_event_ids_sorted) - 1):
        ev_a, ev_b = div_event_ids_sorted[i], div_event_ids_sorted[i + 1]
        rows_a = {e["wrestler_id"]: e for e in entrants_by_event_all[ev_a]}
        rows_b = {e["wrestler_id"]: e for e in entrants_by_event_all[ev_b]}
        field_size_a = len(entrants_by_event_all[ev_a])
        if field_size_a == 0:
            continue
        for wid, row_b in rows_b.items():
            if row_b.get("is_winner") != "TRUE":
                continue
            row_a = rows_a.get(wid)
            if not row_a or not row_a.get("elim_number") or row_a.get("is_winner") == "TRUE":
                continue
            percentile = int(row_a["elim_number"]) / field_size_a
            bounce_candidates.append((percentile, wid, ev_a, ev_b, row_a["elim_number"], field_size_a))

    if bounce_candidates:
        bounce_candidates.sort(key=lambda t: t[0])
        pct, wid, ev_a, ev_b, elim_num, field_size = bounce_candidates[0]
        add(division, "Durability", "Best bounce-back (earliest elimination immediately followed by a win the next edition)",
            wid, f"Eliminated #{elim_num} of {field_size} at {ev_a}, won {ev_b}", ev_b,
            f"Score = elimination position / field size for the earlier event (lower = eliminated earlier); "
            f"this entrant scored {pct:.3f}. Restricted to truly back-to-back editions of this division as "
            f"present in the database, and to an outright win the following year (not a looser 'deep run' "
            f"threshold, to keep this record unambiguous).")

# Preserve established record IDs by semantic key. New categories can become
# available later (for example when a division gains its first complete
# occupancy timeline); they append after the highest existing ID instead of
# renumbering every record that follows their generation block.
prior_record_ids = {
    (r["division"], r["category"], r["record_name"]): r["record_id"]
    for r in prior_record_rows if r.get("record_id")
}
next_record_number = max(
    [int(rid_value[1:]) for rid_value in prior_record_ids.values()
     if rid_value.startswith("R") and rid_value[1:].isdigit()] or [0]
) + 1
for record in records:
    key = (record["division"], record["category"], record["record_name"])
    if key in prior_record_ids:
        record["record_id"] = prior_record_ids[key]
    else:
        record["record_id"] = f"R{next_record_number:03d}"
        next_record_number += 1
records.sort(key=lambda r: int(r["record_id"][1:]))
write("records.csv", DERIVED_TABLES["records.csv"], records)

# ---------------------------------------------------------------------------
# records_history.csv -- APPEND-ONLY. Diff new `records` against whatever
# records.csv held before this run, keyed by (division, category,
# record_name) so a Men's record and a Women's record in the same category
# never overwrite each other's history.
# ---------------------------------------------------------------------------
existing_history = load("records_history.csv", DERIVED_DIR)
history_rows = list(existing_history)
next_hid = len(history_rows) + 1

baseline_path = os.path.join(DERIVED_DIR, ".records_baseline.csv")
previous = {}
if os.path.exists(baseline_path):
    with open(baseline_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            previous[(row.get("division", ""), row["category"], row["record_name"])] = row

for r in records:
    key = (r["division"], r["category"], r["record_name"])
    prev = previous.get(key)
    changed = prev is None or prev.get("holder_wrestler_id") != r["holder_wrestler_id"] or str(prev.get("value")) != str(r["value"])
    if changed:
        history_rows.append({
            "history_id": f"H{next_hid:04d}", "division": r["division"], "category": r["category"], "record_name": r["record_name"],
            "new_holder_wrestler_id": r["holder_wrestler_id"], "new_value": r["value"],
            "broke_event_id": r["event_id"],
            "previous_holder_wrestler_id": prev["holder_wrestler_id"] if prev else "",
            "previous_value": prev["value"] if prev else "",
            "logged_date": TODAY,
            "notes": "initial record (first event processed for this division/category)" if prev is None else "",
        })
        next_hid += 1

write("records_history.csv", DERIVED_TABLES["records_history.csv"], history_rows)

# persist this run's records.csv as the new baseline for next time
with open(baseline_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=DERIVED_TABLES["records.csv"])
    writer.writeheader()
    writer.writerows(records)

# ---------------------------------------------------------------------------
# Full-card stats (2026-09-30): commentators, other/undercard matches, and
# how they cross-reference with the Royal Rumble match itself. Per Shane's
# request to also track "the other matches on the card" and surface things
# like dual-duty entrants (wrestled earlier AND entered the Rumble),
# non-Rumble card regulars (on the card repeatedly but never in the Rumble
# match itself), commentator appearance counts, and the most frequent match
# types / titles featured on the card. Only events with actual other_matches
# / show_appearances rows contribute here -- an event missing from these
# tables simply has no full-card research done yet, not a zero.
# ---------------------------------------------------------------------------
other_matches = load("other_matches.csv")
show_appearances = load("show_appearances.csv")

entrants_by_event_wid = {(e["event_id"], e["wrestler_id"]): e for e in entrants}

# --- card_dual_duty.csv: other_matches rows for a wrestler who ALSO entered
# that same event's Royal Rumble match (i.e. has an entrants.csv row there).
dual_duty_rows = []
for r in other_matches:
    if r["time_before_rumble"] != "TRUE":
        continue
    ent = entrants_by_event_wid.get((r["event_id"], r["wrestler_id"]))
    if not ent:
        continue  # wrestled earlier on the card, but didn't also enter the Rumble
    rumble_result = (
        "Winner" if ent["is_winner"] == "TRUE" else
        "Runner-up" if ent["is_runner_up"] == "TRUE" else
        (f"Eliminated (#{ent['elim_number']})" if ent.get("elim_number") else "Eliminated")
    )
    dual_duty_rows.append({
        "event_id": r["event_id"],
        "division": division_of(r["event_id"]),
        "wrestler_id": r["wrestler_id"],
        "other_match_number": r["match_number_on_card"],
        "other_match_type": r["match_type"],
        "other_match_result": r["result"],
        "entry_number": ent.get("entry_number", ""),
        "rumble_result": rumble_result,
        "notes": "",
    })
dual_duty_rows.sort(key=lambda r: (r["event_id"], r["wrestler_id"]))
write("card_dual_duty.csv", DERIVED_TABLES["card_dual_duty.csv"], dual_duty_rows)

# --- card_non_rumble_regulars.csv: wrestlers who show up in other_matches.csv
# at 2+ distinct events but never have an entrants.csv row at all (i.e. never
# entered ANY Royal Rumble match, in either division).
entrant_wids_all = set(e["wrestler_id"] for e in entrants)
events_by_wid = defaultdict(set)
for r in other_matches:
    events_by_wid[r["wrestler_id"]].add(r["event_id"])

regulars_rows = []
for wid, evset in events_by_wid.items():
    if wid in entrant_wids_all:
        continue
    if len(evset) < 2:
        continue
    ev_sorted = sorted(evset, key=lambda eid: (events[eid]["event_date"] if eid in events else eid))
    regulars_rows.append({
        "wrestler_id": wid,
        "card_appearances_count": len(evset),
        "events_with_card_appearance": ";".join(ev_sorted),
        "first_event_id": ev_sorted[0],
        "most_recent_event_id": ev_sorted[-1],
        "notes": "Appeared on the card multiple times but has never entered a Royal Rumble match (in either division) among the events with full-card research done so far.",
    })
regulars_rows.sort(key=lambda r: (-r["card_appearances_count"], r["wrestler_id"]))
write("card_non_rumble_regulars.csv", DERIVED_TABLES["card_non_rumble_regulars.csv"], regulars_rows)

# --- commentator_stats.csv: appearance counts per person/role from
# show_appearances.csv (Commentator, Ring Announcer, Referee roles).
by_person_role = defaultdict(list)
for r in show_appearances:
    if r["role"] not in ("Commentator", "Ring Announcer", "Referee"):
        continue
    by_person_role[(r["person_id"], r["role"])].append(r)

commentator_rows = []
for (pid, role), apps in by_person_role.items():
    evset = sorted(set(a["event_id"] for a in apps), key=lambda eid: (events[eid]["event_date"] if eid in events else eid))
    name = apps[0]["person_name"]
    commentator_rows.append({
        "person_id": pid,
        "person_name": name,
        "role": role,
        "events_count": len(evset),
        "first_event_id": evset[0],
        "most_recent_event_id": evset[-1],
        "events_list": ";".join(evset),
    })
commentator_rows.sort(key=lambda r: (r["role"], -r["events_count"], r["person_id"]))
write("commentator_stats.csv", DERIVED_TABLES["commentator_stats.csv"], commentator_rows)

# --- card_match_type_frequency.csv / card_title_frequency.csv: dedupe
# other_matches.csv rows down to one row per actual MATCH (not per
# participant) before counting.
matches_seen = {}
for r in other_matches:
    key = (r["event_id"], r["match_number_on_card"])
    if key not in matches_seen:
        matches_seen[key] = r

type_counter = Counter()
type_events = defaultdict(set)
for (eid, mnum), r in matches_seen.items():
    mtype = r["match_type"].strip()
    if not mtype:
        continue
    type_counter[mtype] += 1
    type_events[mtype].add(eid)

type_rows = [{
    "match_type": mtype, "occurrences": n, "events_count": len(type_events[mtype]), "notes": "",
} for mtype, n in type_counter.most_common()]
write("card_match_type_frequency.csv", DERIVED_TABLES["card_match_type_frequency.csv"], type_rows)

title_counter = Counter()
title_events = defaultdict(set)
title_champions = defaultdict(set)
for (eid, mnum), r in matches_seen.items():
    title = r["title_involved"].strip()
    if not title:
        continue
    title_counter[title] += 1
    title_events[title].add(eid)
for r in other_matches:
    title = r["title_involved"].strip()
    if title and r["was_champion_entering"] == "TRUE":
        title_champions[title].add(r["wrestler_id"])

title_rows = [{
    "title_involved": title, "occurrences": n, "events_count": len(title_events[title]),
    "distinct_champions_count": len(title_champions.get(title, set())), "notes": "",
} for title, n in title_counter.most_common()]
write("card_title_frequency.csv", DERIVED_TABLES["card_title_frequency.csv"], title_rows)

print(f"Full-card stats: {len(dual_duty_rows)} dual-duty entrant rows, {len(regulars_rows)} non-Rumble card "
      f"regulars, {len(commentator_rows)} person/role appearance-count rows, {len(type_rows)} match types, "
      f"{len(title_rows)} titles featured on the card.")

print(f"Derived tables rebuilt from {len(events)} event(s) across {len(DIVISIONS)} division(s) ({', '.join(DIVISIONS)}): "
      f"{len(career_rows)} wrestler career rows, {len(entry_rows)} entry-number rows, "
      f"{len(records)} current records, {len(history_rows) - len(existing_history)} new records_history entries "
      f"({len(history_rows)} total), {len(rivalry_rows)} elimination pairings, {len(dyn_rows)} event_dynamic_stats rows.")
if len(events) == 1:
    print("NOTE: only 1 event loaded -- every 'ever'/'career' record above is really just that event's "
          "numbers. That's expected and correct; they'll become real all-time records as more Rumbles are "
          "added, and records_history.csv will start logging when/if a later Rumble breaks an early mark.")
