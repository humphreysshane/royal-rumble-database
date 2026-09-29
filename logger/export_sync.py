# -*- coding: utf-8 -*-
"""
Export/Sync-to-CSV -- turns the Logger's reviewed rows back into a
proposed eliminations.csv.

DELIBERATELY DOES NOT TOUCH THE LIVE DATABASE. It writes a proposed
replacement file to export/eliminations_proposed_<timestamp>.csv plus a
plain-text change summary. Merging into the live database still goes
through the project's standard protocol: isolated-copy test,
build_derived.py, build_dashboard_data.py, validate_integrity.py,
smoke test, THEN merge -- same as every other change to this database
this whole project. This script only produces the proposed file; it
never merges it.

Only rows with verification_status != 'unreviewed' are exported.
Fields the Logger doesn't edit (is_accidental, is_self_elimination,
is_storyline_related, was_already_incapacitated, is_disputed,
simultaneous_group_id) are carried over unchanged from the live row --
this export never invents a value for a field it never asked about.

Vocabulary mapping (Logger workflow status -> database data_quality_status),
per the approved Logger plan:
    confirmed -> CONFIRMED
    corrected -> PROBABLE
    uncertain -> UNCERTAIN
    conflict  -> CONFLICTING
"""
import csv
import os
import sqlite3
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "data", "logger.db")
EXPORT_DIR = os.path.join(HERE, "export")

STATUS_MAP = {
    "confirmed": "CONFIRMED",
    "corrected": "PROBABLE",
    "uncertain": "UNCERTAIN",
    "conflict": "CONFLICTING",
}

ELIMINATIONS_FIELDS = [
    "event_id", "order_in_match", "eliminated_wrestler_id",
    "eliminator_wrestler_id", "assisting_wrestler_ids",
    "entry_number_of_eliminated", "entry_number_of_eliminator",
    "elimination_clock_time", "elimination_clock_seconds",
    "elimination_type", "elimination_method", "location_side", "location_status",
    "is_solo", "is_shared", "is_accidental", "is_self_elimination",
    "is_storyline_related", "was_already_incapacitated", "is_disputed",
    "simultaneous_group_id", "data_quality_status", "source_ids", "notes",
]


def mmss_to_seconds(t):
    if not t or ":" not in t:
        return ""
    try:
        parts = [int(p) for p in t.strip().split(":")]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
    except ValueError:
        return ""
    return ""


def run_export(live_db_dir):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    live_path = os.path.join(live_db_dir, "eliminations.csv")
    with open(live_path, newline="", encoding="utf-8") as f:
        live_rows = list(csv.DictReader(f))
    # Key is the full triple, matching elimination_reviews' own natural key
    # (see import_adapter.py's schema comment) -- (event_id, eliminated_wrestler_id)
    # alone is not unique: group eliminations put several real rows against
    # one victim, one per contributing eliminator.
    live_by_key = {(r["event_id"], r["eliminated_wrestler_id"], r["eliminator_wrestler_id"]): r for r in live_rows}

    # entry_number lookups, needed to fill entry_number_of_eliminated/eliminator
    entrants_path = os.path.join(live_db_dir, "entrants.csv")
    with open(entrants_path, newline="", encoding="utf-8") as f:
        entry_lookup = {(r["event_id"], r["wrestler_id"]): r["entry_number"] for r in csv.DictReader(f)}

    reviewed = conn.execute("""
        SELECT * FROM elimination_reviews WHERE verification_status != 'unreviewed'
    """).fetchall()
    conn.close()

    if not reviewed:
        print("No reviewed rows yet -- nothing to export.")
        return None

    changed_summary = []
    out_rows = list(live_rows)  # start from a full copy of the live file
    out_by_key = dict(live_by_key)

    for rv in reviewed:
        # keyed on the ORIGINAL (imported) eliminator, not the possibly-edited
        # reviewed one -- this is the row's identity, established at import time;
        # correcting the eliminator is an edit to this row, not a new key
        key = (rv["event_id"], rv["eliminated_wrestler_id"], rv["imported_eliminator_wrestler_id"])
        if key not in out_by_key:
            print(f"WARNING: reviewed row {rv['event_id']}/{rv['eliminated_wrestler_id']}/"
                  f"{rv['imported_eliminator_wrestler_id']} has no matching live row (live database "
                  f"may have changed since this was imported -- re-run import_adapter.py) -- skipped.")
            continue
        base = dict(out_by_key[key])
        before = dict(base)

        base["order_in_match"] = rv["reviewed_order_in_match"] or ""
        base["eliminator_wrestler_id"] = rv["reviewed_eliminator_wrestler_id"] or ""
        base["assisting_wrestler_ids"] = rv["reviewed_assisting_wrestler_ids"] or ""
        base["elimination_clock_time"] = rv["reviewed_elimination_clock_time"] or ""
        secs = mmss_to_seconds(rv["reviewed_elimination_clock_time"] or "")
        base["elimination_clock_seconds"] = str(secs) if secs != "" else ""
        base["elimination_type"] = rv["reviewed_elimination_type"] or ""
        base["elimination_method"] = rv["reviewed_elimination_method"] or ""
        base["location_side"] = rv["reviewed_location_side"] or ""
        base["is_solo"] = rv["reviewed_is_solo"] or ""
        base["is_shared"] = rv["reviewed_is_shared"] or ""
        base["entry_number_of_eliminated"] = entry_lookup.get((rv["event_id"], rv["eliminated_wrestler_id"]), "")
        base["entry_number_of_eliminator"] = entry_lookup.get((rv["event_id"], rv["reviewed_eliminator_wrestler_id"]), "")
        base["data_quality_status"] = STATUS_MAP[rv["verification_status"]]
        existing_notes = base.get("notes", "") or ""
        review_note = f"[Logger review {rv['reviewed_at']}: {rv['verification_status']}]"
        if review_note not in existing_notes:
            base["notes"] = (existing_notes + " " + review_note).strip()
        if rv["reviewed_notes"]:
            base["notes"] = (base["notes"] + " " + rv["reviewed_notes"]).strip()

        out_by_key[key] = base
        if before != base:
            changed_summary.append((key, before, base))

    # rebuild out_rows in original file order, keyed lookup on the same triple
    out_rows = [out_by_key.get((r["event_id"], r["eliminated_wrestler_id"], r["eliminator_wrestler_id"]), r) for r in live_rows]

    os.makedirs(EXPORT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(EXPORT_DIR, f"eliminations_proposed_{ts}.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ELIMINATIONS_FIELDS)
        w.writeheader()
        for r in out_rows:
            w.writerow({k: r.get(k, "") for k in ELIMINATIONS_FIELDS})

    summary_path = os.path.join(EXPORT_DIR, f"eliminations_proposed_{ts}_SUMMARY.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"Logger export -- {len(changed_summary)} row(s) changed vs. live eliminations.csv\n")
        f.write(f"Live database read from: {live_db_dir}\n\n")
        for key, before, after in changed_summary:
            f.write(f"{key[0]} / eliminated={key[1]} / originally-recorded-eliminator={key[2] or '(blank)'}:\n")
            for field in ELIMINATIONS_FIELDS:
                if before.get(field, "") != after.get(field, ""):
                    f.write(f"    {field}: {before.get(field,'')!r} -> {after.get(field,'')!r}\n")
            f.write("\n")

    print(f"Wrote {out_path} ({len(changed_summary)} row(s) actually changed vs. live)")
    print(f"Wrote {summary_path}")
    print("This is a PROPOSED file, not a live edit -- test it through the standard "
          "isolated-copy protocol (build_derived.py, build_dashboard_data.py, "
          "validate_integrity.py, smoke test) before merging into the live database.")
    return out_path


if __name__ == "__main__":
    # Shipped inside the royal-rumble-database repo as logger/ at repo root.
    live_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.normpath(os.path.join(HERE, "..", "data"))
    run_export(live_dir)
