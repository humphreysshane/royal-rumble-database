#!/usr/bin/env python3
"""
Fact-check fix: RR1992M eliminator ID confusion between two DIFFERENT
wrestler_ids that both display as "Big Boss(s) Man":

  - big-bossman   (no hyphen) = Ray Traylor's ORIGINAL WWF-era Big Bossman,
                    the wrestler who actually entered RR1992M at #13 and
                    self-eliminated (lunged at Ric Flair, missed, went over
                    untouched -- entrants.csv/eliminations.csv both already
                    correctly use "big-bossman" for HIS OWN row).
  - big-boss-man  (hyphenated) = a SEPARATE wrestler_id this database uses
                    for Traylor's later 1999-era "Corporation" gimmick
                    appearance (RR1999M/2000M/2002M) -- confirmed by
                    wrestlers.csv's own bio note on that id ("Part of Vince
                    McMahon's Corporation... probably Austin's 4th named
                    elimination, see F119") and by build_1992.py's own
                    WRESTLER_ID_MAP (line 202: "Big Boss Man": "big-bossman").

Discovered during the 1989-1992 fact-check sweep: scripts/factcheck_
elimination_gaps_1991_1997.py (deployed earlier this session under flag
F332) hard-coded the WRONG, hyphenated id when crediting Big Bossman with
two RR1992M eliminations -- Smash (Repo Man) and Hercules. Root cause was a
plain copy-paste of the wrong existing id; the correct one-1992 id was
sitting right there in the same file's own WRESTLER_ID_MAP reference used
for other 1992 credits.

This patch corrects exactly those 2 rows in each of eliminations.csv and
entrants.csv (4 total edits) from "big-boss-man" to "big-bossman". Nothing
else in the database references "big-boss-man" in a way that's wrong -- the
1999/2000/2002 uses of that id were checked and are legitimate (that IS the
correct id for the Corporation-era Big Boss Man in those events).

No new sources are needed -- this is a plain internal-consistency fix
(the correct id, and the underlying facts, were already confirmed and
sourced elsewhere in the database: S020/S021 for the RR1992M elimination
order, and wrestlers.csv's big-bossman row for the wrestler's identity).
One new flag is logged.

Usage:
    python3 factcheck_1992_big_bossman_id.py [data_dir]   (default: data)
"""
import csv
import sys

DATA_DIR = sys.argv[1] if len(sys.argv) > 1 else "data"

WRONG_ID = "big-boss-man"
RIGHT_ID = "big-bossman"


def load(name):
    path = f"{DATA_DIR}/{name}"
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def save(name, fieldnames, rows):
    path = f"{DATA_DIR}/{name}"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    elim_fields, elim_rows = load("eliminations.csv")
    ent_fields, ent_rows = load("entrants.csv")
    flag_fields, flag_rows = load("flags.csv")

    elim_fixed = 0
    for row in elim_rows:
        if (
            row["event_id"] == "RR1992M"
            and row["eliminated_wrestler_id"] in ("smash", "hercules")
            and row["eliminator_wrestler_id"] == WRONG_ID
        ):
            row["eliminator_wrestler_id"] = RIGHT_ID
            elim_fixed += 1

    ent_fixed = 0
    for row in ent_rows:
        if (
            row["event_id"] == "RR1992M"
            and row["wrestler_id"] in ("smash", "hercules")
            and row["eliminated_by_ids"] == WRONG_ID
        ):
            row["eliminated_by_ids"] = RIGHT_ID
            ent_fixed += 1

    assert elim_fixed == 2, f"expected 2 eliminations.csv fixes, got {elim_fixed}"
    assert ent_fixed == 2, f"expected 2 entrants.csv fixes, got {ent_fixed}"

    # new flag id: continue the global sequence from F337
    new_flag_id = "F338"
    flag_rows.append({
        "flag_id": new_flag_id,
        "event_id": "RR1992M",
        "table": "eliminations;entrants",
        "record_id": "smash;hercules",
        "field": "eliminator_wrestler_id;eliminated_by_ids",
        "issue_type": "corrected",
        "description": (
            "Found during the 1989-1992 fact-check sweep. scripts/factcheck_elimination_gaps_"
            "1991_1997.py (deployed earlier this session, flag F332) credited Smash's and "
            "Hercules's RR1992M eliminations to wrestler_id 'big-boss-man' (hyphenated) -- but "
            "that id belongs to a DIFFERENT, later wrestler entry in this database: Ray Traylor's "
            "1999-era 'Corporation' Big Boss Man (see wrestlers.csv's own bio note on that id, "
            "and F119). The wrestler who actually entered RR1992M is a separate, earlier id, "
            "'big-bossman' (no hyphen) -- already used correctly on his own RR1992M row "
            "(entry #13, self-eliminated lunging at Ric Flair) and confirmed as the canonical "
            "1992 id by build_1992.py's own WRESTLER_ID_MAP. Corrected both eliminator credits "
            "(eliminations.csv eliminator_wrestler_id, entrants.csv eliminated_by_ids) from "
            "'big-boss-man' to 'big-bossman'. Internal-consistency fix, no new sources needed -- "
            "the underlying elimination facts were already CONFIRMED via S020/S021/S026/S042, "
            "only the id was wrong."
        ),
        "source_ids_involved": "S020;S021;S026;S042",
        "status": "resolved",
        "date_logged": "2026-09-18",
    })

    save("eliminations.csv", elim_fields, elim_rows)
    save("entrants.csv", ent_fields, ent_rows)
    save("flags.csv", flag_fields, flag_rows)

    print(f"Fixed {elim_fixed} eliminations.csv rows and {ent_fixed} entrants.csv rows.")
    print(f"Logged 1 flag ({new_flag_id}).")


if __name__ == "__main__":
    main()
