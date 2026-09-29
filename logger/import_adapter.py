# -*- coding: utf-8 -*-
"""
Import Adapter -- builds/refreshes the Logger's SQLite working store
(data/logger.db) from the live Royal Rumble database's CSV files.

Reads by COLUMN NAME, never column position, so a reordered or
extended CSV (new columns added elsewhere in the database) never
silently misaligns the import -- this was an explicit decision in the
approved Logger plan (Docs artifact "Royal Rumble Event Logger --
Architecture & Development Plan", Section H).

THREE-STATE FIELD MODEL: every elimination-relevant field gets two
columns in elimination_reviews -- an `imported_*` column (a read-only
snapshot of what's currently in the live database) and a `reviewed_*`
column (what the Logger's own review flow edits). On first import,
reviewed_* is seeded from imported_* (this is what makes the review
screen "pre-populated" rather than blank). Re-running this script
against a refreshed live database:
  - never overwrites a row that's already been reviewed
    (verification_status != 'unreviewed') -- imported_* is refreshed
    so you can SEE what changed upstream, but reviewed_* (your work)
    is left alone;
  - for an unreviewed row, re-seeds reviewed_* from the new imported_*
    as normal;
  - if a previously-reviewed row's underlying imported_* values changed
    since it was reviewed (someone corrected the live database in the
    meantime), it's flagged via `import_conflict = 1` rather than
    silently resolved either direction -- surfaced on the Overview
    table so a human decides, never guessed at here.

Natural key: (event_id, eliminated_wrestler_id) for the elimination
fact -- matches the re-import conflict handling approach in the
approved plan. NOTE: this means a wrestler eliminated twice in the same
Rumble in two truly separate elimination facts (has never happened in
this database, but the RR1996M duplicate-row incident this session is
a reminder that literal duplicates can and do creep into eliminations.csv)
is NOT representable by this key -- run scripts/validate_integrity.py
against the live database before importing here; this adapter trusts
that the live database has already been validated and does no
duplicate-detection of its own.
"""
import csv
import os
import sqlite3
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "data", "logger.db")


def default_live_db_path():
    # Now shipped inside the royal-rumble-database repo itself, as the
    # logger/ folder at repo root -- so the live data is just one level up.
    # (Originally this pointed at ../royal_rumble_database/data, back when
    # the Logger was a separately-zipped tool sitting beside a standalone
    # copy of the database folder. If you've kept that older layout instead
    # of cloning the GitHub repo, pass that path explicitly as argv[1].)
    candidate = os.path.join(HERE, "..", "data")
    return os.path.normpath(candidate)


def load_csv(folder, name):
    path = os.path.join(folder, name)
    if not os.path.exists(path):
        print(f"WARNING: {path} not found -- skipping.")
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    event_name TEXT,
    match_name TEXT,
    division TEXT,
    event_date TEXT,
    duration_total TEXT,
    entrant_count INTEGER,
    video_reference TEXT,           -- blank until Shane points this at his own footage (local path or URL)
    video_reference_notes TEXT
);

CREATE TABLE IF NOT EXISTS entrants (
    event_id TEXT,
    wrestler_id TEXT,
    entry_number TEXT,
    ring_name_at_time TEXT,
    is_winner TEXT,
    elim_number TEXT,
    PRIMARY KEY (event_id, wrestler_id)
);

CREATE TABLE IF NOT EXISTS wrestlers (
    wrestler_id TEXT PRIMARY KEY,
    ring_name TEXT
);

-- The core review queue: one row per elimination fact in the live
-- database's eliminations.csv. Natural key is the full triple
-- (event_id, eliminated_wrestler_id, imported_eliminator_wrestler_id) --
-- NOT just (event_id, eliminated_wrestler_id). A single victim can have
-- several genuinely separate elimination-fact rows recorded against
-- different eliminators (a "group elimination", e.g. RR2023W's Nia Jax
-- has 11 -- one row per contributing eliminator, all with the same
-- order_in_match, per the project's own recording convention). Keying on
-- only (event_id, eliminated_wrestler_id) would silently collapse every
-- one of those down to a single row on import, keeping only the last
-- eliminator processed and losing the rest -- caught in testing before
-- this tool shipped (an early version of this file did exactly that).
-- The key deliberately stays anchored to imported_eliminator_wrestler_id,
-- never reviewed_eliminator_wrestler_id: correcting who the eliminator
-- actually was is an edit to a specific elimination-fact row, not a
-- change to which row it is.
CREATE TABLE IF NOT EXISTS elimination_reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL,
    eliminated_wrestler_id TEXT NOT NULL,

    -- read-only snapshot of the live database at last import
    imported_eliminator_wrestler_id TEXT,
    imported_assisting_wrestler_ids TEXT,
    imported_order_in_match TEXT,
    imported_elimination_clock_time TEXT,
    imported_elimination_method TEXT,
    imported_location_side TEXT,
    imported_elimination_type TEXT,
    imported_is_solo TEXT,
    imported_is_shared TEXT,
    imported_data_quality_status TEXT,
    imported_source_ids TEXT,
    imported_notes TEXT,

    -- editable working copy -- seeded from imported_* on first import,
    -- edited during the Watch/Click/Verify review flow from here on
    reviewed_eliminator_wrestler_id TEXT,
    reviewed_assisting_wrestler_ids TEXT,
    reviewed_order_in_match TEXT,
    reviewed_elimination_clock_time TEXT,
    reviewed_elimination_method TEXT,
    reviewed_location_side TEXT,
    reviewed_location_zone_id TEXT,     -- new spatial fields, not in the live schema yet -- see README
    reviewed_location_x REAL,
    reviewed_location_y REAL,
    reviewed_elimination_type TEXT,
    reviewed_is_solo TEXT,
    reviewed_is_shared TEXT,
    reviewed_notes TEXT,

    -- Logger workflow state. Vocabulary mapping to the live database's
    -- data_quality_status happens at export time (export_sync.py):
    --   unreviewed -> (not exported)
    --   confirmed  -> CONFIRMED
    --   corrected  -> PROBABLE
    --   uncertain  -> UNCERTAIN
    --   conflict   -> CONFLICTING
    verification_status TEXT NOT NULL DEFAULT 'unreviewed',
    import_conflict INTEGER NOT NULL DEFAULT 0,  -- 1 = imported_* changed since this row was reviewed
    reviewed_at TEXT,

    UNIQUE (event_id, eliminated_wrestler_id, imported_eliminator_wrestler_id)
);

CREATE INDEX IF NOT EXISTS idx_reviews_event ON elimination_reviews(event_id);
CREATE INDEX IF NOT EXISTS idx_reviews_status ON elimination_reviews(verification_status);

CREATE TABLE IF NOT EXISTS import_log (
    imported_at TEXT,
    events_imported INTEGER,
    entrants_imported INTEGER,
    reviews_seeded INTEGER,
    reviews_refreshed_imported_snapshot INTEGER,
    reviews_flagged_conflict INTEGER,
    reviews_left_untouched INTEGER
);
"""


def run_import(live_db_dir=None):
    live_db_dir = live_db_dir or default_live_db_path()
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    events = load_csv(live_db_dir, "events.csv")
    entrants = load_csv(live_db_dir, "entrants.csv")
    eliminations = load_csv(live_db_dir, "eliminations.csv")
    wrestlers = load_csv(live_db_dir, "wrestlers.csv")

    if not events or not eliminations:
        print("ERROR: events.csv or eliminations.csv missing/empty at", live_db_dir)
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    cur = conn.cursor()

    # --- events (always refreshed -- read-only reference data) ---
    for ev in events:
        cur.execute("""
            INSERT INTO events (event_id, event_name, match_name, division, event_date, duration_total, entrant_count, video_reference, video_reference_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?,
                    COALESCE((SELECT video_reference FROM events WHERE event_id = ?), ''),
                    COALESCE((SELECT video_reference_notes FROM events WHERE event_id = ?), ''))
            ON CONFLICT(event_id) DO UPDATE SET
                event_name=excluded.event_name, match_name=excluded.match_name,
                division=excluded.division, event_date=excluded.event_date,
                duration_total=excluded.duration_total, entrant_count=excluded.entrant_count
        """, (
            ev["event_id"], ev.get("event_name", ""), ev.get("match_name", ""),
            ev.get("match_type", ""), ev.get("event_date", ""), ev.get("duration_total", ""),
            int(ev["entrant_count"]) if (ev.get("entrant_count") or "").isdigit() else None,
            ev["event_id"], ev["event_id"],
        ))

    # --- wrestlers (id -> display name lookup, read-only reference) ---
    for w in wrestlers:
        cur.execute("""
            INSERT INTO wrestlers (wrestler_id, ring_name) VALUES (?, ?)
            ON CONFLICT(wrestler_id) DO UPDATE SET ring_name=excluded.ring_name
        """, (w["wrestler_id"], w.get("ring_name", "")))

    # --- entrants (always refreshed -- read-only reference data) ---
    cur.execute("DELETE FROM entrants")
    for e in entrants:
        cur.execute("""
            INSERT INTO entrants (event_id, wrestler_id, entry_number, ring_name_at_time, is_winner, elim_number)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            e["event_id"], e["wrestler_id"], e.get("entry_number", ""),
            e.get("ring_name_at_time", ""), e.get("is_winner", ""), e.get("elim_number", ""),
        ))

    # --- elimination_reviews: the three-state import logic ---
    seeded = 0
    refreshed_snapshot = 0
    flagged_conflict = 0
    left_untouched = 0

    for el in eliminations:
        # full triple -- see the schema comment above on why eliminated_wrestler_id
        # alone is not enough (group eliminations: several real rows per victim)
        key = (el["event_id"], el["eliminated_wrestler_id"], el.get("eliminator_wrestler_id", ""))
        imported_cols = {
            "imported_eliminator_wrestler_id": el.get("eliminator_wrestler_id", ""),
            "imported_assisting_wrestler_ids": el.get("assisting_wrestler_ids", ""),
            "imported_order_in_match": el.get("order_in_match", ""),
            "imported_elimination_clock_time": el.get("elimination_clock_time", ""),
            "imported_elimination_method": el.get("elimination_method", ""),
            "imported_location_side": el.get("location_side", ""),
            "imported_elimination_type": el.get("elimination_type", ""),
            "imported_is_solo": el.get("is_solo", ""),
            "imported_is_shared": el.get("is_shared", ""),
            "imported_data_quality_status": el.get("data_quality_status", ""),
            "imported_source_ids": el.get("source_ids", ""),
            "imported_notes": el.get("notes", ""),
        }

        cur.execute("""
            SELECT review_id, verification_status, imported_eliminator_wrestler_id,
                   imported_order_in_match, imported_elimination_clock_time,
                   imported_elimination_method, imported_location_side,
                   imported_elimination_type, imported_is_solo, imported_is_shared
            FROM elimination_reviews
            WHERE event_id = ? AND eliminated_wrestler_id = ? AND imported_eliminator_wrestler_id = ?
        """, key)
        existing = cur.fetchone()

        if existing is None:
            # brand new row -- insert with reviewed_* seeded from imported_*
            cur.execute("""
                INSERT INTO elimination_reviews (
                    event_id, eliminated_wrestler_id,
                    imported_eliminator_wrestler_id, imported_assisting_wrestler_ids,
                    imported_order_in_match, imported_elimination_clock_time,
                    imported_elimination_method, imported_location_side,
                    imported_elimination_type, imported_is_solo, imported_is_shared,
                    imported_data_quality_status, imported_source_ids, imported_notes,
                    reviewed_eliminator_wrestler_id, reviewed_assisting_wrestler_ids,
                    reviewed_order_in_match, reviewed_elimination_clock_time,
                    reviewed_elimination_method, reviewed_location_side,
                    reviewed_elimination_type, reviewed_is_solo, reviewed_is_shared,
                    reviewed_notes, verification_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'unreviewed')
            """, (
                key[0], key[1],
                imported_cols["imported_eliminator_wrestler_id"], imported_cols["imported_assisting_wrestler_ids"],
                imported_cols["imported_order_in_match"], imported_cols["imported_elimination_clock_time"],
                imported_cols["imported_elimination_method"], imported_cols["imported_location_side"],
                imported_cols["imported_elimination_type"], imported_cols["imported_is_solo"], imported_cols["imported_is_shared"],
                imported_cols["imported_data_quality_status"], imported_cols["imported_source_ids"], imported_cols["imported_notes"],
                # reviewed_* seeded identical to imported_* -- this is the "pre-populated" part
                imported_cols["imported_eliminator_wrestler_id"], imported_cols["imported_assisting_wrestler_ids"],
                imported_cols["imported_order_in_match"], imported_cols["imported_elimination_clock_time"],
                imported_cols["imported_elimination_method"], imported_cols["imported_location_side"],
                imported_cols["imported_elimination_type"], imported_cols["imported_is_solo"], imported_cols["imported_is_shared"],
                imported_cols["imported_notes"],
            ))
            seeded += 1
        else:
            review_id, status = existing[0], existing[1]
            old_snapshot = existing[2:]
            new_snapshot = (
                imported_cols["imported_eliminator_wrestler_id"], imported_cols["imported_order_in_match"],
                imported_cols["imported_elimination_clock_time"], imported_cols["imported_elimination_method"],
                imported_cols["imported_location_side"], imported_cols["imported_elimination_type"],
                imported_cols["imported_is_solo"], imported_cols["imported_is_shared"],
            )
            changed_upstream = tuple(old_snapshot) != new_snapshot

            if status == "unreviewed":
                # safe to refresh both imported_* and reviewed_* (nothing to lose)
                cur.execute("""
                    UPDATE elimination_reviews SET
                        imported_eliminator_wrestler_id=?, imported_assisting_wrestler_ids=?,
                        imported_order_in_match=?, imported_elimination_clock_time=?,
                        imported_elimination_method=?, imported_location_side=?,
                        imported_elimination_type=?, imported_is_solo=?, imported_is_shared=?,
                        imported_data_quality_status=?, imported_source_ids=?, imported_notes=?,
                        reviewed_eliminator_wrestler_id=?, reviewed_assisting_wrestler_ids=?,
                        reviewed_order_in_match=?, reviewed_elimination_clock_time=?,
                        reviewed_elimination_method=?, reviewed_location_side=?,
                        reviewed_elimination_type=?, reviewed_is_solo=?, reviewed_is_shared=?,
                        reviewed_notes=?, import_conflict=0
                    WHERE review_id=?
                """, (
                    imported_cols["imported_eliminator_wrestler_id"], imported_cols["imported_assisting_wrestler_ids"],
                    imported_cols["imported_order_in_match"], imported_cols["imported_elimination_clock_time"],
                    imported_cols["imported_elimination_method"], imported_cols["imported_location_side"],
                    imported_cols["imported_elimination_type"], imported_cols["imported_is_solo"], imported_cols["imported_is_shared"],
                    imported_cols["imported_data_quality_status"], imported_cols["imported_source_ids"], imported_cols["imported_notes"],
                    imported_cols["imported_eliminator_wrestler_id"], imported_cols["imported_assisting_wrestler_ids"],
                    imported_cols["imported_order_in_match"], imported_cols["imported_elimination_clock_time"],
                    imported_cols["imported_elimination_method"], imported_cols["imported_location_side"],
                    imported_cols["imported_elimination_type"], imported_cols["imported_is_solo"], imported_cols["imported_is_shared"],
                    imported_cols["imported_notes"],
                    review_id,
                ))
                refreshed_snapshot += 1
            else:
                # already reviewed -- NEVER touch reviewed_*. Refresh the
                # imported_* snapshot so it's visible, and flag a conflict
                # if what's live now actually differs from what this row
                # was reviewed against.
                cur.execute("""
                    UPDATE elimination_reviews SET
                        imported_eliminator_wrestler_id=?, imported_assisting_wrestler_ids=?,
                        imported_order_in_match=?, imported_elimination_clock_time=?,
                        imported_elimination_method=?, imported_location_side=?,
                        imported_elimination_type=?, imported_is_solo=?, imported_is_shared=?,
                        imported_data_quality_status=?, imported_source_ids=?, imported_notes=?,
                        import_conflict=?
                    WHERE review_id=?
                """, (
                    imported_cols["imported_eliminator_wrestler_id"], imported_cols["imported_assisting_wrestler_ids"],
                    imported_cols["imported_order_in_match"], imported_cols["imported_elimination_clock_time"],
                    imported_cols["imported_elimination_method"], imported_cols["imported_location_side"],
                    imported_cols["imported_elimination_type"], imported_cols["imported_is_solo"], imported_cols["imported_is_shared"],
                    imported_cols["imported_data_quality_status"], imported_cols["imported_source_ids"], imported_cols["imported_notes"],
                    1 if changed_upstream else 0,
                    review_id,
                ))
                if changed_upstream:
                    flagged_conflict += 1
                else:
                    left_untouched += 1

    cur.execute("""
        INSERT INTO import_log (imported_at, events_imported, entrants_imported, reviews_seeded, reviews_refreshed_imported_snapshot, reviews_flagged_conflict, reviews_left_untouched)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.datetime.now().isoformat(timespec="seconds"),
        len(events), len(entrants), seeded, refreshed_snapshot, flagged_conflict, left_untouched,
    ))

    conn.commit()
    conn.close()

    print(f"Import complete from {live_db_dir}")
    print(f"  {len(events)} events, {len(entrants)} entrants, {len(wrestlers)} wrestlers referenced")
    print(f"  elimination_reviews: {seeded} new rows seeded, {refreshed_snapshot} unreviewed rows refreshed, "
          f"{flagged_conflict} previously-reviewed rows flagged import_conflict, {left_untouched} previously-reviewed rows untouched")
    if flagged_conflict:
        print(f"  NOTE: {flagged_conflict} row(s) need a human look -- their live data changed after they were "
              f"already reviewed in the Logger. See the Overview page's conflict filter.")


if __name__ == "__main__":
    live_dir = sys.argv[1] if len(sys.argv) > 1 else None
    run_import(live_dir)
