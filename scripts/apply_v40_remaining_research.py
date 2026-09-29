#!/usr/bin/env python3
"""Apply the final, conservatively verified V40 research tranche."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TODAY = "2026-09-25"


def read_csv(name):
    with (DATA / name).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def write_csv(name, fields, rows):
    with (DATA / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def append_id(existing, value):
    values = [v for v in (existing or "").split(";") if v]
    if value not in values:
        values.append(value)
    return ";".join(values)


def add_source(rows, *, name, url, source_type="reference", tier="10", label="Wikipedia/reference", notes=""):
    for row in rows:
        if row["url"] == url:
            return row["source_id"]
    highest = max(int(r["source_id"][1:]) for r in rows if re.fullmatch(r"S\d+", r["source_id"]))
    sid = f"S{highest + 1:03d}"
    rows.append({
        "source_id": sid, "source_name": name, "source_type": source_type, "url": url,
        "reliability_tier": tier, "tier_label": label, "accessed_date": TODAY, "notes": notes,
    })
    return sid


def add_flag(rows, *, entity_id, fields, issue_type, description, source_ids):
    highest = max(int(r["flag_id"][1:]) for r in rows if re.fullmatch(r"F\d+", r["flag_id"]))
    rows.append({
        "flag_id": f"F{highest + 1:03d}", "event_id": "", "table": "entrants",
        "record_id": entity_id, "field": fields, "issue_type": issue_type,
        "description": description, "source_ids_involved": source_ids, "status": "open", "date_logged": TODAY,
    })


def main():
    entrant_fields, entrants = read_csv("entrants.csv")
    wrestler_fields, wrestlers = read_csv("wrestlers.csv")
    family_fields, families = read_csv("families.csv")
    source_fields, sources = read_csv("sources.csv")
    flag_fields, flags = read_csv("flags.csv")

    # Exact-identity Wikidata death dates and exact/same-performer Wikipedia HOF entries.
    death_data = {
        "harley-race": ("2019-08-01", "Q314517"), "ron-bass": ("2017-03-07", "Q7364921"),
        "sapphire": ("1996-09-10", "Q7421016"), "sid-justice": ("2024-08-26", "Q714630"),
        "giant-gonzalez": ("2010-09-22", "Q547033"), "mo": ("2025-10-19", "Q6890157"),
        "timothy-well": ("2017-01-09", "Q7808463"), "steven-dunn": ("2009-03-22", "Q7613351"),
        "viscera": ("2014-02-18", "Q726556"), "umaga": ("2009-12-04", "Q449927"),
    }
    hof_data = {
        "rick-rude": ("2017", "https://en.wikipedia.org/wiki/Rick_Rude"),
        "the-honky-tonk-man": ("2019", "https://en.wikipedia.org/wiki/The_Honky_Tonk_Man"),
        "sgt-slaughter": ("2004", "https://en.wikipedia.org/wiki/Sgt._Slaughter"),
        "sid-justice": ("2026", "https://en.wikipedia.org/wiki/Sid_Eudy"),
        "jeff-jarrett": ("2018", "https://en.wikipedia.org/wiki/Jeff_Jarrett"),
        "lex-luger": ("2025", "https://en.wikipedia.org/wiki/Lex_Luger"),
        "mil-mascaras": ("2012", "https://en.wikipedia.org/wiki/Mil_M%C3%A1scaras"),
        "x-pac": ("2019", "https://en.wikipedia.org/wiki/Sean_Waltman"),
        "drew-carey": ("2011", "https://en.wikipedia.org/wiki/Drew_Carey"),
        "road-dogg": ("2019", "https://en.wikipedia.org/wiki/Road_Dogg"),
        "ivory": ("2018", "https://en.wikipedia.org/wiki/Ivory_(wrestler)"),
        "fatu": ("2015", "https://en.wikipedia.org/wiki/Rikishi_(wrestler)"),
        "the-sultan": ("2015", "https://en.wikipedia.org/wiki/Rikishi_(wrestler)"),
        "papa-shango": ("2016", "https://en.wikipedia.org/wiki/The_Godfather_(wrestler)"),
        "kama": ("2016", "https://en.wikipedia.org/wiki/The_Godfather_(wrestler)"),
        "cactus-jack": ("2013", "https://en.wikipedia.org/wiki/Mick_Foley"),
        "dude-love": ("2013", "https://en.wikipedia.org/wiki/Mick_Foley"),
        "isaac-yankem": ("2021", "https://en.wikipedia.org/wiki/Kane_(wrestler)"),
        "fake-diesel": ("2021", "https://en.wikipedia.org/wiki/Kane_(wrestler)"),
        "chainz": ("2020", "https://en.wikipedia.org/wiki/John_Layfield"),
    }
    source_cache = {}
    for row in wrestlers:
        wid = row["wrestler_id"]
        if wid in death_data:
            value, qid = death_data[wid]
            url = f"https://www.wikidata.org/wiki/{qid}"
            sid = source_cache.setdefault(url, add_source(
                sources, name=f"{row['ring_name']} — Wikidata", url=url, source_type="database",
                tier="9", label="Structured reference", notes="Exact-identity entity; used for deceased date.",
            ))
            row["deceased_date"], row["deceased_date_status"] = value, "PROBABLE"
            row["source_ids"] = append_id(row["source_ids"], sid)
        if wid in hof_data:
            value, url = hof_data[wid]
            sid = source_cache.setdefault(url, add_source(
                sources, name=f"{row['ring_name']} — Wikipedia", url=url,
                notes="Exact performer or documented prior persona; used for WWE Hall of Fame induction year.",
            ))
            row["hall_of_fame_year"], row["hall_of_fame_year_status"] = value, "PROBABLE"
            row["source_ids"] = append_id(row["source_ids"], sid)

    # Finish the per-appearance masked field. FALSE means the entrant did not wrestle masked in that match.
    always_masked = {
        "aldo-montoya", "doink", "doink-1995", "dragon-lee", "el-grande-americano-i",
        "el-grande-americano-ii", "el-torito", "golga", "hunico", "kalisto", "la-parka-iii",
        "mankind", "penta", "rey-fenix", "rey-mysterio", "the-sultan",
    }
    for row in entrants:
        masked = row["wrestler_id"] in always_masked
        if row["wrestler_id"] == "the-hurricane":
            masked = row["ring_name_at_time"] in {"The Hurricane", "Hurricane Helms"}
        if row["wrestler_id"] == "molly-holly":
            masked = row["ring_name_at_time"] == "Mighty Molly"
        if row["wrestler_id"] == "kane":
            year = int(row["event_id"][2:6])
            masked = year <= 2003 or year >= 2013
        row["wrestled_masked"] = "TRUE" if masked else "FALSE"

    # Residual women's billed-weight research.
    weight_sources = {
        "rox_wp": add_source(sources, name="Roxanne Perez — Wrestling Profiles", url="https://wrestlingprofiles.com/wrestler/roxanne-perez/", source_type="profile", tier="7", label="Secondary profile", notes="Lists billed weight as 115 lb."),
        "rox_aa": add_source(sources, name="Roxanne Perez — AthleteAgent", url="https://www.athleteagent.com/athletes/roxanne-perez/vitals", source_type="profile", tier="7", label="Secondary profile", notes="Lists weight as 115 lb."),
        "zel_sdh": add_source(sources, name="Zelina Vega — The SmackDown Hotel", url="https://www.thesmackdownhotel.com/wrestlers/zelina-vega-rosita", source_type="database", tier="8", label="Wrestling database", notes="Lists weight as 106 lb / 48 kg."),
        "zel_topps": add_source(sources, name="Zelina Vega — Topps Ripped WWE profile", url="https://ripped.topps.com/profile/wwe/zelina-vega/", source_type="profile", tier="8", label="Licensed profile", notes="Lists weight as 106 lb / 48 kg."),
        "zel_oww": add_source(sources, name="Zelina Vega — Online World of Wrestling", url="https://www.onlineworldofwrestling.com/profile/rosita/", source_type="database", tier="7", label="Wrestling database", notes="Lists weight as 107 lb, conflicting by one pound with two other profiles."),
    }
    for row in entrants:
        if row["wrestler_id"] == "roxanne-perez" and not row["billed_weight_kg_at_event"]:
            row["billed_weight_kg_at_event"] = "52"
            row["physical_status"] = "CONFIRMED"
            row["source_ids"] = append_id(append_id(row["source_ids"], weight_sources["rox_wp"]), weight_sources["rox_aa"])
        elif row["wrestler_id"] == "zelina-vega" and not row["billed_weight_kg_at_event"]:
            row["billed_weight_kg_at_event"] = "48"
            row["physical_status"] = "PROBABLE"
            for key in ("zel_sdh", "zel_topps", "zel_oww"):
                row["source_ids"] = append_id(row["source_ids"], weight_sources[key])
    if not any(r["record_id"] == "zelina-vega" and r["field"] == "billed_weight_kg_at_event" for r in flags):
        add_flag(flags, entity_id="zelina-vega", fields="billed_weight_kg_at_event", issue_type="conflicting_sources",
                 description="Two profiles list 106 lb / 48 kg while Online World of Wrestling lists 107 lb. The two-source 48 kg value is retained as PROBABLE pending event-era confirmation; disagreement preserved here.",
                 source_ids=";".join(weight_sources[k] for k in ("zel_sdh", "zel_topps", "zel_oww")))

    # Relevant Royal Rumble family units. Persona IDs are retained so every entrant row can join.
    family_specs = [
        ("FAM001", "Anoaʻi family", "tama;yokozuna;fatu;samu;the-sultan;rocky-maivia;rikishi;jamal;rosey;umaga;jey-uso;jimmy-uso;roman-reigns;nia-jax;jacob-fatu;solo-sikoa;naomi", "extended family and marriage", "https://en.wikipedia.org/wiki/Anoa%CA%BBi_family"),
        ("FAM002", "Hart family", "bret-hart;owen-hart;jim-neidhart;british-bulldog;natalya;tyson-kidd", "extended family and marriage", "https://en.wikipedia.org/wiki/Hart_wrestling_family"),
        ("FAM003", "Rhodes family", "dusty-rhodes;dustin-rhodes;goldust;cody-rhodes", "parent, children and persona identity", "https://en.wikipedia.org/wiki/Rhodes_wrestling_family"),
        ("FAM004", "DiBiase family", "ted-dibiase;ted-dibiase-jr", "father and son", "https://en.wikipedia.org/wiki/Ted_DiBiase_Jr."),
        ("FAM005", "Guerrero family", "eddie-guerrero;chavo-guerrero;vickie-guerrero", "extended family and marriage", "https://en.wikipedia.org/wiki/Guerrero_family"),
        ("FAM006", "Rotunda-Windham family", "irwin-r-schyster;husky-harris;bray-wyatt;bo-dallas", "father, sons and persona identity", "https://en.wikipedia.org/wiki/Windham_family"),
        ("FAM007", "Bella family", "nikki-bella;brie-bella;daniel-bryan", "twin sisters and marriage", "https://en.wikipedia.org/wiki/The_Bella_Twins"),
        ("FAM008", "Steiner family", "rick-steiner;scott-steiner;bron-breakker", "brothers and nephew", "https://en.wikipedia.org/wiki/The_Steiner_Brothers"),
        ("FAM009", "Hardy family", "matt-hardy;jeff-hardy", "brothers", "https://en.wikipedia.org/wiki/The_Hardy_Boyz"),
        ("FAM010", "Harris twins", "eli-blu;eight-ball;jacob-blu;skull", "twin brothers and persona identities", "https://en.wikipedia.org/wiki/Harris_Brothers"),
        ("FAM011", "Rougeau family", "jacques-rougeau;raymond-rougeau", "brothers", "https://en.wikipedia.org/wiki/The_Fabulous_Rougeaus"),
        ("FAM012", "Copeland-Copeland family", "edge;beth-phoenix", "married couple", "https://en.wikipedia.org/wiki/Beth_Phoenix"),
        ("FAM013", "Rollins-Lynch family", "seth-rollins;becky-lynch", "married couple", "https://en.wikipedia.org/wiki/Becky_Lynch"),
        ("FAM014", "Crawford-Lopez family", "bianca-belair;montez-ford", "married couple", "https://en.wikipedia.org/wiki/Bianca_Belair"),
        ("FAM015", "Calaway-McCool family", "the-undertaker;michelle-mccool", "married couple", "https://en.wikipedia.org/wiki/Michelle_McCool"),
        ("FAM016", "Budgen-Trinidad family", "aleister-black;zelina-vega", "married couple", "https://en.wikipedia.org/wiki/Zelina_Vega"),
        ("FAM017", "Gargano-Dawson family", "johnny-gargano;candice-lerae", "married couple", "https://en.wikipedia.org/wiki/Candice_LeRae"),
        ("FAM018", "Lee-Yim family", "keith-lee;mia-yim", "married couple", "https://en.wikipedia.org/wiki/Mia_Yim"),
        ("FAM019", "Barnyashev-Perry family", "rusev;lana", "former married couple", "https://en.wikipedia.org/wiki/Lana_(wrestler)"),
    ]
    valid_ids = {r["wrestler_id"] for r in wrestlers}
    families.clear()
    for fid, name, members, relation, url in family_specs:
        missing = set(members.split(";")) - valid_ids
        if missing:
            raise ValueError(f"Unknown family member IDs for {fid}: {sorted(missing)}")
        sid = add_source(sources, name=f"{name} — Wikipedia", url=url, notes="Used to document the named real-life wrestling family or relationship.")
        families.append({"family_id": fid, "family_name": name, "member_wrestler_ids": members,
                         "relationship_type": relation, "notes": "Includes only identities represented in the Royal Rumble database; persona IDs are retained for entrant joins.",
                         "data_quality_status": "PROBABLE", "source_ids": sid})

    write_csv("entrants.csv", entrant_fields, entrants)
    write_csv("wrestlers.csv", wrestler_fields, wrestlers)
    write_csv("families.csv", family_fields, families)
    write_csv("sources.csv", source_fields, sources)
    write_csv("flags.csv", flag_fields, flags)
    print("V40 final research applied")
    print(f"masked complete: {sum(bool(r['wrestled_masked']) for r in entrants)}/{len(entrants)}")
    print(f"families: {len(families)}")


if __name__ == "__main__":
    main()
