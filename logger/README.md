# Royal Rumble Event Logger — V1

A standalone tool for reviewing every already-recorded elimination in the
Royal Rumble database against your own footage, one at a time, with every
field pre-populated from what's already there. This is V1 of the tool
scoped in the "Royal Rumble Event Logger — Architecture & Development
Plan" document — the existing-data-first Logger, built around the
Load → Watch → Click → Verify → Save & Next flow. It does not include the
Arena Configuration or Heatmap pieces from that plan; those are later
phases.

## What it is

- A local web app: a small Python server (stdlib only — no `pip install`
  needed) plus a single-page frontend, backed by a local SQLite file.
- It imports a working copy of the *current* elimination data from the
  live Royal Rumble database. Nothing you do here touches the live
  database directly — see "Getting your work back out" below.
- Every elimination fact starts pre-populated with whatever's already
  recorded (order, clock time, method, etc.) so reviewing is "confirm
  this is right" far more often than "type it from scratch."

## Running it

This tool now lives inside the `royal-rumble-database` GitHub repo, as
the `logger/` folder at the repo root — so a single `git clone` gets
you the database and the Logger together, always pointed at the same
data:

```
git clone https://github.com/humphreysshane/royal-rumble-database.git
cd royal-rumble-database/logger
python3 import_adapter.py     # builds/refreshes data/logger.db from ../data (the live database)
python3 server.py             # starts the server on http://localhost:8420
```

Then open `http://localhost:8420/` in a browser. No build step, no
dependencies beyond a normal Python 3 install.

By default `import_adapter.py` looks for the live database one level
up, at `../data` — i.e. the repo's own `data/` folder, since `logger/`
sits at the repo root beside it. Pass a different path as an argument
if you're pointing it at some other copy of the database:
`python3 import_adapter.py /path/to/royal_rumble_database/data`.

To pick up corrections merged into the repo after you last ran it —
whether from the live GitHub Actions build, another contributor, or
your own earlier review session — `git pull` and rerun
`import_adapter.py`; the three-state field model below is what makes
that safe to do at any time, mid-review.

## The workflow

**Home** shows every event with a progress bar and a single big
**Continue from next unreviewed elimination** button — click it and
you're straight into the review screen for whatever's next, chronologically.

**Review screen**: every field is pre-populated from the current data.
Set a video reference on the event's Overview page first (a local file
path or a URL — just a text note for now, V1 doesn't embed a video
player) so you know what you're checking against. Watch, correct
anything that's wrong, then pick one of four outcomes:

- **Confirm as-is** (key `1`) — matches the footage exactly.
- **Save correction** (key `2`) — you changed something above.
- **Mark uncertain** (key `3`) — not confident, needs another pass.
- **Flag conflict** (key `4`) — your footage and the recorded sources
  genuinely disagree.

Any of these saves and jumps straight to the next unreviewed elimination
in the same event (Save & Next). Left/right arrow keys move between
eliminations without saving, for double-checking. A **Jump** bar and the
event's **Overview** table (click any row) let you go straight to a
specific one.

**Overview** (top nav) is a searchable/filterable table across every
event — filter by status, or by "import conflicts only" (see below).

## The three-state field model, and why re-importing is safe

Every field has an `imported_*` value (a read-only snapshot of what's
currently in the live database) and a `reviewed_*` value (what you see
and edit on the Review screen, seeded from `imported_*` the first time).
Re-running `import_adapter.py` — say, after I merge a database correction
from the other side — is always safe:

- An **unreviewed** row gets both its `imported_*` and `reviewed_*`
  refreshed to match the current live data (nothing to lose yet).
- An **already-reviewed** row's `reviewed_*` (your work) is never
  touched by a re-import. Its `imported_*` snapshot is refreshed so you
  can see what's live now, and if that actually changed since you
  reviewed it, the row is flagged `import_conflict` — visible on the
  Overview page's "import conflicts only" filter — rather than either
  silently keeping your old review or silently overwriting it. Those are
  rare (only happens if I correct something you'd already reviewed) but
  worth a human glance when they occur.

One identity note: a single victim can have several genuinely separate
elimination rows in the live database — a "group elimination" where
multiple wrestlers jointly eliminated one entrant (e.g. RR2023W's Nia
Jax has 11 separate rows, one per contributing eliminator). The Logger
keys each of those as its own reviewable row, not one row per victim —
this was caught and fixed during this tool's own testing before it
shipped (see the comment at the top of `import_adapter.py` if you're
curious what that bug looked like).

## Getting your work back out

```
python3 export_sync.py
```

This reads every reviewed row and writes a **proposed** replacement
`eliminations.csv` to `export/eliminations_proposed_<timestamp>.csv`,
plus a plain-text summary of exactly which rows changed and how. It does
**not** touch the live database. Your review status maps to the
database's own data-quality vocabulary:

| Logger status | `data_quality_status` |
|---|---|
| Confirmed | CONFIRMED |
| Corrected | PROBABLE |
| Uncertain | UNCERTAIN |
| Conflict | CONFLICTING |

Now that the database lives in the `royal-rumble-database` repo, turn a
proposed export into a pull request the same way any other database
change gets merged:

```
cd royal-rumble-database
git checkout -b logger-review-<event-or-date>
cp logger/export/eliminations_proposed_<timestamp>.csv data/eliminations.csv
python3 scripts/build_derived.py
python3 scripts/build_dashboard_data.py
python3 scripts/validate_integrity.py data
git add data/eliminations.csv data/derived/ dashboard/data.json
git commit -m "Logger review: <event(s) reviewed>"
git push -u origin logger-review-<event-or-date>
```

Then open a PR from that branch on GitHub as usual — same review step
before it merges into `main` as any other change, human or AI. This
replaces sending me the `export/` folder directly, though that's still
fine if you'd rather have it checked before it's a PR. You don't need
to finish every event before exporting a batch — partial progress
exports fine, same fields that are still `unreviewed` just won't be in
the export.

## What's not in V1

- No embedded video player — the video reference field is just a note
  (path or URL) for now. Watching happens in whatever player you
  already use, side by side with the browser.
- No Arena Configuration UI or spatial Heatmap — those are separate,
  later phases in the approved plan. The three new `reviewed_location_*`
  fields (zone id, x, y) exist in the schema already so this V1 doesn't
  need a schema change when that phase starts, but there's no UI for
  them yet beyond the existing Left/Right/Hard camera/Corner/Unknown
  side dropdown.
- No multi-user support — this is a single local SQLite file for one
  reviewer at a time, per the "standalone" brief.

## Files

- `import_adapter.py` — builds/refreshes `data/logger.db` from the live
  database's CSVs. Safe to re-run any time.
- `server.py` — the local web server (stdlib `http.server` + `sqlite3`,
  no dependencies). Serves the frontend and a small JSON API.
- `static/index.html` — the entire frontend (single file, vanilla JS).
- `export_sync.py` — turns reviewed rows into a proposed CSV + summary
  for me to verify and merge.
- `data/logger.db` — your local working database. This is where your
  review progress lives between sessions; back it up if you want, but
  don't send it to me directly — send the `export_sync.py` output
  instead, since that's what actually needs verifying against sources.
