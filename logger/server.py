# -*- coding: utf-8 -*-
"""
Royal Rumble Event Logger -- local server.

Stdlib only (http.server + sqlite3), deliberately -- "standalone,
reliable" per the approved brief means no dependency install step
between cloning this folder and running it. Serves:
  - the static frontend (static/index.html) at /
  - a small JSON API at /api/* backing the Review workflow

Run: python3 server.py [port]   (default port 8420)
Then open http://localhost:8420/ in a browser.

Before first use, run import_adapter.py to build/refresh data/logger.db
from the live Royal Rumble database. Re-run it any time the live
database changes (new event added, a correction merged) -- it's safe
to re-run repeatedly; see import_adapter.py's own docstring for exactly
what does and doesn't get overwritten on a re-import.
"""
import json
import os
import sqlite3
import sys
import datetime
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "data", "logger.db")
STATIC_DIR = os.path.join(HERE, "static")

VERIFICATION_STATUSES = ("unreviewed", "confirmed", "corrected", "uncertain", "conflict")

REVIEW_EDITABLE_FIELDS = [
    "reviewed_eliminator_wrestler_id", "reviewed_assisting_wrestler_ids",
    "reviewed_order_in_match", "reviewed_elimination_clock_time",
    "reviewed_elimination_method", "reviewed_location_side",
    "reviewed_location_zone_id", "reviewed_location_x", "reviewed_location_y",
    "reviewed_elimination_type", "reviewed_is_solo", "reviewed_is_shared",
    "reviewed_notes",
]


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def row_order_key(row):
    # Orders a review row within its event: numeric order_in_match first
    # (using whichever of reviewed/imported is populated), unordered rows
    # (order_in_match blank on both) sort to the end by eliminated_wrestler_id
    # so the queue is at least stable, never silently reshuffled between loads.
    order = row["reviewed_order_in_match"] or row["imported_order_in_match"]
    try:
        return (0, int(order))
    except (TypeError, ValueError):
        return (1, row["eliminated_wrestler_id"])


def wrestler_name_map(conn):
    cur = conn.execute("SELECT wrestler_id, ring_name FROM wrestlers")
    return {r["wrestler_id"]: r["ring_name"] for r in cur.fetchall()}


def review_to_dict(row, names):
    d = dict(row)
    d["eliminated_wrestler_name"] = names.get(row["eliminated_wrestler_id"], row["eliminated_wrestler_id"])
    d["imported_eliminator_wrestler_name"] = names.get(row["imported_eliminator_wrestler_id"], row["imported_eliminator_wrestler_id"])
    d["reviewed_eliminator_wrestler_name"] = names.get(row["reviewed_eliminator_wrestler_id"], row["reviewed_eliminator_wrestler_id"])
    return d


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep the console quiet; errors still raise/print via default 500 handling

    # ---------------- routing ----------------

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            return self.serve_static("index.html")
        if path.startswith("/static/"):
            return self.serve_static(path[len("/static/"):])

        if path == "/api/events":
            return self.api_events()
        if path == "/api/next-unreviewed":
            return self.api_next_unreviewed(qs)
        if path.startswith("/api/events/"):
            event_id = path[len("/api/events/"):]
            return self.api_event_detail(event_id)
        if path.startswith("/api/review/"):
            review_id = path[len("/api/review/"):]
            return self.api_review_get(review_id)
        if path == "/api/wrestlers":
            return self.api_wrestlers(qs)
        if path == "/api/overview":
            return self.api_overview(qs)
        if path == "/api/import-log":
            return self.api_import_log()

        self.send_error(404, "Not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            return self.send_json({"error": "invalid JSON body"}, status=400)

        if path.startswith("/api/review/"):
            review_id = path[len("/api/review/"):]
            return self.api_review_save(review_id, payload)
        if path.startswith("/api/events/") and path.endswith("/video"):
            event_id = path[len("/api/events/"):-len("/video")]
            return self.api_set_video_reference(event_id, payload)

        self.send_error(404, "Not found")

    # ---------------- static ----------------

    def serve_static(self, rel_path):
        rel_path = rel_path or "index.html"
        full = os.path.normpath(os.path.join(STATIC_DIR, rel_path))
        if not full.startswith(STATIC_DIR) or not os.path.isfile(full):
            return self.send_error(404, "Not found")
        ctype = "text/html"
        if full.endswith(".js"):
            ctype = "application/javascript"
        elif full.endswith(".css"):
            ctype = "text/css"
        elif full.endswith(".json"):
            ctype = "application/json"
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, obj, status=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ---------------- API: events ----------------

    def api_events(self):
        conn = get_conn()
        rows = conn.execute("SELECT * FROM events ORDER BY event_date").fetchall()
        out = []
        for ev in rows:
            counts = conn.execute("""
                SELECT verification_status, COUNT(*) as n FROM elimination_reviews
                WHERE event_id = ? GROUP BY verification_status
            """, (ev["event_id"],)).fetchall()
            count_map = {s: 0 for s in VERIFICATION_STATUSES}
            for c in counts:
                count_map[c["verification_status"]] = c["n"]
            total = sum(count_map.values())
            conflict_count = conn.execute(
                "SELECT COUNT(*) as n FROM elimination_reviews WHERE event_id=? AND import_conflict=1",
                (ev["event_id"],)
            ).fetchone()["n"]
            out.append({
                "eventId": ev["event_id"], "eventName": ev["event_name"], "matchName": ev["match_name"],
                "division": ev["division"], "eventDate": ev["event_date"],
                "entrantCount": ev["entrant_count"], "videoReference": ev["video_reference"],
                "total": total, "counts": count_map,
                "reviewedCount": total - count_map["unreviewed"],
                "importConflicts": conflict_count,
            })
        conn.close()
        self.send_json({"events": out})

    def api_event_detail(self, event_id):
        conn = get_conn()
        ev = conn.execute("SELECT * FROM events WHERE event_id=?", (event_id,)).fetchone()
        if not ev:
            conn.close()
            return self.send_error(404, "Event not found")
        names = wrestler_name_map(conn)
        entrants = conn.execute("""
            SELECT * FROM entrants WHERE event_id=? ORDER BY CAST(entry_number AS INTEGER)
        """, (event_id,)).fetchall()
        entrant_list = [{
            "wrestlerId": e["wrestler_id"], "name": names.get(e["wrestler_id"], e["wrestler_id"]),
            "entryNumber": e["entry_number"], "ringNameAtTime": e["ring_name_at_time"],
            "isWinner": e["is_winner"] == "TRUE",
        } for e in entrants]

        reviews = conn.execute("SELECT * FROM elimination_reviews WHERE event_id=?", (event_id,)).fetchall()
        reviews = sorted(reviews, key=row_order_key)
        review_list = [review_to_dict(r, names) for r in reviews]
        conn.close()
        self.send_json({
            "event": {
                "eventId": ev["event_id"], "eventName": ev["event_name"], "matchName": ev["match_name"],
                "division": ev["division"], "eventDate": ev["event_date"], "durationTotal": ev["duration_total"],
                "entrantCount": ev["entrant_count"], "videoReference": ev["video_reference"],
                "videoReferenceNotes": ev["video_reference_notes"],
            },
            "entrants": entrant_list,
            "reviews": review_list,
        })

    def api_set_video_reference(self, event_id, payload):
        conn = get_conn()
        conn.execute("UPDATE events SET video_reference=?, video_reference_notes=? WHERE event_id=?", (
            payload.get("videoReference", ""), payload.get("videoReferenceNotes", ""), event_id,
        ))
        conn.commit()
        conn.close()
        self.send_json({"ok": True})

    # ---------------- API: review ----------------

    def api_review_get(self, review_id):
        conn = get_conn()
        names = wrestler_name_map(conn)
        row = conn.execute("SELECT * FROM elimination_reviews WHERE review_id=?", (review_id,)).fetchone()
        if not row:
            conn.close()
            return self.send_error(404, "Review row not found")
        conn.close()
        self.send_json({"review": review_to_dict(row, names)})

    def api_review_save(self, review_id, payload):
        status = payload.get("verificationStatus")
        if status not in VERIFICATION_STATUSES:
            return self.send_json({"error": f"verificationStatus must be one of {VERIFICATION_STATUSES}"}, status=400)

        conn = get_conn()
        row = conn.execute("SELECT * FROM elimination_reviews WHERE review_id=?", (review_id,)).fetchone()
        if not row:
            conn.close()
            return self.send_error(404, "Review row not found")

        updates = {}
        for field in REVIEW_EDITABLE_FIELDS:
            key = field[len("reviewed_"):]
            # accept either snake_case or camelCase from the client
            camel = "".join(w.capitalize() if i else w for i, w in enumerate(key.split("_")))
            if key in payload:
                updates[field] = payload[key]
            elif camel in payload:
                updates[field] = payload[camel]

        set_clause = ", ".join(f"{f}=?" for f in updates) + (", " if updates else "")
        conn.execute(f"""
            UPDATE elimination_reviews SET {set_clause}
                verification_status=?, import_conflict=0, reviewed_at=?
            WHERE review_id=?
        """, list(updates.values()) + [status, datetime.datetime.now().isoformat(timespec="seconds"), review_id])
        conn.commit()

        # find next-unreviewed within the same event for a smooth "Save & Next"
        next_row = conn.execute("""
            SELECT review_id FROM elimination_reviews
            WHERE event_id=? AND verification_status='unreviewed' AND review_id != ?
        """, (row["event_id"], review_id)).fetchall()
        conn.close()

        next_id = None
        if next_row:
            # pick lowest by the same ordering used for display
            conn2 = get_conn()
            candidates = conn2.execute("SELECT * FROM elimination_reviews WHERE event_id=? AND verification_status='unreviewed'", (row["event_id"],)).fetchall()
            conn2.close()
            candidates = sorted(candidates, key=row_order_key)
            if candidates:
                next_id = candidates[0]["review_id"]

        self.send_json({"ok": True, "nextReviewIdInEvent": next_id})

    def api_next_unreviewed(self, qs):
        event_id = qs.get("event_id", [None])[0]
        conn = get_conn()
        if event_id:
            rows = conn.execute("SELECT * FROM elimination_reviews WHERE event_id=? AND verification_status='unreviewed'", (event_id,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT er.* FROM elimination_reviews er
                JOIN events ev ON ev.event_id = er.event_id
                WHERE er.verification_status='unreviewed'
                ORDER BY ev.event_date
            """).fetchall()
        conn.close()
        if not rows:
            return self.send_json({"reviewId": None, "eventId": None})
        if event_id:
            rows = sorted(rows, key=row_order_key)
            chosen = rows[0]
        else:
            # global "continue" -- earliest event (by date) with any unreviewed row,
            # then lowest order within it, so Continue always walks chronologically
            first_event_id = rows[0]["event_id"]
            same_event = [r for r in rows if r["event_id"] == first_event_id]
            chosen = sorted(same_event, key=row_order_key)[0]
        self.send_json({"reviewId": chosen["review_id"], "eventId": chosen["event_id"]})

    # ---------------- API: wrestlers / overview ----------------

    def api_wrestlers(self, qs):
        q = (qs.get("q", [""])[0] or "").strip().lower()
        conn = get_conn()
        if q:
            rows = conn.execute(
                "SELECT wrestler_id, ring_name FROM wrestlers WHERE LOWER(ring_name) LIKE ? ORDER BY ring_name LIMIT 25",
                (f"%{q}%",)
            ).fetchall()
        else:
            rows = []
        conn.close()
        self.send_json({"wrestlers": [{"wrestlerId": r["wrestler_id"], "name": r["ring_name"]} for r in rows]})

    def api_overview(self, qs):
        conn = get_conn()
        names = wrestler_name_map(conn)
        event_id = qs.get("event_id", [None])[0]
        status = qs.get("status", [None])[0]
        only_conflicts = qs.get("conflicts", ["0"])[0] == "1"

        sql = "SELECT er.*, ev.event_name, ev.event_date FROM elimination_reviews er JOIN events ev ON ev.event_id = er.event_id WHERE 1=1"
        params = []
        if event_id:
            sql += " AND er.event_id=?"
            params.append(event_id)
        if status:
            sql += " AND er.verification_status=?"
            params.append(status)
        if only_conflicts:
            sql += " AND er.import_conflict=1"
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        rows = sorted(rows, key=lambda r: (r["event_date"], row_order_key(r)))
        out = []
        for r in rows:
            d = review_to_dict(r, names)
            d["eventName"] = r["event_name"]
            d["eventDate"] = r["event_date"]
            out.append(d)
        self.send_json({"rows": out})

    def api_import_log(self):
        conn = get_conn()
        rows = conn.execute("SELECT * FROM import_log ORDER BY imported_at DESC LIMIT 10").fetchall()
        conn.close()
        self.send_json({"log": [dict(r) for r in rows]})


def main():
    if not os.path.exists(DB_PATH):
        print(f"No database found at {DB_PATH}. Run `python3 import_adapter.py` first.")
        sys.exit(1)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8420
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Royal Rumble Event Logger running at http://localhost:{port}/")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
