# -*- coding: utf-8 -*-
"""
Generates dashboard/data.json from the live CSVs -- the single data file the
Royal Rumble dashboard artifact loads client-side. Run this any time the
database changes and the published dashboard needs a refresh:

    python3 scripts/build_dashboard_data.py data dashboard/data.json

Still deliberately lean (drops long free-text columns like full notes,
source_ids, alignment/gimmick detail), but now covers a full wrestler-profile
scope too: each wrestler entry carries a bio (real name, DOB, birthplace,
nationality, HOF year, deceased status -- with each fact's own CONFIRMED/
PROBABLE/etc status where the source table tracks one), a complete Rumble-by-
Rumble history (reverse-indexed from the same per-event entrant data the
Events page uses), any notable_moments they're involved in, and any all-time
records they personally hold (Field composition records are event-level, not
personal, so they're excluded here -- see field_composition_members instead).

DIVISION SPLIT (2026-09-20): per Shane's instruction "I think I want all of
the woman's stats and info completely separate to the man's", the top-level
output is now a `divisions` array -- one entry per division (Men's Royal
Rumble, Women's Royal Rumble), each carrying its OWN fully independent
`events`, `records` and `wrestlers` lists, built only from that division's
own events/entrants/eliminations/career_stats/records rows. Nothing here is
blended across divisions.

wrestlers.csv itself stays one shared identity table -- a performer who has
wrestled in both divisions (e.g. Beth Phoenix: Men's 2010, Women's 2018)
keeps ONE wrestler_id and appears once in EACH division's `wrestlers` array,
with two fully independent stat lines (her Men's numbers, her Women's
numbers -- never summed together). Each such entry also carries an
`otherDivision` cross-link so the dashboard can point from one of her
division profiles to the other, the same way `samePerformer` already
cross-links different wrestler_ids that are the same real person under
different gimmick eras (that feature is division-scoped too now: a sibling
only shows up in a division's list if they themselves have a stat line in
that same division). See IDEAS.md for the full write-up of this change.
"""
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from schema import slugify

DATA_DIR = sys.argv[1] if len(sys.argv) > 1 else "data"
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "dashboard/data.json"


def load(fname):
    with open(os.path.join(DATA_DIR, fname), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def i(v, default=None):
    v = (v or "").strip()
    if not v:
        return default
    try:
        return int(v)
    except ValueError:
        try:
            return int(float(v))
        except ValueError:
            return default


def f(v, default=None):
    v = (v or "").strip()
    if not v:
        return default
    try:
        return float(v)
    except ValueError:
        return default


def trim(s, n):
    s = (s or "").strip()
    if len(s) <= n:
        return s
    return s[: n - 1].rsplit(" ", 1)[0] + "…"


wrestlers = load("wrestlers.csv")
events = load("events.csv")
entrants = load("entrants.csv")
entrance_timings = load("entrances.csv")
eliminations = load("eliminations.csv")
records = load("derived/records.csv")
career = load("derived/career_stats.csv")
rivalries = load("derived/elimination_rivalries.csv")
entry_number_stats = load("derived/entry_number_stats.csv")
ring_occupancy_stats = load("derived/ring_occupancy_stats.csv")
ring_crowdedness = load("derived/ring_crowdedness.csv")
ring_physical_peaks = load("derived/ring_physical_peaks.csv")
entrance_event_stats = load("derived/entrance_event_stats.csv")
event_field_physical_stats = load("derived/event_field_physical_stats.csv")
try:
    event_nationality_breakdown = load("derived/event_nationality_breakdown.csv")
except FileNotFoundError:
    event_nationality_breakdown = []
try:
    card_dual_duty = load("derived/card_dual_duty.csv")
    card_non_rumble_regulars = load("derived/card_non_rumble_regulars.csv")
    commentator_stats = load("derived/commentator_stats.csv")
    card_match_type_frequency = load("derived/card_match_type_frequency.csv")
    card_title_frequency = load("derived/card_title_frequency.csv")
except FileNotFoundError:
    card_dual_duty = card_non_rumble_regulars = commentator_stats = []
    card_match_type_frequency = card_title_frequency = []
flags = load("flags.csv")
try:
    event_winners = load("event_winners.csv")
except FileNotFoundError:
    event_winners = []
try:
    notable_moments = load("notable_moments.csv")
except FileNotFoundError:
    notable_moments = []
try:
    event_ratings = load("event_ratings.csv")
except FileNotFoundError:
    event_ratings = []
try:
    promotions = load("promotions.csv")
    championships = load("championships.csv")
    championship_reigns = load("championship_reigns.csv")
except FileNotFoundError:
    promotions, championships, championship_reigns = [], [], []

wrestlers_by_id = {w["wrestler_id"]: w for w in wrestlers}
events_by_id = {ev["event_id"]: ev for ev in events}


def division_of(event_id):
    return events_by_id[event_id]["match_type"]


DIVISIONS = sorted(set(ev["match_type"] for ev in events))
DIV_KEY = {d: slugify(d) for d in DIVISIONS}
DIV_LABEL = {d: f"{d} Royal Rumble" for d in DIVISIONS}

# Entrants who were drawn/advertised but never actually entered the ring at all
# (storyline-attacked, withdrew, substituted before their entrance) -- mirrors
# build_derived.py's own NEVER_ENTERED set so the dashboard doesn't misrepresent
# these as unrecorded elimination-credit gaps.
NEVER_ENTERED = {
    ("RR1991M", "randy-savage"), ("RR1994M", "bastion-booger"), ("RR1998M", "skull"),
    ("RR2004M", "spike-dudley"), ("RR2004M", "test"), ("RR2005M", "scott-taylor"),
    ("RR2008M", "finlay"), ("RR2015M", "curtis-axel"),
}

wname = {w["wrestler_id"]: w["ring_name"] for w in wrestlers}

# Display name for cross-era views (leaderboards, "eliminated by" links): prefer
# the ring name they were MOST OFTEN billed under across their Rumble history,
# not wrestlers.csv's static ring_name field, which sometimes just reflects
# their first Rumble appearance (e.g. wrestler_id "steve-austin" -> ring_name
# "The Ringmaster", his 1996 gimmick, despite 5 later appearances as "Steve
# Austin"). "Most recent" was tried first and rejected: it picks up one-off
# in-broadcast shorthand like Jake Roberts's 1997 entrant row, billed just
# "Roberts" that one night against 6 other appearances as "Jake Roberts".
# Ties broken by most recent. This is a display-only choice for the dashboard
# -- wrestlers.csv itself is untouched. Division-agnostic on purpose: a
# performer's display name doesn't change depending on which division's page
# you're looking at them from.
event_year = {ev["event_id"]: ev.get("event_date", "")[:4] for ev in events}
name_counts = {}  # wid -> {ring_name: [count, most_recent_year]}
for r in entrants:
    wid = r["wrestler_id"]
    rn = (r.get("ring_name_at_time") or "").strip()
    if not rn:
        continue
    yr = event_year.get(r["event_id"], "")
    bucket = name_counts.setdefault(wid, {})
    entry = bucket.setdefault(rn, [0, ""])
    entry[0] += 1
    entry[1] = max(entry[1], yr)

display_name = {}
for wid, bucket in name_counts.items():
    best = max(bucket.items(), key=lambda kv: (kv[1][0], kv[1][1]))
    display_name[wid] = best[0]


def name(wid):
    return display_name.get(wid) or wname.get(wid, wid)


# ---------------------------------------------------------------------------
# Per-(event, victim) elimination detail: contributors + a short sourced
# narrative snippet (if any) + the data-quality status of that specific
# credit -- this is the project's own CONFIRMED/PROBABLE/etc rigor, worth
# surfacing rather than flattening away. Keyed by event_id, so it's already
# naturally division-scoped (an event belongs to exactly one division).
# ---------------------------------------------------------------------------
elim_detail = {}  # (event_id, victim) -> dict
for e in eliminations:
    key = (e["event_id"], e["eliminated_wrestler_id"])
    d = elim_detail.setdefault(key, {
        "by": [], "quality": e.get("data_quality_status") or "",
        "method": "", "disputed": False,
    })
    if e["eliminator_wrestler_id"] and e["eliminator_wrestler_id"] not in d["by"]:
        d["by"].append(e["eliminator_wrestler_id"])
    for a in filter(None, e.get("assisting_wrestler_ids", "").split(";")):
        if a not in d["by"]:
            d["by"].append(a)
    method = (e.get("elimination_method") or "").strip()
    if method and method != "UNKNOWN" and not d["method"]:
        d["method"] = trim(method, 220)
    if (e.get("is_disputed") or "").upper() == "TRUE":
        d["disputed"] = True
    # weakest-wins ordering isn't needed -- CONFIRMED beats PROBABLE beats blank
    order = {"CONFIRMED": 3, "PROBABLE": 2, "UNCERTAIN": 1}
    if order.get((e.get("data_quality_status") or "").upper(), 0) > order.get(d["quality"].upper() if d["quality"] else "", 0):
        d["quality"] = e.get("data_quality_status") or d["quality"]

# ---------------------------------------------------------------------------
# Events + per-event entrants (the timeline data)
# ---------------------------------------------------------------------------
entrants_by_event = {}
for e in entrants:
    entrants_by_event.setdefault(e["event_id"], []).append(e)

# ---------------------------------------------------------------------------
# Notable moments ("weird and wonderful" trivia that doesn't reduce to a
# single leaderboard number) -- grouped by event for the event detail page,
# and by (wrestler, division) for the wrestler profile page.
# ---------------------------------------------------------------------------
moments_by_event = {}
moments_by_wrestler_div = {}
for m in notable_moments:
    wids = [w for w in (m.get("wrestler_ids_involved") or "").split(";") if w]
    entry = {
        "title": m.get("title") or None,
        "description": m.get("description") or None,
        "category": m.get("category") or None,
        "quality": m.get("data_quality_status") or None,
        "wrestlers": [{"id": w, "name": name(w)} for w in wids],
    }
    eid = m["event_id"]
    moments_by_event.setdefault(eid, []).append(entry)
    div = division_of(eid)
    for w in wids:
        moments_by_wrestler_div.setdefault((w, div), []).append(dict(entry, eventId=eid))

ratings_by_event = {}
for rating in event_ratings:
    ratings_by_event.setdefault(rating["event_id"], []).append({
        "source": rating.get("source_name") or None,
        "scale": rating.get("rating_scale") or None,
        "value": rating.get("rating_value") or None,
        "type": rating.get("rating_type") or None,
        "url": rating.get("review_url") or None,
        "quality": rating.get("rating_status") or None,
        "notes": rating.get("notes") or None,
    })

occupancy_by_event = {r["event_id"]: r for r in ring_occupancy_stats}
entrance_stats_by_event = {r["event_id"]: r for r in entrance_event_stats}
entrance_timing_by_event_wrestler = {
    (r["event_id"], r["wrestler_id"]): r for r in entrance_timings
}
crowdedness_by_event = defaultdict(list)
for r in ring_crowdedness:
    crowdedness_by_event[r["event_id"]].append(r)
for eid in crowdedness_by_event:
    crowdedness_by_event[eid].sort(key=lambda r: int(r["in_ring_count"]))
physical_peaks_by_event = defaultdict(dict)
for r in ring_physical_peaks:
    physical_peaks_by_event[r["event_id"]][r["metric"]] = r
field_physical_by_event = {r["event_id"]: r for r in event_field_physical_stats}
nationality_by_event = defaultdict(list)
for r in event_nationality_breakdown:
    if r.get("nationality"):
        nationality_by_event[r["event_id"]].append(r)
for eid in nationality_by_event:
    nationality_by_event[eid].sort(key=lambda r: -int(r["entrant_count"]))

events_by_division = {d: [] for d in DIVISIONS}
history_by_wrestler_div = {}  # (wid, division) -> [ {eventId, year, ...entrant summary...} ]
# Almost every event has exactly one winner (events.csv:winner_id). RR1994M
# is the one documented exception (events.csv:finish_type == "co_winners"),
# whose declared winner set lives in event_winners.csv instead -- see
# schema.py's EVENT_WINNERS_FIELDS comment for why.
event_winners_by_event = {}
for r in event_winners:
    event_winners_by_event.setdefault(r["event_id"], []).append(r["wrestler_id"])
for ev in events:
    eid = ev["event_id"]
    div = ev["match_type"]
    rows = entrants_by_event.get(eid, [])
    ev_year = i(ev.get("event_date", "")[:4]) or i(eid.replace("RR", "").rstrip("MWG"))
    ev_match_name = ev.get("match_name")

    ent_out = []
    for r in rows:
        wid = r["wrestler_id"]
        entrance_timing = entrance_timing_by_event_wrestler.get((eid, wid), {})
        detail = elim_detail.get((eid, wid), {})
        badges = []
        for flag, label in (
            ("surprise_entrant", "Surprise"),
            ("legend_returning", "Legend returning"),
            ("celebrity_entrant", "Celebrity"),
            ("non_full_time_wrestler", "Part-timer"),
            ("was_hof_member_at_time", "HOF member"),
            ("is_rumble_debut", "Rumble debut"),
            ("is_company_debut", "WWE debut"),
            ("is_returning_wrestler", "Return"),
            ("wrestled_earlier_on_card", "Wrestled earlier on card"),
        ):
            if (r.get(flag) or "").upper() == "TRUE":
                badges.append(label)
        never_entered = (eid, wid) in NEVER_ENTERED
        if never_entered:
            badges.append("Never entered")
        champion_title = (r.get("current_champion_title") or "").strip()
        champion = None
        if champion_title not in ("", "N/A", "UNKNOWN"):
            badges.append("Champion")
            champion = {
                "title": champion_title,
                "level": (r.get("championship_level") or "").strip() or None,
                "partner": None if r.get("championship_partner") in (None, "", "N/A", "UNKNOWN") else r.get("championship_partner"),
                "reignNumber": i(r.get("reign_number")),
                "wonDate": None if r.get("title_won_date") in (None, "", "N/A", "UNKNOWN") else r.get("title_won_date"),
                "daysIntoReign": i(r.get("days_into_reign_at_event")),
                "defendedSameCard": (r.get("title_defended_same_card") or "").upper() == "TRUE",
                "lostSameCard": (r.get("title_lost_same_card") or "").upper() == "TRUE",
            }
        title_lost_same_card = (r.get("title_lost_same_card") or "").upper() == "TRUE"
        title_defended_same_card = (r.get("title_defended_same_card") or "").upper() == "TRUE"
        if title_lost_same_card and champion is None:
            badges.append("Lost title earlier")
        physical_profile = {
            "age": None if r.get("age_at_event") in (None, "", "N/A", "UNKNOWN") else r.get("age_at_event"),
            "ageStatus": (r.get("age_status") or "").strip() or None,
            "heightM": None if r.get("billed_height_m_at_event") in (None, "", "N/A", "UNKNOWN") else r.get("billed_height_m_at_event"),
            "weightKg": None if r.get("billed_weight_kg_at_event") in (None, "", "N/A", "UNKNOWN") else r.get("billed_weight_kg_at_event"),
            "billedFrom": None if r.get("billed_from_at_event") in (None, "", "N/A", "UNKNOWN") else r.get("billed_from_at_event"),
            "status": (r.get("physical_status") or "").strip() or None,
        }
        character_profile = {
            "alignment": None if r.get("alignment") in (None, "", "N/A", "UNKNOWN") else r.get("alignment"),
            "alignmentStatus": (r.get("alignment_status") or "").strip() or None,
            "gimmick": None if r.get("gimmick_at_event") in (None, "", "N/A", "UNKNOWN") else r.get("gimmick_at_event"),
            "manager": None if r.get("manager_at_event") in (None, "", "N/A", "UNKNOWN") else r.get("manager_at_event"),
            "tagTeam": None if r.get("tag_team_name") in (None, "", "N/A", "UNKNOWN") else r.get("tag_team_name"),
            "faction": None if r.get("faction_stable") in (None, "", "N/A", "UNKNOWN") else r.get("faction_stable"),
        }
        ent_out.append({
            "id": wid,
            "name": r.get("ring_name_at_time") or name(wid),
            "entry": i(r.get("entry_number")),
            "elimNum": i(r.get("elim_number")),
            "elimTime": r.get("elimination_clock_time") or None,
            "elimSec": i(r.get("elimination_clock_seconds")),
            "ringTime": None if never_entered else (r.get("ring_time") or None),
            "ringSec": None if never_entered else i(r.get("ring_time_seconds")),
            "by": [{"id": b, "name": name(b)} for b in detail.get("by", [])],
            "method": detail.get("method") or None,
            "quality": detail.get("quality") or None,
            "disputed": detail.get("disputed", False),
            "isWinner": (r.get("is_winner") or "").upper() == "TRUE",
            "isRunnerUp": (r.get("is_runner_up") or "").upper() == "TRUE",
            "isSelf": (r.get("self_eliminated") or "").upper() == "TRUE",
            "neverEntered": never_entered,
            "elimsMade": i(r.get("wrestlers_eliminated_count")),
            "badges": badges,
            "appearanceNo": i(r.get("rumble_appearance_no")),
            "priorAppearances": i(r.get("prior_rumble_appearances_count")),
            "isRumbleDebut": (r.get("is_rumble_debut") or "").upper() == "TRUE",
            "isCompanyDebut": (r.get("is_company_debut") or "").upper() == "TRUE",
            "companyDebutDate": None if r.get("company_debut_date") in (None, "", "N/A", "UNKNOWN") else r.get("company_debut_date"),
            "isReturning": (r.get("is_returning_wrestler") or "").upper() == "TRUE",
            "absenceLength": None if r.get("absence_length") in (None, "", "N/A", "UNKNOWN") else r.get("absence_length"),
            "championship": champion,
            "titleDefendedSameCard": title_defended_same_card,
            "titleLostSameCard": title_lost_same_card,
            "physicalProfile": physical_profile,
            "characterProfile": character_profile,
            "entranceCountdown": entrance_timing.get("countdown_ts") or None,
            "entersRing": entrance_timing.get("enters_ring_ts") or None,
            "entranceDurationSec": i(entrance_timing.get("entrance_duration_seconds")),
        })
        history_by_wrestler_div.setdefault((wid, div), []).append({
            "eventId": eid,
            "year": ev_year,
            "matchName": ev_match_name,
            "entry": ent_out[-1]["entry"],
            "elimNum": ent_out[-1]["elimNum"],
            "elimTime": ent_out[-1]["elimTime"],
            "ringTime": ent_out[-1]["ringTime"],
            "by": ent_out[-1]["by"],
            "isWinner": ent_out[-1]["isWinner"],
            "isRunnerUp": ent_out[-1]["isRunnerUp"],
            "isSelf": ent_out[-1]["isSelf"],
            "neverEntered": never_entered,
            "elimsMade": ent_out[-1]["elimsMade"],
            "badges": badges,
            "appearanceNo": ent_out[-1]["appearanceNo"],
            "priorAppearances": ent_out[-1]["priorAppearances"],
            "isRumbleDebut": ent_out[-1]["isRumbleDebut"],
            "isCompanyDebut": ent_out[-1]["isCompanyDebut"],
            "companyDebutDate": ent_out[-1]["companyDebutDate"],
            "isReturning": ent_out[-1]["isReturning"],
            "absenceLength": ent_out[-1]["absenceLength"],
            "championship": ent_out[-1]["championship"],
            "titleDefendedSameCard": ent_out[-1]["titleDefendedSameCard"],
            "titleLostSameCard": ent_out[-1]["titleLostSameCard"],
            "physicalProfile": ent_out[-1]["physicalProfile"],
            "characterProfile": ent_out[-1]["characterProfile"],
        })
    # sort by entry number for the roster view; elimination order derived client-side
    ent_out.sort(key=lambda x: (x["entry"] is None, x["entry"]))

    attendance = i(ev.get("attendance_official")) or i(ev.get("attendance_reported"))
    # "winners" is the full declared-winner list (2 entries for RR1994M's
    # co-winner finish, 1 for every other event); "winner" stays as its first
    # entry so any consumer that only ever expected one keeps working.
    if ev.get("finish_type") == "co_winners" and eid in event_winners_by_event:
        winners_list = [{"id": wid, "name": name(wid)} for wid in event_winners_by_event[eid]]
    elif ev.get("winner_id"):
        winners_list = [{"id": ev.get("winner_id"), "name": name(ev.get("winner_id"))}]
    else:
        winners_list = []
    entrance_summary = entrance_stats_by_event.get(eid)
    field_physical = field_physical_by_event.get(eid, {})
    events_by_division[div].append({
        "id": eid,
        "year": ev_year,
        "name": ev.get("event_name"),
        "matchName": ev.get("match_name"),
        "date": ev.get("event_date"),
        "venue": ev.get("venue"),
        "city": ev.get("city_region"),
        "country": ev.get("country"),
        "attendance": attendance,
        "duration": ev.get("duration_total") or None,
        "entrantCount": i(ev.get("entrant_count")) or len(rows),
        "elimsCount": i(ev.get("eliminations_count")),
        "entryInterval": i(ev.get("entry_interval_seconds")),
        "championsInField": i(ev.get("champions_in_field_count")),
        "returningCount": sum(1 for r in ent_out if r.get("isReturning")),
        "fieldPhysical": ({
            "actualEntrants": i(field_physical.get("actual_entrant_count")),
            "combinedWeightKg": f(field_physical.get("combined_billed_weight_kg")),
            "averageWeightKg": f(field_physical.get("average_billed_weight_kg")),
            "combinedHeightM": f(field_physical.get("combined_billed_height_m")),
            "averageHeightM": f(field_physical.get("average_billed_height_m")),
            "weightCoveragePct": f(field_physical.get("weight_coverage_percentage")),
            "heightCoveragePct": f(field_physical.get("height_coverage_percentage")),
        } if field_physical else None),
        "nationalityBreakdown": ([
            {"nationality": r["nationality"], "count": i(r["entrant_count"]), "pctOfKnown": f(r["percentage_of_known"])}
            for r in nationality_by_event.get(eid, [])
        ] if nationality_by_event.get(eid) else None),
        "nationalityCoveragePct": (f(nationality_by_event[eid][0].get("coverage_percentage")) if nationality_by_event.get(eid) else None),
        "winner": winners_list[0] if winners_list else None,
        "winners": winners_list,
        "runnerUp": {"id": ev.get("runner_up_id"), "name": name(ev.get("runner_up_id"))} if ev.get("runner_up_id") else None,
        "significance": trim(ev.get("historical_significance"), 320) or None,
        "quality": ev.get("data_quality_status") or None,
        "entrants": ent_out,
        "notableMoments": moments_by_event.get(eid, []),
        "ratings": ratings_by_event.get(eid, []),
        "occupancy": ({
            "peakCount": i(occupancy_by_event[eid].get("peak_in_ring_count")),
            "startSec": i(occupancy_by_event[eid].get("peak_start_seconds")),
            "endSec": i(occupancy_by_event[eid].get("peak_end_seconds")),
            "startTime": occupancy_by_event[eid].get("peak_start_time") or None,
            "endTime": occupancy_by_event[eid].get("peak_end_time") or None,
            "wrestlers": [
                {"id": wid, "name": name(wid)}
                for wid in (occupancy_by_event[eid].get("wrestler_ids_at_peak") or "").split(";") if wid
            ],
            "quality": occupancy_by_event[eid].get("data_quality_status") or None,
        } if eid in occupancy_by_event else None),
        "crowdedness": ([
            {
                "count": i(r["in_ring_count"]),
                "seconds": i(r["seconds_at_count"]),
                "time": r.get("time_at_count") or None,
                "pct": float(r["percentage_of_match_time"]) if r.get("percentage_of_match_time") not in (None, "") else None,
            }
            for r in crowdedness_by_event[eid]
        ] if eid in crowdedness_by_event else None),
        "physicalPeaks": ({
            metric: {
                "value": float(r["peak_value"]),
                "unit": r.get("unit") or None,
                "startTime": r.get("peak_start_time") or None,
                "endTime": r.get("peak_end_time") or None,
                "wrestlers": [
                    {"id": wid, "name": name(wid)}
                    for wid in (r.get("wrestler_ids_at_peak") or "").split(";") if wid
                ],
                "quality": r.get("data_quality_status") or None,
            }
            for metric, r in physical_peaks_by_event.get(eid, {}).items()
        } or None),
        "entranceStats": ({
            "rows": i(entrance_summary.get("entrance_rows_count")),
            "timed": i(entrance_summary.get("timed_entrance_count")),
            "medianSec": f(entrance_summary.get("median_entrance_duration_seconds")),
            "median": entrance_summary.get("median_entrance_duration") or None,
            "averageSec": f(entrance_summary.get("average_entrance_duration_seconds")),
            "shortestSec": i(entrance_summary.get("shortest_entrance_seconds")),
            "longestSec": i(entrance_summary.get("longest_entrance_seconds")),
            "latestPhysicalSec": i(entrance_summary.get("latest_physical_entry_seconds")),
            "latestPhysical": entrance_summary.get("latest_physical_entry_time") or None,
            "latestPhysicalWrestler": ({
                "id": entrance_summary.get("latest_physical_entry_wrestler_id"),
                "name": name(entrance_summary.get("latest_physical_entry_wrestler_id")),
            } if entrance_summary.get("latest_physical_entry_wrestler_id") else None),
            "advertisedIntervalSec": i(entrance_summary.get("advertised_interval_seconds")),
            "intervalSample": i(entrance_summary.get("interval_sample_size")),
            "medianActualIntervalSec": f(entrance_summary.get("median_actual_interval_seconds")),
            "largestVarianceSec": i(entrance_summary.get("largest_interval_variance_seconds")),
            "largestVarianceActualSec": i(entrance_summary.get("largest_interval_actual_seconds")),
            "largestVarianceWrestler": ({
                "id": entrance_summary.get("largest_interval_variance_wrestler_id"),
                "name": name(entrance_summary.get("largest_interval_variance_wrestler_id")),
            } if entrance_summary.get("largest_interval_variance_wrestler_id") else None),
        } if entrance_summary else None),
    })

for d in DIVISIONS:
    events_by_division[d].sort(key=lambda x: x["year"] or 0)
for key in history_by_wrestler_div:
    history_by_wrestler_div[key].sort(key=lambda x: x["year"] or 0)

# ---------------------------------------------------------------------------
# Host location statistics, PER DIVISION. Venue identity is scoped by its
# city/country so arenas with reused names in different places never merge.
# City identity is the existing city_region + country text exactly as stored;
# no geocoding or inferred normalization is introduced.
# ---------------------------------------------------------------------------
locations_by_division = {}
for d in DIVISIONS:
    venue_groups = {}
    city_groups = {}
    for ev in events_by_division[d]:
        event_ref = {
            "id": ev["id"], "year": ev["year"], "attendance": ev["attendance"],
            "winners": ev["winners"],
        }
        if ev.get("venue"):
            key = (ev["venue"], ev.get("city") or "", ev.get("country") or "")
            group = venue_groups.setdefault(key, {
                "name": ev["venue"], "city": ev.get("city") or None,
                "country": ev.get("country") or None, "events": [],
            })
            group["events"].append(event_ref)
        if ev.get("city"):
            key = (ev["city"], ev.get("country") or "")
            group = city_groups.setdefault(key, {
                "name": ev["city"], "country": ev.get("country") or None, "events": [],
            })
            group["events"].append(event_ref)

    def finish_location_group(group):
        group["events"].sort(key=lambda x: (x["year"] or 0, x["id"]))
        years = [e["year"] for e in group["events"] if e["year"]]
        attendance = [e["attendance"] for e in group["events"] if e["attendance"]]
        group["eventCount"] = len(group["events"])
        group["firstYear"] = min(years) if years else None
        group["lastYear"] = max(years) if years else None
        group["knownAttendanceTotal"] = sum(attendance) if attendance else None
        group["attendanceEvents"] = len(attendance)
        return group

    venues = [finish_location_group(g) for g in venue_groups.values()]
    cities = [finish_location_group(g) for g in city_groups.values()]
    venues.sort(key=lambda g: (-g["eventCount"], g["name"].lower(), (g.get("city") or "").lower()))
    cities.sort(key=lambda g: (-g["eventCount"], g["name"].lower()))
    locations_by_division[d] = {"venues": venues, "cities": cities}

# ---------------------------------------------------------------------------
# Records -- records.csv is already division-tagged by build_derived.py, so
# this is a straight group-by.
# ---------------------------------------------------------------------------
# records.csv's free-text notes sometimes embed raw wrestler_ids (e.g. a
# multi-contributor list) rather than display names -- resolve any that
# appear as their own token so the dashboard never shows "booker-t" beside
# "Booker T" in the same sentence.
_wid_pattern = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in sorted(wname, key=len, reverse=True)) + r")\b"
)


def resolve_ids_in_text(text):
    if not text:
        return text
    return _wid_pattern.sub(lambda m: name(m.group(1)), text)


# "Field composition" records count members of one event's field against a
# per-wrestler condition (hall_of_fame_year / deceased_date) rather than
# naming a single holder -- holder_wrestler_id is blank for these in
# records.csv. Recompute the actual member list here (not stored in
# records.csv itself) so the dashboard can show who's actually behind the
# number, not just the count -- Shane asked for this after the hall_of_fame_
# year fact-check (see F333) made clear a raw count alone invites exactly the
# kind of silent data error that pass caught.
def field_composition_members(record):
    if record.get("category") != "Field composition":
        return None
    eid = record.get("event_id")
    if not eid:
        return None
    field = entrants_by_event.get(eid, [])
    rname = record.get("record_name") or ""
    if "Hall of Fame" in rname:
        rows = [
            (wrestlers_by_id[e["wrestler_id"]]["hall_of_fame_year"], e["wrestler_id"])
            for e in field
            if wrestlers_by_id.get(e["wrestler_id"], {}).get("hall_of_fame_year")
        ]
        rows.sort(key=lambda t: t[0])
        return [{"id": wid, "name": name(wid), "detail": "HOF " + yr} for yr, wid in rows]
    if "deceased" in rname:
        rows = [
            (wrestlers_by_id[e["wrestler_id"]]["deceased_date"], e["wrestler_id"])
            for e in field
            if wrestlers_by_id.get(e["wrestler_id"], {}).get("deceased_date")
        ]
        rows.sort(key=lambda t: t[0])
        return [{"id": wid, "name": name(wid), "detail": "d. " + dt} for dt, wid in rows]
    return None


records_by_division = {d: [] for d in DIVISIONS}
for r in records:
    div = r.get("division") or (division_of(r["event_id"]) if r.get("event_id") else None)
    out_r = {
        "id": r["record_id"],
        "category": r.get("category"),
        "name": r.get("record_name"),
        "holder": {"id": r.get("holder_wrestler_id"), "name": name(r.get("holder_wrestler_id"))},
        "value": r.get("value"),
        "eventId": r.get("event_id") or None,
        "notes": trim(resolve_ids_in_text(r.get("notes")), 320) or None,
        "members": field_composition_members(r),
    }
    records_by_division.setdefault(div, []).append(out_r)

# Reverse index: which records each wrestler personally holds, PER DIVISION
# (skips the "Field composition" records, which belong to an EVENT's field,
# not a person -- those wrestlers already surface via "members" above, not
# as a personal record credit). A rivalry-pairing record ("hulk-hogan ->
# the-warlord") counts for both named wrestlers.
records_by_wrestler_div = {}
for div, rs in records_by_division.items():
    for r in rs:
        hid = (r["holder"] or {}).get("id") or ""
        if not hid or r["category"] == "Field composition":
            continue
        for wid in [p.strip() for p in hid.split("->")]:
            if wid and wid in wrestlers_by_id:
                records_by_wrestler_div.setdefault((wid, div), []).append({
                    "id": r["id"], "name": r["name"], "value": r["value"], "category": r["category"],
                })

# ---------------------------------------------------------------------------
# Reverse index: elimination_rivalries.csv (every eliminator/eliminated pair
# that's happened more than once), PER DIVISION, split into "who I've
# repeatedly eliminated" and "who's repeatedly eliminated me" for each
# wrestler. Filtered to times_eliminated >= 2 -- a single past elimination
# isn't a rivalry, it's just one row of the wrestler's own history table
# (already shown there); this panel is specifically for the repeat matchups.
# Top 6 each, by times_eliminated desc then most-recent-first, so a
# wrestler with a long career doesn't get an unreadably long panel.
rivalries_as_eliminator = {}
rivalries_as_victim = {}
for r in rivalries:
    div = r["division"]
    times = i(r.get("times_eliminated"), 0)
    if times < 2:
        continue
    elor, elee = r["eliminator_wrestler_id"], r["eliminated_wrestler_id"]
    if elor in wrestlers_by_id and elee in wrestlers_by_id:
        rivalries_as_eliminator.setdefault((elor, div), []).append({
            "id": elee, "name": name(elee), "times": times,
            "firstEventId": r.get("first_event_id"), "mostRecentEventId": r.get("most_recent_event_id"),
        })
        rivalries_as_victim.setdefault((elee, div), []).append({
            "id": elor, "name": name(elor), "times": times,
            "firstEventId": r.get("first_event_id"), "mostRecentEventId": r.get("most_recent_event_id"),
        })
for d in rivalries_as_eliminator.values():
    d.sort(key=lambda x: x["mostRecentEventId"] or "", reverse=True)  # tiebreak: most recent first
    d.sort(key=lambda x: x["times"], reverse=True)  # stable sort, so ties keep the line above's order
for d in rivalries_as_victim.values():
    d.sort(key=lambda x: x["mostRecentEventId"] or "", reverse=True)
    d.sort(key=lambda x: x["times"], reverse=True)
rivalries_as_eliminator = {k: v[:6] for k, v in rivalries_as_eliminator.items()}
rivalries_as_victim = {k: v[:6] for k, v in rivalries_as_victim.items()}

# ---------------------------------------------------------------------------
# Same-performer identity groups: one real person under several wrestler_ids
# across different gimmick eras (Glenn Jacobs as Isaac Yankem -> Fake Diesel
# -> Kane; John Tenta as Earthquake and Golga; the Big Boss Man split across
# its two eras; etc). This database deliberately keeps each gimmick era as
# its own row (matches WWE's own official-record convention, and Mick
# Foley's 3-gimmicks-in-one-night F111 is the clearest reason why merging
# rows outright isn't safe) -- but left un-cross-linked, these look like
# unrelated people competing for the same leaderboard spot, which is exactly
# the "duplication" concern this was built to answer. The match here is
# real_name equality (normalized: lowercased, punctuation stripped, but
# generational suffixes like "Jr."/"Sr." are KEPT so a father and son with
# the same name -- e.g. Ted DiBiase / Ted DiBiase Jr. -- are never conflated)
# plus a DOB-conflict check across the group: any two non-blank DOBs that
# disagree kill the match rather than risk a false merge. This is a strictly
# HIGHER bar than a same-string real_name match alone, and deliberately
# stays silent on cases this database's own sourcing hasn't confirmed --
# e.g. "doink"/"doink-1995" are a documented PROBABLE same-performer
# candidate (see flags F095/F096) but blank real_name on doink-1995 means
# they don't clear this bar, so they're correctly left unlinked here rather
# than asserted with more confidence than the database itself has.
#
# This identity linking is computed globally (it's about who a person IS,
# not which division they wrestled in) -- the DIVISION SPLIT below only
# affects which of a wrestler's siblings actually get shown as a link in a
# given division's wrestler list (a sibling with no stat line in THIS
# division would be a dead-end link there).
def _norm_real_name(s):
    s = (s or "").strip().lower()
    return re.sub(r"[^a-z0-9\s]", " ", s)
    # (whitespace collapse happens in the join below)


_SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}


def _tokens_no_suffix(s):
    toks = _norm_real_name(s).split()
    return [t for t in toks if t not in _SUFFIXES]


_by_real_name = {}
for w in wrestlers:
    rn = (w.get("real_name") or "").strip()
    if not rn:
        continue
    key = " ".join(_norm_real_name(rn).split())
    _by_real_name.setdefault(key, []).append(w)

# Union-find over wrestler_ids so an exact-match pair and a fuzzy-match pair
# that share a member end up in one combined group (e.g. if A==B exactly and
# B~C fuzzily, A/B/C are all the same performer).
_parent = {}


def _find(x):
    _parent.setdefault(x, x)
    while _parent[x] != x:
        _parent[x] = _parent[_parent[x]]
        x = _parent[x]
    return x


def _union(a, b):
    ra, rb = _find(a), _find(b)
    if ra != rb:
        _parent[ra] = rb


# Pass 1: exact normalized real_name match (suffixes kept, so Ted DiBiase /
# Ted DiBiase Jr. are different strings and never reach this path together).
# DOB is checked only for *conflict* here -- a blank DOB on one side doesn't
# block the match, since an identical full name string (incl. suffix) is
# already strong evidence.
for key, group in _by_real_name.items():
    ids = sorted(set(w["wrestler_id"] for w in group))
    if len(ids) < 2:
        continue
    dobs = set(w["dob"].strip() for w in group if (w.get("dob") or "").strip())
    if len(dobs) > 1:
        continue  # DOB conflict -- e.g. Ted DiBiase vs Ted DiBiase Jr. -- not the same person
    for wid in ids[1:]:
        _union(ids[0], wid)

# Pass 2: fuzzy match for names that *aren't* identical strings but are
# plainly the same person under a fuller/shorter form of their name -- e.g.
# golga's real_name "John Tenta" vs earthquake's "John Anthony Tenta Jr."
# (a middle name and a generational suffix added). Because name-only evidence
# is weaker here, this path requires BOTH DOBs present and EQUAL (not just
# non-conflicting) as well as first- and last-token agreement plus a full
# token-subset relationship, to avoid false positives like two wrestlers who
# happen to share a first and last name.
_wid_dob = {w["wrestler_id"]: (w.get("dob") or "").strip() for w in wrestlers}
_wid_realname = {w["wrestler_id"]: (w.get("real_name") or "").strip() for w in wrestlers}
_candidates = [w for w in wrestlers if (w.get("real_name") or "").strip() and _wid_dob.get(w["wrestler_id"])]
for idx, w1 in enumerate(_candidates):
    id1 = w1["wrestler_id"]
    dob1 = _wid_dob[id1]
    toks1 = _tokens_no_suffix(_wid_realname[id1])
    if not toks1:
        continue
    for w2 in _candidates[idx + 1:]:
        id2 = w2["wrestler_id"]
        if _wid_dob[id2] != dob1:
            continue
        toks2 = _tokens_no_suffix(_wid_realname[id2])
        if not toks2 or toks1 == toks2:
            continue  # identical (post-suffix-strip) already handled by pass 1
        if toks1[0] != toks2[0] or toks1[-1] != toks2[-1]:
            continue  # first/last name must agree
        set1, set2 = set(toks1), set(toks2)
        if set1 <= set2 or set2 <= set1:
            _union(id1, id2)

same_performer = {}  # wid -> [sibling wid, ...]
_groups = {}
for wid in _parent:
    _groups.setdefault(_find(wid), set()).add(wid)
for root, ids in _groups.items():
    if len(ids) < 2:
        continue
    ids = sorted(ids)
    for wid in ids:
        same_performer[wid] = [x for x in ids if x != wid]

# ---------------------------------------------------------------------------
# Per-division wrestler tables (career_stats.csv, joined to wrestler bios,
# division-scoped Rumble history, notable moments and records held).
# career_stats.csv now carries one row per (wrestler_id, division) --
# Beth Phoenix produces two separate rows/entries here, one under Men's
# (her 2010 appearance) and one under Women's (her 2018 appearance), never
# a single blended line.
# ---------------------------------------------------------------------------
career_by_wid_div = {(c["wrestler_id"], c["division"]): c for c in career}
_FINISH_RANK = {"Winner": 3, "Runner-up": 2, "Final Four": 1}


def _combined_stats(wid, division, siblings):
    """Blended totals across gimmick-era sibling ids, WITHIN one division only."""
    ids = [wid] + siblings
    rows = [career_by_wid_div[(x, division)] for x in ids if (x, division) in career_by_wid_div]
    if len(rows) < 2:
        return None
    app = sum(i(r.get("total_appearances"), 0) for r in rows)
    elims = sum(i(r.get("total_eliminations_made"), 0) for r in rows)
    wins = sum(i(r.get("wins"), 0) for r in rows)
    ring = sum(i(r.get("total_ring_time_seconds"), 0) for r in rows)
    best = None
    for r in rows:
        bf = r.get("best_finish") or ""
        if _FINISH_RANK.get(bf, 0) > _FINISH_RANK.get(best or "", 0):
            best = bf
    return {
        "appearances": app,
        "wins": wins,
        "runnerUp": sum(i(r.get("runner_up_finishes"), 0) for r in rows),
        "finalFour": sum(i(r.get("final_four_count"), 0) for r in rows),
        "elims": elims,
        "maxElimsSingle": max((i(r.get("max_eliminations_single_rumble"), 0) for r in rows), default=0),
        "totalRingSec": ring,
        "avgElims": round(elims / app, 2) if app else None,
        "winPct": round(100 * wins / app, 1) if app else None,
        "longestSec": max((i(r.get("longest_single_appearance_seconds")) or 0 for r in rows), default=0) or None,
        "bestFinish": best,
    }


wrestlers_by_division = {d: [] for d in DIVISIONS}
for c in career:
    wid = c["wrestler_id"]
    div = c["division"]
    bio = wrestlers_by_id.get(wid, {})

    def bfact(field, status_field=None):
        v = (bio.get(field) or "").strip()
        if not v:
            return None
        out = {"value": v}
        if status_field:
            st = (bio.get(status_field) or "").strip()
            if st:
                out["status"] = st
        return out

    aliases = [a.strip() for a in (bio.get("aliases_ring_names") or "").split(";") if a.strip()]

    # Gimmick-era siblings that actually have a stat line in THIS division --
    # a sibling who only ever wrestled in the other division wouldn't be a
    # useful link here (nowhere for it to point within this division's own
    # wrestler list); that case is what otherDivision (below) is for instead.
    siblings_in_div = [sid for sid in same_performer.get(wid, []) if (sid, div) in career_by_wid_div]

    # Cross-link to this SAME wrestler_id's stat line in the OTHER
    # division(s) -- this is the Beth Phoenix case: one identity, two
    # independent stat lines, one per division.
    other_division_links = [
        {
            "division": od,
            "divisionKey": DIV_KEY[od],
            "divisionLabel": DIV_LABEL[od],
            "appearances": i(career_by_wid_div[(wid, od)].get("total_appearances"), 0),
            "wins": i(career_by_wid_div[(wid, od)].get("wins"), 0),
            "bestFinish": career_by_wid_div[(wid, od)].get("best_finish") or None,
            "firstYear": i(career_by_wid_div[(wid, od)].get("first_rumble_year")),
            "lastYear": i(career_by_wid_div[(wid, od)].get("last_rumble_year")),
        }
        for od in DIVISIONS if od != div and (wid, od) in career_by_wid_div
    ]

    wrestlers_by_division[div].append({
        "id": wid,
        "name": name(wid),
        "division": div,
        "divisionKey": DIV_KEY[div],
        "appearances": i(c.get("total_appearances"), 0),
        "firstYear": i(c.get("first_rumble_year")),
        "lastYear": i(c.get("last_rumble_year")),
        "wins": i(c.get("wins"), 0),
        "runnerUp": i(c.get("runner_up_finishes"), 0),
        "finalFour": i(c.get("final_four_count"), 0),
        "elims": i(c.get("total_eliminations_made"), 0),
        "avgElims": f(c.get("avg_eliminations_per_appearance")),
        "maxElimsSingle": i(c.get("max_eliminations_single_rumble"), 0),
        "totalRingSec": i(c.get("total_ring_time_seconds"), 0),
        "avgRingSec": f(c.get("avg_ring_time_seconds")),
        "longestSec": i(c.get("longest_single_appearance_seconds")),
        "avgEntry": f(c.get("avg_entry_number")),
        "elimPct": f(c.get("elimination_percentage")),
        "winPct": f(c.get("win_percentage")),
        "bestFinish": c.get("best_finish") or None,
        "bio": {
            "realName": bfact("real_name", "real_name_status"),
            "dob": bfact("dob", "dob_status"),
            "deceasedDate": (bio.get("deceased_date") or "").strip() or None,
            "birthplace": bfact("birthplace", "birthplace_status"),
            "nationality": (bio.get("nationality") or "").strip() or None,
            "ethnicityHeritage": bfact("ethnicity_heritage", "ethnicity_heritage_status"),
            "companyDebutYear": i(bio.get("debut_year_company")),
            "hallOfFameYear": (bio.get("hall_of_fame_year") or "").strip() or None,
            "wrestlingStyle": (bio.get("wrestling_style") or "").strip() or None,
            "gender": (bio.get("gender") or "").strip() or None,
            "aliases": aliases,
        },
        "history": history_by_wrestler_div.get((wid, div), []),
        "notableMoments": moments_by_wrestler_div.get((wid, div), []),
        "recordsHeld": records_by_wrestler_div.get((wid, div), []),
        "rivalries": {
            "asEliminator": rivalries_as_eliminator.get((wid, div), []),
            "asVictim": rivalries_as_victim.get((wid, div), []),
        } if rivalries_as_eliminator.get((wid, div)) or rivalries_as_victim.get((wid, div)) else None,
        "samePerformer": [
            {
                "id": sid, "name": name(sid),
                "years": sorted(set(hh["year"] for hh in history_by_wrestler_div.get((sid, div), []) if hh.get("year"))),
                "appearances": i(career_by_wid_div.get((sid, div), {}).get("total_appearances"), 0),
            }
            for sid in siblings_in_div
        ] or None,
        "combinedStats": _combined_stats(wid, div, siblings_in_div),
        "otherDivision": other_division_links or None,
    })
for d in DIVISIONS:
    wrestlers_by_division[d].sort(key=lambda x: -x["elims"])

# ---------------------------------------------------------------------------
# entry_number_stats.csv, PER DIVISION, for the new Entry Number Statistics
# page -- win rate / avg+median survival / final-four rate / runner-up count
# by draw number. Sorted by entry_number so the dashboard can render it
# in order without re-sorting client-side.
# ---------------------------------------------------------------------------
entry_number_stats_by_division = {d: [] for d in DIVISIONS}
for r in entry_number_stats:
    div = r["division"]
    if div not in entry_number_stats_by_division:
        continue
    entry_number_stats_by_division[div].append({
        "entryNumber": i(r.get("entry_number")),
        "sampleSize": i(r.get("events_sample_size"), 0),
        "wins": i(r.get("wins"), 0),
        "winRate": f(r.get("win_rate")),
        "avgSurvivalSec": i(r.get("avg_survival_seconds")),
        "medianSurvivalSec": i(r.get("median_survival_seconds")),
        "avgEliminations": f(r.get("avg_eliminations")),
        "finalFourRate": f(r.get("final_four_rate")),
        "runnerUpCount": i(r.get("runner_up_count"), 0),
    })
for d in DIVISIONS:
    entry_number_stats_by_division[d].sort(key=lambda x: x["entryNumber"] if x["entryNumber"] is not None else 9999)

# entry_number_bands.csv -- coarser "value slice" companion view (2026-09-26,
# per Shane's "win rate by #1 vs #2, first-5 vs middle vs last-5" request).
# Zero new research: a re-bucketing of the same entry_number_stats.csv data.
entry_number_bands = load("derived/entry_number_bands.csv")
_band_order = {"#1": 0, "#2": 1, "First 5 (1-5)": 2, "Middle": 3, "Last 5": 4}
entry_number_bands_by_division = {d: [] for d in DIVISIONS}
for r in entry_number_bands:
    div = r["division"]
    if div not in entry_number_bands_by_division:
        continue
    entry_number_bands_by_division[div].append({
        "band": r.get("band"),
        "bandRange": r.get("band_range"),
        "sampleSize": i(r.get("events_sample_size"), 0),
        "wins": i(r.get("wins"), 0),
        "winRate": f(r.get("win_rate")),
        "avgSurvivalSec": i(r.get("avg_survival_seconds")),
        "avgEliminations": f(r.get("avg_eliminations")),
        "finalFourRate": f(r.get("final_four_rate")),
        "runnerUpCount": i(r.get("runner_up_count"), 0),
        "notes": r.get("notes"),
    })
for d in DIVISIONS:
    entry_number_bands_by_division[d].sort(key=lambda x: _band_order.get(x["band"], 99))

# ---------------------------------------------------------------------------
# TOPIC EXPLORER (2026-09-23) -- a single cross-cutting, searchable index
# over facts already in the database, so a query like "23", "chair",
# "Boston", or a wrestler's name surfaces every relevant record/notable
# moment/elimination/trivia fact without hunting event-by-event. Nothing
# here is new research: every entry is either copied straight from an
# existing sourced table (records.csv, notable_moments.csv, eliminations.csv's
# own narrative text) or computed directly from existing entrants.csv rows
# (e.g. "longest survival from #23"). Two known gaps this can't fix yet,
# because the underlying tagged data doesn't exist: hometown search is only
# as good as billed_from_at_event's current ~3.5% fill rate (this will
# improve automatically, with zero dashboard changes needed, as the Phase B
# biography backfill lands), and there's no "masked wrestler" gimmick tag
# anywhere in the database yet -- that would need new, deliberate tagging
# work, not something to guess at here.
# ---------------------------------------------------------------------------
topic_facts = []
_fid_counter = [0]


def _next_fid():
    _fid_counter[0] += 1
    return f"F{_fid_counter[0]}"


# -- Event-level "field composition" trivia (entrant-count uniqueness) --
_count_events = {}
for _ev in events:
    _c = (_ev.get("entrant_count") or "").strip()
    if not _c:
        continue
    _count_events.setdefault(_c, []).append(_ev)
for _c, _evs in _count_events.items():
    # Only genuinely rare field sizes are notable -- the standard 30-man
    # format covers the overwhelming majority of events and isn't trivia.
    if len(_evs) > 3:
        continue
    _yrs = sorted(set(event_year.get(_e["event_id"], "") for _e in _evs))
    for _ev in _evs:
        _div = DIV_KEY[division_of(_ev["event_id"])]
        _lbl = DIV_LABEL[division_of(_ev["event_id"])]
        _others = [y for y in _yrs if y != event_year.get(_ev["event_id"], "")]
        if len(_evs) == 1:
            _title = f"{event_year.get(_ev['event_id'],'')} is the only {_c}-man {_lbl}"
            _text = f"{_ev.get('event_name','')} at {_ev.get('venue','')} is the only {_lbl} match ever contested with {_c} entrants."
        else:
            _title = f"One of only {len(_evs)} {_c}-man {_lbl} matches ({', '.join(_yrs)})"
            _text = f"{_ev.get('event_name','')} is one of {len(_evs)} {_lbl} matches contested with {_c} entrants, alongside {', '.join(_others)}."
        topic_facts.append({
            "id": _next_fid(), "type": "trivia", "div": _div,
            "title": _title, "text": _text,
            "tags": [f"entrants:{_c}", "field composition", "trivia"],
            "link": {"page": "event", "div": _div, "id": _ev["event_id"]},
        })

# -- records.csv, flattened into searchable facts --
for _r in records:
    _div = DIV_KEY.get(_r.get("division"), _r.get("division"))
    _holder_name = name(_r["holder_wrestler_id"]) if _r.get("holder_wrestler_id") else None
    _title = f"{_r.get('record_name','')}: {_r.get('value','')}" + (f" ({_holder_name})" if _holder_name else "")
    topic_facts.append({
        "id": _next_fid(), "type": "record", "div": _div,
        "title": _title, "text": (_r.get("notes") or ""),
        "tags": [_r.get("category", ""), "record"],
        "link": ({"page": "wrestler", "div": _div, "id": _r["holder_wrestler_id"]} if _r.get("holder_wrestler_id")
                  else ({"page": "event", "div": _div, "id": _r["event_id"]} if _r.get("event_id") else None)),
    })

# -- notable_moments.csv, flattened into searchable facts --
for _m in notable_moments:
    _div = DIV_KEY[division_of(_m["event_id"])]
    _wids = [w.strip() for w in (_m.get("wrestler_ids_involved") or "").split(";") if w.strip()]
    topic_facts.append({
        "id": _next_fid(), "type": "moment", "div": _div,
        "title": _m.get("title", ""), "text": _m.get("description", ""),
        "tags": [_m.get("category", ""), "notable moment"] + [name(w) for w in _wids],
        "link": {"page": "event", "div": _div, "id": _m["event_id"]},
    })

# -- eliminations.csv narrative text: real, already-sourced description
# snippets -- e.g. searching "chair" surfaces every elimination whose
# sourced description happens to mention one. This is NOT a curated
# "weapon" tag (no such structured field exists yet) -- it's the actual
# existing sourced text, shown as-is, so nothing is asserted that isn't
# already in the database. Skipped when too short to be a real narrative
# (a blank/near-blank method field isn't useful to surface here).
for _el in eliminations:
    _method = (_el.get("elimination_method") or "").strip()
    if len(_method) < 15:
        continue
    _div = DIV_KEY[division_of(_el["event_id"])]
    _victim = name(_el.get("eliminated_wrestler_id", ""))
    _eliminator = name(_el.get("eliminator_wrestler_id", "")) if _el.get("eliminator_wrestler_id") else None
    _yr = event_year.get(_el["event_id"], "")
    _title = f"{_victim} eliminated" + (f" by {_eliminator}" if _eliminator else "") + f" -- {_yr}"
    _tags = ["elimination", _victim] + ([_eliminator] if _eliminator else [])
    topic_facts.append({
        "id": _next_fid(), "type": "elimination", "div": _div,
        "title": _title, "text": _method, "tags": _tags,
        "link": {"page": "event", "div": _div, "id": _el["event_id"]},
    })

# -- per-(division, entry number) highlight cards -- computed live from
# entrants.csv. Doesn't duplicate entry_number_stats.csv's own aggregate
# rates (win rate / avg survival / final-four rate -- already on the Entry
# Number Statistics page); adds the SPECIFIC record-holders behind each
# number, which is what actually answers "give me everything about #23".
number_profiles = {d: {} for d in DIV_KEY.values()}
_by_div_entry = {}
for _r in entrants:
    _en = i(_r.get("entry_number"))
    if _en is None:
        continue
    _div = DIV_KEY[division_of(_r["event_id"])]
    _by_div_entry.setdefault((_div, _en), []).append(_r)

for (_div, _en), _rows in _by_div_entry.items():
    _winners = [r for r in _rows if r.get("is_winner") == "TRUE"]
    _with_ring = [(r, i(r.get("ring_time_seconds"))) for r in _rows]
    _with_ring = [(r, s) for r, s in _with_ring if s is not None and s > 0]
    _longest = max(_with_ring, key=lambda rs: rs[1]) if _with_ring else None
    _with_elims = [(r, i(r.get("wrestlers_eliminated_count"), 0)) for r in _rows]
    _with_elims = [(r, c) for r, c in _with_elims if c and c > 0]
    _most_elims = max(_with_elims, key=lambda rc: rc[1]) if _with_elims else None
    _final_four = [r for r in _rows if r.get("is_final_four") == "TRUE"]
    number_profiles[_div][str(_en)] = {
        "entryNumber": _en,
        "appearances": len(_rows),
        "wins": len(_winners),
        "winners": [{"id": w["wrestler_id"], "name": name(w["wrestler_id"]), "eventId": w["event_id"],
                     "year": event_year.get(w["event_id"], "")} for w in _winners],
        "longestSurvival": ({"id": _longest[0]["wrestler_id"], "name": name(_longest[0]["wrestler_id"]),
                              "sec": _longest[1], "eventId": _longest[0]["event_id"],
                              "year": event_year.get(_longest[0]["event_id"], "")} if _longest else None),
        "mostEliminations": ({"id": _most_elims[0]["wrestler_id"], "name": name(_most_elims[0]["wrestler_id"]),
                               "count": _most_elims[1], "eventId": _most_elims[0]["event_id"],
                               "year": event_year.get(_most_elims[0]["event_id"], "")} if _most_elims else None),
        "finalFourCount": len(_final_four),
    }

# -- wrestler quick-index for name/birthplace/nationality/alias search --
wrestler_index = []
for _d in DIVISIONS:
    for _wr in wrestlers_by_division[_d]:
        _bio = _wr.get("bio", {})
        _bp = _bio.get("birthplace")
        _eth = _bio.get("ethnicityHeritage")
        _profile_terms = sorted(set(
            value
            for history_row in (_wr.get("history") or [])
            for value in (
                (history_row.get("physicalProfile") or {}).get("billedFrom"),
                (history_row.get("characterProfile") or {}).get("alignment"),
                (history_row.get("characterProfile") or {}).get("gimmick"),
                (history_row.get("characterProfile") or {}).get("manager"),
                (history_row.get("characterProfile") or {}).get("tagTeam"),
                (history_row.get("characterProfile") or {}).get("faction"),
            )
            if value
        ))
        wrestler_index.append({
            "id": _wr["id"], "div": _wr["divisionKey"], "name": _wr["name"],
            "aliases": _bio.get("aliases") or [],
            "birthplace": (_bp or {}).get("value") if isinstance(_bp, dict) else None,
            "nationality": _bio.get("nationality"),
            "ethnicity": (_eth or {}).get("value") if isinstance(_eth, dict) else None,
            "profileTerms": _profile_terms,
        })

topics_out = {
    "facts": topic_facts,
    "numberProfiles": number_profiles,
    "wrestlerIndex": wrestler_index,
}

# ---------------------------------------------------------------------------
# World map -- wrestlers grouped by recorded nationality and aggregated to
# country level. Compound values use the first named country consistently;
# unmapped values remain visible in the output rather than being guessed.
# ---------------------------------------------------------------------------
NATIONALITY_TO_COUNTRY = {
    "American": "United States", "Canadian": "Canada", "Japanese": "Japan",
    "Mexican": "Mexico", "Australian": "Australia", "Irish": "Ireland",
    "Scottish": "Scotland", "New Zealander": "New Zealand", "Tongan": "Tonga",
    "English": "England", "Nigerian": "Nigeria", "German": "Germany",
    "Mexican-American": "Mexico", "Croatian-American": "Croatia",
    "French": "France", "Dutch": "Netherlands", "Chinese": "China",
    "New Zealand-born, Australia-billed": "New Zealand", "Welsh": "Wales",
    "Puerto Rican": "Puerto Rico", "Austrian": "Austria", "Chilean": "Chile",
    "Russian-German": "Russia", "Cuban-American": "Cuba",
    # Added while extending city-level map coverage (2026-09-29): compound
    # "X-American" nationalities follow this file's existing convention of
    # mapping to the first-named (non-U.S.) country, same as Mexican-American
    # / Croatian-American / Cuban-American above.
    "Argentine": "Argentina", "Australian-American": "Australia",
    "Bulgarian": "Bulgaria", "Canadian-American": "Canada",
    "Canadian-Croatia": "Canada", "Fijian-American": "Fiji",
    "Ghanaian-American": "Ghana", "Guyanese-American": "Guyana",
    "Indian": "India", "Iranian-American": "Iran",
    "Northern Irish": "Northern Ireland", "Samoan-American": "Samoa",
    "South African": "South Africa", "Swiss": "Switzerland",
    "Ukrainian-American": "Ukraine",
}
COUNTRY_COORDS = {
    "United States": (39.8, -98.6), "Canada": (56.1, -106.3), "Japan": (36.2, 138.3),
    "Mexico": (23.6, -102.5), "Australia": (-25.3, 133.8), "Ireland": (53.4, -8.2),
    "Scotland": (56.5, -4.2), "New Zealand": (-41.5, 172.8), "Tonga": (-21.2, -175.2),
    "England": (52.5, -1.5), "Nigeria": (9.1, 8.7), "Germany": (51.2, 10.4),
    "France": (46.6, 2.2), "Netherlands": (52.1, 5.3), "China": (35.9, 104.2),
    "Wales": (52.3, -3.8), "Puerto Rico": (18.2, -66.6), "Austria": (47.5, 14.6),
    "Chile": (-35.7, -71.5), "Croatia": (45.1, 15.2), "Russia": (61.5, 105.3),
    "Cuba": (21.5, -79.5),
    # Added 2026-09-29 for the 15 previously-unmapped nationalities above.
    "Argentina": (-38.4, -63.6), "Bulgaria": (42.7, 25.5), "Fiji": (-17.7, 178.1),
    "Ghana": (7.9, -1.0), "Guyana": (4.9, -58.9), "India": (20.6, 79.0),
    "Iran": (32.4, 53.7), "Northern Ireland": (54.6, -6.7), "Samoa": (-13.8, -172.1),
    "South Africa": (-30.6, 22.9), "Switzerland": (46.8, 8.2), "Ukraine": (48.4, 31.2),
}

# City-level birthplace coordinates (2026-09-29), keyed by the exact
# wrestlers.csv:birthplace string. Resolved via an offline city-name
# gazetteer (geonamescache) for the ~80% of the 369 distinct raw values
# that matched a known city, with the remainder (small towns/townships
# below that dataset's population floor, a few historical/alternate
# place names) filled in by hand. Like COUNTRY_COORDS above, these are
# geographic reference coordinates, not sourced factual claims, so they
# sit outside the CSV data layer's DEFINITIONS.md status/source system.
BIRTHPLACE_COORDS = {
    "Aberdeen, Washington, U.S.": ("Aberdeen", 45.4647, -98.48648, "United States"),
    "Adelaide, South Australia, Australia": ("Adelaide", -34.92866, 138.59863, "Australia"),
    "Aguascalientes, Mexico": ("Aguascalientes", 21.88262, -102.2843, "Mexico"),
    "Aiken, South Carolina, U.S.": ("Aiken", 33.56042, -81.71955, "United States"),
    "Alexandria, Virginia, U.S.": ("Alexandria", 38.80484, -77.04692, "United States"),
    "Allentown, Pennsylvania, U.S.": ("Allentown", 40.60843, -75.49018, "United States"),
    "Alton, Illinois, U.S.": ("Alton", 38.8906, -90.18428, "United States"),
    "American Samoa": ("Pago Pago", -14.2756, -170.702, "American Samoa"),
    "Amsterdam, Netherlands": ("Amsterdam", 52.37403, 4.88969, "The Netherlands"),
    "Anaheim, California, U.S.": ("Anaheim", 33.83529, -117.9145, "United States"),
    "Annville, Pennsylvania, U.S.": ("Annville", 40.3273, -76.515, "United States"),
    "Apopka, Florida, U.S.": ("Apopka", 28.67617, -81.51186, "United States"),
    "Ashikaga, Tochigi, Japan": ("Ashikaga", 36.33333, 139.45, "Japan"),
    "Ashland, Kentucky, United States": ("Ashland", 37.69465, -122.11385, "United States"),
    "Atlanta, Georgia, U.S.": ("Atlanta", 33.749, -84.38798, "United States"),
    "Atlanta, Georgia, United States": ("Atlanta", 33.749, -84.38798, "United States"),
    "Auckland, New Zealand": ("Auckland", -36.84853, 174.76349, "New Zealand"),
    "Augusta, Georgia": ("Augusta", 33.47097, -81.97484, "United States"),
    "Austin, Texas, U.S.": ("Austin", 30.26715, -97.74306, "United States"),
    "Austin, Texas, United States": ("Austin", 30.26715, -97.74306, "United States"),
    "Ayr, Scotland": ("Ayr", 55.46273, -4.63393, "United Kingdom"),
    "Ayrshire, Scotland": ("Ayr", 55.4586, -4.6292, "United Kingdom"),
    "Baltimore, Maryland, U.S.": ("Baltimore", 39.29038, -76.61219, "United States"),
    "Bargoed, Wales": ("Bargoed", 51.69, -3.2334, "United Kingdom"),
    "Baton Rouge, Louisiana, U.S.": ("Baton Rouge", 30.44332, -91.18747, "United States"),
    "Battle Creek, Michigan, U.S.": ("Battle Creek", 42.3173, -85.17816, "United States"),
    "Bay City, Michigan, U.S.": ("Bay City", 43.59447, -83.88886, "United States"),
    "Birmingham, Alabama": ("Birmingham", 33.52066, -86.80249, "United States"),
    "Bloomington, Indiana, U.S.": ("Bloomington", 44.8408, -93.29828, "United States"),
    "Boise, Idaho, U.S.": ("Boise", 43.6135, -116.20345, "United States"),
    "Bolingbrook, Illinois, U.S.": ("Bolingbrook", 41.69864, -88.0684, "United States"),
    "Boronia, Victoria, Australia": ("Boronia", -37.86667, 145.28333, "Australia"),
    "Bowdon, Georgia, U.S.": ("Bowdon", 33.5387, -85.253, "United States"),
    "Boynton Beach, Florida, United States": ("Boynton Beach", 26.52535, -80.06643, "United States"),
    "Bray, County Wicklow, Ireland": ("Bray", 53.20278, -6.09833, "Ireland"),
    "Brooklyn, New York, U.S.": ("Brooklyn", 40.6501, -73.94958, "United States"),
    "Brooksville, Florida, U.S.": ("Brooksville", 28.5553, -82.3879, "United States"),
    "Brownsville, Pennsylvania": ("Brownsville", 25.90175, -97.49748, "United States"),
    "Buffalo, New York, U.S.": ("Buffalo", 42.88645, -78.87837, "United States"),
    "Burlington, New Jersey, U.S.": ("Burlington", 36.09569, -79.4378, "United States"),
    "Calgary, Alberta, Canada": ("Calgary", 51.05011, -114.08529, "Canada"),
    "Camden, New Jersey, U.S.": ("Camden", 39.92595, -75.11962, "United States"),
    "Cameron, North Carolina, U.S.": ("Cameron", 35.3268, -79.2464, "United States"),
    "Canton, Ohio, United States": ("Canton", 42.30865, -83.48216, "United States"),
    "Cape Town, South Africa": ("Cape Town", -33.92584, 18.42322, "South Africa"),
    "Carrickfergus, County Antrim, Northern Ireland": ("Carrickfergus", 54.7158, -5.8058, "United Kingdom"),
    "Champlin, Minnesota, U.S.": ("Champlin", 45.18885, -93.39745, "United States"),
    "Charlotte, North Carolina, U.S.": ("Charlotte", 35.22709, -80.84313, "United States"),
    "Cherry Hill, New Jersey, U.S.": ("Cherry Hill", 39.93484, -75.03073, "United States"),
    "Chicago, Illinois": ("Chicago", 41.85003, -87.65005, "United States"),
    "Chicago, Illinois, U.S.": ("Chicago", 41.85003, -87.65005, "United States"),
    "Chicago, Illinois, United States": ("Chicago", 41.85003, -87.65005, "United States"),
    "Chongqing, China": ("Chongqing", 29.56026, 106.55771, "China"),
    "Chula Vista, California, U.S.": ("Chula Vista", 32.64005, -117.0842, "United States"),
    "Cincinnati, Ohio, United States": ("Cincinnati", 39.12711, -84.51439, "United States"),
    "Clearwater Beach, Florida, United States": ("Clearwater Beach", 27.9775, -82.8288, "United States"),
    "Clearwater, Florida, U.S.": ("Clearwater", 27.96585, -82.8001, "United States"),
    "Cleveland, Ohio, U.S.": ("Cleveland", 41.4995, -81.69541, "United States"),
    "Cobb County, Georgia": ("Marietta", 33.9526, -84.5499, "United States"),
    "Codsall, Staffordshire, England": ("Codsall", 52.6289, -2.1919, "United Kingdom"),
    "Coldwater, Michigan, U.S.": ("Coldwater", 41.9403, -85.0011, "United States"),
    "Columbia, South Carolina": ("Columbia", 34.00071, -81.03481, "United States"),
    "Columbia, South Carolina, United States": ("Columbia", 34.00071, -81.03481, "United States"),
    "Columbus, Georgia": ("Columbus", 39.96118, -82.99879, "United States"),
    "Columbus, Georgia, U.S.": ("Columbus", 39.96118, -82.99879, "United States"),
    "Columbus, Ohio, U.S.": ("Columbus", 39.96118, -82.99879, "United States"),
    "Craigsville, Virginia, U.S.": ("Craigsville", 38.0507, -79.3789, "United States"),
    "Crawfordsville, Indiana": ("Crawfordsville", 40.04115, -86.87445, "United States"),
    "Cuernavaca, Morelos, Mexico": ("Cuernavaca", 18.9261, -99.23075, "Mexico"),
    "Culiacán, Sinaloa, Mexico": ("Culiacán", 24.80209, -107.39421, "Mexico"),
    "Cupertino, California, U.S.": ("Cupertino", 37.323, -122.03218, "United States"),
    "Dallas, Texas, U.S.": ("Dallas", 32.78306, -96.80667, "United States"),
    "Damghan, Iran": ("Dāmghān", 36.1679, 54.34292, "Iran"),
    "Denver, Colorado, U.S.": ("Denver", 39.73915, -104.9847, "United States"),
    "Detroit, Michigan, U.S.": ("Detroit", 42.33143, -83.04575, "United States"),
    "Dhiraina, Himachal Pradesh, India": ("Dhiraina", 31.6, 76.9, "India"),
    "Dublin, Ireland": ("Dublin", 53.33306, -6.24889, "Ireland"),
    "Duluth, Minnesota, U.S.": ("Duluth", 46.78327, -92.10658, "United States"),
    "Durham, North Carolina, U.S.": ("Durham", 35.99403, -78.89862, "United States"),
    "East Palo Alto, California, United States": ("East Palo Alto", 37.46883, -122.14108, "United States"),
    "East Rutherford, New Jersey": ("East Rutherford", 40.8265, -74.0954, "United States"),
    "Ecatepec de Morelos, State of Mexico, Mexico": ("Ecatepec de Morelos", 19.60492, -99.06064, "Mexico"),
    "Edina, Minnesota, United States": ("Edina", 44.88969, -93.34995, "United States"),
    "Edinburgh, Scotland, United Kingdom": ("Edinburgh", 55.95206, -3.19648, "United Kingdom"),
    "Edmond, Oklahoma, U.S.": ("Edmond", 35.65283, -97.4781, "United States"),
    "Edmonton, Alberta, Canada": ("Edmonton", 53.55014, -113.46871, "Canada"),
    "Edwardsburg, Michigan, U.S.": ("Edwardsburg", 41.7997, -86.0764, "United States"),
    "El Paso, Texas, U.S.": ("El Paso", 31.75872, -106.48693, "United States"),
    "Elgin, Illinois, U.S.": ("Elgin", 42.03725, -88.28119, "United States"),
    "Fairfax Station, Virginia, U.S.": ("Fairfax Station", 38.7845, -77.305, "United States"),
    "Fairfax, Virginia, U.S.": ("Fairfax", 38.84622, -77.30637, "United States"),
    "Fairfield, California, U.S.": ("Fairfield", 38.24936, -122.03997, "United States"),
    "Fairfield, Connecticut, U.S.": ("Fairfield", 38.24936, -122.03997, "United States"),
    "Fairfield, Ohio, United States": ("Fairfield", 38.24936, -122.03997, "United States"),
    "Fargo, North Dakota, U.S.": ("Fargo", 46.87719, -96.7898, "United States"),
    "Forest Lake, Minnesota, U.S.": ("Forest Lake", 45.27886, -92.98522, "United States"),
    "Fort Lauderdale, Florida, U.S.": ("Fort Lauderdale", 26.12231, -80.14338, "United States"),
    "Fort Worth, Texas": ("Fort Worth", 32.72541, -97.32085, "United States"),
    "Framingham, Massachusetts, United States": ("Framingham", 42.27926, -71.41617, "United States"),
    "Frankfort, Kentucky": ("Frankfort", 38.20091, -84.87328, "United States"),
    "Franklin, Wisconsin, United States": ("Franklin", 35.92506, -86.86889, "United States"),
    "Fredericktown, Missouri, U.S.": ("Fredericktown", 37.5606, -90.2946, "United States"),
    "Gainesville, Florida, U.S.": ("Gainesville", 29.65163, -82.32483, "United States"),
    "Gainesville, Texas": ("Gainesville", 29.65163, -82.32483, "United States"),
    "Gaithersburg, Maryland, U.S.": ("Gaithersburg", 39.14344, -77.20137, "United States"),
    "Garland, Texas, U.S.": ("Garland", 32.91262, -96.63888, "United States"),
    "Gary, Indiana": ("Gary", 41.59337, -87.34643, "United States"),
    "Geneva, New York, U.S.": ("Geneva", 41.88753, -88.30535, "United States"),
    "Georgetown, Ontario, Canada": ("Georgetown", 43.65011, -79.91634, "Canada"),
    "Georgia, U.S.": ("Atlanta", 33.749, -84.388, "United States"),
    "Gifford, Florida, United States": ("Gifford", 27.6717, -80.4187, "United States"),
    "Gifu, Gifu, Japan": ("Gifu", 35.42291, 136.76039, "Japan"),
    "Glasgow, Scotland": ("Glasgow", 55.86515, -4.25763, "United Kingdom"),
    "Glen Burnie, Maryland, U.S.": ("Glen Burnie", 39.16261, -76.62469, "United States"),
    "Glen Cove, New York, U.S.": ("Glen Cove", 40.86232, -73.63374, "United States"),
    "Glen Ridge, New Jersey, U.S.": ("Glen Ridge", 40.802, -74.2018, "United States"),
    "Glendale, California, U.S.": ("Glendale", 33.53865, -112.18599, "United States"),
    "Glendale, Queens, New York, U.S.": ("Glendale", 33.53865, -112.18599, "United States"),
    "Glens Falls, New York": ("Glens Falls", 43.3095, -73.644, "United States"),
    "Golborne, Lancashire, England": ("Golborne", 53.47693, -2.59651, "United Kingdom"),
    "Goldsboro, North Carolina, U.S.": ("Goldsboro", 35.38488, -77.99277, "United States"),
    "Gomez Palacio, Durango, Mexico": ("Gómez Palacio", 25.56871, -103.4996, "Mexico"),
    "Greensboro, North Carolina, United States": ("Greensboro", 36.07264, -79.79198, "United States"),
    "Grenoble, France": ("Grenoble", 45.17869, 5.71479, "France"),
    "Grove City, Pennsylvania, U.S.": ("Grove City", 39.88145, -83.09296, "United States"),
    "Hackensack, New Jersey, U.S.": ("Hackensack", 40.88593, -74.04347, "United States"),
    "Hagerstown, Maryland, United States": ("Hagerstown", 39.64176, -77.71999, "United States"),
    "Hammond, Indiana, U.S.": ("Hammond", 41.58337, -87.50004, "United States"),
    "Hammond, Louisiana": ("Hammond", 41.58337, -87.50004, "United States"),
    "Hanover, West Virginia, U.S.": ("Hanover", 39.19289, -76.72414, "United States"),
    "Harrisburg, Arkansas": ("Harrisburg", 40.2737, -76.88442, "United States"),
    "Harrisburg, Pennsylvania, U.S.": ("Harrisburg", 40.2737, -76.88442, "United States"),
    "Hasbrouck Heights, New Jersey, U.S.": ("Hasbrouck Heights", 40.8598, -74.0752, "United States"),
    "Hayward, California, U.S.": ("Hayward", 37.66882, -122.0808, "United States"),
    "Hekinan, Aichi, Japan": ("Hekinan", 34.88333, 136.98333, "Japan"),
    "Hendersonville, Tennessee, U.S.": ("Hendersonville", 36.30477, -86.62, "United States"),
    "Hikari, Yamaguchi Prefecture, Japan": ("Hikari", 33.955, 131.95, "Japan"),
    "Hokendauqua, Pennsylvania, U.S.": ("Hokendauqua", 40.644, -75.4602, "United States"),
    "Honolulu, Hawaii": ("Honolulu", 21.30694, -157.85833, "United States"),
    "Honolulu, Hawaii, U.S.": ("Honolulu", 21.30694, -157.85833, "United States"),
    "Houston, Texas, U.S.": ("Houston", 29.76328, -95.36327, "United States"),
    "Howard Beach, Queens, New York City, U.S.": ("Howard Beach", 40.65788, -73.83625, "United States"),
    "Huntington Beach, California, U.S.": ("Huntington Beach", 33.6603, -117.99923, "United States"),
    "Hyogo, Japan": ("Kobe", 34.6913, 135.183, "Japan"),
    "Jackson, Mississippi": ("Jackson", 32.29876, -90.18481, "United States"),
    "Jacksonville, Florida, U.S.": ("Jacksonville", 30.33218, -81.65565, "United States"),
    "Jeffersonville, Indiana, U.S.": ("Jeffersonville", 38.27757, -85.73718, "United States"),
    "Junction City, Kansas, U.S.": ("Junction City", 39.02861, -96.8314, "United States"),
    "Kamakura, Kanagawa, Japan": ("Kamakura", 35.31085, 139.54698, "Japan"),
    "Kansas City, Missouri": ("Kansas City", 39.09973, -94.57857, "United States"),
    "Katsuyama, Fukui, Japan": ("Katsuyama", 36.06173, 136.50101, "Japan"),
    "Kensington, New York": ("Kensington", 40.64621, -73.97069, "United States"),
    "Kitchener, Ontario, Canada": ("Kitchener", 43.42537, -80.5112, "Canada"),
    "Knoxville, Tennessee, U.S.": ("Knoxville", 35.96064, -83.92074, "United States"),
    "Knoxville, Tennessee, United States": ("Knoxville", 35.96064, -83.92074, "United States"),
    "Kokomo, Indiana, U.S.": ("Kokomo", 40.48643, -86.1336, "United States"),
    "Kona, Hawaii, U.S.": ("Kailua-Kona", 19.64, -155.9969, "United States"),
    "Kumasi, Ashanti Region, Ghana": ("Kumasi", 6.68848, -1.62443, "Ghana"),
    "Kyiv, Ukrainian SSR, Soviet Union (now Ukraine)": ("Kyiv", 50.45466, 30.5238, "Ukraine"),
    "Kyotango, Kyoto Prefecture, Japan": ("Kyōtango", 35.60623, 135.04429, "Japan"),
    "La Feria, Texas, United States": ("La Feria", 26.1554, -97.8228, "United States"),
    "Lagos, Nigeria": ("Lagos", 6.45407, 3.39467, "Nigeria"),
    "Lakewood, Ohio, U.S.": ("Lakewood", 39.70471, -105.08137, "United States"),
    "Lancaster, Pennsylvania, U.S.": ("Lancaster", 34.69804, -118.13674, "United States"),
    "Laredo, Texas, United States": ("Laredo", 27.50641, -99.50754, "United States"),
    "Las Vegas, Nevada, U.S.": ("Las Vegas", 36.17497, -115.13722, "United States"),
    "Laval, Quebec, Canada": ("Laval", 45.56995, -73.692, "Canada"),
    "Lenexa, Kansas, U.S.": ("Lenexa", 38.95362, -94.73357, "United States"),
    "Lexington, Tennessee, U.S.": ("Lexington", 37.98869, -84.47772, "United States"),
    "Liberty City, Miami, Florida, U.S.": ("Liberty City, Miami", 25.829, -80.2141, "United States"),
    "Lima, Ohio, U.S.": ("Lima", 40.74255, -84.10523, "United States"),
    "Limerick, Ireland": ("Limerick", 52.66472, -8.62306, "Ireland"),
    "Lincoln Park, Michigan, U.S.": ("Lincoln Park", 41.9217, -87.64783, "United States"),
    "Linden, Guyana": ("Linden", 6.00815, -58.30724, "Guyana"),
    "Liversedge, West Yorkshire, England": ("Liversedge", 53.70514, -1.69327, "United Kingdom"),
    "Lodi, California, U.S.": ("Lodi", 38.1302, -121.27245, "United States"),
    "London, England, United Kingdom": ("London", 51.50853, -0.12574, "United Kingdom"),
    "Long Island, New York, U.S.": ("Long Island", 40.7891, -73.135, "United States"),
    "Loomis, California, United States": ("Loomis", 38.8171, -121.1897, "United States"),
    "Los Angeles, California": ("Los Angeles", 34.05223, -118.24368, "United States"),
    "Los Angeles, California, U.S.": ("Los Angeles", 34.05223, -118.24368, "United States"),
    "Los Angeles, California, United States": ("Los Angeles", 34.05223, -118.24368, "United States"),
    "Louisville, Kentucky": ("Louisville", 38.25424, -85.75941, "United States"),
    "Louisville, Kentucky, U.S.": ("Louisville", 38.25424, -85.75941, "United States"),
    "Lynn, Massachusetts, United States": ("Lynn", 42.46676, -70.94949, "United States"),
    "Lynwood, California, U.S.": ("Lynwood", 33.93029, -118.21146, "United States"),
    "Manchester, England": ("Manchester", 53.48095, -2.23743, "United Kingdom"),
    "Manhasset, New York, U.S.": ("Manhasset", 40.7987, -73.6918, "United States"),
    "Manhasset, New York, United States": ("Manhasset", 40.7987, -73.6918, "United States"),
    "Marietta, Georgia, U.S.": ("Marietta", 33.9526, -84.54993, "United States"),
    "Mays Landing, Hamilton Township, New Jersey, U.S.": ("Mays Landing", 39.4551, -74.7285, "United States"),
    "McDonough, Georgia, United States": ("McDonough", 33.44734, -84.14686, "United States"),
    "McPherson, Kansas, U.S.": ("McPherson", 38.3708, -97.6642, "United States"),
    "Melbourne, Australia": ("Melbourne", -37.814, 144.96332, "Australia"),
    "Memphis, Tennessee": ("Memphis", 35.14953, -90.04898, "United States"),
    "Memphis, Tennessee, U.S.": ("Memphis", 35.14953, -90.04898, "United States"),
    "Merrick, New York, U.S.": ("Merrick", 40.66288, -73.55152, "United States"),
    "Mexico City, Mexico": ("Mexico City", 19.4326, -99.1332, "Mexico"),
    "Miami, Florida": ("Miami", 25.77427, -80.19366, "United States"),
    "Miami, Florida, United States": ("Miami", 25.77427, -80.19366, "United States"),
    "Minneapolis, Minnesota": ("Minneapolis", 44.97997, -93.26384, "United States"),
    "Minneapolis, Minnesota, U.S.": ("Minneapolis", 44.97997, -93.26384, "United States"),
    "Mississauga, Ontario, Canada": ("Mississauga", 43.5789, -79.6583, "Canada"),
    "Moncton, New Brunswick, Canada": ("Moncton", 46.09454, -64.7965, "Canada"),
    "Monroe, North Carolina, U.S.": ("Monroe", 32.50931, -92.1193, "United States"),
    "Monterrey, Nuevo León, Mexico": ("Monterrey", 25.68435, -100.31721, "Mexico"),
    "Montreal, Quebec": ("Montréal", 45.50884, -73.58781, "Canada"),
    "Montreal, Quebec, Canada": ("Montréal", 45.50884, -73.58781, "Canada"),
    "Morristown, New Jersey, U.S.": ("Morristown", 36.21398, -83.29489, "United States"),
    "Moscow, Russia": ("Moscow", 55.75204, 37.61781, "Russia"),
    "Mount Laurel, New Jersey, U.S.": ("Mount Laurel", 39.934, -74.891, "United States"),
    "Mt. Lebanon, Pennsylvania, U.S.": ("Mt. Lebanon", 40.3667, -80.047, "United States"),
    "Nashua, New Hampshire, U.S.": ("Nashua", 42.76537, -71.46757, "United States"),
    "Nashville, Tennessee, U.S.": ("Nashville", 36.16589, -86.78444, "United States"),
    "Nesquehoning, Pennsylvania, U.S.": ("Nesquehoning", 40.8543, -75.8144, "United States"),
    "New Brighton, Pennsylvania, U.S.": ("New Brighton", 45.06552, -93.20189, "United States"),
    "New York City, New York": ("New York City", 40.71427, -74.00597, "United States"),
    "New York City, New York, U.S.": ("New York City", 40.71427, -74.00597, "United States"),
    "New York City, U.S.": ("New York City", 40.71427, -74.00597, "United States"),
    "New York, New York": ("New York City", 40.71427, -74.00597, "United States"),
    "New York, New York, U.S.": ("New York City", 40.71427, -74.00597, "United States"),
    "New York, New York, United States": ("New York City", 40.71427, -74.00597, "United States"),
    "Niagara Falls, New York, U.S.": ("Niagara Falls", 43.0945, -79.05671, "United States"),
    "Nishinomiya, Hyogo, Japan": ("Nishinomiya", 34.71562, 135.33199, "Japan"),
    "Nobeoka, Japan": ("Nobeoka", 32.58333, 131.66667, "Japan"),
    "Nukuʻalofa, Tonga": ("Nuku'alofa", -21.1394, -175.2049, "Tonga"),
    "Oakville, Ontario, Canada": ("Oakville", 43.45011, -79.68292, "Canada"),
    "Ocala, Florida, United States": ("Ocala", 29.1872, -82.14009, "United States"),
    "Omaha, Nebraska, U.S.": ("Omaha", 41.25626, -95.94043, "United States"),
    "Ontario, California, United States": ("Ontario", 34.06334, -117.65089, "United States"),
    "Orangeburg, South Carolina, U.S.": ("Orangeburg", 33.4918, -80.8556, "United States"),
    "Orangeville, Ontario, Canada": ("Orangeville", 43.9168, -80.09967, "Canada"),
    "Orlando, Florida, U.S.": ("Orlando", 28.53834, -81.37924, "United States"),
    "Osaka, Japan": ("Osaka", 34.69379, 135.50107, "Japan"),
    "Oshkosh, Wisconsin, U.S.": ("Oshkosh", 44.02471, -88.54261, "United States"),
    "Ottawa, Illinois, U.S.": ("Ottawa", 41.34559, -88.84258, "United States"),
    "Paisley, Renfrewshire, Scotland": ("Paisley", 55.83173, -4.43254, "United Kingdom"),
    "Palatka, Florida, U.S.": ("Palatka", 29.6483, -81.6367, "United States"),
    "Palos Verdes, California, U.S.": ("Palos Verdes", 33.7445, -118.387, "United States"),
    "Parma, Ohio, U.S.": ("Parma", 41.40477, -81.72291, "United States"),
    "Peabody, Massachusetts, U.S.": ("Peabody", 42.52787, -70.92866, "United States"),
    "Penwortham, Lancashire, England": ("Penwortham", 53.744, -2.744, "United Kingdom"),
    "Perry, Georgia, U.S.": ("Perry", 32.45821, -83.73157, "United States"),
    "Peterborough, Ontario, Canada": ("Peterborough", 44.30012, -78.31623, "Canada"),
    "Philadelphia, Pennsylvania, U.S.": ("Philadelphia", 39.95238, -75.16362, "United States"),
    "Phoenix, Arizona": ("Phoenix", 33.44838, -112.07404, "United States"),
    "Pinehurst, North Carolina": ("Pinehurst", 35.19543, -79.46948, "United States"),
    "Pineville, West Virginia, U.S.": ("Pineville", 37.5865, -81.5387, "United States"),
    "Pinneberg, Schleswig-Holstein, Germany": ("Pinneberg", 53.65887, 9.79698, "Germany"),
    "Pittsburgh, Pennsylvania, U.S.": ("Pittsburgh", 40.44062, -79.99589, "United States"),
    "Plain Dealing, Louisiana, U.S.": ("Plain Dealing", 32.8965, -93.6979, "United States"),
    "Plum, Pennsylvania, United States": ("Plum", 40.50035, -79.74949, "United States"),
    "Point Pleasant, New Jersey, U.S.": ("Point Pleasant", 40.08317, -74.06819, "United States"),
    "Pompano Beach, Florida": ("Pompano Beach", 26.23786, -80.12477, "United States"),
    "Ponte Vedra Beach, Florida, U.S.": ("Ponte Vedra Beach", 30.23969, -81.38564, "United States"),
    "Port St. Lucie, Florida, United States": ("Port St. Lucie", 27.2939, -80.3501, "United States"),
    "Princeton, Minnesota, U.S.": ("Princeton", 25.53844, -80.40894, "United States"),
    "Prior Lake, Minnesota, United States": ("Prior Lake", 44.7133, -93.42273, "United States"),
    "Quebec City, Quebec": ("Québec", 46.81228, -71.21454, "Canada"),
    "Queens, New York City, U.S.": ("Queens", 40.68149, -73.83652, "United States"),
    "Quitman, Missouri": ("Quitman", 39.9059, -94.7541, "United States"),
    "Richmond, Virginia, U.S.": ("Richmond", 37.55376, -77.46026, "United States"),
    "Ridgewood, New Jersey, U.S.": ("Ridgewood", 40.7001, -73.90569, "United States"),
    "Riverside, California, U.S.": ("Riverside", 33.95335, -117.39616, "United States"),
    "Riverside, California, United States": ("Riverside", 33.95335, -117.39616, "United States"),
    "Roanoke, Virginia": ("Roanoke", 37.27097, -79.94143, "United States"),
    "Roanoke, Virginia, U.S.": ("Roanoke", 37.27097, -79.94143, "United States"),
    "Robbinsdale, Minnesota": ("Robbinsdale", 45.0308, -93.3383, "United States"),
    "Rochester, New York": ("Rochester", 43.15478, -77.61556, "United States"),
    "Rochester, New York, U.S.": ("Rochester", 43.15478, -77.61556, "United States"),
    "Rome, Georgia": ("Rome", 41.89193, 12.51133, "Italy"),
    "Sacramento, California, U.S.": ("Sacramento", 38.58157, -121.4944, "United States"),
    "Sacramento, California, United States": ("Sacramento", 38.58157, -121.4944, "United States"),
    "Saint Michael, Minnesota, United States": ("Saint Michael", 45.20996, -93.66496, "United States"),
    "Saint Paul, Minnesota, U.S.": ("Saint Paul", 44.94441, -93.09327, "United States"),
    "Saint-Sulpice, Quebec": ("Saint-Sulpice", 45.85, -73.25, "Canada"),
    "Salem, New Jersey, U.S.": ("Salem", 44.9429, -123.0351, "United States"),
    "Salt Lake City, Utah, United States": ("Salt Lake City", 40.76078, -111.89105, "United States"),
    "San Antonio, Texas": ("San Antonio", 29.42412, -98.49363, "United States"),
    "San Bernardino, California, U.S.": ("San Bernardino", 34.10834, -117.28977, "United States"),
    "San Bernardino, California, United States": ("San Bernardino", 34.10834, -117.28977, "United States"),
    "San Diego, California, U.S.": ("San Diego", 32.71571, -117.16472, "United States"),
    "San Fernando, Chile": ("San Fernando", 15.03425, 120.68445, "Philippines"),
    "San Francisco, California": ("San Francisco", 37.77493, -122.41942, "United States"),
    "San Francisco, California, U.S.": ("San Francisco", 37.77493, -122.41942, "United States"),
    "San Jose, California, U.S.": ("San Jose", 37.33939, -121.89496, "United States"),
    "San Juan, Puerto Rico": ("San Juan", 18.46633, -66.10572, "Puerto Rico"),
    "San Luis Potosi City, San Luis Potosi, Mexico": ("San Luis Potosi", 22.1565, -100.9855, "Mexico"),
    "San Luis Potosí, Mexico": ("San Luis Potosí", 22.15234, -100.97135, "Mexico"),
    "Sanford, Florida, U.S.": ("Sanford", 28.80055, -81.27312, "United States"),
    "Santa Clara County, California, U.S.": ("San Jose", 37.3382, -121.8863, "United States"),
    "Santa Isabel, Puerto Rico": ("Santa Isabel", -23.31556, -46.22139, "Brazil"),
    "Santa Monica, California, U.S.": ("Santa Monica", 34.01949, -118.49138, "United States"),
    "Sarasota, Florida": ("Sarasota", 27.33643, -82.53065, "United States"),
    "Sarnia, Ontario, Canada": ("Sarnia", 42.97866, -82.40407, "Canada"),
    "Saskatoon, Saskatchewan, Canada": ("Saskatoon", 52.13238, -106.66892, "Canada"),
    "Seattle, Washington": ("Seattle", 47.60621, -122.33207, "United States"),
    "Seven Hills, Ohio, U.S.": ("Seven Hills", -33.78333, 150.93333, "Australia"),
    "Shamong Township, New Jersey, U.S.": ("Shamong Township", 39.7768, -74.7099, "United States"),
    "Silsbee, Texas, U.S.": ("Silsbee", 30.341, -94.1794, "United States"),
    "Sioux City, Iowa, United States": ("Sioux City", 42.49999, -96.40031, "United States"),
    "Sioux Falls, South Dakota, U.S.": ("Sioux Falls", 43.54369, -96.72796, "United States"),
    "Smithfield, North Carolina, U.S.": ("Smithfield", 41.92204, -71.54951, "United States"),
    "Socialist Republic of Croatia, SFRY": ("Zagreb", 45.815, 15.9819, "Croatia"),
    "Solihull, West Midlands, England": ("Solihull", 52.41426, -1.78094, "United Kingdom"),
    "Southbridge, Massachusetts, U.S.": ("Southbridge", 42.0751, -72.03341, "United States"),
    "Spencer, Massachusetts, U.S.": ("Spencer", 42.2459, -71.9926, "United States"),
    "St. Catharines, Ontario, Canada": ("St. Catharines", 43.17126, -79.24267, "Canada"),
    "St. Cloud, Minnesota, U.S.": ("St. Cloud", 45.5579, -94.1632, "United States"),
    "St. Louis, Missouri, U.S.": ("St. Louis", 38.62727, -90.19789, "United States"),
    "St. Petersburg, Florida, U.S.": ("St. Petersburg", 27.77086, -82.67927, "United States"),
    "Staten Island, New York, U.S.": ("Staten Island", 40.56233, -74.13986, "United States"),
    "Sunset Beach, Hawaii": ("Sunset Beach", 21.6672, -158.0389, "United States"),
    "Surrey, British Columbia, Canada": ("Surrey", 49.10635, -122.82509, "Canada"),
    "Suva, Fiji": ("Suva", -18.13683, 178.42531, "Fiji"),
    "Sweetwater, Texas, U.S.": ("Sweetwater", 25.76343, -80.37311, "United States"),
    "Sydney, New South Wales, Australia": ("Sydney", -33.86785, 151.20732, "Australia"),
    "Syracuse, New York, U.S.": ("Syracuse", 43.04812, -76.14742, "United States"),
    "Tala, Jalisco, Mexico": ("Tala", 20.65267, -103.70148, "Mexico"),
    "Tamana, Kumamoto, Japan": ("Tamana", 32.94716, 130.57446, "Japan"),
    "Tampa, Florida": ("Tampa", 27.94752, -82.45843, "United States"),
    "Tampa, Florida, U.S.": ("Tampa", 27.94752, -82.45843, "United States"),
    "Throop, New York, U.S.": ("Throop", 43.0087, -76.5844, "United States"),
    "Tijuana, Baja California, Mexico": ("Tijuana", 32.5027, -117.00371, "Mexico"),
    "Titusville, Florida, U.S.": ("Titusville", 28.61222, -80.80755, "United States"),
    "Tocula, Mexico": ("Tocula", 19.7, -99.2, "Mexico"),
    "Tokushima, Tokushima, Japan": ("Tokushima", 34.06667, 134.56667, "Japan"),
    "Tokyo, Japan": ("Tokyo", 35.6895, 139.69171, "Japan"),
    "Toms River, New Jersey, U.S.": ("Toms River", 39.95373, -74.19792, "United States"),
    "Tonga (billed from)": ("Nuku'alofa", -21.1394, -175.2049, "Tonga"),
    "Toronto, Ontario, Canada": ("Toronto", 43.70643, -79.39864, "Canada"),
    "Torrejon de Ardoz, Spain": ("Torrejón de Ardoz", 40.45535, -3.46973, "Spain"),
    "Torrejón de Ardoz, Spain": ("Torrejón de Ardoz", 40.45535, -3.46973, "Spain"),
    "Tremadog, Wales": ("Tremadog", 52.9436, -4.1439, "United Kingdom"),
    "Tulancingo, Hidalgo, Mexico": ("Tulancingo", 20.08355, -98.36288, "Mexico"),
    "Tulsa, Oklahoma, U.S.": ("Tulsa", 36.15398, -95.99277, "United States"),
    "Union City, Tennessee": ("Union City", 37.59577, -122.01913, "United States"),
    "Vancouver, Washington, U.S.": ("Vancouver", 45.63873, -122.66149, "United States"),
    "Varennes, Quebec, Canada": ("Varennes", 45.68338, -73.43246, "Canada"),
    "Vega Alta, Puerto Rico": ("Vega Alta", 18.4133, -66.3277, "Puerto Rico"),
    "Vega Baja, Puerto Rico": ("Vega Baja", 18.44439, -66.38767, "Puerto Rico"),
    "Vero Beach, Florida": ("Vero Beach", 27.63864, -80.39727, "United States"),
    "Victoria, British Columbia, Canada": ("Victoria", 48.4359, -123.35155, "Canada"),
    "Vienna, Austria": ("Vienna", 48.20849, 16.37208, "Austria"),
    "Wadesboro, North Carolina": ("Wadesboro", 34.964, -80.0787, "United States"),
    "Warner Robins, Georgia, U.S.": ("Warner Robins", 32.61574, -83.62664, "United States"),
    "Washington, D.C., U.S.": ("Washington", 38.89511, -77.03637, "United States"),
    "Waterbury, Connecticut, U.S.": ("Waterbury", 41.55815, -73.0515, "United States"),
    "Waxahachie, Texas, U.S.": ("Waxahachie", 32.38653, -96.84833, "United States"),
    "Webster, South Dakota, U.S.": ("Webster", 45.3363, -97.5219, "United States"),
    "Wellington, New Zealand": ("Wellington", -41.28664, 174.77557, "New Zealand"),
    "West Newbury, Massachusetts, U.S.": ("West Newbury", 42.8065, -70.9673, "United States"),
    "West Point, New York": ("West Point", 41.3903, -73.9587, "United States"),
    "West Warwick, Rhode Island, U.S.": ("West Warwick", 41.69689, -71.52194, "United States"),
    "Westbrook, Maine, U.S.": ("Westbrook", 43.67703, -70.37116, "United States"),
    "Westchester County, New York, U.S.": ("White Plains", 41.034, -73.7629, "United States"),
    "Westlake, Ohio, United States": ("Westlake", 41.45532, -81.91792, "United States"),
    "Whitby, Ontario, Canada": ("Whitby", 43.88342, -78.93287, "Canada"),
    "White Bear Lake, Minnesota": ("White Bear Lake", 45.08469, -93.00994, "United States"),
    "Wichita Falls, Texas, U.S.": ("Wichita Falls", 33.91371, -98.49339, "United States"),
    "Wilkinsburg, Pennsylvania": ("Wilkinsburg", 40.44174, -79.88199, "United States"),
    "Winnipeg, Manitoba, Canada": ("Winnipeg", 49.8844, -97.14704, "Canada"),
    "Winter Park, Florida, United States": ("Winter Park", 28.6, -81.33924, "United States"),
    "Wisconsin Rapids, Wisconsin, U.S.": ("Wisconsin Rapids", 44.38358, -89.81735, "United States"),
    "Woodbury, New Jersey, U.S.": ("Woodbury", 44.92386, -92.95938, "United States"),
    "Woodstock, Georgia, United States": ("Woodstock", 34.10149, -84.51938, "United States"),
    "Yonkers, New York, U.S.": ("Yonkers", 40.9304, -73.89789, "United States"),
    "Zagreb, Croatia": ("Zagreb", 45.81444, 15.97798, "Croatia"),
    "Zagreb, SR Croatia, SFR Yugoslavia": ("Zagreb", 45.81444, 15.97798, "Croatia"),
}

_MAP_W, _MAP_H = 960, 480

def _project(lat, lon):
    return round((lon + 180) * (_MAP_W / 360.0), 1), round((90 - lat) * (_MAP_H / 180.0), 1)

_country_wrestlers = defaultdict(list)
_unmapped_nationalities = Counter()
_with_nationality = 0
for w in wrestlers:
    nat = (w.get("nationality") or "").strip()
    if not nat:
        continue
    _with_nationality += 1
    country = NATIONALITY_TO_COUNTRY.get(nat)
    if not country:
        _unmapped_nationalities[nat] += 1
        continue
    _country_wrestlers[country].append((w["wrestler_id"], name(w["wrestler_id"]), nat))

world_map_countries = []
for country, members in _country_wrestlers.items():
    lat, lon = COUNTRY_COORDS[country]
    x, y = _project(lat, lon)
    nat_counts = Counter(m[2] for m in members)
    members_sorted = sorted(members, key=lambda m: m[1] or "")
    world_map_countries.append({
        "country": country, "x": x, "y": y, "count": len(members),
        "nationalities": [{"label": lbl, "count": c} for lbl, c in nat_counts.most_common()],
        "wrestlers": [{"id": wid, "name": nm, "nationality": nat} for wid, nm, nat in members_sorted],
    })
world_map_countries.sort(key=lambda r: -r["count"])
world_map = {
    "countries": world_map_countries, "totalWrestlers": len(wrestlers),
    "totalWithNationality": _with_nationality,
    "totalPlotted": sum(c["count"] for c in world_map_countries),
    "coveragePct": round(100.0 * _with_nationality / len(wrestlers), 1) if wrestlers else 0,
    "unmapped": [{"nationality": k, "count": v} for k, v in _unmapped_nationalities.most_common()],
    "mapWidth": _MAP_W, "mapHeight": _MAP_H,
}
if _unmapped_nationalities:
    print("WARNING: world map has no country mapping for: " +
          ", ".join(sorted(_unmapped_nationalities)) +
          " -- these wrestlers are counted in totalWithNationality but not plotted.")

# ---------------------------------------------------------------------------
# World map, city level -- one pin per distinct birthplace (not per
# nationality/country), built from wrestlers.csv:birthplace + BIRTHPLACE_COORDS
# above. A city can hold several wrestlers; each pin lists them all.
# ---------------------------------------------------------------------------
_city_wrestlers = defaultdict(list)
_unmapped_birthplaces = Counter()
_with_birthplace = 0
for w in wrestlers:
    bp = (w.get("birthplace") or "").strip()
    if not bp:
        continue
    _with_birthplace += 1
    coords = BIRTHPLACE_COORDS.get(bp)
    if not coords:
        _unmapped_birthplaces[bp] += 1
        continue
    city_label, lat, lon, country = coords
    _city_wrestlers[(city_label, lat, lon, country)].append((w["wrestler_id"], name(w["wrestler_id"]), bp))

world_map_cities = []
for (city_label, lat, lon, country), members in _city_wrestlers.items():
    x, y = _project(lat, lon)
    members_sorted = sorted(members, key=lambda m: m[1] or "")
    world_map_cities.append({
        "city": city_label, "country": country, "lat": lat, "lon": lon,
        "x": x, "y": y, "count": len(members),
        "wrestlers": [{"id": wid, "name": nm, "birthplace": bp} for wid, nm, bp in members_sorted],
    })
world_map_cities.sort(key=lambda r: -r["count"])
world_map["cities"] = world_map_cities
world_map["totalWithBirthplace"] = _with_birthplace
world_map["totalCitiesPlotted"] = len(world_map_cities)
world_map["birthplaceCoveragePct"] = round(100.0 * _with_birthplace / len(wrestlers), 1) if wrestlers else 0
world_map["unmappedBirthplaces"] = [{"birthplace": k, "count": v} for k, v in _unmapped_birthplaces.most_common()]
if _unmapped_birthplaces:
    print("WARNING: city map has no coordinate for: " +
          ", ".join(sorted(_unmapped_birthplaces)) +
          " -- these wrestlers are counted in totalWithBirthplace but not plotted as city pins.")

# ---------------------------------------------------------------------------
# Cross-promotion championship-history browser data
# ---------------------------------------------------------------------------
championship_reigns_by_title = defaultdict(list)
championship_summary_by_wrestler = defaultdict(lambda: {
    "reignIds": set(), "championshipIds": set(), "promotionIds": set(),
})
championships_by_id = {row["championship_id"]: row for row in championships}

for row in championship_reigns:
    compact = {
        "id": row["reign_id"],
        "type": row["record_type"],
        "champion": row["champion_name"],
        "wrestlerIds": [x for x in row.get("champion_wrestler_ids", "").split(";") if x],
        "reignNumber": i(row.get("reign_number")),
        "wonDate": row.get("won_date") or None,
        "lostDate": row.get("lost_date") or None,
        "daysReported": row.get("days_reported") or None,
        "daysRecognizedReported": row.get("days_recognized_reported") or None,
        "event": row.get("event_name") or None,
        "location": row.get("location") or None,
        "current": row.get("is_current") == "TRUE",
        "status": row.get("data_quality_status") or None,
        "notes": row.get("notes") or None,
    }
    championship_reigns_by_title[row["championship_id"]].append(compact)
    if row.get("record_type") == "reign":
        championship = championships_by_id.get(row["championship_id"], {})
        for wrestler_id in compact["wrestlerIds"]:
            summary = championship_summary_by_wrestler[wrestler_id]
            summary["reignIds"].add(row["reign_id"])
            summary["championshipIds"].add(row["championship_id"])
            if championship.get("promotion_id"):
                summary["promotionIds"].add(championship["promotion_id"])

# A performer can have several deliberately separate gimmick-era wrestler IDs
# in the Rumble data. Make the championship summary career-spanning across the
# same sourced identity groups used by the wrestler profile, while the reign
# row itself keeps the historically correct ring-name-specific link.
for wrestler_id, siblings in same_performer.items():
    group = {wrestler_id, *siblings}
    reign_ids = set()
    championship_ids = set()
    promotion_ids = set()
    for group_id in group:
        summary = championship_summary_by_wrestler.get(group_id)
        if not summary:
            continue
        reign_ids.update(summary["reignIds"])
        championship_ids.update(summary["championshipIds"])
        promotion_ids.update(summary["promotionIds"])
    if not reign_ids:
        continue
    for group_id in group:
        championship_summary_by_wrestler[group_id] = {
            "reignIds": set(reign_ids),
            "championshipIds": set(championship_ids),
            "promotionIds": set(promotion_ids),
        }

championship_history_out = {
    "asOf": "2026-09-28",
    "scope": "World-title lineages; source snapshots, not a live dependency",
    "promotions": [
        {
            "id": row["promotion_id"], "name": row["promotion_name"],
            "abbreviation": row.get("abbreviation") or None,
            "country": row.get("country") or None,
            "activeFrom": row.get("active_from") or None,
            "activeTo": row.get("active_to") or None,
            "formerNames": [x for x in row.get("former_names", "").split(";") if x],
            "officialUrl": row.get("official_url") or None,
            "wikipediaUrl": row.get("wikipedia_url") or None,
        }
        for row in promotions
    ],
    "championships": [
        {
            "id": row["championship_id"], "promotionId": row["promotion_id"],
            "name": row["championship_name"], "level": row["championship_level"],
            "division": row["division"], "activeFrom": row.get("active_from") or None,
            "activeTo": row.get("active_to") or None, "status": row.get("status") or None,
            "predecessorIds": [x for x in row.get("predecessor_championship_ids", "").split(";") if x],
            "successorIds": [x for x in row.get("successor_championship_ids", "").split(";") if x],
            "officialHistoryUrl": row.get("official_history_url") or None,
            "wikipediaHistoryUrl": row.get("wikipedia_history_url") or None,
            "reigns": championship_reigns_by_title.get(row["championship_id"], []),
        }
        for row in championships
    ],
    "wrestlerSummary": {
        wrestler_id: {
            "reigns": len(summary["reignIds"]),
            "championshipIds": sorted(summary["championshipIds"]),
            "promotionIds": sorted(summary["promotionIds"]),
        }
        for wrestler_id, summary in championship_summary_by_wrestler.items()
    },
}

# ---------------------------------------------------------------------------
# Full-card stats (2026-09-30): commentators + the rest of the card, not just
# the Royal Rumble match itself. Covers only the events with other_matches /
# show_appearances research done -- "coveredEvents" tells the dashboard which
# ones that is, so it can label the rest as "no full-card data yet" rather
# than implying a true zero.
# ---------------------------------------------------------------------------
_covered_from_om = set()
try:
    for _r in load("other_matches.csv"):
        _covered_from_om.add(_r["event_id"])
except FileNotFoundError:
    pass
covered_event_ids = sorted(_covered_from_om)

def _event_brief(eid):
    ev = events_by_id.get(eid)
    if not ev:
        return {"id": eid, "name": eid, "year": None}
    return {"id": eid, "name": ev.get("event_name") or eid, "year": (ev.get("event_date") or "")[:4] or None}

full_card_out = {
    "coveredEvents": [_event_brief(eid) for eid in covered_event_ids],
    "dualDutyEntrants": [
        {
            "eventId": r["event_id"],
            "event": _event_brief(r["event_id"]),
            "division": r["division"],
            "wrestlerId": r["wrestler_id"],
            "wrestlerName": name(r["wrestler_id"]),
            "otherMatchNumber": r["other_match_number"] or None,
            "otherMatchType": r["other_match_type"],
            "otherMatchResult": r["other_match_result"],
            "entryNumber": i(r["entry_number"]),
            "rumbleResult": r["rumble_result"],
        }
        for r in card_dual_duty
    ],
    "nonRumbleCardRegulars": [
        {
            "wrestlerId": r["wrestler_id"],
            "wrestlerName": name(r["wrestler_id"]),
            "cardAppearancesCount": i(r["card_appearances_count"]),
            "events": [_event_brief(eid) for eid in r["events_with_card_appearance"].split(";") if eid],
            "firstEvent": _event_brief(r["first_event_id"]),
            "mostRecentEvent": _event_brief(r["most_recent_event_id"]),
        }
        for r in card_non_rumble_regulars
    ],
    "commentators": [
        {
            "personId": r["person_id"],
            "personName": r["person_name"],
            "role": r["role"],
            "eventsCount": i(r["events_count"]),
            "firstEvent": _event_brief(r["first_event_id"]),
            "mostRecentEvent": _event_brief(r["most_recent_event_id"]),
            "events": [_event_brief(eid) for eid in r["events_list"].split(";") if eid],
        }
        for r in commentator_stats
    ],
    "matchTypeFrequency": [
        {"matchType": r["match_type"], "occurrences": i(r["occurrences"]), "eventsCount": i(r["events_count"])}
        for r in card_match_type_frequency
    ],
    "titleFrequency": [
        {
            "title": r["title_involved"], "occurrences": i(r["occurrences"]),
            "eventsCount": i(r["events_count"]), "distinctChampionsCount": i(r["distinct_champions_count"]),
        }
        for r in card_title_frequency
    ],
}

# ---------------------------------------------------------------------------
# Flags summary (lightweight -- counts + status breakdown, not the full table)
# ---------------------------------------------------------------------------
status_counts = Counter(fl["status"] for fl in flags)

meta = {
    "generated": "2026-09-28",
    "wrestlers": len(wrestlers),
    "entrants": len(entrants),
    "eliminations": len(eliminations),
    "events": len(events),
    "records": len(records),
    "flagsOpen": status_counts.get("open", 0),
    "flagsResolved": status_counts.get("resolved", 0),
    "divisions": [
        {
            "key": DIV_KEY[d], "label": DIV_LABEL[d], "matchType": d,
            "events": len(events_by_division[d]),
            "wrestlers": len(wrestlers_by_division[d]),
            "records": len(records_by_division.get(d, [])),
        }
        for d in DIVISIONS
    ],
}

out = {
    "meta": meta,
    "divisions": [
        {
            "key": DIV_KEY[d],
            "label": DIV_LABEL[d],
            "matchType": d,
            "events": events_by_division[d],
            "records": records_by_division.get(d, []),
            "wrestlers": wrestlers_by_division[d],
            "entryNumberStats": entry_number_stats_by_division[d],
            "entryNumberBands": entry_number_bands_by_division[d],
            "locations": locations_by_division[d],
        }
        for d in DIVISIONS
    ],
    "topics": topics_out,
    "worldMap": world_map,
    "championshipHistory": championship_history_out,
    "fullCard": full_card_out,
}

os.makedirs(os.path.dirname(OUT_PATH) or ".", exist_ok=True)
with open(OUT_PATH, "w", encoding="utf-8") as fh:
    json.dump(out, fh, separators=(",", ":"), ensure_ascii=False)

size_kb = os.path.getsize(OUT_PATH) / 1024
div_summary = ", ".join(f"{d['label']}: {d['events']} events / {d['wrestlers']} wrestlers / {d['records']} records" for d in meta["divisions"])
print(f"Wrote {OUT_PATH}: {div_summary} ({size_kb:.0f} KB).")
