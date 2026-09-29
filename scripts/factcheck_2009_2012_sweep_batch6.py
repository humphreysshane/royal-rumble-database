#!/usr/bin/env python3
"""
2009-2012 fact-check sweep, batch 6. Continues the deceased-status and WWE
Hall of Fame audits from batches 4-5 into the next 4 events, plus a
same-performer sibling bio-completion (husky-harris -> bray-wyatt, the same
pattern used for golga/earthquake in batch 3), 3 more Hall of Fame
bio-completions, and 8 more notable_moments.csv rows.

(0) Reconnaissance: like every prior batch, RR2009M-RR2012M already carry
    substantial flags (F229-F266) from this database's original build and
    earlier fact-check passes. Several remaining open flags are genuine
    CONFLICTING_SOURCES disagreements (eliminator-credit disputes, DOB/
    birthplace disputes, attendance/match-time disputes) deliberately left
    untouched this pass, per this project's rule that real disagreements
    between sources stay preserved as flags rather than force-resolved.
    Winner/entrant-count/elimination-count/duration for all 4 events were
    independently spot-checked against historical record and are already
    correctly CONFIRMED in this database -- no fix needed there. Also noted:
    RR2010M carries pre-existing flags (F244/F245) documenting that Shane's
    own reference document has literally no content for that year and no
    per-wrestler timing-graphic source exists for it -- a sourcing gap
    worth flagging for awareness, not something this pass can close.

(1) DECEASED-STATUS AUDIT, same method as batches 1-5: checked all 71
    unique entrants across RR2009M-RR2012M against Wikipedia (S022) and the
    mainstream-obituary bucket (S131). Unlike every prior batch, NONE of the
    71 already had deceased_date set going in. Individually spot-checked the
    lower-profile/higher-perceived-risk names -- Jim Duggan, Jerry Lawler
    (had a well-publicized 2025 stroke; confirmed alive and recovering, NOT
    a deceased-status hit -- explicitly not conflated with a death), Kevin
    Nash/Diesel, Kharma, Tyson Kidd, Curtis Axel/Michael McGillicutty, Mason
    Ryan, Vladimir Kozlov, Chris Masters, Ezekiel Jackson, Tyler Reks (now
    living as Gabbi Tuft -- a gender transition, not a death), Epico/Primo
    Colon, Finlay, William Regal, Road Dogg, Mike Knox, JTG, The Brian
    Kendrick, Shelton Benjamin, Chavo Guerrero, Carlito, and Johnny Nitro --
    and found exactly ONE new death, this batch's headline finding:

      - husky-harris (Windham Lawrence Rotunda) died 2023-08-24, of a heart
        attack in his sleep related to an undisclosed illness (sleep apnea
        exacerbating a pre-existing heart condition) he had been managing
        since February 2023. He had been hospitalized for a heart issue one
        week prior and advised to wear a defibrillator vest, but was not
        wearing it at the time of death. Independently corroborated by CBS
        News, CBS Sports, TVLine, and Cageside Seats in addition to
        Wikipedia -- comfortably clears this database's 2-independent-
        source CONFIRMED bar.

    This database already tracks 'husky-harris' (his 2011 Rumble entrant
    identity) and a separate, out-of-this-batch's-range 'bray-wyatt' id
    (his later Rumble appearance) as two rows, per this project's
    gimmick-era-split convention (same pattern as golga/earthquake and
    jamal/umaga). husky-harris's own notes already state "Later became
    Bray Wyatt," and bray-wyatt's real_name/dob/deceased_date were all
    blank. Following the exact precedent set by batch 3's golga/earthquake
    fix, filled in bray-wyatt's real_name, dob and deceased_date from
    husky-harris's own already-sourced row -- NOT a wrestler_id merge, just
    completing the real-person facts on both sibling rows. Because
    husky-harris's own real_name/dob/birthplace are themselves only
    PROBABLE (single-sourced, Wikipedia only) rather than CONFIRMED, the
    copied fields on bray-wyatt are recorded at the same PROBABLE level --
    not artificially upgraded just because the sibling link is solid.

(2) WWE HALL OF FAME bio-completion, continuing batches 4-5's audit type.
    Reused the same reusable HOF-bucket sources (S123, S124). Added:
      - Edge: 2012 (individual induction, following his 2011 forced
        retirement; he later un-retired in 2020 and wrestled through
        2024/2025, but was not re-inducted -- the 2012 date stands)
      - Beth Phoenix: 2017 (individual induction)
      - diesel (Kevin Nash's Diesel-gimmick id): 2015 -- Nash was inducted
        that year under his own name, "Kevin Nash," not "Diesel"; recorded
        on this database's 'diesel' wrestler_id row per the same
        gimmick-era-split convention used throughout this project (the
        induction is of the person, and this is the row tracking that
        person's RR2011M entrant appearance). He also has a separate 2020
        group induction as part of the nWo, not modeled here since this
        field tracks individual inductions per batch 4/5 convention.
    Checked and found NOT yet inducted, left unchanged: William Regal,
    Road Dogg (group-only DX induction, 2019 -- doesn't count per this
    field's individual-induction convention), MVP, Goldust, Matt Hardy.

(3) 8 new notable_moments.csv rows, again mostly surfaced from this
    database's own already-CONFIRMED events.csv historical_significance
    text and existing flags:
      - RR2009M: Santino Marella's 0:02 survival time, the shortest in
        Royal Rumble history, breaking The Warlord's 1989 mark.
      - RR2010M: Edge's 7:19 ring time, the shortest ever by a Royal
        Rumble winner -- a record that stood until 2022.
      - RR2010M: Beth Phoenix becoming only the second woman ever to
        compete in a standard 30-man Royal Rumble, after Chyna.
      - RR2011M: the first-ever 40-man Royal Rumble match.
      - RR2012M: the entire WWE commentary team (Cole, Lawler, Booker T)
        entering the match as competitors.
      - RR2012M: Kofi Kingston's widely-remembered walking-handstand
        escape to save himself from elimination.
      - RR2012M: The Miz's non-entrant interference elimination of John
        Cena (surfaced from F262).
      - RR2012M: Big Show's two unusual eliminations landed before his own
        official entry, during his entrance walk (surfaced from F241) --
        single-sourced (S084) this pass, logged PROBABLE not CONFIRMED.

Usage:
    python3 factcheck_2009_2012_sweep_batch6.py [data_dir]   (default: data)
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import NOTABLE_MOMENTS_FIELDS

DATA_DIR = sys.argv[1] if len(sys.argv) > 1 else "data"


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
    w_fields, w_rows = load("wrestlers.csv")
    flag_fields, flags = load("flags.csv")
    try:
        nm_fields, nm_rows = load("notable_moments.csv")
    except FileNotFoundError:
        nm_fields, nm_rows = NOTABLE_MOMENTS_FIELDS, []

    by_id = {r["wrestler_id"]: r for r in w_rows}

    def add_src(row, *ids):
        cur = set(filter(None, row["source_ids"].split(";")))
        cur.update(ids)
        row["source_ids"] = ";".join(sorted(cur))

    # ---- (1) deceased-status audit: husky-harris + bray-wyatt sibling ----
    husky = by_id["husky-harris"]
    husky["deceased_date"] = "2023-08-24"
    husky["notes"] = (
        husky["notes"] + " Died 2023-08-24 (heart attack in his sleep, related to an "
        "undisclosed illness -- a pre-existing heart condition exacerbated by sleep "
        "apnea -- he had been managing since February 2023; hospitalized for a heart "
        "issue one week prior and advised to wear a defibrillator vest, but was not "
        "wearing it at the time of death. Confirmed independently by CBS News, CBS "
        "Sports, TVLine, and Cageside Seats in addition to Wikipedia."
    )
    add_src(husky, "S022", "S131")

    wyatt = by_id["bray-wyatt"]
    wyatt["real_name"] = "Windham Lawrence Rotunda"
    wyatt["real_name_status"] = "PROBABLE"
    wyatt["dob"] = "1987-05-23"
    wyatt["dob_status"] = "PROBABLE"
    wyatt["deceased_date"] = "2023-08-24"
    wyatt["notes"] = (
        wyatt["notes"] + " Same performer as this database's husky-harris entrant "
        "(RR2011M, New Nexus stable) -- both rows independently state the 'Later "
        "became Bray Wyatt' / Windham Rotunda identity link. Real name, dob and "
        "deceased_date (2023-08-24) filled in here from husky-harris's own "
        "already-sourced row rather than newly researched, following this "
        "database's gimmick-era-split convention (ids kept separate, bios "
        "cross-completed) -- the same pattern used for golga/earthquake in batch "
        "3. Recorded at PROBABLE, matching husky-harris's own single-sourced "
        "confidence level, not upgraded just because the sibling link is solid."
    )
    add_src(wyatt, "S022", "S131")

    # ---- (2) WWE Hall of Fame bio-completion pass ------------------------
    hof_fixed = []
    hof_years = {
        "edge": "2012",
        "beth-phoenix": "2017",
        "diesel": "2015",
    }
    for wid, year in hof_years.items():
        row = by_id[wid]
        row["hall_of_fame_year"] = year
        add_src(row, "S123", "S124")
        hof_fixed.append(wid)

    assert len(hof_fixed) == 3

    counter = 354
    flags.append({
        "flag_id": f"F{counter:03d}",
        "event_id": "",
        "table": "wrestlers",
        "record_id": "husky-harris;bray-wyatt",
        "field": "deceased_date",
        "issue_type": "corrected",
        "description": (
            "2009-2012 fact-check sweep batch 6, continuing the deceased-status audit from batches "
            "1-5: all 71 unique RR2009M-RR2012M entrants checked -- unlike every prior batch, NONE "
            "already had deceased_date set going in. Individually spot-checked the lower-profile/"
            "higher-perceived-risk names (Jim Duggan, Jerry Lawler -- a 2025 stroke, confirmed alive "
            "and recovering, not a death -- Kevin Nash/Diesel, Kharma, Tyson Kidd, Curtis Axel, Mason "
            "Ryan, Vladimir Kozlov, Chris Masters, Ezekiel Jackson, Tyler Reks, Epico/Primo, Finlay, "
            "William Regal, Road Dogg, Mike Knox, JTG, The Brian Kendrick, Shelton Benjamin, Chavo "
            "Guerrero, Carlito, and Johnny Nitro) and found exactly one new death: husky-harris "
            "(Windham Lawrence Rotunda), died 2023-08-24 of a heart attack in his sleep related to an "
            "undisclosed heart condition, independently corroborated by CBS News, CBS Sports, TVLine "
            "and Cageside Seats in addition to Wikipedia. Also completed a same-real-person bio gap "
            "using this database's own already-sourced sibling data, the same pattern used for golga/"
            "earthquake in batch 3: bray-wyatt's real_name/dob/deceased_date filled in from "
            "husky-harris's own row (both rows already independently state the identity link), at "
            "PROBABLE -- matching husky-harris's own single-sourced confidence rather than an "
            "upgrade. The two ids remain separate rows per this database's gimmick-era convention."
        ),
        "source_ids_involved": "S022;S131",
        "status": "resolved",
        "date_logged": "2026-09-20",
    })
    counter += 1

    flags.append({
        "flag_id": f"F{counter:03d}",
        "event_id": "",
        "table": "wrestlers",
        "record_id": ";".join(hof_fixed),
        "field": "hall_of_fame_year",
        "issue_type": "corrected",
        "description": (
            "2009-2012 fact-check sweep batch 6, continuing the WWE Hall of Fame bio-completion audit "
            "started in batch 4: Edge (2012, individual induction following his 2011 forced "
            "retirement), Beth Phoenix (2017), and Kevin Nash (2015, individually inducted under his "
            "own name rather than 'Diesel' -- recorded on this database's 'diesel' wrestler_id row per "
            "the project's gimmick-era-split convention; he also has a separate, not-modeled-here 2020 "
            "group induction as part of the nWo). All previously blank hall_of_fame_year fields, "
            "confirmed via this database's existing reusable HOF-bucket sources (S123, S124). Checked "
            "and found NOT yet inducted, left unchanged: William Regal, Road Dogg (group-only DX "
            "induction, 2019 -- doesn't satisfy this field's individual-induction convention), MVP, "
            "Goldust, and Matt Hardy."
        ),
        "source_ids_involved": "S123;S124",
        "status": "resolved",
        "date_logged": "2026-09-20",
    })
    counter += 1

    # ---- (3) notable_moments additions -----------------------------------
    nm_rows.append({
        "moment_id": "NM026",
        "event_id": "RR2009M",
        "wrestler_ids_involved": "santino-marella",
        "category": "record",
        "title": "Santino Marella's 0:02 survival time -- the shortest in Royal Rumble history",
        "description": (
            "Santino Marella was eliminated just 2 seconds after entering, setting a new record for "
            "shortest survival time in Royal Rumble history and breaking The Warlord's mark from 1989."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S082;S097",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text.",
    })
    nm_rows.append({
        "moment_id": "NM027",
        "event_id": "RR2010M",
        "wrestler_ids_involved": "edge",
        "category": "record",
        "title": "Edge's 7:19 ring time -- the shortest ever by a Royal Rumble winner",
        "description": (
            "Edge entered as a surprise #29 entrant, returning from a torn Achilles tendon suffered "
            "mid-2009, and won after just 7 minutes 19 seconds in the match -- a record for shortest "
            "time spent in the match by an eventual winner, which stood until Brock Lesnar broke it "
            "in 2022."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S086;S089",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text.",
    })
    nm_rows.append({
        "moment_id": "NM028",
        "event_id": "RR2010M",
        "wrestler_ids_involved": "beth-phoenix;the-great-khali;cm-punk",
        "category": "milestone_first",
        "title": "Beth Phoenix becomes only the second woman ever to compete in a standard 30-man Royal Rumble",
        "description": (
            "Beth Phoenix became just the second woman to compete in a standard 30-man Royal Rumble "
            "match, after Chyna (1999 and 2000). She eliminated The Great Khali by distracting him "
            "with a kiss before being eliminated herself by CM Punk."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S085;S086",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text.",
    })
    nm_rows.append({
        "moment_id": "NM029",
        "event_id": "RR2011M",
        "wrestler_ids_involved": "",
        "category": "milestone_first",
        "title": "The first-ever 40-man Royal Rumble match",
        "description": (
            "RR2011M was the first-ever 40-man Royal Rumble match -- every prior year from 1988-2010 "
            "had used the standard 30-man field. Billed going in as 'the biggest Royal Rumble match "
            "in history.'"
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S083;S097",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text.",
    })
    nm_rows.append({
        "moment_id": "NM030",
        "event_id": "RR2012M",
        "wrestler_ids_involved": "michael-cole;jerry-lawler;booker-t",
        "category": "other",
        "title": "The entire WWE commentary team entered the match as competitors",
        "description": (
            "RR2012M notably featured the entire WWE commentary team -- Michael Cole, Jerry Lawler, "
            "and Booker T -- entering the match as competitors, a gimmick not repeated in most other "
            "years."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S084;S097",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text.",
    })
    nm_rows.append({
        "moment_id": "NM031",
        "event_id": "RR2012M",
        "wrestler_ids_involved": "kofi-kingston",
        "category": "other",
        "title": "Kofi Kingston's walking-handstand escape",
        "description": (
            "Kofi Kingston pulled off a widely remembered walking-handstand escape to save himself "
            "from elimination, going on to survive an additional 7 minutes 45 seconds afterward."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S084;S097",
        "notes": "Surfaced from this event's own already-CONFIRMED historical_significance text.",
    })
    nm_rows.append({
        "moment_id": "NM032",
        "event_id": "RR2012M",
        "wrestler_ids_involved": "john-cena;the-miz",
        "category": "controversy",
        "title": "The Miz's non-entrant interference elimination of John Cena",
        "description": (
            "John Cena's eliminator, The Miz, was not an entrant in this Royal Rumble match at all -- "
            "Miz ran in from outside, with Alex Riley's distraction, while defending the WWE "
            "Championship elsewhere on the same card. An unusual non-participant interference "
            "elimination, agreed on by 2 independent sources."
        ),
        "data_quality_status": "CONFIRMED",
        "source_ids": "S059;S097",
        "notes": "Surfaced from flags.csv F262 rather than newly researched.",
    })
    nm_rows.append({
        "moment_id": "NM033",
        "event_id": "RR2012M",
        "wrestler_ids_involved": "big-show;jack-swagger;the-miz;cody-rhodes",
        "category": "other",
        "title": "Big Show eliminated two pairs of wrestlers before his own official entry",
        "description": (
            "Big Show's eliminations of Jack Swagger, and of the Miz and Cody Rhodes together, both "
            "occurred before his own entry_actual time (46:32) -- during his roughly 1:47 entrance "
            "walk, interfering from ringside before formally entering the ring. Directly narrated by "
            "a single source (S084, Shane's own frame-by-frame timing analysis) and modeled as-is; "
            "not independently cross-checked this pass, so logged here at PROBABLE rather than "
            "CONFIRMED."
        ),
        "data_quality_status": "PROBABLE",
        "source_ids": "S084",
        "notes": "Surfaced from flags.csv F241 rather than newly researched.",
    })
    flags.append({
        "flag_id": f"F{counter:03d}",
        "event_id": "RR2009M;RR2010M;RR2011M;RR2012M",
        "table": "notable_moments",
        "record_id": "NM026;NM027;NM028;NM029;NM030;NM031;NM032;NM033",
        "field": "n/a",
        "issue_type": "corrected",
        "description": (
            "Added 8 notable_moments.csv rows for the 2009-2012 batch: RR2009M's Santino Marella "
            "record-breaking 0:02 survival time; RR2010M's Edge shortest-winning-time record and Beth "
            "Phoenix's second-woman-ever milestone; RR2011M's first-ever 40-man Rumble milestone; "
            "RR2012M's full commentary-team entrants, Kofi Kingston's handstand escape, The Miz's "
            "non-entrant interference elimination of John Cena (F262), and Big Show's unusual "
            "before-his-own-entry eliminations (F241, deliberately logged PROBABLE not CONFIRMED, "
            "single-sourced). Mostly surfaced from content already CONFIRMED elsewhere in this "
            "database rather than newly researched."
        ),
        "source_ids_involved": "S059;S082;S083;S084;S085;S086;S089;S097",
        "status": "resolved",
        "date_logged": "2026-09-20",
    })

    save("wrestlers.csv", w_fields, w_rows)
    save("flags.csv", flag_fields, flags)
    save("notable_moments.csv", nm_fields, nm_rows)

    print("Deceased-status audit: 1 new death found (husky-harris/Bray Wyatt, 2023-08-24),")
    print("  plus a sibling bio-completion on bray-wyatt.")
    print(f"Updated {len(hof_fixed)} wrestlers.csv rows (WWE Hall of Fame bio-completion).")
    print("Added 8 notable_moments.csv rows (NM026-NM033).")
    print("Added 3 new flags (F354-F356). No new sources needed (reused existing buckets).")


if __name__ == "__main__":
    main()
