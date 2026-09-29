"""Add sourced cross-promotion ring identities to existing wrestler rows."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "wrestlers.csv"

UPDATES = {
    "adam-bomb": {"aliases": ["Wrath", "Bryan Clark", "The Nightstalker"], "sources": ["S2128"]},
    "aldo-montoya": {"aliases": ["Justin Credible", "P. J. Polaco"], "sources": ["S610"]},
    "bill-demott": {"aliases": ["Hugh Morrus", "General Rection", "Gen. Rection"], "sources": ["S698"]},
    "kharma": {"aliases": ["Awesome Kong", "Amazing Kong"], "sources": ["S788"]},
    "sid-justice": {"aliases": ["Sid Vicious", "Sycho Sid"], "sources": ["S562"]},
    "tugboat": {"aliases": ["Typhoon", "The Shockmaster"], "sources": ["S550"]},
    "kenny-dykstra": {"aliases": ["Kenny", "Ken Doane"], "sources": ["S742"]},
    "irwin-r-schyster": {"aliases": ["Mike Rotunda", "Mike Rotundo", "Michael Wallstreet"], "sources": ["S555"]},
    "kwang": {
        "real_name": "Juan Rivera", "real_name_status": "PROBABLE",
        "aliases": ["Savio Vega", "TNT"], "sources": ["S588"],
    },
    "savio-vega": {
        "real_name": "Juan Rivera", "real_name_status": "PROBABLE",
        "aliases": ["Kwang", "TNT"], "sources": ["S588"],
    },
    "brodus-clay": {
        "real_name": "George Timothy Murdoch", "real_name_status": "PROBABLE",
        "aliases": ["Tyrus", "G-Rilla"], "sources": ["S1686"],
    },
    "chris-masters": {"aliases": ["Chris Adonis"], "sources": ["S738"]},
    "elijah-burke": {"aliases": ["D'Angelo Dinero", "Da Pope"], "sources": ["S755"]},
    "flash-funk": {"aliases": ["2 Cold Scorpio", "Scorpio"], "sources": ["S643"]},
    "golga": {
        "real_name": "John Anthony Tenta Jr.", "real_name_status": "PROBABLE",
        "aliases": ["Earthquake", "John Tenta"], "sources": ["S654"],
    },
    "headshrinker-sione": {
        "real_name": "Sione Havea Vailahi", "real_name_status": "PROBABLE",
        "aliases": ["The Barbarian", "Barbarian"], "sources": ["S604"],
    },
    "saba-simba": {
        "real_name": "Anthony White", "real_name_status": "PROBABLE",
        "aliases": ["Tony Atlas"], "sources": ["S542"],
    },
    "simon-dean": {
        "real_name": "Michael Bucci", "real_name_status": "PROBABLE",
        "aliases": ["Nova", "Super Nova", "Hollywood Nova", "Mike Bucci"], "sources": ["S724"],
    },
    "skinner": {
        "real_name": "Stephen Paul Keirn", "real_name_status": "PROBABLE",
        "aliases": ["Steve Keirn"], "sources": ["S2133"],
    },
    "the-berzerker": {"aliases": ["John Nord"], "sources": ["S556"]},
    "tom-prichard": {"aliases": ["Zip", "Dr. Tom Prichard"], "sources": ["S605"]},
    "eight-ball": {
        "real_name": "Ronald Harris", "real_name_status": "PROBABLE",
        "aliases": ["Ron Harris", "Gerald", "Eli Blu", "Ron Bruise"], "sources": ["S601"],
    },
    "eli-blu": {
        "real_name": "Ronald Harris", "real_name_status": "PROBABLE",
        "aliases": ["Ron Harris", "Gerald", "Eight-Ball", "Ron Bruise"], "sources": ["S601"],
    },
    "jacob-blu": {
        "real_name": "Donald Harris", "real_name_status": "PROBABLE",
        "aliases": ["Don Harris", "Patrick", "Skull", "Don Bruise"], "sources": ["S601"],
    },
    "skull": {
        "real_name": "Donald Harris", "real_name_status": "PROBABLE",
        "aliases": ["Don Harris", "Jacob Blu", "Patrick", "Don Bruise"], "sources": ["S601"],
    },
    "kama": {
        "real_name": "Charles Wright", "real_name_status": "PROBABLE",
        "aliases": ["The Godfather", "The Goodfather", "Papa Shango"], "sources": ["S565"],
    },
    "papa-shango": {
        "real_name": "Charles Wright", "real_name_status": "PROBABLE",
        "aliases": ["The Godfather", "The Goodfather", "Kama"], "sources": ["S565"],
    },
    "the-godfather": {
        "real_name": "Charles Wright", "real_name_status": "PROBABLE",
        "aliases": ["The Goodfather", "Papa Shango", "Kama"], "sources": ["S565"],
    },
    "hakushi": {
        "real_name": "Kensuke Shinzaki", "real_name_status": "PROBABLE",
        "aliases": ["Jinsei Shinzaki"], "sources": ["S618"],
    },
    "max-moon": {
        "real_name": "Thomas Boric", "real_name_status": "PROBABLE",
        "aliases": ["Paul Diamond", "Kato"], "sources": ["S2134"],
    },
    "adam-rose": {"aliases": ["Leo Kruger"], "sources": ["S814"]},
    "big-cass": {"aliases": ["Big Bill", "W. Morrissey", "Colin Cassady"], "sources": ["S821"]},
    "bastion-booger": {"aliases": ["Mike Shaw", "Norman the Lunatic", "Makhan Singh"], "sources": ["S600"]},
    "fake-razor-ramon": {"aliases": ["Big Titan", "Rick Titan"], "sources": ["S1694"]},
    "headhunter-1": {"aliases": ["Headhunter A", "Mofat"], "sources": ["S625"]},
    "headhunter-2": {"aliases": ["Headhunter B", "Mahim"], "sources": ["S625"]},
}


def append_unique(existing: str, values: list[str]) -> str:
    items = [x.strip() for x in (existing or "").split(";") if x.strip()]
    seen = {x.casefold() for x in items}
    for value in values:
        if value.casefold() not in seen:
            items.append(value)
            seen.add(value.casefold())
    return "; ".join(items)


def main() -> None:
    with PATH.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    by_id = {row["wrestler_id"]: row for row in rows}
    missing = sorted(set(UPDATES) - set(by_id))
    if missing:
        raise RuntimeError(f"Missing expected wrestler IDs: {missing}")
    changed = 0
    for wrestler_id, update in UPDATES.items():
        row = by_id[wrestler_id]
        before = dict(row)
        if update.get("real_name"):
            row["real_name"] = update["real_name"]
            row["real_name_status"] = update["real_name_status"]
        row["aliases_ring_names"] = append_unique(row.get("aliases_ring_names", ""), update["aliases"])
        row["source_ids"] = append_unique(row.get("source_ids", ""), update["sources"])
        if row != before:
            changed += 1
    with PATH.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Updated {changed} wrestler identity rows.")


if __name__ == "__main__":
    main()
