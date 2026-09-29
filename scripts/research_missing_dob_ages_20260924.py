#!/usr/bin/env python3
"""Resolve the safe remainder of the P0 missing-DOB age tier.

Adds 38 single-source PROBABLE DOBs (reusing registered sources where
possible), then derives 121 appearance ages. Every candidate is checked
against open record-specific DOB flags; known conflicts and identity
ambiguities remain untouched.
"""

from __future__ import annotations

import argparse
import calendar
import csv
from datetime import date
from pathlib import Path


EXPECTED_BASELINE_BLANK_AGES = 143
EXPECTED_WRESTLERS = 38
EXPECTED_ENTRANTS = 121

# wrestler_id: (DOB, source_id)
DOBS = {
    "adam-rose": ("1979-07-20", "S1684"),
    "aj-styles": ("1977-06-02", "S815"),
    "barry-horowitz": ("1960-03-24", "S1685"),
    "beth-phoenix": ("1980-11-24", "S792"),
    "big-e": ("1986-03-01", "S809"),
    "bo-dallas": ("1990-05-25", "S793"),
    "braun-strowman": ("1983-09-06", "S818"),
    "brodus-clay": ("1973-02-21", "S1686"),
    "bubba-ray-dudley": ("1971-07-14", "S810"),
    "cesaro": ("1980-12-27", "S1687"),
    "crash-holly": ("1971-08-25", "S1688"),
    "curtis-axel": ("1979-10-01", "S769"),
    "damien-sandow": ("1982-08-03", "S1519"),
    "darren-young": ("1983-11-02", "S1689"),
    "dean-ambrose": ("1985-12-07", "S1690"),
    "el-torito": ("1982-02-19", "S1691"),
    "erick-rowan": ("1981-11-28", "S808"),
    "evan-bourne": ("1983-03-19", "S1692"),
    "fake-diesel": ("1967-04-26", "S1693"),
    "fake-razor-ramon": ("1970-01-16", "S1694"),
    "fandango": ("1983-07-22", "S805"),
    "hardcore-holly": ("1963-01-29", "S592"),
    "headshrinker-sione": ("1958-09-06", "S1530"),
    "jimmy-uso": ("1985-08-22", "S802"),
    "kevin-owens": ("1984-05-07", "S819"),
    "luke-harper": ("1979-12-16", "S1695"),
    "neville": ("1986-08-22", "S1696"),
    "roman-reigns": ("1985-05-25", "S804"),
    "rusev": ("1985-12-25", "S801"),
    "ryback": ("1981-11-10", "S795"),
    "sami-zayn": ("1984-07-12", "S820"),
    "savio-vega": ("1964-08-10", "S588"),
    "seth-rollins": ("1986-05-28", "S800"),
    "spike-dudley": ("1970-08-13", "S1697"),
    "tatanka": ("1961-06-08", "S571"),
    "the-boogeyman": ("1964-07-15", "S813"),
    "titus-oneil": ("1977-04-29", "S797"),
    "tyler-breeze": ("1988-01-19", "S816"),
}

NEW_SOURCES = [
    ("S1684", "Wikipedia profile: Adam Rose (wrestler)", "reference", "https://en.wikipedia.org/wiki/Adam_Rose_(wrestler)", "10", "Wikipedia/reference", "2026-09-24", "DOB source for Adam Rose; corrected wrestler-specific page rather than the existing disambiguation URL."),
    ("S1685", "Wikipedia profile: Barry Horowitz", "reference", "https://en.wikipedia.org/wiki/Barry_Horowitz", "10", "Wikipedia/reference", "2026-09-24", "DOB source for Barry Horowitz."),
    ("S1686", "Wikipedia profile: Tyrus / Brodus Clay", "reference", "https://en.wikipedia.org/wiki/Tyrus_(wrestler)", "10", "Wikipedia/reference", "2026-09-24", "DOB source for Brodus Clay."),
    ("S1687", "Wikipedia profile: Claudio Castagnoli / Cesaro", "reference", "https://en.wikipedia.org/wiki/Claudio_Castagnoli", "10", "Wikipedia/reference", "2026-09-24", "DOB source for Cesaro."),
    ("S1688", "Wikipedia profile: Crash Holly", "reference", "https://en.wikipedia.org/wiki/Crash_Holly", "10", "Wikipedia/reference", "2026-09-24", "DOB source for Crash Holly; existing birthplace conflict remains open and untouched."),
    ("S1689", "Wikipedia profile: Fred Rosser / Darren Young", "reference", "https://en.wikipedia.org/wiki/Fred_Rosser", "10", "Wikipedia/reference", "2026-09-24", "DOB source for Darren Young."),
    ("S1690", "Wikipedia profile: Jon Moxley / Dean Ambrose", "reference", "https://en.wikipedia.org/wiki/Jon_Moxley", "10", "Wikipedia/reference", "2026-09-24", "DOB source for Dean Ambrose."),
    ("S1691", "Wikipedia profile: Mascarita Dorada / El Torito", "reference", "https://en.wikipedia.org/wiki/Mascarita_Dorada", "10", "Wikipedia/reference", "2026-09-24", "DOB source for El Torito."),
    ("S1692", "Wikipedia profile: Matt Sydal / Evan Bourne", "reference", "https://en.wikipedia.org/wiki/Matt_Sydal", "10", "Wikipedia/reference", "2026-09-24", "DOB source for Evan Bourne."),
    ("S1693", "Wikipedia profile: Kane / Fake Diesel", "reference", "https://en.wikipedia.org/wiki/Kane_(wrestler)", "10", "Wikipedia/reference", "2026-09-24", "DOB source for Glenn Jacobs's Fake Diesel appearance."),
    ("S1694", "Wikipedia profile: Rick Bognar / Fake Razor Ramon", "reference", "https://en.wikipedia.org/wiki/Rick_Bognar", "10", "Wikipedia/reference", "2026-09-24", "DOB source for Fake Razor Ramon."),
    ("S1695", "Wikipedia profile: Brodie Lee / Luke Harper", "reference", "https://en.wikipedia.org/wiki/Brodie_Lee", "10", "Wikipedia/reference", "2026-09-24", "DOB source for Luke Harper."),
    ("S1696", "Wikipedia profile: Pac / Neville", "reference", "https://en.wikipedia.org/wiki/Pac_(wrestler)", "10", "Wikipedia/reference", "2026-09-24", "DOB source for Neville."),
    ("S1697", "Wikipedia profile: Spike Dudley", "reference", "https://en.wikipedia.org/wiki/Spike_Dudley", "10", "Wikipedia/reference", "2026-09-24", "DOB source for Spike Dudley."),
]

BLOCKED = {
    "doink", "doink-1995", "eight-ball", "elijah-burke", "haku",
    "michael-cole", "sabu", "santino-marella", "scott-taylor", "skull",
    "virgil", "vladimir-kozlov",
}


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def exact_age(dob: date, event_date: date) -> str:
    years = event_date.year - dob.year
    months = event_date.month - dob.month
    days = event_date.day - dob.day
    if days < 0:
        months -= 1
        previous_month = event_date.month - 1 or 12
        previous_year = event_date.year if event_date.month > 1 else event_date.year - 1
        days += calendar.monthrange(previous_year, previous_month)[1]
    if months < 0:
        years -= 1
        months += 12
    return f"{years} Years, {months} Months, {days} Days"


def add_source_id(existing: str, source_id: str) -> str:
    ids = [item for item in existing.split(";") if item]
    if source_id not in ids:
        ids.append(source_id)
    return ";".join(ids)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()

    entrants, entrant_fields = read_csv(args.data_dir / "entrants.csv")
    wrestlers, wrestler_fields = read_csv(args.data_dir / "wrestlers.csv")
    events, _ = read_csv(args.data_dir / "events.csv")
    sources, source_fields = read_csv(args.data_dir / "sources.csv")
    flags, _ = read_csv(args.data_dir / "flags.csv")

    if sum(not row.get("age_at_event", "").strip() for row in entrants) != EXPECTED_BASELINE_BLANK_AGES:
        raise SystemExit("Refusing to edit: expected the verified Version 33 baseline with 143 blank ages.")
    if len(DOBS) != EXPECTED_WRESTLERS:
        raise SystemExit("Internal DOB mapping count changed unexpectedly.")
    if max(int(row["source_id"][1:]) for row in sources if row.get("source_id", "").startswith("S")) != 1683:
        raise SystemExit("Refusing to edit: source registry has drifted from expected max S1683.")

    # Guard the derivation inputs against unresolved record-specific DOB disputes.
    for flag in flags:
        if flag.get("status", "").lower() == "resolved" or "dob" not in flag.get("field", "").lower():
            continue
        record_ids = {item.strip() for item in flag.get("record_id", "").split(";")}
        overlap = record_ids & set(DOBS)
        if overlap and flag.get("issue_type") in {"conflicting_sources", "needs_human_judgement"}:
            raise SystemExit(f"Open DOB dispute {flag['flag_id']} blocks: {sorted(overlap)}")

    existing_source_ids = {row["source_id"] for row in sources}
    if existing_source_ids & {row[0] for row in NEW_SOURCES}:
        raise SystemExit("One or more planned source IDs already exist.")
    for values in NEW_SOURCES:
        sources.append(dict(zip(source_fields, values)))

    wrestler_by_id = {row["wrestler_id"]: row for row in wrestlers}
    event_by_id = {row["event_id"]: row for row in events}
    for wrestler_id, (dob, source_id) in DOBS.items():
        row = wrestler_by_id[wrestler_id]
        if row.get("dob", "").strip():
            raise SystemExit(f"Refusing to overwrite existing DOB for {wrestler_id}")
        row["dob"] = dob
        row["dob_status"] = "PROBABLE"
        row["source_ids"] = add_source_id(row.get("source_ids", ""), source_id)

    manifest: list[dict[str, str]] = []
    for entrant in entrants:
        wrestler_id = entrant["wrestler_id"]
        if wrestler_id not in DOBS or entrant.get("age_at_event", "").strip():
            continue
        dob, source_id = DOBS[wrestler_id]
        value = exact_age(date.fromisoformat(dob), date.fromisoformat(event_by_id[entrant["event_id"]]["event_date"]))
        entrant["age_at_event"] = value
        entrant["age_status"] = "DERIVED"
        entrant["source_ids"] = add_source_id(entrant.get("source_ids", ""), source_id)
        manifest.append({
            "event_id": entrant["event_id"], "wrestler_id": wrestler_id,
            "dob": dob, "dob_status": "PROBABLE", "dob_source_id": source_id,
            "event_date": event_by_id[entrant["event_id"]]["event_date"],
            "age_at_event": value, "age_status": "DERIVED",
        })

    if len(manifest) != EXPECTED_ENTRANTS:
        raise SystemExit(f"Expected {EXPECTED_ENTRANTS} entrant ages, built {len(manifest)}")
    remaining = {row["wrestler_id"] for row in entrants if not row.get("age_at_event", "").strip()}
    if remaining != BLOCKED:
        raise SystemExit(f"Unexpected remaining cohort: {sorted(remaining ^ BLOCKED)}")

    write_csv(args.data_dir / "entrants.csv", entrants, entrant_fields)
    write_csv(args.data_dir / "wrestlers.csv", wrestlers, wrestler_fields)
    write_csv(args.data_dir / "sources.csv", sources, source_fields)
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        write_csv(args.manifest, manifest, [
            "event_id", "wrestler_id", "dob", "dob_status", "dob_source_id",
            "event_date", "age_at_event", "age_status",
        ])
    print(f"Added {len(DOBS)} DOBs, {len(NEW_SOURCES)} sources, and derived {len(manifest)} ages.")


if __name__ == "__main__":
    main()
