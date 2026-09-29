#!/usr/bin/env python3
"""Apply the structured Cain A. Knight timing harvest without guessing."""

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INPUT = ROOT / "scripts" / "research_inputs" / "cain_timing_closeout.json"


def read(name):
    with (DATA / name).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def write(name, fields, rows):
    with (DATA / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def clock(value):
    return f"{value // 60}:{value % 60:02d}"


def append_id(existing, source_id):
    ids = [x for x in (existing or "").split(";") if x]
    if source_id not in ids:
        ids.append(source_id)
    return ";".join(ids)


def main():
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    entrant_fields, entrants = read("entrants.csv")
    entrance_fields, entrances = read("entrances.csv")
    entrance_by_key = {(r["event_id"], r["wrestler_id"]): r for r in entrances}
    changed_ring = changed_entry = changed_exit = 0

    for event_id, timing in data.items():
        source_id = timing["source_id"]
        field = [r for r in entrants if r["event_id"] == event_id]
        by_number = {int(r["entry_number"]): r for r in field if r["entry_number"].isdigit()}
        buzzer_clock = 0
        for position, item in enumerate(timing["buzzer_intervals"], start=3):
            buzzer_clock += int(item["seconds"])
            entrant = by_number.get(position)
            # RR2004's official #21 Test was replaced by Mick Foley after the
            # buzzer; both rows carry the draw number, so select the entrant
            # explicitly named by Cain's timing article.
            if event_id == "RR2004M" and position == 21:
                entrant = next(r for r in field if r["wrestler_id"] == "mick-foley")
            if not entrant:
                continue
            key = (event_id, entrant["wrestler_id"])
            row = entrance_by_key.get(key)
            if row is None:
                row = {field_name: "" for field_name in entrance_fields}
                row.update({"event_id": event_id, "wrestler_id": entrant["wrestler_id"], "entry_number": str(position)})
                entrances.append(row)
                entrance_by_key[key] = row
            delay = timing["entrance_delay"].get(entrant["wrestler_id"])
            row["countdown_ts"] = clock(buzzer_clock)
            if delay is not None and entrant.get("elim_number_status") != "N/A":
                row["entrance_duration_seconds"] = str(delay)
                row["enters_ring_ts"] = clock(buzzer_clock + int(delay))
            row["video_source"] = source_id
            row["reviewer"] = "Cain A. Knight / Cageside Seats"
            row["confidence"] = "HIGH"
            row["human_verified"] = "TRUE"
            changed_entry += 1

        for entrant in field:
            actual = entrant.get("is_winner") == "TRUE" or entrant.get("elim_number_status") != "N/A"
            if not actual:
                continue
            survival = timing["survival"].get(entrant["wrestler_id"])
            if survival is not None and not entrant.get("ring_time_seconds"):
                entrant["ring_time_seconds"] = str(survival)
                entrant["ring_time"] = clock(survival)
                entrant["ring_time_status"] = "PROBABLE"
                entrant["source_ids"] = append_id(entrant.get("source_ids", ""), source_id)
                changed_ring += 1

            entrance = entrance_by_key.get((event_id, entrant["wrestler_id"]), {})
            start_text = entrance.get("enters_ring_ts")
            ring_text = entrant.get("ring_time_seconds")
            if entrant.get("entry_number") in {"1", "2"}:
                start = 0
            elif start_text:
                mins, secs = map(int, start_text.split(":"))
                start = mins * 60 + secs
            else:
                start = None
            if start is not None and ring_text and entrant.get("is_winner") != "TRUE":
                end = start + int(ring_text)
                if not entrant.get("elimination_clock_seconds") or event_id in {"RR1988M", "RR1989M"}:
                    entrant["elimination_clock_seconds"] = str(end)
                    entrant["elimination_clock_time"] = clock(end)
                    entrant["source_ids"] = append_id(entrant.get("source_ids", ""), source_id)
                    changed_exit += 1

    entrances.sort(key=lambda r: (r["event_id"], int(r["entry_number"] or 999), r["wrestler_id"]))
    write("entrants.csv", entrant_fields, entrants)
    write("entrances.csv", entrance_fields, entrances)
    print(f"ring times added: {changed_ring}")
    print(f"entrance rows updated/added: {changed_entry}")
    print(f"elimination clocks derived: {changed_exit}")


if __name__ == "__main__":
    main()
