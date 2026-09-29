# -*- coding: utf-8 -*-
"""
Builds the static reference-data JSON for the LIVE (Artifact-hosted)
version of the Royal Rumble Event Logger. This replaces the local
SQLite import_adapter.py for that version: the Artifact page fetches
this JSON once for read-only reference data (events, entrants,
wrestlers, and each elimination's IMPORTED snapshot), and layers the
viewer's own review edits on top via the artifact's `db` capability
(a small, separate collection of only the rows someone has actually
reviewed -- an absent doc just means "still unreviewed, use the
imported snapshot from this file").

Re-run and republish this file (via the Artifact tool, same page.html)
any time the live database changes -- it never touches anyone's
in-progress review state, which lives entirely in the artifact's db,
not in this file.

Document id grammar for the `db` collection this pairs with: each
review's stable id is
    <event_id>__<eliminated_wrestler_id>__<eliminator_wrestler_id or 'none'>
matching this script's own `id` field below -- keyed on the ORIGINAL
imported eliminator, exactly like the local-server version, and for
the same reason (see import_adapter.py's docstring on group
eliminations): a single victim can have several genuinely separate
elimination rows (different eliminator per row), and correcting who
the eliminator was during review is an edit to a row, never a change
to which row it is.
"""
import csv
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))


def default_live_db_path():
    # Shipped inside the royal-rumble-database repo as logger/ at repo root.
    return os.path.normpath(os.path.join(HERE, "..", "data"))


def load_csv(folder, name):
    path = os.path.join(folder, name)
    if not os.path.exists(path):
        print(f"WARNING: {path} not found -- skipping.")
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sanitize_id_part(s):
    # db path segments: letters, digits, _ - . ~ : @ + only
    if not s:
        return "none"
    out = "".join(c if (c.isalnum() or c in "_-.~:@+") else "-" for c in s)
    return out or "none"


def build(live_db_dir, out_path):
    events = load_csv(live_db_dir, "events.csv")
    entrants = load_csv(live_db_dir, "entrants.csv")
    eliminations = load_csv(live_db_dir, "eliminations.csv")
    wrestlers = load_csv(live_db_dir, "wrestlers.csv")

    wrestler_names = {w["wrestler_id"]: w.get("ring_name", w["wrestler_id"]) for w in wrestlers}

    events_out = []
    for ev in sorted(events, key=lambda e: e.get("event_date", "")):
        events_out.append({
            "eventId": ev["event_id"],
            "eventName": ev.get("event_name", ""),
            "matchName": ev.get("match_name", ""),
            "division": ev.get("match_type", ""),
            "eventDate": ev.get("event_date", ""),
            "durationTotal": ev.get("duration_total", ""),
            "entrantCount": int(ev["entrant_count"]) if (ev.get("entrant_count") or "").isdigit() else None,
        })

    entrants_by_event = {}
    for e in entrants:
        entrants_by_event.setdefault(e["event_id"], []).append({
            "wrestlerId": e["wrestler_id"],
            "name": wrestler_names.get(e["wrestler_id"], e["wrestler_id"]),
            "entryNumber": e.get("entry_number", ""),
            "ringNameAtTime": e.get("ring_name_at_time", ""),
            "isWinner": e.get("is_winner") == "TRUE",
        })
    for eid in entrants_by_event:
        entrants_by_event[eid].sort(key=lambda x: (int(x["entryNumber"]) if str(x["entryNumber"]).isdigit() else 9999))

    reviews_out = []
    seen_ids = set()
    for el in eliminations:
        eliminator = el.get("eliminator_wrestler_id", "")
        rid = f"{el['event_id']}__{sanitize_id_part(el['eliminated_wrestler_id'])}__{sanitize_id_part(eliminator)}"
        if rid in seen_ids:
            # true duplicate triple -- should not happen post-Version-39 merge,
            # but guard rather than silently overwrite if it ever recurs
            print(f"WARNING: duplicate review id {rid} -- keeping first occurrence only, check eliminations.csv")
            continue
        seen_ids.add(rid)
        reviews_out.append({
            "id": rid,
            "eventId": el["event_id"],
            "eliminatedWrestlerId": el["eliminated_wrestler_id"],
            "eliminatedWrestlerName": wrestler_names.get(el["eliminated_wrestler_id"], el["eliminated_wrestler_id"]),
            "imported": {
                "eliminatorWrestlerId": eliminator,
                "eliminatorWrestlerName": wrestler_names.get(eliminator, eliminator) if eliminator else "",
                "assistingWrestlerIds": el.get("assisting_wrestler_ids", ""),
                "orderInMatch": el.get("order_in_match", ""),
                "eliminationClockTime": el.get("elimination_clock_time", ""),
                "eliminationMethod": el.get("elimination_method", ""),
                "locationSide": el.get("location_side", ""),
                "eliminationType": el.get("elimination_type", ""),
                "isSolo": el.get("is_solo", ""),
                "isShared": el.get("is_shared", ""),
                "dataQualityStatus": el.get("data_quality_status", ""),
                "sourceIds": el.get("source_ids", ""),
                "notes": el.get("notes", ""),
            },
        })

    out = {
        "generatedFrom": live_db_dir,
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "events": events_out,
        "entrantsByEvent": entrants_by_event,
        "reviews": reviews_out,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))

    size_kb = os.path.getsize(out_path) / 1024
    print(f"Wrote {out_path} ({size_kb:.0f} KB): {len(events_out)} events, "
          f"{sum(len(v) for v in entrants_by_event.values())} entrant rows, {len(reviews_out)} review rows.")


if __name__ == "__main__":
    live_dir = sys.argv[1] if len(sys.argv) > 1 else default_live_db_path()
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "webapp", "data.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(live_dir, out)
